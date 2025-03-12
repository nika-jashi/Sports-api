from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tournaments.serializers import TournamentSerializer


@extend_schema(tags=["Tournament"],
               responses={
                   status.HTTP_201_CREATED: TournamentSerializer,
                   status.HTTP_400_BAD_REQUEST: TournamentSerializer,
               })
class TournamentCreationView(APIView):
    serializer_class = TournamentSerializer

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs) -> Response:
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_400_BAD_REQUEST)
