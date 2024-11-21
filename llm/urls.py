from django.urls import path
from llm.views import handle_command

urlpatterns = [
    path('command/', handle_command, name='handle_command'),
]
