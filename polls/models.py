"""Models for the poll application."""
import datetime
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from django.utils import timezone


# Create your models here.
class Question(models.Model):
    """Question of the poll."""

    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    end_date = models.DateTimeField('end date')

    def __str__(self):
        """Return question text as string."""
        return self.question_text

    @admin.display(
        boolean=True,
        ordering='pub_date',
        description='Published recently?'
    )
    def was_published_recently(self):
        """Return true is the question is published less than 1 day from now."""
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def is_published(self):
        """Return true if the question is published."""
        now = timezone.now()
        return now >= self.pub_date

    def can_vote(self):
        """Return true if the question in the voting duration."""
        now = timezone.now()
        return self.pub_date <= now <= self.end_date


class Choice(models.Model):
    """Choice assigned to each question."""

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    # votes = models.IntegerField(default=0)

    def __str__(self):
        """Return choice text as string representation."""
        return self.choice_text

    @property
    def votes(self) -> int:
        """Return votes in that choice."""
        return Vote.objects.filter(choice=self).count()


class Vote(models.Model):
    """Vote assigned to each choice."""

    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    voter = models.ForeignKey(
                              User,
                              on_delete=models.CASCADE,
                              null=False,
                              blank=False)

    def __str__(self):
        """Return vote representation using both username and choice."""
        return f"Vote by {self.voter.username} for {self.choice}"
