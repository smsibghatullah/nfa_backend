from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class EmailOrCNICBackend(ModelBackend):
    def authenticate(self, request, email=None, cnic=None, username=None, password=None, **kwargs):
        identifier = email or cnic or username
        if not identifier or not password:
            return None

        try:
            if "@" in identifier:
                user = UserModel.objects.get(email__iexact=identifier)
            elif identifier.isdigit() or "-" in identifier:
                user = UserModel.objects.get(cnic=identifier)
            else:
                user = UserModel.objects.get(username__iexact=identifier)
        except UserModel.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
    