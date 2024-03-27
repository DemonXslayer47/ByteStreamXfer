var socket = io.connect('http://' + document.domain + ':' + location.port);

socket.on('file_chunk', function(msg) {
    var link = document.createElement('a');
    link.download = msg.filename;
    link.href = 'data:application/octet-stream;base64,' + btoa(msg.data);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
});

function uploadFiles() {
    const fileInput = document.getElementById('fileInput');
    const files = fileInput.files;
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append('file', files[i]);
    }

    fetch('/send', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => alert(data.message))
    .catch(error => console.error('Error:', error));
}

function downloadFiles() {
    // Get all checked checkboxes in the form
    const selectedFiles = document.querySelectorAll('#filesForm input[name="files"]:checked');

    selectedFiles.forEach(fileCheckbox => {
        const filename = fileCheckbox.value;
        downloadFile(filename);
    });
}

function downloadFile(filename) {
    // Create a link and set the URL to the download route for the file
    const link = document.createElement('a');
    link.href = `/download/${filename}`;
    // Use the 'download' attribute to specify the filename
    link.setAttribute('download', filename);
    // Append the link to the document and trigger the download
    document.body.appendChild(link);
    link.click();
    // Remove the link from the document
    document.body.removeChild(link);
}

function deleteSelectedFiles() {
    // Get all checked checkboxes in the form
    const selectedFiles = document.querySelectorAll('#filesForm input[name="files"]:checked');

    selectedFiles.forEach(fileCheckbox => {
        const filename = fileCheckbox.value;
        deleteFile(filename);
    });
}

// Function to display uploaded files
function displayUploadedFiles() {
    const fileInput = document.getElementById('fileInput');
    const uploadedFilesList = document.getElementById('uploadedFilesList');
    uploadedFilesList.innerHTML = ''; // Clear previous list

    // Display selected files
    for (let i = 0; i < fileInput.files.length; i++) {
        const file = fileInput.files[i];
        const listItem = document.createElement('li');
        listItem.className = 'list-group-item';
        listItem.textContent = file.name;

        // Add a delete button for each file
        const deleteButton = document.createElement('button');
        deleteButton.textContent = 'Delete';
        deleteButton.className = 'btn btn-sm btn-danger ml-2';
        deleteButton.onclick = function() {
            deleteFile(file.name);
            // Remove the file from the UI
            listItem.parentNode.removeChild(listItem);
        };
        listItem.appendChild(deleteButton);

        uploadedFilesList.appendChild(listItem);
    }
}

// Call displayUploadedFiles() whenever files are selected
document.getElementById('fileInput').addEventListener('change', displayUploadedFiles);

// Function to delete a file
function deleteFile(filename) {
    fetch(`/delete/${filename}`, {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        // Inform the receiver that the file has been deleted
        socketio.emit('file_deleted', {'filename': filename}, broadcast=True);
    })
    .catch(error => console.error('Error:', error));
}
// Event listener for file deletion from SocketIO message
socket.on('file_deleted', function(data) {
    const filename = data.filename;
    // Remove the deleted file from the UI
    const fileItem = document.getElementById(filename);
    if (fileItem) {
        fileItem.parentElement.removeChild(fileItem);
    }
});
