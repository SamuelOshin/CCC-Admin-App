# Inside create_floating.py

from django.core.management.base import BaseCommand
from transfer.models import ClergyDetails, ClergyTrfbio

class Command(BaseCommand):
    help = 'Creates ClergyTrfbio instances for existing ClergyDetails objects'

    def handle(self, *args, **options):
        clergy_details = ClergyDetails.objects.all()
        for clergy in clergy_details:
            clergy_trfbio, created = ClergyTrfbio.objects.get_or_create(clergy=clergy)
            if created:
                # Update the floating status if it's a new instance
                clergy_trfbio.floating = True
                clergy_trfbio.save()
        self.stdout.write(self.style.SUCCESS('Successfully created ClergyTrfbio instances.'))

# to run 'python manage.py create_floating'