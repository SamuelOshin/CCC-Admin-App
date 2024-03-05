from django.db import models

class Location(models.Model):
    LEVEL_CHOICES = [
        ('continent', 'Continent'),
        ('diocese', 'Diocese'),
        ('region', 'Region'),
        ('state', 'State'),
        ('area', 'Area'),
        ('district', 'District'),
        ('circuit', 'Circuit'),
        ('parish', 'Parish'),
    ]
    
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)

    def __str__(self):
        return self.name

class ParishDirectory(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    register_status = models.BooleanField(default=False)

    def __str__(self):
        return f" CCC {self.name}"
class ParishRegistration(models.Model):
    parish = models.OneToOneField(ParishDirectory, on_delete=models.CASCADE, null=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)  
    city = models.CharField(max_length=100, null=True, blank=True)
    diocese = models.ForeignKey(Location, on_delete=models.CASCADE)
    date_of_establishment = models.DateField(null=True, blank=True)
    founding_patron = models.CharField(max_length=100, null=True, blank=True)
    name_of_shepherd = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.CharField(max_length=25, null=True, blank=True)
    date_applied = models.DateTimeField(auto_now_add=True) 
    date_approved = models.DateTimeField(null=True, blank=True)
    date_issued_certificate = models.DateTimeField(null=True, blank=True)
    notes = models.CharField(max_length=255, null=True, blank=True)
    parish_picture = models.ImageField(upload_to='ParishRestructure/parish_pic', null=True, blank=True)
    application_for_registration = models.BooleanField(default=False)
    original_receipt_of_land = models.BooleanField(default=False)
    original_survey_plan = models.BooleanField(default=False)
    building_plan = models.BooleanField(default=False)
    sworn_affidavit = models.BooleanField(default=False)
    passport_photograph = models.BooleanField(default=False)
    approval_from_government_diaspora = models.BooleanField(default=False)
    payment_proof_of_auditorium = models.BooleanField(default=False)

    # @property
    # def is_registered(self):
    #     return self.parish.register_status if self.parish else False

    # def approve(self, user):
    #     self.parish.register_status = True
    #     self.parish.save()
    #     self.date_approved = timezone.now()
    #     self.save()
    #     Notifications.success(user, "Parish registration approved", f"{self.parish.name} has been approved for registration")
    #     ApprovalNotification(user, self).send()
        
    # class Meta:
    #     verbose_name = "Parish Registration"
    #     verbose_name_plural = "Parish Registrations"

    
    

    def save(self, *args, **kwargs):
        # Automatically create or update the corresponding Parish object
        parish, created = ParishDirectory.objects.get_or_create(name=self.parish.name, address=self.parish.address)
        self.parish = parish
        super(ParishRegistration, self).save(*args, **kwargs)

    def __str__(self):
        return f"Details for {self.parish.name}"


class ParishRestructure(models.Model):
    parish = models.ForeignKey(ParishDirectory, on_delete=models.CASCADE, null=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    address  = models.CharField(max_length=500)

    def __str__(self):
        return self.parish.name
    


