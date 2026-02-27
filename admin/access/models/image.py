from django.db import models

class Image(models.Model):
    """
    Model to store images locally. 
    Images are uploaded to the 'images/' directory within your configured MEDIA_ROOT.
    """
    image_id = models.CharField(
        max_length=100, 
        unique=True, 
        help_text="Unique identifier to retrieve the image (e.g., 'logo_primary')"
    )
    image_file = models.ImageField(upload_to='images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.image_id
