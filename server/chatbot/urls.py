from django.urls import path, include
from .views import TestConnectionAPI
from .views import CustomUserViewSet, ConversationViewSet, MessageViewSet
from .views import PasswordResetRequestView, PasswordResetConfirmView,InstrumentViewSet, EquivalentViewSet, InstrumentFeatureViewSet
from .views import AccessRequestCreateView, AccessRequestListView, AccessRequestApproveView, AccessRequestRejectView
from rest_framework.routers import DefaultRouter
from .views import DocumentUploadView,DocumentListView,DocumentDeleteView,AskQuestionView,getCurrentUser

router = DefaultRouter()
router.register(r'users', CustomUserViewSet)
router.register(r'conversations', ConversationViewSet)
router.register(r'messages', MessageViewSet)
router.register(r'instruments', InstrumentViewSet)
router.register(r'equivalents', EquivalentViewSet)
router.register(r'instrument_features', InstrumentFeatureViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('test/', TestConnectionAPI.as_view(), name='test-connection'),
    path('password-reset-request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('access-requests/', AccessRequestCreateView.as_view(), name='access_request_create'),
    path('access-requests/list/', AccessRequestListView.as_view(), name='access_request_list'),
    path('access-requests/approve/<int:pk>/', AccessRequestApproveView.as_view(), name='access_request_approve'),
    path('access-requests/reject/<int:pk>/', AccessRequestRejectView.as_view(), name='access_request_reject'),
    path('documents/upload/', DocumentUploadView.as_view(), name='document-upload'),
    path('documents/', DocumentListView.as_view(), name='document-list'),
    path('documents/<int:pk>/', DocumentDeleteView.as_view(), name='document-delete'),
    path('ask/', AskQuestionView.as_view(), name='ask-question'),
    path('current-user/', getCurrentUser.as_view(), name='current-user'),
]