from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from .models import DonorProfile, BloodRequest, BLOOD_GROUPS
def home_view(request):
    return render(request, 'donors/home.html')
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        blood_group = request.POST.get('blood_group')
        city = request.POST.get('city')
        locality = request.POST.get('locality')
        phone = request.POST.get('phone')

        errors = []

        if not username or not email or not password or not blood_group or not city or not phone:
            errors.append('All fields are required.')
        
        if password != password2:
            errors.append('Passwords do not match.')

        if User.objects.filter(username=username).exists():
            errors.append('Username already taken.')

        if User.objects.filter(email=email).exists():
            errors.append('Email already registered.')

        if errors:
            return render(request, 'donors/register.html', {
                'errors': errors,
                'blood_groups': BLOOD_GROUPS,
                'form_data': request.POST
            })

        user = User.objects.create_user(username=username, email=email, password=password)
        DonorProfile.objects.create(
            user=user,
            blood_group=blood_group,
            city=city,
            locality=locality,
            phone=phone,
            is_available=True
        )

        login(request, user)
        messages.success(request, 'Account created successfully!')
        return redirect('dashboard')

    return render(request, 'donors/register.html', {
        'blood_groups': BLOOD_GROUPS
    })
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Logged in successfully!')
            return redirect('dashboard')
        else:
            return render(request, 'donors/login.html', {
                'error': 'Invalid username or password.',
                'form_username': username
            })

    return render(request, 'donors/login.html')
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')
@login_required
def dashboard_view(request):
    profile = DonorProfile.objects.filter(user=request.user).first()
    my_requests = BloodRequest.objects.filter(requester=request.user).order_by('-created_at')

    context = {
        'profile': profile,
        'my_requests': my_requests,
        'my_requests_count': my_requests.count(),
        'pending_count': my_requests.filter(status='Pending').count(),
        'fulfilled_count': my_requests.filter(status='Fulfilled').count(),
    }
    return render(request, 'donors/dashboard.html', context)

@login_required
def profile_view(request):
    profile = get_object_or_404(DonorProfile, user=request.user)

    if request.method == 'POST':
        profile.blood_group = request.POST.get('blood_group')
        profile.city = request.POST.get('city')
        profile.locality = request.POST.get('locality')
        profile.phone = request.POST.get('phone')
        profile.is_available = (request.POST.get('is_available') == 'on')
        profile.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('dashboard')

    return render(request, 'donors/profile.html', {
        'profile': profile,
        'blood_groups': BLOOD_GROUPS
    })
def find_donors_view(request):
    blood_group = request.GET.get('blood_group', '').strip()
    city = request.GET.get('city', '').strip()
    locality = request.GET.get('locality', '').strip()
    available_only = request.GET.get('available_only', '1')

    donors = DonorProfile.objects.all()

    if blood_group:
        donors = donors.filter(blood_group=blood_group)
    if city:
        donors = donors.filter(city__icontains=city)
    if locality:
        donors = donors.filter(locality__icontains=locality)
    if available_only == '1':
        donors = donors.filter(is_available=True)

    paginator = Paginator(donors, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    searched = bool(blood_group or city or locality)

    return render(request, 'donors/find_donors.html', {
        'donors': page_obj,
        'blood_groups': BLOOD_GROUPS,
        'selected_blood_group': blood_group,
        'selected_city': city,
        'selected_locality': locality,
        'selected_available': available_only,
        'searched': searched,
    })
@login_required
def create_request_view(request):
    if request.method == 'POST':
        blood_group = request.POST.get('blood_group')
        hospital = request.POST.get('hospital')
        city = request.POST.get('city')
        units_needed = request.POST.get('units_needed', 1)
        urgency = request.POST.get('urgency', 'Normal')

        errors = []
        if not blood_group or not hospital or not city:
            errors.append('Please fill all required fields.')

        if errors:
            return render(request, 'donors/create_request.html', {
                'errors': errors,
                'blood_groups': BLOOD_GROUPS,
                'form_data': request.POST
            })

        req = BloodRequest.objects.create(
            requester=request.user,
            blood_group=blood_group,
            hospital=hospital,
            city=city,
            units_needed=units_needed,
            urgency=urgency,
            status='Pending'
        )
        messages.success(request, 'Blood request created successfully!')
        return redirect('request_detail', pk=req.pk)

    return render(request, 'donors/create_request.html', {
        'blood_groups': BLOOD_GROUPS
    })
def request_list_view(request):
    blood_group = request.GET.get('blood_group', '').strip()
    city = request.GET.get('city', '').strip()
    urgency = request.GET.get('urgency', '').strip()
    status = request.GET.get('status', 'Pending').strip()

    requests_list = BloodRequest.objects.all().order_by('-created_at')

    if blood_group:
        requests_list = requests_list.filter(blood_group=blood_group)
    if city:
        requests_list = requests_list.filter(city__icontains=city)
    if urgency:
        requests_list = requests_list.filter(urgency=urgency)
    if status:
        requests_list = requests_list.filter(status=status)

    paginator = Paginator(requests_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'donors/request_list.html', {
        'requests': page_obj,
        'blood_groups': BLOOD_GROUPS,
        'selected_blood_group': blood_group,
        'selected_city': city,
        'selected_urgency': urgency,
        'selected_status': status,
    })
def request_detail_view(request, pk):
    blood_request = get_object_or_404(BloodRequest, pk=pk)
    is_owner = (request.user == blood_request.requester)

    return render(request, 'donors/request_detail.html', {
        'blood_request': blood_request,
        'is_owner': is_owner,
    })
@login_required
def update_request_status_view(request, pk):
    blood_request = get_object_or_404(BloodRequest, pk=pk)

    if request.method == 'POST' and blood_request.requester == request.user:
        new_status = request.POST.get('status')
        if new_status:
            blood_request.status = new_status
            blood_request.save()
            messages.success(request, 'Status updated successfully!')

    return redirect('request_detail', pk=pk)
