from graphql import GraphQLError
from graphql_relay import from_global_id
from .constants import NUMBER_TRACKER
from .models import Ingredient, Recipe


def get_internal_id_from_global_id(global_id, expected_type, label="ID"):
    """
    Decodes a global ID and validates its type.

    Args:
        global_id (str): The base64-encoded global ID.
        expected_type (str): The expected GraphQL node type (e.g., "RecipeType").
        label (str): Label for error message clarity.

    Returns:
        int: Internal (database) ID.

    Raises:
        GraphQLError: If ID is invalid or type mismatched.
    """
    try:
        _type, internal_id = from_global_id(global_id)
        if not internal_id:
            raise GraphQLError(f"{label} is invalid.")
        if _type != expected_type:
            raise GraphQLError(f"Invalid node type for {label}. Expected '{expected_type}', got '{_type}'.")
        elif _type=="IngredientType":
            ingredient = Ingredient.objects.filter(pk=internal_id).first()
            if not ingredient:
                raise GraphQLError(f"{label} not found.")
            else:
                return (ingredient, int(internal_id))
        else:
            recipe = Recipe.objects.filter(pk=internal_id).first()
            if not recipe:
                raise GraphQLError(f"{label} not found.")
            return (recipe, int(internal_id))
        
    except Exception as e:
        raise GraphQLError(str(e))


def decode_global_ids_with_labels(global_ids, expected_type, tracker_label="ID"):
    """
    Decodes and validates a list of global IDs using a number-to-label tracker.

    Args:
        global_ids (list): List of global IDs.
        expected_type (str): The expected GraphQL node type.
        tracker_label (str): Prefix used in error messages.

    Returns:
        list: Internal (database) IDs.

    Raises:
        GraphQLError: For any invalid or mismatched ID.
    """

    internal_ids = []
    Ingredient_hash = {
        "ingredient": Ingredient.objects.none()
    }
    for i, gid in enumerate(global_ids, start=1):
        label = NUMBER_TRACKER.get(i, f"{i}th")
        ingredient, internal_id = get_internal_id_from_global_id(gid, expected_type, f"{label} {tracker_label}")
        Ingredient_hash["ingredient"] = ingredient
        internal_ids.append(internal_id)
    return (ingredient, internal_ids)
