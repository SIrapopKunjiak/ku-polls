"""Unittest for testing index"""
import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from ..models import Question


def create_question(question_text, pub, end):
    """Create question.
    Create a question with the given `question_text` and published the
    given number of `pub` and `end` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    pub_date = timezone.now() + datetime.timedelta(days=pub)
    end_date = timezone.now() + datetime.timedelta(days=end)
    return Question.objects.create(question_text=question_text, pub_date=pub_date, end_date=end_date)

class QuestionIndexViewTests(TestCase):
    """Class for question index view tests."""

    def test_no_questions(self):
        """If no questions exist, an appropriate message is displayed."""
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """Questions with a pub_date in the past are displayed on the index page."""
        create_question(question_text="Past question.", pub=-30, end=-27)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_future_question(self):
        """Questions with a pub_date in the future aren't displayed on the index page."""
        create_question(question_text="Future question.", pub=30, end=31)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """Even if both past and future questions exist, only past questions are displayed."""
        create_question(question_text="Past question.", pub=-30, end=-27)
        create_question(question_text="Future question.", pub=30, end=31)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_two_past_questions(self):
        """The questions index page may display multiple questions."""
        create_question(question_text="Past question 1.", pub=-30, end=-27)
        create_question(question_text="Past question 2.", pub=-5, end=-3)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )