from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import UserRateThrottle,AnonRateThrottle,ScopedRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework import generics
from rest_framework.permissions import (IsAuthenticated,IsAuthenticatedOrReadOnly)
from watchlist_app.api import permission,serializers,throttling,pagination
from watchlist_app.models import WatchList,StreamPlatform,Review

class UserReview(generics.ListAPIView):
    serializer_class = serializers.ReviewSerializer
    def get_queryset(self):
        username = self.request.query_params.get('username',None)
        return Review.objects.filter(review_user__username=username)

class ReviewCreate(generics.CreateAPIView):
    serializer_class = serializers.ReviewSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes=[throttling.ReviewCreateThrottle]

    def get_queryset(self):
        return Review.objects.all()

    def perform_create(self,serializer):
         pk=self.kwargs.get('pk')
         watchlist=WatchList.objects.get(pk=pk)

         review_user=self.request.user
         review_queryset=Review.objects.filter(watchlist=watchlist,review_user=review_user)

         if review_queryset.exists():
             raise ValidationError("you have already reviewed this movie")
         
         if watchlist.number_rating==0:
             watchlist.avg_rating=serializer.validated_data['rating']
         else:
             watchlist.avg_rating=(watchlist.avg_rating+serializer.validated_data['rating'])/2  

         watchlist.number_rating=watchlist.number_rating+1
         watchlist.save()

         serializer.save(watchlist=watchlist,review_user=review_user)

class ReviewList(generics.ListAPIView):
    serializer_class = serializers.ReviewSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes =[throttling.ReviewListThrottle,UserRateThrottle] 
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['review_user__username', 'active']


    def get_queryset(self):
        pk=self.kwargs['pk']
        return Review.objects.filter(watchlist=pk)

class ReviewDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = serializers.ReviewSerializer
    permission_classes = [permission.IsReviewUserOrReadOnly]
    throttle_classes =[ScopedRateThrottle]
    throttle_scope='review-detail' 



class Streamplatformt(viewsets.ModelViewSet):

    queryset = StreamPlatform.objects.all()
    serializer_class = serializers.StreamPlatformSerializer
    permission_classes = [permission.IsAdminOrReadOnly]


class WatchListAV(APIView):
    
    permission_classes = [permission.IsAdminOrReadOnly]
    def get(self,request):
       movies=WatchList.objects.all()
       serializer=serializers.WatchListSerializer(movies,many=True,context={'request': request})
       return Response(serializer.data)
    
    def post(self,request):
        serializer=serializers.WatchListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
        
class WatchDetailAV(APIView):

    def get(self,request,pk):
       try:
          Movie=WatchList.objects.get(pk=pk)
       except WatchList.DoesNotExist:  
           return Response({'error':' not found'},status=status.HTTP_404_NOT_FOUND)

       serializer=serializers.WatchListSerializer(Movie,context={'request': request})
       return Response(serializer.data) 
    
    def put(self,request,pk):
      permission_classes = [permission.IsAdminOrReadOnly]
      Movie=WatchList.objects.get(pk=pk)
      serializer=serializers.WatchListSerializer(Movie,data=request.data)
      if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
      else:
            return Response(serializer.errors)  

    def delete(self,request,pk):       
      Movie=WatchList.objects.get(pk=pk)
      Movie.delete()
      return Response(status=status.HTTP_204_NO_CONTENT)
