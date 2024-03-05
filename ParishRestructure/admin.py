from django.contrib import admin
from .models import Location, ParishRestructure, ParishRegistration, ParishDirectory

admin.site.register(Location)
admin.site.register(ParishRestructure)
admin.site.register(ParishRegistration)
admin.site.register(ParishDirectory)

    
# Register your models here.