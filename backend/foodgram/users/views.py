from .models import User, Follow
from .serializers import FollowUsersSerializer, FullUserSerializer
from rest_framework.decorators import action
from djoser.views import UserViewSet
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status, permissions


class FollowUserViewSet(UserViewSet):

    serializer_class = FullUserSerializer

    def get_serializer_class(self):
        return super().get_serializer_class()

    @action(
        detail=True,
        methods=['get', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscribe(self, serializer, id=None):
        following_user = get_object_or_404(User, id=id)

        if self.request.method == 'GET':
            if self.request.user == following_user:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            try:
                Follow.objects.get(
                    user=self.request.user,
                    following=following_user
                )
                return Response(status=status.HTTP_400_BAD_REQUEST)

            except Follow.DoesNotExist:
                follow = Follow.objects.create(
                    user=self.request.user,
                    following=following_user
                )
                return Response(FollowUsersSerializer(follow).data)

        if self.request.method == 'DELETE':
            try:
                Follow.objects.get(
                    user=self.request.user,
                    following=following_user
                ).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Follow.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)


class FollowViewSet(UserViewSet):
    serializer_class = FollowUsersSerializer
    permission_classes = (permissions.IsAuthenticated)
    http_method_names = ['get']

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)
