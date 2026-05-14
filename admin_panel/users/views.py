from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserSerializer, CreateUserSerializer, UpdateUserSerializer
from .permissions import IsAdmin, IsAdminOrSelf, is_admin


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if not user:
            return Response(
                {'detail': 'Неверный логин или пароль'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        if not user.is_active:
            return Response(
                {'detail': 'Учётная запись деактивирована'},
                status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user, context={'request': request}).data,
        })


class UserListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        """Список всех пользователей — только для админа"""
        users = User.objects.prefetch_related('groups', 'profile').all()
        serializer = UserSerializer(users, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        """Создание пользователя — только для админа"""
        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                UserSerializer(user, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):
    permission_classes = [IsAdminOrSelf]

    def get_object(self, pk, request):
        try:
            user = User.objects.prefetch_related('groups', 'profile').get(pk=pk)
            self.check_object_permissions(request, user)
            return user
        except User.DoesNotExist:
            return None

    def get(self, request, pk):
        user = self.get_object(pk, request)
        if not user:
            return Response({'detail': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)
        return Response(UserSerializer(user, context={'request': request}).data)

    def patch(self, request, pk):
        if not is_admin(request.user):
            return Response({'detail': 'Недостаточно прав'}, status=status.HTTP_403_FORBIDDEN)
        user = self.get_object(pk, request)
        if not user:
            return Response({'detail': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UpdateUserSerializer(
            user, data=request.data, partial=True,
            context={'user': user, 'request': request}
        )
        if serializer.is_valid():
            updated_user = serializer.update(user, serializer.validated_data)
            return Response(UserSerializer(updated_user, context={'request': request}).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if not is_admin(request.user):
            return Response({'detail': 'Недостаточно прав'}, status=status.HTTP_403_FORBIDDEN)
        user = self.get_object(pk, request)
        if not user:
            return Response({'detail': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)
        if user == request.user:
            return Response(
                {'detail': 'Нельзя деактивировать собственную учётную запись'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.is_active = False
        user.save()
        return Response({'detail': 'Учётная запись деактивирована'})


class MeView(APIView):
    """Текущий пользователь смотрит на себя"""
    def get(self, request):
        return Response(UserSerializer(request.user, context={'request': request}).data)