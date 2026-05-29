from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import numpy as np
#from tensorflow.keras.models import load_model
#from tensorflow.keras.preprocessing import image
import tensorflow as tf
from PIL import Image

import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'neuroassist-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'

# Create database tables
with app.app_context():
    db.create_all()

# Load the pre-trained model
#model = load_model('Semonet_model.keras')

# Class labels
class_labels = ['Glioma tumor', 'Meningioma tumor', 'No tumor', 'Pituitary tumor']

# Preprocess image for model prediction
def preprocess_image(img_path):
    img = Image.open(img_path).convert('RGB')  # Open and ensure 3 channels
    img = img.resize((224, 224))  # Resize to expected dimensions
    img = np.array(img) / 255.0  # Normalize
    img = np.expand_dims(img, axis=0)  # Add batch dimension
    return img


# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/tumor-prediction')
def tumor_prediction():
    if 'user_id' not in session:
        return jsonify({'redirect': url_for('login_page')})
    return render_template('tumor_prediction.html')

@app.route('/chatbot')
def chatbot():
    #if 'user_id' not in session:
       # return jsonify({'redirect': url_for('login_page')})
    return render_template('chatbot.html')

@app.route('/health-plan')
def health_plan():
    if 'user_id' not in session:
        return jsonify({'redirect': url_for('login_page')})
    return render_template('health_plan.html')

@app.route('/login-page')
def login_page():
    return render_template('login.html')

@app.route('/signup-page')
def signup_page():
    return render_template('signup.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.form
    user = User.query.filter_by(email=data.get('email')).first()
    
    if user and check_password_hash(user.password, data.get('password')):
        session['user_id'] = user.id
        session['username'] = user.username
        flash('Login successful!', 'success')
        return redirect(url_for('dashboard'))
    
    flash('Invalid email or password', 'danger')
    return redirect(url_for('login_page'))

@app.route('/signup', methods=['POST'])
def signup():
    data = request.form
    
    # Check if email already exists
    existing_user = User.query.filter_by(email=data.get('email')).first()
    if existing_user:
        flash('Email already registered', 'danger')
        return redirect(url_for('signup_page'))
    
    # Create new user
    hashed_password = generate_password_hash(data.get('password'))
    new_user = User(
        username=data.get('username'),
        email=data.get('email'),
        password=hashed_password
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    flash('Account created successfully! Please log in.', 'success')
    return redirect(url_for('login_page'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Preprocess the image
        processed_image = preprocess_image(file_path)
        
        # Make prediction
        #prediction = model.predict(processed_image)
        #predicted_class_index = np.argmax(prediction[0])
        #predicted_class = class_labels[predicted_class_index]
        #confidence = float(prediction[0][predicted_class_index]) * 100
        
        return jsonify({
           # 'prediction': predicted_class,
            #'confidence': confidence,
            'image_path': file_path.replace('static/', '')
        })

@app.route('/get-health-plan/<tumor_type>')
def get_health_plan(tumor_type):
    # Enhanced rule-based health plans based on tumor type
    health_plans = {
        'Glioma tumor': {
            'tumorTypeName': 'Glioma Tumor',
            'dietOverview': 'A diet rich in antioxidants and anti-inflammatory foods can help support overall health during glioma treatment. Focus on whole foods and limit processed items.',
            'recommendedFoods': [
                'Berries (blueberries, strawberries, blackberries)',
                'Leafy greens (spinach, kale, collard greens)',
                'Fatty fish rich in omega-3 (salmon, mackerel, sardines)',
                'Nuts and seeds (walnuts, flaxseeds, chia seeds)',
                'Turmeric and other anti-inflammatory spices',
                'Green tea',
                'Whole grains',
                'Legumes and beans'
            ],
            'foodsToAvoid': [
                'Processed meats (bacon, sausage, hot dogs)',
                'Refined sugars and high-fructose corn syrup',
                'Excessive alcohol',
                'Fried foods and trans fats',
                'Artificial sweeteners and additives',
                'Excessive caffeine'
            ],
            'treatmentOverview': 'Treatment for glioma tumors typically involves a multidisciplinary approach combining surgery, radiation therapy, and chemotherapy. The specific treatment plan depends on the tumor grade, location, and the patient\'s overall health.',
            'surgeryDescription': 'Surgical resection aims to remove as much of the tumor as possible while preserving neurological function. Advanced techniques like awake craniotomy and intraoperative mapping may be used for tumors in eloquent brain areas.',
            'radiationDescription': 'Radiation therapy uses high-energy beams to target and kill tumor cells. For gliomas, this often involves external beam radiation therapy (EBRT) delivered over several weeks. Stereotactic radiosurgery may be used for smaller tumors.',
            'chemotherapyDescription': 'Temozolomide is the standard chemotherapy drug for gliomas, often administered orally. It may be given during and after radiation therapy. For recurrent tumors, bevacizumab or lomustine might be considered.',
            'priorityLevels': 'High priority: Surgery for symptomatic or growing tumors. Medium priority: Radiation therapy. Ongoing priority: Regular MRI monitoring and symptom management.',
            'targetedTherapy': 'For specific genetic mutations like IDH mutations or MGMT methylation, targeted therapies may be available through clinical trials. Tumor treating fields (TTFields) is an FDA-approved device therapy for certain glioblastomas.'
        },
        'Meningioma tumor': {
            'tumorTypeName': 'Meningioma Tumor',
            'dietOverview': 'A balanced diet that supports brain health and reduces inflammation is recommended for meningioma patients. Focus on Mediterranean-style eating patterns.',
            'recommendedFoods': [
                'Olive oil and other healthy fats',
                'Fatty fish rich in omega-3 (salmon, trout, sardines)',
                'Colorful fruits and vegetables',
                'Foods rich in vitamin D (egg yolks, fortified foods)',
                'Calcium-rich foods (dairy, fortified plant milks, leafy greens)',
                'Magnesium-rich foods (nuts, seeds, whole grains)',
                'Lean proteins',
                'Hydrating foods and plenty of water'
            ],
            'foodsToAvoid': [
                'Excessive salt (may worsen edema)',
                'Processed foods with preservatives',
                'High-sugar foods and beverages',
                'Excessive alcohol',
                'Artificial sweeteners',
                'Foods that trigger individual sensitivities'
            ],
            'treatmentOverview': 'Treatment for meningiomas depends on size, location, growth rate, and symptoms. Many meningiomas grow slowly and may only require monitoring, while others need intervention.',
            'surgeryDescription': 'For symptomatic or growing meningiomas, surgical removal is often the primary treatment. Complete resection (Simpson Grade I or II) offers the best chance for cure. Minimally invasive approaches may be used when appropriate.',
            'radiationDescription': 'Radiation therapy may be recommended for incompletely resected tumors, recurrent tumors, or those in locations that make surgery risky. Stereotactic radiosurgery is often used for smaller meningiomas.',
            'chemotherapyDescription': 'Chemotherapy is rarely used for meningiomas but may be considered for aggressive or recurrent tumors. Hydroxyurea, sunitinib, or bevacizumab might be options in specific cases.',
            'priorityLevels': 'High priority: Surgery for symptomatic tumors. Medium priority: Radiation for residual tumor. Low priority: Observation for small, asymptomatic tumors.',
            'targetedTherapy': 'Hormone therapy may be considered as meningiomas often have hormone receptors. Clinical trials investigating targeted therapies based on molecular profiles are ongoing.'
        },
        'No tumor': {
            'tumorTypeName': 'No Tumor Detected',
            'dietOverview': 'A brain-healthy diet is recommended for overall neurological health and prevention. Focus on foods that support cognitive function and reduce inflammation.',
            'recommendedFoods': [
                'Fatty fish rich in omega-3 (salmon, trout, sardines)',
                'Berries and other antioxidant-rich fruits',
                'Leafy green vegetables',
                'Nuts and seeds (especially walnuts)',
                'Whole grains',
                'Olive oil',
                'Lean proteins',
                'Dark chocolate (70% or higher cocoa content)'
            ],
            'foodsToAvoid': [
                'Highly processed foods',
                'Foods high in saturated and trans fats',
                'Excessive sugar and refined carbohydrates',
                'Excessive alcohol',
                'Excessive sodium',
                'Artificial additives and preservatives'
            ],
            'treatmentOverview': 'With no tumor detected, focus should be on maintaining brain health and addressing any neurological symptoms that prompted the initial evaluation.',
            'surgeryDescription': 'No surgical intervention is needed in the absence of a tumor. If neurological symptoms persist, further evaluation may be warranted.',
            'radiationDescription': 'Radiation therapy is not indicated when no tumor is present.',
            'chemotherapyDescription': 'Chemotherapy is not indicated when no tumor is present.',
            'priorityLevels': 'Priority should be given to identifying the cause of any persistent symptoms and maintaining overall brain health.',
            'targetedTherapy': 'No targeted therapy is needed, but addressing risk factors for neurological conditions is recommended.'
        },
        'Pituitary tumor': {
            'tumorTypeName': 'Pituitary Tumor',
            'dietOverview': 'Diet for pituitary tumor patients should focus on supporting hormone balance and overall endocrine health. The specific recommendations may vary based on hormone abnormalities.',
            'recommendedFoods': [
                'Foods rich in vitamin D (fatty fish, egg yolks, fortified foods)',
                'Zinc-rich foods (oysters, beef, pumpkin seeds)',
                'Magnesium-rich foods (dark chocolate, avocados, nuts)',
                'Selenium-rich foods (Brazil nuts, seafood)',
                'Iodine-rich foods for thyroid function (seaweed, fish, dairy)',
                'Antioxidant-rich fruits and vegetables',
                'Healthy fats (avocados, olive oil, nuts)',
                'Adequate protein sources'
            ],
            'foodsToAvoid': [
                'Excessive caffeine (may affect adrenal function)',
                'High-sugar foods (may affect insulin and other hormones)',
                'Excessive alcohol',
                'Highly processed foods',
                'Artificial hormones in food products',
                'Soy products in large amounts (for hormone-secreting tumors)'
            ],
            'treatmentOverview': 'Treatment for pituitary tumors depends on the type, size, and hormonal activity. Options include medication, surgery, and radiation therapy.',
            'surgeryDescription': 'Transsphenoidal surgery (through the nose and sphenoid sinus) is the most common surgical approach for pituitary tumors. Its minimally invasive and avoids brain retraction. Endoscopic techniques offer excellent visualization.',
            'radiationDescription': 'Stereotactic radiosurgery (like Gamma Knife) may be used for residual tumor after surgery or as primary treatment for patients who cannot undergo surgery. Conventional radiation therapy is used less frequently.',
            'chemotherapyDescription': 'Traditional chemotherapy is rarely used for pituitary tumors. However, temozolomide may be considered for aggressive or malignant tumors.',
            'priorityLevels': 'High priority: Normalizing hormone levels and relieving pressure on surrounding structures. Medium priority: Tumor removal or shrinkage. Ongoing priority: Hormone replacement if needed.',
            'targetedTherapy': 'Medical therapy is often the first line for hormone-secreting tumors. Prolactinomas respond to dopamine agonists (cabergoline, bromocriptine). Somatostatin analogs (octreotide, lanreotide) may be used for growth hormone-secreting tumors.'
        }
    }
    
    return jsonify(health_plans.get(tumor_type, {'dietOverview': '', 'recommendedFoods': [], 'foodsToAvoid': [], 'treatmentOverview': '', 'surgeryDescription': '', 'radiationDescription': '', 'chemotherapyDescription': '', 'priorityLevels': '', 'targetedTherapy': ''}))

@app.route('/chatbot-query', methods=['POST'])
def chatbot_query():
    data = request.json
    query = data.get('query', '').lower()
    tumor_type = data.get('tumor_type', '')

    # Simple rule-based responses
    responses = {
        'what is a brain tumor': 'A brain tumor is a mass or growth of abnormal cells in the brain. Brain tumors can be benign (non-cancerous) or malignant (cancerous).',
        'what are the symptoms': 'Common symptoms of brain tumors include headaches, seizures, difficulty thinking or speaking, changes in personality, and problems with balance.',
        'my mri result says glioma, probability 95% what does this mean?': "Your MRI result indicates a glioma with a probability of 95%. This means that there is a high likelihood that the observed lesion is a glioma. However, further evaluation by a neurologist or neurosurgeon, which may include additional imaging or a biopsy, is necessary to confirm the diagnosis and determine the type and grade of the tumor.",
        'what is the treatment': f'Treatment for {tumor_type} typically includes surgery, radiation therapy, and/or chemotherapy, depending on the type and location of the tumor.',
        'what is the prognosis': f'The prognosis for {tumor_type} varies depending on the type, size, and location of the tumor, as well as the patient\'s age and overall health.',
        'what causes brain tumors': 'The exact cause of most brain tumors is unknown. However, risk factors include exposure to radiation, family history, and certain genetic conditions.',
        'can brain tumors be prevented': 'Most brain tumors cannot be prevented. However, avoiding risk factors like radiation exposure may help reduce the risk.',
        'what is glioma': 'Glioma is a type of tumor that occurs in the brain and spinal cord. It begins in the glial cells that surround and support nerve cells.',
        'what is meningioma': 'Meningioma is a tumor that arises from the meninges — the membranes that surround your brain and spinal cord. Most meningiomas are noncancerous.',
        'what is pituitary tumor': 'A pituitary tumor is an abnormal growth in the pituitary gland, which is a small gland located at the base of the brain that regulates many vital functions.',
        'diet recommendations': f'For {tumor_type}, we recommend a diet rich in antioxidants, omega-3 fatty acids, and anti-inflammatory foods. Please check the Health Plan section for more details.',
        'treatment plan': f'The treatment plan for {tumor_type} may include surgery, radiation therapy, and/or medication. Please consult with your healthcare provider for personalized advice.'
    }

    response = responses.get(query)
    if response:
        return jsonify({'response': response})
    
    return jsonify({'response': f"I'm sorry, I don't have specific information about that. Please consult with a healthcare professional for advice regarding {tumor_type}."})

    
    # Check for matches in our response dictionary
    for key, response in responses.items():
        if key in query:
            return jsonify({'response': response})
    
    # Default response if no match is found
    return jsonify({'response': f"I'm sorry, I don't have specific information about that. Please consult with a healthcare professional for advice regarding {tumor_type}."})

if __name__ == '__main__':
    app.run(debug=True)
