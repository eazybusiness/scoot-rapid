# Render.com Deployment Guide - ScootRapid (FREE TIER)

## Prerequisites
- GitHub account connected to Render.com
- Repository: https://github.com/eazybusiness/scoot-rapid
- **NO payment information required** - 100% Free Tier

## Free Tier Deployment Steps

### Step 1: Create MySQL Database

1. Go to Render Dashboard
2. Click "New +" → "MySQL"
3. Configure:
   - Name: `scoot-rapid-db`
   - Database: `scoot_rapid`
   - User: `scooter_user`
   - Region: Choose closest to you
   - Plan: Free
4. Click "Create Database"
5. Copy the "Internal Database URL"

### Step 2: Create Web Service

1. Click "New +" → "Web Service"
2. Connect GitHub repository: `eazybusiness/scoot-rapid`
3. Configure:
   - Name: `scoot-rapid`
   - Region: Same as database
   - Branch: `main`
   - Root Directory: (leave empty)
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn -w 4 -b 0.0.0.0:$PORT wsgi:app`
   - Plan: Free

### Step 3: Environment Variables

Add these environment variables in Render dashboard (Settings → Environment):

**IMPORTANT**: Use the **Internal Database URL** from Step 1!

```
FLASK_APP=wsgi.py
FLASK_ENV=production
SECRET_KEY=your-secret-key-here-change-this
SQLALCHEMY_DATABASE_URI=<PASTE-INTERNAL-DATABASE-URL-HERE>
BASE_PRICE_PER_MINUTE=0.30
START_FEE=1.50
PYTHON_VERSION=3.11.0
```

**To generate secure keys**, use Python:
```python
import secrets
print(secrets.token_urlsafe(32))
```

### Step 4: Deploy

1. Click "Create Web Service"
2. Wait for initial deployment
3. Check logs for any errors

## Post-Deployment

### Initialize Database

The database tables will be created automatically on first run using `db.create_all()`.

### Create Admin User

Connect to your service shell:

```bash
# In Render dashboard, go to Shell tab
flask create-admin
```

Or use Python directly:

```python
from app import create_app, db
from app.models import User

app = create_app('production')
with app.app_context():
    admin = User(
        email='admin@scootrapid.com',
        first_name='Admin',
        last_name='User',
        role='admin'
    )
    admin.set_password('SecurePassword123!')
    db.session.add(admin)
    db.session.commit()
```

## Access Your Application

Your app will be available at:
```
https://scoot-rapid.onrender.com
```

API Endpoints:
```
https://scoot-rapid.onrender.com/api/scooters
https://scoot-rapid.onrender.com/api/rentals
```

## Monitoring

- **Logs**: Available in Render dashboard
- **Metrics**: CPU, Memory usage in dashboard
- **Health Check**: Automatic by Render

## Troubleshooting

### Database Connection Issues
- Verify SQLALCHEMY_DATABASE_URI is set correctly
- Check database is in same region as web service
- Ensure internal database URL is used (not external)
- MySQL URL format: `mysql+pymysql://user:pass@host:port/dbname`

### Application Won't Start
- Check logs in Render dashboard
- Verify all environment variables are set
- Check requirements.txt includes PyMySQL

### Migrations
If you need to run migrations:
```bash
flask db upgrade
```

## Free Tier Limitations

- **Database**: 1GB storage, expires after 90 days
- **Web Service**: 750 hours/month, sleeps after 15 min inactivity
- **Cold Start**: ~30 seconds when waking from sleep

## Updating

Push to GitHub `main` branch:
```bash
git push origin main
```

Render will automatically redeploy.

## Support

- Render Docs: https://render.com/docs
- Community: https://community.render.com
