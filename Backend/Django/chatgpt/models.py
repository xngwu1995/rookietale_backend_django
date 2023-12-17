from django.db import models
from django.contrib.auth.models import User

class ChatGPTInteraction(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    requirement_text = models.TextField(
        help_text="The user's requirements."
    )
    content_text = models.TextField(
        help_text="The user's input."
    )
    response_text = models.TextField(blank=True, null=True)
    request_time = models.DateTimeField(auto_now_add=True)
    response_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"ChatGPT Interaction by {self.user.username} at {self.request_time}"
