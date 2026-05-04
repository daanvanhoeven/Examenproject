from django.contrib import admin
from .models import Discipline, Profiel, Challenge, ChallengeDeelname, Project


@admin.register(Discipline)
class DisciplineAdmin(admin.ModelAdmin):
    list_display = ['naam']
    search_fields = ['naam']


@admin.register(Profiel)
class ProfielAdmin(admin.ModelAdmin):
    list_display = ['user', 'rol']
    list_filter = ['rol']
    search_fields = ['user__username']


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ['titel', 'discipline_een', 'discipline_twee', 'aangemaakt_door', 'aangemaakt_op']
    list_filter = ['discipline_een', 'discipline_twee']
    search_fields = ['titel', 'omschrijving']


@admin.register(ChallengeDeelname)
class ChallengeDeelnameAdmin(admin.ModelAdmin):
    list_display = ['deelnemer', 'challenge', 'status', 'ingediend_op']
    list_filter = ['status']
    search_fields = ['deelnemer__username', 'challenge__titel']





@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['deelnemer', 'challenge', 'status', 'ingediend_op']
    list_filter = ['status']
    search_fields = ['deelnemer__username', 'challenge__titel']    