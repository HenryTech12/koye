from django.shortcuts import render
from rest_framework.views import APIView
from .models import User,Profile
from django.db.models import F
from .serializers import UserSerializer
from django.contrib.auth import authenticate
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated,AllowAny
import jwt
from django.conf import settings
from rest_framework import status

def getUserByToken(request):
    token = request.headers.get("Authorization").split(" ")[1]
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    return User.objects.get(pk=payload["user_id"])
# Create your views here.
class RegisterView(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(request_body=UserSerializer, responses={201: UserSerializer})
    def post(self,request):
        data = request.data
        email = data['email']
        if User.objects.filter(email=email).exists():
            error_response = {
                "error": "Email already exists"
            }
            return Response(error_response, status=400) 
        else:
            serializer = UserSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=201)
            
        
class UserView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(request_body=UserSerializer, responses={201: UserSerializer})
    def delete(self,request):
        user = getUserByToken(request)
        user.delete()
        return Response({"message":"User deleted successfully"},status=200)
    def put(self,request):
        user = getUserByToken(request)
        serializer = UserSerializer(user, data=request.data, partial=True)
        return Response(serializer.data, status=200)    
    
class MeView(APIView):
    def get(self,request):
       user = getUserByToken(request)
       serializer = UserSerializer(user)   # ✅ pass instance, not data
       # get wallet balance and add to response
       return Response(serializer.data, status=status.HTTP_200_OK)
class FollowView(APIView):
    def post(self,request,pk):
        user = User.objects.get(pk=pk)
        if user is not None:
            profile = Profile.objects.get(user=user)
            if profile is not None:
                profile.objects.filter(pk=profile.id).update(followers=F("followers")+1)
                profile.refresh_from_db()
                return Response({
                    "following":True,
                    "followers":profile.followers
                })
            else:
                return Response({"message":"User doesn't have a profile"})
        else:
            return Response({"message":"User id is not valid"})
    
class UnfollowView(APIView):    
    def delete(self,request,pk):
        user = User.objects.get(pk=pk)
        if user is not None:
            profile = Profile.objects.get(user=user)
            profile.delete()
            return Response({"message":"Profile deleted successfully"})
        else:
            return Response({"message":"User id is not valid"})
        
class UpdateDataView(APIView):
    def put(self,request):
        user = getUserByToken(request)
        if not Profile.objects.filter(displayName=request.data.get('displayName')).exists():
            profile = Profile.objects.create(
            user =user,
            displayName=request.data.get('displayName'),
            bio = request.data.get('bio'),
            tags = request.data.get('tags'),
            followers = 0
            )
            dbUser = User.objects.get(pk=user.id)
            dbUser.set_tags(profile.tags)
            dbUser.refresh_from_db()
            profile.save()
            return Response({"success":True})
        else:
            return Response({"success":False,"message":"profile already exists"})
    