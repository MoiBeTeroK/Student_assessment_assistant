from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

from .models import UserProfile
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

        # Гарантируем наличие Django-прав для работы в admin-панели
        if user.groups.filter(name__in=['admin', 'teacher']).exists():
            from django.contrib.contenttypes.models import ContentType
            from django.contrib.auth.models import Permission
            ct = ContentType.objects.get_for_model(User)
            perms = Permission.objects.filter(content_type=ct, codename__in=['view_user', 'change_user'])
            user.user_permissions.add(*perms)

        profile, _ = UserProfile.objects.get_or_create(user=user)

        if profile.active_jti:
            has_valid_tokens = OutstandingToken.objects.filter(
                user=user,
                expires_at__gt=timezone.now(),
            ).exclude(id__in=BlacklistedToken.objects.values('token_id')).exists()

            if has_valid_tokens:
                return Response(
                    {'detail': 'Вы уже вошли в систему с другого устройства'},
                    status=status.HTTP_403_FORBIDDEN,
                )
            # Сессия протухла сама по себе — разрешаем вход
            profile.active_jti = ''

        refresh = RefreshToken.for_user(user)
        profile.active_jti = str(refresh.access_token['jti'])
        profile.save(update_fields=['active_jti'])

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user, context={'request': request}).data,
        })


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh = request.data.get('refresh')
        if not refresh:
            return Response({'detail': 'Refresh-токен не передан'}, status=status.HTTP_400_BAD_REQUEST)

        # Декодируем payload без валидации, чтобы получить user_id даже если токен уже невалиден
        user_id = None
        try:
            import base64, json
            payload = refresh.split('.')[1]
            payload += '=' * (-len(payload) % 4)
            user_id = json.loads(base64.b64decode(payload)).get('user_id')
        except Exception:
            pass

        try:
            RefreshToken(refresh).blacklist()
        except TokenError:
            pass

        if user_id:
            UserProfile.objects.filter(user_id=user_id).update(active_jti='')

        return Response({'detail': 'Выход выполнен'})


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