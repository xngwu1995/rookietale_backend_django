from rest_framework import serializers
from academicworld.models import University, Faculty, Publication

class UniversitySerializer(serializers.ModelSerializer):
    avg_professor_score = serializers.FloatField()

    class Meta:
        model = University
        fields = '__all__'


class KeywordRankSerializer(serializers.Serializer):
    keyword__name = serializers.CharField()
    total_score = serializers.FloatField()

class FacultySerializer(serializers.ModelSerializer):
    total_score = serializers.FloatField(read_only=True)
    faculty_keywords = serializers.SerializerMethodField()
    university_name = serializers.SerializerMethodField()

    class Meta:
        model = Faculty
        fields = ['id', 'name', 'total_score', 'faculty_keywords', 'photo_url', 'university_name']

    def get_faculty_keywords(self, obj):
        faculty_keywords = []
        keywords = set(self.context['keywords'])
        filtered_faculty_keywords = obj.facultykeyword_set.filter(keyword__name__in=keywords)

        for fk in filtered_faculty_keywords:
            fk_name = fk.keyword.name
            faculty_keywords.append({
                'keyword': fk_name,
                'score': fk.score
            })
        return faculty_keywords
    
    def get_university_name(self, obj):
        return obj.university.name

class PublicationSerializer(serializers.ModelSerializer):
    total_score = serializers.FloatField(read_only=True)
    publication_keywords = serializers.SerializerMethodField()

    class Meta:
        model = Publication
        fields = '__all__'
    
    def get_publication_keywords(self, obj):
        publication_keywords = []
        keywords = set(self.context['keywords'])

        # Filter the publicationkeyword_set queryset based on keywords
        filtered_publication_keywords = obj.publicationkeyword_set.filter(keyword__name__in=keywords)

        for fk in filtered_publication_keywords:
            fk_name = fk.keyword.name
            publication_keywords.append({
                'keyword': fk_name,
                'score': fk.score
            })

        return publication_keywords

