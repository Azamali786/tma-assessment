from django_filters import FilterSet

from .models import Ingredient, Recipe


class IngredientFilter(FilterSet):
    """
    FilterSet for the Ingredient model to support filtering in GraphQL queries.

    Allows filtering ingredients by their 'name' field using:
    - exact match
    - case-insensitive containment (icontains)
    - case-insensitive startswith (istartswith)
    """
    
    class Meta:
        model = Ingredient      # The Django model to filter
        fields = {
            'name': ['exact', 'icontains', 'istartswith'],  # Filters on the Ingredient name field
        }
      
        
class RecipeFilter(FilterSet):
    """
    FilterSet for the Recipe model to enable filtering in GraphQL queries.

    Supports filtering recipes by:
    - title with exact match, case-insensitive containment, and startswith filters
    - ingredient names using case-insensitive containment filter (filters recipes by related ingredients' names)
    """
    
    class Meta:
        model = Recipe
        fields = {
            'title': ['exact', 'icontains', 'istartswith'],     # Filters on the Recipe title field
            'ingredients__name': ['icontains'],     # Filter recipes by the name of related ingredients (many-to-many relationship)
        }
      