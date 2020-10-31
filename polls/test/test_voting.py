"""Unittest for testing the polls voting"""
import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User

from polls.models import Question, Vote

def create_question(question_text, days, end_date=7):
    """
    Create a question.
    Keyword arguments:
    question_text -- a question text
    days -- published the given number of days offset to now
    end_date -- end date for the question (default 7)
    """
    time = timezone.now() + datetime.timedelta(days=days)
    end_date_time = time + datetime.timedelta(days=end_date)
    return Question.objects.create(question_text=question_text, pub_date=time, end_date=end_date_time)

class VotingTests(TestCase):

    def setUp(self):
        """For setup the test"""
        #create user1
        User.objects.create_user(username="User1",email='User1@gmail.com',password='isp123456')
        #create user2
        User.objects.create_user(username="User2",email='User2@gmail.com',password='isp123456')
        self.question1 = create_question(question_text='Question1', days=-1)
        self.choice1 = self.question1.choice_set.create(choice_text='Choice1', votes=0)
        self.choice2 = self.question1.choice_set.create(choice_text='Choice2', votes=0)
        self.question1_url = reverse('polls:vote', args=(self.question1.id,))

    def test_response_code_authentication_user_vote(self):
        """Authentication user can access to see the detail page"""
        self.client.post(reverse('login'), {'username':'User1', 'password':'isp123456'}, follow=True)
        response = self.client.get(self.question1_url)
        self.assertEqual(response.status_code, 200)

    def test_response_code_unauthenticated_user_vote(self):
        """Unauthenticated user can not access to see the detail page"""
        response = self.client.get(self.question1_url)
        self.assertEqual(response.status_code, 302)

    def test_try_to_vote_choice_one(self):
        """If vote button work it should save number of votes to the database"""
        self.client.post(reverse('login'), {'username':'User1', 'password':'isp123456'}, follow=True)
        selected_choice = self.question1.choice_set.get(pk=self.choice1.id)
        self.client.post(self.question1_url, {'choice': selected_choice.id})
        new_vote = Vote.objects.filter(question=self.question1).filter(user_choice=selected_choice).count()
        self.assertEqual(new_vote, 1)

    def test_try_to_vote_with_two_users_in_the_same_question_but_different_choice(self):
        """When vote with different user it should be save number of votes to the database"""
        #login with User1
        self.client.post(reverse('login'), {'username':'User1', 'password':'isp123456'}, follow=True)
        selected_choice = self.question1.choice_set.get(pk=self.choice1.id)
        #vote choice1
        self.client.post(self.question1_url, {'choice': selected_choice.id})
        #logged out
        response = self.client.get(reverse('logout'))
        #login with User2
        self.client.post(reverse('login'), {'username':'User2', 'password':'isp123456'}, follow=True)
        selected_choice2 = self.question1.choice_set.get(pk=self.choice2.id)
        #vote choice2
        self.client.post(self.question1_url, {'choice': selected_choice2.id})
        #logged out
        response = self.client.get(reverse('logout'))
        choice1_vote = Vote.objects.filter(question=self.question1).filter(user_choice=selected_choice).count()
        choice2_vote = Vote.objects.filter(question=self.question1).filter(user_choice=selected_choice2).count()
        self.assertEqual(choice1_vote, 1)
        self.assertEqual(choice2_vote, 1)

    def test_try_to_vote_with_two_users_in_the_same_question_and_the_same_choice(self):
        """Number of votes must more than one if two user vote that choice"""
        #login with User1
        self.client.post(reverse('login'), {'username':'User1', 'password':'isp123456'}, follow=True)
        selected_choice = self.question1.choice_set.get(pk=self.choice1.id)
        #vote choice1
        self.client.post(self.question1_url, {'choice': selected_choice.id})
        #logged out
        response = self.client.get(reverse('logout'))
        #login with User2
        self.client.post(reverse('login'), {'username':'User2', 'password':'isp123456'}, follow=True)
        selected_choice2 = self.question1.choice_set.get(pk=self.choice1.id)
        #vote choice1
        self.client.post(self.question1_url, {'choice': selected_choice2.id})
        #logged out
        response = self.client.get(reverse('logout'))
        choice1_vote = Vote.objects.filter(question=self.question1).filter(user_choice=selected_choice).count()
        self.assertEqual(choice1_vote, 2)

    def test_is_replace_the_previous_vote_when_resubmit_on_the_question(self):
        """When the user resubmit vote replaces his previous vote"""
        #login with User1
        self.client.post(reverse('login'), {'username':'User1', 'password':'isp123456'}, follow=True)
        selected_choice = self.question1.choice_set.get(pk=self.choice1.id)
        selected_choice2 = self.question1.choice_set.get(pk=self.choice2.id)
        #vote choice1
        self.client.post(self.question1_url, {'choice': selected_choice.id})
        #vote choice2
        self.client.post(self.question1_url, {'choice': selected_choice2.id})
        choice1_vote = Vote.objects.filter(question=self.question1).filter(user_choice=selected_choice).count()
        choice2_vote = Vote.objects.filter(question=self.question1).filter(user_choice=selected_choice2).count()
        self.assertEqual(choice1_vote, 0)
        self.assertEqual(choice2_vote, 1)