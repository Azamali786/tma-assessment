from django.contrib import admin
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from .schema import schema

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from recipe_management.views import DRFAuthenticatedGraphQLView

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # ingredient related endpoints
    path("api/", include("recipe_management.urls", namespace="recipe_management")),
    
    # graphQL endpoints
    path('graphql/', DRFAuthenticatedGraphQLView.as_view(graphiql=True)),
]
