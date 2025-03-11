from django.urls import path

from apps.users.views import (
    UserRegistrationView,
    UserLoginView,
    UserProfileView,
    UserChangePasswordView, PasswordResetRequestEmailView, EmailVerifyView, PasswordResetConfirmView
)

app_name = 'users'

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('change/password/', UserChangePasswordView.as_view(), name='password-change'),
    # password reset cycle
    path('reset-password/', PasswordResetRequestEmailView.as_view(), name='reset-password'),
    path('reset-password/verify/', EmailVerifyView.as_view(), name='reset-password-verify'),
    path('reset-password/confirm/', PasswordResetConfirmView.as_view(), name='reset-password-confirm'),
]