from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=False,
        allow_blank=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    cnic = serializers.CharField(
        required=False,
        allow_blank=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("email", "cnic", "password", "password2", "first_name", "last_name")

    def validate(self, attrs):
        if not attrs.get("email") and not attrs.get("cnic"):
            raise serializers.ValidationError("Either email or CNIC is required.")

        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2", None)
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    cnic = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, required=True)
    otp = serializers.CharField(write_only=True, required=False, allow_blank=True)

    def validate(self, data):
        email = data.get("email") or None
        cnic = data.get("cnic") or None
        password = data.get("password")
        otp = data.get("otp")

        if not email and not cnic:
            raise serializers.ValidationError({"detail": "Email or CNIC is required."})

        user = authenticate(self.context.get("request"), email=email, cnic=cnic, password=password)
        if not user or not user.is_active:
            raise serializers.ValidationError({"detail": "Invalid credentials."})

        data["user"] = user
        data["otp"] = otp
        return data

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])

class TOTPSetupSerializer(serializers.Serializer):
    pass

class TOTPVerifySetupSerializer(serializers.Serializer):
    otp = serializers.CharField(required=True)

class TOTPDisableSerializer(serializers.Serializer):
    confirm = serializers.BooleanField(required=True)
