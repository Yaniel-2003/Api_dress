from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from django.utils.translation import gettext_lazy as _
from core.models import Usuario

class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        """
        Sobrescribimos este método para que JWT busque en nuestro modelo Usuario
        en lugar del modelo User por defecto de Django.
        """
        try:
            # Obtenemos el ID del token (que en settings lo llamaste 'user_id')
            user_id = validated_token['user_id']
        except KeyError:
            raise AuthenticationFailed(_('El Token no contiene el ID del usuario'))

        try:
            # Buscamos en NUESTRO modelo personalizado
            user = Usuario.objects.get(idusuario=user_id)
        except Usuario.DoesNotExist:
            raise AuthenticationFailed(_('Usuario no encontrado'), code='user_not_found')

        if not user.activo:
            raise AuthenticationFailed(_('El usuario está inactivo'), code='user_inactive')

        return user