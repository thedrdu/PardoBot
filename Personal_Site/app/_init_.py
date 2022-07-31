from flask import Flask
# from waitress import serve

app = Flask(__name__) 
#creates the application object as an instance of class Flask imported from the flask package
#_name_ is predefined as the name of the module in which it is used
# serve(app, host='0.0.0.0', port=80)
if __name__ == "__main__":
    app.run(host='18.188.129.222',port=80)

from app import routes
#routes needs to import app so we put it below
#routes are the different URLs that the application implements