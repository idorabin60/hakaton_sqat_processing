from django.db import models

# Create your models here.
from django.db import models


class SquatAnalysis(models.Model):
    rep = models.PositiveIntegerField()
    duration_sec = models.FloatField()
    back_straight = models.CharField(
        max_length=10, choices=[("Yes", "Yes"), ("No", "No")])
    knees_over_toes = models.CharField(
        max_length=10, choices=[("Yes", "Yes"), ("No", "No")])
    min_depth = models.FloatField()
    valid_depth = models.BooleanField()

    def __str__(self):
        return f"Rep {self.rep} - Valid: {self.valid_depth}"
