"""Views for poll application."""
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from .models import Question, Choice
from django.views import generic


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


def vote(request, question_id: int):
    """Vote on a question."""
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        messages.add_message(request, messages.ERROR, "You didn't select a choice.")
        return render(request, 'polls/detail.html', {
            'question': question,
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()

        # Always redirect after POST request to prevent multiple
        # requests if user presses back button.
        return redirect('polls:results', question.id)
