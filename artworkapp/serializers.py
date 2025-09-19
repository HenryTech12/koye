from rest_framework.serializers import ModelSerializer
from .models import Artwork

class SeperateSlash(ModelSerializer):
    def to_representation(self, instance):
        if isinstance(instance,list):
            return "/".join(str(item) for item in instance)
        return instance
    def to_internal_value(self, data):
        if isinstance(data,str):
            return data.split('/')
        return data
    
class ArtworkSerializer(ModelSerializer):
    tags = SeperateSlash()
    class Meta:
        model = Artwork
        fields = '__all__'
        
