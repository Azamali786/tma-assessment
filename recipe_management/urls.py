from django.urls import path
from .views import list_ingredients


app_name = "recipe_management"


urlpatterns = [
    path("ingredients/", list_ingredients, name="list_ingredients")
]
