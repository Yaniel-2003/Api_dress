from rest_framework.views import APIView
from django.contrib.auth.hashers import check_password
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import authenticate
import secrets
from django.utils import timezone
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from ..models import Usuario

from ..serializers import UsuarioListSerializer, UsuarioWriteSerializer


#### INICIO Y REGISTRO DE SESION 

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Obtenermos el email y la contraseña directamente de la peticion

        # Obtenemos el email y contraseña validos 
        email = request.data.get('email')
        password = request.data.get('password_hash')

        # Validamos las credenciales 
        if not email or not password:
            return Response({'error': 'Faltan credenciales'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Buscamos al usuario
        usuario = Usuario.objects.filter(email=email).first()

        #Verrificamos que exista y la contraseña este haseada
        if usuario is None or not check_password(password, usuario.password_hash):
            return Response(
                {'error': 'Email o contraseña incorrectos'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Verificamos si la cuenta esta activa 
        if not usuario.activo:
            return Response(
                {'error': 'Usuario inactivo'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Generamos los token de la sesion 

        refresh = RefreshToken.for_user(usuario)

        # Retornamos los tokens y los datos del usuario
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'usuario': UsuarioListSerializer(usuario).data
        }, status=status.HTTP_200_OK)
    

#### CIERRE DE SESION 

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            #Obtenemos el refresh token de la peticion 
            refresh_token = request.data.get('refresh')

            # Si no es refres token lanzamos error 
            if not refresh_token:
                return Response(
                    {'error': 'Se requiere el token de refresh para cerrar sesión'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Agregamos el Refresh Token a la blacklist para invalidarlo  
            token = RefreshToken(refresh_token)
            #token.blacklist()

            # Retornamos los resultados 
            return Response(
                {'mensaje': 'Sesion cerrada correctamente'},
                status=status.HTTP_200_OK
            )
        
        except TokenError:
            return Response(
                {'error': 'El token es invalido o ya esta expirado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        

#### RECUPERACION DE CONTRASEÑA 