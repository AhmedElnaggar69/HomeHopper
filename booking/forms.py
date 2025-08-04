# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Apartment, UserProfile, OwnerProfile, Message

# --- Authentication Forms ---
class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input'}))

class UserSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'form-input'

class OwnerLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input'}))

class OwnerSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-input'}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'form-input'

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            OwnerProfile.objects.create(user=user)
        return user

# --- Apartment Form ---
class ApartmentForm(forms.ModelForm):
    class Meta:
        model = Apartment
        fields = ['title', 'description', 'price', 'latitude', 'longitude', 'is_available']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-input'}),
            'latitude': forms.HiddenInput(attrs={'id': 'id_latitude'}),
            'longitude': forms.HiddenInput(attrs={'id': 'id_longitude'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        latitude = cleaned_data.get('latitude')
        longitude = cleaned_data.get('longitude')
        if latitude is None or longitude is None:
            raise forms.ValidationError("Please set a location on the map.")
        return cleaned_data

# --- Profile Forms ---
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'address']
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-input'}),
            'address': forms.TextInput(attrs={'class': 'form-input'}),
        }

class OwnerProfileForm(forms.ModelForm):
    class Meta:
        model = OwnerProfile
        fields = ['company_name']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-input'}),
        }

# --- Message Form ---
class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Type your message...'}),
        }