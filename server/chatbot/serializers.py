from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Conversation, Message, AccessRequest, Instrument, Equivalent, InstrumentFeature, CustomUser , PasswordReset, Document
from django.utils import timezone
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import uuid
import json

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'password', 'first_name', 'last_name', 'email', 'profile', 'role', 'site', 'created_at', 'updated_at']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        try:
            user = CustomUser.objects.create_user(
                username=validated_data['email'],
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                email=validated_data['email'],
                profile=validated_data['profile'],
                role=validated_data.get('role', 'user'),
                site=validated_data['site'],
                password=validated_data['password']
            )
            return user
        except Exception as e:
            print(e)
            raise serializers.ValidationError({'error': str(e)})

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('email', instance.email)
        instance.profile = validated_data.get('profile', instance.profile)
        instance.role = validated_data.get('role', instance.role)
        instance.site = validated_data.get('site', instance.site)
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        instance.save()
        return instance

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = CustomUser.objects.get(email=value)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        return value

    def create(self, validated_data):
        user = CustomUser.objects.get(email=validated_data['email'])
        password_reset_data = {
            'user': user.id
        }
        password_reset_serializer = PasswordResetSerializer(data=password_reset_data)
        password_reset_serializer.is_valid(raise_exception=True)
        reset_token = password_reset_serializer.save()
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token.token}"
        
        # Render the HTML template
        html_content = render_to_string('password_reset_email.html', {'reset_url': reset_url})
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            'Password Reset Request',
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )
        email.attach_alternative(html_content, "text/html")
        try:
            email.send()
        except Exception as e:
            print(e)
            raise serializers.ValidationError({'error': str(e)})
        
        
        return reset_token

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    new_password = serializers.CharField(write_only=True)

    def validate_token(self, value):
        try:
            reset_request = PasswordReset.objects.get(token=value)
        except PasswordReset.DoesNotExist:
            raise serializers.ValidationError("Invalid token.")
        
        if reset_request.is_expired():
            raise serializers.ValidationError("Token has expired.")
        
        return value

    def save(self):
        try:
            validated_data = self.validated_data
            token = validated_data['token']
            new_password = validated_data['new_password']
            reset_request = PasswordReset.objects.get(token=token)
            user = reset_request.user
            user.set_password(new_password)
            user.save()
            reset_request.delete()
        except Exception as e:
            print(e)
            raise serializers.ValidationError({'error': str(e)})

class PasswordResetSerializer(serializers.ModelSerializer):
    class Meta:
        model = PasswordReset
        fields = ['id', 'user', 'token', 'created_at', 'expiration_time']

    def create(self, validated_data):
        expiration_time = validated_data.get('expiration_time', timezone.now() + settings.PASSWORD_RESET_EXPIRATION_TIME)
        try:
            password_reset = PasswordReset.objects.create(
                user=validated_data['user'],
                token=uuid.uuid4(),
                expiration_time=expiration_time
            )
            return password_reset
        except Exception as e:
            print(e)
            raise serializers.ValidationError({'error': str(e)})


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = '__all__'
        read_only_fields = ['user']

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'

class AccessRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessRequest
        fields = ['id', 'first_name', 'last_name', 'profile', 'email', 'site', 'reason', 'created_at', 'updated_at', 'status']
        read_only_fields = ['status', 'created_at', 'updated_at']

    def validate_email(self, value):
        # Vérifier s'il existe déjà une demande avec cet email
        if AccessRequest.objects.filter(email=value).exists():
            raise serializers.ValidationError("A request with this email already exists.")
        
        # Vérifier s'il existe déjà un utilisateur avec cet email
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        
        return value

class InstrumentSerializer(serializers.ModelSerializer):
    characteristics = serializers.SerializerMethodField()
    specifications = serializers.SerializerMethodField()
    performance = serializers.SerializerMethodField()
    physical = serializers.SerializerMethodField()
    input_output = serializers.SerializerMethodField()
    software = serializers.SerializerMethodField()
    other = serializers.SerializerMethodField()
    display = serializers.SerializerMethodField()
    io_interfaces = serializers.SerializerMethodField()
    acquisition_modes = serializers.SerializerMethodField()
    trigger_system = serializers.SerializerMethodField()
    cursors = serializers.SerializerMethodField()
    automatic_waveform_measurements = serializers.SerializerMethodField()
    waveform_math = serializers.SerializerMethodField()
    autoset_menu = serializers.SerializerMethodField()
    display_characteristics = serializers.SerializerMethodField()
    environmental_safety = serializers.SerializerMethodField()
    signal_sampling = serializers.SerializerMethodField()
    amplitude_range = serializers.SerializerMethodField()
    offset_range = serializers.SerializerMethodField()
    sine_distortion = serializers.SerializerMethodField()
    pulse_width = serializers.SerializerMethodField()
    reference_input = serializers.SerializerMethodField()
    output_characteristics = serializers.SerializerMethodField()
    input_characteristics = serializers.SerializerMethodField()
    interface = serializers.SerializerMethodField()
    parameters = serializers.SerializerMethodField()
    pattern = serializers.SerializerMethodField()
    input_output_ports = serializers.SerializerMethodField()
    pressure_range = serializers.SerializerMethodField()
    pressure_generation_measurement = serializers.SerializerMethodField()
    measurement_accuracy = serializers.SerializerMethodField()

    def get_characteristics(self, obj):
        return json.loads(obj.specifications) if obj.specifications else []

    def get_specifications(self, obj):
        return json.loads(obj.specifications) if obj.specifications else []

    def get_performance(self, obj):
        return json.loads(obj.performance) if obj.performance else []

    def get_physical(self, obj):
        return json.loads(obj.physical) if obj.physical else []

    def get_input_output(self, obj):
        return json.loads(obj.input_output) if obj.input_output else []

    def get_software(self, obj):
        return json.loads(obj.software) if obj.software else []

    def get_other(self, obj):
        return json.loads(obj.other) if obj.other else []

    def get_display(self, obj):
        return json.loads(obj.display) if obj.display else []

    def get_io_interfaces(self, obj):
        return json.loads(obj.io_interfaces) if obj.io_interfaces else []

    def get_acquisition_modes(self, obj):
        return json.loads(obj.acquisition_modes) if obj.acquisition_modes else []

    def get_trigger_system(self, obj):
        return json.loads(obj.trigger_system) if obj.trigger_system else []

    def get_cursors(self, obj):
        return json.loads(obj.cursors) if obj.cursors else []

    def get_automatic_waveform_measurements(self, obj):
        return json.loads(obj.automatic_waveform_measurements) if obj.automatic_waveform_measurements else []

    def get_waveform_math(self, obj):
        return json.loads(obj.waveform_math) if obj.waveform_math else []

    def get_autoset_menu(self, obj):
        return json.loads(obj.autoset_menu) if obj.autoset_menu else []

    def get_display_characteristics(self, obj):
        return json.loads(obj.display_characteristics) if obj.display_characteristics else []

    def get_environmental_safety(self, obj):
        return json.loads(obj.environmental_safety) if obj.environmental_safety else []

    def get_signal_sampling(self, obj):
        return json.loads(obj.signal_sampling) if obj.signal_sampling else []

    def get_amplitude_range(self, obj):
        return json.loads(obj.amplitude_range) if obj.amplitude_range else []

    def get_offset_range(self, obj):
        return json.loads(obj.offset_range) if obj.offset_range else []

    def get_sine_distortion(self, obj):
        return json.loads(obj.sine_distortion) if obj.sine_distortion else []

    def get_pulse_width(self, obj):
        return json.loads(obj.pulse_width) if obj.pulse_width else []

    def get_reference_input(self, obj):
        return json.loads(obj.reference_input) if obj.reference_input else []

    def get_output_characteristics(self, obj):
        return json.loads(obj.output_characteristics) if obj.output_characteristics else []

    def get_input_characteristics(self, obj):
        return json.loads(obj.input_characteristics) if obj.input_characteristics else []

    def get_interface(self, obj):
        return json.loads(obj.interface) if obj.interface else []

    def get_parameters(self, obj):
        return json.loads(obj.parameters) if obj.parameters else []

    def get_pattern(self, obj):
        return json.loads(obj.pattern) if obj.pattern else []

    def get_input_output_ports(self, obj):
        return json.loads(obj.input_output_ports) if obj.input_output_ports else []

    def get_pressure_range(self, obj):
        return json.loads(obj.pressure_range) if obj.pressure_range else []

    def get_pressure_generation_measurement(self, obj):
        return json.loads(obj.pressure_generation_measurement) if obj.pressure_generation_measurement else []

    def get_measurement_accuracy(self, obj):
        return json.loads(obj.measurement_accuracy) if obj.measurement_accuracy else []

    class Meta:
        model = Instrument
        fields = '__all__'


class EquivalentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equivalent
        fields = '__all__'

class InstrumentFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstrumentFeature
        fields = '__all__'

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'file']

class CustomTokenObtainPairSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("No user with this email found.")

        if not user.check_password(password):
            raise serializers.ValidationError("Incorrect password.")

        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)

            return {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }

        raise serializers.ValidationError("Unable to log in with provided credentials.")