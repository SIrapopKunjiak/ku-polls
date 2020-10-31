"""Unittest for testing models"""
import datetime

from django.test import TestCase
from django.utils import timezone

from polls.models import Question

class QuestionModelTests(TestCase):
    """Testing class for Model."""

    def test_was_published_recently_with_future_question(self):
        """was_published_recently() returns False for questions whose pub_date is in the future."""
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """was_published_recently() returns False for questions whose pub_date is older than 1 day."""
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """was_published_recently() returns True for questions whose pub_date is within the last day."""
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

    def test_is_published_with_old_question(self):
        """is_published() return True for questions when reach to pub_date."""
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.is_published(), True)

    def test_is_published_with_recent_question(self):
        """is_published() return True for questions when reach to pub_date."""
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.is_published(), True)

    def test_is_published_with_future_question(self):
        """is_published() return False for questions that not reach to pub_date."""
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.is_published(), False)

    def test_can_vote_with_published_question_but_it_closed(self):
        """can_vote() return False for the questions that is_published() is True but reach to end_date."""
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        end_date_time = time + datetime.timedelta(seconds=10)
        question = Question(pub_date=time, end_date=end_date_time)
        self.assertIs(question.can_vote(), False)

    def test_can_vote_with_unpublished_question(self):
        """can_vote() return False for the questions that is_published() is False."""
        time = timezone.now() + datetime.timedelta(days=30)
        end_date_time = time + datetime.timedelta(seconds=10)
        question = Question(pub_date=time, end_date=end_date_time)
        self.assertIs(question.can_vote(), False)

    def test_can_vote_with_published_question_and_it_opened(self):
        """can_vote() return True for the questions that is_published() is True but not reach to end_date."""
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        end_date_time = time + datetime.timedelta(days=10)
        question = Question(pub_date=time, end_date=end_date_time)
        self.assertIs(question.can_vote(), True) 