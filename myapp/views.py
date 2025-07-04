from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from .forms import PlayerRegistrationForm
from .models import Player
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from myapp.models import CountryEvent
from .models import Trophy
from django.shortcuts import render
from .models import President
from .models import Player, CountryEvent
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CountryEvent, EventRSVP
from datetime import timedelta
from .models import MatchPerformance
from .models import News
from django.db.models import Q, Sum
from django.shortcuts import render
from .models import Player, News, MatchPerformance
import stripe , os
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
import json
from django.urls import reverse
from django.middleware.csrf import get_token
import logging
from .models import Country
from .models import Group, Standing, Team










def player_registration(request):
    if request.method == 'POST':
        form = PlayerRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            # Check if user with email already exists to avoid duplicate users
           
            if User.objects.filter(email=email).exists():
                form.add_error('email', 'Email is already registered.')
                return render(request, 'register.html', {'form': form})

            # Create user
            user = User.objects.create_user(username=email, email=email, password=password)
            user.first_name = form.cleaned_data['name']  # Optional
            user.save()

            # Create linked player
            player = form.save(commit=False)
            player.user = user
            player.save()

            messages.success(request, 'Registration successful. You can now log in.')
            return redirect('login')  

    else:
        form = PlayerRegistrationForm()

    return render(request, 'register.html', {'form': form})


#def index(request):
    return render(request, 'index.html')

def player_list(request):
    country = request.GET.get('country')  # Gets '?country=Denmark' from URL
    if country:
        players = Player.objects.filter(country__iexact=country)
    else:
        players = Player.objects.all()

    return render(request, 'players.html', {
        'players': players,
        'selected_country': country
    })


def custom_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')  # HTML field uses "username", but it's really email
        password = request.POST.get('password')

        try:
            player = Player.objects.get(email=email)

            if check_password(password, player.password):
                request.session['player_id'] = str(player.id)
                return redirect('user_login')  # Named URL for userLogin page

            else:
                messages.error(request, 'Invalid password')
        except Player.DoesNotExist:
            messages.error(request, 'User not found')

    return render(request, 'login.html')
@login_required
def user_profile(request):
    user = request.user

    try:
        player = user.player
        user_country = player.country
    except Player.DoesNotExist:
        player = None
        user_country = None

    # Fetch last 10 match performances for this player (new code)
    if player:
        match_stats = MatchPerformance.objects.filter(player=player).order_by('-match_date')[:10]
    else:
        match_stats = []

    if user_country:
        user_events = CountryEvent.objects.filter(country=user_country).order_by('date')
    else:
        user_events = []

    rsvps = EventRSVP.objects.filter(event__in=user_events)

    event_data = []
    for event in user_events:
        rsvps_for_event = rsvps.filter(event=event)
        going_count = rsvps_for_event.filter(status='Going').count()
        not_going_count = rsvps_for_event.filter(status='Not Going').count()
        going_users = [
            rsvp.user.get_full_name() or rsvp.user.username 
            for rsvp in rsvps_for_event.filter(status='Going')
        ]

        try:
            user_rsvp = rsvps_for_event.get(user=user)
        except (ValueError, EventRSVP.DoesNotExist):
            user_rsvp = None

        event_data.append({
            'event': event,
            'going_count': going_count,
            'not_going_count': not_going_count,
            'going_users': going_users,
            'user_rsvp': user_rsvp,
        })

    context = {
        'event_data': event_data,
        'user_country': user_country,
        'player': player,
        'match_stats': match_stats,  # Add this here
    }
    return render(request, 'users.html', context)



def index(request):
    denmark = CountryEvent.objects.filter(country='Denmark').first()
    portugal = CountryEvent.objects.filter(country='Portugal').first()
    country_events = CountryEvent.objects.all().order_by('date')
    countries = Country.objects.prefetch_related('gallery_images').filter(name__in=['Denmark', 'Portugal'])



    return render(request, 'index.html', {
        'denmark': denmark,
        'portugal': portugal,
        'country_events': country_events,
        'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY,
        'countries':countries,
    })

def contact_view(request):
    return render(request, 'contact.html')

def trophies_view(request):
    trophies = Trophy.objects.all()
    return render(request, 'trophies.html', {'trophies': trophies})

def presidents_view(request):
    presidents = President.objects.all().order_by('-term_start')
    return render(request, 'presidents.html', {'presidents': presidents})

@login_required
def rsvp_event(request, event_id):
    if request.method == "POST":
        status = request.POST.get('status')
        if status not in ['Going', 'Not Going']:
            # fallback or error if needed
            status = 'Not Going'  # default fallback

        event = get_object_or_404(CountryEvent, uuid=event_id)
        rsvp, created = EventRSVP.objects.get_or_create(event=event, user=request.user)
        rsvp.status = status
        rsvp.save()
    return redirect('user_profile')

def player_profile_view(request, player_id):
    player = get_object_or_404(Player, id=player_id)
    match_stats = MatchPerformance.objects.filter(player=player).order_by('-match_date')[:10]

    context = {
        'player': player,
        'match_stats': match_stats,
    }
    return render(request, 'player_profile.html', context)

def news_list(request):
    news_list = News.objects.all().order_by('-created_at')
    return render(request, 'news.html', {'news_list': news_list})

def search_results(request):
    query = request.GET.get('q', '').strip()

    players = Player.objects.filter(
        Q(name__icontains=query) | Q(surname__icontains=query)
    ).annotate(
        total_goals=Sum('match_performances__goals'),
        total_assists=Sum('match_performances__assists'),
        total_yellow=Sum('match_performances__yellow_cards'),
        total_red=Sum('match_performances__red_cards'),
        total_minutes=Sum('match_performances__minutes_played')
    ) if query else Player.objects.none()

    news = News.objects.filter(
        Q(headline__icontains=query) | Q(content__icontains=query)
    ) if query else News.objects.none()

    context = {
        'query': query,
        'players': players,
        'news': news,
    }
    return render(request, 'search_results.html', context)

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_checkout_session(request):
    data = json.loads(request.body)
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': 'Donation to FC Himalayan',
                    },
                    'unit_amount': data['amount'],  # amount in cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='https://44b6-2a01-11-810-4300-71fe-60a2-1741-24fc.ngrok-free.app/donation-success/',
            cancel_url='https://44b6-2a01-11-810-4300-71fe-60a2-1741-24fc.ngrok-free.app/donation-cancelled/',
        )
        return JsonResponse({'id': session.id})
    except Exception as e:
        logging.error(f"Stripe checkout session error: {e}")
        return JsonResponse({'error': str(e)})
    

    return render(request, 'index.html', {
        'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY,
    })

def donation_success(request):
    return render(request, 'donation_success.html')

def donation_cancelled(request):
    return render(request, 'donation_cancelled.html')

def gallery_view(request):
    countries = Country.objects.all()
    country_name = request.GET.get('country')
    selected_country = None
    images = []

    if country_name:
        try:
            selected_country = Country.objects.get(name__iexact=country_name)
            images = selected_country.gallery_images.all()
        except Country.DoesNotExist:
            selected_country = None
            images = []
            # You can add a message here if you want

    return render(request, 'gallery.html', {
        'countries': countries,
        'selected_country': selected_country,
        'images': images
    })

from django.shortcuts import render, get_object_or_404
from .models import CountryEvent, Standing, Team  # Adjust imports to your app

def standings_view(request):
    events = CountryEvent.objects.all()
    selected_event_uuid = request.GET.get('event')
    selected_event = None
    grouped_standings = {}

    # Knockout matches default structure
    knockout_matches = {
        'quarterfinals': [],
        'semifinals': [],
        'final': None,
    }

    if selected_event_uuid:
        selected_event = get_object_or_404(CountryEvent, uuid=selected_event_uuid)
        groups = selected_event.group_set.all()

        # Group phase standings: fetch standings for each group
        for group in groups:
            standings = Standing.objects.filter(team__group=group).select_related('team').order_by('-points', '-goals_for')
            grouped_standings[group.name] = standings

        # DummyMatch class for knockout phase dummy data
        class DummyMatch:
            def __init__(self, team1, team2, score1, score2):
                self.team1 = team1
                self.team2 = team2
                self.score1 = score1
                self.score2 = score2

        # Get all teams in this event (via groups)
        all_teams = Team.objects.filter(group__event=selected_event).select_related('group')
        teams_list = list(all_teams)

        # Populate dummy knockout matches if enough teams
        if len(teams_list) >= 8:
            knockout_matches['quarterfinals'] = [
                DummyMatch(teams_list[0], teams_list[1], 2, 1),
                DummyMatch(teams_list[2], teams_list[3], 0, 0),
                DummyMatch(teams_list[4], teams_list[5], 1, 3),
                DummyMatch(teams_list[6], teams_list[7], 2, 2),
            ]
            knockout_matches['semifinals'] = [
                DummyMatch(teams_list[0], teams_list[2], 1, 2),
                DummyMatch(teams_list[5], teams_list[7], 0, 1),
            ]
            knockout_matches['final'] = DummyMatch(teams_list[2], teams_list[7], 1, 3)
        else:
            # Fallback: no matches if less than 8 teams
            knockout_matches['quarterfinals'] = []
            knockout_matches['semifinals'] = []
            knockout_matches['final'] = None

    return render(request, 'standings.html', {
        'events': events,
        'selected_event': selected_event,
        'grouped_standings': grouped_standings,
        'knockout_matches': knockout_matches,
    })
