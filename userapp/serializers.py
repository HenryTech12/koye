from rest_framework import serializers
from .models import User,Profile
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email','password','tags']
        extra_kwargs = {
            'password':{'write_only':True}
        }
    def create(self,validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password) #hash the password
        instance.save()
        return instance
    
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['user','bio','displayName','tags','followers']