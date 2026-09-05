import os
import uuid
import hashlib
import qrcode
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.core.files import File
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def generate_unique_filename(original_filename, prefix=''):
    """Generate unique filename with UUID"""
    ext = os.path.splitext(original_filename)[1]
    unique_id = str(uuid.uuid4())[:8]
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    return f"{prefix}{timestamp}_{unique_id}{ext}"

def generate_qr_code(data, size=(200, 200)):
    """Generate QR code image"""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create QR code image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img = qr_img.resize(size, Image.Resampling.LANCZOS)
        
        # Save to BytesIO
        buffer = BytesIO()
        qr_img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return buffer
        
    except Exception as e:
        logger.error(f"Error generating QR code: {e}")
        return None

def create_letterhead_image(village_name, village_address, logo_path=None, size=(800, 200)):
    """Create letterhead image"""
    try:
        # Create image
        img = Image.new('RGB', size, color='white')
        draw = ImageDraw.Draw(img)
        
        # Try to load fonts
        try:
            title_font = ImageFont.truetype('arial.ttf', 24)
            subtitle_font = ImageFont.truetype('arial.ttf', 16)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
        
        # Add logo if provided
        logo_width = 0
        if logo_path and os.path.exists(logo_path):
            try:
                logo = Image.open(logo_path)
                logo_size = (80, 80)
                logo = logo.resize(logo_size, Image.Resampling.LANCZOS)
                img.paste(logo, (20, 60))
                logo_width = 120
            except Exception as e:
                logger.warning(f"Could not load logo: {e}")
        
        # Add text
        text_x = 20 + logo_width
        
        # Village name
        draw.text((text_x, 60), village_name, fill='black', font=title_font)
        
        # Village address
        draw.text((text_x, 90), village_address, fill='black', font=subtitle_font)
        
        # Add line separator
        line_y = 160
        draw.line([(20, line_y), (size[0] - 20, line_y)], fill='black', width=2)
        
        # Save to BytesIO
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return buffer
        
    except Exception as e:
        logger.error(f"Error creating letterhead: {e}")
        return None

def calculate_reading_time(text, words_per_minute=200):
    """Calculate estimated reading time in seconds"""
    if not text:
        return 0
    
    word_count = len(text.split())
    reading_time_minutes = word_count / words_per_minute
    return max(60, int(reading_time_minutes * 60))  # Minimum 1 minute

def extract_text_statistics(text):
    """Extract various statistics from text"""
    if not text:
        return {
            'word_count': 0,
            'character_count': 0,
            'paragraph_count': 0,
            'sentence_count': 0,
            'reading_time': 0
        }
    
    words = text.split()
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    sentences = [s.strip() for s in text.replace('!', '.').replace('?', '.').split('.') if s.strip()]
    
    return {
        'word_count': len(words),
        'character_count': len(text),
        'paragraph_count': len(paragraphs),
        'sentence_count': len(sentences),
        'reading_time': calculate_reading_time(text)
    }

def generate_letter_hash(letter_content, letter_number, created_at):
    """Generate hash for letter verification"""
    content = f"{letter_content}{letter_number}{created_at.isoformat()}"
    return hashlib.sha256(content.encode()).hexdigest()

def validate_file_upload(file, allowed_extensions=None, max_size_mb=10):
    """Validate uploaded file"""
    if not file:
        return False, "No file provided"
    
    # Check file size
    max_size_bytes = max_size_mb * 1024 * 1024
    if file.size > max_size_bytes:
        return False, f"File size exceeds {max_size_mb}MB limit"
    
    # Check file extension
    if allowed_extensions:
        file_ext = os.path.splitext(file.name)[1].lower()
        if file_ext not in allowed_extensions:
            return False, f"File type not allowed. Allowed: {', '.join(allowed_extensions)}"
    
    return True, "File is valid"

def format_letter_number(template, letter_type_code, count, date=None):
    """Format letter number based on template"""
    if not date:
        date = timezone.now()
    
    replacements = {
        '{type}': letter_type_code,
        '{number}': f'{count:03d}',
        '{month}': f'{date.month:02d}',
        '{year}': str(date.year),
        '{village}': 'DSA',  # Default village code
        '{roman_month}': convert_to_roman(date.month)
    }
    
    result = template
    for placeholder, value in replacements.items():
        result = result.replace(placeholder, value)
    
    return result

def convert_to_roman(number):
    """Convert number to Roman numerals"""
    roman_numerals = {
        1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI',
        7: 'VII', 8: 'VIII', 9: 'IX', 10: 'X', 11: 'XI', 12: 'XII'
    }
    return roman_numerals.get(number, str(number))

def clean_html_content(html_content):
    """Clean HTML content for plain text extraction"""
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text()
    except ImportError:
        # Fallback: simple HTML tag removal
        import re
        clean = re.compile('<.*?>')
        return re.sub(clean, '', html_content)

def generate_verification_token():
    """Generate verification token for public access"""
    return str(uuid.uuid4()).replace('-', '')[:16]

def format_indonesian_date(date, include_day=True):
    """Format date in Indonesian format"""
    months = [
        'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
        'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
    ]
    
    days = [
        'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu'
    ]
    
    if include_day:
        day_name = days[date.weekday()]
        return f"{day_name}, {date.day} {months[date.month - 1]} {date.year}"
    else:
        return f"{date.day} {months[date.month - 1]} {date.year}"

def create_backup_filename(original_name):
    """Create backup filename with timestamp"""
    name, ext = os.path.splitext(original_name)
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    return f"{name}_backup_{timestamp}{ext}"

def validate_letter_content(content):
    """Basic validation for letter content"""
    errors = []
    warnings = []
    
    if not content or len(content.strip()) < 10:
        errors.append("Konten surat terlalu pendek")
    
    if len(content) > 10000:
        warnings.append("Konten surat sangat panjang, pertimbangkan untuk mempersingkat")
    
    # Check for common issues
    if content.count('\n\n') < 1:
        warnings.append("Surat sebaiknya memiliki paragraf yang terpisah")
    
    # Check for placeholder text
    placeholders = ['{', '}', '[', ']', 'TODO', 'FIXME']
    for placeholder in placeholders:
        if placeholder in content:
            warnings.append(f"Ditemukan placeholder '{placeholder}' yang belum diisi")
    
    return {
        'is_valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }

def compress_image(image_file, max_width=800, quality=85):
    """Compress image file"""
    try:
        img = Image.open(image_file)
        
        # Calculate new size
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        
        # Save compressed image
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=quality, optimize=True)
        buffer.seek(0)
        
        return buffer
        
    except Exception as e:
        logger.error(f"Error compressing image: {e}")
        return None

def get_file_icon(filename):
    """Get appropriate icon for file type"""
    ext = os.path.splitext(filename)[1].lower()
    
    icon_map = {
        '.pdf': 'fas fa-file-pdf text-danger',
        '.doc': 'fas fa-file-word text-primary',
        '.docx': 'fas fa-file-word text-primary',
        '.xls': 'fas fa-file-excel text-success',
        '.xlsx': 'fas fa-file-excel text-success',
        '.jpg': 'fas fa-file-image text-info',
        '.jpeg': 'fas fa-file-image text-info',
        '.png': 'fas fa-file-image text-info',
        '.gif': 'fas fa-file-image text-info',
        '.txt': 'fas fa-file-alt text-secondary',
        '.zip': 'fas fa-file-archive text-warning',
        '.rar': 'fas fa-file-archive text-warning',
    }
    
    return icon_map.get(ext, 'fas fa-file text-muted')

def sanitize_filename(filename):
    """Sanitize filename for safe storage"""
    import re
    
    # Remove or replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove multiple underscores
    filename = re.sub(r'_+', '_', filename)
    
    # Trim and ensure it's not empty
    filename = filename.strip('_')
    if not filename:
        filename = 'unnamed_file'
    
    return filename

def create_thumbnail(image_file, size=(150, 150)):
    """Create thumbnail from image"""
    try:
        img = Image.open(image_file)
        img.thumbnail(size, Image.Resampling.LANCZOS)
        
        # Create thumbnail with white background
        thumb = Image.new('RGB', size, 'white')
        
        # Center the image
        x = (size[0] - img.width) // 2
        y = (size[1] - img.height) // 2
        thumb.paste(img, (x, y))
        
        # Save to BytesIO
        buffer = BytesIO()
        thumb.save(buffer, format='JPEG', quality=90)
        buffer.seek(0)
        
        return buffer
        
    except Exception as e:
        logger.error(f"Error creating thumbnail: {e}")
        return None

def get_letter_status_badge(status):
    """Get Bootstrap badge class for letter status"""
    status_map = {
        'draft': 'badge-secondary',
        'pending': 'badge-warning',
        'approved': 'badge-success',
        'rejected': 'badge-danger',
        'sent': 'badge-info',
        'archived': 'badge-dark'
    }
    return status_map.get(status, 'badge-secondary')

def calculate_letter_priority(letter):
    """Calculate letter priority based on various factors"""
    priority_score = 0
    
    # Check letter type priority
    if letter.letter_type:
        if 'urgent' in letter.letter_type.name.lower():
            priority_score += 3
        elif 'penting' in letter.letter_type.name.lower():
            priority_score += 2
    
    # Check content for urgent keywords
    urgent_keywords = ['segera', 'urgent', 'mendesak', 'penting', 'darurat']
    content_lower = letter.content.lower()
    for keyword in urgent_keywords:
        if keyword in content_lower:
            priority_score += 1
            break
    
    # Check due date if exists
    if hasattr(letter, 'due_date') and letter.due_date:
        days_until_due = (letter.due_date - timezone.now().date()).days
        if days_until_due <= 1:
            priority_score += 3
        elif days_until_due <= 3:
            priority_score += 2
        elif days_until_due <= 7:
            priority_score += 1
    
    # Return priority level
    if priority_score >= 5:
        return 'high'
    elif priority_score >= 3:
        return 'medium'
    else:
        return 'low'