from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import Question


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
    return HttpResponse(f"You're looking at the result of {question_id}")


def vote(request, question_id: int):
    """Vote on a question"""
    return HttpResponse(f"You're voting on the question {question_id}")
