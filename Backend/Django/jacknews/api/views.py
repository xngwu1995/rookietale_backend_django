from rest_framework import viewsets
from rest_framework.response import Response
from jacknews.models import JackNews
from jacknews.api.serializers import JackNewsSerializer

class JacknewsViewSet(viewsets.ModelViewSet):
    queryset = JackNews.objects.all()
    serializer_class = JackNewsSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)