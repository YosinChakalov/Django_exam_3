from django.urls import path
from .views import *

urlpatterns = [
    path("register/",register),
    path("login/",login),
    path("projects/",projects),
    path("tasks/",tasks),
    path("project_add/",project_add),
    path("task_add/",task_add),
    path("task/<int:pk>/",task_detail),
    path("project/<int:pk>/",project_detail),
    path("project_update/<int:pk>/",project_update),
    path("task_update/<int:pk>/",task_update),
    path("project_delete/<int:pk>/",project_delete),
    path("task_delete/<int:pk>/",task_delete),
    path("project_restore/<int:pk>/",project_restore),
    path("task_restore/<int:pk>/",task_restore),
    path("logout/",logout),
]
