const express = require('express');
const multer = require('multer');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const nodemailer = require('nodemailer');

const app = express();
const port = 3000;

// Configure Nodemailer
let transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
        user: 'itceduckie@gmail.com',
        pass: 'zmee bszt tvvt orvk',
    }
});

// Configure storage
const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, 'uploads/');
    },
    filename: function (req, file, cb) {
        cb(null, Date.now() + path.extname(file.originalname));
    }
});

// Serve static files
app.use(express.static(path.join(__dirname, '/')));

// Serve the index.html file
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

const upload = multer({ storage: storage });

app.post('/upload', upload.single('video'), (req, res) => {
    const inputFile = req.file.path;
    const outputFile = `uploads/${Date.now()}_converted.mp4`;

    exec(`ffmpeg -i ${inputFile} ${outputFile}`, (error, stdout, stderr) => {
        if (error) {
            console.error(`Error executing FFmpeg: ${error}`);
            return res.status(500).send('Failed to convert video');
        }

        // Delete the original file
        fs.unlinkSync(inputFile);

        // Email the converted file
        let mailOptions = {
            from: '"NPA Mailing Client" <itceduckie@gmail.com>',
            to: "winleydelafuente@gmail.com, rgestudillo@up.edu.ph, jmojado@up.edu.ph,fc185017@ncr.com",
            //to: "winleydelafuente@gmail.com",
            subject: 'Video Alert',
            text: 'A new security alert has been detected.',
            attachments: [
                {
                    filename: 'converted_video.mp4',
                    path: outputFile
                }
            ]
        };

        transporter.sendMail(mailOptions, function (error, info) {
            if (error) {
                console.error(`Error sending email: ${error}`);
                return res.status(500).send('Failed to send email');
            } else {
                console.log(`Email sent: ${info.response}`);
                return res.status(200).send('Successfully converted and emailed');
            }
        });
    });
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}/`);
});