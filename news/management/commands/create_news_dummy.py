from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify
from datetime import timedelta
import random
from news.models import News, NewsCategory, NewsTag

User = get_user_model()

class Command(BaseCommand):
    help = 'Create dummy news data'

    def handle(self, *args, **options):
        self.stdout.write('Creating dummy news data...')
        
        # Create categories
        categories_data = [
            {'name': 'Pemerintahan Desa', 'description': 'Berita seputar pemerintahan dan administrasi desa', 'color': '#007bff'},
            {'name': 'Pembangunan', 'description': 'Berita tentang pembangunan infrastruktur desa', 'color': '#28a745'},
            {'name': 'Sosial Kemasyarakatan', 'description': 'Berita kegiatan sosial dan kemasyarakatan', 'color': '#ffc107'},
            {'name': 'Ekonomi Desa', 'description': 'Berita seputar ekonomi dan UMKM desa', 'color': '#17a2b8'},
            {'name': 'Pendidikan', 'description': 'Berita tentang pendidikan dan pelatihan', 'color': '#6f42c1'},
            {'name': 'Kesehatan', 'description': 'Berita kesehatan masyarakat desa', 'color': '#e83e8c'},
            {'name': 'Lingkungan', 'description': 'Berita tentang lingkungan dan kebersihan', 'color': '#20c997'},
            {'name': 'Budaya', 'description': 'Berita seni budaya dan tradisi desa', 'color': '#fd7e14'},
        ]
        
        categories = []
        for cat_data in categories_data:
            category, created = NewsCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'color': cat_data['color']
                }
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        # Create tags
        tags_data = [
            'Gotong Royong', 'Musyawarah', 'Pemberdayaan', 'Inovasi', 'Teknologi',
            'Kearifan Lokal', 'Partisipasi', 'Transparansi', 'Akuntabilitas', 'Kolaborasi',
            'Swadaya', 'Mandiri', 'Berkelanjutan', 'Inklusif', 'Responsif'
        ]
        
        tags = []
        for tag_name in tags_data:
            tag, created = NewsTag.objects.get_or_create(
                name=tag_name,
                defaults={'slug': slugify(tag_name)}
            )
            tags.append(tag)
            if created:
                self.stdout.write(f'Created tag: {tag.name}')
        
        # Get or create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@pulosarok.id',
                'first_name': 'Administrator',
                'last_name': 'Desa',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write('Created admin user')
        
        # Create news articles
        news_data = [
            {
                'title': 'Musyawarah Desa Bahas Rencana Pembangunan Jalan Desa Tahun 2025',
                'content': '''Desa Pulosarok mengadakan musyawarah desa untuk membahas rencana pembangunan jalan desa tahun 2025. Kegiatan ini dihadiri oleh seluruh perangkat desa, tokoh masyarakat, dan perwakilan dari setiap RT/RW.

Kepala Desa menyampaikan bahwa pembangunan jalan desa merupakan prioritas utama untuk meningkatkan aksesibilitas dan mobilitas masyarakat. Rencana pembangunan meliputi perbaikan jalan utama sepanjang 2 km dan pembangunan jalan baru menuju area persawahan.

Dalam musyawarah tersebut, masyarakat memberikan masukan dan saran terkait prioritas pembangunan. Beberapa warga menyampaikan pentingnya perbaikan jalan di area yang sering tergenang air saat musim hujan.

Rencana anggaran untuk pembangunan jalan desa tahun 2025 sebesar Rp 500 juta yang bersumber dari Dana Desa dan swadaya masyarakat. Pelaksanaan pembangunan dijadwalkan dimulai pada bulan Maret 2025.''',
                'category': 'Pemerintahan Desa',
                'tags': ['Musyawarah', 'Pembangunan', 'Partisipasi'],
                'status': 'published',
                'priority': 'high',
                'is_featured': True
            },
            {
                'title': 'Program Pelatihan Keterampilan Menjahit untuk Ibu-Ibu PKK',
                'content': '''Tim Penggerak PKK Desa Pulosarok mengadakan program pelatihan keterampilan menjahit untuk meningkatkan kemampuan dan kemandirian ekonomi ibu-ibu di desa.

Pelatihan ini berlangsung selama 2 minggu dengan peserta sebanyak 25 orang ibu-ibu dari berbagai RT. Materi pelatihan meliputi teknik dasar menjahit, membuat pola, dan keterampilan finishing.

Ketua PKK menyampaikan bahwa program ini bertujuan untuk memberdayakan perempuan desa agar memiliki keterampilan yang dapat dijadikan sumber penghasilan tambahan. Setelah pelatihan, peserta diharapkan dapat membuka usaha jahit mandiri atau bergabung dalam kelompok usaha bersama.

Pelatihan ini mendapat dukungan penuh dari pemerintah desa dan bekerja sama dengan Dinas Pemberdayaan Perempuan dan Perlindungan Anak Kabupaten.''',
                'category': 'Sosial Kemasyarakatan',
                'tags': ['Pemberdayaan', 'PKK', 'Keterampilan'],
                'status': 'published',
                'priority': 'normal'
            },
            {
                'title': 'Launching Website Resmi Desa Pulosarok untuk Pelayanan Digital',
                'content': '''Pemerintah Desa Pulosarok resmi meluncurkan website desa sebagai upaya digitalisasi pelayanan publik dan transparansi informasi kepada masyarakat.

Website desa yang dapat diakses melalui alamat www.pulosarok.desa.id menyediakan berbagai informasi seperti profil desa, berita terkini, layanan administrasi online, dan data pembangunan desa.

Kepala Desa menyampaikan bahwa website ini merupakan wujud komitmen pemerintah desa dalam memberikan pelayanan yang lebih baik dan transparan kepada masyarakat. Melalui website ini, masyarakat dapat mengakses informasi dan layanan desa kapan saja dan dimana saja.

Fitur unggulan website ini antara lain layanan surat online, informasi program desa, galeri kegiatan, dan sistem pengaduan masyarakat. Website ini dikembangkan dengan dukungan dari mahasiswa KKN dan tim IT lokal.''',
                'category': 'Pemerintahan Desa',
                'tags': ['Teknologi', 'Inovasi', 'Transparansi'],
                'status': 'published',
                'priority': 'high',
                'is_featured': True
            },
            {
                'title': 'Gotong Royong Pembersihan Saluran Air dan Lingkungan Desa',
                'content': '''Masyarakat Desa Pulosarok mengadakan kegiatan gotong royong pembersihan saluran air dan lingkungan desa dalam rangka menyambut musim hujan.

Kegiatan yang diikuti oleh lebih dari 100 warga ini meliputi pembersihan saluran drainase, pengangkatan sampah, dan penataan lingkungan di area publik. Gotong royong dimulai pukul 07.00 WIB dan berlangsung hingga siang hari.

Kepala Desa mengapresiasi antusiasme masyarakat dalam menjaga kebersihan lingkungan. Kegiatan ini merupakan bentuk kepedulian bersama untuk mencegah banjir dan menjaga kesehatan lingkungan.

Selain pembersihan, kegiatan ini juga dimanfaatkan untuk sosialisasi program pengelolaan sampah dan himbauan untuk tidak membuang sampah sembarangan. Pemerintah desa menyediakan konsumsi dan peralatan kebersihan untuk mendukung kegiatan ini.''',
                'category': 'Lingkungan',
                'tags': ['Gotong Royong', 'Lingkungan', 'Partisipasi'],
                'status': 'published',
                'priority': 'normal'
            },
            {
                'title': 'Festival Budaya Desa Pulosarok Lestarikan Tradisi Lokal',
                'content': '''Desa Pulosarok menggelar Festival Budaya Desa untuk melestarikan dan memperkenalkan kekayaan tradisi lokal kepada generasi muda.

Festival yang berlangsung selama 3 hari ini menampilkan berbagai pertunjukan seni tradisional seperti tari-tarian daerah, musik tradisional, dan pameran kerajinan tangan khas desa.

Acara ini juga dimeriahkan dengan lomba-lomba tradisional seperti panjat pinang, balap karung, dan tarik tambang antar RT. Selain itu, terdapat pameran produk UMKM lokal dan kuliner khas desa.

Kepala Desa menyampaikan bahwa festival ini bertujuan untuk memperkuat identitas budaya desa dan meningkatkan rasa bangga masyarakat terhadap warisan leluhur. Festival ini juga diharapkan dapat menjadi daya tarik wisata dan meningkatkan ekonomi masyarakat.''',
                'category': 'Budaya',
                'tags': ['Budaya', 'Kearifan Lokal', 'Festival'],
                'status': 'published',
                'priority': 'high'
            },
            {
                'title': 'Posyandu Balita Raih Penghargaan Terbaik Tingkat Kabupaten',
                'content': '''Posyandu Balita Desa Pulosarok meraih penghargaan sebagai Posyandu Terbaik tingkat kabupaten berkat konsistensi dan inovasi dalam pelayanan kesehatan anak.

Penghargaan ini diberikan berdasarkan penilaian terhadap kelengkapan data, keaktifan kader, cakupan pelayanan, dan inovasi program. Posyandu Pulosarok dinilai unggul dalam hal partisipasi masyarakat dan penggunaan teknologi untuk pencatatan data.

Ketua Posyandu menyampaikan bahwa pencapaian ini tidak lepas dari dukungan pemerintah desa, antusiasme masyarakat, dan dedikasi para kader kesehatan. Posyandu ini melayani lebih dari 150 balita dengan tingkat partisipasi mencapai 95%.

Sebagai tindak lanjut, Posyandu Pulosarok akan menjadi percontohan bagi posyandu lain di kabupaten dan mendapat bantuan peralatan kesehatan tambahan dari pemerintah daerah.''',
                'category': 'Kesehatan',
                'tags': ['Posyandu', 'Kesehatan', 'Penghargaan'],
                'status': 'published',
                'priority': 'high',
                'is_breaking': True
            },
            {
                'title': 'Pelatihan Budidaya Ikan Lele untuk Kelompok Tani Desa',
                'content': '''Kelompok Tani Desa Pulosarok mengikuti pelatihan budidaya ikan lele sebagai upaya diversifikasi usaha dan peningkatan pendapatan petani.

Pelatihan yang diselenggarakan selama 3 hari ini menghadirkan narasumber dari Dinas Perikanan Kabupaten dan praktisi budidaya ikan sukses. Materi pelatihan meliputi teknik pembenihan, pembesaran, pakan, dan manajemen kolam.

Ketua Kelompok Tani menyampaikan bahwa pelatihan ini sangat bermanfaat untuk mengembangkan usaha sampingan di luar pertanian padi. Budidaya lele dipilih karena relatif mudah, modal terjangkau, dan permintaan pasar yang tinggi.

Setelah pelatihan, kelompok tani berencana membuat kolam percontohan dan mengembangkan usaha budidaya ikan secara berkelompok. Pemerintah desa berkomitmen memberikan dukungan berupa bantuan bibit dan pendampingan teknis.''',
                'category': 'Ekonomi Desa',
                'tags': ['Pelatihan', 'Budidaya', 'Kelompok Tani'],
                'status': 'published',
                'priority': 'normal'
            },
            {
                'title': 'Pembangunan Balai Desa Baru Dimulai, Target Selesai 6 Bulan',
                'content': '''Pembangunan Balai Desa baru Pulosarok resmi dimulai dengan peletakan batu pertama oleh Kepala Desa dan disaksikan masyarakat.

Balai Desa baru ini dibangun di atas lahan seluas 500 m² dengan konsep modern namun tetap mempertahankan unsur arsitektur tradisional. Bangunan akan terdiri dari ruang pertemuan, ruang pelayanan, dan ruang kerja perangkat desa.

Anggaran pembangunan sebesar Rp 800 juta bersumber dari Dana Desa dan APBD Kabupaten. Kontraktor yang ditunjuk adalah perusahaan lokal dengan pengalaman membangun fasilitas publik.

Kepala Desa menyampaikan bahwa balai desa baru ini akan meningkatkan kualitas pelayanan kepada masyarakat dan menjadi pusat kegiatan pemerintahan dan kemasyarakatan. Target penyelesaian pembangunan adalah 6 bulan ke depan.''',
                'category': 'Pembangunan',
                'tags': ['Pembangunan', 'Balai Desa', 'Infrastruktur'],
                'status': 'published',
                'priority': 'high'
            },
            {
                'title': 'Program Beasiswa Pendidikan untuk Anak Berprestasi Desa Pulosarok',
                'content': '''Pemerintah Desa Pulosarok meluncurkan program beasiswa pendidikan untuk mendukung anak-anak berprestasi melanjutkan pendidikan ke jenjang yang lebih tinggi.

Program beasiswa ini memberikan bantuan biaya pendidikan untuk 10 siswa berprestasi dari keluarga kurang mampu. Beasiswa mencakup biaya sekolah, seragam, buku, dan uang saku bulanan.

Kriteria penerima beasiswa meliputi prestasi akademik, kondisi ekonomi keluarga, dan komitmen untuk berkontribusi bagi desa setelah menyelesaikan pendidikan. Seleksi dilakukan secara transparan dengan melibatkan komite pendidikan desa.

Kepala Desa menyampaikan bahwa investasi pendidikan adalah investasi terbaik untuk masa depan desa. Diharapkan para penerima beasiswa dapat menjadi generasi penerus yang berkualitas dan berkontribusi membangun desa.''',
                'category': 'Pendidikan',
                'tags': ['Beasiswa', 'Pendidikan', 'Prestasi'],
                'status': 'published',
                'priority': 'normal'
            },
            {
                'title': 'Koperasi Desa Pulosarok Raih Omzet 2 Miliar di Tahun 2024',
                'content': '''Koperasi Desa Pulosarok berhasil mencatatkan omzet sebesar Rp 2 miliar pada tahun 2024, meningkat 150% dibandingkan tahun sebelumnya.

Pencapaian ini tidak lepas dari diversifikasi usaha koperasi yang meliputi simpan pinjam, toko kebutuhan pokok, dan unit usaha pengolahan hasil pertanian. Koperasi juga mengembangkan layanan digital untuk memudahkan anggota.

Ketua Koperasi menyampaikan bahwa keberhasilan ini merupakan hasil kerja keras pengurus dan dukungan penuh dari anggota. Saat ini koperasi memiliki 300 anggota aktif dengan tingkat kepercayaan yang tinggi.

Rencana ke depan, koperasi akan mengembangkan unit usaha baru berupa pengolahan makanan ringan dan ekspansi ke desa-desa tetangga. Target omzet tahun 2025 adalah Rp 3 miliar dengan penambahan 100 anggota baru.''',
                'category': 'Ekonomi Desa',
                'tags': ['Koperasi', 'Ekonomi', 'Prestasi'],
                'status': 'published',
                'priority': 'high',
                'is_featured': True
            },
            {
                'title': 'Sosialisasi Program Stunting dan Gizi Buruk untuk Ibu Hamil',
                'content': '''Puskesmas bekerja sama dengan Pemerintah Desa Pulosarok mengadakan sosialisasi program pencegahan stunting dan gizi buruk khusus untuk ibu hamil dan menyusui.

Kegiatan ini dihadiri oleh 50 ibu hamil dan menyusui dari seluruh RT di desa. Materi sosialisasi meliputi pentingnya gizi seimbang, ASI eksklusif, dan pemantauan tumbuh kembang anak.

Dokter Puskesmas menyampaikan bahwa pencegahan stunting harus dimulai sejak masa kehamilan dengan asupan gizi yang cukup dan pemeriksaan rutin. Program ini juga memberikan suplemen gratis untuk ibu hamil.

Sebagai tindak lanjut, akan dibentuk kader gizi di setiap RT untuk memantau status gizi ibu dan anak. Pemerintah desa juga berkomitmen menyediakan makanan tambahan untuk balita dengan risiko gizi kurang.''',
                'category': 'Kesehatan',
                'tags': ['Stunting', 'Gizi', 'Kesehatan'],
                'status': 'published',
                'priority': 'normal'
            },
            {
                'title': 'Desa Pulosarok Terpilih sebagai Desa Wisata Percontohan Kabupaten',
                'content': '''Desa Pulosarok resmi ditetapkan sebagai Desa Wisata Percontohan tingkat kabupaten berkat potensi alam dan budaya yang dimiliki.

Penetapan ini berdasarkan penilaian terhadap potensi wisata, kesiapan masyarakat, dan komitmen pemerintah desa dalam mengembangkan sektor pariwisata. Desa Pulosarok dinilai memiliki keunggulan dalam wisata alam dan budaya tradisional.

Kepala Desa menyampaikan bahwa status ini merupakan peluang besar untuk meningkatkan ekonomi masyarakat melalui sektor pariwisata. Berbagai persiapan akan dilakukan termasuk pelatihan guide lokal dan penataan objek wisata.

Rencana pengembangan meliputi pembangunan homestay, paket wisata edukasi pertanian, dan festival budaya tahunan. Pemerintah kabupaten berkomitmen memberikan dukungan dana dan pendampingan teknis untuk pengembangan desa wisata.''',
                'category': 'Ekonomi Desa',
                'tags': ['Wisata', 'Pariwisata', 'Ekonomi'],
                'status': 'published',
                'priority': 'high',
                'is_breaking': True
            }
        ]
        
        # Create news articles
        for i, news_item in enumerate(news_data):
            # Find category
            category = NewsCategory.objects.get(name=news_item['category'])
            
            # Create unique slug
            base_slug = slugify(news_item['title'])
            slug = base_slug
            counter = 1
            while News.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            # Create news
            news = News.objects.create(
                title=news_item['title'],
                slug=slug,
                content=news_item['content'],
                category=category,
                status=news_item['status'],
                priority=news_item['priority'],
                is_featured=news_item.get('is_featured', False),
                is_breaking=news_item.get('is_breaking', False),
                author=admin_user,
                published_date=timezone.now() - timedelta(days=random.randint(1, 30)),
                views_count=random.randint(50, 500),
                likes_count=random.randint(5, 50),
                comments_count=random.randint(0, 20),
                shares_count=random.randint(0, 15)
            )
            
            # Add tags
            news_tags = []
            for tag_name in news_item['tags']:
                try:
                    tag = NewsTag.objects.get(name=tag_name)
                    news_tags.append(tag)
                except NewsTag.DoesNotExist:
                    self.stdout.write(f'Tag not found: {tag_name}')
            news.tags.set(news_tags)
            
            self.stdout.write(f'Created news: {news.title}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {len(news_data)} news articles, '
                f'{len(categories)} categories, and {len(tags)} tags'
            )
        )