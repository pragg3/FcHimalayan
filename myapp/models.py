from django.db import models
from django.contrib.auth import get_user_model
import uuid
from datetime import datetime
from django.conf import settings
from django.db import models

# Get the user model
User = get_user_model()

class ClubHistory(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.title

class Trophy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    year = models.IntegerField()
    image = models.ImageField(upload_to='trophies/',null=True, blank=True)  
    country = models.CharField(max_length=100,null=True,blank=True)  



    def __str__(self):
        return f"{self.name} ({self.year}) - {self.country}"

class President(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(upload_to='trophies/',null=True, blank=True)  
    name = models.CharField(max_length=100)
    term_start = models.DateField()
    term_end = models.DateField(null=True, blank=True)
    description = models.TextField(null=True,blank=True)

    def __str__(self):
        return self.name


class News(models.Model):
    headline = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='news/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField('Tag', blank=True)

class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Contact(models.Model):
    name = models.CharField(max_length=100,default='Default Name')
    email = models.EmailField(null=True, blank=True)  # Allow it to be null for now
    message = models.TextField()

    def __str__(self):
        return self.name


class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(upload_to='player_images/')
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    age = models.IntegerField()
    sex = models.CharField(max_length=10)
    position = models.CharField(max_length=100)
    jersey_number = models.IntegerField()
    country = models.CharField(max_length=100)
    nationality = models.CharField(max_length=100)
    address = models.TextField()
    contacts = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.name} {self.surname}"

class CountryEvent(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # primary key


    COUNTRY_CHOICES = [
        ('Denmark', 'Denmark'),
        ('Portugal', 'Portugal'),
    ]

    country = models.CharField(max_length=100, choices=COUNTRY_CHOICES)
    event_name = models.CharField(max_length=200)
    date = models.DateTimeField()
    address = models.CharField(max_length=300)  # Physical address for the map

    def __str__(self):
        return f"{self.country} - {self.event_name}"
    
class EventRSVP(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(CountryEvent, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[('Going', 'Going'), ('Not Going', 'Not Going')], default='Not Going')

    class Meta:
        unique_together = ('event', 'user')

class MatchPerformance(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='match_performances')
    match_date = models.DateField()
    opponent_team = models.CharField(max_length=100)

    goals = models.PositiveIntegerField(default=0)
    assists = models.PositiveIntegerField(default=0)
    yellow_cards = models.PositiveIntegerField(default=0)
    red_cards = models.PositiveIntegerField(default=0)

    minutes_played = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.player} vs {self.opponent_team} on {self.match_date}"

class Country(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class GalleryImage(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='gallery/')
    caption = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.country.name} - {self.caption or 'Image'}"
    
class Group(models.Model):
    name = models.CharField(max_length=50)
    event = models.ForeignKey(CountryEvent, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.event.event_name})"

    
class Team(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=100)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, default='YOUR-GROUP-UUID-HERE')


    def __str__(self):
        return self.name

class Standing(models.Model):
    team = models.OneToOneField(Team, on_delete=models.CASCADE)
    played = models.PositiveIntegerField(default=0)
    won = models.PositiveIntegerField(default=0)
    drawn = models.PositiveIntegerField(default=0)
    lost = models.PositiveIntegerField(default=0)
    goals_for = models.PositiveIntegerField(default=0)
    goals_against = models.PositiveIntegerField(default=0)
    points = models.IntegerField(default=0)

    @property
    def goal_difference(self):
        return self.goals_for - self.goals_against

    class Meta:
        ordering = ['-points', '-goals_for']

  
    def __str__(self):
        return f"{self.team.name} - {self.team.group.name}"