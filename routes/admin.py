from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, g
from flask_login import login_user, logout_user, login_required, current_user
from db import get_db
from bson import ObjectId
from datetime import datetime
import os, re, uuid
from werkzeug.utils import secure_filename

admin_bp = Blueprint('admin', __name__)

# ── Image field definitions for the Image Manager ──────────────────────────
# Each entry: (section_label, setting_key, field_name, description)
SITE_IMAGE_FIELDS = [
    # Hero Section
    ('hero',    'hero_image_1',         'Hero Main (fullwidth background)',   'Main large hero background image'),
    ('hero',    'hero_image_2',         'Hero Grid Top-Right',                'Mosaic panel – top right'),
    ('hero',    'hero_image_3',         'Hero Grid Bottom-Right',             'Mosaic panel – bottom right'),
    ('hero',    'hero_image_4',         'Hero Bento Photo',                   'Why-choose-us section photo card'),
    # Head Teacher / About
    ('about',   'head_teacher_image',   'Head Teacher Portrait',              'Homepage & About page principal photo'),
    ('about',   'about_banner_image',   'About Page Banner',                  'Full-width banner on About page'),
    ('about',   'mission_image',        'Mission / Vision Section Image',     'Image alongside mission statement'),
    # Academics
    ('academics','academics_banner',    'Academics Page Banner',              'Full-width banner on Academics page'),
    ('academics','cbc_image',           'CBC Section Photo',                  'CBC curriculum visual'),
    # Admissions
    ('admissions','admissions_banner',  'Admissions Page Banner',             'Banner on the Admissions page'),
    ('admissions','admissions_form_img','Apply Section Image',                'Sidebar image on admissions form'),
    # School Life
    ('life',    'life_banner',          'School Life Banner',                 'Banner on School Life page'),
    # Contact
    ('contact', 'contact_banner',       'Contact Page Banner',                'Banner on Contact page'),
    # Footer / Branding
    ('branding','school_logo',          'School Logo',                        'Logo used in navbar & footer'),
    ('branding','og_image',             'Social Share Image (OG)',            'Preview image for social media links'),
]

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# get_db imported from db.py

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_file(file):
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        upload_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'uploads', filename)
        file.save(upload_path)
        return filename
    return None

def resolve_image(file_obj, url_str, existing_file='', existing_url=''):
    """
    Returns (file_filename, url) tuple.
    Priority: new file upload > url field > keep existing.
    """
    if file_obj and file_obj.filename:
        saved = upload_file(file_obj)
        if saved:
            return saved, ''
    if url_str and url_str.strip():
        return '', url_str.strip()
    return existing_file, existing_url

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text

# ── Inject unread counts into admin templates ──────────────────────────────
@admin_bp.before_request
def inject_counts():
    if current_user.is_authenticated:
        db = get_db()
        g.g_inq_count = db.inquiries.count_documents({'status': 'new'})
        g.g_msg_count = db.messages.count_documents({'read': False})

@admin_bp.context_processor
def admin_globals():
    return dict(
        g_inq_count=getattr(g, 'g_inq_count', 0),
        g_msg_count=getattr(g, 'g_msg_count', 0)
    )

# ── LOGIN / LOGOUT ─────────────────────────────────────────────────────────
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    from models.user import User
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.get_by_username(username)
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin.dashboard'))
        flash('Invalid username or password.', 'error')
    return render_template('admin/login.html')

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin.login'))

# ── DASHBOARD ──────────────────────────────────────────────────────────────
@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    stats = {
        'news_count': db.news.count_documents({}),
        'gallery_count': db.gallery.count_documents({}),
        'inq_count': db.inquiries.count_documents({'status': 'new'}),
        'msg_count': db.messages.count_documents({'read': False}),
        'staff_count': db.staff.count_documents({}),
        'events_count': db.events.count_documents({}),
        'newsletter_count': db.newsletter.count_documents({'active': True}),
    }
    recent_inquiries = list(db.inquiries.find().sort('date', -1).limit(5))
    recent_messages = list(db.messages.find().sort('date', -1).limit(5))
    return render_template('admin/dashboard.html', stats=stats,
        recent_inquiries=recent_inquiries, recent_messages=recent_messages)

# ── NEWS ───────────────────────────────────────────────────────────────────
@admin_bp.route('/news')
@login_required
def news():
    db = get_db()
    articles = list(db.news.find().sort('date', -1))
    return render_template('admin/news.html', articles=articles)

@admin_bp.route('/news/new', methods=['GET', 'POST'])
@admin_bp.route('/news/edit/<article_id>', methods=['GET', 'POST'])
@login_required
def news_form(article_id=None):
    db = get_db()
    article = db.news.find_one({'_id': ObjectId(article_id)}) if article_id else None

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        image_file = request.files.get('image')
        image = upload_file(image_file) if image_file and image_file.filename else (article.get('image', '') if article else '')

        data = {
            'title': title,
            'slug': slugify(title),
            'excerpt': request.form.get('excerpt', '').strip(),
            'content': request.form.get('content', '').strip(),
            'category': request.form.get('category', 'News'),
            'author': request.form.get('author', '').strip(),
            'image': image,
            'published': request.form.get('published') in ('on', 'true', '1'),
            'featured': request.form.get('featured') in ('on', 'true', '1'),
            'date': datetime.utcnow(),
        }
        if article_id:
            db.news.update_one({'_id': ObjectId(article_id)}, {'$set': data})
            flash('Article updated successfully.', 'success')
        else:
            data['views'] = 0
            db.news.insert_one(data)
            flash('Article published successfully.', 'success')
        return redirect(url_for('admin.news'))

    return render_template('admin/news_form.html', article=article)

@admin_bp.route('/news/save', methods=['POST'])
@admin_bp.route('/news/save/<id>', methods=['POST'])
@login_required
def save_news(id=None):
    data = request.get_json() or {}
    title = (data.get('title') or '').strip()
    if not title:
        return jsonify({'success': False, 'message': 'Title is required.'})
    payload = {
        'title': title,
        'slug': slugify(title),
        'category': data.get('category', 'News'),
        'excerpt': (data.get('excerpt') or '').strip(),
        'content': (data.get('content') or '').strip(),
        'author': (data.get('author') or '').strip(),
        'image_url': (data.get('image_url') or '').strip(),
        'published': bool(data.get('published')),
        'featured': bool(data.get('featured')),
        'date': datetime.strptime(data['date'], '%Y-%m-%d') if data.get('date') else datetime.utcnow(),
    }
    db = get_db()
    article_id = id or data.get('id')
    if article_id:
        db.news.update_one({'_id': ObjectId(article_id)}, {'$set': payload})
        return jsonify({'success': True, 'message': 'Article updated successfully.'})
    else:
        payload['views'] = 0
        db.news.insert_one(payload)
        return jsonify({'success': True, 'message': 'Article published successfully.'})

@admin_bp.route('/news/delete/<id>', methods=['POST'])
@login_required
def delete_news(id):
    get_db().news.delete_one({'_id': ObjectId(id)})
    return jsonify({'success': True})

# ── GALLERY ────────────────────────────────────────────────────────────────
@admin_bp.route('/gallery')
@login_required
def gallery():
    db = get_db()
    items = list(db.gallery.find().sort('date', -1))
    return render_template('admin/gallery.html', items=items)

@admin_bp.route('/gallery/upload', methods=['POST'])
@login_required
def gallery_upload():
    db = get_db()
    files = request.files.getlist('images')
    category = request.form.get('category', 'General')
    title = request.form.get('title', '').strip()
    image_url = request.form.get('image_url', '').strip()
    featured = request.form.get('featured', 'false') in ('on', 'true', 'True')
    count = 0

    # Handle URL-based image
    if image_url and not any(f.filename for f in files):
        db.gallery.insert_one({
            'title': title or 'Gallery Photo',
            'category': category,
            'image': '',
            'image_url': image_url,
            'description': request.form.get('description', ''),
            'date': datetime.utcnow(),
            'featured': featured
        })
        count = 1
    else:
        for f in files:
            filename = upload_file(f)
            if filename:
                db.gallery.insert_one({
                    'title': title or f.filename,
                    'category': category,
                    'image': filename,
                    'image_url': image_url,
                    'description': request.form.get('description', ''),
                    'date': datetime.utcnow(),
                    'featured': featured
                })
                count += 1

    flash(f'{count} photo(s) added successfully.', 'success')
    return redirect(url_for('admin.gallery'))

@admin_bp.route('/gallery/delete/<id>', methods=['POST'])
@login_required
def delete_gallery(id):
    get_db().gallery.delete_one({'_id': ObjectId(id)})
    return jsonify({'success': True})

# ── EVENTS ─────────────────────────────────────────────────────────────────
@admin_bp.route('/events')
@login_required
def events():
    db = get_db()
    items = list(db.events.find().sort('date', 1))
    return render_template('admin/events.html', events=items)

@admin_bp.route('/events/save', methods=['POST'])
@login_required
def save_event():
    db = get_db()
    event_id = request.form.get('event_id')
    data = {
        'title': request.form.get('title', '').strip(),
        'date': request.form.get('date', ''),
        'end_date': request.form.get('end_date', ''),
        'time': request.form.get('time', '').strip(),
        'venue': request.form.get('venue', '').strip(),
        'category': request.form.get('category', 'event'),
        'description': request.form.get('description', '').strip(),
        'color': request.form.get('color', '#6B1E2E'),
    }
    if event_id:
        db.events.update_one({'_id': ObjectId(event_id)}, {'$set': data})
        flash('Event updated.', 'success')
    else:
        db.events.insert_one(data)
        flash('Event created.', 'success')
    return redirect(url_for('admin.events'))

@admin_bp.route('/events/delete/<id>', methods=['POST'])
@login_required
def delete_event(id):
    get_db().events.delete_one({'_id': ObjectId(id)})
    return jsonify({'success': True})

# ── STAFF ──────────────────────────────────────────────────────────────────
@admin_bp.route('/staff')
@login_required
def staff():
    db = get_db()
    members = list(db.staff.find().sort('order', 1))
    return render_template('admin/staff.html', staff=members)

@admin_bp.route('/staff/save', methods=['POST'])
@login_required
def save_staff():
    db = get_db()
    staff_id = request.form.get('staff_id')
    photo_file = request.files.get('photo')
    photo_url_input = request.form.get('photo_url', '').strip()
    existing = db.staff.find_one({'_id': ObjectId(staff_id)}) if staff_id else {}

    ex_file = existing.get('photo', '') if existing else ''
    ex_url  = existing.get('photo_url', '') if existing else ''
    saved_file, saved_url = resolve_image(photo_file, photo_url_input, ex_file, ex_url)

    data = {
        'name': request.form.get('name', '').strip(),
        'role': request.form.get('role', '').strip(),
        'qualifications': request.form.get('qualifications', '').strip(),
        'bio': request.form.get('bio', '').strip(),
        'photo': saved_file,
        'photo_url': saved_url,
        'featured': request.form.get('featured') in ('true', 'on', '1'),
        'order': int(request.form.get('order') or 99),
    }
    if staff_id:
        db.staff.update_one({'_id': ObjectId(staff_id)}, {'$set': data})
        flash('Staff member updated.', 'success')
    else:
        db.staff.insert_one(data)
        flash('Staff member added.', 'success')
    return redirect(url_for('admin.staff'))

@admin_bp.route('/staff/delete/<id>', methods=['POST'])
@login_required
def delete_staff(id):
    get_db().staff.delete_one({'_id': ObjectId(id)})
    return jsonify({'success': True})

# ── TESTIMONIALS ───────────────────────────────────────────────────────────
@admin_bp.route('/testimonials')
@login_required
def testimonials():
    db = get_db()
    items = list(db.testimonials.find().sort('order', 1))
    return render_template('admin/testimonials.html', testimonials=items)

@admin_bp.route('/testimonials/save', methods=['POST'])
@login_required
def save_testimonial():
    db = get_db()
    tid = request.form.get('testimonial_id')
    published_val = request.form.get('published', 'false')

    photo_file = request.files.get('photo')
    photo_url_input = request.form.get('photo_url', '').strip()
    existing = db.testimonials.find_one({'_id': ObjectId(tid)}) if tid else {}
    ex_file = existing.get('photo', '') if existing else ''
    ex_url  = existing.get('photo_url', '') if existing else ''
    saved_file, saved_url = resolve_image(photo_file, photo_url_input, ex_file, ex_url)

    data = {
        'name': request.form.get('name', '').strip(),
        'role': request.form.get('role', '').strip(),
        'text': request.form.get('text', '').strip(),
        'rating': int(request.form.get('rating') or 5),
        'active': published_val in ('true', 'on', '1'),
        'order': int(request.form.get('order') or 99),
        'photo': saved_file,
        'photo_url': saved_url,
    }
    if tid:
        db.testimonials.update_one({'_id': ObjectId(tid)}, {'$set': data})
        flash('Testimonial updated.', 'success')
    else:
        db.testimonials.insert_one(data)
        flash('Testimonial added.', 'success')
    return redirect(url_for('admin.testimonials'))

@admin_bp.route('/testimonials/delete/<id>', methods=['POST'])
@login_required
def delete_testimonial(id):
    get_db().testimonials.delete_one({'_id': ObjectId(id)})
    return jsonify({'success': True})

# ── ACHIEVEMENTS ───────────────────────────────────────────────────────────
@admin_bp.route('/achievements')
@login_required
def achievements():
    db = get_db()
    items = list(db.achievements.find().sort('order', 1))
    return render_template('admin/achievements.html', achievements=items)

@admin_bp.route('/achievements/save', methods=['POST'])
@login_required
def save_achievement():
    db = get_db()
    aid = request.form.get('achievement_id')
    data = {
        'title': request.form.get('title', '').strip(),
        'year': request.form.get('year', '').strip(),
        'category': request.form.get('category', 'academic'),
        'description': request.form.get('description', '').strip(),
        'icon': request.form.get('icon', 'trophy'),
        'order': int(request.form.get('order') or 99),
    }
    if aid:
        db.achievements.update_one({'_id': ObjectId(aid)}, {'$set': data})
        flash('Achievement updated.', 'success')
    else:
        db.achievements.insert_one(data)
        flash('Achievement added.', 'success')
    return redirect(url_for('admin.achievements'))

@admin_bp.route('/achievements/delete/<id>', methods=['POST'])
@login_required
def delete_achievement(id):
    get_db().achievements.delete_one({'_id': ObjectId(id)})
    return jsonify({'success': True})

# ── CBC STRANDS ────────────────────────────────────────────────────────────
@admin_bp.route('/cbc')
@login_required
def cbc():
    db = get_db()
    strands = list(db.cbc_strands.find().sort('order', 1))
    return render_template('admin/cbc.html', strands=strands)

@admin_bp.route('/cbc/save', methods=['POST'])
@login_required
def save_cbc():
    db = get_db()
    sid = request.form.get('strand_id')
    data = {
        'name': request.form.get('name', '').strip(),
        'grades': request.form.get('grades', '').strip(),
        'description': request.form.get('description', '').strip(),
        'icon': request.form.get('icon', 'bi-journal-bookmark'),
        'order': int(request.form.get('order') or 99),
    }
    if sid:
        db.cbc_strands.update_one({'_id': ObjectId(sid)}, {'$set': data})
        flash('Strand updated.', 'success')
    else:
        db.cbc_strands.insert_one(data)
        flash('Strand added.', 'success')
    return redirect(url_for('admin.cbc'))

@admin_bp.route('/cbc/delete/<id>', methods=['POST'])
@login_required
def delete_cbc(id):
    get_db().cbc_strands.delete_one({'_id': ObjectId(id)})
    return jsonify({'success': True})

# ── FEES ───────────────────────────────────────────────────────────────────
@admin_bp.route('/fees')
@login_required
def fees():
    db = get_db()
    items = list(db.fees.find().sort('order', 1))
    return render_template('admin/fees.html', fees=items)

@admin_bp.route('/fees/save', methods=['POST'])
@login_required
def save_fee():
    db = get_db()
    fid = request.form.get('fee_id')
    def to_num(val):
        try: return float(val) if val and val.strip() else None
        except: return None
    tuition  = to_num(request.form.get('tuition'))
    boarding = to_num(request.form.get('boarding'))
    activity = to_num(request.form.get('activity'))
    total    = to_num(request.form.get('total')) or (
        (tuition or 0) + (boarding or 0) + (activity or 0) or None
    )
    data = {
        'grade':    request.form.get('grade', '').strip(),
        'tuition':  tuition,
        'boarding': boarding,
        'activity': activity,
        'total':    total,
        'notes':    request.form.get('notes', '').strip(),
        'order':    int(request.form.get('order', 99) or 99),
    }
    if fid:
        db.fees.update_one({'_id': ObjectId(fid)}, {'$set': data})
        flash('Fee structure updated.', 'success')
    else:
        db.fees.insert_one(data)
        flash('Fee entry added.', 'success')
    return redirect(url_for('admin.fees'))

@admin_bp.route('/fees/delete/<id>', methods=['POST'])
@login_required
def delete_fee(id):
    get_db().fees.delete_one({'_id': ObjectId(id)})
    return jsonify({'success': True})

# ── FAQS ───────────────────────────────────────────────────────────────────
@admin_bp.route('/faqs')
@login_required
def faqs():
    db = get_db()
    items = list(db.faqs.find().sort('order', 1))
    return render_template('admin/faqs.html', faqs=items)

@admin_bp.route('/faqs/save', methods=['POST'])
@login_required
def save_faq():
    db = get_db()
    fid = request.form.get('faq_id')
    published_val = request.form.get('published', 'true')
    data = {
        'question': request.form.get('question', '').strip(),
        'answer': request.form.get('answer', '').strip(),
        'category': request.form.get('category', 'general'),
        'order': int(request.form.get('order', 99) or 99),
        'published': published_val in ('true', 'on', '1'),
    }
    if fid:
        db.faqs.update_one({'_id': ObjectId(fid)}, {'$set': data})
        flash('FAQ updated.', 'success')
    else:
        db.faqs.insert_one(data)
        flash('FAQ added.', 'success')
    return redirect(url_for('admin.faqs'))

@admin_bp.route('/faqs/delete/<id>', methods=['POST'])
@login_required
def delete_faq(id):
    get_db().faqs.delete_one({'_id': ObjectId(id)})
    return jsonify({'success': True})

# ── INQUIRIES ──────────────────────────────────────────────────────────────
@admin_bp.route('/inquiries')
@login_required
def inquiries():
    db = get_db()
    status_filter = request.args.get('status', '')
    query = {'status': status_filter} if status_filter else {}
    items = list(db.inquiries.find(query).sort('date', -1))
    return render_template('admin/inquiries.html', inquiries=items, status_filter=status_filter)

@admin_bp.route('/inquiries/update/<iid>', methods=['POST'])
@login_required
def update_inquiry(iid):
    status = request.form.get('status', 'reviewed')
    notes = request.form.get('notes', '').strip()
    get_db().inquiries.update_one({'_id': ObjectId(iid)}, {'$set': {'status': status, 'notes': notes}})
    flash('Inquiry updated.', 'success')
    return redirect(url_for('admin.inquiries'))

@admin_bp.route('/inquiries/<iid>/review', methods=['POST'])
@login_required
def review_inquiry(iid):
    """JSON endpoint called by the Mark Reviewed button in inquiries.html"""
    get_db().inquiries.update_one({'_id': ObjectId(iid)}, {'$set': {'status': 'reviewed'}})
    return jsonify({'success': True})

@admin_bp.route('/inquiries/delete/<id>', methods=['POST'])
@login_required
def delete_inquiry(id):
    get_db().inquiries.delete_one({'_id': ObjectId(id)})
    return jsonify({'success': True})

# ── MESSAGES ───────────────────────────────────────────────────────────────
@admin_bp.route('/messages')
@login_required
def messages():
    db = get_db()
    items = list(db.messages.find().sort('date', -1))
    db.messages.update_many({'read': False}, {'$set': {'read': True}})
    return render_template('admin/messages.html', messages=items)

@admin_bp.route('/messages/delete/<id>', methods=['POST'])
@login_required
def delete_message(id):
    get_db().messages.delete_one({'_id': ObjectId(id)})
    return jsonify({'success': True})

# ── NEWSLETTER ─────────────────────────────────────────────────────────────
@admin_bp.route('/newsletter')
@login_required
def newsletter():
    db = get_db()
    subscribers = list(db.newsletter.find({'active': True}).sort('date', -1))
    return render_template('admin/newsletter.html', subscribers=subscribers)

@admin_bp.route('/newsletter/delete/<id>', methods=['POST'])
@login_required
def delete_subscriber(id):
    get_db().newsletter.update_one({'_id': ObjectId(id)}, {'$set': {'active': False}})
    return jsonify({'success': True})

# ── IMAGE MANAGER ──────────────────────────────────────────────────────────
@admin_bp.route('/images')
@login_required
def image_manager():
    db = get_db()
    raw = db.settings.find_one({'key': 'site'}) or {}
    s = {k: v for k, v in raw.items() if k != '_id'}
    from routes.admin import SITE_IMAGE_FIELDS
    sections = {}
    for (sec, key, label, desc) in SITE_IMAGE_FIELDS:
        sections.setdefault(sec, []).append({'key': key, 'label': label, 'desc': desc, 'value': s.get(key, '')})
    return render_template('admin/image_manager.html', sections=sections, settings=s)

@admin_bp.route('/images/save', methods=['POST'])
@login_required
def save_image():
    """Save a single site image — either an uploaded file or a URL."""
    db = get_db()
    field_key = request.form.get('field_key', '').strip()
    if not field_key:
        return jsonify({'success': False, 'message': 'No field key provided.'})

    image_file = request.files.get('image_file')
    image_url  = request.form.get('image_url', '').strip()

    raw = db.settings.find_one({'key': 'site'}) or {}
    existing_file = raw.get(field_key + '_file', '')
    existing_url  = raw.get(field_key, '')

    # If the existing value is a static upload path, treat it as file
    if existing_url.startswith('/static/uploads/'):
        existing_file = existing_url.replace('/static/uploads/', '')
        existing_url = ''

    saved_file, saved_url = resolve_image(image_file, image_url, existing_file, existing_url)

    if saved_file:
        final_val = '/static/uploads/' + saved_file
    elif saved_url:
        final_val = saved_url
    else:
        return jsonify({'success': False, 'message': 'No image provided.'})

    db.settings.update_one({'key': 'site'}, {'$set': {field_key: final_val}}, upsert=True)
    return jsonify({'success': True, 'message': 'Image updated.', 'url': final_val})

@admin_bp.route('/images/clear', methods=['POST'])
@login_required
def clear_image():
    db = get_db()
    field_key = request.form.get('field_key', '').strip()
    if field_key:
        db.settings.update_one({'key': 'site'}, {'$unset': {field_key: ''}})
    return jsonify({'success': True})

# ── SETTINGS ───────────────────────────────────────────────────────────────
@admin_bp.route('/settings')
@login_required
def settings():
    db = get_db()
    raw = db.settings.find_one({'key': 'site'}) or {}
    s = {k: v for k, v in raw.items() if k != '_id'}
    return render_template('admin/settings.html', settings=s)

@admin_bp.route('/settings/save', methods=['POST'])
@login_required
def save_settings():
    db = get_db()
    data = {k: v for k, v in request.form.items() if k not in ['new_password', 'confirm_password']}
    data['maintenance'] = 'maintenance' in request.form
    data['announcement_active'] = 'announcement_active' in request.form
    data['key'] = 'site'

    # Handle image uploads for settings (hero images + branding)
    raw = db.settings.find_one({'key': 'site'}) or {}
    for img_key in ['hero_image_1', 'hero_image_2', 'hero_image_3', 'hero_image_4',
                    'head_teacher_image', 'school_logo', 'og_image',
                    'about_banner_image', 'mission_image', 'academics_banner',
                    'admissions_banner', 'life_banner', 'contact_banner']:
        f = request.files.get(img_key + '_file')
        url = request.form.get(img_key, '').strip()
        existing = raw.get(img_key, '')
        existing_file = existing.replace('/static/uploads/', '') if existing.startswith('/static/uploads/') else ''
        saved_file, saved_url = resolve_image(f, url, existing_file, existing if not existing_file else '')
        if saved_file:
            data[img_key] = '/static/uploads/' + saved_file
        elif saved_url:
            data[img_key] = saved_url
        elif existing:
            data[img_key] = existing  # keep existing

    # Handle password change
    new_pw = request.form.get('new_password', '').strip()
    confirm_pw = request.form.get('confirm_password', '').strip()
    if new_pw:
        if new_pw != confirm_pw:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('admin.settings'))
        from werkzeug.security import generate_password_hash
        db.users.update_one({'username': current_user.username}, {'$set': {'password_hash': generate_password_hash(new_pw)}})
        flash('Password updated successfully.', 'success')

    db.settings.update_one({'key': 'site'}, {'$set': data}, upsert=True)
    flash('Settings saved successfully.', 'success')
    return redirect(url_for('admin.settings'))
