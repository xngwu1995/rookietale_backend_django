from django.db import models

class University(models.Model):
    name = models.CharField(max_length=512)
    photo_url = models.CharField(max_length=512, null=True, blank=True)

    def __str__(self):
        return self.name

class Faculty(models.Model):
    name = models.CharField(max_length=512)
    position = models.CharField(max_length=512, null=True, blank=True)
    research_interest = models.CharField(max_length=512, null=True, blank=True)
    email = models.CharField(max_length=512, null=True, blank=True)
    phone = models.CharField(max_length=512, null=True, blank=True)
    photo_url = models.CharField(max_length=512, null=True, blank=True)
    university = models.ForeignKey(University, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

class Keyword(models.Model):
    name = models.CharField(max_length=512)

    def __str__(self):
        return self.name

class Publication(models.Model):
    title = models.CharField(max_length=512)
    venue = models.CharField(max_length=512, null=True, blank=True)
    year = models.CharField(max_length=512, null=True, blank=True)
    num_citations = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.title

class FacultyKeyword(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE)
    score = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ('faculty', 'keyword')

class FacultyPublication(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('faculty', 'publication')

class PublicationKeyword(models.Model):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE)
    score = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ('publication', 'keyword')
