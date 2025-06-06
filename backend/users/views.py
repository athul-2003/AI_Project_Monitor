from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token
from .serializers import RegisterSerializer
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.views import ObtainAuthToken

class RegisterUser(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginUser(ObtainAuthToken):
    permission_classes = [AllowAny]

    # def post(self, request, *args, **kwargs):
    #     serializer = self.serializer_class(data=request.data, context={'request': request})
    #     serializer.is_valid(raise_exception=True)
    #     user = serializer.validated_data['user']
    #     token, created = Token.objects.get_or_create(user=user)
    #     login(request, user)  # Log user into Django session
    #     return Response({'token': token.key}, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()  # Deletes the token
            return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)
        except:
            return Response({"error": "Logout failed."}, status=status.HTTP_400_BAD_REQUEST)

    # def post(self, request):
    #     try:
    #         request.user.auth_token.delete()  # Deletes the token
    #         logout(request)  # Clears Django session
    #         return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)
    #     except:
    #         return Response({"error": "Logout failed."}, status=status.HTTP_400_BAD_REQUEST)



# django views













