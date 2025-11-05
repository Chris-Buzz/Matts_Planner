# Supabase Setup Guide

## Quick Setup (5 minutes)

### 1. Create Supabase Project
1. Go to [supabase.com](https://supabase.com) and sign in/sign up
2. Click **"New Project"**
3. Choose your organization
4. Enter:
   - **Name**: Matts Planner
   - **Database Password**: (create a strong password - SAVE THIS!)
   - **Region**: Choose closest to your users
5. Click **"Create new project"** (takes ~2 minutes)

### 2. Get Database Connection String
1. In your Supabase dashboard, go to:
   **Project Settings** (gear icon) → **Database** → **Connection String**
2. Select **URI** tab
3. Copy the connection string (looks like):
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.abcdefghijk.supabase.co:5432/postgres
   ```
4. Replace `[YOUR-PASSWORD]` with the password you created in step 1

### 3. Update Your .env File
Replace the DATABASE_URL in your `.env` file with your Supabase connection string:
```
DATABASE_URL=postgresql://postgres:your-actual-password@db.xxxxx.supabase.co:5432/postgres
```

### 4. Update Vercel Environment Variables
1. Go to your Vercel dashboard
2. Select your project
3. Go to **Settings** → **Environment Variables**
4. Add/Update:
   ```
   DATABASE_URL = [paste your Supabase connection string]
   SECRET_KEY = 9b8d4c0bee465e6bc2f155ca6a374a2e3e2964709c328a2cdd7587e8258b1643
   VERCEL = 1
   ```
5. Click **Save**

### 5. Install PostgreSQL Adapter Locally (Optional - for local testing)
```bash
pip install psycopg2-binary
```

### 6. Deploy
```bash
git add .
git commit -m "Add Supabase PostgreSQL support"
git push
```

Vercel will auto-deploy with your new database!

## Testing Locally with Supabase

1. Make sure your `.env` has the Supabase DATABASE_URL
2. Run the app:
   ```bash
   python app.py
   ```
3. The app will automatically create tables in Supabase on first run

## Features

✅ **Persistent Data** - Your data won't reset on deployments
✅ **Automatic Backups** - Supabase handles backups
✅ **Real-time Dashboard** - View your database in Supabase dashboard
✅ **Free Tier** - 500MB database, 2GB bandwidth/month
✅ **Scalable** - Easy to upgrade as you grow

## Supabase Dashboard Features

- **Table Editor**: View/edit your data directly
- **SQL Editor**: Run custom queries
- **Database Backups**: Automatic daily backups
- **Logs**: Monitor database activity

## Troubleshooting

### "Connection refused" error
- Check your password in DATABASE_URL
- Verify project is fully initialized (takes ~2 minutes)
- Make sure you're using the correct region endpoint

### Tables not created
- The app creates tables on first request (`@app.before_request`)
- Just visit any page and tables will be created automatically

### Need to reset database
1. Go to Supabase Dashboard → SQL Editor
2. Run:
   ```sql
   DROP TABLE IF EXISTS shopping_item, task, user CASCADE;
   ```
3. Restart your app to recreate tables

## Support
- Supabase Docs: https://supabase.com/docs
- Supabase Discord: https://discord.supabase.com
