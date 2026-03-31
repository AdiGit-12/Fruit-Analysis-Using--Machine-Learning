from flask import Flask, request, render_template, redirect, url_for, flash, session
from datetime import datetime, timedelta
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from keras.preprocessing import image
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import bleach
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

# Load the pre-trained model
model = load_model("models/fruits.h5", compile=False)

# Define the class names
class_name = ['freshapples',
 'freshbanana',
 'freshoranges',
 'rottenapples',
 'rottenbanana',
 'rottenoranges']

# Freshness data for fruits
freshness_data = {
    'freshapples': {
        'name': 'Apple',
        'duration': '5-7 days at room temperature, 4-6 weeks refrigerated',
        'storage_tips': 'Store in a cool, dry place away from direct sunlight. For longer storage, keep in the crisper drawer of your refrigerator.'
    },
    'freshbanana': {
        'name': 'Banana',
        'duration': '2-5 days at room temperature',
        'storage_tips': 'Store at room temperature away from other fruits. To slow ripening, wrap the stem in plastic wrap. Once ripe, you can refrigerate (peel will darken but fruit will be fine).'
    },
    'freshoranges': {
        'name': 'Orange',
        'duration': '1-2 weeks at room temperature, 3-4 weeks refrigerated',
        'storage_tips': 'Store at room temperature for short term or in the refrigerator for longer storage. Keep in a mesh bag for air circulation.'
    },
    # Rotten fruits
    'rottenapples': {
        'name': 'Rotten Apple',
        'duration': 'Not applicable',
        'storage_tips': 'This apple is no longer fresh. Consider composting if appropriate.'
    },
    'rottenbanana': {
        'name': 'Rotten Banana',
        'duration': 'Not applicable',
        'storage_tips': 'Overripe bananas can be used for baking (banana bread) or smoothies. Otherwise, consider composting.'
    },
    'rottenoranges': {
        'name': 'Rotten Orange',
        'duration': 'Not applicable',
        'storage_tips': 'This orange is no longer fresh. Discard appropriately.'
    }
}
# Initialize Flask app
app = Flask(__name__)

# Initialize Limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)
# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost' # my localhost name
app.config['MYSQL_USER'] = 'root'  # Change to your MySQL username
app.config['MYSQL_PASSWORD'] = 'Aditya#123'  # Change to your MySQL password
app.config['MYSQL_DB'] = 'fruit_analysis_db'
app.secret_key = 'your_secret_key_here'  # Needed for flash messages

# Admin Configuration
app.config['ADMIN_USERNAME'] = 'admin'
app.config['ADMIN_PASSWORD'] = 'admin1204'  # Change to a strong password

# Initialize MySQL
mysql = MySQL(app)


def create_tables():
    try:
        cur = mysql.connection.cursor()
        
        # Users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                email VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(200) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) AUTO_INCREMENT=1
        """)
        
        # Contacts table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL,
                subject VARCHAR(200) NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Predictions table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                filename VARCHAR(255) NOT NULL,
                prediction VARCHAR(100) NOT NULL,
                confidence INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            ) AUTO_INCREMENT=1
        """)
        
        mysql.connection.commit()
        cur.close()
    except Exception as e:
        print(f"Error creating tables: {e}")

# Create tables when app starts
with app.app_context():
    create_tables()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'danger')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            flash('Admin access required', 'danger')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    # Redirect to login if not authenticated, otherwise show homepage
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template("index.html")


@app.route('/about.html')
@login_required
def about():
    return render_template("about.html")

@app.route('/contact.html', methods=['GET', 'POST'])
@login_required
@limiter.limit("5 per minute")
def contact():
    if request.method == 'POST':
        # Get form data and sanitize it using bleach
        name = bleach.clean(request.form['name'])
        email = bleach.clean(request.form['email'])
        subject = bleach.clean(request.form['subject'])
        message = bleach.clean(request.form['message'])
        
        # Create cursor
        cur = mysql.connection.cursor()
        
        try:
            # Execute query
            cur.execute(
                "INSERT INTO contacts(name, email, subject, message) VALUES(%s, %s, %s, %s)",
                (name, email, subject, message))
            
            # Commit to DB
            mysql.connection.commit()
            
            # Close connection
            cur.close()
            
            flash('Your message has been sent successfully!', 'success')
            return redirect(url_for('contact'))
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('contact'))
    
    return render_template("contact.html")



# User Authentication Routes
@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def register():
    if request.method == 'POST':
        username = bleach.clean(request.form['username'])
        email = bleach.clean(request.form['email'])
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        cur = mysql.connection.cursor()
        try:
            cur.execute(
                "INSERT INTO users(username, email, password) VALUES(%s, %s, %s)",
                (username, email, hashed_password))
            mysql.connection.commit()
            cur.close()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('register'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if 'user_id' in session:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/prediction.html', methods=['GET', 'POST'])
@login_required
@limiter.limit("10 per minute")
def prediction():
    if request.method == 'POST':
        try:
            f = request.files['fruit']
            filename = f.filename
            target = os.path.join(APP_ROOT, 'static/uploads/')
            os.makedirs(target, exist_ok=True)
            des = "/".join([target, filename])
            f.save(des)

            # Process image and get prediction
            test_image = image.load_img(des, target_size=(300,300))
            test_image = image.img_to_array(test_image)
            test_image = np.expand_dims(test_image, axis=0)
            prediction_result = model.predict(test_image)

            predicted_class = class_name[np.argmax(prediction_result[0])]
            confidence = round(np.max(prediction_result[0])*100)
            current_time = datetime.now()

            # Calculate freshness information
            freshness = {
                'timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                'fresh_until': None,
                'storage_condition': ''
            }

            if 'fresh' in predicted_class:
                if 'apple' in predicted_class:
                    expiry = current_time + timedelta(days=5)
                    freshness['fresh_until'] = expiry.strftime('%Y-%m-%d')
                    freshness['storage_condition'] = 'at room temperature'
                elif 'banana' in predicted_class:
                    expiry = current_time + timedelta(days=3)
                    freshness['fresh_until'] = expiry.strftime('%Y-%m-%d')
                elif 'orange' in predicted_class:
                    expiry = current_time + timedelta(days=10)
                    freshness['fresh_until'] = expiry.strftime('%Y-%m-%d')

            # Store prediction in database (without BLOB)
            cur = mysql.connection.cursor()
            cur.execute(
                "INSERT INTO predictions(user_id, filename, prediction, confidence) VALUES(%s, %s, %s, %s)",
                (session['user_id'], filename, predicted_class, confidence)
            )
            mysql.connection.commit()
            cur.close()

            # Render template with all information
            return render_template("prediction.html",
                                confidence=confidence,
                                prediction=predicted_class,
                                fruit_info=freshness_data.get(predicted_class),
                                freshness=freshness,
                                image_path=f"uploads/{filename}")

        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('prediction'))

    return render_template("prediction.html")
    

# Admin Routes
@app.route('/admin/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def admin_login():
    if request.method == 'POST':
        username = bleach.clean(request.form['username'])
        password = request.form['password']
        
        if username == app.config['ADMIN_USERNAME'] and password == app.config['ADMIN_PASSWORD']:
            session['admin_logged_in'] = True
            flash('Admin login successful', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials', 'danger')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
@admin_required
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Admin logged out successfully', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    cur = mysql.connection.cursor()
    
    # Total users
    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]
    
    # Total predictions
    cur.execute("SELECT COUNT(*) FROM predictions")
    total_predictions = cur.fetchone()[0]
    
    # Recent users (last 5)
    cur.execute("SELECT username, email, created_at FROM users ORDER BY created_at DESC LIMIT 5")
    recent_users = cur.fetchall()
    
    # Recent predictions (last 5)
    cur.execute("""
        SELECT u.username, p.filename, p.prediction, p.confidence, p.created_at 
        FROM predictions p
        JOIN users u ON p.user_id = u.id
        ORDER BY p.created_at DESC LIMIT 5
    """)
    recent_predictions = cur.fetchall()

    # Convert predictions to include image paths
    predictions_with_images = []
    for pred in recent_predictions:
        pred_dict = {
            'username': pred[0],
            'filename': pred[1],
            'prediction': pred[2],
            'confidence': pred[3],
            'created_at': pred[4],
            'image_path': f"uploads/{pred[1]}"  # Add the image path here
        }
        predictions_with_images.append(pred_dict)
    
    cur.close()
    
    return render_template('admin_dashboard.html',
                         total_users=total_users,
                         total_predictions=total_predictions,
                         recent_users=recent_users,
                         recent_predictions=predictions_with_images)

@app.route('/admin/users')
@admin_required
def admin_users():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, username, email, created_at FROM users ORDER BY created_at DESC")
    users = cur.fetchall()
    cur.close()
    return render_template('admin_users.html', users=users)

@app.route('/admin/predictions')
@admin_required
def admin_predictions():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT p.id, u.username, p.filename, p.prediction, p.confidence, p.created_at 
        FROM predictions p
        JOIN users u ON p.user_id = u.id
        ORDER BY p.created_at DESC
    """)
    predictions = cur.fetchall()

    # Convert predictions to include image paths
    predictions_with_images = []
    for pred in predictions:
        pred_dict = {
            'id': pred[0],
            'username': pred[1],
            'filename': pred[2],
            'prediction': pred[3],
            'confidence': pred[4],
            'created_at': pred[5],
            'image_path': f"uploads/{pred[2]}"  # Add the image path here
        }
        predictions_with_images.append(pred_dict)
    
    cur.close()
    return render_template('admin_predictions.html', predictions=predictions_with_images)

@app.route('/admin/contacts')
@admin_required
def admin_contacts():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id, name, email, subject, message, created_at 
        FROM contacts 
        ORDER BY created_at DESC
    """)
    contacts = cur.fetchall()
    cur.close()
    return render_template('admin_contacts.html', contacts=contacts)

if __name__ == '__main__':
    app.debug = True
    app.run()