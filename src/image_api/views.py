import os
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from PIL import Image as PillowImage

from .models import Tier, Image, Thumbnail, create_thumbnail
from .serializers import TierSerializer, ThumbnailSerializer


class ImageCreateView(APIView):
    parser_classes = (MultiPartParser,)
    queryset = Image.objects.all()  # Set the queryset

    def post(self, request):
        uploaded_file = request.data['image']
        user = request.user

        # Check the file extension
        allowed_extensions = ['.jpg', '.jpeg', '.png']  # Add other allowed extensions as needed
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()

        if file_extension not in allowed_extensions:
            return Response({'error': 'Invalid file format. Please upload a JPG or PNG image.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Determine the tier of the user
        user_tier = user.tier  # Assuming user.tier stores the tier information

        # Create an Image instance and save it
        image = Image(user=user, image=uploaded_file)
        image.save()

        # Open the image using Pillow and convert it to RGB color mode if it's RGBA
        with PillowImage.open(image.image.path) as img:
            if img.mode == 'RGBA':
                img = img.convert('RGB')

            # Save the image as JPEG (you can choose the desired format)
            img.save(image.image.path, format='JPEG')

        # Create thumbnails for the image
        thumbnail_sizes = user_tier.thumbnail_sizes
        for size in thumbnail_sizes:
            thumbnail = create_thumbnail(image, size)
            thumbnail.save()

        # Generate links to the originally uploaded image for Premium and Enterprise tiers
        if user_tier.name in ["Premium", "Enterprise"]:
            image.original_image_link = request.data.get('image_url')  # Store the link to the original image
            image.save()

        # Generate an expiring link if expiring_link_seconds is provided
        expiring_link_seconds = request.data.get('expiring_link_seconds')
        if expiring_link_seconds:
            thumbnail = Thumbnail.objects.get(image=image, size=thumbnail_sizes[0])
            thumbnail.generate_expiring_link(expiration_seconds=expiring_link_seconds)

        return Response({'message': 'Image uploaded successfully.'}, status=status.HTTP_201_CREATED)


class ThumbnailListView(APIView):
    queryset = Thumbnail.objects.all()

    def get(self, request):
        thumbnails = Thumbnail.objects.all()
        serializer = ThumbnailSerializer(thumbnails, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TierListView(APIView):
    queryset = Tier.objects.all()

    def get(self, request):
        tiers = Tier.objects.all()
        serializer = TierSerializer(tiers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = TierSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TierDetailView(APIView):
    queryset = Tier.objects.all()

    def get(self, request, pk):
        try:
            tier = Tier.objects.get(pk=pk)
            serializer = TierSerializer(tier)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Tier.DoesNotExist:
            return Response({'error': 'Tier not found.'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            tier = Tier.objects.get(pk=pk)
            serializer = TierSerializer(tier, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Tier.DoesNotExist:
            return Response({'error': 'Tier not found.'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            tier = Tier.objects.get(pk=pk)
            tier.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Tier.DoesNotExist:
            return Response({'error': 'Tier not found.'}, status=status.HTTP_404_NOT_FOUND)


class ThumbnailDetailView(APIView):
    queryset = Thumbnail.objects.all()

    def get(self, request, pk):
        try:
            thumbnail = Thumbnail.objects.get(pk=pk)
            serializer = ThumbnailSerializer(thumbnail)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Thumbnail.DoesNotExist:
            return Response({'error': 'Thumbnail not found.'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            thumbnail = Thumbnail.objects.get(pk=pk)
            thumbnail.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Thumbnail.DoesNotExist:
            return Response({'error': 'Thumbnail not found.'}, status=status.HTTP_404_NOT_FOUND)
