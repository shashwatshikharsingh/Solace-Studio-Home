# Solace Studio Website

**This project is a Flask web application with Tailwind CSS for styling.**

# Authors

- [Shashwat Shikhar Singh](https://github.com/shashwatshikharsingh)
- [Hardik Sharma](https://github.com/hardiksharma23)
- [Tushar Harsan](https://github.com/TusharHarsan)
- [Rachell](https://github.com/Richie3935)

# Project Overview

Welcome to Solace Studio web application, an intuitive and dynamic platform designed with both users and administrators in mind. This application is built using Flask, a lightweight WSGI web application framework, and incorporates Jinja2 for template rendering, Tailwind CSS for responsive styling, and SQLite3 for database management. Our Website offers a comprehensive suite of features that cater to a wide range of functionalities, from content management to event organization, ensuring a seamless experience for both our management and our users.

## Features

Our application boasts a fully dynamic interface with specialized admin features to manage and curate content effectively. Here's a glimpse into what our platform offers:

- **Dynamic Pages:** Home Page, About Page, Error (Apology Page), and more, providing a rich user experience.
- **Admin Features:** Approve Games, Add Core Members, Manage Events, Games, Newsletters, Users, and more, for full administrative control.
- **Event Management:** All Events Done Page and Individual Events Blog Page to showcase past and upcoming events.
- **Game Showcase:** All Games Showcase Page and Submit Games Page for highlighting and managing game submissions.
- **User Management:** Dedicated pages for user registration (register.html), login (login.html), and submissions (submit_event.html), enhancing the user engagement.
- **Responsive Design:** Leveraging Tailwind CSS for a mobile-first, responsive design.

## Getting Started

### Prerequisites

Ensure you have the following installed before you begin:

- Python 3.6 or later
- Node.js and npm (for Tailwind CSS installation and management)

### Installation

Follow these steps to get your development environment up and running:

1. **Clone the repository:**

   ```
   git clone https://github.com/Solace-Studio/home.git
   ```

2. **Install Python dependencies:**

   ```
   pip install -r requirements.txt
   ```

3. **Install Node.js dependencies (for Tailwind CSS):**

   ```
   npm install
   ```

### Running the Application

To launch the application, follow these steps:

1. **Start the Flask development server:**

   ```
   flask run
   ```

2. **Access the application via your browser:**

   ```
   http://127.0.0.1:5000/
   ```

### Development Tools

- **Tailwind CSS Compilation:** Use `npm run buildcss` to watch and compile Tailwind CSS automatically during development.

## Project Structure

A brief overview of the project structure to help you navigate the codebase:

```
project/
├── app/  # Flask application core
│   ├── __init__.py  # Application factory
│   ├── app.py      # Main application file
│   └── ...
├── static/  # Static files (CSS, JS, images)
│   └── output.css # Compiled Tailwind CSS
│   └── ...
├── templates/  # Jinja2 templates for rendering HTML
│   └── index.html
│   └── ...
├── requirements.txt  # Python dependencies
├── package.json      # Node.js dependencies
├── README.md
└── ...
```

# Deployment
## Deployment Guide for Solace Studio Website

Deploying a our Website on a Linux VPS, such as DigitalOcean, involves several steps, from setting up the server to configuring the web server and running the Flask app. This guide will walk you through the process, ensuring your Flask application is securely and efficiently hosted.

## Step 1: Setting Up Your Server

1. **Create a Droplet:**
   - Log into your DigitalOcean dashboard and create a new droplet.
   - Choose an image (e.g., Ubuntu 20.04 LTS) and a plan that suits your application's needs.
   - Select a data center region.
   - Add SSH keys for secure access.
   - Click the "Create Droplet" button.

2. **Access Your Droplet:**
   - Use SSH to log into your droplet. Replace `your_server_ip` with your droplet's IP address.
     ```
     ssh root@your_server_ip
     ```

3. **Update Your Server:**
   - Update the package lists and upgrade the installed packages to their latest versions.
     ```
     apt update && apt upgrade -y
     ```

## Step 2: Installing Python and Required Packages

1. **Install Python 3 and pip:**
   ```
   apt install python3-pip python3-dev -y
   ```

2. **Install Virtualenv:**
   ```
   pip3 install virtualenv
   ```

## Step 3: Setting Up Your Flask Application

1. **Upload Your Application:**
   - Use `scp`, GitHub, or any method you prefer to upload your Flask application to your server.

2. **Create a Virtual Environment:**
   - Navigate to your app's directory and create a virtual environment.
     ```
     virtualenv venv
     ```
   - Activate the virtual environment.
     ```
     source venv/bin/activate
     ```

3. **Install Dependencies:**
   - Install the dependencies specified in your `requirements.txt`.
     ```
     pip install -r requirements.txt
     ```

## Step 4: Configuring Gunicorn

1. **Install Gunicorn:**
   ```
   pip install gunicorn
   ```

2. **Run Your Flask Application with Gunicorn:**
     ```
     gunicorn --workers 3 --bind unix:app.sock -m 007 app:app
     ```

## Step 5: Setting Up Nginx as a Reverse Proxy

1. **Install Nginx:**
   ```
   apt install nginx -y
   ```

2. **Configure Nginx:**
   - Create a new Nginx server block configuration.
     ```
     nano /etc/nginx/sites-available/app
     ```
   - Insert the following configuration.
     ```nginx
     server {
         listen 80;
         server_name solacestudio.online www.solacestudio.online;

         location / {
             include proxy_params;
             proxy_pass http://unix:/app.sock;
         }
     }
     ```
   - Enable the configuration by linking it to the sites-enabled directory.
     ```
     ln -s /etc/nginx/sites-available/app /etc/nginx/sites-enabled
     ```

3. **Restart Nginx:**
   ```
   systemctl restart nginx
   ```

## Step 6: Securing Your Application with SSL/TLS

1. **Install Certbot:**
   ```
   apt install certbot python3-certbot-nginx -y
   ```

2. **Obtain an SSL/TLS Certificate:**
     ```
     certbot --nginx -d solacestudio.online -d www.solacestudio.online
     ```

3. **Automate Renewal:**
   - Certbot will automatically add a cronjob to renew the certificates.

## Step 7: Final Steps

- Ensure your firewall is configured to allow traffic on ports 80 and 443.
- Test your application by accessing your domain name in a browser.

Congratulations! Solace Studio Website is now deployed on a Linux VPS with Gunicorn and Nginx, secured with SSL/TLS certificates from Let's Encrypt. Remember to regularly update your server and application dependencies to keep your deployment secure.

## Contributing

We welcome contributions from the community. If you're interested in enhancing the features, fixing bugs, or improving documentation, please fork the repository and submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE.md) - see the LICENSE file for details.

---

This README aims to provide a comprehensive overview of our Flask web application, making it easier for developers and administrators to understand, set up, and contribute to the project.
