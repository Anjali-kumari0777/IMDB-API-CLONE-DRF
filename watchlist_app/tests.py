from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from watchlist_app.api import serializers
from watchlist_app import models

class StreamPlatformTestCase(APITestCase):

    def setUp(self):
          self.user=User.objects.create_user(username="example",password="password")
          self.token=Token.objects.get(user__username=self.user)
          self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
          self.stream=models.StreamPlatform.objects.create(name="Netflix",about="#1 platform",website="https://www.netflix.com")


    def test_streamplatform_create(self):
           data={
               "name":"Netflix",
               "about":"1 Streaming Platform",
               "website":"https://netflix.com"
           }
           response=self.client.post(reverse('streamplatform-list'),data)
           self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_streamplatform_list(self):  
           response=self.client.get(reverse('streamplatform-list'))
           self.assertEqual(response.status_code, status.HTTP_200_OK)
              
    def test_streamplatform_ind(self):  
           response=self.client.get(reverse('streamplatform-detail',args=(self.stream.id,)))
           self.assertEqual(response.status_code, status.HTTP_200_OK)

class WatchListTestCase(APITestCase):
        
        def setUp(self):
          self.user=User.objects.create_user(username="example",password="password")
          self.token=Token.objects.get(user__username=self.user)
          self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
          self.stream=models.StreamPlatform.objects.create(name="Netflix",about="#1 platform",website="https://www.netflix.com")
          self.watchlist=models.WatchList.objects.create(platform=self.stream,title="example movie",storyline="example story",active=True)

        def test_watchlist_create(self):
                data={
                    "platform":self.stream,
                    "title":"example movie",
                    "storyline":"example story",
                    "active":True
                }  
                response=self.client.post(reverse('watchlist'),data)
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        def test_watchlist_list(self):  
               response=self.client.get(reverse('watchlist'))
               self.assertEqual(response.status_code, status.HTTP_200_OK)
                  
        def test_watchlist_ind(self):  
               response=self.client.get(reverse('watchlist_details',args=(self.watchlist.id,)))
               self.assertEqual(response.status_code, status.HTTP_200_OK)
               self.assertEqual(models.WatchList.objects.count(), 1)
               self.assertEqual(models.WatchList.objects.get().title, 'example movie')

class ReviewTestCase(APITestCase):
      
        def setUp(self):
          self.user=User.objects.create_user(username="example",password="password")
          self.token=Token.objects.get(user__username=self.user)
          self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
          self.stream=models.StreamPlatform.objects.create(name="Netflix",about="#1 platform",website="https://www.netflix.com")
          self.watchlist=models.WatchList.objects.create(platform=self.stream,title="example movie",storyline="example story",active=True)
          self.watchlist2=models.WatchList.objects.create(platform=self.stream,title="example movie",storyline="example story",active=True)
          self.review=models.Review.objects.create(review_user=self.user,rating=5,description="greate movie-2",watchlist=self.watchlist2,active=True)
        
        def test_review_create(self):
                data={
                    "review-user":self.user,
                    "rating":5,
                    "description":"Great movie!",
                    "watchlist":self.watchlist,
                    "active":True
                }  
                response=self.client.post(reverse('review-create',args=(self.watchlist.id,)),data)
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
                self.assertEqual(models.Review.objects.count(), 2)


                response=self.client.post(reverse('review-create',args=(self.watchlist.id,)),data)
                self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        def test_review_create_unauth(self):
                data={
                    "review-user":self.user,
                    "rating":5,
                    "description":"Great movie!",
                    "watchlist":self.watchlist,
                    "active":True
                }  
                self.client.force_authenticate(user=None)
                response=self.client.post(reverse('review-create',args=(self.watchlist.id,)),data)
                self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        def test_review_update(self):
                data={
                    "review-user":self.user,
                    "rating":4,
                    "description":"Great movie!",
                    "watchlist":self.watchlist,
                    "active":False
                }    
                response=self.client.put(reverse('review-details',args=(self.review.id,)),data)
                self.assertEqual(response.status_code, status.HTTP_200_OK) 

        def test_review_list(self):  
               response=self.client.get(reverse('review-list',args=(self.watchlist.id,)))
               self.assertEqual(response.status_code, status.HTTP_200_OK)
                  
        def test_review_ind(self):  
               response=self.client.get(reverse('review-details',args=(self.review.id,)))
               self.assertEqual(response.status_code, status.HTTP_200_OK)     

        # def test_review_delete(self):  
        #        response=self.client.delete(reverse('review-details',args=(self.review.id,)))
        #        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)   
        # 
        def test_review_user(self):
               response=self.client.get('/api/watch/user-reviews/?username' +  self.user.username)     
               self.assertEqual(response.status_code, status.HTTP_200_OK)     
