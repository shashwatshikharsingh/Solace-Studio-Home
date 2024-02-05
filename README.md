 **# Getting Started with Solace Webpage**

**This project is a Flask web application with Tailwind CSS for styling.**

## Prerequisites

- Python 3.6 or later
- Node.js and npm (for Tailwind CSS)

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Solace-Studio/home.git
   ```


2. **Install Python dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Install Node.js dependencies:**

   ```bash
   npm install
   ```


## Running the application

1. **Start the development server:**

   ```bash
   flask run
   ```

2. **Access the application in your browser:**

   ```
   http://127.0.0.1:5000/
   ```

## Watching Tailwind CSS

To automatically recompile Tailwind CSS when you make changes to your CSS files, run:

```bash
npm buildcss
```

This will start a watcher that monitors for changes and recompiles the CSS.

## Project Structure

```
homepage/
├── app/  # Flask application files
│   ├── __init__.py
│   ├── routes.py
│   └── ...
├── static/  # Static assets (CSS, JavaScript, images)
│   └── tailwind.css
├── templates/  # Jinja2 templates
│   └── index.html
├── requirements.txt
├── package.json
├── README.md
└── ...
```
