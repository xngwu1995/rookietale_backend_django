from comments.models import Comment
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from comments.api.serializers import (
	CommentSerializer,
	CommentSerializerForCreate,
	CommentSerializerForUpdate,
)
from utils.permissions import IsObjectOwner
from inbox.services import NotificationService
from utils.decorators import required_params


class CommentViewSet(viewsets.GenericViewSet):
	serializer_class = CommentSerializerForCreate
	queryset = Comment.objects.all()
	filterset_fields = ('tweet_id',)
	# POST /api/comments/ -> create
	# GET /api/comments/ -> list
	# GET /api/comments/1/ -> retrieve
	# DELETE /api/comments/1/ -> destroy
	# PATCH /api/comments/1/ -> partial_update
	# PUT /api/comments/1/ -> update
	def get_permissions(self):
		if self.action == 'create':
			return [IsAuthenticated()]
		if self.action in ['destroy', 'update']:
			return [IsAuthenticated(), IsObjectOwner()]
		return [AllowAny()]

	@required_params(params=['tweet_id'])
	def list(self, request, *args, **kwargs):
		queryset = self.get_queryset()
		comments = self.filter_queryset(queryset)\
			.prefetch_related('user')\
			.order_by('created_at')
		serializer = CommentSerializer(comments, many=True)
		return Response({
			'comments': serializer.data
		}, status=status.HTTP_200_OK)

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
		NotificationService.send_comment_notification(comment)
		return Response(
			CommentSerializer(comment).data,
			status=status.HTTP_201_CREATED,
		)

	def update(self, request, *args, **kwargs):
		# Get_object is a function in DRF, will raise 404 error,
		# if it can not get object.
		comment = self.get_object()
		serializer = CommentSerializerForUpdate(
			instance=comment,
			data=request.data,
		)
		if not serializer.is_valid():
			return Response({
				'message': 'Please check input',
				'errors': serializer.errors,
			}, status=status.HTTP_400_BAD_REQUEST)
		comment = serializer.save()
		return Response(
			CommentSerializer(comment).data,
			status=status.HTTP_200_OK,
		)

	def destroy(self, request, *args, **kwargs):
		comment = self.get_object()
		comment.delete()
		return Response({
			'success': True
		}, status=status.HTTP_200_OK)