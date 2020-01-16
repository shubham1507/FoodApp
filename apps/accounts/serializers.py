from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _
from .models import EmailUser


class SettingsUserForSerializers:
    def __init__(self, *args, **kwargs):
        if not getattr(self.Meta, 'model', None):
            self.Meta.model = get_user_model()
        super().__init__(*args, **kwargs)


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if user:
                if not user.validated_at:
                    msg = _('Validate your email address.')
                    return msg

                if not user.is_active:
                    msg = _('User account is disabled.')
                    return msg
            else:
                msg = _('Unable to log in with provided credentials.')
                return msg
        else:
            msg = _('Must include "email" and "password".')
            return msg

        data['user'] = user
        return data


class CreateEmailUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    token = serializers.SerializerMethodField()

    class Meta:
        model = EmailUser
        fields = ('first_name', 'last_name', 'email', 'is_buyer', 'is_seller',
                  'image', 'password', 'token')

    def get_token(self, validated_data):
        user = EmailUser.objects.filter(email=validated_data.email)
        token = Token.objects.get(user=user)
        return token.key


class UserSerializer(SettingsUserForSerializers, serializers.ModelSerializer):
    class Meta:

        read_only_fields = ('email', )
        exclude = ('password', 'is_superuser', 'groups', 'user_permissions',
                   'is_staff', 'is_active')


class EmailUserSerializer(UserSerializer):
    class Meta:
        model = SignUp
        fields = ('first_name', 'last_name', 'email', 'is_seller',
                  'is_customer', 'image')
