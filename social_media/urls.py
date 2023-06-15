from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('signup/', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('home/', views.home, name='home'),
    path('home/search', views.search, name='search'),
    path('logout/', views.logout, name='logout'),
    path('settings/', views.settings, name='settings'),
    path('home/upload', views.upload, name='upload'),
    path('home/profile/<str:user_name>', views.profile, name='profile'),
    path('follow', views.follow, name='follow'),
    path('like-post', views.like_post, name='like-post'),
    path('view-followers', views.view_followers, name='view-followers'),
    path('view-following', views.view_following, name='view-following'),
]