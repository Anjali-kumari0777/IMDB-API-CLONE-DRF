from django.urls import path,include
from watchlist_app.api import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'stream', views.Streamplatformt, basename='streamplatform')

urlpatterns = [
    path('',views.WatchListAV.as_view(),name='watchlist'),
    path('<int:pk>/',views.WatchDetailAV.as_view(),name='watchlist_details'),
    path('<int:pk>/reviews/',views.ReviewList.as_view(),name='review-list'),
    path('<int:pk>/reviews/create/',views.ReviewCreate.as_view(),name='review-create'),
    path('reviews/<int:pk>/',views.ReviewDetail.as_view(),name='review-details'),
    path('user-reviews/',views.UserReview.as_view(),name='user-review-detail'),
    path('',include(router.urls)),

]