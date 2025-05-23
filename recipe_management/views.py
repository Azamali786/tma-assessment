from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response


from graphene_django.views import GraphQLView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin

from graphene_django.views import GraphQLView

import rest_framework
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.settings import api_settings
from rest_framework.exceptions import AuthenticationFailed
from django.http import JsonResponse

@method_decorator(csrf_exempt, name='dispatch')
class DRFAuthenticatedGraphQLView(GraphQLView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JsonResponse(
                {"message": "Authentication token not provided."}, status=401
            )

        for authenticator in self.authentication_classes:
            try:
                auth_instance = authenticator()
                user_auth_tuple = auth_instance.authenticate(request)
                if user_auth_tuple is not None:
                    request.user, _ = user_auth_tuple
                    break
            except AuthenticationFailed as e:
                return JsonResponse({"message": str(e)}, status=401)

        if not request.user or not request.user.is_authenticated:
            return JsonResponse(
                {"message": "Invalid or expired token."}, status=401
            )

        return super().dispatch(request, *args, **kwargs)


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})