from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.contrib import messages
from .models import TourismEvent, TourismLocation, TourismCategory, TourismPackage, TourismReview, TourismRating

# Placeholder functions for other views defined in urls.py
def tourism_dashboard(request):
    """View for tourism dashboard"""
    # Get statistics for dashboard
    total_locations = TourismLocation.objects.count()
    total_categories = TourismCategory.objects.count()
    featured_locations = TourismLocation.objects.filter(featured=True, is_active=True)[:3]
    recent_locations = TourismLocation.objects.filter(is_active=True).order_by('-created_at')[:5]
    
    # Get upcoming events (events with start_date >= today)
    from datetime import date
    today = date.today()
    upcoming_events = TourismEvent.objects.filter(
        is_active=True,
        start_date__gte=today
    ).order_by('start_date')[:5]
    
    # Get categories for dashboard
    categories = TourismCategory.objects.all()[:8]
    
    context = {
        'total_locations': total_locations,
        'total_categories': total_categories,
        'featured_locations': featured_locations,
        'recent_locations': recent_locations,
        'upcoming_events': upcoming_events,
        'categories': categories,
    }
    
    return render(request, 'admin/modules/tourism/admin_dashboard.html', context)

def tourism_list(request):
    """View for listing tourism locations"""
    locations = TourismLocation.objects.filter(is_active=True).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(locations, 12)  # Show 12 locations per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get categories for filtering
    categories = TourismCategory.objects.filter(is_active=True)
    
    context = {
        'locations': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'location_types': TourismLocation.LOCATION_TYPE_CHOICES,
    }
    
    return render(request, 'admin/modules/tourism/location_list.html', context)

def tourism_detail(request, slug):
    """View for tourism location detail"""
    location = get_object_or_404(TourismLocation, slug=slug, is_active=True)
    
    # Get gallery images
    gallery_images = location.gallery.filter(is_active=True, media_type='image')
    
    # Get related locations (same category)
    related_locations = TourismLocation.objects.filter(
        category=location.category,
        is_active=True
    ).exclude(id=location.id)[:3]
    
    # Get upcoming events at this location
    from datetime import date
    today = date.today()
    upcoming_events = location.events.filter(
        is_active=True,
        start_date__gte=today
    ).order_by('start_date')[:3]
    
    context = {
        'location': location,
        'gallery_images': gallery_images,
        'related_locations': related_locations,
        'upcoming_events': upcoming_events,
    }
    
    return render(request, 'admin/modules/tourism/location_detail.html', context)

def category_list(request):
    """View for listing tourism categories"""
    categories = TourismCategory.objects.filter(is_active=True).order_by('name')
    
    context = {
        'categories': categories,
    }
    
    return render(request, 'admin/modules/tourism/category_list.html', context)

def category_detail(request, category_id):
    """View for category detail and its locations"""
    category = get_object_or_404(TourismCategory, id=category_id, is_active=True)
    
    # Get locations in this category
    locations = TourismLocation.objects.filter(
        category=category,
        is_active=True
    ).order_by('-featured', '-created_at')
    
    # Pagination
    paginator = Paginator(locations, 12)  # Show 12 locations per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'locations': page_obj,
        'page_obj': page_obj,
    }
    
    return render(request, 'admin/modules/tourism/category_detail.html', context)

def event_list(request):
    """View for listing events"""
    events = TourismEvent.objects.filter(is_active=True).order_by('-start_date')
    
    # Pagination
    paginator = Paginator(events, 12)  # Show 12 events per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'events': page_obj,
        'page_obj': page_obj,
    }
    
    return render(request, 'public/event_list.html', context)

def event_detail(request, event_id):
    """View for event detail"""
    event = get_object_or_404(TourismEvent, id=event_id)
    
    # Get related events (same location or same event type)
    related_events = TourismEvent.objects.filter(
        is_active=True
    ).exclude(id=event.id)
    
    if event.tourism_location:
        related_events = related_events.filter(tourism_location=event.tourism_location)[:4]
    else:
        related_events = related_events.filter(event_type=event.event_type)[:4]
    
    context = {
        'event': event,
        'related_events': related_events,
    }
    
    return render(request, 'public/event_detail.html', context)

def package_list(request):
    """View for listing tourism packages"""
    from django.db.models import Min
    
    packages = TourismPackage.objects.filter(is_active=True).order_by('-is_featured', 'price')
    
    # Filter by location if provided
    location_id = request.GET.get('location')
    if location_id:
        packages = packages.filter(tourism_location_id=location_id)
    
    # Get locations for filtering
    locations = TourismLocation.objects.filter(is_active=True, packages__isnull=False).distinct()
    
    # Pagination
    paginator = Paginator(packages, 12)  # Show 12 packages per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'packages': page_obj,
        'page_obj': page_obj,
        'locations': locations,
        'selected_location': location_id,
    }
    
    return render(request, 'admin/modules/tourism/package_list.html', context)

def package_detail(request, package_id):
    """View for package detail"""
    package = get_object_or_404(TourismPackage, id=package_id, is_active=True)
    
    # Get related packages (same location or similar price range)
    related_packages = TourismPackage.objects.filter(
        is_active=True
    ).exclude(id=package.id)
    
    # First try to get packages from same location
    if package.tourism_location:
        location_packages = related_packages.filter(tourism_location=package.tourism_location)[:3]
        if location_packages.exists():
            related_packages = location_packages
        else:
            # If no packages from same location, get packages with similar price
            from decimal import Decimal
            price_min = package.price * Decimal('0.7')  # 30% less
            price_max = package.price * Decimal('1.3')  # 30% more
            related_packages = related_packages.filter(price__gte=price_min, price__lte=price_max)[:3]
    
    context = {
        'package': package,
        'related_packages': related_packages,
    }
    
    return render(request, 'public/package_detail.html', context)

def search_tourism(request):
    """View for searching tourism locations"""
    from django.db.models import Q
    
    # Get search parameters
    query = request.GET.get('q', '')
    category_id = request.GET.get('category')
    location_type = request.GET.get('type')
    min_rating = request.GET.get('rating')
    
    # Start with all active locations
    locations = TourismLocation.objects.filter(is_active=True)
    
    # Apply filters
    if query:
        locations = locations.filter(
            Q(title__icontains=query) |
            Q(short_description__icontains=query) |
            Q(full_description__icontains=query) |
            Q(address__icontains=query)
        )
    
    if category_id:
        locations = locations.filter(category_id=category_id)
    
    if location_type:
        locations = locations.filter(location_type=location_type)
    
    if min_rating:
        # This is a simplified approach - in a real app you might want to use annotations
        # to filter by average rating more efficiently
        min_rating = int(min_rating)
        filtered_locations = []
        for location in locations:
            if location.average_rating >= min_rating:
                filtered_locations.append(location.id)
        locations = locations.filter(id__in=filtered_locations)
    
    # Order results
    locations = locations.order_by('-featured', '-created_at')
    
    # Pagination
    paginator = Paginator(locations, 12)  # Show 12 locations per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get categories and location types for filtering
    categories = TourismCategory.objects.filter(is_active=True)
    
    context = {
        'locations': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'location_types': TourismLocation.LOCATION_TYPE_CHOICES,
        'search_params': {
            'q': query,
            'category': category_id,
            'type': location_type,
            'rating': min_rating,
        }
    }
    
    return render(request, 'admin/modules/tourism/search_results.html', context)

def submit_review(request, location_id):
    """View for submitting a review for a tourism location"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)
    
    location = get_object_or_404(TourismLocation, id=location_id, is_active=True)
    
    # Get form data
    title = request.POST.get('title')
    comment = request.POST.get('comment')
    rating = request.POST.get('rating')
    visit_date = request.POST.get('visit_date')
    visit_type = request.POST.get('visit_type')
    
    # Validate required fields
    if not all([title, comment, rating]):
        return JsonResponse({'status': 'error', 'message': 'Missing required fields'}, status=400)
    
    try:
        rating = int(rating)
        if not (1 <= rating <= 5):
            raise ValueError('Rating must be between 1 and 5')
    except ValueError:
        return JsonResponse({'status': 'error', 'message': 'Invalid rating value'}, status=400)
    
    # Check if user already reviewed this location
    existing_review = location.reviews.filter(user=request.user).first()
    if existing_review:
        # Update existing review
        existing_review.title = title
        existing_review.comment = comment
        existing_review.rating = rating
        if visit_date:
            existing_review.visit_date = visit_date
        if visit_type:
            existing_review.visit_type = visit_type
        existing_review.save()
        message = 'Review updated successfully'
    else:
        # Create new review
        review_data = {
            'tourism_location': location,
            'user': request.user,
            'title': title,
            'comment': comment,
            'rating': rating,
        }
        if visit_date:
            review_data['visit_date'] = visit_date
        if visit_type:
            review_data['visit_type'] = visit_type
        
        from .models import TourismReview
        review = TourismReview.objects.create(**review_data)
        message = 'Review submitted successfully'
    
    return JsonResponse({'status': 'success', 'message': message})

def submit_rating(request, location_id):
    """View for submitting a rating for a tourism location"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)
    
    location = get_object_or_404(TourismLocation, id=location_id, is_active=True)
    
    # Get form data
    rating = request.POST.get('rating')
    cleanliness = request.POST.get('cleanliness')
    accessibility = request.POST.get('accessibility')
    facilities = request.POST.get('facilities')
    service = request.POST.get('service')
    value = request.POST.get('value')
    
    # Validate required fields
    if not rating:
        return JsonResponse({'status': 'error', 'message': 'Rating is required'}, status=400)
    
    try:
        rating = int(rating)
        if not (1 <= rating <= 5):
            raise ValueError('Rating must be between 1 and 5')
        
        # Convert optional ratings if provided
        if cleanliness:
            cleanliness = int(cleanliness)
        if accessibility:
            accessibility = int(accessibility)
        if facilities:
            facilities = int(facilities)
        if service:
            service = int(service)
        if value:
            value = int(value)
    except ValueError:
        return JsonResponse({'status': 'error', 'message': 'Invalid rating value'}, status=400)
    
    # Check if user already rated this location
    from .models import TourismRating
    existing_rating = TourismRating.objects.filter(tourism_location=location, user=request.user).first()
    
    if existing_rating:
        # Update existing rating
        existing_rating.rating = rating
        if cleanliness:
            existing_rating.cleanliness = cleanliness
        if accessibility:
            existing_rating.accessibility = accessibility
        if facilities:
            existing_rating.facilities = facilities
        if service:
            existing_rating.service = service
        if value:
            existing_rating.value = value
        existing_rating.save()
        message = 'Rating updated successfully'
    else:
        # Create new rating
        rating_data = {
            'tourism_location': location,
            'user': request.user,
            'rating': rating,
        }
        if cleanliness:
            rating_data['cleanliness'] = cleanliness
        if accessibility:
            rating_data['accessibility'] = accessibility
        if facilities:
            rating_data['facilities'] = facilities
        if service:
            rating_data['service'] = service
        if value:
            rating_data['value'] = value
        
        TourismRating.objects.create(**rating_data)
        message = 'Rating submitted successfully'
    
    return JsonResponse({'status': 'success', 'message': message})

# Admin views
@login_required
def admin_dashboard(request):
    """Admin dashboard for tourism module"""
    # Get statistics for dashboard
    total_locations = TourismLocation.objects.count()
    total_categories = TourismCategory.objects.count()
    total_events = TourismEvent.objects.count()
    total_packages = TourismPackage.objects.count()
    
    # Get recent locations
    recent_locations = TourismLocation.objects.order_by('-created_at')[:5]
    
    # Get featured locations
    featured_locations = TourismLocation.objects.filter(featured=True)[:6]
    
    # Get categories
    categories = TourismCategory.objects.filter(is_active=True)[:8]
    
    # Get upcoming events
    from datetime import date
    today = date.today()
    upcoming_events = TourismEvent.objects.filter(
        start_date__gte=today
    ).order_by('start_date')[:5]
    
    context = {
        'total_locations': total_locations,
        'total_categories': total_categories,
        'total_events': total_events,
        'total_packages': total_packages,
        'recent_locations': recent_locations,
        'featured_locations': featured_locations,
        'categories': categories,
        'upcoming_events': upcoming_events,
    }
    
    return render(request, 'admin/modules/tourism/admin_dashboard.html', context)

@login_required
def admin_location_list(request):
    """Admin view for listing tourism locations"""
    locations = TourismLocation.objects.all().order_by('-created_at')
    
    # Filter by category if provided
    category_id = request.GET.get('category')
    if category_id:
        locations = locations.filter(category_id=category_id)
    
    # Filter by status if provided
    status = request.GET.get('status')
    if status:
        is_active = status == 'active'
        locations = locations.filter(is_active=is_active)
    
    # Pagination
    paginator = Paginator(locations, 10)  # Show 10 locations per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get categories for filtering
    categories = TourismCategory.objects.all()
    
    context = {
        'locations': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': category_id,
        'selected_status': status,
    }
    
    return render(request, 'admin/modules/tourism/admin_location_list.html', context)

@login_required
def admin_package_list(request):
    """Admin view for listing tourism packages"""
    packages = TourismPackage.objects.all().order_by('-created_at')
    
    # Filter by location if provided
    location_id = request.GET.get('location')
    if location_id:
        packages = packages.filter(tourism_location_id=location_id)
    
    # Filter by status if provided
    status = request.GET.get('status')
    if status:
        is_active = status == 'active'
        packages = packages.filter(is_active=is_active)
    
    # Pagination
    paginator = Paginator(packages, 10)  # Show 10 packages per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get locations for filtering
    locations = TourismLocation.objects.all()
    
    context = {
        'packages': page_obj,
        'page_obj': page_obj,
        'locations': locations,
        'selected_location': location_id,
        'selected_status': status,
    }
    
    return render(request, 'admin/modules/tourism/admin_package_list.html', context)

@login_required
def admin_location_detail(request, location_id):
    """View for admin location detail"""
    location = get_object_or_404(TourismLocation, id=location_id)
    
    # Get related tourism packages
    related_packages = TourismPackage.objects.filter(tourism_location=location).order_by('-created_at')
    
    context = {
        'location': location,
        'related_packages': related_packages,
    }
    
    return render(request, 'admin/modules/tourism/admin_location_detail_standalone.html', context)

@login_required
def admin_location_create(request):
    """Admin view for creating a new tourism location"""
    if request.method == 'POST':
        # Process form data
        title = request.POST.get('title')
        slug = request.POST.get('slug')
        category_id = request.POST.get('category')
        location_type = request.POST.get('location_type')
        short_description = request.POST.get('short_description')
        full_description = request.POST.get('full_description')
        address = request.POST.get('address')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        featured = request.POST.get('featured') == 'on'
        is_active = request.POST.get('is_active') == 'on'
        
        # Validate required fields
        if not all([title, category_id, location_type, short_description, address]):
            messages.error(request, 'Ada beberapa field yang wajib diisi')
            # Get categories for form
            categories = TourismCategory.objects.filter(is_active=True)
            
            context = {
                'title': 'Tambah Lokasi Wisata',
                'subtitle': 'Buat lokasi wisata baru di desa Pulo Sarok',
                'categories': categories,
                'location_types': TourismLocation.LOCATION_TYPE_CHOICES,
            }
            
            return render(request, 'admin/modules/tourism/admin_location_form_unified.html', context)
        
        # Create location
        location = TourismLocation(
            title=title,
            slug=slug or None,  # Will be auto-generated if None
            category_id=category_id,
            location_type=location_type,
            short_description=short_description,
            full_description=full_description,
            address=address,
            latitude=latitude,
            longitude=longitude,
            featured=featured,
            is_active=is_active,
            created_by=request.user,
        )
        location.save()
        
        # Handle main image if provided
        if 'main_image' in request.FILES:
            location.main_image = request.FILES['main_image']
            location.save()
        
        messages.success(request, f'Lokasi wisata "{title}" berhasil dibuat')
        return redirect('tourism:admin_location_edit', location_id=location.id)
    
    # Get categories for form
    categories = TourismCategory.objects.filter(is_active=True)
    
    context = {
        'title': 'Tambah Lokasi Wisata',
        'subtitle': 'Buat lokasi wisata baru di desa Pulo Sarok',
        'categories': categories,
        'location_types': TourismLocation.LOCATION_TYPE_CHOICES,
    }
    
    return render(request, 'admin/modules/tourism/admin_location_form_unified.html', context)

@login_required
def admin_location_edit(request, location_id):
    """Admin view for editing a tourism location"""
    location = get_object_or_404(TourismLocation, id=location_id)
    
    if request.method == 'POST':
        # Process form data
        location.title = request.POST.get('title')
        location.slug = request.POST.get('slug') or None  # Will be auto-generated if None
        location.category_id = request.POST.get('category')
        location.location_type = request.POST.get('location_type')
        location.short_description = request.POST.get('short_description')
        location.full_description = request.POST.get('full_description')
        location.address = request.POST.get('address')
        location.latitude = request.POST.get('latitude')
        location.longitude = request.POST.get('longitude')
        location.featured = request.POST.get('featured') == 'on'
        location.is_active = request.POST.get('is_active') == 'on'
        location.updated_by = request.user
        
        # Validate required fields
        if not all([location.title, location.category_id, location.location_type, location.short_description, location.address]):
            messages.error(request, 'Ada beberapa field yang wajib diisi')
            # Get categories for form
            categories = TourismCategory.objects.filter(is_active=True)
            
            context = {
                'title': 'Edit Lokasi Wisata',
                'subtitle': f'Edit data lokasi wisata "{location.title}"',
                'location': location,
                'categories': categories,
                'location_types': TourismLocation.LOCATION_TYPE_CHOICES,
                'is_edit': True,
            }
            
            return render(request, 'admin/modules/tourism/admin_location_form_unified.html', context)
        
        location.save()
        
        # Handle main image if provided
        if 'main_image' in request.FILES:
            location.main_image = request.FILES['main_image']
            location.save()
        
        messages.success(request, f'Lokasi wisata "{location.title}" berhasil diperbarui')
        return redirect('tourism:admin_location_detail', location_id=location.id)
    
    # Get categories for form
    categories = TourismCategory.objects.filter(is_active=True)
    
    context = {
        'title': 'Edit Lokasi Wisata',
        'subtitle': f'Edit data lokasi wisata "{location.title}"',
        'location': location,
        'categories': categories,
        'location_types': TourismLocation.LOCATION_TYPE_CHOICES,
        'is_edit': True,
    }
    
    return render(request, 'admin/modules/tourism/admin_location_form_unified.html', context)

@login_required
def admin_location_delete(request, location_id):
    """Admin view for deleting a tourism location"""
    location = get_object_or_404(TourismLocation, id=location_id)
    
    if request.method == 'POST':
        # Soft delete by setting is_active to False
        location_title = location.title
        location.is_active = False
        location.updated_by = request.user
        location.save()
        messages.success(request, f'Lokasi wisata "{location_title}" berhasil dihapus')
        return redirect('tourism:admin_dashboard')
    
    context = {
        'location': location,
    }
    
    return render(request, 'admin/modules/tourism/admin_location_delete.html', context)

@login_required
def admin_category_list(request):
    """Admin view for listing tourism categories"""
    categories = TourismCategory.objects.all().order_by('name')
    
    # Filter by status if provided
    status = request.GET.get('status')
    if status:
        is_active = status == 'active'
        categories = categories.filter(is_active=is_active)
    
    # Pagination
    paginator = Paginator(categories, 10)  # Show 10 categories per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'categories': page_obj,
        'page_obj': page_obj,
        'selected_status': status,
    }
    
    return render(request, 'admin/modules/tourism/admin_category_list.html', context)

@login_required
def admin_category_create(request):
    """Admin view for creating a new tourism category"""
    if request.method == 'POST':
        # Process form data
        name = request.POST.get('name')
        description = request.POST.get('description')
        icon = request.POST.get('icon')
        color = request.POST.get('color', '#3498db')  # Default blue color
        is_active = request.POST.get('is_active') == 'on'
        
        # Validate required fields
        if not name:
            return JsonResponse({'status': 'error', 'message': 'Name is required'}, status=400)
        
        # Create category
        category = TourismCategory(
            name=name,
            description=description,
            icon=icon,
            color=color,
            is_active=is_active,
        )
        
        # Handle image upload
        if 'image' in request.FILES:
            image = request.FILES['image']
            # Validate image file type
            if not image.content_type in ['image/jpeg', 'image/png', 'image/gif']:
                messages.error(request, 'Format gambar tidak didukung. Gunakan JPG, PNG, atau GIF.')
                return redirect('admin_category_list')
            # Validate image file size (max 2MB)
            if image.size > 2 * 1024 * 1024:
                messages.error(request, 'Ukuran gambar terlalu besar. Maksimal 2MB.')
                return redirect('admin_category_list')
            category.image = image
        
        # Handle video upload
        if 'video' in request.FILES:
            video = request.FILES['video']
            # Validate video file type
            if not video.content_type in ['video/mp4', 'video/webm']:
                messages.error(request, 'Format video tidak didukung. Gunakan MP4 atau WebM.')
                return redirect('admin_category_list')
            # Validate video file size (max 10MB)
            if video.size > 10 * 1024 * 1024:
                messages.error(request, 'Ukuran video terlalu besar. Maksimal 10MB.')
                return redirect('admin_category_list')
            category.video = video
        
        # Handle YouTube link
        youtube_link = request.POST.get('youtube_link')
        if youtube_link:
            category.youtube_link = youtube_link
        
        category.save()
        messages.success(request, f'Kategori {category.name} berhasil dibuat.')
        return redirect('admin_category_list')
    
    context = {}
    
    return render(request, 'admin/modules/tourism/admin_category_form.html', context)

@login_required
def admin_category_edit(request, category_id):
    """Admin view for editing a tourism category"""
    category = get_object_or_404(TourismCategory, id=category_id)
    
    if request.method == 'POST':
        # Process form data
        category.name = request.POST.get('name')
        category.description = request.POST.get('description')
        category.icon = request.POST.get('icon')
        category.color = request.POST.get('color', '#3498db')  # Default blue color
        category.is_active = request.POST.get('is_active') == 'on'
        
        # Validate required fields
        if not category.name:
            return JsonResponse({'status': 'error', 'message': 'Name is required'}, status=400)
        
        # Handle image upload
        if 'image' in request.FILES:
            image = request.FILES['image']
            # Validate image file type
            if not image.content_type in ['image/jpeg', 'image/png', 'image/gif']:
                messages.error(request, 'Format gambar tidak didukung. Gunakan JPG, PNG, atau GIF.')
                return redirect('admin_category_edit', category_id=category.id)
            # Validate image file size (max 2MB)
            if image.size > 2 * 1024 * 1024:
                messages.error(request, 'Ukuran gambar terlalu besar. Maksimal 2MB.')
                return redirect('admin_category_edit', category_id=category.id)
            category.image = image
        
        # Handle image removal
        if request.POST.get('remove_image') == 'on':
            if category.image:
                category.image.delete(save=False)
                category.image = None
        
        # Handle video upload
        if 'video' in request.FILES:
            video = request.FILES['video']
            # Validate video file type
            if not video.content_type in ['video/mp4', 'video/webm']:
                messages.error(request, 'Format video tidak didukung. Gunakan MP4 atau WebM.')
                return redirect('admin_category_edit', category_id=category.id)
            # Validate video file size (max 10MB)
            if video.size > 10 * 1024 * 1024:
                messages.error(request, 'Ukuran video terlalu besar. Maksimal 10MB.')
                return redirect('admin_category_edit', category_id=category.id)
            category.video = video
        
        # Handle video removal
        if request.POST.get('remove_video') == 'on':
            if category.video:
                category.video.delete(save=False)
                category.video = None
        
        # Handle YouTube link
        youtube_link = request.POST.get('youtube_link')
        if youtube_link:
            category.youtube_link = youtube_link
        elif request.POST.get('remove_youtube_link') == 'on':
            category.youtube_link = None
        
        category.save()
        messages.success(request, f'Kategori {category.name} berhasil diperbarui.')
        return redirect('admin_category_list')
    
    context = {
        'category': category,
    }
    
    return render(request, 'admin/modules/tourism/admin_category_form.html', context)

@login_required
def admin_category_delete(request, category_id):
    """Admin view for deleting a tourism category"""
    category = get_object_or_404(TourismCategory, id=category_id)
    
    if request.method == 'POST':
        # Check if category has locations
        if category.locations.exists():
            # Soft delete by setting is_active to False
            category.is_active = False
            category.updated_by = request.user
            category.save()
        else:
            # Hard delete if no locations are associated
            category.delete()
        
        return redirect('category_list')
    
    context = {
        'category': category,
        'has_locations': category.locations.exists(),
    }
    
    return render(request, 'admin/modules/tourism/admin_category_delete.html', context)

@login_required
def admin_package_create(request):
    """Admin view for creating a new tourism package"""
    if request.method == 'POST':
        # Process form data
        title = request.POST.get('title')
        location_id = request.POST.get('location')
        package_type = request.POST.get('package_type')
        description = request.POST.get('description')
        duration = request.POST.get('duration')
        price = request.POST.get('price')
        inclusions = request.POST.get('inclusions')
        exclusions = request.POST.get('exclusions')
        itinerary = request.POST.get('itinerary')
        is_active = request.POST.get('is_active') == 'on'
        
        # Validate required fields
        if not all([title, package_type, description, duration, price]):
            return JsonResponse({'status': 'error', 'message': 'Missing required fields'}, status=400)
        
        # Create package
        package = TourismPackage(
            title=title,
            tourism_location_id=location_id or None,
            package_type=package_type,
            description=description,
            duration=duration,
            price=price,
            inclusions=inclusions,
            exclusions=exclusions,
            itinerary=itinerary,
            is_active=is_active,
            created_by=request.user,
        )
        package.save()
        
        return redirect('admin_package_edit', package_id=package.id)
    
    # Get locations for form
    locations = TourismLocation.objects.filter(is_active=True)
    
    context = {
        'locations': locations,
        'package_types': TourismPackage.PACKAGE_TYPE_CHOICES,
    }
    
    return render(request, 'admin/modules/tourism/admin_package_form.html', context)

@login_required
def admin_package_detail(request, package_id):
    """Admin view for viewing details of a tourism package"""
    package = get_object_or_404(TourismPackage, id=package_id)
    
    context = {
        'package': package,
        'title': f'Detail Paket Wisata - {package.title}',
        'subtitle': f'Informasi lengkap tentang paket wisata {package.title}',
    }
    
    return render(request, 'admin/modules/tourism/admin_package_detail.html', context)

@login_required
def admin_package_edit(request, package_id):
    """Admin view for editing a tourism package"""
    package = get_object_or_404(TourismPackage, id=package_id)
    
    if request.method == 'POST':
        # Process form data
        package.title = request.POST.get('name')
        package.slug = request.POST.get('slug')
        package.tourism_location_id = request.POST.get('location') or None
        package.package_type = request.POST.get('package_type')
        package.description = request.POST.get('description')
        package.duration = request.POST.get('duration')
        package.price = request.POST.get('price')
        package.whatsapp = request.POST.get('whatsapp')
        package.includes = request.POST.get('includes')
        package.excludes = request.POST.get('excludes')
        package.itinerary = request.POST.get('itinerary')
        package.is_active = request.POST.get('is_active') == 'True'
        package.is_featured = request.POST.get('featured') == 'True'
        
        # Handle image upload
        if 'image' in request.FILES:
            package.image = request.FILES['image']
        elif request.POST.get('clear_image') == 'True':
            package.image = None
            
        # Handle video upload
        if 'video' in request.FILES:
            package.video = request.FILES['video']
        elif request.POST.get('clear_video') == 'True':
            package.video = None
            
        # Handle YouTube link
        package.youtube_link = request.POST.get('youtube_link')
        
        # Validate required fields
        if not all([package.title, package.slug, package.tourism_location_id, package.description]):
            return JsonResponse({'status': 'error', 'message': 'Missing required fields'}, status=400)
        
        package.save()
        
        # Handle gallery images
        if 'gallery_images' in request.FILES:
            gallery_images = request.FILES.getlist('gallery_images')
            for i, img in enumerate(gallery_images):
                TourismGallery.objects.create(
                    package=package,
                    image=img,
                    order=i+1
                )
                
        # Handle gallery image deletion
        if request.POST.getlist('delete_gallery_images'):
            image_ids = request.POST.getlist('delete_gallery_images')
            TourismGallery.objects.filter(id__in=image_ids, package=package).delete()
        
        return redirect('tourism:admin_package_list')
    
    # Get locations and categories for form
    locations = TourismLocation.objects.filter(is_active=True)
    categories = TourismCategory.objects.filter(is_active=True)
    
    # Get gallery images
    gallery_images = TourismGallery.objects.filter(package=package, is_active=True).order_by('order')
    
    context = {
        'package': package,
        'locations': locations,
        'categories': categories,
        'package_types': TourismPackage.PACKAGE_TYPE_CHOICES,
        'gallery_images': gallery_images,
    }
    
    return render(request, 'admin/modules/tourism/admin_package_edit.html', context)

@login_required
def admin_package_detail(request, package_id):
    """Admin view for package detail"""
    package = get_object_or_404(TourismPackage, id=package_id)
    
    context = {
        'package': package,
    }
    
    return render(request, 'admin/modules/tourism/admin_package_detail.html', context)

@login_required
def admin_package_delete(request, package_id):
    """Admin view for deleting a tourism package"""
    package = get_object_or_404(TourismPackage, id=package_id)
    
    if request.method == 'POST':
        # Soft delete by setting is_active to False
        package.is_active = False
        package.updated_by = request.user
        package.save()
        return redirect('package_list')
    
    context = {
        'package': package,
    }
    
    return render(request, 'admin/modules/tourism/admin_package_delete.html', context)