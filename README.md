# MPSK Kabarak — School Website

A full-featured school website with a CMS admin panel, built with Flask and MongoDB.

---

## 🚀 Deploy on Render (Recommended)

### Prerequisites
- A [Render](https://render.com) account (free tier works)
- A MongoDB Atlas cluster ([free at mongodb.com/atlas](https://www.mongodb.com/atlas))

### Step 1 — Set up MongoDB Atlas
1. Create a free cluster on MongoDB Atlas
2. Create a database user (username + password)
3. Under **Network Access**, add `0.0.0.0/0` to allow connections from Render
4. Copy your connection string:
   ```
   mongodb+srv://<user>:<password>@<cluster>.mongodb.net/mpsk_db?retryWrites=true&w=majority
   ```

### Step 2 — Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/mpsk-kabarak.git
git push -u origin main
```

### Step 3 — Create a Web Service on Render
1. Go to [render.com](https://render.com) → **New → Web Service**
2. Connect your GitHub repo
3. Render auto-detects `render.yaml` settings
4. Set these **Environment Variables** in the Render dashboard:
   | Key | Value |
   |-----|-------|
   | `MONGO_URI` | Your MongoDB Atlas connection string |
   | `SECRET_KEY` | A long random string (Render can auto-generate) |
   | `FLASK_ENV` | `production` |
   | `FLASK_DEBUG` | `0` |
5. Click **Create Web Service**

The site will be live at `https://mpsk-kabarak.onrender.com`.

---

## 💻 Local Development

### Requirements
- Python 3.10+
- MongoDB running locally (`mongod`)

### Install & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
python app.py
```

Visit: http://localhost:5000

### Admin Login
- URL: http://localhost:5000/admin
- Username: `admin`
- Password: `Admin@MPSK2024`

**Change the password immediately after first login via Settings.**

### Environment Variables (.env)
```
SECRET_KEY=change-this-to-a-strong-random-key
MONGO_URI=mongodb://localhost:27017/mpsk_db
FLASK_ENV=production
FLASK_DEBUG=0
```

### Project Structure
```
mpsk_kabarak/
├── app.py                  # Flask app factory
├── routes/
│   ├── public.py           # Public website routes
│   └── admin.py            # Admin CMS routes
├── models/
│   └── user.py             # User model
├── templates/
│   ├── public/             # Public-facing pages
│   └── admin/              # Admin panel pages
├── static/
│   ├── css/                # Stylesheets
│   ├── js/                 # JavaScript
│   └── uploads/            # Uploaded images
└── utils/
    └── db_seed.py          # Database seed data
```

### Pages
| URL | Description |
|-----|-------------|
| / | Homepage |
| /about | About MPSK |
| /academics | CBC curriculum |
| /admissions | Admissions + fees + inquiry form |
| /life | School life & gallery |
| /news | News & blog |
| /events | School events |
| /gallery | Photo gallery |
| /contact | Contact page |
| /faq | FAQs |
| /privacy | Privacy policy |
| /admin | Admin CMS |
