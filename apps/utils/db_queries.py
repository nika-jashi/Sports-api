from apps.users.models import CustomUser


def check_user_exists(uid=None, email=None, username=None) -> bool:
    queryset = CustomUser.objects.filter(is_active=True)

    return (
        queryset.filter(id=uid).exists() if uid is not None else
        queryset.filter(email=email).exists() if email is not None else
        queryset.filter(username=username).exists() if username is not None else
        False
    )


def check_if_user_is_active(email) -> bool:
    user = CustomUser.objects.get(email=email)
    return user.is_active