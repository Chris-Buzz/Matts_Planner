# Matt's Planner - Task Tracker & Shopping List

A Flask-based task management and shopping list application with email notifications, built for modern web deployment.

## Features

- ✅ Task Management with priorities and categories
- 🛒 Shopping List functionality
- 📧 Email notifications and reminders
- 🌓 Dark/Light theme toggle
- 📱 Responsive design
- 👤 User authentication and accounts

## Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd "Matts Planner"
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the app**
   Open your browser to `http://localhost:5000`

## Deploy to Vercel

### Prerequisites
- A [Vercel account](https://vercel.com/signup)
- Vercel CLI (optional): `npm install -g vercel`

### Deployment Steps

#### Option 1: Deploy via Vercel Dashboard (Recommended)

1. **Push your code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Import to Vercel**
   - Go to [vercel.com/new](https://vercel.com/new)
   - Import your GitHub repository
   - Vercel will automatically detect the Flask app

3. **Configure Environment Variables**
   In Vercel Dashboard → Settings → Environment Variables, add:
   - `SECRET_KEY`: Generate a random string (use `python -c "import secrets; print(secrets.token_hex(32))"`)
   - `FLASK_ENV`: Set to `production`
   - Optional email variables if you want notifications:
     - `MAIL_USERNAME`
     - `MAIL_PASSWORD`
     - `MAIL_SERVER`
     - `MAIL_PORT`

4. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete
   - Your app will be live at `https://your-project.vercel.app`

#### Option 2: Deploy via CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
vercel

# Follow the prompts and set environment variables when asked
```

### Important Notes for Vercel Deployment

⚠️ **Database Consideration**: 
- SQLite is not persistent on Vercel (serverless environment)
- For production, consider using:
  - **Vercel Postgres** (recommended)
  - **PlanetScale** (MySQL)
  - **Supabase** (PostgreSQL)
  - **MongoDB Atlas**

To use Vercel Postgres:
1. Enable it in your Vercel project
2. Copy the `DATABASE_URL` from Vercel
3. Update `DATABASE_URL` environment variable
4. Update `requirements.txt` to use `psycopg2-binary` for PostgreSQL

⚠️ **Background Tasks**:
- The email scheduler is disabled on Vercel (serverless)
- For background tasks, consider:
  - **Vercel Cron Jobs** (scheduled functions)
  - **External services** like AWS Lambda, Railway, or Render

### Update Database URL for PostgreSQL

If using PostgreSQL, update your `requirements.txt`:

```txt
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Mail==0.9.1
APScheduler==3.10.4
Werkzeug==3.0.1
email-validator==2.1.0
psycopg2-binary==2.9.9
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Flask secret key for sessions | Yes |
| `FLASK_ENV` | Flask environment (`production` or `development`) | Yes |
| `DATABASE_URL` | Database connection string | No (defaults to SQLite) |
| `MAIL_SERVER` | SMTP server for emails | No |
| `MAIL_PORT` | SMTP port | No |
| `MAIL_USE_TLS` | Use TLS for email | No |
| `MAIL_USERNAME` | Email username | No |
| `MAIL_PASSWORD` | Email password | No |

## Project Structure

```
Matts Planner/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── vercel.json           # Vercel configuration
├── .vercelignore         # Files to ignore during deployment
├── static/               # Static files (CSS, JS)
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── theme.js
│       ├── auth.js
│       └── dashboard.js
├── templates/            # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   └── shopping_list.html
└── instance/            # Instance folder (SQLite DB)
    └── tasks.db
```

## Security Best Practices

1. **Never commit** `.env` file or real credentials
2. **Always use** environment variables for sensitive data
3. **Generate a strong** `SECRET_KEY` for production
4. **Use HTTPS** (automatic with Vercel)
5. **Enable rate limiting** for authentication endpoints (future enhancement)

## Troubleshooting

### Issue: Database doesn't persist on Vercel
- **Solution**: Migrate to Vercel Postgres or another cloud database

### Issue: Email notifications not working
- **Solution**: Ensure all `MAIL_*` environment variables are set correctly

### Issue: 500 Internal Server Error
- **Solution**: Check Vercel function logs for detailed error messages

## Support

For issues or questions, please open an issue in the repository.

## License

This project is licensed under the MIT License.
