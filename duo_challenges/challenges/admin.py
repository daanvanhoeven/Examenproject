from django.contrib import admin
from .models import Discipline, Profiel, Challenge, ChallengeDeelname, Project


@admin.register(Discipline)
class DisciplineAdmin(admin.ModelAdmin):
    # Maakt disciplines makkelijk vindbaar in de admin.
    list_display = ['naam']
    search_fields = ['naam']


@admin.register(Profiel)
class ProfielAdmin(admin.ModelAdmin):
    # Toont snel welke rol een gebruiker heeft.
    list_display = ['user', 'rol']
    list_filter = ['rol']
    search_fields = ['user__username']


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    # Overzicht van challenges met de bijbehorende disciplines.
    list_display = ['titel', 'discipline_een', 'discipline_twee', 'aangemaakt_door', 'aangemaakt_op']
    list_filter = ['discipline_een', 'discipline_twee']
    search_fields = ['titel', 'omschrijving']


@admin.register(ChallengeDeelname)
class ChallengeDeelnameAdmin(admin.ModelAdmin):
    # Laat zien wie meedoet en wat de status is.
    list_display = ['deelnemer', 'challenge', 'status', 'ingediend_op']
    list_filter = ['status']
    search_fields = ['deelnemer__username', 'challenge__titel']





@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    # Projecten kunnen hier worden bekeken op status.
    list_display = ['deelnemer', 'challenge', 'status', 'ingediend_op']
    list_filter = ['status']
    search_fields = ['deelnemer__username', 'challenge__titel']    
