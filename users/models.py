from django.db import models
from django.contrib.auth.models import User
from PIL import Image

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    pic = models.ImageField(upload_to='userpics', null=True, blank=True, default='profile_pics/default.png')

    def __str__(self):
        return f'{self.user.username} Profile'

    # Override the save method of the model
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.pic:  # Check if a profile picture is provided
            img = Image.open(self.pic.path)  # Open image

            # Resize image if it's larger than 300x300
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)  # Resize image
                img.save(self.pic.path)  # Save it again and override the larger image
