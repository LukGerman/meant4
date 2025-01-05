# Meant4 Face Detector  

This project implements a recruitment process task described in [task.md](docs/task.md).  

## Getting Started  

### Prerequisites  
Ensure Docker is installed on your local system. For installation instructions, visit: https://www.docker.com/get-started/.  

### Running locally using Docker

1. Clone this repository to your local system.  
2. Open your terminal and navigate to the root folder of the project (the folder containing this README file).  
3. Build the Docker image by running:  
   ```bash
   docker build -t meant4 .
   ```
4. Run the Docker container:
   ```bash
   docker run -d -p 8000:8282 meant4
   ```
5. Open your browser and navigate to http://localhost:8000. This page will display recognized images for testing purposes.
6. To test the API:
    * Visit the API documentation at http://localhost:8000/docs#/default/create_image_image_post.
    * Use the Swagger interface to upload a file to the `/image` endpoint. A sample test image can be downloaded from https://freerangestock.com/sample/121690/a-group-of-people-taking-a-group-selfie.jpg.

## Design Considerations  

The general design principles and detailed justifications for the decisions made in this project are outlined in [design_considerations.md](docs/design_considerations.md).





