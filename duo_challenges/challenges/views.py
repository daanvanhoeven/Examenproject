from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Challenge, Profiel, ChallengeDeelname, Discipline

def login_view(request):
    fout = None

    if request.method == 'POST':
        gebruikersnaam = request.POST['gebruikersnaam']
        wachtwoord = request.POST['wachtwoord']
        user = authenticate(request, username=gebruikersnaam, password=wachtwoord)

        if user is not None:
            login(request, user)
            return redirect('challenges_lijst')
        else:
            fout = 'Gebruikersnaam of wachtwoord klopt niet.'

    return render(request, 'login.html', {'fout': fout})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def challenges_lijst(request):
    challenges = Challenge.objects.all()
    return render(request, 'challenges_lijst.html', {'challenges': challenges})


@login_required(login_url='login')
def profiel(request):
    profiel, aangemaakt = Profiel.objects.get_or_create(user=request.user)
    disciplines = Discipline.objects.all()

    if request.method == 'POST':
        discipline_id = request.POST['discipline']
        profiel.discipline = get_object_or_404(Discipline, id=discipline_id)
        profiel.save()
        return redirect('profiel')

    return render(request, 'profiel.html', {
        'profiel': profiel,
        'disciplines': disciplines
    })



@login_required(login_url='login')
def mijn_challenges(request):
    deelnames = ChallengeDeelname.objects.filter(deelnemer=request.user)
    return render(request, 'mijn_challenges.html', {'deelnames': deelnames})


@login_required(login_url='login')
def deelnemen(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id)

    al_deelnemer = ChallengeDeelname.objects.filter(
        deelnemer=request.user,
        challenge=challenge
    ).exists()

    if not al_deelnemer:
        ChallengeDeelname.objects.create(
            challenge=challenge,
            deelnemer=request.user,
            status='bezig'
        )

    return redirect('mijn_challenges')


@login_required(login_url='login')
def indienen(request, deelname_id):
    deelname = get_object_or_404(ChallengeDeelname, id=deelname_id, deelnemer=request.user)

    if deelname.status == 'bezig':
        deelname.status = 'ingediend'
        deelname.ingediend_op = timezone.now()
        deelname.save()

    return redirect('mijn_challenges')


@login_required(login_url='login')
def beoordelen(request, deelname_id):
    deelname = get_object_or_404(ChallengeDeelname, id=deelname_id)

    try:
        profiel = Profiel.objects.get(user=request.user)
    except Profiel.DoesNotExist:
        return redirect('challenges_lijst')

    if profiel.rol != 'begeleider':
        return redirect('challenges_lijst')

    if request.method == 'POST':
        beslissing = request.POST['beslissing']
        feedback = request.POST['feedback']

        deelname.status = beslissing
        deelname.feedback = feedback
        deelname.save()

        return redirect('overzicht_ingediend')

    return render(request, 'beoordelen.html', {'deelname': deelname})


@login_required(login_url='login')
def overzicht_ingediend(request):
    try:
        profiel = Profiel.objects.get(user=request.user)
    except Profiel.DoesNotExist:
        return redirect('challenges_lijst')

    if profiel.rol != 'begeleider':
        return redirect('challenges_lijst')

    deelnames = ChallengeDeelname.objects.filter(status='ingediend')
    return render(request, 'overzicht_ingediend.html', {'deelnames': deelnames})