"""Views for KU-Polls."""

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import generic
from .models import Choice, Question, Vote
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import logging.config
from .settings import LOGGING

logging.config.dictConfig(LOGGING)
logger = logging.getLogger('polls')

class IndexView(generic.ListView):
    """Class for index view."""
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')


class DetailView(generic.DetailView):
    """Class for detail view."""
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    """Class for results view."""
    model = Question
    template_name = 'polls/results.html'


def index(request):
    """Index to view."""
    latest_question_list = Question.objects.order_by('-pub_date')
    context = {'latest_question_list': latest_question_list}
    return render(request, 'polls/index.html', context)


def detail(request, question_id):
    """Details to view."""
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/detail.html', {'question': question})


def results(request, question_id):
    """Results to view."""
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', {'question': question})


@login_required
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        if not (question.can_vote()):
            messages.warning(request, "This polls are not allowed.")
            elif Vote.objects.filter(user=request.user, question=question).exists():
            current_votes = Vote.objects.get(user=request.user, question=question)
            current_votes.choice = selected_choice
            current_votes.save()
        else:
            question.vote_set.create(choice=selected_choice, user=request.user)
            messages.success(request, "Vote success.")
            return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
