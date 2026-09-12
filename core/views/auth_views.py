from rest_framework.views import APIView
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
from rest_framework import serializers
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from rest_framework.throttling import AnonRateThrottle


from ..models import Usuario
from ..send_email import enviar_reset_contraseña_email
from ..serializers import UsuarioListSerializer, UsuarioWriteSerializer, PasswordResetConfirmSerializers, PasswordResetRequestSerializer


#### INICIO Y REGISTRO DE SESION 

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Obtenermos el email y la contraseña directamente de la peticion

        # Obtenemos el email y contraseña validos 
        email = request.data.get('email')
        password = request.data.get('password')

        # Validamos las credenciales 
        if not email or not password:
            return Response({'error': 'Faltan credenciales'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Buscamos al usuario
        usuario = Usuario.objects.filter(email=email).first()

        #Verrificamos que exista y la contraseña este haseada
        if usuario is None or not usuario.check_password(password):
            return Response(
                {'error': 'Email o contraseña incorrectos'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Verificamos si la cuenta esta activa 
        if not usuario.is_active:
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
        refreh_token = request.data.get('refresh')

        if not refreh_token:
            return Response(
                {'error': 'Se requiere el token refrehs para cerra sesion'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            token = RefreshToken(refreh_token)
            token.blacklist()
        except TokenError: 
            return Response(
                {'error': 'El token es invalido o ya esta expirado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {'mensaje': 'Sesion cerrada correctamente'},
            status=status.HTTP_200_OK
        )

#### RECUPERACION DE CONTRASEÑA 

class RecoverPssword(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        serialiser = PasswordResetRequestSerializer(data=request.data)
        serialiser.is_valid(raise_exception=True)
        email = serialiser.validated_data['email']

        usuario = Usuario.objects.filter(email=email).first()

        if usuario is not None:
            uid = urlsafe_base64_encode(force_bytes(usuario.pk))
            token = default_token_generator.make_token(usuario)
            enviar_reset_contraseña_email(usuario, uid, token)
        return Response(
            {'mensaje': 'Si el correo existe, se envio un enlace a tu email'},
            status=status.HTTP_200_OK
        )

class ResetpasswordConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)

        uid = serializer.validated_data['uid']
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        try:
            pk = force_str(urlsafe_base64_decode(uid))
            usuario = Usuario.objects.get(pk=pk)
        except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
            return Response(
                {'error': 'Enlace invalido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not default_token_generator.check_token(usuario, token):
            return Response(
                {'error': 'El token es invalido o ha expirado '},
                status=status.HTTP_400_BAD_REQUEST
            )

        usuario.set_password(new_password)
        usuario.save()

        return Response(
            {'mensaje': 'Contraseña actualizada correctamente'},
            status=status.HTTP_200_OK
        )