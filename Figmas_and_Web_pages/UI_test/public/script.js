window.onload = function() {
    // Check if the certain directory exists
    // Assume the directory is named 'images'
    fetch('http://localhost:8000/images/directory-check')
        .then(response => {
            if (!response.ok) {
                throw new Error('Directory not found');
            }
            return response.json();
        })
        .then(data => {
            // Directory exists, load images and text
            document.getElementById('image1').src = `http://localhost:8000/images/${data.image1}`;
            document.getElementById('image2').src = `http://localhost:8000/images/${data.image2}`;
            document.getElementById('text').innerText = data.text;
        })
        .catch(error => {
            console.error('Error:', error);
        });
};
