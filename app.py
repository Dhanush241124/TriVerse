from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'techembedinnov2024secretkey'

# Database initialization
def init_db():
    conn = sqlite3.connect('techembeddb.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS internship_applications
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  email TEXT NOT NULL,
                  phone TEXT NOT NULL,
                  program TEXT NOT NULL,
                  message TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS workshop_registrations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  email TEXT NOT NULL,
                  phone TEXT NOT NULL,
                  workshop TEXT NOT NULL,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS contact_messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  email TEXT NOT NULL,
                  phone TEXT NOT NULL,
                  message TEXT NOT NULL,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/internships', methods=['GET', 'POST'])
def internships():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        program = request.form.get('program')
        message = request.form.get('message', '')
        
        conn = sqlite3.connect('techembeddb.db')
        c = conn.cursor()
        c.execute('INSERT INTO internship_applications (name, email, phone, program, message) VALUES (?, ?, ?, ?, ?)',
                  (name, email, phone, program, message))
        conn.commit()
        conn.close()
        
        flash('Application submitted successfully! We will contact you soon.', 'success')
        return redirect(url_for('internships'))
    
    return render_template('internships.html')

@app.route('/workshops', methods=['GET', 'POST'])
def workshops():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        workshop = request.form.get('workshop')
        
        conn = sqlite3.connect('techembeddb.db')
        c = conn.cursor()
        c.execute('INSERT INTO workshop_registrations (name, email, phone, workshop) VALUES (?, ?, ?, ?)',
                  (name, email, phone, workshop))
        conn.commit()
        conn.close()
        
        flash('Registration successful! Check your email for details.', 'success')
        return redirect(url_for('workshops'))
    
    return render_template('workshops.html')

@app.route('/projects')
def projects():
    return render_template('projects.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        
        conn = sqlite3.connect('techembeddb.db')
        c = conn.cursor()
        c.execute('INSERT INTO contact_messages (name, email, phone, message) VALUES (?, ?, ?, ?)',
                  (name, email, phone, message))
        conn.commit()
        conn.close()
        
        flash('Message sent successfully! We will get back to you soon.', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
