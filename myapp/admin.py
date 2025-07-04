from django.contrib import admin
from .models import ClubHistory, Trophy, President, Team, News, Contact
from .models import Player
from .models import CountryEvent 
from .models import MatchPerformance 
#from .models import EventRSVP
from .models import Country, GalleryImage
from .models import Group, Team, Standing


admin.site.register(Player)
admin.site.register(ClubHistory)
admin.site.register(Trophy)
admin.site.register(President)
admin.site.register(Team)
admin.site.register(News)
admin.site.register(Contact)
admin.site.register(CountryEvent)
admin.site.register(MatchPerformance) 
admin.site.register(Country)

@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('country', 'caption')

admin.site.register(Group)
admin.site.register(Standing)
