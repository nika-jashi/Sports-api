from django.contrib.auth import get_user_model
from django.core.cache import cache
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.users.serializers import (
    UserSerializer,
    UserProfileSerializer,
    UserChangePasswordSerializer,
    PasswordResetRequestEmailSerializer,
    OTPValidationSerializer,
    PasswordResetConfirmSerializer)
from apps.utils.db_queries import check_user_exists
from apps.utils.email_sender import SendEmail
from apps.utils.email_html_templates import email_verify, password_reset
from apps.utils.otp_generator import OTP_generator


@extend_schema(tags=["Auth"],
               responses={
                   status.HTTP_201_CREATED: UserSerializer,
                   status.HTTP_400_BAD_REQUEST: UserSerializer,
               })
class UserRegistrationView(APIView):
    """ A view for creating new users. with POST request method and proper status codes """

    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs) -> Response:
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            data = request.data
            otp = OTP_generator(password_reset=False)

            cache.set(otp, data.get('email'), timeout=3600)
            # SendEmail.send_email(subject="Your Account Has Been Created Get Verified",
            #                      body=email_verify(otp=otp),
            #                      to=[serializer.data.get("email")])
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Auth"],
               responses={
                   status.HTTP_200_OK: TokenObtainPairSerializer,
                   status.HTTP_400_BAD_REQUEST: 'Bad Request',
                   status.HTTP_401_UNAUTHORIZED: 'Unauthorized',
               })
class UserLoginView(TokenObtainPairView):
    """View for user to log in using JWT bearer Token"""

    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs) -> Response:
        email = request.data.get("email")
        if not check_user_exists(email=email):
            return Response(
                data={"detail": "No Active User Found With The Given Credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response(data=serializer.validated_data, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Profile"])
class UserProfileView(APIView):
    """ View For User To See Their Profile """

    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs) -> Response:
        """ GET Method For Users To View Their Profile """

        current_user = request.user
        serializer = UserProfileSerializer(instance=current_user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs) -> Response:
        """ PATCH Method For Users To Update Their Profile """

        current_user = request.user
        serializer = UserProfileSerializer(instance=current_user, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Profile"])
class UserChangePasswordView(APIView):
    """View for user to change password when authenticated"""

    serializer_class = UserChangePasswordSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request) -> Response:
        current_user = request.user
        serializer = self.serializer_class(
            instance=current_user, data=request.data, context={"request": request}
        )
        if not serializer.is_valid(raise_exception=True):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response({"detail": "You successfully changed your password."}, status=status.HTTP_200_OK)


@extend_schema(tags=["PasswordReset"])
class PasswordResetRequestEmailView(APIView):
    """View for user to request password reset by email verification, when user is not authenticated"""
    serializer_class = PasswordResetRequestEmailSerializer

    def post(self, request):
        data = request.data
        otp = OTP_generator(password_reset=True)

        cache.set(otp, data.get('email'))

        serializer = PasswordResetRequestEmailSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            SendEmail.send_email(subject="Password Reset for your account",
                                 body=password_reset(otp),
                                 to=[serializer.data.get("email")])

            return Response({"detail": "We Have Sent You Message To your email"}, status=status.HTTP_200_OK)

        return Response({"detail": "There Was Problem Validating Data"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["PasswordReset"])
class EmailVerifyView(APIView):
    """ View for user to verify User by input of generated otp sent on email
       this view also generated JWT token for changing password afterward """
    serializer_class = OTPValidationSerializer

    def post(self, request):
        data = {
            'Success': 'Successful'
        }
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data.get("email")
            user = get_user_model().objects.get_queryset().filter(email=email).first()

            if not user:
                return Response({"detail": "User does not exist."}, status=status.HTTP_400_BAD_REQUEST)

            access = AccessToken.for_user(user=user)
            otp = serializer.validated_data.get('OTP')
            if len(otp) == 6:
                data = {
                    'access': str(access),
                }
            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["PasswordReset"])
class PasswordResetConfirmView(APIView):
    """View for user to confirm new password after verifying email and otp from request"""
    serializer_class = PasswordResetConfirmSerializer
    queryset = get_user_model().objects.get_queryset().all()
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user
        serializer = PasswordResetConfirmSerializer(instance=user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"detail": "You successfully changed your password!"}, status=status.HTTP_200_OK)
