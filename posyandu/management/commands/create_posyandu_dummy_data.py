from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
import random

from posyandu.models import (
    PosyanduLocation, PosyanduKader, IbuHamil, PemeriksaanIbuHamil,
    StuntingData, HealthRecord, Immunization, NutritionData
)
from references.models import Penduduk
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create dummy data for Posyandu module'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of records to create for each model'
        )

    def handle(self, *args, **options):
        count = options['count']
        
        self.stdout.write('Creating Posyandu dummy data...')
        
        # Get or create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            
        # Get existing residents or create some
        residents = list(Penduduk.objects.all()[:50])
        if not residents:
            self.stdout.write('No residents found. Please create residents first.')
            return
            
        # Create Posyandu Locations
        self.stdout.write('Creating Posyandu Locations...')
        locations = []
        for i in range(count):
            location = PosyanduLocation.objects.create(
                name=f'Posyandu {chr(65+i)}',
                address=f'Jalan Posyandu {i+1}, RT {i+1:02d}/RW {(i//3)+1:02d}',
                coordinator=random.choice(residents),
                contact_phone=f'08{random.randint(1000000000, 9999999999)}',
                capacity=random.randint(30, 100),
                facilities='Timbangan, Pengukur tinggi, Alat tensi, Termometer',
                is_active=True,
                established_date=date.today() - timedelta(days=random.randint(365, 1825))
            )
            locations.append(location)
        self.stdout.write(f'Created {len(locations)} Posyandu locations')
        
        # Create Posyandu Kaders
        self.stdout.write('Creating Posyandu Kaders...')
        jabatan_choices = ['ketua', 'wakil_ketua', 'sekretaris', 'bendahara', 'anggota']
        kaders = []
        for i in range(count * 2):
            try:
                kader = PosyanduKader.objects.create(
                    penduduk=random.choice(residents),
                    posyandu=random.choice(locations),
                    jabatan=random.choice(jabatan_choices),
                    nomor_hp=f'08{random.randint(1000000000, 9999999999)}',
                    tanggal_mulai=date.today() - timedelta(days=random.randint(30, 365)),
                    status='aktif',
                    keterangan=f'Kader aktif sejak {date.today().year - random.randint(1, 3)}'
                )
                kaders.append(kader)
            except Exception as e:
                # Skip if duplicate
                continue
        self.stdout.write(f'Created {len(kaders)} Posyandu kaders')
        
        # Create Ibu Hamil
        self.stdout.write('Creating Ibu Hamil data...')
        ibu_hamil_list = []
        female_residents = [r for r in residents if r.gender == 'P']
        for i in range(min(count, len(female_residents))):
            resident = female_residents[i]
            hpht = date.today() - timedelta(days=random.randint(30, 280))
            ibu_hamil = IbuHamil.objects.create(
                penduduk=resident,
                posyandu=random.choice(locations),
                tanggal_hpht=hpht,
                usia_kehamilan=random.randint(4, 40),
                tanggal_perkiraan_lahir=hpht + timedelta(days=280),
                riwayat_kehamilan=random.choice(['1', '2', '3', '4+']),
                berat_badan_sebelum_hamil=random.uniform(45.0, 70.0),
                tinggi_badan=random.uniform(150.0, 170.0),
                golongan_darah=random.choice(['A', 'B', 'AB', 'O']),
                risiko_kehamilan=random.choice(['rendah', 'tinggi']),
                nomor_buku_kia=f'KIA{random.randint(100000, 999999)}',
                status_aktif=True
            )
            ibu_hamil_list.append(ibu_hamil)
        self.stdout.write(f'Created {len(ibu_hamil_list)} Ibu Hamil records')
        
        # Create Pemeriksaan Ibu Hamil
        self.stdout.write('Creating Pemeriksaan Ibu Hamil data...')
        pemeriksaan_count = 0
        for ibu_hamil in ibu_hamil_list:
            for j in range(random.randint(1, 4)):
                PemeriksaanIbuHamil.objects.create(
                    ibu_hamil=ibu_hamil,
                    tanggal_periksa=date.today() - timedelta(days=random.randint(1, 90)),
                    usia_kehamilan=random.randint(4, 40),
                    berat_badan=random.uniform(50.0, 80.0),
                    tekanan_darah=f'{random.randint(90, 140)}/{random.randint(60, 90)}',
                    tinggi_fundus=random.uniform(20.0, 35.0),
                    lingkar_lengan_atas=random.uniform(23.0, 30.0),
                    hemoglobin=random.uniform(9.0, 14.0),
                    tablet_fe=random.choice([True, False]),
                    imunisasi_tt=random.choice([True, False]),
                    keluhan=random.choice(['Tidak ada keluhan', 'Mual', 'Pusing', 'Kram kaki']),
                    anjuran='Istirahat cukup, makan bergizi',
                    pemeriksa=admin_user
                )
                pemeriksaan_count += 1
        self.stdout.write(f'Created {pemeriksaan_count} Pemeriksaan Ibu Hamil records')
        
        # Create Stunting Data
        self.stdout.write('Creating Stunting data...')
        balita_residents = [r for r in residents if r.gender in ['L', 'P'] and 
                           r.birth_date and (date.today() - r.birth_date).days < 1825]  # Under 5 years
        stunting_count = 0
        for i in range(min(count, len(balita_residents))):
            balita = balita_residents[i]
            age_days = (date.today() - balita.birth_date).days
            age_months = age_days // 30
            
            StuntingData.objects.create(
                balita=balita,
                posyandu=random.choice(locations),
                tanggal_ukur=date.today() - timedelta(days=random.randint(1, 30)),
                usia_bulan=age_months,
                tinggi_badan=random.uniform(60.0, 110.0),
                berat_badan=random.uniform(6.0, 20.0),
                z_score_tb_u=random.uniform(-3.0, 2.0),
                z_score_bb_u=random.uniform(-3.0, 2.0),
                z_score_bb_tb=random.uniform(-3.0, 2.0),
                status_stunting=random.choice(['normal', 'pendek', 'sangat_pendek']),
                asi_eksklusif=random.choice([True, False]),
                riwayat_bblr=random.choice([True, False]),
                intervensi_diberikan=random.choice(['gizi', 'kesehatan', 'sanitasi', 'edukasi']),
                follow_up_date=date.today() + timedelta(days=30),
                recorded_by=admin_user
            )
            stunting_count += 1
        self.stdout.write(f'Created {stunting_count} Stunting records')
        
        # Create Health Records
        self.stdout.write('Creating Health Records...')
        health_count = 0
        for i in range(count):
            HealthRecord.objects.create(
                patient=random.choice(residents),
                posyandu=random.choice(locations),
                patient_type=random.choice(['balita', 'ibu_hamil', 'ibu_menyusui', 'lansia']),
                visit_date=date.today() - timedelta(days=random.randint(1, 90)),
                weight=random.uniform(10.0, 80.0),
                height=random.uniform(60.0, 180.0),
                blood_pressure=f'{random.randint(90, 140)}/{random.randint(60, 90)}',
                temperature=random.uniform(36.0, 38.0),
                complaints=random.choice(['Tidak ada keluhan', 'Demam', 'Batuk', 'Pilek', 'Sakit kepala']),
                diagnosis=random.choice(['Sehat', 'ISPA', 'Hipertensi', 'Anemia']),
                treatment='Istirahat, minum obat sesuai anjuran',
                next_visit=date.today() + timedelta(days=30),
                recorded_by=admin_user
            )
            health_count += 1
        self.stdout.write(f'Created {health_count} Health Records')
        
        # Create Immunization Records
        self.stdout.write('Creating Immunization Records...')
        vaccine_types = ['bcg', 'hepatitis_b', 'polio', 'dpt', 'campak', 'mmr']
        immunization_count = 0
        for i in range(count):
            vaccine_type = random.choice(vaccine_types)
            Immunization.objects.create(
                patient=random.choice(residents),
                posyandu=random.choice(locations),
                vaccine_type=vaccine_type,
                vaccine_name=vaccine_type.upper(),
                dose_number=random.randint(1, 3),
                immunization_date=date.today() - timedelta(days=random.randint(1, 365)),
                batch_number=f'BATCH{random.randint(100000, 999999)}',
                expiry_date=date.today() + timedelta(days=random.randint(365, 730)),
                next_dose_date=date.today() + timedelta(days=random.randint(30, 90)),
                administered_by=admin_user
            )
            immunization_count += 1
        self.stdout.write(f'Created {immunization_count} Immunization Records')
        
        # Create Nutrition Data
        self.stdout.write('Creating Nutrition Data...')
        nutrition_count = 0
        for i in range(count):
            patient = random.choice(balita_residents) if balita_residents else random.choice(residents)
            age_days = (date.today() - patient.birth_date).days if patient.birth_date else 365
            age_months = age_days // 30
            
            NutritionData.objects.create(
                patient=patient,
                posyandu=random.choice(locations),
                measurement_date=date.today() - timedelta(days=random.randint(1, 30)),
                age_months=age_months,
                weight=random.uniform(6.0, 25.0),
                height=random.uniform(60.0, 120.0),
                head_circumference=random.uniform(40.0, 55.0),
                arm_circumference=random.uniform(12.0, 18.0),
                nutrition_status=random.choice(['normal', 'kurang', 'buruk', 'lebih', 'stunting', 'wasting']),
                vitamin_a_given=random.choice([True, False]),
                iron_supplement_given=random.choice([True, False]),
                notes='Pemantauan rutin pertumbuhan',
                recorded_by=admin_user
            )
            nutrition_count += 1
        self.stdout.write(f'Created {nutrition_count} Nutrition Data records')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created Posyandu dummy data:\n'
                f'- {len(locations)} Posyandu Locations\n'
                f'- {len(kaders)} Kaders\n'
                f'- {len(ibu_hamil_list)} Ibu Hamil\n'
                f'- {pemeriksaan_count} Pemeriksaan Ibu Hamil\n'
                f'- {stunting_count} Stunting Data\n'
                f'- {health_count} Health Records\n'
                f'- {immunization_count} Immunization Records\n'
                f'- {nutrition_count} Nutrition Data'
            )
        )