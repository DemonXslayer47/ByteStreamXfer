from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import os
import threading
import socket

app = Flask(__name__)
socketio = SocketIO(app)
UPLOAD_FOLDER = 'uploaded_files'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Route to delete files
@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        # Inform the receiver that the file has been deleted
        socketio.emit('file_deleted', {'filename': filename}, broadcast=True)
        return jsonify({"message": f"{filename} deleted successfully"})
    else:
        return jsonify({"error": f"{filename} not found"})

# Route to handle file download and delete the file after downloading
@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        # Delete the file after successful download
        @after_this_request
        def remove_file(response):
            os.remove(file_path)
            return response
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    else:
        return jsonify({"error": f"{filename} not found"})
    
@app.route('/')
def index():
    # Serve the main page with send and receive options
    return render_template('index.html')

@app.route('/send', methods=['GET', 'POST'])
def send():
    if request.method == 'POST':
        files = request.files.getlist('file')  # This handles multiple files
        for file in files:
            if file:
                filename = file.filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({"message": f"{len(files)} files uploaded successfully"})
    return render_template('send.html')

@app.route('/receive')
def receive():
    # Serve the page for listing and downloading files
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('receive.html', files=files)

def socket_server():
    HOST = '127.0.0.1'
    PORT = 6001  # Port for the socket server
    BUFFER_SIZE = 1024

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"Socket server listening on {HOST}:{PORT}")

        while True:
            conn, _ = server_socket.accept()
            with conn:
                filename = conn.recv(BUFFER_SIZE).decode()
                if filename:
                    file_path = os.path.join(UPLOAD_FOLDER, filename)
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as f:
                            while True:
                                bytes_read = f.read(BUFFER_SIZE)
                                if not bytes_read:
                                    break  # End of file
                                conn.sendall(bytes_read)
                    else:
                        print("File not found:", filename)

@socketio.on('request_file')
def handle_request_file(json):
    filename = json['filename']
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(1024)
                if not chunk:
                    break
                emit('file_chunk', {'filename': filename, 'data': chunk.decode('latin-1')})
        emit('file_complete', {'filename': filename})
    else:
        emit('file_error', {'filename': filename, 'message': 'File not found'})

if __name__ == '__main__':
    # Start the socket server in a separate thread
    threading.Thread(target=socket_server, daemon=True).start()
    socketio.run(app, host='192.168.1.143', port=5000, debug=True, use_reloader=False)
#10.178.50.147