from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Asignacion, CambioReparacion, Notificacion


@receiver(post_save, sender=Asignacion)
def notificar_nueva_asignacion(sender, instance, created, **kwargs):
    if created and instance.cliente.email:
        asunto = f'Te han asignado el equipo: {instance.equipo}'
        mensaje = (
            f'Hola {instance.cliente.nombre},\n\n'
            f'Se te ha asignado el equipo {instance.equipo}.\n'
            f'Serial: {instance.equipo.serial}\n'
            f'Fecha: {instance.fecha_asignacion.strftime("%d/%m/%Y %H:%M")}\n\n'
            f'Saludos.'
        )
        send_mail(
            subject=asunto,
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.cliente.email],
            fail_silently=True
        )
        Notificacion.objects.create(
            tipo='email',
            destinatario=instance.cliente.email,
            asunto=asunto,
            mensaje=mensaje,
            enviado=True
        )


@receiver(post_save, sender=CambioReparacion)
def notificar_reparacion(sender, instance, created, **kwargs):
    if created:
        asig = instance.equipo.asignaciones.filter(activa=True).first()
        if asig and asig.cliente.email:
            asunto = f'Reparacion registrada: {instance.equipo}'
            mensaje = (
                f'Su equipo {instance.equipo} ha sido registrado con una {instance.get_tipo_display()}.\n'
                f'Detalle: {instance.descripcion}\n'
                f'Tecnico: {instance.tecnico or "No asignado"}\n'
                f'Costo: Q{instance.costo}'
            )
            send_mail(
                subject=asunto,
                message=mensaje,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[asig.cliente.email],
                fail_silently=True
            )
            Notificacion.objects.create(
                tipo='email',
                destinatario=asig.cliente.email,
                asunto=asunto,
                mensaje=mensaje,
                enviado=True
            )
