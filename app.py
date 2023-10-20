import os

from flask import Flask, flash, redirect, render_template, request, send_file
from werkzeug.utils import secure_filename

import decrypter as dec
import divider as dv
import encrypter as enc
import restore as rst
import tools
from flask import request
from pymongo import MongoClient
from gridfs import GridFS


UPLOAD_FOLDER = './uploads/'
UPLOAD_KEY = './key/'
ALLOWED_EXTENSIONS = set(['pem'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_KEY'] = UPLOAD_KEY

#port = int(os.getenv('PORT', 8000))
client = MongoClient("mongodb+srv://ayushsk0000:Ucsp7hehpIlapdsJ@upescsa.7bupqwk.mongodb.net/")  # Replace with your MongoDB URI
db = client['FilesUpload']  # Replace 'your_database' with your database name
fs = GridFS(db)  # Initialize GridFS


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def start_encryption():
    dv.divide()
    tools.empty_folder('uploads')
    enc.encrypter()
    return render_template('success.html')


def start_decryption():
    dec.decrypter()
    tools.empty_folder('key')
    rst.restore()
    return render_template('restore_success.html')


@app.route('/return-key')
def return_key():
    print("reached")
    list_directory = tools.list_dir('key')
    filename = './key/' + list_directory[0]
    print(filename)
    return send_file(filename, download_name="My_Key.pem", as_attachment=True)


@app.route('/return-file/')
def return_file():
    list_directory = tools.list_dir('restored_file')
    filename = './restored_file/' + list_directory[0]
    print("****************************************")
    print(list_directory[0])
    print("****************************************")
    return send_file(filename, download_name=list_directory[0], as_attachment=True)


@app.route('/download/')
def downloads():
    return render_template('download.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/upload')
def call_page_upload():
    return render_template('upload.html')


@app.route('/home')
def back_home():
    tools.empty_folder('key')
    tools.empty_folder('restored_file')
    return render_template('index.html')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/data', methods=['GET', 'POST'])
def upload_file():
    tools.empty_folder('uploads')
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return 'NO FILE SELECTED'
        if file:
            
            file_data = file.read()
            file_id = fs.put(file_data, filename=file.filename)
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
            with open('raw_data/meta_data.txt', 'a') as file:
                file.write(filename + '\n')
            return start_encryption()
            return f'File uploaded with ID: {file_id}'

        return 'Invalid File Format !'

@app.route('/list-encrypted-files')
def list_encrypted_files():
    # Assuming you store the encrypted files in the 'uploads' directory
    encrypted_files = tools.list_dir('encrypted')
    
    # Read the contents of the uploaded files text file
    uploaded_files = []
    with open('raw_data/meta_data.txt', 'r') as file:
        uploaded_files = file.read().splitlines()    
    return render_template('list_files.html', files=encrypted_files, uploaded_files=uploaded_files)

@app.route('/download-file/<filename>')
def download_file(filename):
    # Your code to serve the file here
    # You can use send_file or any other method to serve the file
    return send_file(filename, as_attachment=True)

@app.route('/download_data', methods=['GET', 'POST'])
def upload_key():
    tools.empty_folder('key')
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return 'NO FILE SELECTED'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_KEY'], file.filename))
            return start_decryption()
        return 'Invalid File Format !'   



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
    # app.run()
