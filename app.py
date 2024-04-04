from flask import Flask, render_template, request, send_from_directory, abort, jsonify
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO
import os
import base64
import random
import io
import zipfile
import qrcode

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['UPLOAD_FOLDER'] = 'uploaded_files'
app.config['MAX_CONTENT_LENGTH'] = 3 * 1024 * 1024 * 1024  # 2 gigabytes

socketio = SocketIO(app)

# Adjust with your actual IP address
network_ip = 'http://10.178.50.101:5000'

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

code_file_mapping = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['GET', 'POST'])
def download_page():
    if request.method == 'POST':
        code = request.form.get('code')
        return redirect(url_for('download_file', code=code))
    else:
        return render_template('download.html')  # Assuming this is your first download page HTML

@app.route('/upload', methods=['POST'])
def upload_file():
    files = request.files.getlist('file')
    if not files:
        return 'No files to upload', 400

    zip_filename = "files.zip"
    zip_path = os.path.join(app.config['UPLOAD_FOLDER'], zip_filename)
    
    with zipfile.ZipFile(zip_path, 'w') as myzip:
        for file in files:
            if file.filename:
                filename = secure_filename(file.filename)
                in_memory_file = io.BytesIO()
                file.save(in_memory_file)
                in_memory_file.seek(0)
                myzip.writestr(filename, in_memory_file.read())
    
    code = generate_random_pin()
    code_file_mapping[code] = zip_filename
    full_url = network_ip + '/download/' + code
    qr_code_img = generate_qr_code(full_url)

    return jsonify({'filename': zip_filename, 'qr': qr_code_img, 'pin': code})

@app.route('/download/<code>')
def download_file(code):
    filename = code_file_mapping.get(code)
    if filename and os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
        # Render a page that shows the file details and provides a download button.
        return render_template('download_page.html', filename=filename, code=code)
    else:
        abort(404)

@app.route('/download/file/<code>')
def download_file_direct(code):
    filename = code_file_mapping.get(code)
    if filename and os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    else:
        abort(404)

def generate_random_pin():
    return '{:04d}'.format(random.randint(0, 9999))

def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    qr_code_data = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return f"data:image/jpeg;base64,{qr_code_data}"

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
