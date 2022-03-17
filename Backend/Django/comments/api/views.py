from comments.models import Comment
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from comments.api.serializers import (
	CommentSerializer,
	CommentSerializerForCreate,
)

class CommentViewSet(viewsets.GenericViewSet):
	serializer_class = CommentSerializerForCreate
	queryset = Comment.objects.all()
	# POSt /api/comments/ -> create
	# GET /api/comments/ -> list
	# GET /api/comments/1/ -> retrieve
	# DELETE /api/comments/1/ -> destroy
	# PATCH /api/comments/1/ -> partial_update
	# PUT /api/comments/1/ -> update
	def get_permissions(self):
		if self.action == 'create':
			return [IsAuthenticated()]
		return [AllowAny()]

	def create(self, request, *args, **kwargs):
		data = {
			'user_id': request.user.id,
			'tweet_id': request.data.get('tweet_id'),
			'content': request.data.get('content'),
		}
		# Need to use data= to assign the instance to data
		serializer = CommentSerializerForCreate(data=data)
		if not serializer.is_valid():
			return Response({
				'message': 'Please check input',
				'errors': serializer.errors,
			}, status=status.HTTP_400_BAD_REQUEST)

		comment = serializer.save()
		return Response(
			CommentSerializer(comment).data,
			status=status.HTTP_201_CREATED,
		)