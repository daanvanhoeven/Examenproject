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
    aangemaakt_op = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titel


class ChallengeDeelname(models.Model):

    STATUS_KEUZES = [
        ('bezig', 'Bezig'),
        ('ingediend', 'Ingediend'),
        ('goedgekeurd', 'Goedgekeurd'),
        ('afgekeurd', 'Afgekeurd'),
    ]

    challenge = models.ForeignKey(
        Challenge,
        on_delete=models.CASCADE
    )
    # Houdt bij welke gebruiker meedoet en wat de status is.
    deelnemer = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_KEUZES,
        default='bezig'
    )
    feedback = models.TextField(blank=True, null=True)
    ingediend_op = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.deelnemer.username} - {self.challenge.titel} ({self.status})"


@receiver(post_save, sender=User)
def maak_profiel_aan(sender, instance, created, **kwargs):
    # Maakt automatisch een profiel aan bij een nieuwe gebruiker.
    if created:
        Profiel.objects.create(user=instance)





class Project(models.Model):
    # Project met GitHub-link dat bij een challenge hoort.
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    deelnemer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projecten')
    # Partner wordt automatisch gezocht op basis van discipline.
    partner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='partner_projecten')
    github_link = models.URLField()
    beschrijving = models.TextField(blank=True)
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
