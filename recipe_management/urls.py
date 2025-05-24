from django.urls import path

from .views import CustomAuthToken, ReadmeFileAPIView

app_name = "recipe_management"


urlpatterns = [
    path('token-auth/', CustomAuthToken.as_view(), name="auth_token"),
    path('readme/', ReadmeFileAPIView.as_view(), name='readme-api'),
]