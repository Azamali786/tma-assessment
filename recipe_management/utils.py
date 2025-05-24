from graphql import GraphQLError
from graphql_relay import from_global_id

from .constants import NUMBER_TRACKER
from .models import Ingredient, Recipe


def get_internal_id_from_global_id(global_id, expected_type, label="ID"):
    """
    Decode a Relay global ID to extract the internal database ID and validate the node type.

    Args:
        global_id (str): The Relay global ID (base64-encoded string).
        expected_type (str): Expected GraphQL node type name (e.g., "RecipeType", "IngredientType").
        label (str): Descriptive label for error messages to clarify which ID is being processed.

    Returns:
        tuple: (model_instance, int) where model_instance is the Django model object
               (Ingredient or Recipe) corresponding to the internal ID, and int is the internal ID.

    Raises:
        GraphQLError: Raised if the ID is invalid, the type doesn't match expected_type,
                      or the database object does not exist.
    """
    try:
        # Decode the global ID into type and internal database ID
        _type, internal_id = from_global_id(global_id)

        # Check that internal_id is present
        if not internal_id:
            raise GraphQLError(f"{label} is invalid.")

        # Check the decoded node type matches the expected GraphQL type
        if _type != expected_type:
            raise GraphQLError(
                f"Invalid node type for {label}. Expected '{expected_type}', got '{_type}'."
            )

        # Fetch and validate the corresponding model instance based on type
        if _type == "IngredientType":
            ingredient = Ingredient.objects.filter(pk=internal_id).first()
            if not ingredient:
                raise GraphQLError(f"{label} not found.")
            return (ingredient, int(internal_id))

        else:  # Assume RecipeType for all other cases
            recipe = Recipe.objects.filter(pk=internal_id).first()
            if not recipe:
                raise GraphQLError(f"{label} not found.")
            return (recipe, int(internal_id))

    except Exception as e:
        # Re-raise any exception as a GraphQLError for consistent error handling
        raise GraphQLError(str(e))


def decode_global_ids_with_labels(global_ids, expected_type, tracker_label="ID"):
    """
    Decode and validate a list of Relay global IDs, converting them to internal IDs.

    Args:
        global_ids (list): List of Relay global IDs (base64-encoded strings).
        expected_type (str): Expected GraphQL node type name for all IDs.
        tracker_label (str): Prefix label used in error messages to identify the ID group.

    Returns:
        tuple: (last_model_instance, list[int]) where last_model_instance is the
               model instance of the last decoded ID (usually the last ingredient),
               and list[int] is the list of all internal IDs extracted.

    Raises:
        GraphQLError: Raised if any ID is invalid, mismatched type, or database object missing.
    """
    internal_ids = []
    Ingredient_hash = {
        "ingredient": Ingredient.objects.none()  # Placeholder for last decoded ingredient
    }

    for i, gid in enumerate(global_ids, start=1):
        # Get human-friendly label for the position (e.g., "First", "Second", etc.)
        label = NUMBER_TRACKER.get(i, f"{i}th")

        # Decode and validate each global ID, expecting the given node type
        ingredient, internal_id = get_internal_id_from_global_id(
            gid, expected_type, f"{label} {tracker_label}"
        )

        # Store the last decoded ingredient (could be used outside)
        Ingredient_hash["ingredient"] = ingredient

        # Append internal ID to the list
        internal_ids.append(internal_id)

    # Return the last ingredient instance and the list of all internal IDs
    return (ingredient, internal_ids)
