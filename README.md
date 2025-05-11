# therooms
Flask-based web application where users can log in, create, and decorate virtual rooms. The application allows users to save, edit, and manage their room designs with a drag-and-drop editor.

## Features
- User registration, login, and password reset via email.
- Create and decorate virtual rooms using a drag-and-drop editor.
- Admin panel for managing users.
- Rooms and user data stored in an SQLite database.
- Email integration for password reset (using Flask-Mail).

## Technologies Used
- Python & Flask
- HTML, CSS, JavaScript
- SQLite
- Flask-Mail (for email functionality)


  ## Installation Instructions

### Clone the repository
First, you'll need to clone the project repository from GitHub to your local machine. Open your terminal and run the following command:

git clone https://github.com/AnaKopadze01/therooms.git
cd therooms


### Set up a virtual environment
For macOS/Linux:
python3 -m venv venv
source venv/bin/activate

For Windows:
python -m venv venv
venv\Scripts\activate

### Install the required dependencies
With the virtual environment activated, install all the necessary Python libraries specified in the requirements.txt file:
pip install -r requirements.txt

### Set up environment variables
You need to create a .env file in the root of your project directory.

Example .env file:
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your_secret_key
MAIL_SERVER=smtp.yourmail.com
MAIL_PORT=587
MAIL_USERNAME=your_email@example.com
MAIL_PASSWORD=your_email_password
MAIL_USE_TLS=True

Replace the placeholders with your actual values.


### Run the application
In your terminal, make sure your virtual environment is still activated, and run:
flask run

This will start the development server and open it in your browser (http://localhost:5001).




