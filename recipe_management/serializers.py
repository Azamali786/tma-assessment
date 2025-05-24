import re

from rest_framework import serializers

from .models import Ingredient, Recipe


def validate_string_field(value):
    """
    Validate that a string field meets the following criteria:

    - Must be at least 2 characters long.
    - Must not consist solely of numeric characters.
    - Must not consist solely of special characters.
    
    Parameters:
        value (str): The string input to validate.
    
    Returns:
        str: The validated input string.
    
    Raises:
        serializers.ValidationError: If the input fails any of the validation checks.
    """
    
    if len(value) < 2:
        raise serializers.ValidationError("Must be at least 2 characters long.")
    if value.isdigit():
        raise serializers.ValidationError("Must not be only numbers.")
    if re.fullmatch(r'[^\w\s]+', value):  # matches only special characters
        raise serializers.ValidationError("Must not be only special characters.")
    return value


class IngredientSerializer(serializers.ModelSerializer):
    """
    Serializer for the Ingredient model.

    Serializes all fields of the Ingredient model,
    allowing conversion between Ingredient instances and JSON representations.
    """
    
    name = serializers.CharField(validators=[validate_string_field])
    
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
    
    title = serializers.CharField(validators=[validate_string_field])
    ingredients = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        many=True,
        write_only=True,
    )
    
    class Meta:
        model = Recipe
        fields = '__all__'
        
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients', [])
        recipe = Recipe.objects.create(**validated_data)
        recipe.ingredients.set(ingredients)
        return recipe
