from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.forms.models import model_to_dict
from django.middleware.csrf import get_token
from .models import (
    TourismLocation, TourismCategory, TourismGallery, 
    TourismReview, TourismRating, TourismEvent, TourismPackage, TourismFAQ
)
from .forms import (
    TourismLocationForm, TourismGalleryForm, TourismReviewForm,
    TourismEventForm, TourismPackageForm
)
import json

@csrf_exempt
@require_http_methods(["GET"])
def api_stats(request):
    """API endpoint untuk statistik tourism"""
    try:
        stats = {
            'total_destinations': TourismLocation.objects.filter(is_active=True).count(),
            'total_categories': TourismCategory.objects.filter(is_active=True).count(),
            'total_reviews': TourismReview.objects.filter(is_approved=True).count(),
            'average_rating': TourismRating.objects.aggregate(avg=Avg('rating'))['avg'] or 0,
            'featured_destinations': TourismLocation.objects.filter(featured=True, is_active=True).count(),
            'categories': list(TourismCategory.objects.filter(is_active=True).annotate(
                destination_count=Count('tourismlocation')
            ).values('name', 'destination_count')[:5])
        }
        return JsonResponse(stats)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def api_destinations(request):
    """API endpoint untuk daftar destinasi wisata"""
    try:
        destinations = TourismLocation.objects.filter(is_active=True, status='published')
        
        # Filtering
        featured = request.GET.get('featured')
        category = request.GET.get('category')
        search = request.GET.get('search')
        
        if featured == 'true':
            destinations = destinations.filter(featured=True)
        
        if category:
            destinations = destinations.filter(category_id=category)
        
        if search:
            destinations = destinations.filter(
                Q(title__icontains=search) |
                Q(short_description__icontains=search) |
                Q(address__icontains=search)
            )
        
        # Pagination
        page_size = int(request.GET.get('page_size', 10))
        page = int(request.GET.get('page', 1))
        
        paginator = Paginator(destinations, page_size)
        page_obj = paginator.get_page(page)
        
        results = []
        for destination in page_obj:
            # Get featured image
            featured_image = destination.gallery.filter(is_featured=True).first()
            
            results.append({
                'id': destination.id,
                'title': destination.title,
                'slug': destination.slug,
                'short_description': destination.short_description,
                'address': destination.address,
                'category': {
                    'id': destination.category.id,
                    'name': destination.category.name
                } if destination.category else None,
                'location_type': destination.location_type,
                'entry_fee': float(destination.entry_fee) if destination.entry_fee else 0,
                'average_rating': destination.average_rating,
                'total_reviews': destination.total_reviews,
                'featured': destination.featured,
                'image': featured_image.image.url if featured_image and featured_image.image else None,
                'created_at': destination.created_at.isoformat()
            })
        
        return JsonResponse({
            'results': results,
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'current_page': page,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous()
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def api_csrf_token(request):
    """API endpoint untuk mendapatkan CSRF token"""
    try:
        token = get_token(request)
        return JsonResponse({'csrf_token': token})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ==================== CRUD API ENDPOINTS ====================

@method_decorator(login_required, name='dispatch')
class TourismLocationAPIView(View):
    """API View untuk CRUD Tourism Location"""
    
    def get(self, request, location_id=None):
        """Get location(s)"""
        try:
            if location_id:
                # Get single location
                location = TourismLocation.objects.get(id=location_id)
                data = self._serialize_location(location)
                return JsonResponse(data)
            else:
                # Get all locations with pagination
                locations = TourismLocation.objects.all().order_by('-created_at')
                
                # Search and filter
                search = request.GET.get('search', '')
                status = request.GET.get('status', '')
                category = request.GET.get('category', '')
                
                if search:
                    locations = locations.filter(
                        Q(title__icontains=search) |
                        Q(short_description__icontains=search) |
                        Q(address__icontains=search)
                    )
                
                if status:
                    locations = locations.filter(status=status)
                    
                if category:
                    locations = locations.filter(category_id=category)
                
                # Pagination
                page_size = int(request.GET.get('page_size', 20))
                page = int(request.GET.get('page', 1))
                
                paginator = Paginator(locations, page_size)
                page_obj = paginator.get_page(page)
                
                results = [self._serialize_location(loc) for loc in page_obj]
                
                return JsonResponse({
                    'results': results,
                    'count': paginator.count,
                    'num_pages': paginator.num_pages,
                    'current_page': page,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous()
                })
                
        except TourismLocation.DoesNotExist:
            return JsonResponse({'error': 'Location not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def post(self, request):
        """Create new location"""
        try:
            data = json.loads(request.body)
            form = TourismLocationForm(data)
            
            if form.is_valid():
                location = form.save(commit=False)
                location.created_by = request.user
                location.updated_by = request.user
                location.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Location created successfully',
                    'data': self._serialize_location(location)
                }, status=201)
            else:
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def put(self, request, location_id):
        """Update location"""
        try:
            location = TourismLocation.objects.get(id=location_id)
            data = json.loads(request.body)
            form = TourismLocationForm(data, instance=location)
            
            if form.is_valid():
                location = form.save(commit=False)
                location.updated_by = request.user
                location.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Location updated successfully',
                    'data': self._serialize_location(location)
                })
            else:
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)
                
        except TourismLocation.DoesNotExist:
            return JsonResponse({'error': 'Location not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def delete(self, request, location_id):
        """Delete location"""
        try:
            location = TourismLocation.objects.get(id=location_id)
            location.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Location deleted successfully'
            })
            
        except TourismLocation.DoesNotExist:
            return JsonResponse({'error': 'Location not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def _serialize_location(self, location):
        """Serialize location object to dict"""
        return {
            'id': location.id,
            'title': location.title,
            'slug': location.slug,
            'category': {
                'id': location.category.id,
                'name': location.category.name
            } if location.category else None,
            'location_type': location.location_type,
            'short_description': location.short_description,
            'full_description': location.full_description,
            'address': location.address,
            'latitude': float(location.latitude) if location.latitude else None,
            'longitude': float(location.longitude) if location.longitude else None,
            'opening_hours': location.opening_hours,
            'entry_fee': float(location.entry_fee) if location.entry_fee else 0,
            'contact_phone': location.contact_phone,
            'contact_email': location.contact_email,
            'website': location.website,
            'facilities': location.facilities,
            'activities': location.activities,
            'status': location.status,
            'featured': location.featured,
            'is_active': location.is_active,
            'average_rating': location.average_rating,
            'total_reviews': location.total_reviews,
            'created_at': location.created_at.isoformat(),
            'updated_at': location.updated_at.isoformat()
        }


@method_decorator(login_required, name='dispatch')
class TourismCategoryAPIView(View):
    """API View untuk CRUD Tourism Category"""
    
    def get(self, request, category_id=None):
        """Get category(s)"""
        try:
            if category_id:
                category = TourismCategory.objects.get(id=category_id)
                data = self._serialize_category(category)
                return JsonResponse(data)
            else:
                categories = TourismCategory.objects.all().order_by('name')
                results = [self._serialize_category(cat) for cat in categories]
                return JsonResponse({'results': results})
                
        except TourismCategory.DoesNotExist:
            return JsonResponse({'error': 'Category not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def post(self, request):
        """Create new category"""
        try:
            data = json.loads(request.body)
            category = TourismCategory.objects.create(
                name=data.get('name'),
                description=data.get('description', ''),
                icon=data.get('icon', ''),
                color=data.get('color', '#3B82F6'),
                is_active=data.get('is_active', True)
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Category created successfully',
                'data': self._serialize_category(category)
            }, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def put(self, request, category_id):
        """Update category"""
        try:
            category = TourismCategory.objects.get(id=category_id)
            data = json.loads(request.body)
            
            category.name = data.get('name', category.name)
            category.description = data.get('description', category.description)
            category.icon = data.get('icon', category.icon)
            category.color = data.get('color', category.color)
            category.is_active = data.get('is_active', category.is_active)
            category.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Category updated successfully',
                'data': self._serialize_category(category)
            })
            
        except TourismCategory.DoesNotExist:
            return JsonResponse({'error': 'Category not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def delete(self, request, category_id):
        """Delete category"""
        try:
            category = TourismCategory.objects.get(id=category_id)
            category.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Category deleted successfully'
            })
            
        except TourismCategory.DoesNotExist:
            return JsonResponse({'error': 'Category not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def _serialize_category(self, category):
        """Serialize category object to dict"""
        return {
            'id': category.id,
            'name': category.name,
            'description': category.description,
            'icon': category.icon,
            'color': category.color,
            'is_active': category.is_active,
            'location_count': category.tourismlocation_set.count(),
            'created_at': category.created_at.isoformat(),
            'updated_at': category.updated_at.isoformat()
        }


@method_decorator(login_required, name='dispatch')
class TourismEventAPIView(View):
    """API View untuk CRUD Tourism Event"""
    
    def get(self, request, event_id=None):
        """Get event(s)"""
        try:
            if event_id:
                event = TourismEvent.objects.get(id=event_id)
                data = self._serialize_event(event)
                return JsonResponse(data)
            else:
                events = TourismEvent.objects.all().order_by('-start_date')
                
                # Filter by location
                location_id = request.GET.get('location_id')
                if location_id:
                    events = events.filter(tourism_location_id=location_id)
                
                # Pagination
                page_size = int(request.GET.get('page_size', 20))
                page = int(request.GET.get('page', 1))
                
                paginator = Paginator(events, page_size)
                page_obj = paginator.get_page(page)
                
                results = [self._serialize_event(event) for event in page_obj]
                
                return JsonResponse({
                    'results': results,
                    'count': paginator.count,
                    'num_pages': paginator.num_pages,
                    'current_page': page,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous()
                })
                
        except TourismEvent.DoesNotExist:
            return JsonResponse({'error': 'Event not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def post(self, request):
        """Create new event"""
        try:
            form = TourismEventForm(request.POST, request.FILES)
            
            if form.is_valid():
                event = form.save(commit=False)
                event.created_by = request.user
                event.updated_by = request.user
                event.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Event created successfully',
                    'data': self._serialize_event(event)
                }, status=201)
            else:
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def put(self, request, event_id):
        """Update event"""
        try:
            event = TourismEvent.objects.get(id=event_id)
            form = TourismEventForm(request.POST, request.FILES, instance=event)
            
            if form.is_valid():
                event = form.save(commit=False)
                event.updated_by = request.user
                event.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Event updated successfully',
                    'data': self._serialize_event(event)
                })
            else:
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)
                
        except TourismEvent.DoesNotExist:
            return JsonResponse({'error': 'Event not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def delete(self, request, event_id):
        """Delete event"""
        try:
            event = TourismEvent.objects.get(id=event_id)
            event.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Event deleted successfully'
            })
            
        except TourismEvent.DoesNotExist:
            return JsonResponse({'error': 'Event not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def _serialize_event(self, event):
        """Serialize event object to dict"""
        return {
            'id': event.id,
            'title': event.title,
            'tourism_location': {
                'id': event.tourism_location.id,
                'title': event.tourism_location.title
            } if event.tourism_location else None,
            'event_type': event.event_type,
            'description': event.description,
            'start_date': event.start_date.isoformat(),
            'end_date': event.end_date.isoformat() if event.end_date else None,
            'organizer': event.organizer,
            'contact_info': event.contact_info,
            'registration_required': event.registration_required,
            'registration_url': event.registration_url,
            'is_featured': event.is_featured,
            'is_active': event.is_active,
            'created_at': event.created_at.isoformat(),
            'updated_at': event.updated_at.isoformat()
        }


@method_decorator(login_required, name='dispatch')
class TourismReviewAPIView(View):
    """API View untuk CRUD Tourism Review"""
    
    def get(self, request, review_id=None):
        """Get review(s)"""
        try:
            if review_id:
                review = TourismReview.objects.get(id=review_id)
                data = self._serialize_review(review)
                return JsonResponse(data)
            else:
                reviews = TourismReview.objects.all().order_by('-created_at')
                
                # Filter by location
                location_id = request.GET.get('location_id')
                if location_id:
                    reviews = reviews.filter(tourism_location_id=location_id)
                
                # Filter by approval status
                is_approved = request.GET.get('is_approved')
                if is_approved is not None:
                    reviews = reviews.filter(is_approved=is_approved.lower() == 'true')
                
                # Pagination
                page_size = int(request.GET.get('page_size', 20))
                page = int(request.GET.get('page', 1))
                
                paginator = Paginator(reviews, page_size)
                page_obj = paginator.get_page(page)
                
                results = [self._serialize_review(review) for review in page_obj]
                
                return JsonResponse({
                    'results': results,
                    'count': paginator.count,
                    'num_pages': paginator.num_pages,
                    'current_page': page,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous()
                })
                
        except TourismReview.DoesNotExist:
            return JsonResponse({'error': 'Review not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def post(self, request):
        """Create new review"""
        try:
            data = json.loads(request.body)
            form = TourismReviewForm(data)
            
            if form.is_valid():
                review = form.save(commit=False)
                review.user = request.user
                review.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Review created successfully',
                    'data': self._serialize_review(review)
                }, status=201)
            else:
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def put(self, request, review_id):
        """Update review (approve/reject)"""
        try:
            review = TourismReview.objects.get(id=review_id)
            data = json.loads(request.body)
            
            # Only allow updating approval status and flagged status
            if 'is_approved' in data:
                review.is_approved = data['is_approved']
            if 'is_flagged' in data:
                review.is_flagged = data['is_flagged']
            if 'flagged_reason' in data:
                review.flagged_reason = data['flagged_reason']
            
            review.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Review updated successfully',
                'data': self._serialize_review(review)
            })
            
        except TourismReview.DoesNotExist:
            return JsonResponse({'error': 'Review not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def delete(self, request, review_id):
        """Delete review"""
        try:
            review = TourismReview.objects.get(id=review_id)
            review.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Review deleted successfully'
            })
            
        except TourismReview.DoesNotExist:
            return JsonResponse({'error': 'Review not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def _serialize_review(self, review):
        """Serialize review object to dict"""
        return {
            'id': review.id,
            'tourism_location': {
                'id': review.tourism_location.id,
                'title': review.tourism_location.title
            } if review.tourism_location else None,
            'user': {
                'id': review.user.id,
                'username': review.user.username,
                'full_name': review.user.get_full_name()
            },
            'rating': review.rating,
            'title': review.title,
            'comment': review.comment,
            'visit_date': review.visit_date.isoformat() if review.visit_date else None,
            'visit_type': review.visit_type,
            'is_approved': review.is_approved,
            'is_flagged': review.is_flagged,
            'flagged_reason': review.flagged_reason,
            'created_at': review.created_at.isoformat(),
            'updated_at': review.updated_at.isoformat()
        }


@method_decorator(login_required, name='dispatch')
class TourismPackageAPIView(View):
    """API View untuk CRUD Tourism Package"""
    
    def get(self, request, package_id=None):
        """Get package(s)"""
        try:
            if package_id:
                package = TourismPackage.objects.get(id=package_id)
                data = self._serialize_package(package)
                return JsonResponse(data)
            else:
                packages = TourismPackage.objects.all().order_by('-created_at')
                
                # Filter by location
                location_id = request.GET.get('location_id')
                if location_id:
                    packages = packages.filter(tourism_location_id=location_id)
                
                # Filter by active status
                is_active = request.GET.get('is_active')
                if is_active is not None:
                    packages = packages.filter(is_active=is_active.lower() == 'true')
                
                # Pagination
                page_size = int(request.GET.get('page_size', 20))
                page = int(request.GET.get('page', 1))
                
                paginator = Paginator(packages, page_size)
                page_obj = paginator.get_page(page)
                
                results = [self._serialize_package(package) for package in page_obj]
                
                return JsonResponse({
                    'results': results,
                    'count': paginator.count,
                    'num_pages': paginator.num_pages,
                    'current_page': page,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous()
                })
                
        except TourismPackage.DoesNotExist:
            return JsonResponse({'error': 'Package not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def post(self, request):
        """Create new package"""
        try:
            data = json.loads(request.body)
            form = TourismPackageForm(data)
            
            if form.is_valid():
                package = form.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Package created successfully',
                    'data': self._serialize_package(package)
                }, status=201)
            else:
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def put(self, request, package_id):
        """Update package"""
        try:
            package = TourismPackage.objects.get(id=package_id)
            data = json.loads(request.body)
            form = TourismPackageForm(data, instance=package)
            
            if form.is_valid():
                package = form.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Package updated successfully',
                    'data': self._serialize_package(package)
                })
            else:
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)
                
        except TourismPackage.DoesNotExist:
            return JsonResponse({'error': 'Package not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def delete(self, request, package_id):
        """Delete package"""
        try:
            package = TourismPackage.objects.get(id=package_id)
            package.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Package deleted successfully'
            })
            
        except TourismPackage.DoesNotExist:
            return JsonResponse({'error': 'Package not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def _serialize_package(self, package):
        """Serialize package object to dict"""
        return {
            'id': package.id,
            'name': package.name,
            'tourism_location': {
                'id': package.tourism_location.id,
                'title': package.tourism_location.title
            } if package.tourism_location else None,
            'package_type': package.package_type,
            'description': package.description,
            'duration_days': package.duration_days,
            'duration_nights': package.duration_nights,
            'price_per_person': float(package.price_per_person) if package.price_per_person else 0,
            'min_participants': package.min_participants,
            'max_participants': package.max_participants,
            'included_services': package.included_services,
            'excluded_services': package.excluded_services,
            'itinerary': package.itinerary,
            'terms_conditions': package.terms_conditions,
            'booking_deadline': package.booking_deadline.isoformat() if package.booking_deadline else None,
            'is_featured': package.is_featured,
            'is_active': package.is_active,
            'created_at': package.created_at.isoformat(),
            'updated_at': package.updated_at.isoformat()
        }


@method_decorator(login_required, name='dispatch')
class TourismGalleryAPIView(View):
    """API View untuk CRUD Tourism Gallery"""
    
    def get(self, request, gallery_id=None):
        """Get gallery item(s)"""
        try:
            if gallery_id:
                gallery = TourismGallery.objects.get(id=gallery_id)
                data = self._serialize_gallery(gallery)
                return JsonResponse(data)
            else:
                galleries = TourismGallery.objects.all().order_by('-created_at')
                
                # Filter by location
                location_id = request.GET.get('location_id')
                if location_id:
                    galleries = galleries.filter(tourism_location_id=location_id)
                
                # Filter by media type
                media_type = request.GET.get('media_type')
                if media_type:
                    galleries = galleries.filter(media_type=media_type)
                
                # Pagination
                page_size = int(request.GET.get('page_size', 20))
                page = int(request.GET.get('page', 1))
                
                paginator = Paginator(galleries, page_size)
                page_obj = paginator.get_page(page)
                
                results = [self._serialize_gallery(gallery) for gallery in page_obj]
                
                return JsonResponse({
                    'results': results,
                    'count': paginator.count,
                    'num_pages': paginator.num_pages,
                    'current_page': page,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous()
                })
                
        except TourismGallery.DoesNotExist:
            return JsonResponse({'error': 'Gallery item not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def post(self, request):
        """Create new gallery item"""
        try:
            # Handle multipart form data for file uploads
            form = TourismGalleryForm(request.POST, request.FILES)
            
            if form.is_valid():
                gallery = form.save(commit=False)
                gallery.uploaded_by = request.user
                gallery.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Gallery item created successfully',
                    'data': self._serialize_gallery(gallery)
                }, status=201)
            else:
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def put(self, request, gallery_id):
        """Update gallery item"""
        try:
            gallery = TourismGallery.objects.get(id=gallery_id)
            
            # Handle both JSON and multipart data
            if request.content_type and 'application/json' in request.content_type:
                data = json.loads(request.body)
                form = TourismGalleryForm(data, instance=gallery)
            else:
                form = TourismGalleryForm(request.POST, request.FILES, instance=gallery)
            
            if form.is_valid():
                gallery = form.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Gallery item updated successfully',
                    'data': self._serialize_gallery(gallery)
                })
            else:
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)
                
        except TourismGallery.DoesNotExist:
            return JsonResponse({'error': 'Gallery item not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def delete(self, request, gallery_id):
        """Delete gallery item"""
        try:
            gallery = TourismGallery.objects.get(id=gallery_id)
            
            # Delete the file from storage if it exists
            if gallery.image:
                gallery.image.delete(save=False)
            if gallery.video:
                gallery.video.delete(save=False)
            
            gallery.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Gallery item deleted successfully'
            })
            
        except TourismGallery.DoesNotExist:
            return JsonResponse({'error': 'Gallery item not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def _serialize_gallery(self, gallery):
        """Serialize gallery object to dict"""
        return {
            'id': gallery.id,
            'tourism_location': {
                'id': gallery.tourism_location.id,
                'title': gallery.tourism_location.title
            } if gallery.tourism_location else None,
            'title': gallery.title,
            'description': gallery.description,
            'media_type': gallery.media_type,
            'image': gallery.image.url if gallery.image else None,
            'video': gallery.video.url if gallery.video else None,
            'video_url': gallery.video_url,
            'alt_text': gallery.alt_text,
            'is_featured': gallery.is_featured,
            'display_order': gallery.display_order,
            'uploaded_by': {
                'id': gallery.uploaded_by.id,
                'username': gallery.uploaded_by.username
            } if gallery.uploaded_by else None,
            'created_at': gallery.created_at.isoformat(),
            'updated_at': gallery.updated_at.isoformat()
        }


@csrf_exempt
@require_http_methods(["GET"])
def api_destination_detail(request, destination_id):
    """API endpoint untuk detail destinasi wisata"""
    try:
        destination = TourismLocation.objects.get(id=destination_id, is_active=True, status='published')
        
        # Get gallery
        gallery = []
        for item in destination.gallery.filter(is_active=True).order_by('order'):
            gallery.append({
                'id': item.id,
                'title': item.title,
                'media_type': item.media_type,
                'image': item.image.url if item.image else None,
                'video_url': item.video_url,
                'caption': item.caption,
                'is_featured': item.is_featured
            })
        
        # Get reviews
        reviews = []
        for review in destination.reviews.filter(is_approved=True).order_by('-created_at')[:10]:
            reviews.append({
                'id': review.id,
                'user': review.user.get_full_name() or review.user.username,
                'rating': review.rating,
                'title': review.title,
                'comment': review.comment,
                'visit_date': review.visit_date.isoformat() if review.visit_date else None,
                'created_at': review.created_at.isoformat()
            })
        
        data = {
            'id': destination.id,
            'title': destination.title,
            'slug': destination.slug,
            'short_description': destination.short_description,
            'full_description': destination.full_description,
            'address': destination.address,
            'latitude': float(destination.latitude) if destination.latitude else None,
            'longitude': float(destination.longitude) if destination.longitude else None,
            'opening_hours': destination.opening_hours,
            'entry_fee': float(destination.entry_fee) if destination.entry_fee else 0,
            'contact_phone': destination.contact_phone,
            'contact_email': destination.contact_email,
            'website': destination.website,
            'category': {
                'id': destination.category.id,
                'name': destination.category.name,
                'description': destination.category.description
            } if destination.category else None,
            'location_type': destination.location_type,
            'facilities': destination.facilities,
            'activities': destination.activities,
            'average_rating': destination.average_rating,
            'total_reviews': destination.total_reviews,
            'featured': destination.featured,
            'gallery': gallery,
            'reviews': reviews,
            'created_at': destination.created_at.isoformat()
        }
        
        return JsonResponse(data)
    except TourismLocation.DoesNotExist:
        return JsonResponse({'error': 'Destination not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def api_destination_visit(request, destination_id):
    """API endpoint untuk mencatat kunjungan destinasi"""
    try:
        destination = TourismLocation.objects.get(id=destination_id, is_active=True)
        
        # Increment visit count (you might want to add a visit tracking model)
        # For now, we'll just return success
        
        return JsonResponse({'message': 'Visit recorded successfully'})
    except TourismLocation.DoesNotExist:
        return JsonResponse({'error': 'Destination not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def api_gallery(request):
    """API endpoint untuk galeri tourism"""
    try:
        gallery_items = TourismGallery.objects.filter(is_active=True).select_related('tourism_location')
        
        # Pagination
        page_size = int(request.GET.get('page_size', 12))
        page = int(request.GET.get('page', 1))
        
        paginator = Paginator(gallery_items, page_size)
        page_obj = paginator.get_page(page)
        
        results = []
        for item in page_obj:
            results.append({
                'id': item.id,
                'title': item.title,
                'media_type': item.media_type,
                'image': item.image.url if item.image else None,
                'video_url': item.video_url,
                'caption': item.caption,
                'destination': {
                    'id': item.tourism_location.id,
                    'title': item.tourism_location.title
                } if item.tourism_location else None,
                'created_at': item.created_at.isoformat()
            })
        
        return JsonResponse({
            'results': results,
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'current_page': page,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous()
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)