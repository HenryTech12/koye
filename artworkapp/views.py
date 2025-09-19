from django.shortcuts import render
import os
from django.forms.models import model_to_dict
from django.conf import settings
from rest_framework.views import Response, APIView
from .models import Artwork
from django.db.models import F
from userapp.models import User
from .serializers import ArtworkSerializer
import jwt,requests
from userapp.views import getUserByToken
from .pagination import SearchPagination
import google.generativeai as genai

# Create your views here.

blockchainUrl = 'https://koye.onrender.com'

def getCreator(request):
    token = request.headers.get('Authorization').split(' ')[1]
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"]) 
    return payload['user_id']
def getCID(request):
    url = 'http://127.0.0.1:5001/api/v0/add'
    file=request.FILES['file']
    if file is not None:
        response = requests.post(url,files={"file":file})
        return response.json()
    else:
        return None
class TagView(APIView):
    def get(self,request):
        user_input = request.data.get('userInput')
        prompt = f"""
        You are an autocomplete engine for an African art,music, and NFT platform
        The user is typing a tag: "{user_input}".
        Suggest 4-8 relevant tag completions related to art, African culture, music or NFTs.
        return them strictly as a JSON array of strings, nothing else.
        """
        
        genai.configure(api_key=os.environ.get('GOOGLE_API_KEY'))

        # Example: generate text
        
        response = genai.ChatCompletion.create(
            model="chat-bison-001",
            messages=[
                {"author": "user", "content": prompt},
            ],
        )
        return Response({"tags":response.last},status=200)
class LikeArt(APIView):
    def post(self,request,pk):
        creator=request.data.get('userId')
        userId = int(creator)
        artwork = Artwork.objects.filter(pk=pk).first()
        creatorId = int(artwork.creator.id)
        if userId == creatorId:
            Artwork.objects.filter(pk=pk).update(likes=F("likes")+1)
            artwork.refresh_from_db()
            return Response({
                "artId":artwork.id,
                "likes":artwork.likes
            })
        else:
            return Response({"message":"invalid user id!"})
class SaveArt(APIView):
    def post(self,request,pk):
        creator = request.get('userId')
        userId = int(creator)
        artwork = Artwork.objects.filter(creator=creator).filter().first()
        creatorId = int(artwork.creator.id)
        
        if userId == creatorId:
            Artwork.objects.filter(pk=pk).update(saves=F("saves")+1)
            artwork.refresh_from_db()
            return Response({
                "artId":artwork.id,
                "saves":artwork.saves
            })
        else:
            return Response({"message":"invalid user id!"})
        
class  FeedView(APIView):
    def get(self,request):
        location = request.query_params.get('location')
        tags = request.query_params.get('tags')
        
        user = getUserByToken(request)
        queryset = Artwork.objects.filter(creator=user).all()
        if location:
            queryset = queryset.filter(location__icontains=location)
        if tags:
            tag_list = tags.split(',')
            for tag in tag_list:
                queryset = queryset.filter(tags__icontains=tag)
        paginator = SearchPagination()
        result_page = paginator.paginate_queryset(request=request,queryset=queryset)
        serializer = ArtworkSerializer(result_page,many=True)
        return paginator.get_paginated_response(serializer.data)
    
class SearchView(APIView):
    def get(self,request):
        q = request.query_params.get('q')
        type=request.query_params.get('type')
        tags = request.query_params.get('tags')
        location = request.query_params.get('location')
        
        user = getUserByToken(request)
        queryset = Artwork.objects.filter(creator=user).all()
        
        if q:
            queryset = queryset.filter(title__icontains=q)
        if type:
            queryset = queryset.filter(type__icontains=type)
        if tags:
            queryset = queryset.filter(tags__icontains=tags)
        if location:
            queryset = queryset.filter(location__icontains=location)
        pagination = SearchPagination()
        result_page = pagination.paginate_queryset(request=request,queryset=queryset)
        serializer = ArtworkSerializer(result_page,many=True)
        return pagination.get_paginated_response(serializer.data)
        
class BlockchainView(APIView):
    def get(self,request,pk):
        response = requests.get(url=blockchainUrl+'/art/status/'+pk)
        return Response(response.json()) 
    def post(self,request):
        filename = request.data.get('filename')
        contentType = request.data.get('contentType')
        size = request.data.get('size')
        data = {
            'filename':filename,
            'contentType':contentType,
            'size':size
        }
        response = requests.post(url=blockchainUrl+'/uploads/presign', data=data)
        return Response(response.json())     
class ArtworkView(APIView):
    def post(self,request):
        user = User.objects.get(pk=getCreator(request))
        print(request.data.get('tags'))
        if user is not None:
            #const { title, description, fileUrl, metadata, username, artistWallet } = req.body;
            data = {
                "title": request.data.get('name'),
                "description": request.data.get('description'),
                "fileUrl":request.data.get('fileUrl'),
                "username": user.username
            }
            response = requests.post(blockchainUrl+'', data=data)
            artwork = Artwork(
                    creator= user,
                    location = request.data.get('location'),
                    desc = request.data.get('description'),
                    name = request.data.get('name'),
                    tags = request.data.get('tags'),
                    fileUrl = request.data.get('fileUrl'),
                    likes = 0,saves = 0,
                    data = data
            )
            artwork.save()
            
            return Response({
                "artId": artwork.id,
                "status":"success",
            },status=200)
        else:
            return Response({
                "status":"failed!",
                "message":"invalid token"
            }, status=404)
            
class GetArtworkView(APIView):
    def get(self,request,pk):
        if pk is None:
            user = getUserByToken(request)
            artworks = Artwork.objects.filter(creator=user)
            artworkSerializer = ArtworkSerializer(artworks, many=True)
            return Response(artworkSerializer.data)
        else:
            user = getUserByToken(request)
            userId = int(user.id)
            artwork = Artwork.objects.filter(creator=user).all()
            creatorId = int(artwork.creator.id)
            if userId == creatorId:
                artworkSerializer = ArtworkSerializer(artwork)
                return Response(artworkSerializer.data)
            else:
                return Response("invalid token!")
            
class RecommendationView(APIView):
    def get(self,request):
        client = genai.Client()
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Explain how AI works in a few words"
        )
        return Response({"tags":response.text},status=200)
        