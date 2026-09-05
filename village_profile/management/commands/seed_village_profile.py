from django.core.management.base import BaseCommand
from django.utils import timezone
from village_profile.models import (
    VillageVision, VillageHistory, VillageMap, VillageGeography
)
from io import BytesIO
from django.core.files.base import ContentFile

try:
    from PIL import Image, ImageDraw  # pillow is commonly installed with Django projects
except Exception:  # fallback without Pillow
    Image = None


class Command(BaseCommand):
    help = "Seed dummy data for village profile (visions, history, geography, maps)"

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('Seeding village profile data...'))

        # 1) Visi Misi
        if not VillageVision.objects.exists():
            VillageVision.objects.create(
                title='Visi Misi Desa Pulosarok',
                vision_text='Mewujudkan Desa Pulosarok yang maju, mandiri, dan sejahtera.',
                mission_text='1. Pelayanan publik prima\n2. Ekonomi desa berdaya\n3. Pemerintahan transparan',
                description='Dokumen visi misi desa.',
                is_active=True,
                effective_date=timezone.now().date(),
            )
            self.stdout.write(self.style.SUCCESS('- Visi misi dibuat'))
        else:
            self.stdout.write('- Visi misi sudah ada, lewati')

        # 2) Sejarah
        if not VillageHistory.objects.exists():
            VillageHistory.objects.create(
                title='Sejarah Desa Pulosarok',
                content='Desa berdiri pada abad ke-19 dan berkembang pesat hingga kini.',
                period_start='1890',
                period_end='Sekarang',
                is_featured=True,
                is_active=True,
            )
            self.stdout.write(self.style.SUCCESS('- Sejarah dibuat'))
        else:
            self.stdout.write('- Sejarah sudah ada, lewati')

        # 3) Geografi
        if not VillageGeography.objects.filter(is_active=True).exists():
            VillageGeography.objects.create(
                total_area=500,
                agricultural_area=300,
                residential_area=150,
                water_area=10,
                altitude_min=50,
                altitude_max=300,
                climate_type='Tropis',
                rainfall_average=2000,
                temperature_min=22.5,
                temperature_max=31.0,
                boundaries_north='Desa A',
                boundaries_south='Desa B',
                boundaries_east='Desa C',
                boundaries_west='Desa D',
                is_active=True,
            )
            self.stdout.write(self.style.SUCCESS('- Geografi dibuat'))
        else:
            self.stdout.write('- Geografi aktif sudah ada, lewati')

        # 4) Peta (buat placeholder image jika memungkinkan)
        if not VillageMap.objects.exists():
            content_file = None
            if Image is not None:
                img = Image.new('RGB', (600, 400), color=(30, 100, 200))
                d = ImageDraw.Draw(img)
                d.text((20, 20), 'Peta Desa Pulosarok (Dummy)', fill=(255, 255, 255))
                buffer = BytesIO()
                img.save(buffer, format='PNG')
                content_file = ContentFile(buffer.getvalue(), name='map_dummy.png')

            map_obj = VillageMap(
                title='Peta Administrasi Desa',
                map_type='ADMINISTRATIVE',
                description='Peta dummy untuk pengujian.',
                is_active=True,
                zoom_level=14,
            )
            if content_file:
                map_obj.map_image.save('map_dummy.png', content_file, save=False)
            map_obj.save()
            self.stdout.write(self.style.SUCCESS('- Peta dibuat'))
        else:
            self.stdout.write('- Peta sudah ada, lewati')

        self.stdout.write(self.style.SUCCESS('Selesai seeding village profile.'))
