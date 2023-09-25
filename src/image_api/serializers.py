from rest_framework import serializers
from .models import Tier, Image, Thumbnail


class TierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tier
        fields = '__all__'


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'


class ThumbnailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thumbnail
        fields = '__all__'
