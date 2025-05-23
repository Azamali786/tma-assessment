import graphene
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from .models import Ingredient, Recipe
from .serializers import IngredientSerializer, RecipeSerializer
from graphql_jwt.decorators import login_required
from graphene import relay
from graphql_relay import from_global_id

from django_filters import FilterSet
from .models import Ingredient
from graphql import GraphQLError

class IngredientFilter(FilterSet):
    class Meta:
        model = Ingredient
        fields = {
            'name': ['exact', 'icontains', 'istartswith'],
        }
        
class RecipeFilter(FilterSet):
    class Meta:
        model = Recipe
        fields = {
            'title': ['exact', 'icontains', 'istartswith'],
            'ingredients__name': ['icontains'],  # Filter by ingredient name
        }

class IngredientType(DjangoObjectType):
    class Meta:
        model = Ingredient
        interfaces = (relay.Node,)
        filterset_class = IngredientFilter  # Add this line
        fields = '__all__'  # Explicitly declare fields

class RecipeType(DjangoObjectType):
    ingredient_count = graphene.Int()

    class Meta:
        model = Recipe
        fields = '__all__'
        interfaces = (relay.Node,)
        filterset_class = RecipeFilter  # ← Add this line

    def resolve_ingredient_count(self, info):
        return self.ingredients.count()

# Queries
class Query(graphene.ObjectType):
    all_ingredients = DjangoFilterConnectionField(IngredientType)
    all_recipes = DjangoFilterConnectionField(RecipeType)  # ← Add this line
    recipe = graphene.Field(RecipeType, id=graphene.ID(required=True))

    def resolve_all_ingredients(self, info, **kwargs):
        return Ingredient.objects.all()
    
    def resolve_all_recipes(self, info, **kwargs):
        return Recipe.objects.all()

    def resolve_recipe(self, info, id):
        return Recipe.objects.get(pk=id)
    

# Mutations
class CreateIngredient(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)

    ingredient = graphene.Field(IngredientType)

    def mutate(self, info, name):
        serializer = IngredientSerializer(data={'name': name})
        serializer.is_valid(raise_exception=True)
        ingredient = serializer.save()
        return CreateIngredient(ingredient=ingredient)

class UpdateIngredient(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)

    ingredient = graphene.Field(IngredientType)

    def mutate(self, info, id, name):
        _, internal_id = from_global_id(id)     # gives up type and database id (pk)
        ingredient = Ingredient.objects.get(pk=internal_id)
        serializer = IngredientSerializer(ingredient, data={'name': name})
        serializer.is_valid(raise_exception=True)
        ingredient = serializer.save()
        return UpdateIngredient(ingredient=ingredient)

class DeleteIngredient(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        try:
            _type, internal_id = from_global_id(id)
            if not internal_id:
                raise GraphQLError("Invalid ID")
            if _type != "IngredientType":
                raise GraphQLError("Invalid node type for Ingredient.")
            ingredient = Ingredient.objects.filter(pk=internal_id).first()
            if not ingredient:
                raise GraphQLError("Ingredient not found.")

            ingredient.delete()
            return DeleteIngredient(success=True)

        except Exception as e:
            raise GraphQLError(str(e))

class CreateRecipe(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        ingredient_ids = graphene.List(graphene.ID)

    recipe = graphene.Field(RecipeType)

    def mutate(self, info, title, ingredient_ids=[]):
        data = {
            'title': title,
            'ingredient_ids': ingredient_ids
        }
        serializer = RecipeSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save()
        return CreateRecipe(recipe=recipe)

class AddIngredientsToRecipe(graphene.Mutation):
    class Arguments:
        recipe_id = graphene.ID(required=True)
        ingredient_ids = graphene.List(graphene.ID)

    recipe = graphene.Field(RecipeType)

    def mutate(self, info, recipe_id, ingredient_ids):
        recipe = Recipe.objects.get(pk=recipe_id)
        recipe.ingredients.add(*ingredient_ids)
        return AddIngredientsToRecipe(recipe=recipe)

class RemoveIngredientsFromRecipe(graphene.Mutation):
    class Arguments:
        recipe_id = graphene.ID(required=True)
        ingredient_ids = graphene.List(graphene.ID)

    recipe = graphene.Field(RecipeType)

    def mutate(self, info, recipe_id, ingredient_ids):
        recipe = Recipe.objects.get(pk=recipe_id)
        recipe.ingredients.remove(*ingredient_ids)
        return RemoveIngredientsFromRecipe(recipe=recipe)

class Mutation(graphene.ObjectType):
    create_ingredient = CreateIngredient.Field()
    update_ingredient = UpdateIngredient.Field()
    delete_ingredient = DeleteIngredient.Field()
    create_recipe = CreateRecipe.Field()
    add_ingredients_to_recipe = AddIngredientsToRecipe.Field()
    remove_ingredients_from_recipe = RemoveIngredientsFromRecipe.Field()
