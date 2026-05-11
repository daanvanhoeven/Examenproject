from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Challenge, Profiel, ChallengeDeelname, Discipline, Project





def zoek_partner(gebruiker, challenge):
    # Haal de disciplines van de huidige gebruiker op.
    eigen_profiel = Profiel.objects.get(user=gebruiker)
    eigen_disciplines = eigen_profiel.disciplines.all()

    # Zoek andere projecten bij dezelfde challenge zonder partner.
    andere_projecten = Project.objects.filter(
        challenge=challenge,
        partner=None
    ).exclude(deelnemer=gebruiker)

    # Zoek iemand met een andere discipline voor de automatische matching.
    for project in andere_projecten:
        try:
            ander_profiel = Profiel.objects.get(user=project.deelnemer)
        except Profiel.DoesNotExist:
            continue

        andere_disciplines = ander_profiel.disciplines.all()

        # Geen overlap betekent dat deze gebruiker een goede partner is.
        overlap = eigen_disciplines.filter(id__in=andere_disciplines).exists()
        if not overlap:
            return project.deelnemer

    return None

def login_view(request):
    # Verwerkt het inloggen van de gebruiker.
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
    # Logt de gebruiker uit en stuurt terug naar de loginpagina.
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def challenges_lijst(request):
    # Toont alle challenges op de overzichtspagina.
    challenges = Challenge.objects.all()
    return render(request, 'challenges_lijst.html', {'challenges': challenges})


@login_required(login_url='login')
def profiel(request):
    # Laat de gebruiker zijn profiel en disciplines aanpassen.
    profiel, aangemaakt = Profiel.objects.get_or_create(user=request.user)
    disciplines = Discipline.objects.all()

    if request.method == 'POST':
        gekozen_ids = request.POST.getlist('disciplines')
        profiel.disciplines.set(gekozen_ids)
        profiel.save()
        return redirect('profiel')

    return render(request, 'profiel.html', {
        'profiel': profiel,
        'disciplines': disciplines
    })



@login_required(login_url='login')
def mijn_challenges(request):
    # Toont de challenges waaraan de gebruiker meedoet.
    deelnames = ChallengeDeelname.objects.filter(deelnemer=request.user)
    return render(request, 'mijn_challenges.html', {'deelnames': deelnames})


@login_required(login_url='login')
def deelnemen(request, challenge_id):
    # Schrijft de gebruiker in voor een challenge als dat nog niet gebeurd is.
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
    # Zet een deelname op ingediend en bewaart de inleverdatum.
    deelname = get_object_or_404(ChallengeDeelname, id=deelname_id, deelnemer=request.user)

    if deelname.status == 'bezig':
        deelname.status = 'ingediend'
        deelname.ingediend_op = timezone.now()
        deelname.save()

    return redirect('mijn_challenges')


@login_required(login_url='login')
def beoordelen(request, project_id):
    # Alleen begeleiders mogen projecten beoordelen en feedback geven.
    project = get_object_or_404(Project, id=project_id)

    try:
        profiel = Profiel.objects.get(user=request.user)
    except Profiel.DoesNotExist:
        return redirect('challenges_lijst')

    if profiel.rol != 'begeleider':
        return redirect('challenges_lijst')

    if request.method == 'POST':
        beslissing = request.POST['beslissing']
        feedback = request.POST['feedback']

        project.status = beslissing
        project.feedback = feedback
        project.save()

        return redirect('overzicht_ingediend')

    return render(request, 'beoordelen.html', {'project': project})


@login_required(login_url='login')
def overzicht_ingediend(request):
    # Laat begeleiders alle ingediende projecten zien.
    try:
        profiel = Profiel.objects.get(user=request.user)
    except Profiel.DoesNotExist:
        return redirect('challenges_lijst')

    if profiel.rol != 'begeleider':
        return redirect('challenges_lijst')

    projecten = Project.objects.filter(status='ingediend')
    return render(request, 'overzicht_ingediend.html', {'projecten': projecten})




@login_required(login_url='login')
def project_aanmaken(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id)

    # Check of deelnemer al een project heeft bij deze challenge
    al_project = Project.objects.filter(
        deelnemer=request.user,
        challenge=challenge
    ).exists()

    if al_project:
        return redirect('mijn_projecten')

    # Haal disciplines van de deelnemer op
    try:
        profiel = Profiel.objects.get(user=request.user)
    except Profiel.DoesNotExist:
        return redirect('profiel')

    eigen_disciplines = profiel.disciplines.all()
    vereiste_disciplines = [challenge.discipline_een, challenge.discipline_twee]

    # Check of deelnemer minstens één vereiste discipline heeft
    heeft_discipline = eigen_disciplines.filter(
        id__in=[d.id for d in vereiste_disciplines]
    ).exists()

    if not heeft_discipline:
        return render(request, 'geen_toegang.html', {
            'challenge': challenge,
            'eigen_disciplines': eigen_disciplines,
            'vereiste_disciplines': vereiste_disciplines,
        })

    if request.method == 'POST':
        github_link = request.POST['github_link']
        beschrijving = request.POST['beschrijving']

        partner = zoek_partner(request.user, challenge)

        nieuw_project = Project.objects.create(
            challenge=challenge,
            deelnemer=request.user,
            github_link=github_link,
            beschrijving=beschrijving,
            partner=partner,
            status='bezig'
        )

        if partner:
            partner_project = Project.objects.filter(
                deelnemer=partner,
                challenge=challenge
            ).first()
            if partner_project:
                partner_project.partner = request.user
                partner_project.save()

        return redirect('mijn_projecten')

    return render(request, 'project_aanmaken.html', {'challenge': challenge})


@login_required(login_url='login')
def project_indienen(request, project_id):
    # Zet een project op ingediend zodat een begeleider het kan beoordelen.
    project = get_object_or_404(Project, id=project_id, deelnemer=request.user)

    if project.status == 'bezig':
        project.status = 'ingediend'
        project.ingediend_op = timezone.now()
        project.save()

    return redirect('mijn_projecten')


@login_required(login_url='login')
def mijn_projecten(request):
    # Toont de projecten van de ingelogde gebruiker.
    projecten = Project.objects.filter(deelnemer=request.user)
    return render(request, 'mijn_projecten.html', {'projecten': projecten})

@login_required(login_url='login')
def challenge_aanmaken(request):
    # Alleen begeleiders mogen nieuwe challenges aanmaken.
    try:
        profiel = Profiel.objects.get(user=request.user)
    except Profiel.DoesNotExist:
        return redirect('challenges_lijst')

    if profiel.rol != 'begeleider':
        return redirect('challenges_lijst')

    disciplines = Discipline.objects.all()

    if request.method == 'POST':
        titel = request.POST['titel']
        omschrijving = request.POST['omschrijving']
        discipline_een_id = request.POST['discipline_een']
        discipline_twee_id = request.POST['discipline_twee']

        Challenge.objects.create(
            titel=titel,
            omschrijving=omschrijving,
            discipline_een=get_object_or_404(Discipline, id=discipline_een_id),
            discipline_twee=get_object_or_404(Discipline, id=discipline_twee_id),
            aangemaakt_door=request.user
        )
        return redirect('challenges_lijst')

    return render(request, 'challenge_aanmaken.html', {'disciplines': disciplines})
