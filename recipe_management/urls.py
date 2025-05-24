from django.urls import path

from .views import CustomAuthToken, ReadmeAPIView

app_name = "recipe_management"


urlpatterns = [
    path('token-auth/', CustomAuthToken.as_view(), name="auth_token"),
    path('readme/', ReadmeAPIView.as_view(), name='readme-api'),
]