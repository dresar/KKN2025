import json
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.dateparse import parse_datetime
from django.utils.text import slugify
from news.models import News, NewsCategory, NewsTag
from django.conf import settings

User = get_user_model()

class Command(BaseCommand):
    help = 'Import dummy news data from JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='news_dummy_data.json',
            help='JSON file path (default: news_dummy_data.json)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing news data before import'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        
        # If file path is relative, make it relative to project root
        if not os.path.isabs(file_path):
            file_path = os.path.join(settings.BASE_DIR, file_path)
        
        if not os.path.exists(file_path):
            self.stdout.write(
                self.style.ERROR(f'File not found: {file_path}')
            )
            return
        
        # Clear existing data if requested
        if options['clear']:
            News.objects.all().delete()
            NewsCategory.objects.all().delete()
            NewsTag.objects.all().delete()
            self.stdout.write(
                self.style.WARNING('Cleared existing news data')
            )
        
        # Get or create default user
        try:
            author = User.objects.filter(is_superuser=True).first()
            if not author:
                author = User.objects.first()
            if not author:
                self.stdout.write(
                    self.style.ERROR('No user found. Please create a user first.')
                )
                return
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error getting user: {e}')
            )
            return
        
        # Load JSON data
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                news_data = json.load(f)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error reading JSON file: {e}')
            )
            return
        
        created_count = 0
        updated_count = 0
        
        for item in news_data:
            try:
                # Get or create category
                category_name = item.get('category', 'Umum')
                category, created = NewsCategory.objects.get_or_create(
                    name=category_name,
                    defaults={
                        'slug': slugify(category_name),
                        'description': f'Kategori {category_name}',
                        'is_active': True
                    }
                )
                
                # Parse published date
                published_date = None
                if item.get('published_date'):
                    published_date = parse_datetime(item['published_date'])
                
                # Create or update news
                news, created = News.objects.get_or_create(
                    slug=item['slug'],
                    defaults={
                        'title': item['title'],
                        'content': item['content'],
                        'excerpt': item.get('excerpt', ''),
                        'status': item.get('status', 'published'),
                        'is_featured': item.get('is_featured', False),
                        'is_breaking': item.get('is_breaking', False),
                        'views_count': item.get('views_count', 0),
                        'likes_count': item.get('likes_count', 0),
                        'shares_count': item.get('shares_count', 0),
                        'reading_time': item.get('reading_time', 1),
                        'published_date': published_date,
                        'meta_title': item.get('meta_title', ''),
                        'meta_description': item.get('meta_description', ''),
                        'category': category,
                        'author': author
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Created: {news.title}')
                    )
                else:
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'Already exists: {news.title}')
                    )
                
                # Add tags
                if 'tags' in item and item['tags']:
                    for tag_name in item['tags']:
                        tag, _ = NewsTag.objects.get_or_create(
                            name=tag_name,
                            defaults={'slug': slugify(tag_name)}
                        )
                        news.tags.add(tag)
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing item {item.get("title", "Unknown")}: {e}')
                )
                continue
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nImport completed!\n'
                f'Created: {created_count} news\n'
                f'Already existed: {updated_count} news'
            )
        )