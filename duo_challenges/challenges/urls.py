from django.urls import path
from . import views

urlpatterns = [
    # Basis pagina's voor login, profiel en challenge-overzicht.
    path('', views.challenges_lijst, name='challenges_lijst'),
    path('profiel/', views.profiel, name='profiel'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.challenges_lijst, name='challenges_lijst'),
    path('profiel/', views.profiel, name='profiel'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Routes voor deelnemen, indienen en beoordelen.
    path('challenge/<int:challenge_id>/deelnemen/', views.deelnemen, name='deelnemen'),
    path('deelname/<int:deelname_id>/indienen/', views.indienen, name='indienen'),
    path('project/<int:project_id>/beoordelen/', views.beoordelen, name='beoordelen'),
    path('mijn-challenges/', views.mijn_challenges, name='mijn_challenges'),
    path('overzicht/', views.overzicht_ingediend, name='overzicht_ingediend'),

    # Routes voor projecten en challenges aanmaken.
    path('challenge/<int:challenge_id>/project/aanmaken/', views.project_aanmaken, name='project_aanmaken'),
    path('project/<int:project_id>/indienen/', views.project_indienen, name='project_indienen'),
    path('mijn-projecten/', views.mijn_projecten, name='mijn_projecten'),
    path('challenge/aanmaken/', views.challenge_aanmaken, name='challenge_aanmaken'),
]

