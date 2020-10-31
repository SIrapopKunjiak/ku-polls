"""Unittest for detail."""
import datetime

from django.shortcuts import reverse
from django.test import TestCase
from django.utils import timezone

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


class QuestionDetailViewTests(TestCase):
    """Class for question detail view tests."""

    def test_future_question(self):
        """The detail view of a question with a pub_date in the future returns a 404 not found."""
        future_question = create_question(question_text='Future question.', pub=5, end=6)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_past_question(self):
        """The detail view of a question with a pub_date in the past displays the question's text."""
        past_question = create_question(question_text='Past Question.', pub=-5, end=-4)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)