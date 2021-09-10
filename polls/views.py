from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Question, Choice
from django.views import generic


# Create your views here.
class IndexView(generic.ListView):
    """Display latest questions"""
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return all available questions"""
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')


class DetailView(generic.DetailView):
    """Question detail page"""
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """Exclude unpublished questions"""
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    """Question result page"""
    model = Question
    template_name = 'polls/results.html'


def vote(request, question_id: int):
    """Vote on a question"""
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice."
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()

        # Always redirect after POST request to prevent multiple
        # requests if user presses back button.
        return redirect('polls:results', question.id)
