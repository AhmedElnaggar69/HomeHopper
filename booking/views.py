# views.py
print("DEBUG: views.py - START LOADING")
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.contrib.auth.models import User
from django.db.models import Q


from .models import Message, Apartment



print("DEBUG: views.py - After initial Django imports")

from .forms import (
    UserLoginForm, UserSignUpForm, OwnerLoginForm, OwnerSignUpForm,
    ApartmentForm, UserProfileForm, OwnerProfileForm, MessageForm
)
print("DEBUG: views.py - After forms import")

from .models import Apartment, UserProfile, OwnerProfile, Message
print("DEBUG: views.py - After models import")

# --- Helper Functions for User Type Checks ---
# --- Helper Functions for User Type Checks ---
def is_owner(user):
    # Check if the user has an owner_profile
    return hasattr(user, 'owner_profile')

def is_user(user):
    # Check if the user has a user_profile and NOT an owner_profile
    # This ensures a user is a 'regular' user if they don't have an owner profile
    return hasattr(user, 'user_profile') and not hasattr(user, 'owner_profile')

# --- Authentication Views ---
def starter_view(request):
    return render(request, 'starter.html')

def user_login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                # IMPORTANT: Check if the user is specifically a 'user' type
                if is_user(user):
                    login(request, user)
                    # Ensure UserProfile exists (though it should from signup)
                    UserProfile.objects.get_or_create(user=user)
                    return redirect('index_user')
                else:
                    form.add_error(None, "Invalid credentials or not a regular user account.")
            else:
                form.add_error(None, "Invalid username or password.")
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form})

def user_signup_view(request):
    if request.method == 'POST':
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Ensure no OwnerProfile exists for this user
            if hasattr(user, 'owner_profile'):
                user.owner_profile.delete() # Or handle this more gracefully if needed
            UserProfile.objects.create(user=user) # Create UserProfile
            login(request, user)
            return redirect('index_user')
        else:
            print(form.errors) # Debug form errors
    else:
        form = UserSignUpForm()
    return render(request, 'signin.html', {'form': form})

def owner_login_view(request):
    if request.method == 'POST':
        form = OwnerLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                # IMPORTANT: Check if the user is specifically an 'owner' type
                if is_owner(user):
                    login(request, user)
                    return redirect('owner_dashboard')
                else:
                    form.add_error(None, "Invalid credentials or not an owner account.")
            else:
                form.add_error(None, "Invalid username or password.")
    else:
        form = OwnerLoginForm()
    return render(request, 'login_owner.html', {'form': form})

def owner_signup_view(request):
    if request.method == 'POST':
        form = OwnerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Ensure no UserProfile exists for this owner
            if hasattr(user, 'user_profile'):
                user.user_profile.delete() # Or handle this more gracefully if needed
            # OwnerProfile is created automatically by the OwnerSignUpForm's save method
            # if it's designed that way, or you'd create it here:
            # OwnerProfile.objects.create(user=user)
            login(request, user)
            return redirect('owner_dashboard')
        else:
            print(form.errors) # Debug form errors
    else:
        form = OwnerSignUpForm()
    return render(request, 'signin_owner.html', {'form': form})

@login_required
def user_logout_view(request):
    logout(request)
    return redirect('starter')

# --- User Dashboard & Apartment Search ---
@login_required
@user_passes_test(is_user, login_url='owner_dashboard') # login_url should redirect to owner dashboard if an owner tries to access user dashboard
def index_user_view(request):
    return render(request, 'index.html')

@login_required
@user_passes_test(is_user, login_url='owner_dashboard') # Ensure only users can see this
def apartment_list_view(request):
    latitude = request.GET.get('lat')
    longitude = request.GET.get('lon')
    all_apart = []

    if latitude and longitude:
        try:
            lat = float(latitude)
            lon = float(longitude)
            all_apart = Apartment.objects.filter(is_available=True)
        except ValueError:
            pass
    else:
        all_apart = Apartment.objects.filter(is_available=True)

    context = {
        'all_apart': all_apart
    }
    return render(request, 'apart_detail.html', context)

# --- Owner Dashboard & Listing Management ---
@login_required
@user_passes_test(is_owner, login_url='index_user') # login_url should redirect to user dashboard if a user tries to access owner dashboard
def owner_dashboard_view(request):
    owner_apartments = Apartment.objects.filter(owner=request.user)
    context = {
        'name': request.user.username,
        'all_apart': owner_apartments,
    }
    return render(request, 'index_owner.html', context)

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_owner, login_url='index_user'), name='dispatch') # Ensure only owners can create
class ApartmentCreateView(CreateView):
    model = Apartment
    form_class = ApartmentForm
    template_name = 'apartment_form.html'
    success_url = reverse_lazy('owner_dashboard')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

print(f"DEBUG: views.py - ApartmentCreateView defined. Type: {type(ApartmentCreateView)}")

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_owner, login_url='index_user'), name='dispatch') # Ensure only owners can update
class ApartmentUpdateView(UpdateView):
    model = Apartment
    form_class = ApartmentForm
    template_name = 'apartment_form.html'
    success_url = reverse_lazy('owner_dashboard')

    def get_queryset(self):
        return self.model.objects.filter(owner=self.request.user)

print(f"DEBUG: views.py - ApartmentUpdateView defined. Type: {type(ApartmentUpdateView)}")

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_owner, login_url='index_user'), name='dispatch') # Ensure only owners can delete
class ApartmentDeleteView(DeleteView):
    model = Apartment
    template_name = 'apartment_confirm_delete.html'
    success_url = reverse_lazy('owner_dashboard')

    def get_queryset(self):
        return self.model.objects.filter(owner=self.request.user)

print(f"DEBUG: views.py - ApartmentDeleteView defined. Type: {type(ApartmentDeleteView)}")

# --- Profile Management Views ---
@login_required
@user_passes_test(is_user, login_url='owner_profile') # Ensure users go to their profile, not owner's
def user_profile_view(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('user_profile')
    else:
        form = UserProfileForm(instance=user_profile)
    return render(request, 'user_profile.html', {'form': form})

@login_required
@user_passes_test(is_owner, login_url='user_profile') # Ensure owners go to their profile, not user's
def owner_profile_view(request):
    owner_profile, created = OwnerProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = OwnerProfileForm(request.POST, instance=owner_profile)
        if form.is_valid():
            form.save()
            return redirect('owner_profile')
    else:
        form = OwnerProfileForm(instance=owner_profile)
    return render(request, 'owner_profile.html', {'form': form})

# --- Chat Views ---
@login_required
def chat_list_view(request):
    # This view is accessible by both user types, so no user_passes_test here
    participants_as_sender = User.objects.filter(received_messages__sender=request.user).distinct()
    participants_as_receiver = User.objects.filter(sent_messages__receiver=request.user).distinct()
    all_participants = (participants_as_sender | participants_as_receiver).distinct()
    chat_partners = [p for p in all_participants if p != request.user]
    context = {
        'chat_partners': chat_partners
    }
    return render(request, 'chat_list.html', context)


@login_required
def chat_detail_view(request, participant_id):
    participant = get_object_or_404(User, id=participant_id)
    messages = Message.objects.filter(
        (Q(sender=request.user, receiver=participant) | Q(sender=participant, receiver=request.user))
    ).order_by('timestamp')

       # Generate room name based on sorted user IDs
    user_ids = sorted([request.user.id, participant.id])
    room_name = f"chat_{user_ids[0]}_{user_ids[1]}"

    context = {
        'participant': participant,
        'messages': messages,
        'room_name': room_name,  # Pass room_name to template
        'current_user_id': request.user.id,
        'participant_id': participant.id,
    }
    return render(request, 'chat_detail.html', context)
   
@login_required
def initiate_chat_from_apartment(request, apartment_id):
    apartment = get_object_or_404(Apartment, id=apartment_id)
    owner = apartment.owner
    if request.user == owner:
        return redirect('chat_list')

    # Determine the room name
    user_ids = sorted([request.user.id, owner.id])
    room_name = f"chat_{user_ids[0]}_{user_ids[1]}"

    return redirect('chat_detail', participant_id=owner.id)
