from rest_framework import serializers
from .models import Ingredient, Recipe

class IngredientSerializer(serializers.ModelSerializer):
    """
    Serializer for the Ingredient model.

    Serializes all fields of the Ingredient model,
    allowing conversion between Ingredient instances and JSON representations.
    """
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    """
    Serializer for the Recipe model.

    Serializes all fields of the Recipe model, including its many-to-many
    relationship with ingredients. Automatically handles nested representation
    using primary keys for ingredients.
    """
    class Meta:
        model = Recipe
        fields = '__all__'