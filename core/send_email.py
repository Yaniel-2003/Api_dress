from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils.html import escape


def enviar_reset_contraseña_email(usuario, uid, token):
    enlace = f"{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}"
    nombre = escape(usuario.nombres)

    # Tiempo de vida del enlace (Django lo define en segundos, por defecto 3 días)
    horas = settings.PASSWORD_RESET_TIMEOUT // 3600
    vigencia = f"{horas // 24} días" if horas % 24 == 0 and horas >= 48 else f"{horas} horas"

    # Versión en texto plano: la ven los clientes de correo que no soportan HTML
    texto = (
        f"Hola {usuario.nombres},\n\n"
        "Recibimos una solicitud para restablecer la contraseña de tu cuenta en Dress Shopy.\n"
        f"Entra a este enlace para crear una nueva contraseña (válido por {vigencia}):\n\n"
        f"{enlace}\n\n"
        "Si no fuiste tú, ignora este mensaje: tu contraseña seguirá siendo la misma.\n\n"
        "— Dress Shopy"
    )

    # Versión HTML: estilos en línea y tablas, que es lo que soportan todos los clientes de correo
    html = f"""\
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Restablecer contraseña</title>
</head>
<body style="margin:0;padding:0;background-color:#FAFAFA;font-family:Inter,-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;color:#09090B;">
  <div style="display:none;max-height:0;overflow:hidden;opacity:0;">
    Crea una nueva contraseña para tu cuenta de Dress Shopy.
  </div>

  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#FAFAFA;">
    <tr>
      <td align="center" style="padding:40px 16px;">

        <!-- Marca -->
        <table role="presentation" cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
          <tr>
            <td style="width:36px;height:36px;background-color:#09090B;border-radius:10px;text-align:center;vertical-align:middle;color:#FFFFFF;font-size:18px;font-weight:700;line-height:36px;">D</td>
            <td style="padding-left:10px;font-size:18px;font-weight:600;letter-spacing:-0.3px;color:#09090B;">
              Dress <span style="color:#059669;">Shopy</span>
            </td>
          </tr>
        </table>

        <!-- Tarjeta -->
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:480px;background-color:#FFFFFF;border:1px solid #E4E4E7;border-radius:16px;">
          <tr>
            <td style="height:4px;background-color:#10B981;border-radius:16px 16px 0 0;font-size:0;line-height:0;">&nbsp;</td>
          </tr>
          <tr>
            <td style="padding:36px 32px 32px 32px;">
              <h1 style="margin:0 0 12px 0;font-size:24px;font-weight:700;letter-spacing:-0.5px;color:#09090B;">Restablece tu contraseña</h1>
              <p style="margin:0 0 8px 0;font-size:15px;line-height:24px;color:#09090B;">Hola {nombre},</p>
              <p style="margin:0 0 28px 0;font-size:15px;line-height:24px;color:#71717A;">
                Recibimos una solicitud para restablecer la contraseña de tu cuenta.
                Pulsa el botón para crear una nueva.
              </p>

              <!-- Botón -->
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td align="center" style="background-color:#09090B;border-radius:12px;">
                    <a href="{enlace}" target="_blank"
                       style="display:block;padding:14px 24px;font-size:15px;font-weight:600;color:#FFFFFF;text-decoration:none;">
                      Crear nueva contraseña
                    </a>
                  </td>
                </tr>
              </table>

              <p style="margin:20px 0 0 0;font-size:13px;line-height:20px;color:#71717A;text-align:center;">
                Este enlace es válido por {vigencia}.
              </p>

              <hr style="border:none;border-top:1px solid #E4E4E7;margin:28px 0;">

              <p style="margin:0 0 6px 0;font-size:13px;line-height:20px;color:#71717A;">
                Si el botón no funciona, copia y pega este enlace en tu navegador:
              </p>
              <p style="margin:0;font-size:12px;line-height:18px;word-break:break-all;">
                <a href="{enlace}" target="_blank" style="color:#047857;text-decoration:underline;">{enlace}</a>
              </p>
            </td>
          </tr>
        </table>

        <!-- Pie -->
        <p style="max-width:480px;margin:24px 0 0 0;font-size:12px;line-height:18px;color:#71717A;text-align:center;">
          Si no solicitaste este cambio, ignora este correo: tu contraseña seguirá siendo la misma.
        </p>
        <p style="margin:12px 0 0 0;font-size:12px;color:#A1A1AA;text-align:center;">
          © Dress Shopy
        </p>

      </td>
    </tr>
  </table>
</body>
</html>"""

    correo = EmailMultiAlternatives(
        subject="Restablece tu contraseña de Dress Shopy",
        body=texto,
        from_email=f"Dress Shopy <{settings.DEFAULT_FROM_EMAIL}>",
        to=[usuario.email],
    )
    correo.attach_alternative(html, "text/html")
    correo.send()
