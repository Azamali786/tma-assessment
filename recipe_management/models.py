from django.db import models


class Ingredient(models.Model):
    """
    Represents a single ingredient that can be used in one or more recipes.

    Attributes:
        name (str): The name of the ingredient (e.g., "Salt", "Tomato").
    """
    name = models.CharField(max_length=100, help_text="Name of the ingredient")

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """
    Represents a recipe which contains a title and a set of ingredients.

    Attributes:
        title (str): The name or title of the recipe (e.g., "Spaghetti Bolognese").
        ingredients (ManyToMany): A many-to-many relationship with Ingredient.
    """
    title = models.CharField(max_length=100, help_text="Title of the recipe")
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        help_text="List of ingredients used in the recipe"
    )

    def __str__(self):
        return self.title
