"""Models for KU-Polls."""

import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Question(models.Model):
    """Class for question in KU-Polls."""
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    end_date = models.DateTimeField('ending date')

    def __str__(self):
        """Return the question text."""
        return self.question_text

    def was_published_recently(self):
        """Return True if the question was published recently."""
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def is_published(self):
        """Return True if the question is published."""
        return timezone.now() >= self.pub_date

    def can_vote(self):
        """Return True if you can vote the question."""
        return self.end_date >= timezone.now() >= self.pub_date

    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'


class Choice(models.Model):
    """Class for choices in KU-Polls."""

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        """Return the selected choice text."""
        return self.choice_text

    @property
    def votes(self):
        """Return the votes that the user can change."""
        return self.question.vote_set.filter(choice=self).count()


class Vote(models.Model):
    """Class for vote in KU-Polls."""

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
