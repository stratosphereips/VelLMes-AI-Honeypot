const express = require('express');
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3000;

app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(express.static('.'));

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'Experiment.html'));
});

// Endpoint to handle email submissions
app.post('/submit-email', (req, res) => {
    const email = req.body.email;
	
    // Write email to a file
    getNumberOfLines('emails.txt', (numLines) => {
        // Append the email along with the line number to the file
        fs.appendFile('emails.txt', `${numLines}. ${email}\n`, (err) => {
            if (err) throw err;
            console.log('Email saved:', email);
        });
    });
    res.send('Email submitted successfully');
});

// Endpoint to handle key submissions
app.post('/submit-key', (req, res) => {
    const key = req.body.key;
	const mail = req.body.email;
    const prob = req.body.prob;
	const currentDateTime = new Date();
    currentDateTime.setHours(currentDateTime.getHours() + 2); // Adjust for GMT+2
    const dateTime = currentDateTime.toISOString();
    // Write key to a file
    fs.appendFile('keys.txt', `${mail} - ${key} - ${prob} - ${dateTime}\n`, (err) => {
        if (err) throw err;
        console.log('Key saved:', key);
    });
    res.send('Key submitted successfully');
});

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});

function getNumberOfLines(filePath, callback) {
    fs.readFile(filePath, 'utf8', (err, data) => {
        if (err) {
            console.error('Error reading file:', err);
            return;
        }
        const numLines = data.split('\n').length;
        callback(numLines);
    });
}