from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    passphrase = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email',
                  'is_active', 'date_joined', 'role', 'passphrase']

    def get_role(self, obj):
        if obj.groups.filter(name='admin').exists():
            return 'администратор'
        if obj.groups.filter(name='teacher').exists():
            return 'преподаватель'
        return None

    def get_passphrase(self, obj):
        request = self.context.get('request')
        if not request:
            return None
        if request.user == obj or request.user.groups.filter(name='admin').exists():
            try:
                return obj.profile.passphrase
            except UserProfile.DoesNotExist:
                return None
        return None


class CreateUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=6)
    first_name = serializers.CharField(required=False, default='')
    last_name = serializers.CharField(required=False, default='')
    email = serializers.EmailField(required=False, default='')
    role = serializers.ChoiceField(choices=['admin', 'teacher'])
    passphrase = serializers.CharField(required=False, default='', allow_blank=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Пользователь с таким логином уже существует')
        return value

    def create(self, validated_data):
        role = validated_data.pop('role')
        passphrase = validated_data.pop('passphrase', '')

        user = User.objects.create(
            username=validated_data['username'],
            password=make_password(validated_data['password']),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            email=validated_data.get('email', ''),
            is_staff=True,
        )

        group, _ = Group.objects.get_or_create(name=role)
        user.groups.add(group)

        if role == 'teacher':
            UserProfile.objects.create(user=user, passphrase=passphrase)

        return user


class UpdateUserSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    password = serializers.CharField(required=False, write_only=True, min_length=6)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    is_active = serializers.BooleanField(required=False)
    role = serializers.ChoiceField(choices=['admin', 'teacher'], required=False)
    passphrase = serializers.CharField(required=False, allow_blank=True)

    def validate_username(self, value):
        user = self.context.get('user')
        if User.objects.filter(username=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError('Этот логин уже занят')
        return value

    def update(self, instance, validated_data):
        role = validated_data.pop('role', None)
        passphrase = validated_data.pop('passphrase', None)
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.password = make_password(password)

        instance.save()

        if role:
            instance.groups.clear()
            group, _ = Group.objects.get_or_create(name=role)
            instance.groups.add(group)

        if passphrase is not None:
            profile, _ = UserProfile.objects.get_or_create(user=instance)
            profile.passphrase = passphrase
            profile.save()

        return instance