from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("chat/<int:conversation_id>/", views.home, name="conversation"),  # ✅ ADD
    path("new-chat/", views.new_chat, name="new_chat"),

    path("signup/", views.signup, name="signup"),

    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html"
        ),
        name="login"
    ),

    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("delete/<int:convo_id>/", views.delete_chat, name="delete_chat"),
    path("health/", views.health_check, name="health_check"),
]
