from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.contrib.auth.models import User
from .models import Conversation, Message, AccessRequest,CustomUser
from .serializers import CustomUserSerializer, ConversationSerializer, MessageSerializer, AccessRequestSerializer
from rest_framework import viewsets
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from .serializers import PasswordResetRequestSerializer, PasswordResetConfirmSerializer
from .permissions import IsAdmin
from .utils import send_password_reset_email
from django.conf import settings
from rest_framework.parsers import MultiPartParser, FormParser
from .services import handle_user_question
from django.forms.models import model_to_dict
import uuid

class TestConnectionAPI(APIView):
    """
    Test API for checking the connectivity of the chatbot service.
    """
    permission_classes = [AllowAny]
    def get(self, request, format=None):
        return Response({'status': 'success', 'message': 'Chatbot API is reachable'}, status=status.HTTP_200_OK)

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
        
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class PasswordResetRequestView(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'detail': 'Password reset link sent.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'Password has been reset.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class AccessRequestCreateView(generics.CreateAPIView):
    queryset = AccessRequest.objects.all()
    serializer_class = AccessRequestSerializer

class AccessRequestListView(generics.ListAPIView):
    queryset = AccessRequest.objects.all()
    serializer_class = AccessRequestSerializer
    permission_classes = [IsAdmin]

class AccessRequestApproveView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        try:
            access_request = AccessRequest.objects.get(pk=pk)
            access_request.status = 'approved'
            access_request.save()
            
            # Générer un mot de passe par défaut
            default_password = str(uuid.uuid4())

            data = {
                'password': default_password,
                'email': access_request.email,
                'first_name': access_request.first_name,
                'last_name': access_request.last_name,
                'profile': access_request.profile,
                'site': access_request.site,
                'role': 'user',
            }
            
            # Utiliser le sérialiseur pour créer l'utilisateur
            user_serializer = CustomUserSerializer(data=data)
            if user_serializer.is_valid():
                user = user_serializer.save()

                # Envoyer un email pour réinitialiser le mot de passe
                reset_url = f"{settings.FRONTEND_URL}/reset-password"
                send_password_reset_email(user, reset_url)

                return Response({'detail': 'Access request approved and user created.'}, status=status.HTTP_200_OK)
            else:
                return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except AccessRequest.DoesNotExist:
            return Response({'error': 'Access request not found.'}, status=status.HTTP_404_NOT_FOUND)
        
class AccessRequestRejectView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        try:
            access_request = AccessRequest.objects.get(pk=pk)
            if access_request.status == 'approved':
                return Response({'error': 'Cannot reject an already approved access request.'}, status=status.HTTP_400_BAD_REQUEST)

            access_request.status = 'rejected'
            access_request.save()
            return Response({'detail': 'Access request rejected.'}, status=status.HTTP_200_OK)
        except AccessRequest.DoesNotExist:
            return Response({'error': 'Access request not found.'}, status=status.HTTP_404_NOT_FOUND)
        
class getCurrentUser(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_serialized = CustomUserSerializer(user).data
        return Response(user_serialized, status=status.HTTP_200_OK)

class AskQuestionView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):

        user = request.user
        question = request.data.get('question')
        conversation_id = request.data.get('conversation_id', None)
        
        if not question:
            return Response({'error': 'Question is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Rechercher une conversation existante si conversation_id est fourni
        if conversation_id:
            try:
                conversation = Conversation.objects.get(id=conversation_id, user=user)
            except Conversation.DoesNotExist:
                return Response({'error': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Créer une nouvelle conversation si conversation_id n'est pas fourni
            conversation = Conversation.objects.create(user=user)

        try:
            result = handle_user_question(user, question, conversation)
            conversation_serializer = ConversationSerializer(result)
            return Response({
                'ai_response': result
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)