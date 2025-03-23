from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth import logout
from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render, redirect
from accounts.form import CustomUserCreationForm, CustomLoginView, CustomLoginForm
from utils.app import is_not_authenticated

@user_passes_test(is_not_authenticated)
# Assuming you have this form defined

def login_view(request):
    """Vue de connexion personnalisée avec redirection basée sur le rôle de l'utilisateur"""
    if request.method == "POST":
        form = CustomLoginForm(request, data=request.POST)  # Pass request for CSRF validation
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, "Connexion réussie !")

                # Handle the 'next' parameter
                next_url = request.POST.get('next', request.GET.get('next', '/'))
                return redirect(next_url)  # Redirect to 'next' URL or '/' if not provided
            else:
                messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = CustomLoginForm()

    return render(request, "registration/login.html", {"form": form})
@user_passes_test(is_not_authenticated)
def register_view(request):
    """Vue d'inscription personnalisée avec redirection"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Inscription réussie !")

            # Handle the 'next' parameter
            next_url = request.POST.get('next', request.GET.get('next', '/'))
            return redirect(next_url)  # Redirect to 'next' URL or '/' if not provided
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})
@login_required
def logout_view(request):
    logout(request)
    return redirect('/')

@login_required
def home_view(request):
    """Redirect to the appropriate dashboard based on user role"""
    if request.user.is_superuser:
        return render(request, "dashboard.html")  # Admin dashboard
    return render(request, "customer_page.html")
