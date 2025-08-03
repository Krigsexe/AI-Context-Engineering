#!/usr/bin/env python3
"""
ODIN Flask Sample App
Testing ODIN v6.0 - Semantic Integrity Hash, TestGen, and DepGuard
"""

import os
import requests
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///odin_sample.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'odin-v6-secret-key-2025')

# Initialize database
db = SQLAlchemy(app)

# User model
class User(db.Model):
    """User model for testing database operations"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }

    def __repr__(self):
        return f'<User {self.username}>'

# Post model
class Post(db.Model):
    """Post model for testing relationships"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('posts', lazy=True))

    def to_dict(self):
        """Convert post object to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'user_id': self.user_id,
            'username': self.user.username,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<Post {self.title}>'

# Utility functions
def validate_email(email):
    """Basic email validation"""
    return '@' in email and '.' in email.split('@')[1]

def get_user_stats():
    """Calculate user statistics"""
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    total_posts = Post.query.count()
    
    return {
        'total_users': total_users,
        'active_users': active_users,
        'total_posts': total_posts,
        'average_posts_per_user': round(total_posts / total_users, 2) if total_users > 0 else 0
    }

def fetch_external_data():
    """Fetch data from external API (for testing purposes)"""
    try:
        response = requests.get('https://jsonplaceholder.typicode.com/posts/1', timeout=5)
        return response.json() if response.status_code == 200 else None
    except requests.RequestException:
        return None

# Routes
@app.route('/')
def index():
    """Home page with app information"""
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ODIN Flask Sample</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
            .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
            .stat-card { background: #007bff; color: white; padding: 20px; border-radius: 8px; text-align: center; }
            .stat-value { font-size: 2em; font-weight: bold; }
            .endpoints { background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; }
            a { color: #007bff; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 ODIN Flask Sample App</h1>
            <p><strong>Version:</strong> v6.0 Testing Environment</p>
            <p><strong>Purpose:</strong> Testing Semantic Integrity Hash, TestGen, and DepGuard</p>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value">{{ stats.total_users }}</div>
                    <div>Total Users</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{{ stats.active_users }}</div>
                    <div>Active Users</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{{ stats.total_posts }}</div>
                    <div>Total Posts</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{{ stats.average_posts_per_user }}</div>
                    <div>Avg Posts/User</div>
                </div>
            </div>
            
            <div class="endpoints">
                <h3>🔗 Available Endpoints:</h3>
                <ul>
                    <li><a href="/api/users">GET /api/users</a> - List all users</li>
                    <li><a href="/api/posts">GET /api/posts</a> - List all posts</li>
                    <li><a href="/api/stats">GET /api/stats</a> - Get application statistics</li>
                    <li><a href="/api/external">GET /api/external</a> - Fetch external data</li>
                    <li>POST /api/users - Create new user</li>
                    <li>POST /api/posts - Create new post</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """
    stats = get_user_stats()
    return render_template_string(template, stats=stats)

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users"""
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@app.route('/api/users', methods=['POST'])
def create_user():
    """Create a new user"""
    data = request.get_json()
    
    if not data or 'username' not in data or 'email' not in data:
        return jsonify({'error': 'Username and email are required'}), 400
    
    if not validate_email(data['email']):
        return jsonify({'error': 'Invalid email format'}), 400
    
    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    user = User(
        username=data['username'],
        email=data['email'],
        is_active=data.get('is_active', True)
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201

@app.route('/api/posts', methods=['GET'])
def get_posts():
    """Get all posts with user information"""
    posts = Post.query.all()
    return jsonify([post.to_dict() for post in posts])

@app.route('/api/posts', methods=['POST'])
def create_post():
    """Create a new post"""
    data = request.get_json()
    
    if not data or 'title' not in data or 'content' not in data or 'user_id' not in data:
        return jsonify({'error': 'Title, content, and user_id are required'}), 400
    
    # Check if user exists
    user = User.query.get(data['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    post = Post(
        title=data['title'],
        content=data['content'],
        user_id=data['user_id']
    )
    
    db.session.add(post)
    db.session.commit()
    
    return jsonify(post.to_dict()), 201

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get application statistics"""
    return jsonify(get_user_stats())

@app.route('/api/external', methods=['GET'])
def get_external_data():
    """Fetch external data for testing"""
    data = fetch_external_data()
    if data:
        return jsonify(data)
    else:
        return jsonify({'error': 'Failed to fetch external data'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': 'v6.0-testing'
    })

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

# Initialize database
def init_db():
    """Initialize database with sample data"""
    db.create_all()
    
    # Add sample users if none exist
    if User.query.count() == 0:
        sample_users = [
            User(username='alice', email='alice@example.com'),
            User(username='bob', email='bob@example.com'),
            User(username='charlie', email='charlie@example.com', is_active=False)
        ]
        
        for user in sample_users:
            db.session.add(user)
        
        db.session.commit()
        
        # Add sample posts
        sample_posts = [
            Post(title='Welcome to ODIN', content='This is a test post for ODIN v6.0', user_id=1),
            Post(title='Flask Testing', content='Testing Flask integration with ODIN', user_id=1),
            Post(title='Database Operations', content='Testing database operations and relationships', user_id=2)
        ]
        
        for post in sample_posts:
            db.session.add(post)
        
        db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        init_db()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
