from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from .forms import RegisterForm
from django.contrib.auth.models import User
from django.http import HttpResponse


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
    return render(request, 'dashboard.html', {'name': request.user.first_name})
