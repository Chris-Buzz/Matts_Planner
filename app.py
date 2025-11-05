from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps
import os

# Import scheduler only if not in serverless environment
try:
    from apscheduler.schedulers.background import BackgroundScheduler
    SCHEDULER_AVAILABLE = True
except ImportError:
    SCHEDULER_AVAILABLE = False

app = Flask(__name__)

# Configuration - use environment variables for production
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Database configuration - fix postgres:// to postgresql:// for SQLAlchemy
database_url = os.environ.get('DATABASE_URL', 'sqlite:///tasks.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email configuration
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')

db = SQLAlchemy(app)
mail = Mail(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tasks = db.relationship('Task', backref='user', lazy=True, cascade='all, delete-orphan')
    shopping_items = db.relationship('ShoppingItem', backref='user', lazy=True, cascade='all, delete-orphan')

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), default='personal')
    due_date = db.Column(db.DateTime, nullable=False)
    priority = db.Column(db.String(20), default='medium')
    status = db.Column(db.String(20), default='pending')
    notification_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ShoppingItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_name = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.String(50), default='1')
    category = db.Column(db.String(50), default='other')
    is_purchased = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'message': 'Username already exists'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'success': False, 'message': 'Email already exists'}), 400
        
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Registration successful'})
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return jsonify({'success': True, 'message': 'Login successful'})
        
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=session.get('username'))

# Task API Routes
@app.route('/api/tasks', methods=['GET'])
@login_required
def get_tasks():
    user_id = session['user_id']
    view = request.args.get('view', 'all')
    
    query = Task.query.filter_by(user_id=user_id)
    
    if view == 'today':
        today = datetime.now().date()
        query = query.filter(db.func.date(Task.due_date) == today)
    elif view == 'week':
        today = datetime.now().date()
        week_end = today + timedelta(days=7)
        query = query.filter(Task.due_date >= today, Task.due_date <= week_end)
    elif view == 'completed':
        query = query.filter_by(status='completed')
    elif view == 'pending':
        query = query.filter_by(status='pending')
    
    tasks = query.order_by(Task.due_date.asc()).all()
    
    return jsonify([{
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'category': task.category,
        'due_date': task.due_date.isoformat(),
        'priority': task.priority,
        'status': task.status
    } for task in tasks])

@app.route('/api/tasks', methods=['POST'])
@login_required
def create_task():
    data = request.get_json()
    
    new_task = Task(
        user_id=session['user_id'],
        title=data['title'],
        description=data.get('description', ''),
        category=data.get('category', 'personal'),
        due_date=datetime.fromisoformat(data['due_date']),
        priority=data.get('priority', 'medium'),
        status='pending'
    )
    
    db.session.add(new_task)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Task created successfully',
        'task': {
            'id': new_task.id,
            'title': new_task.title,
            'description': new_task.description,
            'category': new_task.category,
            'due_date': new_task.due_date.isoformat(),
            'priority': new_task.priority,
            'status': new_task.status
        }
    })

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first()
    
    if not task:
        return jsonify({'success': False, 'message': 'Task not found'}), 404
    
    data = request.get_json()
    
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.category = data.get('category', task.category)
    task.priority = data.get('priority', task.priority)
    task.status = data.get('status', task.status)
    
    if 'due_date' in data:
        task.due_date = datetime.fromisoformat(data['due_date'])
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Task updated successfully'})

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first()
    
    if not task:
        return jsonify({'success': False, 'message': 'Task not found'}), 404
    
    db.session.delete(task)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Task deleted successfully'})

@app.route('/api/tasks/<int:task_id>/complete', methods=['POST'])
@login_required
def complete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first()
    
    if not task:
        return jsonify({'success': False, 'message': 'Task not found'}), 404
    
    task.status = 'completed'
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Task marked as completed'})

@app.route('/api/stats')
@login_required
def get_stats():
    user_id = session['user_id']
    today = datetime.now().date()
    week_end = today + timedelta(days=7)
    
    total_tasks = Task.query.filter_by(user_id=user_id).count()
    today_tasks = Task.query.filter_by(user_id=user_id).filter(db.func.date(Task.due_date) == today).count()
    completed_today = Task.query.filter_by(user_id=user_id, status='completed').filter(db.func.date(Task.due_date) == today).count()
    pending_tasks = Task.query.filter_by(user_id=user_id, status='pending').count()
    
    completion_rate = (completed_today / today_tasks * 100) if today_tasks > 0 else 0
    
    return jsonify({
        'total_tasks': total_tasks,
        'today_tasks': today_tasks,
        'completed_today': completed_today,
        'pending_tasks': pending_tasks,
        'completion_rate': round(completion_rate, 1)
    })

# Shopping List API Routes
@app.route('/shopping-list')
@login_required
def shopping_list():
    return render_template('shopping_list.html', username=session.get('username'))

@app.route('/api/shopping-items', methods=['GET'])
@login_required
def get_shopping_items():
    user_id = session['user_id']
    filter_type = request.args.get('filter', 'all')
    
    query = ShoppingItem.query.filter_by(user_id=user_id)
    
    if filter_type == 'purchased':
        query = query.filter_by(is_purchased=True)
    elif filter_type == 'pending':
        query = query.filter_by(is_purchased=False)
    
    items = query.order_by(ShoppingItem.created_at.desc()).all()
    
    return jsonify([{
        'id': item.id,
        'item_name': item.item_name,
        'quantity': item.quantity,
        'category': item.category,
        'is_purchased': item.is_purchased,
        'notes': item.notes,
        'created_at': item.created_at.isoformat()
    } for item in items])

@app.route('/api/shopping-items', methods=['POST'])
@login_required
def create_shopping_item():
    data = request.get_json()
    
    new_item = ShoppingItem(
        user_id=session['user_id'],
        item_name=data['item_name'],
        quantity=data.get('quantity', '1'),
        category=data.get('category', 'other'),
        notes=data.get('notes', '')
    )
    
    db.session.add(new_item)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Item added to shopping list',
        'item': {
            'id': new_item.id,
            'item_name': new_item.item_name,
            'quantity': new_item.quantity,
            'category': new_item.category,
            'is_purchased': new_item.is_purchased,
            'notes': new_item.notes
        }
    })

@app.route('/api/shopping-items/<int:item_id>', methods=['PUT'])
@login_required
def update_shopping_item(item_id):
    item = ShoppingItem.query.filter_by(id=item_id, user_id=session['user_id']).first()
    
    if not item:
        return jsonify({'success': False, 'message': 'Item not found'}), 404
    
    data = request.get_json()
    
    item.item_name = data.get('item_name', item.item_name)
    item.quantity = data.get('quantity', item.quantity)
    item.category = data.get('category', item.category)
    item.notes = data.get('notes', item.notes)
    item.is_purchased = data.get('is_purchased', item.is_purchased)
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Item updated successfully'})

@app.route('/api/shopping-items/<int:item_id>', methods=['DELETE'])
@login_required
def delete_shopping_item(item_id):
    item = ShoppingItem.query.filter_by(id=item_id, user_id=session['user_id']).first()
    
    if not item:
        return jsonify({'success': False, 'message': 'Item not found'}), 404
    
    db.session.delete(item)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Item deleted successfully'})

@app.route('/api/shopping-items/<int:item_id>/toggle', methods=['POST'])
@login_required
def toggle_shopping_item(item_id):
    item = ShoppingItem.query.filter_by(id=item_id, user_id=session['user_id']).first()
    
    if not item:
        return jsonify({'success': False, 'message': 'Item not found'}), 404
    
    item.is_purchased = not item.is_purchased
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': 'Item marked as ' + ('purchased' if item.is_purchased else 'not purchased'),
        'is_purchased': item.is_purchased
    })

@app.route('/api/shopping-items/clear-purchased', methods=['POST'])
@login_required
def clear_purchased_items():
    user_id = session['user_id']
    ShoppingItem.query.filter_by(user_id=user_id, is_purchased=True).delete()
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Purchased items cleared'})

# Email notification functions
def send_task_reminder(task, user):
    try:
        msg = Message(
            subject=f'Reminder: {task.title}',
            recipients=[user.email],
            body=f'''Hello {user.username},

This is a reminder for your upcoming task:

Task: {task.title}
Description: {task.description}
Due: {task.due_date.strftime('%Y-%m-%d %H:%M')}
Priority: {task.priority}

Don't forget to complete it on time!

Best regards,
Task Tracker App
'''
        )
        mail.send(msg)
        task.notification_sent = True
        db.session.commit()
    except Exception as e:
        print(f"Failed to send email: {e}")

def check_and_send_reminders():
    with app.app_context():
        now = datetime.now()
        reminder_time = now + timedelta(hours=1)
        
        tasks = Task.query.filter(
            Task.status == 'pending',
            Task.notification_sent == False,
            Task.due_date <= reminder_time,
            Task.due_date > now
        ).all()
        
        for task in tasks:
            user = User.query.get(task.user_id)
            send_task_reminder(task, user)

def send_daily_summary():
    with app.app_context():
        users = User.query.all()
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        
        for user in users:
            tasks = Task.query.filter(
                Task.user_id == user.id,
                Task.status == 'pending',
                db.func.date(Task.due_date) == today
            ).all()
            
            if tasks:
                task_list = '\n'.join([f"- {task.title} at {task.due_date.strftime('%H:%M')} ({task.priority} priority)" for task in tasks])
                
                try:
                    msg = Message(
                        subject=f'Daily Task Summary - {today.strftime("%B %d, %Y")}',
                        recipients=[user.email],
                        body=f'''Hello {user.username},

Here's your task summary for today:

{task_list}

Total tasks: {len(tasks)}

Have a productive day!

Best regards,
Task Tracker App
'''
                    )
                    mail.send(msg)
                except Exception as e:
                    print(f"Failed to send daily summary: {e}")

# Initialize scheduler only if available and not in serverless environment
if SCHEDULER_AVAILABLE and not os.environ.get('VERCEL'):
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=check_and_send_reminders, trigger="interval", minutes=30)
    scheduler.add_job(func=send_daily_summary, trigger="cron", hour=7, minute=0)
    scheduler.start()

# Initialize database tables on first request
@app.before_request
def initialize_database():
    if not hasattr(app, 'db_initialized'):
        try:
            db.create_all()
            app.db_initialized = True
        except Exception as e:
            print(f"Database initialization error: {e}")

# Vercel requires the app to be named 'app' or exported
# This is the WSGI application Vercel will use
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=os.environ.get('FLASK_ENV') != 'production')