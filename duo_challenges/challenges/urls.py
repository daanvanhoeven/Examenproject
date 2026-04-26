from django.urls import path
from . import views

urlpatterns = [
    path('', views.challenges_lijst, name='challenges_lijst'),
    path('profiel/', views.profiel, name='profiel'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.challenges_lijst, name='challenges_lijst'),
    path('profiel/', views.profiel, name='profiel'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('challenge/<int:challenge_id>/deelnemen/', views.deelnemen, name='deelnemen'),
    path('deelname/<int:deelname_id>/indienen/', views.indienen, name='indienen'),
    path('deelname/<int:deelname_id>/beoordelen/', views.beoordelen, name='beoordelen'),
    path('mijn-challenges/', views.mijn_challenges, name='mijn_challenges'),
    path('overzicht/', views.overzicht_ingediend, name='overzicht_ingediend'),
]

