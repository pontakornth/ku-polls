from django.http import HttpResponse
from django.shortcuts import render


# Create your views here.
def index(request):
    """Display available questions"""
    return render(request, 'index.html')


def detail(request, question_id: int):
    """Display detail of the question"""
    return HttpResponse(f"You're looking at question {question_id}")


def results(request, question_id: int):
    """Display the result of the question"""
    return HttpResponse(f"You're looking at the result of {question_id}")


def vote(request, question_id: int):
    """Vote on a question"""
    return HttpResponse(f"You're voting on the question {question_id}")
