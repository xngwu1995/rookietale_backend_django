from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from chatgpt.models import ChatGPTInteraction
from chatgpt.api.serializers import ChatGPTInteractionSerializer
from chatgpt.utils import ChatGPTApi
from django.utils import timezone
from utils.permissions import IsAdminUser


class ChatgptViewSet(viewsets.ViewSet):
    permission_classes = (IsAdminUser,)

    @action(methods=['POST'], detail=False)
    def ask_chatgpt(self, request):
        # Extract user's requirements and content from the request
        requirements = request.data.get('requirements')
        content = request.data.get('content')
        wordlimits = int(request.data.get('wordLimit'))
        language = request.data.get('languageSelect')
        islong = request.data.get('islong')

        if not request.user:
            return None
        user = request.user

        if language == "chinese":
            wordlimits //= 1

        # Validate inputs
        if not requirements or not content:
            return Response({'error': 'Both requirements and content are required'}, 
                            status=status.HTTP_400_BAD_REQUEST)

        # Initialize the ChatGPT API class
        chatgpt_api = ChatGPTApi()

        # # Get the response from ChatGPT
        if islong == 'true':
            response_text = chatgpt_api.write_long_essay(
                requirements, content, wordlimits)
        else:
            response_text = chatgpt_api.process_text_and_get_response(
                requirements, content, wordlimits, language)
        response_time = timezone.now()

        # Create a record in the ChatGPTInteraction model
        chat_interaction = ChatGPTInteraction.objects.create(
            user=user,
            requirement_text=requirements,
            content_text=content,
            response_text=response_text,
            response_time=response_time
        )

        # Serialize the data
        serializer = ChatGPTInteractionSerializer(chat_interaction)

        # Check for a valid response
        if response_text is None:
            return Response({'error': 'Failed to get response from ChatGPT'}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Return the response along with the recorded interaction
        return Response(serializer.data)
