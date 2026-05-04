from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Challenge, Profiel, ChallengeDeelname, Discipline, Project





def zoek_partner(gebruiker, challenge):
    # Haal de disciplines van de huidige gebruiker op
    eigen_profiel = Profiel.objects.get(user=gebruiker)
    eigen_disciplines = eigen_profiel.disciplines.all()

    # Zoek andere projecten bij dezelfde challenge zonder partner
    andere_projecten = Project.objects.filter(
        challenge=challenge,
        partner=None
    ).exclude(deelnemer=gebruiker)

    # Loop door andere projecten en zoek iemand met een andere discipline
    for project in andere_projecten:
        try:
            ander_profiel = Profiel.objects.get(user=project.deelnemer)
        except Profiel.DoesNotExist:
            continue

        andere_disciplines = ander_profiel.disciplines.all()

        # Controleer of er geen overlap is in disciplines
        overlap = eigen_disciplines.filter(id__in=andere_disciplines).exists()
        if not overlap:
            return project.deelnemer

    return None

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
def beoordelen(request, project_id):
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

    al_project = Project.objects.filter(
        deelnemer=request.user,
        challenge=challenge
    ).exists()

    if al_project:
        return redirect('mijn_projecten')

    if request.method == 'POST':
        github_link = request.POST['github_link']
        beschrijving = request.POST['beschrijving']

        # Zoek automatisch een partner
        partner = zoek_partner(request.user, challenge)

        # Maak het project aan
        nieuw_project = Project.objects.create(
            challenge=challenge,
            deelnemer=request.user,
            github_link=github_link,
            beschrijving=beschrijving,
            partner=partner,
            status='bezig'
        )

        # Koppel ook de partner terug aan dit project
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
    project = get_object_or_404(Project, id=project_id, deelnemer=request.user)

    if project.status == 'bezig':
        project.status = 'ingediend'
        project.ingediend_op = timezone.now()
        project.save()

    return redirect('mijn_projecten')


@login_required(login_url='login')
def mijn_projecten(request):
    projecten = Project.objects.filter(deelnemer=request.user)
    return render(request, 'mijn_projecten.html', {'projecten': projecten})

@login_required(login_url='login')
def challenge_aanmaken(request):
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