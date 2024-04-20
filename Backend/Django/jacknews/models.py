from django.db import models


class JackNews(models.Model):
    title = models.CharField(max_length=255)  # Assuming titles won't exceed 255 characters
    summary = models.TextField()  # Suitable for longer text
    content = models.TextField()  # Suitable for potentially very long text
    created = models.DateTimeField(auto_now_add=True)  # Automatically set to now when object is created

    def __str__(self):
        return self.title
