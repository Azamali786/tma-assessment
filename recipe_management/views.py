import json

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from graphene_django.views import GraphQLView
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class CustomAuthToken(ObtainAuthToken):
    """
    Custom endpoint for obtaining auth token using username/password.

    Overrides the default DRF ObtainAuthToken POST method to:
    - Validate credentials.
    - Return a token key on success.
    """
    def post(self, request, *args, **kwargs):
        """
        Handles POST requests to generate or retrieve a token for a user.

        Args:
            request (HttpRequest): The HTTP request with login credentials.

        Returns:
            Response: JSON containing the token key on successful authentication.

        Raises:
            ValidationError: If provided credentials are invalid.
        """
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})


@method_decorator(csrf_exempt, name='dispatch')
class DRFAuthenticatedGraphQLView(GraphQLView):
    """
    GraphQL view with DRF Token Authentication and permission enforcement.

    Supports:
    - Unauthenticated GET requests for the GraphiQL interface (HTML).
    - Unauthenticated POST requests containing introspection queries.
    - Requires a valid token for all other POST requests.

    This view integrates DRF TokenAuthentication and IsAuthenticated permission checks
    to secure the GraphQL API endpoint while allowing introspection and the GraphiQL IDE
    without authentication.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        """
        Overrides the dispatch method to implement:
        - Unauthenticated access for GraphiQL (GET + Accept: text/html).
        - Unauthenticated access for introspection queries (POST with 'IntrospectionQuery').
        - Token authentication for all other requests.

        Args:
            request (HttpRequest): The HTTP request instance.
            *args, **kwargs: Additional arguments passed to parent dispatch.

        Returns:
            HttpResponse: The appropriate response based on authentication and permissions.
        """

        # Allow unauthenticated GET requests for GraphiQL interface (accept header text/html)
        if request.method == "GET" and "text/html" in request.META.get("HTTP_ACCEPT", ""):
            return super().dispatch(request, *args, **kwargs)

        # Allow unauthenticated POST requests if the query is an introspection query
        if request.method == "POST":
            try:
                body = json.loads(request.body.decode("utf-8"))
                query = body.get("query", "")
                if "IntrospectionQuery" in query:
                    return super().dispatch(request, *args, **kwargs)
            except Exception:
                # If body is invalid JSON or query is missing, fall through to authentication
                pass

        # For all other requests, require Authorization token in header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse(
                {"message": "Authentication token not provided."},
                status=401
            )

        # Attempt to authenticate using configured authentication classes
        for authenticator in self.authentication_classes:
            try:
                auth_instance = authenticator()
                user_auth_tuple = auth_instance.authenticate(request)
                if user_auth_tuple is not None:
                    request.user, _ = user_auth_tuple
                    break
            except AuthenticationFailed as e:
                # Return 401 with the error message if authentication fails
                return JsonResponse({"message": str(e)}, status=401)

        # If user is not authenticated after checking tokens, return 401
        if not request.user or not request.user.is_authenticated:
            return JsonResponse({"message": "Invalid or expired token."}, status=401)

        # If authenticated, proceed with the normal dispatch flow
        return super().dispatch(request, *args, **kwargs)