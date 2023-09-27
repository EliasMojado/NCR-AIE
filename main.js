/*jshint esversion:6*/

$(function () {
    const video = $("video")[0];

    var model;
    var cameraMode = "environment"; // or "user"

    const startVideoStreamPromise = navigator.mediaDevices
        .getUserMedia({
            audio: false,
            video: {
                facingMode: cameraMode
            }
        })
        .then(function (stream) {
            return new Promise(function (resolve) {
                video.srcObject = stream;
                video.onloadeddata = function () {
                    video.play();
                    resolve();
                };
            });
        });

    var publishable_key = "rf_fdUtmgtJyWMPdCGBnSBg2A90ZU73";
    var toLoad = {
        model: "atm-security-v3",
        version: 1
    };

    const loadModelPromise = new Promise(function (resolve, reject) {
        roboflow
            .auth({
                publishable_key: publishable_key
            })
            .load(toLoad)
            .then(function (m) {
                model = m;
                model.configure({
                    threshold: 0.5,
                    overlap: 0.5,
                    max_objects: 20
                });
                resolve();
            });
    });

    Promise.all([startVideoStreamPromise, loadModelPromise]).then(function () {
        $("body").removeClass("loading");
        resizeCanvas();
        detectFrame();
    });

    var canvas, ctx;
    const font = "16px sans-serif";

    function videoDimensions(video) {
        // Ratio of the video's intrisic dimensions
        var videoRatio = video.videoWidth / video.videoHeight;

        // The width and height of the video element
        var width = video.offsetWidth,
            height = video.offsetHeight;

        // The ratio of the element's width to its height
        var elementRatio = width / height;

        // If the video element is short and wide
        if (elementRatio > videoRatio) {
            width = height * videoRatio;
        } else {
            // It must be tall and thin, or exactly equal to the original ratio
            height = width / videoRatio;
        }

        return {
            width: width,
            height: height
        };
    }

    $(window).resize(function () {
        resizeCanvas();
    });

    // Event listener for 'w' key press
    $(window).keydown(function (event) {
        // Check if the 'w' key was pressed
        if (event.which === 87) {  // ASCII code for 'w' is 87
            // Stop current recording if any
            if (mediaRecorder && mediaRecorder.state === "recording") {
                mediaRecorder.stop();
            }

            // Reset firstInstance to true to start a new recording
            firstInstance = true;

            // Clear past chunks
            chunks = [];
        }
    });

    const resizeCanvas = function () {
        $("canvas").remove();

        canvas = $("<canvas/>");

        ctx = canvas[0].getContext("2d");

        var dimensions = videoDimensions(video);

        console.log(
            video.videoWidth,
            video.videoHeight,
            video.offsetWidth,
            video.offsetHeight,
            dimensions
        );

        canvas[0].width = video.videoWidth;
        canvas[0].height = video.videoHeight;

        canvas.css({
            width: dimensions.width,
            height: dimensions.height,
            left: ($(window).width() - dimensions.width) / 2,
            top: ($(window).height() - dimensions.height) / 2
        });

        $("body").append(canvas);
    };

    const renderPredictions = function (predictions) {

        var scale = 1;

        //ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);

        predictions.forEach(function (prediction) {
            const x = prediction.bbox.x;
            const y = prediction.bbox.y;

            const width = prediction.bbox.width;
            const height = prediction.bbox.height;

            // Draw the bounding box.
            ctx.strokeStyle = prediction.color;
            ctx.lineWidth = 4;
            ctx.strokeRect(
                (x - width / 2) / scale,
                (y - height / 2) / scale,
                width / scale,
                height / scale
            );

            // Draw the label background.
            ctx.fillStyle = prediction.color;
            const textWidth = ctx.measureText(prediction.class).width + 50;
            const textHeight = parseInt(font, 10); // base 10
            ctx.fillRect(
                (x - width / 2) / scale,
                (y - height / 2) / scale,
                textWidth + 8,
                textHeight + 4
            );
        });

        predictions.forEach(function (prediction) {
            const x = prediction.bbox.x;
            const y = prediction.bbox.y;

            const width = prediction.bbox.width;
            const height = prediction.bbox.height;

            const confidence = prediction.confidence ? parseFloat(prediction.confidence).toFixed(2) : '?';
            const label = `${prediction.class} (${confidence})`;  // Combine class and confidence

            // Draw the text last to ensure it's on top.
            ctx.font = font;
            ctx.textBaseline = "top";
            ctx.fillStyle = "#000000";
            ctx.fillText(
                label,
                (x - width / 2) / scale + 4,
                (y - height / 2) / scale + 1
            );
        });
    };

    var prevTime;
    var pastFrameTimes = [];

    let mediaRecorder;
    let chunks = [];
    let firstInstance = true;

    const detectFrame = function () {
        if (!model) return requestAnimationFrame(detectFrame);

        model
            .detect(video)
            .then(function (predictions) {
                requestAnimationFrame(detectFrame);
                console.log(predictions);


                ctx.drawImage(video, 0, 0, video.videoWidth, video.videoHeight);
                renderPredictions(predictions);

                if (predictions.length > 0 && firstInstance) {
                    firstInstance = false;

                    // Capture canvas stream instead of video stream
                    const canvasStream = canvas[0].captureStream();  // No frame rate specified
                    mediaRecorder = new MediaRecorder(canvasStream);




                    mediaRecorder.ondataavailable = function (e) {
                        console.log('Data available:', e);
                        chunks.push(e.data);
                    };



                    /*    mediaRecorder.onstart = function () {
                        console.log('MediaRecorder started', mediaRecorder.state);
                    };
                    mediaRecorder.onstop = function () {
                        console.log('MediaRecorder stopped', mediaRecorder.state);
                    }; */

                    mediaRecorder.onstop = function () {
                        const blob = new Blob(chunks, { 'type': 'video/webm' });
                        chunks = [];

                        const formData = new FormData();
                        formData.append('video', blob); // blob is your video blob object
                        axios.post('http://localhost:3000/upload', formData, {
                            headers: {
                                'Content-Type': 'multipart/form-data'
                            }
                        })
                            .then(response => {
                                console.log('Video uploaded and email sent:', response);
                            })
                            .catch(error => {
                                console.log('Failed to upload or send email:', error);
                            });


                        /*   // TODO: Upload the video file to a server or email it.
                           const url = URL.createObjectURL(blob);
                           const a = document.createElement("a");
                           a.style.display = "none";
                           a.href = url;
                           a.download = 'recorded-video.webm';
                           document.body.appendChild(a);
                           a.click();
                           window.URL.revokeObjectURL(url); */
                    };

                    mediaRecorder.onerror = function (e) {
                        console.error('MediaRecorder error:', e);
                    };

                    mediaRecorder.start();
                    setTimeout(() => mediaRecorder.stop(), 15000);  // stop recording after 15 seconds

                }

                // ... (existing code for FPS calculation)
                if (prevTime) {
                    pastFrameTimes.push(Date.now() - prevTime);
                    if (pastFrameTimes.length > 30) pastFrameTimes.shift();

                    var total = 0;
                    _.each(pastFrameTimes, function (t) {
                        total += t / 1000;
                    });

                    var fps = pastFrameTimes.length / total;
                    $("#fps").text(Math.round(fps));
                }
                prevTime = Date.now();
            })
            .catch(function (e) {
                console.log("CAUGHT", e);
                requestAnimationFrame(detectFrame);
            });
    };

});
