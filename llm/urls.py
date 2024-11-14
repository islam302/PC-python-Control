from django.urls import path
from .views import Main

urlpatterns = [
    path('process-command/', Main.as_view(), name='process-command'),
]
