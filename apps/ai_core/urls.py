from django.urls import path
from .views.audit_view import AIThreadAuditView

urlpatterns = [
    path('audit/<uuid:thread_id>/', AIThreadAuditView.as_view(), name='ai_thread_audit'),
]
