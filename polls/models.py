import datetime
from django.db import models
from django.contrib import admin
from django.utils import timezone


# Create your models here.
class Question(models.Model):
    """Question of the poll"""
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    end_date = models.DateTimeField('end date')

    def __str__(self):
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
        """Returns true if the question is published"""
        now = timezone.now()
        return now >= self.pub_date

    def can_vote(self):
        """Returns true if the question in the voting duration"""
        now = timezone.now()
        return self.pub_date <= now <= self.end_date


class Choice(models.Model):
    """Choice assigned to each question"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text
