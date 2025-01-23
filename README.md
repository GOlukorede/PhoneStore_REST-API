# Flask RESTx API for a Phone Store

This project is an **ALX final project** designed to provide comprehensive RESTful API endpoints for building a microservice-based web application for managing a phone store.

## Features

This API utilizes various Flask technologies to deliver a robust and efficient backend system:

- **Database Management**: Powered by **Flask-SQLAlchemy** for ORM-based interactions.
- **Authentication**: Secured endpoints with **Flask-JWT-Extended** for JWT authentication.
- **Environment Management**: Seamlessly manage configuration using **Python-Decouple**.
- **Database Migrations**: Handle database schema changes using **Flask-Migrate**.
- **API Documentation**: Interactive documentation with **SwaggerUI** integrated via **Flask-RESTx**.
- **Testing**: Reliable test coverage using Python’s built-in **unittest** module.
- **Error Handling**: Robust error handling with **Werkzeug**.

---

## Getting Started

Follow these steps to set up and run the project locally.

### Prerequisites

Ensure the following are installed on your system:

- Python 3.8 or later
- Git

### Setup Instructions

1. **Clone the Repository**  
   Clone the project repository from GitHub:  
   ```bash
   git clone https://github.com/GOlukorede/PhoneStore_REST-API.git

2. **Navigate to the Project Folder**
    ```bash
   cd PhoneStore_REST-API

3. **Create a Virtual Environment**
   Create a virtual environment to manage dependencies:
   ```bash
   python -m venv .venv

4. **Activate Virtual Environment**
   ```bash
   On Linux or macOS:
   source .venv/bin/activate

   On Windows:
    .venv\Scripts\activate

5. **Install Required Dependencies**
   Install all necessary Python packages:
   ```bash
   pip install -r requirements.txt

6. **Set Environment Variables**
   Export the required Flask environment variables:
   ```bash
   On Linux/macOS:
   export FLASK_APP=api/
   export FLASK_DEBUG=1

    On Windows (Command Prompt):
    set FLASK_APP=api/
    set FLASK_DEBUG=1

7.  **Run the Application**
     Start the Flask development server:
     ```bash
     flask run

## **HOW IT WORKS**
**Admin related operations**
- Add, update, and delete products
- View user details and delete users

## **Author**
- Olukorede Samson Gbenga

## **Acknowledgments**
**Special thanks to ALX for the scholarship and the excellent training offered to me.**


