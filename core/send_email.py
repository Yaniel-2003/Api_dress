from django.core.mail import send_mail
from django.conf import settings

def enviar_reset_contraseña_email(usuario, uid, token):
    enlace = f"{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}"

    send_mail(
        subject="Recuperar contraseña",
        message=f"Hola {usuario.nombres}, entra a este nelace para cambiar tu contraseña: \n{enlace}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[usuario.email],
    )