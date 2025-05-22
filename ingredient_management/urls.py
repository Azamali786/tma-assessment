from django.urls import path
from .views import list_ingredients


app_name = "ingredient_managment"


urlpatterns = [
    path("ingredients/", list_ingredients, name="list_ingredients")
]
