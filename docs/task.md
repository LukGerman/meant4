## Task: Real-Time Face Detection and Image Generation Server

### Description:
You are tasked with developing a server application that receives an image via a POST request,
detects faces in the provided image, generates a new image with the detected faces marked,
and returns a URL to the new image using websockets. Additionally, you need to create an
endpoint for serving the generated image.

### Requirements:
1. Implement a server using Python with a framework such as Django.
2. Set up an endpoint to receive an image via a POST request: /image
3. Use a face detection algorithm to find coordinates of faces in the provided image.
4. Generate a new image with the detected faces marked as bounding boxes around the
faces.
5. Implement websockets to send the URL of the generated image to all connected clients
in real-time. Websocket endpoint: /faces
6. Serve the generated image using an endpoint with a unique URL.
7. Ensure that the server handles errors gracefully and provides informative error
messages when necessary.
8. The app must be running in a docker container on port 8282

### Submission Guidelines:
1. Submit your code via a Git repository (GitHub, GitLab, etc.).
2. Include a README.md file with instructions on how to run the server.
3. Provide any necessary setup/configuration instructions.
4. Optionally, include any additional notes or explanations about your implementation
choices.
5. Send a link to the Git repository to info@meant4.com