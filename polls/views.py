"""Views for poll application."""
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Question, Choice, Vote
from django.views import generic
import logging

logger = logging.getLogger("polls")


# Create your views here.
class IndexView(generic.ListView):
    """Display latest questions."""

    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return all available questions."""
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')


class DetailView(generic.DetailView):
    """Question detail page."""

    model = Question
    template_name = 'polls/detail.html'

    def get(self, request, *args, **kwargs):
        """
        Get question object based on id.

        If the question is already ended, it redirects to result view.
        If the question is not available yet, it redirects to the home page
        with an error message.

        """
        try:
            self.object = self.get_object()
            if not self.object.can_vote():
                return redirect(reverse('polls:results', args=(self.object.id,)))
            context = self.get_context_data(object=self.object)
            return self.render_to_response(context)
        except Http404:
            messages.add_message(request, messages.ERROR, "Question not found")
            return redirect(reverse('polls:index'))

    def get_queryset(self):
        """Exclude unpublished questions."""
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    """Question result page."""

    model = Question
    template_name = 'polls/results.html'

    def get(self, request, *args, **kwargs):
        """
        Get question by id.

        If there is no such question or it is not available,
        it redirects to the home page with an error message.
        """
        try:
            return super(ResultsView, self).get(request, *args, **kwargs)
        except Http404:
            messages.add_message(request, messages.ERROR, "Question not found")
            return redirect(reverse('polls:index'))

    def get_queryset(self):
        """Exclude unpublished questions."""
        return Question.objects.filter(pub_date__lte=timezone.now())


@login_required
def vote(request, question_id: int):
    """Vote on a question."""
    question = get_object_or_404(Question, pk=question_id)
    if not question.can_vote():
        messages.error(request, "The question is ended. Voting is not allowed.")
        return redirect('polls:index')
    try:
        choice_id = request.POST['choice']
        selected_choice = question.choice_set.get(pk=choice_id)
    except (KeyError, Choice.DoesNotExist):
        messages.error(request, "You didn't select a choice.")
        return render(request, 'polls/detail.html', {
            'question': question,
        })
    else:
        # selected_choice.votes += 1
        user = request.user
        vote = get_vote_for_user(question, user)
        if not vote:
            vote = Vote.objects.create(choice=selected_choice, voter=user)
        else:
            vote.choice = selected_choice
        vote.save()
        logger.info(f"{user} voted in {question}.")

        # Always redirect after POST request to prevent multiple
        # requests if user presses back button.
        return redirect('polls:results', question.id)


def get_vote_for_user(question: Question, user: User):
    """Return vote of the user from the question."""
    try:
        return Vote.objects.get(voter=user, choice__question=question)
    except Vote.DoesNotExist:
        return None
