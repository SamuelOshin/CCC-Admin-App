from django.db import models
from clergy_registration.models import ClergyDetails
from ParishRestructure.models import ParishDirectory
from ParishRestructure.models import ParishRestructure
from datetime import date
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class PostingHistory(models.Model):
    clergy = models.ForeignKey(ClergyDetails, on_delete=models.CASCADE, null=True, blank=True)
    parish = models.ForeignKey(ParishDirectory, on_delete=models.CASCADE, null=True)
    designation = models.CharField(max_length=50, choices=[
        ('Head of Diocese', 'Head of Diocese'),
        ('State Evangelist', 'State Evangelist'),
        ('Regional Evangelist', 'Regional Evangelist'),
        ('Divisional Evangelist', 'Divisional Evangelist'),
        ('Area Evangelist', 'Area Evangelist'),
        ('District Evangelist', 'District Evangelist'),
        ('Zonal Evangelist', 'Zonal Evangelist'),
        ('Shepherd in Charge', 'Shepherd in Charge'),
        ('Assistant Shepherd', 'Assitant Shepherd'),
        ('Church Worker', 'Church Worker'),
        ('Church Prophet/ess', 'Church Prophet/ess'),
    ]) 
    date_of_entry = models.DateField()
    date_of_exit = models.DateField()
    purpose = models.CharField(max_length=250, null=True)

    class Meta:
        db_table = 'posting_history'

    def __str__(self):
        return self.clergy.last_name + ' ' + self.parish.name + ' ' + self.designation

class ClergyTrfbio(models.Model):
    clergy = models.OneToOneField(ClergyDetails, on_delete=models.CASCADE, null=True, blank=True)
    floating = models.BooleanField(default=True)

    class Meta:
        db_table = 'clergy_trfbio'

    def update_floating_status(self):
        latest_transfer = self.clergy.transferdata_set.order_by('-date_transfered').first()

        if latest_transfer:
            if latest_transfer.trf_status == 'Withdrawn' and not latest_transfer.trf_extended:
                self.floating = True
            else:
                self.floating = False
        else:
            self.floating = False

        self.save()

# Signal receiver to create ClergyTrfbio instance for each new ClergyDetails object
@receiver(post_save, sender=ClergyDetails)
def create_clergy_trfbio(sender, instance, created, **kwargs):
    if created:
        ClergyTrfbio.objects.create(clergy=instance, floating=True)        

class TransferData(models.Model):
    clergy = models.ForeignKey(ClergyDetails, on_delete=models.CASCADE, null=True, blank=True)
    parishFrm = models.ForeignKey(ParishRestructure, on_delete=models.CASCADE, null=True, related_name='parishFrm')
    parishTo = models.ForeignKey(ParishRestructure, on_delete=models.CASCADE, null=True, related_name='parishTo')
    date_transfered = models.DateField()
    trf_begin = models.DateField()
    trf_end = models.DateField()
    trf_status = models.CharField(max_length=50, choices=[
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Withdrawn', 'Withdrawn'),
    ])
    designation_frm = models.CharField(max_length=50, choices=[
        ('Head of Diocese', 'Head of Diocese'),
        ('State Evangelist', 'State Evangelist'),
        ('Regional Evangelist', 'Regional Evangelist'),
        ('Divisional Evangelist', 'Divisional Evangelist'),
        ('Area Evangelist', 'Area Evangelist'),
        ('District Evangelist', 'District Evangelist'),
        ('Zonal Evangelist', 'Zonal Evangelist'),
        ('Shepherd in Charge', 'Shepherd in Charge'),
        ('Assistant Shepherd', 'Assitant Shepherd'),
        ('Church Worker', 'Church Worker'),
        ('Church Prophet/ess', 'Church Prophet/ess'),
    ], null=True, blank=True) 
    designation_to = models.CharField(max_length=50, choices=[
        ('Head of Diocese', 'Head of Diocese'),
        ('State Evangelist', 'State Evangelist'),
        ('Regional Evangelist', 'Regional Evangelist'),
        ('Divisional Evangelist', 'Divisional Evangelist'),
        ('Area Evangelist', 'Area Evangelist'),
        ('District Evangelist', 'District Evangelist'),
        ('Zonal Evangelist', 'Zonal Evangelist'),
        ('Shepherd in Charge', 'Shepherd in Charge'),
        ('Assistant Shepherd', 'Assitant Shepherd'),
        ('Church Worker', 'Church Worker'),
        ('Church Prophet/ess', 'Church Prophet/ess'),
    ], null=True, blank=True) 
    trf_extended = models.BooleanField(default=False)
    extended_date = models.DateField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'transfer_data'

    # Override the save method to set date_transfered only on creation
    def save(self, *args, **kwargs):
        if not self.id:  # If it's a new object
            self.date_transfered = timezone.now().date()  # Set current date
        super().save(*args, **kwargs)

    @property
    def days_in_position(self):
        return (self.trf_end - self.trf_begin).days
    @property
    def days_left(self):
        today = date.today()
        if self.trf_begin != today:
            return None
        duration = (self.trf_end - self.trf_begin).days
        days_left = (self.trf_end - today).days
        return days_left if days_left >= 0 else 0

def __str__(self):
    parishFrm_name = self.parishFrm.parish.name if self.parishFrm else "Unknown"
    parishTo_name = self.parishTo.parish.name if self.parishTo else "Unknown"

    return f"{self.clergy.last_name}, From: {parishFrm_name}, To: {parishTo_name}, {self.date_transfered.strftime('%d-%m-%Y')}, {self.trf_status}"


