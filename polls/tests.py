import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question

def create_question(question_text, pub, end):
    """
    Create a question with the given `question_text` and published the
    given number of `pub` and `end` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    pub_date = timezone.now() + datetime.timedelta(days=pub)
    end_date = timezone.now() + datetime.timedelta(days=end)
    return Question.objects.create(question_text=question_text, pub_date=pub_date, end_date=end_date)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        create_question(question_text="Past question.", pub=-30, end=-27)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question(question_text="Future question.", pub=30, end=31)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        create_question(question_text="Past question.", pub=-30, end=-27)
        create_question(question_text="Future question.", pub=30, end=31)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        create_question(question_text="Past question 1.", pub=-30, end=-27)
        create_question(question_text="Past question 2.", pub=-5, end=-3)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )


class QuestionModelTests(TestCase):

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

    def test_is_published_with_past_question(self):
        """
        is_published() returns True for questions whose pub_date is in the past.
        """
        time = timezone.now() - datetime.timedelta(days=2)
        past_question = Question(pub_date=time)
        self.assertIs(past_question.is_published(), True)

    def test_is_published_with_future_question(self):
        """
        is_published() returns False for questions whose pub_date is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=5)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.is_published(), False)

    def test_can_vote_with_past_question(self):
        """
        can_vote() returns False for questions that are closed.
        """
        time = timezone.now() - datetime.timedelta(days=4)
        end_time = timezone.now() - datetime.timedelta(days=2)
        past_question = Question(pub_date=time, end_date=end_time)
        self.assertIs(past_question.can_vote(), False)

    def test_can_vote_with_future_question(self):
        """
        can_vote() returns False for questions that are not open yet.
        """
        time = timezone.now() + datetime.timedelta(days=1)
        end_time = timezone.now() + datetime.timedelta(days=3)
        future_question = Question(pub_date=time, end_date=end_time)
        self.assertIs(future_question.can_vote(), False)

class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text='Future question.', pub=5, end=6)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date and end_date in the past
        which is closed, they will displayed the question's text.
        """
        past_question = create_question(question_text='Past Question.', pub=-5, end=-4)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)