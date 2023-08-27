from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from academicworld.models import University, FacultyKeyword, Faculty, Publication, Keyword
from .serializers import UniversitySerializer, KeywordRankSerializer, FacultySerializer, PublicationSerializer
from django.db.models import Avg, Sum, Count
from academicworld.constants import get_score_quantile, CLUSTERMAP
from utils.db_handler import get_top10_faculty, get_recommend_faculty

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
        universities = University.objects.values_list('name', flat=True)

        return Response({'universities': universities, 'success': True})

class FacultyViewSet(viewsets.ModelViewSet):
    queryset = FacultyKeyword.objects.values('keyword__name').annotate(total_score=Sum('score')).order_by('-total_score')
    serializer_class = KeywordRankSerializer

    @action(methods=['GET'], detail=False)
    def get_all_professors(self, request):
        professors = Faculty.objects.values_list('name', flat=True)
        return Response({'professors': professors, 'success': True})

    @action(methods=['GET'], detail=False)
    def get_university_professors(self, request):
        university_name = request.GET.get('university', None)
        professors = Faculty.objects.prefetch_related(
                'university'
            ).filter(
                university__name=university_name
            ).values_list('name', flat=True)
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

class MangoViewSet(viewsets.ModelViewSet):

    @action(methods=['POST'], detail=False, url_path='get-top10-faculty-university')
    def keyword_faculty_university_krc(self, request):
        university, keyword = request.data['University'], request.data['Keyword']
        data = get_top10_faculty(university, keyword)
        return Response({'data': data, 'success': True})

class Neo4JViewSet(viewsets.ModelViewSet):

    @action(methods=['POST'], detail=False, url_path='get-recommend-faculty')
    def get_recommend_faculty(self, request):
        university, professor, target_school = request.data['University'], request.data['Professor'], request.data['TargetSchool']
        data = get_recommend_faculty(university, professor, target_school)
        return Response({'data': data, 'success': True})
