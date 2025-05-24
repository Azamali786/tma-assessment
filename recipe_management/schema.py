import graphene
from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType
from graphql import GraphQLError
from graphql_relay import from_global_id

from .filters import IngredientFilter, RecipeFilter
from .models import Ingredient, Recipe
from .serializers import IngredientSerializer, RecipeSerializer
from .utils import (
    decode_global_ids_with_labels,
    get_internal_id_from_global_id
)


class IngredientType(DjangoObjectType):
    """
    GraphQL type for the Ingredient model.

    This type exposes all fields from the Ingredient model and supports Relay's Node interface
    for global object identification. It also supports filtering via the specified filterset.
    """
    class Meta:
        model = Ingredient                  # The Django model this type represents
        interfaces = (relay.Node,)          # Enable Relay global node interface (provides `id` field as global ID)
        filterset_class = IngredientFilter  # Enables filtering support using DjangoFilterConnectionField
        fields = '__all__'   # Expose all model fields in the GraphQL schema
            
class RecipeType(DjangoObjectType):
    """
    GraphQL type for the Recipe model.

    Adds:
        ingredient_count (graphene.Int): A custom field that returns the number of ingredients in the recipe.
    """
    
    # Custom field to return the number of ingredients in a recipe
    ingredient_count = graphene.Int()

    class Meta:
        model = Recipe
        fields = '__all__'               # Include all fields from the Recipe model
        interfaces = (relay.Node,)       # Use Relay's global node interface for Relay compatibility
        filterset_class = RecipeFilter   # Enables filtering support using DjangoFilterConnectionField

    def resolve_ingredient_count(self, info):
        """
        Resolver for the `ingredient_count` field.

        Args:
            info: GraphQL execution context.

        Returns:
            int: Number of ingredients associated with the recipe.
        """
        return self.ingredients.count()

# Queries
class Query(graphene.ObjectType):
    """
    GraphQL Query class for retrieving ingredients and recipes.

    Fields:
        all_ingredients (DjangoFilterConnectionField): Returns a paginated, filterable list of all ingredients.
        all_recipes (DjangoFilterConnectionField): Returns a paginated, filterable list of all recipes.
        recipe (graphene.Field): Returns a single recipe by its global ID.
    """
    # GraphQL connection fields for listing all ingredients and recipes
    all_ingredients = DjangoFilterConnectionField(IngredientType)
    all_recipes = DjangoFilterConnectionField(RecipeType)  # ← Add this line
    
    # Field to retrieve a single recipe by ID
    recipe = graphene.Field(RecipeType, id=graphene.ID(required=True))

    def resolve_all_ingredients(self, info, **kwargs):
        """
        Resolver for fetching all ingredients.

        Returns:
            QuerySet: All Ingredient objects from the database.
        """
        return Ingredient.objects.all()
    
    def resolve_all_recipes(self, info, **kwargs):
        """
        Resolver for fetching all recipes.

        Returns:
            QuerySet: All Recipe objects from the database.
        """
        return Recipe.objects.all()

    def resolve_recipe(self, info, id):
        """
        Resolver for fetching a single recipe by global ID.

        Args:
            id (str): Global Relay ID of the recipe.

        Returns:
            Recipe: The recipe object matching the decoded primary key.

        Raises:
            GraphQLError: If the ID is invalid, node type is incorrect, or recipe is not found.
        """
        try:
            # Decode the global Relay ID into its type and internal database ID
            _type, internal_id = from_global_id(id)
            if not internal_id:
                raise GraphQLError("Invalid ID.")
            if _type != "RecipeType":
                raise GraphQLError("Invalid node type for Recipe.")
            
            # Fetch the recipe using the internal ID
            recipe = Recipe.objects.filter(pk=internal_id).first()
            if not recipe:
                raise GraphQLError("Recipe not found.")
            return recipe

        except Exception as e:
            raise GraphQLError(str(e))
    
# Mutations
class CreateIngredient(graphene.Mutation):
    """
    GraphQL Mutation to create a new ingredient.

    Arguments:
        name (graphene.String): The name of the ingredient to be created.

    Returns:
        ingredient (IngredientType): The newly created ingredient instance.
    """
    
    class Arguments:
        name = graphene.String(required=True)   # Name of the new ingredient

    ingredient = graphene.Field(IngredientType) # Output: the created ingredient

    def mutate(self, info, name):
        """
        Handles the mutation logic to create a new ingredient.

        Steps:
        1. Accept the name from arguments.
        2. Use DRF serializer to validate and save the new ingredient.
        3. Return the newly created ingredient object.

        Raises:
            GraphQLError: If validation fails.

        Returns:
            CreateIngredient: Mutation response containing the created ingredient.
        """
        
        serializer = IngredientSerializer(data={'name': name})  # Initialize serializer with input data
        serializer.is_valid(raise_exception=True)               # Validate the data and raise GraphQLError if invalid
        ingredient = serializer.save()                          # Save and retrieve the newly created ingredient object
        return CreateIngredient(ingredient=ingredient)          # Return the ingredient in mutation response

class UpdateIngredient(graphene.Mutation):
    """
    GraphQL Mutation to update the name of an existing ingredient.

    Arguments:
        id (graphene.ID): The global ID of the ingredient to update.
        name (graphene.String): The new name for the ingredient.

    Returns:
        ingredient (IngredientType): The updated ingredient instance.
    """
    
    class Arguments:
        id = graphene.ID(required=True)         # Global ID of the ingredient to update
        name = graphene.String(required=True)   # New name to set on the ingredient

    ingredient = graphene.Field(IngredientType) # Output field for the updated ingredient

    def mutate(self, info, id, name):
        """
        Handles the mutation logic to update an ingredient's name.

        Steps:
        1. Decode and validate the global ID (expects type 'IngredientType').
        2. Validate the input name using the serializer.
        3. Save the changes and return the updated ingredient instance.

        Raises:
            GraphQLError: If ID is invalid or serializer validation fails.

        Returns:
            UpdateIngredient: Mutation response containing the updated ingredient.
        """
        
        # Decode and validate the global ID, expecting it to be of type IngredientType
        ingredient, internal_id = get_internal_id_from_global_id(id, "IngredientType", "Ingredient ID")
        
        # Use serializer to validate and update the ingredient name
        serializer = IngredientSerializer(ingredient, data={'name': name})
        serializer.is_valid(raise_exception=True)
        
        # Save the validated data and return the updated ingredient
        ingredient = serializer.save()
        return UpdateIngredient(ingredient=ingredient)

class DeleteIngredient(graphene.Mutation):
    """
    GraphQL Mutation to delete an ingredient by its global ID.
    """
    
    class Arguments:
        id = graphene.ID(required=True, description="The global ID of the ingredient to delete.")

    success = graphene.Boolean(description="True if the ingredient was successfully deleted.")

    def mutate(self, info, id):
        """
        Handles the deletion of an Ingredient instance.

        Args:
            info (ResolveInfo): GraphQL execution context.
            id (str): The global ID of the ingredient to be deleted.

        Returns:
            DeleteIngredient: Mutation response with success flag.

        Raises:
            GraphQLError: If the ID is invalid or the ingredient doesn't exist.
        """
        try:
            # Decode and validate the global ID, expecting an IngredientType node
            ingredient, internal_id = get_internal_id_from_global_id(id, "IngredientType", "Ingredient ID")
            
            # Delete the ingredient
            ingredient.delete()
            
            # Return success response
            return DeleteIngredient(success=True)

        except Exception as e:
            # Raise a GraphQL-friendly error for the client
            raise GraphQLError(str(e))

class CreateRecipe(graphene.Mutation):
    """
    GraphQL Mutation to create a new Recipe with associated ingredients.
    """
    
    class Arguments:
        title = graphene.String(required=True, description="Title of the new recipe.")
        ingredient_ids = graphene.List(graphene.ID, description="List of global IDs for ingredients.")

    recipe = graphene.Field(RecipeType, description="The newly created recipe object.")

    def mutate(self, info, title, ingredient_ids=[]):
        """
        Handles the creation of a new Recipe instance.

        Args:
            info (ResolveInfo): GraphQL execution context.
            title (str): Title of the new recipe.
            ingredient_ids (List[str]): List of global IDs for ingredients.

        Returns:
            CreateRecipe: Mutation result containing the created recipe.

        Raises:
            GraphQLError: If ingredient IDs are invalid or validation fails.
        """
        
        try:
            # Ensure at least one ingredient is provided
            if not ingredient_ids:
                raise GraphQLError("Atleat one ingredient is necessary to create recipe.")
            
            # Decode and validate all global IDs, ensuring they match IngredientType
            _, internal_ids = decode_global_ids_with_labels(ingredient_ids, "IngredientType", "Ingredient ID")

            # Prepare data for serializer
            data = {
                'title': title,
                'ingredients': internal_ids
            }
            
            # Validate and save the recipe using Django Serializer
            serializer = RecipeSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            recipe = serializer.save()
            
            # Return the newly created recipe
            return CreateRecipe(recipe=recipe)

        except Exception as e:
            # Convert any exception to a GraphQL-friendly error
            raise GraphQLError(str(e))
        
class AddIngredientsToRecipe(graphene.Mutation):
    """
    GraphQL Mutation to add one or more ingredients to an existing recipe.
    """
    
    class Arguments:
        recipe_id = graphene.ID(required=True, description="Global ID of the recipe.")
        ingredient_ids = graphene.List(graphene.ID, description="List of global IDs for ingredients to add.")

    recipe = graphene.Field(RecipeType, description="The updated recipe after adding ingredients.")

    def mutate(self, info, recipe_id, ingredient_ids):
        """
        Handles the addition of ingredients to a recipe.

        Args:
            info (ResolveInfo): GraphQL execution context.
            recipe_id (str): Global ID of the recipe to update.
            ingredient_ids (List[str]): List of global IDs for ingredients to be added.

        Returns:
            AddIngredientsToRecipe: Mutation result containing the updated recipe.

        Raises:
            GraphQLError: If IDs are invalid or serializer validation fails.
        """

        try:
            # Ensure ingredient list is not empty
            if not ingredient_ids:
                raise GraphQLError("At least one ingredient ID must be provided.")
            
            # Decode and validate the recipe global ID and fetch the instance
            recipe, internal_id = get_internal_id_from_global_id(recipe_id, "RecipeType", "Recipe ID")
            
            # Decode and validate each ingredient ID
            _, internal_ingredient_ids = decode_global_ids_with_labels(ingredient_ids, "IngredientType", "Ingredient ID")
            
            # Prepare data for partial update of the recipe 
            data = {
                'ingredients': internal_ingredient_ids
            }
            
            # Use the RecipeSerializer to validate and perform the update
            serializer = RecipeSerializer(instance=recipe, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            recipe = serializer.save()
            
            # Return the updated recipe
            return AddIngredientsToRecipe(recipe=recipe)

        except Exception as e:
            # Catch and format any exception as a GraphQL-friendly error
            raise GraphQLError(str(e))
        
class RemoveIngredientsFromRecipe(graphene.Mutation):
    """
    GraphQL Mutation to remove one or more ingredients from an existing recipe.
    """
    
    class Arguments:
        recipe_id = graphene.ID(required=True, description="Global ID of the recipe.")
        ingredient_ids = graphene.List(graphene.ID, description="List of global IDs for ingredients to remove.")

    recipe = graphene.Field(RecipeType, description="The updated recipe after removing ingredients.")

    def mutate(self, info, recipe_id, ingredient_ids):
        """
        Handles the removal of specified ingredients from a recipe.

        Args:
            info (ResolveInfo): GraphQL execution context.
            recipe_id (str): Global ID of the recipe from which ingredients will be removed.
            ingredient_ids (List[str]): List of global IDs of the ingredients to remove.

        Returns:
            RemoveIngredientsFromRecipe: Mutation result containing the updated recipe.

        Raises:
            GraphQLError: If validation or decoding of IDs fails.
        """

        try:
            # Ensure ingredient list is not empty
            if not ingredient_ids:
                raise GraphQLError("At least one ingredient ID must be provided.")
            
            # Decode and validate the recipe global ID, and fetch the recipe instance
            recipe, internal_id = get_internal_id_from_global_id(recipe_id, "RecipeType", "Recipe ID")
            
            # Decode and validate the ingredient global IDs
            _, internal_ingredient_ids = decode_global_ids_with_labels(ingredient_ids, "IngredientType", "Ingredient ID")
                
            # Remove the specified ingredients from the recipe
            recipe.ingredients.remove(*internal_ingredient_ids)
            
            # Return the updated recipe
            return RemoveIngredientsFromRecipe(recipe=recipe)

        except Exception as e:
            # Catch any exception and raise it as a GraphQL-friendly error
            raise GraphQLError(str(e))
        
class Mutation(graphene.ObjectType):
    """
    Root GraphQL Mutation class that aggregates all mutation operations 
    related to Ingredients and Recipes.

    Exposes fields to:
    - Create, update, and delete ingredients.
    - Create a recipe.
    - Add or remove ingredients from a recipe.
    """
    
    create_ingredient = CreateIngredient.Field()    # Mutation to create a new ingredient
    update_ingredient = UpdateIngredient.Field()    # Mutation to update an existing ingredient
    delete_ingredient = DeleteIngredient.Field()    # Mutation to delete an ingredient by ID

    create_recipe = CreateRecipe.Field()    # Mutation to create a new recipe with ingredients
    add_ingredients_to_recipe = AddIngredientsToRecipe.Field()  # Mutation to add ingredients to a recipe
    remove_ingredients_from_recipe = RemoveIngredientsFromRecipe.Field()    # Mutation to remove ingredients from a recipe
