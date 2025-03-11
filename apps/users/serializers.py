from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from apps.utils.custom_validators import (does_not_contains_whitespace,
                                          contains_uppercase,
                                          contains_digits,
                                          contains_lowercase)
from apps.utils.db_queries import check_if_user_is_active


class UserSerializer(serializers.ModelSerializer):
    """ Serializer For The User Object """

    password = serializers.CharField(
        max_length=255,
        write_only=True,
        validators=[does_not_contains_whitespace,
                    contains_uppercase,
                    contains_digits,
                    contains_lowercase,
                    MinLengthValidator(8)],
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        max_length=255,
        write_only=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = get_user_model()
        fields = ['email', 'first_name','last_name', 'password', 'confirm_password']

    def validate(self, data):
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError(
                {"confirm_password": _("[Password] and [Confirm Password] Don't Match.")}
            )

        del data['confirm_password']  # deleting confirm_password because we only need it for verification
        return data

    def create(self, validated_data):
        """ Create And Return A User With Encrypted Password """
        instance = get_user_model().objects.create_user(**validated_data, is_active=True)
        return instance


class UserProfileSerializer(serializers.ModelSerializer):
    """ Serializer To View Users Profile and Update It """

    email = serializers.EmailField(read_only=True)
    date_joined = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)
    profile_picture = serializers.ImageField(required=False)

    class Meta:
        model = get_user_model()
        fields = [
            'email',
            'first_name',
            'last_name',
            'date_joined',
            'profile_picture',
        ]

        extra_kwargs = {
            'first_name': {'min_length': 3},
            'last_name': {'min_length': 3},
        }

    def validate(self, data):
        return data

    def update(self, instance, validated_data):
        user = super().update(instance=instance, validated_data=validated_data)
        user.save()
        return user


class UserChangePasswordSerializer(serializers.Serializer):  # noqa
    """A serializer for user to change password when authenticated. Includes all the required
       fields and validations, plus a repeated password. """

    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[does_not_contains_whitespace,
                    contains_uppercase,
                    contains_digits,
                    contains_lowercase,
                    MinLengthValidator(8)])
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        user = self.context.get('request').user
        if not user.check_password(data.get("old_password")):
            raise serializers.ValidationError({"old_password": "Old password is not correct"})

        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError(
                {"new_password": "[New Password] and [Confirm Password] Don't Match."}
            )

        return data

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()

        return instance


class PasswordResetRequestEmailSerializer(serializers.Serializer):  # noqa
    """A serializer for user to request password reset when is not authenticated.
     Includes email field for sending otp and all required validations. """
    email = serializers.EmailField(required=True)

    def validate(self, data):
        data = super().validate(data)
        if not get_user_model().objects.get_queryset().filter(email=data.get('email'), is_active=True):
            raise serializers.ValidationError({'detail': _('No Active User Was Found')})
        return data


class OTPValidationSerializer(serializers.Serializer):  # noqa
    """A serializer for user to verify sent otp includes all required verifications. """
    OTP = serializers.CharField(write_only=True,
                                required=True,
                                help_text="Please input your otp code")
    email = serializers.CharField(read_only=True)

    def validate(self, data):
        data = super().validate(data)
        email = cache.get(data.get('OTP'))
        if not email:
            raise serializers.ValidationError({'detail': _('otp is wrong or expired')})
        data["email"] = email
        if len(data.get('OTP')) == 5 and check_if_user_is_active(email=email) is False:
            get_user_model().objects.filter(email=email).update(is_active=True)
        cache.delete(data.get('OTP'))
        return data


class PasswordResetConfirmSerializer(serializers.Serializer):  # noqa
    """A serializer for user to confirm new password and obtain full access of account
     includes all password, plus a repeated password. """
    new_password = serializers.CharField(required=True, write_only=True, validators=[does_not_contains_whitespace,
                                                                                     contains_uppercase,
                                                                                     contains_digits,
                                                                                     contains_lowercase,
                                                                                     MinLengthValidator(8)])
    new_password_confirm = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        data = super().validate(data)
        new_password = data.get("new_password")
        new_password_confirm = data.get("new_password_confirm")

        if new_password != new_password_confirm:
            raise serializers.ValidationError({"new_password_confirm": _("Passwords are not matched.")})

        return data

    def update(self, instance, validated_data):
        instance.set_password(validated_data.get('new_password'))
        instance.save()
        return instance