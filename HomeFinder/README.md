# HomeFinder - Real Estate Listings Platform

HomeFinder is a modern, responsive, and fully functional real estate web application built with Python (Flask) and MySQL. It allows users to browse properties, filter by various criteria, save their favorites, and contact property agents. Authorized agents and admins can add, edit, and delete properties.

## Features

- **Responsive Design**: Professional UI/UX using pure HTML/CSS and Lucide Icons, perfectly responsive on desktop, tablet, and mobile devices.
- **Advanced Search & Filtering**: Filter properties by location, type, price range, and status (Sale/Rent).
- **User Authentication**: Secure user registration and login with password hashing.
- **Role-based Access Control**: 
  - *Users* can view properties and save favorites.
  - *Agents/Admins* have access to a dashboard to manage listings (Add/Edit/Delete).
- **Favorites System**: Users can save properties they like to their profile.
- **Inquiry System**: Built-in contact forms on every property detail page.

## Project Structure

```
HomeFinder/
├── app.py                  # Main Flask application and routes
├── config.py               # Configuration and environment variables
├── requirements.txt        # Python dependencies
├── schema.sql              # MySQL database schema and sample data
├── .env.example            # Template for environment variables
├── README.md               # Documentation
├── utils/
│   ├── database.py         # Database connection and execution utilities
│   └── validators.py       # Input validation utilities
├── templates/              # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html
│   └── ...
└── static/                 # CSS, JavaScript, and Images
    ├── css/style.css
    └── js/script.js
```

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8+
- MySQL Server
- Git (optional, for version control)
- Visual Studio Code (recommended IDE)

## Local Setup Instructions (Windows)

1. **Open the Project Folder**
   Open Visual Studio Code, click `File > Open Folder`, and select the `HomeFinder` directory.

2. **Create a Virtual Environment**
   Open the integrated terminal in VS Code (`Ctrl + ~`) and run:
   ```cmd
   python -m venv venv
   ```

3. **Activate the Virtual Environment**
   ```cmd
   venv\Scripts\activate
   ```
   *(You should see `(venv)` appear at the beginning of your terminal prompt)*

4. **Install Dependencies**
   ```cmd
   pip install -r requirements.txt
   ```

5. **Configure the Database (MySQL)**
   - Open MySQL Workbench or your preferred MySQL client.
   - Run the SQL queries provided in `schema.sql`. This will create the database `homefinder_db`, create the necessary tables, and insert some sample data (including an admin and agent account).
   
   *Demo Accounts created by default:*
   - Agent: `john@example.com` | Password: `password123`
   - Admin: `admin@homefinder.com` | Password: `password123`

6. **Environment Variables**
   - Rename `.env.example` to `.env`.
   - Open the `.env` file and update `DB_PASSWORD` with your actual MySQL root password (if you are using the root user).

7. **Run the Application**
   In the terminal, ensure your virtual environment is activated, and run:
   ```cmd
   python app.py
   ```
   *Note: Do not try to open the HTML files directly in your browser or use "Live Server". They must be served by Flask.*

8. **View the Website**
   Open your web browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

## Troubleshooting Common Errors

- **`ModuleNotFoundError: No module named 'flask'`**: You forgot to activate your virtual environment before running the app, or forgot to run `pip install -r requirements.txt`.
- **Database connection error**: Ensure MySQL is running on your machine and that the credentials in your `.env` file perfectly match your MySQL setup.
- **Port 5000 in use**: If another app is using port 5000, modify `app.run(debug=True, port=5000)` at the bottom of `app.py` to use a different port, e.g., `port=5001`.

## Deployment Instructions

To deploy this application to the web so others can see it, you will need a backend host (like Render, Heroku, or PythonAnywhere) and a managed MySQL database (like Aiven or PlanetScale). 
*Note: You cannot deploy a Python Flask backend to Netlify or GitHub Pages, as they only support static frontend files.*

### Deploying to Render
1. Push this entire project folder to a new repository on GitHub.
2. Sign up for Render (render.com).
3. First, create a **New PostgreSQL** database on Render (Render doesn't natively host MySQL for free, so you'd either modify the code to use PostgreSQL via psycopg2, or use a third-party free MySQL host like Aiven and skip this step). Assuming you use Aiven for MySQL:
   - Create a free MySQL database on Aiven.
   - Get the connection URI/details.
4. On Render, create a **New Web Service**.
5. Connect your GitHub repository.
6. Configure the Web Service:
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app` (You will need to add `gunicorn==21.2.0` to your `requirements.txt` first!)
7. In the Render dashboard, click on **Environment** and add all the variables from your `.env` file (e.g., `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `SECRET_KEY`).
8. Click **Deploy**.

## Future Improvements for Students

If you want to expand this project further for your college mentors, consider adding:
1. **Image Uploads**: Currently, image URLs are used. Implement File Uploads using Flask-Uploads to save images locally or to AWS S3.
2. **Password Reset**: Implement an email service (like SendGrid or Flask-Mail) to allow users to reset forgotten passwords.
3. **Pagination**: If you have hundreds of properties, update the `/listings` route and template to paginate results (e.g., 10 per page).
4. **Interactive Maps**: Integrate Google Maps API or Mapbox to show property locations on a map on the details page.
