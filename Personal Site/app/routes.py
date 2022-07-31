from flask import render_template, redirect, url_for, request #rendering converts templates into complete html pages
from app._init_ import app

@app.route('/') #decorator
@app.route('/index') #decorator
def index():
    return render_template('index.html', title='Home')
