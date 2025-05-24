import re

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

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
    
    name = serializers.CharField(
        validators=[
            validate_string_field,
            UniqueValidator(queryset=Ingredient.objects.all(), message="Ingredient with this name already exists.")
        ]
    )
    
    class Meta:
        model = Ingredient
        fields = '__all__'
        
    def update(self, instance, validated_data):
        """
        Prevent updating if the ingredient is associated with any recipe.
        """
        if instance.recipes.exists():
            raise serializers.ValidationError("This ingredient is associated with a recipe and cannot be updated.")
        
        # If not associated, allow update
        return super().update(instance, validated_data)


class RecipeSerializer(serializers.ModelSerializer):
    """
    Serializer for the Recipe model.

    Serializes all fields of the Recipe model, including its many-to-many
    relationship with ingredients. Automatically handles nested representation
    using primary keys for ingredients.
    """
    
    title = serializers.CharField(
        validators=[
            validate_string_field,
            UniqueValidator(queryset=Recipe.objects.all(), message="Recipe with this name already exists.")
        ]
    )
    ingredients = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        many=True,
        write_only=True,
    )
    
    class Meta:
        model = Recipe
        fields = '__all__'
        
    # def validate(self, data):
    #     ingredient_ids = data.get('ingredients', [])
    #     recipe = self.instance  # Will be set for updates

    #     if recipe:
    #         # Existing recipe: check for duplicates
    #         existing_ids = set(recipe.ingredients.values_list('id', flat=True))
    #         duplicate_ids = existing_ids.intersection(set(ingredient_ids))

    #         if duplicate_ids:
    #             names = Ingredient.objects.filter(id__in=duplicate_ids).values_list('name', flat=True)
    #             raise serializers.ValidationError({
    #                 'ingredient_ids': f"The following ingredients are already added to this recipe: {', '.join(names)}"
    #             })

    #     return data
        
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients', [])
        recipe = Recipe.objects.create(**validated_data)
        recipe.ingredients.set(ingredients)
        return recipe
