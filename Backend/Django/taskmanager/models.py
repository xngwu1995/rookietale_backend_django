from django.db import models
from django.contrib.auth.models import User

class TaskManager(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False, help_text="Name of the task.")
    mistress = models.ForeignKey(
        User, related_name='task_mistress',
        on_delete=models.CASCADE, 
        help_text="The user who assigns the task."
    )
    sub = models.ForeignKey(
        User, related_name='task_sub',
        on_delete=models.CASCADE, 
        help_text="The user who is responsible for completing the task."
    )
    completed = models.BooleanField(default=False, help_text="Status of the task completion.")
    created_date = models.DateTimeField(auto_now_add=True, help_text="The date and time the task was created.")
    updated_date = models.DateTimeField(auto_now=True, help_text="The date and time the task was last updated.")
    completed_date = models.DateTimeField(null=True, blank=True, help_text="The date and time the task was completed.")

    def __str__(self):
        return f"Task '{self.name}' assigned by {self.mistress.username} to {self.sub.username}"
