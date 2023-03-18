from django.contrib import admin
from .models import University, Faculty, Keyword, Publication, FacultyKeyword, FacultyPublication, PublicationKeyword

class UniversityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'photo_url')

class FacultyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'position', 'research_interest', 'email', 'phone', 'photo_url', 'university')
    list_filter = ('university',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('university')

class KeywordAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

class PublicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'venue', 'year', 'num_citations')

class FacultyKeywordAdmin(admin.ModelAdmin):
    list_display = ('faculty', 'keyword', 'score')
    list_filter = ('faculty', 'keyword')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('faculty', 'keyword')

class FacultyPublicationAdmin(admin.ModelAdmin):
    list_display = ('faculty', 'publication')
    list_filter = ('faculty',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('faculty', 'publication')

class PublicationKeywordAdmin(admin.ModelAdmin):
    list_display = ('publication', 'keyword', 'score')
    list_filter = ('publication', 'keyword')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('publication', 'keyword')

admin.site.register(University, UniversityAdmin)
admin.site.register(Faculty, FacultyAdmin)
admin.site.register(Keyword, KeywordAdmin)
admin.site.register(Publication, PublicationAdmin)
admin.site.register(FacultyKeyword, FacultyKeywordAdmin)
admin.site.register(FacultyPublication, FacultyPublicationAdmin)
admin.site.register(PublicationKeyword, PublicationKeywordAdmin)
