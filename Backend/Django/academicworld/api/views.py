from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from academicworld.models import University, FacultyKeyword, Faculty, Publication, Keyword
from .serializers import UniversitySerializer, KeywordRankSerializer, FacultySerializer, PublicationSerializer
from django.db.models import Avg, Sum, Count
from academicworld.constants import get_score_quantile, CLUSTERMAP


class UniversityViewSet(viewsets.ModelViewSet):
    serializer_class = UniversitySerializer

    def get_queryset(self):
        return University.objects.annotate(
            avg_professor_score=Avg('faculty__facultykeyword__score')
        ).values(
            'avg_professor_score', 'name', 'photo_url'
        ).order_by('-avg_professor_score')[:10]

    @action(methods=['GET'], detail=False)
    def all_universities(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

class FacultyViewSet(viewsets.ModelViewSet):
    queryset = FacultyKeyword.objects.values('keyword__name').annotate(total_score=Sum('score')).order_by('-total_score')
    serializer_class = KeywordRankSerializer

    @action(methods=['GET'], detail=False)
    def get_all_professors(self, request):
        professors = Faculty.objects.values_list('name', flat=True)
        return Response({'professors': professors, 'success': True})

    @action(methods=['POST'], detail=False)
    def get_professors_group_score(self, request):
        query_dict = request.data
        professors = [value for key in query_dict.keys() for value in query_dict.getlist(key)]

        if not professors:
            return Response({'error': 'Both professor1 and professor2 parameters are required'}, status=status.HTTP_400_BAD_REQUEST)

        professors = Faculty.objects.filter(name__in=professors).prefetch_related('facultykeyword_set__keyword')
        group_scores = []
        for professor in professors:
            professor_scores = []
            for key, val in CLUSTERMAP.items():
                group_map = {}
                group_score = getattr(professor, key)
                group_map['group'] = val
                group_map['value'] = get_score_quantile(key, group_score)
                professor_scores.append(group_map)
            group_scores.append({'id': professor.id, 'university': professor.university.name, 'name': professor.name, 'data': professor_scores})
        return Response({'professors_group_scores': group_scores, 'success': True})


class KeywordViewSet(viewsets.ModelViewSet):

    @action(methods=['GET'], detail=False)
    def get_all_keywords(self, request):
        keywords = Keyword.objects.values_list('name', flat=True)
        return Response({'keywords': keywords, 'success': True})

    @action(methods=['POST'], detail=False)
    def keyword_faculty(self, request):
        query_dict = request.data
        keywords = [value for key in query_dict.keys() for value in query_dict.getlist(key)]
        if keywords:
            top_faculty = Faculty.objects.filter(
                facultykeyword__keyword__name__in=keywords
            ).annotate(
                keyword_count=Count('facultykeyword__keyword'),
                average_score=Avg('facultykeyword__score')
            ).order_by(
                '-keyword_count', '-average_score'
            )[:5]
            # Serialize the results
            serializer = FacultySerializer(top_faculty, context={'keywords': keywords}, many=True)
            return Response(serializer.data)
        return Response({"error": "No keywords provided"}, status=400)


    @action(methods=['POST'], detail=False)
    def keyword_publication(self, request):
        query_dict = request.data
        keywords = [value for key in query_dict.keys() for value in query_dict.getlist(key)]
        if keywords:
            top_publication = Publication.objects.filter(
                publicationkeyword__keyword__name__in=keywords
            ).annotate(
                keyword_count=Count('publicationkeyword__keyword'),
                average_score=Avg('publicationkeyword__score')
            ).order_by(
                '-keyword_count', '-average_score'
            ).distinct()[:5]
            # Serialize the results
            serializer = PublicationSerializer(top_publication, context={'keywords': keywords}, many=True)
            return Response(serializer.data)
        return Response({"error": "No keywords provided"}, status=400)


class TopEntitiesViewSet(viewsets.ModelViewSet):
    serializer_class = FacultySerializer

    @action(methods=['GET'], detail=False)
    def top_faculty(self, request):
        queryset = Faculty.objects.annotate(total_score=Sum('facultykeyword__score')).order_by('-total_score')[:10]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['GET'], detail=False)
    def top_publication(self, request):
        queryset = Publication.objects.annotate(total_score=Sum('publicationkeyword__score')).order_by('-total_score')[:10]
        serializer = PublicationSerializer(queryset, many=True)
        return Response(serializer.data)
