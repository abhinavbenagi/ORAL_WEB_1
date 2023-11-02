import functools
from flask import Flask, render_template, session, redirect,request, url_for
from functools import wraps
import pymongo
from db import db
import uuid
from PIL import Image
from ultralytics import YOLO
import os

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
app = Flask(__name__)
app.secret_key = b'\xcd\xbf(+=\t\xdc\xd9u\xfa\xd6Znh \xc5'

#Decoraters page

def login_required(f):
  @wraps(f)
  def wrap(*args , **kwargs):
    if 'logged_in' in session:
        return f(*args, **kwargs)
    else:
        return redirect('/')
  return wrap
      


from user.models import User

# Routes
# from user import routes

@app.route('/')
def home():
  return render_template('home.html')

@app.route('/dashboard/')
@login_required
def dashboard():
  return render_template('dashboard.html')

@app.route('/index2/')
@login_required
def index2():
    return render_template('index2.html')


@app.route('/user/signup', methods=['POST'])
def signup():
  return User().signup()

@app.route('/user/signout')
def signout():
   return User().signout()

@app.route('/user/login', methods=['POST'])
def login():
   return User().login()



model = YOLO('best (1).pt')

def run_keratin_pearls_detection(U_id,case_id, uploaded_images):
    
    in_folder = f'static/Output/uploaded/{case_id}/'
    os.makedirs(in_folder, exist_ok=True)

    out_folder = f'static/Output/detected/{case_id}/'
    os.makedirs(out_folder, exist_ok=True)

    for i, uploaded_image in enumerate(uploaded_images):
        image_path = f'{in_folder}{i}_{U_id}.jpg'
        uploaded_image.save(image_path)
        results_list = model.predict([image_path])
        for j, results in enumerate(results_list):
            im_array = results.plot()
            im = Image.fromarray(im_array)
            im.save(f'{out_folder}{i}_results_{U_id}.jpg')

def run_multiple_nucleoli_detection(U_id,case_id, uploaded_images):
    
    in_folder = f'static/Output/uploaded/{case_id}/'
    os.makedirs(in_folder, exist_ok=True)

    out_folder = f'static/Output/detected/{case_id}/'
    os.makedirs(out_folder, exist_ok=True)

    for i, uploaded_image in enumerate(uploaded_images):
        image_path = f'{in_folder}{i}_{U_id}.jpg'
        uploaded_image.save(image_path)
        results_list = model.predict([image_path])
        for j, results in enumerate(results_list):
            im_array = results.plot()
            im = Image.fromarray(im_array)
            im.save(f'{out_folder}{i}_results_{U_id}.jpg')

@app.route('/submit_form', methods=['POST'])
@login_required
def submit_form():
    U_id = str(uuid.uuid4())
    name = request.form['name']
    case_id = request.form['id']
    site = request.form['site']
    grade = request.form['grade']

    detection_type = request.form['detection_type']
    uploaded_images = request.files.getlist('image')

    # Assuming you have a collection named 'records' in your MongoDB
    records = db.Patient_info

    record_data = {
       'U_id': U_id,
        'name': name,
        'case_id': case_id,
        'site': site,
        'grade': grade,
    }
    records.insert_one(record_data)



    if detection_type == 'keratin_pearls':
        run_keratin_pearls_detection(U_id,case_id, uploaded_images)

    elif detection_type == 'multiple_nucleoli':
        print("Multiple nucleli")
        run_multiple_nucleoli_detection(U_id,case_id, uploaded_images)
    # elif detection_type == 'classification':
    #     run_classification(U_id,case_id, uploaded_images)


    # return redirect(url_for('success_page')) 
    return redirect(url_for('detected_images', case_id=case_id))

@app.route('/detected_images/<case_id>')
@login_required
def detected_images(case_id):
    out_folder = f'static/Output/detected/{case_id}/'
    images = [f for f in os.listdir(out_folder) if f.endswith('.jpg')]
    return render_template('detected_images.html', images=list(enumerate(images)), case_id=case_id)



@app.route('/success_page')
@login_required
def success_page():
    output_folder = 'Output/'  # Adjust the path to your output folder
    images = [f for f in os.listdir(output_folder) if f.endswith('.jpg')]
    return render_template('success.html', images=images)


@app.route('/view_patients')
@login_required
def view_patients():
    patients = db.Patient_info.find()  # Assuming 'patients' is the collection name
    return render_template('view_patients.html', patients=patients)


    return 'Form submitted successfully!'
if __name__=="__main__":
    app.run(debug=True)