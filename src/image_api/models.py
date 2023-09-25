from io import BytesIO
import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.signing import Signer
from django.http import HttpResponse
from PIL import Image as PILImage


class Tier(models.Model):
    name = models.CharField(max_length=255, unique=True)
    thumbnail_sizes = models.JSONField()
    generate_expiring_links = models.BooleanField(default=False)
    original_image_link = models.BooleanField(default=False)


class CustomUser(AbstractUser):
    tier = models.ForeignKey(Tier, on_delete=models.CASCADE, null=True, blank=True)


class Image(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/')
    created_at = models.DateTimeField(auto_now_add=True)
    original_image_link = models.URLField(blank=True, null=True)


class Thumbnail(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    size = models.PositiveIntegerField()
    link_expires_in_seconds = models.PositiveIntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    thumbnail = models.ImageField(upload_to='thumbnails/')
    expiring_link = models.CharField(max_length=255, blank=True, null=True)

    def generate_expiring_link(self, expiration_seconds):
        signer = Signer()
        # Encode the thumbnail ID and expiration time as a signed string
        signed_data = signer.sign(self.id)

        # Convert expiration_seconds to an integer
        expiration_seconds = int(expiration_seconds)

        # Calculate the expiration timestamp
        expiration_timestamp = int(
            (datetime.datetime.now() + datetime.timedelta(seconds=expiration_seconds)).timestamp())

        expiring_link = f'https://example.com/your-expiring-link/{signed_data}/{expiration_timestamp}/'

        return HttpResponse(expiring_link)


def create_thumbnail(image, size):
    img = PILImage.open(image.image.path)
    img.thumbnail((size, size))
    thumbnail_io = BytesIO()
    img.save(thumbnail_io, format='JPEG')
    thumbnail = Thumbnail(image=image, size=size)
    thumbnail.thumbnail.save(f'thumbnail_{size}.jpg', thumbnail_io)
    return thumbnail
