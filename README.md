# therooms
Flask-based web application where users can log in, create, and decorate virtual rooms. The application allows users to save, edit, and manage their room designs with a drag-and-drop editor.

## Features
- User registration, login, and password reset via email.
- Create and decorate virtual rooms using a drag-and-drop editor.
- Admin panel for managing users.
- Rooms and user data stored in an SQLite database.
- Email integration for password reset (using Flask-Mail).


## Installation Instructions

### 1. Clone the repository
First, clone the project repository from GitHub to your local machine. Open your terminal and run the following command:
`git clone https://github.com/AnaKopadze01/therooms.git `
`cd therooms`


### 2. Set up a virtual environment
For macOS/Linux:
```python3 -m venv venv
source venv/bin/activate```

For Windows:
```python -m venv venv
venv\Scripts\activate```


### 3. Install the required dependencies
With the virtual environment activated, install all the necessary Python libraries specified in the requirements.txt file:
`pip install -r requirements.txt`


### 4. Set up environment variables
You need to create a .env file in the root of your project directory. The file should look like this:

Example .env file:
```FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your_secret_key_here

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=465
MAIL_USE_SSL=True
MAIL_USERNAME=your_email@example.com
MAIL_PASSWORD=your_email_password
MAIL_DEFAULT_SENDER=your_email@example.com```

Replace the placeholders with your actual values.


### 5. Run the application
nce the environment is set up, run the Flask application with:
`flask run`

The development server will start and you can access the application at http://localhost:5001 in your browser.




## Running with Docker

If you want to run the project inside Docker, follow these additional steps:

### 1. Build the Docker image:
From the root of the project directory, build the Docker image using the following command:
`docker build -t therooms-app .`


### 2. Run the Docker container:
Run the Docker container with the command below, mapping the port 5001 on your machine to the Docker container’s port 5001:
`docker run -p 5001:5001 --env-file .env therooms-app`

The app will be available at http://localhost:5001 in your browser.


