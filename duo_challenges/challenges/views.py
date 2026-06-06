from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from .models import Challenge, Profiel, Discipline, Project
from django.contrib.auth.models import User


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
    goedgekeurde_challenge_ids = Project.objects.filter(
        Q(deelnemer=request.user) | Q(partner=request.user),
        status='goedgekeurd'
    ).values_list('challenge_id', flat=True)

    challenges = Challenge.objects.exclude(id__in=goedgekeurde_challenge_ids)

    projecten = Project.objects.filter(deelnemer=request.user)

    uitgenodigde_projecten = Project.objects.filter(
        uitgenodigde_partner=request.user
    )

    for challenge in challenges:
        challenge.user_project = projecten.filter(challenge=challenge).first()
        challenge.uitnodiging = uitgenodigde_projecten.filter(challenge=challenge).first()

    return render(request, 'challenges_lijst.html', {
        'challenges': challenges,
        'projecten': projecten,
        'uitgenodigde_projecten': uitgenodigde_projecten,
    })


@login_required(login_url='login')
def profiel(request):
    # Laat de gebruiker zijn profiel en disciplines aanpassen.
    profiel, aangemaakt = Profiel.objects.get_or_create(user=request.user)
    disciplines = Discipline.objects.all()

    # Haal alle projecten op van de ingelogde gebruiker.
    projecten = Project.objects.filter(deelnemer=request.user)

    if request.method == 'POST':
        # Disciplines opslaan
        gekozen_ids = request.POST.getlist('disciplines')
        profiel.disciplines.set(gekozen_ids)

        # Quote opslaan
        profiel.quote = request.POST.get('quote', '').strip()

        profiel.save()

        return redirect('profiel')

    return render(request, 'profiel.html', {
        'profiel': profiel,
        'disciplines': disciplines,
        'projecten': projecten,
    })


@login_required(login_url='login')
def project_aanmaken(request, challenge_id):
    # Alleen deelnemers met de juiste discipline kunnen een project aanmaken.
    challenge = get_object_or_404(Challenge, id=challenge_id)

    # Controleer of de gebruiker al deelneemt aan deze challenge.
    al_deelname = Project.objects.filter(
        Q(deelnemer=request.user) | Q(partner=request.user),
        challenge=challenge
    ).exists()

    if al_deelname:
        return redirect('mijn_projecten')

    # Een openstaande uitnodiging blokkeert zelf starten tot de gebruiker kiest.
    heeft_uitnodiging = Project.objects.filter(
        challenge=challenge,
        uitgenodigde_partner=request.user
    ).exists()

    if heeft_uitnodiging:
        return redirect('mijn_projecten')

    # Haal het profiel op van de ingelogde gebruiker.
    try:
        profiel = Profiel.objects.get(user=request.user)
    except Profiel.DoesNotExist:
        return redirect('profiel')

    eigen_disciplines = profiel.disciplines.all()
    vereiste_disciplines = [challenge.discipline_een, challenge.discipline_twee]

    # Controleer of de gebruiker minimaal één vereiste discipline heeft.
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

        # Maak het project aan zonder partner, begeleider koppelt die later.
        Project.objects.create(
            challenge=challenge,
            deelnemer=request.user,
            github_link=github_link,
            beschrijving=beschrijving,
            partner=None,
            status='bezig'
        )

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
    # Toont eigen projecten, partnerprojecten en openstaande uitnodigingen.
    projecten = Project.objects.filter(
        Q(deelnemer=request.user) |
        Q(partner=request.user) |
        Q(uitgenodigde_partner=request.user)
    ).distinct()
    return render(request, 'mijn_projecten.html', {'projecten': projecten})


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


@login_required(login_url='login')
def partner_kiezen(request, project_id):
    # Alleen begeleiders mogen een partner koppelen aan een project.
    project = get_object_or_404(Project, id=project_id)

    try:
        profiel = Profiel.objects.get(user=request.user)
    except Profiel.DoesNotExist:
        return redirect('challenges_lijst')

    if profiel.rol != 'begeleider':
        return redirect('challenges_lijst')

    # Zoek deelnemers met de andere vereiste discipline zonder partner.
    vereiste_disciplines = [project.challenge.discipline_een, project.challenge.discipline_twee]
    deelnemer_disciplines = Profiel.objects.get(user=project.deelnemer).disciplines.all()

    andere_discipline_ids = [
        d.id for d in vereiste_disciplines
        if d not in deelnemer_disciplines
    ]

    # Mogelijke partners hebben de andere discipline en hebben nog geen partner.
    mogelijke_partners = Profiel.objects.filter(
        disciplines__id__in=andere_discipline_ids
    ).exclude(user=project.deelnemer)

    if request.method == 'POST':
        partner_id = request.POST.get('partner')

        if partner_id:
            try:
                partner = User.objects.get(id=partner_id)
            except User.DoesNotExist:
                partner = None

            if partner:
                # Koppel de partner aan het project.
                project.partner = partner
                project.save()

                # Koppel ook terug als de partner al een project heeft.
                partner_project = Project.objects.filter(
                    deelnemer=partner,
                    challenge=project.challenge
                ).first()
                if partner_project:
                    partner_project.partner = project.deelnemer
                    partner_project.save()

        return redirect('overzicht_ingediend')

    return render(request, 'partner_kiezen.html', {
        'project': project,
        'mogelijke_partners': mogelijke_partners,
    })


@login_required(login_url='login')
def projecten_zonder_partner(request):
    # Alleen begeleiders mogen dit overzicht zien.
    try:
        profiel = Profiel.objects.get(user=request.user)
    except Profiel.DoesNotExist:
        return redirect('challenges_lijst')

    if profiel.rol != 'begeleider':
        return redirect('challenges_lijst')

    # Haalt alle projecten op zonder partner.
    projecten = Project.objects.filter(partner=None)
    return render(request, 'projecten_zonder_partner.html', {'projecten': projecten})


@login_required(login_url='login')
def partner_uitnodigen(request, project_id):
    # Haal het project op van de ingelogde deelnemer.
    project = get_object_or_404(
        Project,
        id=project_id,
        deelnemer=request.user
    )

    if project.partner:
        return redirect('mijn_projecten')

    # Bepaal welke discipline de partner moet hebben.
    vereiste_disciplines = [
        project.challenge.discipline_een,
        project.challenge.discipline_twee
    ]

    try:
        deelnemer_disciplines = Profiel.objects.get(
            user=project.deelnemer
        ).disciplines.all()
    except Profiel.DoesNotExist:
        deelnemer_disciplines = Discipline.objects.none()

    andere_discipline_ids = [
        discipline.id for discipline in vereiste_disciplines
        if discipline not in deelnemer_disciplines
    ]

    if not andere_discipline_ids:
        andere_discipline_ids = [discipline.id for discipline in vereiste_disciplines]

    # Sluit gebruikers uit die al bij deze challenge betrokken zijn.
    bezette_gebruikers_ids = Project.objects.filter(
        challenge=project.challenge
    ).filter(
        Q(deelnemer__isnull=False) |
        Q(partner__isnull=False) |
        Q(uitgenodigde_partner__isnull=False)
    ).values_list('deelnemer_id', 'partner_id', 'uitgenodigde_partner_id')

    gebruikers_die_niet_mogen = {request.user.id}
    for deelnemer_id, partner_id, uitgenodigde_partner_id in bezette_gebruikers_ids:
        if deelnemer_id:
            gebruikers_die_niet_mogen.add(deelnemer_id)
        if partner_id:
            gebruikers_die_niet_mogen.add(partner_id)
        if uitgenodigde_partner_id:
            gebruikers_die_niet_mogen.add(uitgenodigde_partner_id)

    # Toon alleen deelnemers met de juiste discipline.
    gebruikers_ids = Profiel.objects.filter(
        rol='deelnemer',
        disciplines__id__in=andere_discipline_ids
    ).exclude(
        user_id__in=gebruikers_die_niet_mogen
    ).values_list('user_id', flat=True).distinct()

    gebruikers = User.objects.filter(id__in=gebruikers_ids)

    if request.method == 'POST':
        # Controleer server-side of de gekozen partner toegestaan is.
        partner_id = request.POST.get('partner')

        if partner_id:
            try:
                partner = gebruikers.get(id=partner_id)
            except User.DoesNotExist:
                partner = None

            if partner:
                # Slaat de uitnodiging op en blokkeert het project tijdelijk.
                project.uitgenodigde_partner = partner
                project.geblokkeerd = True
                project.save()

        return redirect('mijn_projecten')

    return render(request, 'partner_uitnodigen.html', {
        'project': project,
        'gebruikers': gebruikers,
    })


@login_required(login_url='login')
def uitnodiging_accepteren(request, project_id):
    # Alleen de uitgenodigde gebruiker mag de uitnodiging accepteren.
    project = get_object_or_404(
        Project,
        id=project_id,
        uitgenodigde_partner=request.user
    )

    # Koppel de gebruiker als partner en haal de blok weg.
    project.partner = request.user
    project.uitgenodigde_partner = None
    project.geblokkeerd = False
    project.save()

    return redirect('mijn_projecten')


@login_required(login_url='login')
def uitnodiging_weigeren(request, project_id):
    # Alleen de uitgenodigde gebruiker mag de uitnodiging weigeren.
    project = get_object_or_404(
        Project,
        id=project_id,
        uitgenodigde_partner=request.user
    )

    # Maak de uitnodiging leeg zodat het project weer vrij is.
    project.uitgenodigde_partner = None
    project.geblokkeerd = False
    project.save()

    return redirect('mijn_projecten')
