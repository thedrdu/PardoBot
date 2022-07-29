from flask import Flask

app = Flask(__name__) 
#creates the application object as an instance of class Flask imported from the flask package
#_name_ is predefined as the name of the module in which it is used

from app import routes
#routes needs to import app so we put it below
#routes are the different URLs that the application implements