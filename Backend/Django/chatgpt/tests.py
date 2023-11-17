from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import ChatGPTInteraction
import datetime

# Create your tests here.
class ChatGPTInteractionModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        user = get_user_model().objects.create_user(username='testuser', password='12345')
        ChatGPTInteraction.objects.create(user=user, requirement_text='Test Requirement', content_text='Test Response')

    def test_chatgpt_interaction_content(self):
        interaction = ChatGPTInteraction.objects.get(id=1)
        expected_requirement = f'{interaction.requirement_text}'
        expected_content = f'{interaction.content_text}'
        self.assertEquals(expected_requirement, 'Test Requirement')
        self.assertEquals(expected_content, 'Test Response')

    def test_chatgpt_interaction_user(self):
        interaction = ChatGPTInteraction.objects.get(id=1)
        expected_user = f'{interaction.user.username}'
        self.assertEquals(expected_user, 'testuser')

    def test_chatgpt_interaction_str(self):
        interaction = ChatGPTInteraction.objects.get(id=1)
        expected_object_name = f'{interaction}'
        self.assertEquals(expected_object_name, 'ChatGPT Interaction by testuser at {interaction.request_time}')

    def test_chatgpt_interaction_dates(self):
        interaction = ChatGPTInteraction.objects.get(id=1)
        self.assertTrue(isinstance(interaction.request_time, datetime.datetime))
        self.assertIsNone(interaction.response_time)  # assuming response_time is optional and can be None
