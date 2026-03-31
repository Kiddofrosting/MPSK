from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta


def seed_database(db):
    """
    Seeds the database with initial data if collections are empty.
    No images are seeded — upload them via the admin panel.
    """

    if db is None:
        raise RuntimeError("mongo.db is None — MONGO_URI is not set or is invalid.")

    db.client.admin.command('ping')

    # ── Admin user ────────────────────────────────────────────────────────
    if db.users.count_documents({}) == 0:
        db.users.insert_one({
            'username':      'admin',
            'email':         'admin@mpsk.ac.ke',
            'password_hash': generate_password_hash('Admin@MPSK2024'),
            'full_name':     'School Administrator',
            'role':          'superadmin',
        })
        print("✅ Admin user created  |  username: admin  |  password: Admin@MPSK2024")

    # ── Site settings (no images) ─────────────────────────────────────────
    if db.settings.count_documents({}) == 0:
        db.settings.insert_one({
            'key':            'site',
            'school_name':    'Moi Primary & Junior School, Kabarak',
            'short_name':     'MPSK',
            'tagline':        'Nurturing Excellence. Rooted in Faith.',
            'founded':        '1991',
            'phone':          '+254 727 733 113',
            'email':          'info@mpsk.ac.ke',
            'address':        'P.O. Box 20, Kabarak, Nakuru County',
            'location':       'Along Nakuru-Eldama Ravine Highway, 20km from Nakuru',
            'mpesa_paybill':  '123456',
            'mpesa_account':  'Admission Number',
            'whatsapp':       '254727733113',
            'facebook':       'https://www.facebook.com/KABU0727733113',
            'google_maps':    'https://maps.app.goo.gl/MfeNaMXwbWo4RyWV7',
            'lat':            '-0.160579',
            'lng':            '35.9624696',
            'head_teacher':   'Mr. John Kamau',
            'head_teacher_message': (
                'Welcome to Moi Primary & Junior School Kabarak. Our institution stands '
                'on a foundation of academic excellence, Christian values, and holistic '
                'child development. We are committed to nurturing every learner under the '
                'Competence Based Curriculum to become a responsible, creative, and '
                'productive citizen. I warmly invite you to join our school family.'
            ),
            'vision':   'To be an excellent centre of academic knowledge and spiritual growth in Kenya.',
            'mission':  'To provide quality, holistic education grounded in Christian values, nurturing every learner to achieve their full potential.',
            'motto':    'Excellence Through Faith',
            'hero_title': 'Where Excellence\nMeets Faith',
            'hero_text':  'A premier Christian school offering CBC education from PP1 to Grade 9, nestled in the serene Kabarak University campus.',
            'stats_students':   '800+',
            'stats_teachers':   '45+',
            'stats_years':      '30+',
            'stats_pass_rate':  '100%',
            'newsletter_intro': 'Stay updated with school news, events, and announcements.',
            'current_term':     'Term 2 2025',
            'admissions_open':  'true',
        })
        print("✅ Site settings seeded (no images)")

    # ── News ──────────────────────────────────────────────────────────────
    if db.news.count_documents({}) == 0:
        db.news.insert_many([
            {
                'title':    'Grade 9 Students Excel in CBC Final Assessments',
                'slug':     'grade-9-cbc-assessments-2024',
                'excerpt':  'Our inaugural Grade 9 class demonstrated outstanding performance with a 100% pass rate.',
                'content':  'We are proud to announce that our Grade 9 students have achieved exceptional results in the CBC final assessments. Every single student passed, with 78% achieving distinction-level performance.',
                'image': '', 'image_url': '',
                'category': 'Academics', 'author': 'School Administration',
                'date': datetime.utcnow() - timedelta(days=5),
                'published': True, 'featured': True, 'views': 0,
            },
            {
                'title':    'Annual Sports Day 2025 — A Spectacular Success',
                'slug':     'sports-day-2025',
                'excerpt':  'The 2025 Sports Day was a vibrant celebration of athleticism, teamwork, and school spirit.',
                'content':  'The MPSK Annual Sports Day 2025 brought together students, parents, teachers, and the Kabarak community for a day of exciting athletic competitions.',
                'image': '', 'image_url': '',
                'category': 'Sports', 'author': 'Sports Department',
                'date': datetime.utcnow() - timedelta(days=12),
                'published': True, 'featured': True, 'views': 0,
            },
            {
                'title':    'New Science Laboratory Officially Opened',
                'slug':     'new-science-lab-opened',
                'excerpt':  'MPSK unveils a state-of-the-art science laboratory for Grades 4–9.',
                'content':  'We are delighted to announce the official opening of our new Science and Technology Laboratory, equipped with cutting-edge apparatus to support hands-on CBC learning.',
                'image': '', 'image_url': '',
                'category': 'Infrastructure', 'author': 'School Administration',
                'date': datetime.utcnow() - timedelta(days=20),
                'published': True, 'featured': False, 'views': 0,
            },
        ])
        print("✅ News seeded (no images)")

    # ── Events ────────────────────────────────────────────────────────────
    if db.events.count_documents({}) == 0:
        db.events.insert_many([
            {'title': 'Term 2 Opening',   'date': '2026-04-27', 'end_date': '2026-04-27', 'category': 'term',  'description': 'Term 2 commences. All students to report by 8:00 AM.',            'color': '#1A5E38'},
            {'title': 'Open Day',         'date': '2026-05-15', 'end_date': '2026-05-15', 'category': 'event', 'description': 'Annual Open Day — prospective parents welcome. Tours from 9 AM.',  'color': '#1A6E8E'},
            {'title': 'Mid-Term Break',   'date': '2026-05-29', 'end_date': '2026-05-31', 'category': 'break', 'description': 'Mid-term break for all students.',                                 'color': '#8E6B1A'},
            {'title': 'Sports Day',       'date': '2026-06-12', 'end_date': '2026-06-12', 'category': 'event', 'description': 'Annual Sports Day at the school grounds. Parents welcome from 9 AM.','color': '#C25A2A'},
            {'title': 'Term 2 Closing',   'date': '2026-08-07', 'end_date': '2026-08-07', 'category': 'term',  'description': 'Term 2 ends. Report cards issued at 2:00 PM.',                    'color': '#1A5E38'},
            {'title': 'Term 3 Opening',   'date': '2026-09-07', 'end_date': '2026-09-07', 'category': 'term',  'description': 'Term 3 commences.',                                                'color': '#1A5E38'},
            {'title': 'Prize Giving Day', 'date': '2026-11-13', 'end_date': '2026-11-13', 'category': 'event', 'description': 'Annual Prize Giving Ceremony. All parents and guardians invited.',   'color': '#5A1A8E'},
            {'title': 'Term 3 Closing',   'date': '2026-11-27', 'end_date': '2026-11-27', 'category': 'term',  'description': 'End of Year. Term 3 closes. Report cards distributed.',             'color': '#1A5E38'},
        ])
        print("✅ Events seeded")

    # ── Achievements ──────────────────────────────────────────────────────
    if db.achievements.count_documents({}) == 0:
        db.achievements.insert_many([
            {'title': '100% CBC Pass Rate',          'year': '2024', 'category': 'academic',    'description': 'Every Grade 9 student passed CBC assessments',             'icon': 'bi-trophy',            'order': 1},
            {'title': 'County Music Champions',       'year': '2024', 'category': 'arts',        'description': '1st position, Nakuru County Music Festival',               'icon': 'bi-music-note-beamed', 'order': 2},
            {'title': 'National Science Finalists',   'year': '2024', 'category': 'academic',    'description': 'Grade 8 project selected for national science fair',       'icon': 'bi-flask',             'order': 3},
            {'title': 'Best Environmental School',    'year': '2023', 'category': 'environment', 'description': 'Nakuru County Environmental Award for Green Campus',        'icon': 'bi-tree-fill',         'order': 4},
            {'title': 'Regional Athletics Champions', 'year': '2024', 'category': 'sports',      'description': '1st overall, Rift Valley Regional Athletics Championship', 'icon': 'bi-award',             'order': 5},
            {'title': 'Digital Learning Pioneer',     'year': '2024', 'category': 'academic',    'description': 'Recognised by Ministry of Education for CBC integration',  'icon': 'bi-laptop',            'order': 6},
        ])
        print("✅ Achievements seeded")

    # ── Staff (no photos) ─────────────────────────────────────────────────
    if db.staff.count_documents({}) == 0:
        db.staff.insert_many([
            {'name': 'Mr. John Kamau',     'role': 'Head Teacher',        'department': 'Leadership',     'qualifications': 'M.Ed Educational Administration, Kenyatta University', 'bio': 'Over 20 years in education leadership.',          'photo': '', 'photo_url': '', 'order': 1, 'featured': True},
            {'name': 'Mrs. Grace Mutua',   'role': 'Deputy Head Teacher',  'department': 'Leadership',    'qualifications': 'B.Ed, University of Nairobi',                            'bio': 'Specialist in early childhood education.',         'photo': '', 'photo_url': '', 'order': 2, 'featured': True},
            {'name': 'Mr. Peter Ochieng',  'role': 'Head of Academics',   'department': 'Academics',     'qualifications': 'B.Sc Mathematics, Egerton University',                   'bio': 'Mathematics specialist with 15 years experience.',  'photo': '', 'photo_url': '', 'order': 3, 'featured': True},
            {'name': 'Ms. Faith Njeri',    'role': 'Head of Sciences',    'department': 'Academics',     'qualifications': 'B.Sc Biology, Moi University',                           'bio': 'Passionate science educator and CBC facilitator.',   'photo': '', 'photo_url': '', 'order': 4, 'featured': True},
            {'name': 'Mr. Daniel Rotich',  'role': 'Sports Director',     'department': 'Co-curricular', 'qualifications': 'Diploma Physical Education, KIE',                        'bio': 'Former national athlete, coaching champions.',       'photo': '', 'photo_url': '', 'order': 5, 'featured': True},
            {'name': 'Mrs. Susan Wanjiku', 'role': 'Head of Boarding',    'department': 'Boarding',      'qualifications': 'B.Ed Guidance & Counselling, Daystar University',        'bio': 'Ensures a safe, nurturing boarding environment.',    'photo': '', 'photo_url': '', 'order': 6, 'featured': True},
        ])
        print("✅ Staff seeded (no photos)")

    # ── Testimonials (no photos) ──────────────────────────────────────────
    if db.testimonials.count_documents({}) == 0:
        db.testimonials.insert_many([
            {'name': 'Mrs. Achieng Odhiambo', 'role': 'Parent — Grade 6',         'text': 'MPSK has transformed my daughter. The CBC approach here is exceptional — she now loves science and art equally.',               'rating': 5, 'active': True, 'order': 1, 'photo': '', 'photo_url': ''},
            {'name': 'Mr. James Kariuki',     'role': 'Parent — Grade 9 Boarder', 'text': 'I was nervous about boarding but MPSK is wonderful. My son has become independent, disciplined, and made lifelong friends.',     'rating': 5, 'active': True, 'order': 2, 'photo': '', 'photo_url': ''},
            {'name': 'Dr. Wanjiru Mwangi',    'role': 'Alumna — Class of 2018',   'text': 'MPSK gave me the academic and spiritual foundation that propelled me to medical school.',                                        'rating': 5, 'active': True, 'order': 3, 'photo': '', 'photo_url': ''},
            {'name': 'Mr. Samuel Bett',       'role': 'Parent — PP2 & Grade 4',   'text': 'We have two children at MPSK and both are thriving. Great communication, excellent facilities, and values that align perfectly.', 'rating': 5, 'active': True, 'order': 4, 'photo': '', 'photo_url': ''},
        ])
        print("✅ Testimonials seeded (no photos)")

    # ── FAQs ──────────────────────────────────────────────────────────────
    if db.faqs.count_documents({}) == 0:
        db.faqs.insert_many([
            {'question': 'What grades does MPSK offer?',               'answer': 'We offer education from Pre-Primary 1 (PP1) through to Grade 9, covering all CBC levels.',                                            'category': 'general',    'order': 1, 'published': True},
            {'question': 'What are the school fees?',                  'answer': 'Fees vary by grade level and day/boarding option. Visit our Admissions page or call +254 727 733 113.',                               'category': 'fees',       'order': 2, 'published': True},
            {'question': 'How do I pay fees via M-Pesa?',              'answer': "Go to M-Pesa → Lipa na M-Pesa → Paybill → Enter 123456 → Account: child's Admission No. → Enter amount → Confirm.",                 'category': 'fees',       'order': 3, 'published': True},
            {'question': 'Is MPSK a boarding school?',                 'answer': 'Yes. We offer day and full boarding from Grade 4, with supervised study time, meals, and a safe Christian environment.',              'category': 'boarding',   'order': 4, 'published': True},
            {'question': 'What is the admissions process?',            'answer': 'Apply online or visit the office. Bring birth certificate, previous school reports, and passport photos. Assessments required for Grade 4+.', 'category': 'admissions', 'order': 5, 'published': True},
            {'question': 'What is the CBC curriculum?',                'answer': 'CBC focuses on practical, hands-on learning and 7 core competencies including communication, critical thinking, and creativity.',     'category': 'academics',  'order': 6, 'published': True},
            {'question': 'Does the school provide transport?',         'answer': 'Yes. We run buses along select routes in Nakuru. Contact the office for current routes and fees.',                                     'category': 'general',    'order': 7, 'published': True},
            {'question': 'What co-curricular activities are offered?', 'answer': 'Athletics, Football, Basketball, Volleyball, Music, Drama, Scouts, Girl Guides, Chess, Debate, Environmental Club, and Christian Union.', 'category': 'general',  'order': 8, 'published': True},
        ])
        print("✅ FAQs seeded")

    # ── Fee structure ─────────────────────────────────────────────────────
    if db.fees.count_documents({}) == 0:
        db.fees.insert_many([
            {'grade': 'PP1 – PP2',    'tuition': 8000,  'boarding': None,  'activity': 1500, 'total': 9500,  'notes': 'Boarding not available at pre-primary level',       'order': 1},
            {'grade': 'Grade 1 – 3', 'tuition': 10000, 'boarding': None,  'activity': 1500, 'total': 11500, 'notes': 'Boarding not available at lower primary level',      'order': 2},
            {'grade': 'Grade 4 – 6', 'tuition': 13000, 'boarding': 20000, 'activity': 2000, 'total': 35000, 'notes': 'Boarding includes accommodation, meals & laundry',   'order': 3},
            {'grade': 'Grade 7 – 9', 'tuition': 16000, 'boarding': 24000, 'activity': 2500, 'total': 42500, 'notes': 'Includes science lab fee and digital learning levy', 'order': 4},
        ])
        print("✅ Fee structure seeded")

    # ── CBC strands ───────────────────────────────────────────────────────
    if db.cbc_strands.count_documents({}) == 0:
        db.cbc_strands.insert_many([
            {'name': 'Literacy',               'icon': 'bi-book-half',  'color': '#1A5E38', 'description': 'Reading, writing, and communication in English and Kiswahili',       'grades': 'PP1 – Grade 9',    'order': 1},
            {'name': 'Numeracy & Mathematics', 'icon': 'bi-calculator', 'color': '#1A6E8E', 'description': 'Number sense, algebra, geometry, and data analysis',                 'grades': 'PP1 – Grade 9',    'order': 2},
            {'name': 'Science & Technology',   'icon': 'bi-flask',      'color': '#8E6B1A', 'description': 'Inquiry-based biology, chemistry, physics, and ICT',                 'grades': 'Grade 4 – Grade 9','order': 3},
            {'name': 'Creative Arts & Sports', 'icon': 'bi-palette2',   'color': '#5A1A8E', 'description': 'Visual arts, music, physical education, and performance',            'grades': 'PP1 – Grade 9',    'order': 4},
            {'name': 'Social Studies & CRE',   'icon': 'bi-globe',      'color': '#C25A2A', 'description': 'History, geography, citizenship, and Christian Religious Education',  'grades': 'PP1 – Grade 9',    'order': 5},
            {'name': 'Agriculture & Nutrition','icon': 'bi-tree-fill',  'color': '#2A6B10', 'description': 'Practical farming, nutrition, and environmental stewardship',        'grades': 'Grade 4 – Grade 9','order': 6},
        ])
        print("✅ CBC strands seeded")

    # ── Gallery starts empty ──────────────────────────────────────────────
    # Add photos via Admin → Gallery

    print("✅ Database ready. Upload images via Admin → Image Manager & Gallery.")
