"""Views for entire project."""
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect


def signup(request):
    """Register a user.

    If the form is submitted using POST method, it register the user.
    Otherwise, it renders signup form.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('polls')
        else:
            return render(request, "registration/signup.html", {"form": form})
    form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})
