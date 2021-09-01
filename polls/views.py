from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Question, Choice


# Create your views here.
def index(request):
    """Display available questions"""
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {
        'latest_question_list': latest_question_list
    }
    return render(request, 'polls/index.html', context=context)


def detail(request, question_id: int):
    """Display detail of the question"""
    question = get_object_or_404(Question, pk=question_id)
    context = {
        'question': question
    }
    return render(request, 'polls/detail.html', context)


def results(request, question_id: int):
    """Display the result of the question"""
    question = get_object_or_404(Question, pk=question_id)
    context = {
        'question': question
    }
    return render(request, 'polls/results.html', context)


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
