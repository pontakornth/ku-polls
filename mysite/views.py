"""Views for entire project."""
from django.contrib.auth import authenticate, login, user_login_failed, user_logged_in, user_logged_out
from django.contrib.auth.forms import UserCreationForm
from django.dispatch import receiver
from django.http import HttpRequest
from django.shortcuts import render, redirect
import logging

logger = logging.getLogger("mysite")


def get_ip_address(request: HttpRequest) -> str:
    """Get the visitor's IP address using request headers.

    If the request is forwarded, takes the first IP address (separated by ,).
    Otherwise, take the whole header as IP address.
    """
    # HTTP_X_FORWARDED_FOR is non-standard request for forwarding ip.
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        # Take the first IP
        ip_address = x_forwarded_for.split(",")[0]
    else:
        ip_address = request.META.get("REMOTE_ADDR")
    return ip_address


@receiver(user_login_failed)
def log_failed_login(sender, request, user, **kwargs):
    """Log failed login attempt."""
    user_ip = get_ip_address(request)
    logger.warning(f"Invalid login for {user.username} from {user_ip}")


@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    """Log normal login."""
    user_ip = get_ip_address(request)
    logger.info(f"{user.username} logged in from {user_ip}")


@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    """Log when user logout."""
    user_ip = get_ip_address(request)
    logger.info(f"{user.username} logged out from {user_ip}.")


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
