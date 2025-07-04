from django.contrib import admin
from django.urls import path, include
from myapp import views
from django.contrib.auth import views as auth_views
from myapp.views import user_profile
from myapp.forms import EmailAuthenticationForm
from myapp.views import trophies_view
from myapp.views import search_results
from .views import standings_view
from django.urls import path, register_converter
import uuid

class UUIDConverter:
    regex = '[0-9a-fA-F-]{36}'

    def to_python(self, value):
        return uuid.UUID(value)

    def to_url(self, value):
        return str(value)

register_converter(UUIDConverter, 'uuid')





urlpatterns = [
    path('', views.index, name='index'),  # <-- Root URL points to the index view
    path('register/', views.player_registration, name='player_registration'),  # <-- Register URL
    path('players/', views.player_list, name='player_list'), 
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('profile/', user_profile, name='user_profile'),
    path('accounts/login/', auth_views.LoginView.as_view(authentication_form=EmailAuthenticationForm), name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    #path('login/', views.custom_login, name='custom_login'),
    #path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path('contact/', views.contact_view, name='contact'),
    path('trophies/', trophies_view, name='trophies'),
    path('presidents/', views.presidents_view, name='presidents'),
    path('rsvp/<uuid:event_id>/', views.rsvp_event, name='rsvp_event'),
    path('player/<uuid:player_id>/', views.player_profile_view, name='player_profile'),
    path('news/', views.news_list, name='news_list'),
    path('search/', search_results, name='search_results'),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('donation-success/', views.donation_success, name='donation_success'),
    path('donation-cancelled/', views.donation_cancelled, name='donation_cancelled'),
    path('gallery/', views.gallery_view, name='gallery'),
    path('standings/', standings_view, name='standings'),















]
