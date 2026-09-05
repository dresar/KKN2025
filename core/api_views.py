from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
import json

# Note: Most public APIs have been moved to public.api_views
# This file now contains only admin/internal APIs

# All public APIs have been moved to public.api_views
# This file is reserved for admin/internal APIs only