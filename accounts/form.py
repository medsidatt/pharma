import re

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from accounts.models import CustomUser
from django.core.exceptions import ValidationError


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        help_text="Entrez une adresse e-mail valide."
    )

    phone_number = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Le numéro de téléphone doit être au format +222XXXXXXXX."
    )

    address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        help_text="Champ facultatif."
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone_number', 'address', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username.strip():
            raise ValidationError("Le nom d'utilisateur est requis.")
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError("Ce nom d'utilisateur est déjà pris.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email.strip():
            raise ValidationError("L'adresse e-mail est requise.")
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("Cette adresse e-mail est déjà enregistrée.")
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')

        if not phone_number.strip():
            raise ValidationError("Le numéro de téléphone est requis.")

        # Définition des formats de numéros autorisés
        pattern = r"^(?:\+222[234]\d{7}|[234]\d{7})$"

        if not re.match(pattern, phone_number):
            raise ValidationError(
                "Entrez un numéro de téléphone valide"
            )

        return phone_number

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if not password1 or not password2:
            raise ValidationError("Les deux champs de mot de passe sont requis.")
        if password1 != password2:
            raise ValidationError("Les mots de passe ne correspondent pas.")
        return password2




from django.contrib.auth.views import LoginView
from django.shortcuts import redirect

class CustomLoginView(LoginView):
    def get_success_url(self):
        user = self.request.user
        if user.is_superuser:
            return '/dashboard/'
        return '/'


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nom d'utilisateur"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Mot de passe"}))
