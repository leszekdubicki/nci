
from flask import Flask, render_template, request, url_for

# Initialize the Flask application
app = Flask(__name__)

# Define a route for the default URL, which loads the form
@app.route('/')
def form():
    return render_template('index.html')
    #return "wtf???"

@app.route('/procdetails/', methods=['POST'])
def procdetails():
    return "something "+ request.form['noOfProcs']

# Run the app :)
if __name__ == '__main__':
  app.run()