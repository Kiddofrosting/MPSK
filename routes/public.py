from flask import Blueprint, render_template, request, jsonify, redirect, url_for, abort
from db import get_db
from bson import ObjectId
from datetime import datetime, date
import re

public_bp = Blueprint('public', __name__)

def get_settings():
    try:
        raw = get_db().settings.find_one({'key': 'site'}) or {}
        return {k: v for k, v in raw.items() if k != '_id'}
    except Exception:
        return {}

# ── HOME ───────────────────────────────────────────────────────────────────
@public_bp.route('/')
def index():
    db = get_db()
    settings = get_settings()
    if settings.get('maintenance'):
        return render_template('public/503.html'), 503

    news = list(db.news.find({'published': True}).sort('date', -1).limit(3))
    events = list(db.events.find().sort('date', 1).limit(4))
    staff = list(db.staff.find({'featured': True}).sort('order', 1).limit(4))
    testimonials = list(db.testimonials.find({'active': True}).sort('order', 1).limit(3))
    achievements = list(db.achievements.find().sort('order', 1).limit(6))
    gallery = list(db.gallery.find({'featured': True}).sort('date', -1).limit(6))

    return render_template('public/index.html',
        news=news, events=events, staff=staff,
        testimonials=testimonials, achievements=achievements,
        gallery=gallery)

# ── ABOUT ──────────────────────────────────────────────────────────────────
@public_bp.route('/about')
def about():
    db = get_db()
    staff = list(db.staff.find().sort('order', 1))
    testimonials = list(db.testimonials.find({'active': True}).sort('order', 1))
    achievements = list(db.achievements.find().sort('order', 1))
    return render_template('public/about.html',
        staff=staff, testimonials=testimonials, achievements=achievements)

# ── ACADEMICS ─────────────────────────────────────────────────────────────
@public_bp.route('/academics')
def academics():
    db = get_db()
    strands = list(db.cbc_strands.find().sort('order', 1))
    achievements = list(db.achievements.find({'category': 'academic'}).sort('order', 1))
    return render_template('public/academics.html', strands=strands, achievements=achievements)

# ── ADMISSIONS ────────────────────────────────────────────────────────────
@public_bp.route('/admissions')
def admissions():
    db = get_db()
    fees = list(db.fees.find().sort('order', 1))
    faqs = list(db.faqs.find({'category': 'admissions', 'published': True}).sort('order', 1))
    return render_template('public/admissions.html', fees=fees, faqs=faqs)

# ── SCHOOL LIFE ───────────────────────────────────────────────────────────
@public_bp.route('/life')
def life():
    db = get_db()
    gallery = list(db.gallery.find().sort('date', -1).limit(12))
    return render_template('public/life.html', gallery=gallery)

# ── NEWS ──────────────────────────────────────────────────────────────────
@public_bp.route('/news')
def news():
    db = get_db()
    category = request.args.get('category', 'all')
    try:
        page = max(1, int(request.args.get('page', 1) or 1))
    except (ValueError, TypeError):
        page = 1
    per_page = 9

    query = {'published': True}
    if category and category != 'all':
        query['category'] = category

    total = db.news.count_documents(query)
    total_pages = (total + per_page - 1) // per_page
    items = list(db.news.find(query).sort('date', -1).skip((page-1)*per_page).limit(per_page))

    return render_template('public/news.html',
        news=items, category=category,
        page=page, total_pages=total_pages)

@public_bp.route('/news/<slug>')
def news_detail(slug):
    db = get_db()
    article = db.news.find_one({'slug': slug, 'published': True})
    if not article:
        abort(404)
    db.news.update_one({'_id': article['_id']}, {'$inc': {'views': 1}})
    related = list(db.news.find({
        'published': True, 'category': article.get('category'),
        '_id': {'$ne': article['_id']}
    }).sort('date', -1).limit(3))
    return render_template('public/news_detail.html', article=article, related=related)

# ── EVENTS ────────────────────────────────────────────────────────────────
@public_bp.route('/events')
def events():
    db = get_db()
    all_events = list(db.events.find().sort('date', 1))
    today = date.today().strftime('%Y-%m-%d')
    return render_template('public/events.html',
        events=all_events, now_str=today)

# ── GALLERY (standalone page) ─────────────────────────────────────────────
@public_bp.route('/gallery')
def gallery():
    db = get_db()
    cat = request.args.get('category', 'all')
    query = {} if cat == 'all' else {'category': cat}
    items = list(db.gallery.find(query).sort('date', -1))
    cats = db.gallery.distinct('category')
    return render_template('public/gallery.html', gallery=items, category=cat, categories=cats)

# ── CONTACT ───────────────────────────────────────────────────────────────
@public_bp.route('/contact')
def contact():
    return render_template('public/contact.html')

# ── FAQ ───────────────────────────────────────────────────────────────────
@public_bp.route('/faq')
def faq():
    db = get_db()
    faqs = list(db.faqs.find({'published': True}).sort('order', 1))
    return render_template('public/faq.html', faqs=faqs)

# ── PRIVACY POLICY ────────────────────────────────────────────────────────
@public_bp.route('/privacy')
def privacy():
    return render_template('public/privacy.html')

# ══════════════════════════════════════════════════════════════════════════
# API ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════

@public_bp.route('/api/contact', methods=['POST'])
def api_contact():
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip()
    message = (data.get('message') or '').strip()
    subject = (data.get('subject') or '').strip()

    if not name or not email or not message:
        return jsonify({'success': False, 'message': 'Please fill in all required fields.'})
    if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        return jsonify({'success': False, 'message': 'Please enter a valid email address.'})

    db = get_db()
    db.messages.insert_one({
        'name': name, 'email': email,
        'subject': subject, 'message': message,
        'phone': (data.get('phone') or '').strip(),
        'date': datetime.utcnow(), 'read': False
    })
    return jsonify({'success': True, 'message': 'Thank you! Your message has been received. We will respond within 2 business days.'})


@public_bp.route('/api/inquiry', methods=['POST'])
def api_inquiry():
    data = request.get_json() or {}
    required = ['parent_name', 'email', 'child_name', 'grade_applying']
    for field in required:
        if not (data.get(field) or '').strip():
            return jsonify({'success': False, 'message': f'{field.replace("_"," ").title()} is required.'})

    db = get_db()
    db.inquiries.insert_one({
        'parent_name': data.get('parent_name', '').strip(),
        'email': data.get('email', '').strip(),
        'phone': data.get('phone', '').strip(),
        'child_name': data.get('child_name', '').strip(),
        'grade_applying': data.get('grade_applying', '').strip(),
        'message': data.get('message', '').strip(),
        'date': datetime.utcnow(),
        'status': 'new'
    })
    return jsonify({'success': True, 'message': 'Thank you! Your inquiry has been received. Our admissions team will contact you within 3 business days.'})


@public_bp.route('/api/newsletter', methods=['POST'])
def api_newsletter():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    if not email or not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        return jsonify({'success': False, 'message': 'Please enter a valid email address.'})

    db = get_db()
    existing = db.newsletter.find_one({'email': email})
    if existing:
        return jsonify({'success': False, 'message': 'You are already subscribed!'})

    db.newsletter.insert_one({'email': email, 'date': datetime.utcnow(), 'active': True})
    return jsonify({'success': True, 'message': 'Subscribed! Thank you for joining the MPSK community.'})


@public_bp.route('/unsubscribe')
def unsubscribe():
    email = request.args.get('email', '').strip().lower()
    if email:
        get_db().newsletter.update_one({'email': email}, {'$set': {'active': False}})
    return render_template('public/unsubscribe.html', email=email)
