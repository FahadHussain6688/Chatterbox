from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from chat.models import Chat
from users.models import Status, Profile
from django.utils import timezone
from datetime import timedelta
from users.forms import StatusForm, SignupForm, ProfileForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from .utils.bio_client import BioGenerator
import json
from collections import defaultdict
from django.db.models import Exists, OuterRef

# ===== AUTHENTICATION VIEWS =====
def login_signup_view(request):
    login_form = AuthenticationForm(request, data=request.POST or None)
    signup_form = SignupForm(request.POST or None)
    login_error = signup_error = None

    if request.method == 'POST':
        if 'login' in request.POST:
            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                return redirect('dashboard')
            else:
                login_error = 'Invalid login credentials.'
        elif 'signup' in request.POST:
            if signup_form.is_valid():
                user = signup_form.save(commit=False)
                user.set_password(signup_form.cleaned_data['password'])
                user.save()
                Profile.objects.create(user=user)
                return redirect('login_signup')
            else:
                signup_error = 'Signup failed. Please check the form.'

    return render(request, 'users/login_signup.html', {
        'login_form': login_form,
        'signup_form': signup_form,
        'login_error': login_error,
        'signup_error': signup_error,
    })

def signup_view(request):
    signup_form = SignupForm(request.POST or None)
    signup_error = None
    if request.method == 'POST':
        if signup_form.is_valid():
            user = signup_form.save(commit=False)
            user.set_password(signup_form.cleaned_data['password'])
            user.save()
            Profile.objects.create(user=user)
            user = authenticate(username=signup_form.cleaned_data['username'], 
                              password=signup_form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                signup_error = 'Signup succeeded but automatic login failed. Please log in manually.'
        else:
            signup_error = 'Signup failed. Please check the form.'
    return render(request, 'users/signup.html', {
        'signup_form': signup_form,
        'signup_error': signup_error,
    })

# ===== DASHBOARD SECTION VIEWS =====
@login_required
def dashboard(request):
    """Main dashboard view with dynamic section support (chat, profile, status)"""
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)

    # Clean up expired statuses (older than 24 hours)
    Status.objects.filter(timestamp__lt=timezone.now() - timedelta(hours=24)).delete()

    # Determine active section
    active_section = request.GET.get('section', 'chat')

    # Fetch common context data
    chats = Chat.objects.filter(participants=user).distinct().prefetch_related('participants')
    all_users = User.objects.exclude(id=user.id)
    form = ProfileForm(instance=profile)
    statuses = Status.objects.filter(user=user).order_by('-timestamp')
    active_users_with_status = User.objects.exclude(id=user.id).filter(status__isnull=False).distinct()

    # Final context
    context = {
        'user': user,
        'profile': profile,
        'form': form,
        'chats': chats,
        'statuses': statuses,
        'all_users': all_users,
        'active_users_with_statuses': active_users_with_status,
        'active_section': active_section,
    }

    return render(request, 'users/dashboard.html', context)

@login_required
def profile_section(request):
    """Dedicated profile section view"""
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)
    
    context = {
        'user': user,
        'profile': profile,
        'chats': Chat.objects.filter(participants=user),
        'active_section': 'profile'
    }
    return render(request, 'users/dashboard.html', context)

@login_required
def status_section(request):
    """Dedicated status section view"""
    user = request.user
    
    # Status data
    statuses = Status.objects.filter(
        user=user,
        timestamp__gte=timezone.now() - timedelta(hours=24)
    ).order_by('-timestamp')
    
    active_users_with_statuses = User.objects.filter(
        status__timestamp__gte=timezone.now() - timedelta(hours=24)
    ).exclude(id=user.id).distinct().select_related('profile')
    
    context = {
        'user': user,
        'statuses': statuses,
        'active_users_with_statuses': active_users_with_statuses,
        'chats': Chat.objects.filter(participants=user),
        'active_section': 'status'
    }
    return render(request, 'users/dashboard.html', context)

# ===== STATUS MANAGEMENT VIEWS =====
@login_required
def upload_status(request):
    if request.method == 'POST':
        form = StatusForm(request.POST, request.FILES)
        if form.is_valid():
            status = form.save(commit=False)
            status.user = request.user
            status.save()
            return redirect('status')
    else:
        form = StatusForm()
    return render(request, 'users/upload_status.html', {'form': form})

@login_required
def get_active_statuses(request):
    time_threshold = timezone.now() - timedelta(hours=24)
    statuses = Status.objects.filter(timestamp__gte=time_threshold).exclude(user=request.user).select_related('user')

    grouped = defaultdict(list)
    for status in statuses:
        grouped[status.user.username].append(status.image.url)

    data = [{'user': user, 'images': urls} for user, urls in grouped.items()]
    return JsonResponse(data, safe=False)

@login_required
def delete_status(request, status_id):
    status = get_object_or_404(Status, id=status_id, user=request.user)
    if request.method == 'POST':
        status.delete()
    return redirect('status')

@login_required
def user_status_modal(request, username):
    time_threshold = timezone.now() - timedelta(hours=24)
    statuses = Status.objects.filter(
        user__username=username,
        timestamp__gte=time_threshold
    ).order_by('timestamp')

    return render(request, 'users/status_modal.html', {
        'statuses': statuses,
        'username': username
    })

# ===== PROFILE MANAGEMENT VIEWS =====
@login_required
def update_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile_view')
    else:
        form = ProfileForm(instance=profile)
    
    return render(request, 'users/edit_profile.html', {
        'form': form,
        'profile': profile
    })

@login_required
def generate_bio(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name', '')
            age = data.get('age', '')
            hobbies = data.get('hobbies', '')
            profession = data.get('profession', '')

            bio = BioGenerator.generate_from_fastapi(name, age, hobbies, profession)

            profile = Profile.objects.get(user=request.user)
            profile.bio = bio
            profile.save()

            return JsonResponse({'bio': bio})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
def update_profile_bio(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            bio = data.get('bio', '')
            profile, _ = Profile.objects.get_or_create(user=request.user)
            profile.bio = bio
            profile.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)