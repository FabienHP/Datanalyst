from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.contrib.auth.models import User
from .models import Conversation, Message, AccessRequest, Instrument, Equivalent, InstrumentFeature, Document,CustomUser
from .serializers import CustomUserSerializer, ConversationSerializer, MessageSerializer, AccessRequestSerializer, InstrumentSerializer, EquivalentSerializer, InstrumentFeatureSerializer
from rest_framework import viewsets
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from .serializers import PasswordResetRequestSerializer, PasswordResetConfirmSerializer,DocumentSerializer
from .permissions import IsAdmin
from .utils import send_password_reset_email
from django.conf import settings
from .extraction import extract_information
from rest_framework.parsers import MultiPartParser, FormParser
from .chroma_utils import add_document_to_chroma, delete_document_from_chroma
from .utils import calculate_md5
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

class InstrumentViewSet(viewsets.ModelViewSet):
    queryset = Instrument.objects.all()
    serializer_class = InstrumentSerializer
    permission_classes = [IsAuthenticated]

class EquivalentViewSet(viewsets.ModelViewSet):
    queryset = Equivalent.objects.all()
    serializer_class = EquivalentSerializer
    permission_classes = [IsAuthenticated]

class InstrumentFeatureViewSet(viewsets.ModelViewSet):
    queryset = InstrumentFeature.objects.all()
    serializer_class = InstrumentFeatureSerializer
    permission_classes = [IsAuthenticated]

class DocumentUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_serializer = DocumentSerializer(data=request.data)
        try:
            if file_serializer.is_valid():
                # Vérifiez si le fichier est présent dans la requête
                if 'file' not in request.FILES:
                    return Response({'error': 'File not found in request.'}, status=status.HTTP_400_BAD_REQUEST)

                # Calculer le hachage MD5 du fichier
                file = request.FILES['file']
                md5_hash = calculate_md5(file)

                # Vérifier si un document avec ce hachage existe déjà
                if Document.objects.filter(md5_hash=md5_hash).exists():
                    return Response({'error': 'This document has already been uploaded.'}, status=status.HTTP_400_BAD_REQUEST)

                # Sauvegarder le document
                document = file_serializer.save(md5_hash=md5_hash)
                file_path = file_serializer.data['file']
                print(file_path)
                # Ajouter le document dans Chroma DB
                schema_type = request.data.get('schema')
                add_document_to_chroma(str(document.id), schema_type, file_path)

                instrument = extract_information(file_path, request.data.get('schema'))
                instrument_dict = model_to_dict(instrument)
                instrument_serialized = InstrumentSerializer(instrument).data
#                 result = 'Document uploaded successfully.'
                return Response(instrument_serialized, status=status.HTTP_201_CREATED)
            else:
                return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class DocumentListView(generics.ListAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAdmin]

class DocumentDeleteView(APIView):
    permission_classes = [IsAdmin]

    def delete(self, request, pk, format=None):
        try:
            document = Document.objects.get(pk=pk)
            document.file.delete(save=False)  # Supprime le fichier du stockage
            document.delete()  # Supprime l'enregistrement de la base de données
            # Supprimer le document de Chroma DB
            delete_document_from_chroma(str(document.id))
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Document.DoesNotExist:
            return Response({'error': 'Document not found.'}, status=status.HTTP_404_NOT_FOUND)
        
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