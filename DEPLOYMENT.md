# Vercel Deployment Checklist

## Pre-Deployment

- [ ] Push code to GitHub repository
- [ ] Generate SECRET_KEY using `python generate_secret_key.py`
- [ ] Review and update `.env.example` with any new variables
- [ ] Test locally with production settings: `FLASK_ENV=production python app.py`
- [ ] Ensure all sensitive data is in environment variables, not hardcoded

## Vercel Setup

- [ ] Create Vercel account at https://vercel.com
- [ ] Install Vercel CLI (optional): `npm install -g vercel`
- [ ] Import project from GitHub
- [ ] Configure environment variables in Vercel dashboard:
  - [ ] `SECRET_KEY` (required)
  - [ ] `FLASK_ENV=production` (required)
  - [ ] `DATABASE_URL` (if using external database)
  - [ ] `MAIL_SERVER` (optional, for email notifications)
  - [ ] `MAIL_PORT` (optional)
  - [ ] `MAIL_USE_TLS` (optional)
  - [ ] `MAIL_USERNAME` (optional)
  - [ ] `MAIL_PASSWORD` (optional)

## Post-Deployment

- [ ] Test user registration
- [ ] Test user login
- [ ] Test task creation and management
- [ ] Test shopping list functionality
- [ ] Test theme toggle
- [ ] Test on mobile devices
- [ ] Verify HTTPS is working
- [ ] Check Vercel function logs for errors

## Database Migration (if using cloud database)

If using Vercel Postgres, PlanetScale, or another cloud database:

1. [ ] Set up cloud database
2. [ ] Get connection string (DATABASE_URL)
3. [ ] Add to Vercel environment variables
4. [ ] Update `requirements.txt` to include database driver:
   - PostgreSQL: `psycopg2-binary==2.9.9`
   - MySQL: `PyMySQL==1.1.0`
5. [ ] Redeploy

## Optional Enhancements

- [ ] Set up custom domain in Vercel
- [ ] Configure analytics (Vercel Analytics)
- [ ] Set up monitoring/logging service
- [ ] Add rate limiting for security
- [ ] Set up Vercel Cron Jobs for scheduled tasks
- [ ] Add database backups

## Common Issues & Solutions

### SQLite doesn't persist
**Problem**: Data disappears after deployment
**Solution**: Migrate to Vercel Postgres or external database

### Email notifications not working
**Problem**: Emails not being sent
**Solution**: Verify all MAIL_* environment variables are correct

### 500 Error
**Problem**: Application crashes
**Solution**: Check Vercel function logs for detailed error

### Static files not loading
**Problem**: CSS/JS not working
**Solution**: Ensure static files are in `/static` directory and paths use `url_for()`

## Support Resources

- Vercel Documentation: https://vercel.com/docs
- Flask Documentation: https://flask.palletsprojects.com/
- Vercel Postgres: https://vercel.com/docs/storage/vercel-postgres
