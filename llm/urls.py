from django.urls import path
from .views import ExecuteTaskView

urlpatterns = [
    path("execute-task/", ExecuteTaskView.as_view(), name="execute-task"),
]
