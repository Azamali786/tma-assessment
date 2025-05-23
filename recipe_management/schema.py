import graphene
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from .models import Ingredient, Recipe
from .serializers import IngredientSerializer, RecipeSerializer
from graphql_jwt.decorators import login_required
from graphene import relay

from django_filters import FilterSet
from .models import Ingredient

class IngredientFilter(FilterSet):
    class Meta:
        model = Ingredient
        fields = {
            'name': ['exact', 'icontains', 'istartswith'],
        }
        # Alternatively, you can use 'exclude' instead of 'fields'
        # exclude = ['created_at', 'updated_at']

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

    def resolve_ingredient_count(self, info):
        return self.ingredients.count()

# Queries
class Query(graphene.ObjectType):
    all_ingredients = DjangoFilterConnectionField(IngredientType)
    recipe = graphene.Field(RecipeType, id=graphene.ID(required=True))

    # @login_required
    def resolve_all_ingredients(self, info, **kwargs):
        return Ingredient.objects.all()

    # @login_required
    def resolve_recipe(self, info, id):
        return Recipe.objects.get(pk=id)
    

# Mutations
class CreateIngredient(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)

    ingredient = graphene.Field(IngredientType)

    # @login_required
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

    # @login_required
    def mutate(self, info, id, name):
        ingredient = Ingredient.objects.get(pk=id)
        serializer = IngredientSerializer(ingredient, data={'name': name})
        serializer.is_valid(raise_exception=True)
        ingredient = serializer.save()
        return UpdateIngredient(ingredient=ingredient)

class DeleteIngredient(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    # @login_required
    def mutate(self, info, id):
        Ingredient.objects.filter(pk=id).delete()
        return DeleteIngredient(success=True)

class CreateRecipe(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        ingredient_ids = graphene.List(graphene.ID)

    recipe = graphene.Field(RecipeType)

    # @login_required
    def mutate(self, info, title, ingredient_ids=[]):
        recipe = Recipe.objects.create(title=title)
        recipe.ingredients.set(ingredient_ids)
        return CreateRecipe(recipe=recipe)

class AddIngredientsToRecipe(graphene.Mutation):
    class Arguments:
        recipe_id = graphene.ID(required=True)
        ingredient_ids = graphene.List(graphene.ID)

    recipe = graphene.Field(RecipeType)

    # @login_required
    def mutate(self, info, recipe_id, ingredient_ids):
        recipe = Recipe.objects.get(pk=recipe_id)
        recipe.ingredients.add(*ingredient_ids)
        return AddIngredientsToRecipe(recipe=recipe)

class RemoveIngredientsFromRecipe(graphene.Mutation):
    class Arguments:
        recipe_id = graphene.ID(required=True)
        ingredient_ids = graphene.List(graphene.ID)

    recipe = graphene.Field(RecipeType)

    # @login_required
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
