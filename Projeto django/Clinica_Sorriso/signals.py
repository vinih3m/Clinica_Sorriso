import os

from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.apps import apps


@receiver(pre_save)
def apagar_foto_antiga(sender, instance, **kwargs):
    """
    Apaga a foto antiga do Profile quando uma nova for enviada
    """

    # Garante que o signal só roda para o model Profile
    Profile = apps.get_model('Clinica_Sorriso', 'Profile')
    if sender != Profile:
        return

    # Se ainda não existe no banco, não há foto antiga
    if not instance.pk:
        return

    try:
        foto_antiga = Profile.objects.get(pk=instance.pk).foto
    except Profile.DoesNotExist:
        return

    foto_nova = instance.foto

    if foto_antiga and foto_antiga != foto_nova:
        if foto_antiga.path and os.path.isfile(foto_antiga.path):
            os.remove(foto_antiga.path)
