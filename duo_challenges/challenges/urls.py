from django.urls import path
from . import views

urlpatterns = [
    # Basis pagina's voor login, profiel en challenge-overzicht.
    path('', views.afgeronde_projecten, name='home'),
    path('challenges/', views.challenges_lijst, name='challenges_lijst'),
    path('profiel/', views.profiel, name='profiel'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Routes voor deelnemen, indienen en beoordelen.
  
  
    path('project/<int:project_id>/beoordelen/', views.beoordelen, name='beoordelen'),
    path('project/<int:project_id>/partner-kiezen/', views.partner_kiezen, name='partner_kiezen'),
    path('project/<int:project_id>/uitnodigen/', views.partner_uitnodigen, name='partner_uitnodigen'),
    path('project/<int:project_id>/uitnodiging/accepteren/', views.uitnodiging_accepteren, name='uitnodiging_accepteren'),
    path('project/<int:project_id>/uitnodiging/weigeren/', views.uitnodiging_weigeren, name='uitnodiging_weigeren'),
    path('overzicht/', views.overzicht_ingediend, name='overzicht_ingediend'),
    path('projecten-zonder-partner/', views.projecten_zonder_partner, name='projecten_zonder_partner'),
    path('afgeronde-projecten/', views.afgeronde_projecten, name='afgeronde_projecten'),
    path('project/<int:project_id>/like/', views.project_liken, name='project_liken'),
    # Routes voor projecten en challenges aanmaken.
    path('challenge/<int:challenge_id>/project/aanmaken/', views.project_aanmaken, name='project_aanmaken'),
    path('project/<int:project_id>/indienen/', views.project_indienen, name='project_indienen'),
    path('mijn-projecten/', views.mijn_projecten, name='mijn_projecten'),
    path('challenge/aanmaken/', views.challenge_aanmaken, name='challenge_aanmaken'),
]

