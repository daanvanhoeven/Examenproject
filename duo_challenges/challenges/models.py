from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Discipline(models.Model):
    # Discipline die een gebruiker of challenge kan hebben.
    naam = models.CharField(max_length=100)

    def __str__(self):
        return self.naam


class Profiel(models.Model):
    # Profiel van een gebruiker met rol en disciplines.
    ROL_KEUZES = [
        ('deelnemer', 'Deelnemer'),
        ('begeleider', 'Begeleider'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.CharField(max_length=20, choices=ROL_KEUZES, default='deelnemer')
    # Een gebruiker kan meerdere disciplines kiezen op de profielpagina.
    disciplines = models.ManyToManyField(
        Discipline,
        blank=True
    )

    def __str__(self):
        return f"{self.user.username} ({self.rol})"


class Challenge(models.Model):
    # Challenge die door een begeleider wordt aangemaakt.
    titel = models.CharField(max_length=200)
    omschrijving = models.TextField()
    discipline_een = models.ForeignKey(
        Discipline,
        on_delete=models.CASCADE,
        related_name='challenges_een'
    )
    discipline_twee = models.ForeignKey(
        Discipline,
        on_delete=models.CASCADE,
        related_name='challenges_twee'
    )
    aangemaakt_door = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    # Datum wordt automatisch ingevuld bij aanmaken.
    aangemaakt_op = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titel


class Project(models.Model):
    # Project met GitHub-link dat bij een challenge hoort.
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    deelnemer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='projecten'
    )
    # Partner wordt gekoppeld op basis van discipline of eigen keuze.
    partner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='partner_projecten'
    )
    github_link = models.URLField()
    beschrijving = models.TextField(blank=True)
    # Status geeft aan in welke fase het project zich bevindt.
    status = models.CharField(
        max_length=20,
        choices=[
            ('bezig', 'Bezig'),
            ('ingediend', 'Ingediend'),
            ('goedgekeurd', 'Goedgekeurd'),
            ('afgekeurd', 'Afgekeurd'),
        ],
        default='bezig'
    )
    feedback = models.TextField(blank=True, null=True)
    ingediend_op = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.deelnemer.username} - {self.challenge.titel}"


@receiver(post_save, sender=User)
def maak_profiel_aan(sender, instance, created, **kwargs):
    # Maakt automatisch een profiel aan bij een nieuwe gebruiker.
    if created:
        Profiel.objects.create(user=instance)