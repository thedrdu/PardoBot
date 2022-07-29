from app._init_ import app

@app.route('/') #decorator
@app.route('/index') #decorator
def index():
    return "Hello, World!"