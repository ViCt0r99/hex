import os

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Image, Tier, Thumbnail

User = get_user_model()


class ImageAPITestCase(APITestCase):
    def setUp(self):

        # Create a test user
        self.user = User.objects.create_superuser(username="testuser", password="testpassword")
        self.user.set_password('testpassword')
        self.user.save()

        # Create test tiers
        self.basic_tier = Tier.objects.create(name='Basic', thumbnail_sizes=[200])
        self.premium_tier = Tier.objects.create(name='Premium', thumbnail_sizes=[200, 400],
                                                generate_expiring_links=True)
        self.enterprise_tier = Tier.objects.create(name='Enterprise', thumbnail_sizes=[200, 400],
                                                   generate_expiring_links=True)

    def test_create_image_basic_tier(self):
        # Authenticate as the test user
        self.client.login(username='testuser', password='testpassword')

        # Upgrade the user to 'Basic' tier
        self.user.tier = self.basic_tier
        self.user.save()

        url = reverse('image-create')

        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests/test_image.png'), "rb") as image_file:
            data = {
                'image': image_file
            }
            response = self.client.post(url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Image.objects.count(), 1)

    def test_create_image_premium_tier(self):
        # Authenticate as the test user
        self.client.login(username='testuser', password='testpassword')

        # Upgrade the user to 'Premium' tier
        self.user.tier = self.premium_tier
        self.user.save()

        url = reverse('image-create')

        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests/test_image.png'), "rb") as image_file:
            data = {
                'image': image_file,
                'image_url': 'https://example.com/placeholder-url.jpg'
            }
            response = self.client.post(url, data, format='multipart')

        # Rest of the test logic remains the same
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Image.objects.count(), 1)

    def test_create_image_enterprise_tier(self):
        # Authenticate as the test user
        self.client.login(username='testuser', password='testpassword')

        # Upgrade the user to 'Enterprise' tier
        self.user.tier = self.enterprise_tier
        self.user.save()

        url = reverse('image-create')

        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests/test_image.png'), "rb") as image_file:
            expiring_link_seconds = 3600
            data = {
                'image': image_file,
                'expiring_link_seconds': expiring_link_seconds,
                'image_url': 'https://example.com/placeholder-url.jpg'
            }
            response = self.client.post(url, data, format='multipart')

        # Rest of the test logic remains the same
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Image.objects.count(), 1)


class TierTestCase(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_superuser(username="testuser", password="testpassword")
        # Create test tiers
        self.basic_tier = Tier.objects.create(name='Basic', thumbnail_sizes=[200])
        self.premium_tier = Tier.objects.create(name='Premium', thumbnail_sizes=[200, 400],
                                                generate_expiring_links=True)
        self.enterprise_tier = Tier.objects.create(name='Enterprise', thumbnail_sizes=[200, 400],
                                                   generate_expiring_links=True)

    def test_tier_list(self):
        # Authenticate as the test user
        self.client.login(username='testuser', password='testpassword')

        url = reverse('tier-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_tier_detail(self):
        # Authenticate as the test user
        self.client.login(username='testuser', password='testpassword')

        url = reverse('tier-detail', args=[self.basic_tier.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Basic')

    def test_tier_creation(self):
        # Authenticate as the test user
        self.client.login(username='testuser', password='testpassword')

        url = reverse('tier-list')
        data = {'name': 'New Tier', 'thumbnail_sizes': [100, 300], 'generate_expiring_links': True}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Tier.objects.count(), 4)

    def test_tier_update(self):
        # Authenticate as the test user
        self.client.login(username='testuser', password='testpassword')

        url = reverse('tier-detail', args=[self.basic_tier.id])
        data = {'name': 'Updated Basic Tier', 'thumbnail_sizes': [150], 'generate_expiring_links': True}

        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.basic_tier.refresh_from_db()
        self.assertEqual(self.basic_tier.name, 'Updated Basic Tier')
        self.assertEqual(self.basic_tier.thumbnail_sizes, [150])

    def test_tier_deletion(self):
        # Authenticate as the test user
        self.client.login(username='testuser', password='testpassword')

        url = reverse('tier-detail', args=[self.basic_tier.id])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Tier.objects.count(), 2)


class ThumbnailTestCase(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_superuser(username='testuser', password='testpassword')

        # Create a test image associated with the user
        self.image = Image.objects.create(user=self.user, image='images/test_image.jpg')

        # Create test thumbnails associated with the image
        self.thumbnail1 = Thumbnail.objects.create(image=self.image, size=200,
                                                   expiring_link='thumbnails/thumbnail1.jpg')
        self.thumbnail2 = Thumbnail.objects.create(image=self.image, size=400,
                                                   expiring_link='thumbnails/thumbnail2.jpg')

    def test_thumbnail_list(self):
        # Authenticate as the test user
        self.client.login(username='testuser', password='testpassword')

        url = reverse('thumbnail-list')

        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_thumbnail_detail(self):
        # Authenticate as the test user
        self.client.login(username='testuser', password='testpassword')

        url = reverse('thumbnail-detail', args=[self.thumbnail1.id])

        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['size'], 200)

    def test_thumbnail_deletion(self):
        # Authenticate as the test user
        self.client.login(username='testuser', password='testpassword')

        url = reverse('thumbnail-detail', args=[self.thumbnail1.id])

        self.client.login(username='testuser', password='testpassword')
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Thumbnail.objects.count(), 1)
