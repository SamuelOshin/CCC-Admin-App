# signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import TransferData, PostingHistory

@receiver(post_save, sender=TransferData)
def create_posting_history(sender, instance, created, **kwargs):
    if not created and instance.trf_status == 'Withdrawn':
        parish_directory_instance = instance.parishTo.parish

        # Create a PostingHistory entry
        PostingHistory.objects.create(
            clergy=instance.clergy,
            parish=parish_directory_instance,
            designation=instance.designation_to,
            date_of_entry=instance.trf_begin,
            date_of_exit=instance.trf_end
        )
