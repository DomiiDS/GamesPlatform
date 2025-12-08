"""
URL configuration for GamePlatform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from GamePlatformApp.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name="home"),
    path('games', GamesListView.as_view(), name="games"),
    path('games/blackjack', BlackjackView.as_view(), name="blackjack"),
    path('games/coin_toss', GamesListView.as_view(), name="coin_toss"),
    path('games/horse_race', GamesListView.as_view(), name="horse_race"),
    path('login', LoginView.as_view(template_name='GamePlatformApp/login.html'), name="login"),
    path('logout', LogoutView.as_view(template_name='GamePlatformApp/login.html'), name="logout"),
    path('register', RegisterView.as_view(), name="register"),
    path('register/success', RegisterSuccessView.as_view(), name="register_success"),
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/edit/', UserUpdateView.as_view(), name='user-edit'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user-delete'),
    path('profile/<int:pk>/', UserProfileView.as_view(), name="user-profile"),
    path('profile/<int:pk>/edit/', ProfileUpdateView.as_view(), name="profile-edit"),
    path('profile/<int:pk>/stats/', UserStatsView.as_view(), name="user-stats"),
    path('update-chips/', UpdateChipsView.as_view(), name="update-chips"),
    path('race/', race_room, name="race-room"),
    path('race/start', start_race, name="start-race"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)