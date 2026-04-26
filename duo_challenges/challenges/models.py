from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Discipline(models.Model):
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
    discipline = models.ForeignKey(
        Discipline,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.user.username} ({self.rol})"


class Challenge(models.Model):
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
    if created:
        Profiel.objects.create(user=instance)