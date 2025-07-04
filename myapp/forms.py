from django import forms
from django.contrib.auth.hashers import make_password
from .models import Player
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User



class PlayerRegistrationForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, min_length=4, label="Password")
    password_confirm = forms.CharField(widget=forms.PasswordInput, min_length=4, label="Confirm Password")

    class Meta:
        model = Player
        exclude = ['user']

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password') != cleaned_data.get('password_confirm'):
            self.add_error('password_confirm', "Passwords do not match.")
        return cleaned_data

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age < 13:
            raise forms.ValidationError("Minimum age required is 13.")
        return age

    User = get_user_model()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        player = super().save(commit=False)
        # Hash the password before saving
        player.password = make_password(self.cleaned_data["password"])
        # Do NOT save password_confirm in the model
        player.password_confirm = ''
        if commit:
            player.save()
        return player
    
class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email", max_length=254)

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(self.request, username=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError("Invalid email or password.")
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

