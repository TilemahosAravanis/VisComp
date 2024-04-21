const express = require('express');
const app = express();
const fs = require('fs');
const opn = require('opn'); // For opening the browser

const PORT = process.env.PORT || 8000;
let serverStarted = false;

app.get('/', (req, res) => {
    res.redirect('/index.html');
});


app.use(express.static('public'));

// Endpoint to check if the directory exists
app.get('/images/directory-check', (req, res) => {
    const directoryPath = './public/images'; // Path to the directory
    if (fs.existsSync(directoryPath)) {
        // Directory exists, send image filenames and text
        const files = fs.readdirSync(directoryPath);
        const image1 = files.find(file => file.endsWith('.png') && file.includes('Figma'));
        const image2 = files.find(file => file.endsWith('.png') && file.includes('with_errors'));
        const text = fs.readFileSync(`${directoryPath}/differences.txt`, 'utf8');
        const url = `http://localhost:${PORT}`;

        // Print server URL only once when server starts
        if (!serverStarted) {
            console.log(`Server is running on ${url}`);
            serverStarted = true;
        }

        res.json({ image1, image2, text });

        // Check if '--open-browser' flag is provided
        if (process.argv.includes('--open-browser')) {
            opn(url); // Open browser if flag is provided
        }
    } else {
        // Directory does not exist
        res.status(404).send('Directory not found');
    }
});

app.listen(PORT, () => {
    // This callback is executed when the server starts listening
    // No need to print the message here
});
