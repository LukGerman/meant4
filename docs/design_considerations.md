# Detailed Design Choices

### **Web Framework**
**FastAPI** was chosen for its support of asynchronous endpoints and WebSocket features, while being lightweight and requiring minimal setup. Compared to Django, FastAPI is better suited for this use case due to its simplicity and modern design.

### **Face Detection Model**
There is a wide variety of face detection models available. At a high level, these can be categorized into: **CPU-based models** and **GPU-based models**.

Since portability is a key requirement, only CPU-based models were considered, as there is no guarantee that the server will have access to GPU acceleration.

**Chosen Model**: YuNet, a lightweight CPU-based model, was selected for this task. YuNet is efficient, offers reliable performance across diverse scenarios, and has low latency, making it ideal for near real-time face detection.  
*(Source: [Medium article on face detection models](https://medium.com/pythons-gurus/what-is-the-best-face-detector-ab650d8c1225))*

### **Concurrency**
The most performance-intensive endpoint is `POST /image`, which involves image processing, face detection, I/O operations, and WebSocket broadcasting.

1. **File Decoding and Validation**:  
   The input file is decoded and validated asynchronously within the FastAPI endpoint. If errors (e.g., invalid file format) are detected, they are returned to the client immediately.

2. **Background Tasks**:  
   Two background tasks are registered after successful validation:
   - **Face Detection**: This task uses YuNet to detect faces and saves the annotated image using OpenCV. It runs in a separate thread via FastAPI’s `BackgroundTasks` feature, ensuring that the main event loop remains unblocked.  
     YuNet’s low latency allows it to perform face detection in near real-time, eliminating the need for parallel face detection processes.  
     *(Source: [Springer article](https://link.springer.com/article/10.1007/s11633-023-1423-y))*
   - **WebSocket Broadcasting**: After face detection is complete, the URL of the generated image is broadcast asynchronously using the WebSocket connection.

3. **Immediate Response**:  
   The API sends a response to the client right after initiating the background tasks, without waiting for their completion. This approach ensures a responsive and non-blocking user experience.

### **Media Storage**
Volatile disk storage within the Docker container was selected for storing processed images. This is a pragmatic and lightweight solution suitable for the scope of this task.

### **Model Initialization**
To accurately detect faces in images of varying sizes, the `FaceDetector` class uses YuNet's `setInputSize` method to dynamically adjust the model’s `input_size` parameter based on the input image shape.

Concurrent requests to `POST /image` could lead to a race condition, as each request would overwrite the shared model configuration, potentially producing incorrect detection results.

The model is instantiated within the `FaceDetector` class, which is provided as a FastAPI dependency. This ensures that a new instance of the model is created for each request, isolating request processing and avoiding conflicts.
