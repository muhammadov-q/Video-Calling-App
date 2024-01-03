from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_str, force_bytes
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from .forms import RegisterForm


def index(request):
    return render(request, 'index.html')


def page_Not_Found(request):
    previous_url = request.META.get('HTTP_REFERER', '/')
    return render(request, '404.html', {'previous_url': previous_url})


user = get_user_model()


def password_reset(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email=email).first()

            if user:
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)

                current_site = request.get_host()

                subject = 'Password Reset'
                context = {
                    'user': user,
                    'protocol': request.scheme,
                    'domain': current_site,
                    'uid': uid,
                    'token': token,
                    'timeout': 24,
                }

                html_message = render_to_string('password_reset_email.html', context)
                text_message = strip_tags(html_message)

                email = EmailMultiAlternatives(subject, text_message, to=[user.email])
                email.attach_alternative(html_message, "text/html")
                email.send()

                success_message = 'Password reset email sent. Check your inbox. Redirecting login page in 5 secs!'
                return render(request, 'password_reset.html', {'form': form, 'success_message': success_message})

            else:
                error = 'Email not found. Please try again!'
                return render(request, 'password_reset.html', {'form': form, 'error': error})

    else:
        form = PasswordResetForm()

    return render(request, 'password_reset.html', {'form': form})


def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    form = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Password reset successfully. You can now log in with your new password.')
                return render(request, 'password_reset_success.html')
        else:
            form = SetPasswordForm(user)

        return render(request, 'password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, 'Invalid password reset link.')
        return render(request, 'password_reset_confirm.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate until email is confirmed
            user.save()

            current_site = get_current_site(request)
            subject = 'Activate Your Account'
            message = render_to_string('activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(str(user.pk).encode()),
                'token': default_token_generator.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(subject, message, to=[to_email])
            email.send()

            return render(request, 'login.html',
                          {'success': "Registration successful. Please check your email to activate your account."})
        else:
            error_message = form.errors.as_text()
            return render(request, 'register.html', {'error': error_message})

    return render(request, 'register.html')


def confirm_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'confirmation_success.html')
    else:
        return HttpResponse('Activation link is invalid!')


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect("/dashboard")
        else:
            return render(request, 'login.html', {'error': "Invalid credentials. Please try again."})

    return render(request, 'login.html')


@login_required
def dashboard(request):
    return render(request, 'dashboard.html', {'name': request.user.first_name, 'last': request.user.last_name})


@login_required
def videocall(request):
    return render(request, 'videocall.html', {'name': request.user.first_name + " " + request.user.last_name})


@login_required
def join_room(request):
    if request.method == 'POST':
        roomID = request.POST['roomID']
        return redirect(roomID)
    return render(request, 'joinroom.html')
