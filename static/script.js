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