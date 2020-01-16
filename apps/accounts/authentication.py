from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=username)
            if user.is_superuser == True:
                user.is_staff = True
                user.save()
            else:
                user.is_staff = False
                user.save()
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
        return None
