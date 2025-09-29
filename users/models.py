from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.core.files.base import ContentFile
from io import BytesIO
import os


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    pic = models.ImageField(upload_to='userpics', null=True, blank=True, default='profile_pics/default.png')
    password_changed = models.BooleanField(default=False, help_text="Indicates if user has changed their initial password")

    def __str__(self):
        return f'{self.user.username} Profile'

    # Override the save method of the model
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.pic and self.pic.name != 'profile_pics/default.png':  # Check if a profile picture is provided and not the default
            try:
                # Open image from storage (works with both local and cloud storage)
                img = Image.open(self.pic.open())

                # Resize image if it's larger than 300x300
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)  # Resize image

                    # Save the resized image to a BytesIO buffer
                    buffer = BytesIO()
                    img.save(buffer, format=img.format or 'JPEG')
                    buffer.seek(0)

                    # Create a ContentFile from the buffer with just the filename (not full path)
                    filename = os.path.basename(self.pic.name)
                    resized_content = ContentFile(buffer.getvalue(), name=filename)

                    # Save the resized image back to storage, replacing the original
                    self.pic.save(filename, resized_content, save=False)

            except Exception as e:
                # If image processing fails, log the error but don't break the save
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to process profile image for user {self.user}: {e}")
                # Continue with the save operation
