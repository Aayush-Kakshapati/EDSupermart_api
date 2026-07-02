from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

User = get_user_model()

class EmailOrUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        identifier = kwargs.get("email", username)
        if identifier is None or password is None:
            return None
        try:
            user = User.objects.get(
                Q(email=identifier) | Q(username=identifier)
            )
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            user = User.objects.filter(
                Q(email=identifier) | Q(username=identifier)
            ).first()

        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None