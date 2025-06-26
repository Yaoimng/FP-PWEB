# Hugging Face Space Configuration
This file contains configuration for the Hugging Face Space.

## Folders and Files

- The `static/uploads/covers` directory is used for storing uploaded book cover images.
- Actual image files are not included in the repository to comply with Hugging Face's binary file policies.
- When running the application in Hugging Face Space, you'll need to manually upload sample images or the application will use a placeholder.

## Running the Application

To run this application in Hugging Face Space:

1. The Dockerfile is configured to automatically create the required directories.
2. The application will start on port 5000.

## Managing Images

Since the binary image files are excluded from the repository, you have a few options:

1. When users upload new images through the application, they will be stored in the container's filesystem.
2. For persistent storage of images beyond the container's lifecycle, consider integrating with an external service like S3, GCP Storage, or similar.

## Environment Variables

Make sure to set these environment variables in Hugging Face Space:
- DB_HOST
- DB_USER
- DB_PASSWORD
- DB_NAME
- JWT_SECRET_KEY
