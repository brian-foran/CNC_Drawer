from flask import Flask, request, render_template

import sys
import os
from Final2 import cnc_machine


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_script', methods=['POST'])
def run_script():
    # Add code here to run your Python script
    topic = request.form.get('arg1')
    com_port = request.form.get('arg2')
    cnc_machine(topic, com_port)
    return 'Script executed successfully!'

if __name__ == '__main__':
    app.run(host='192.168.1.135', port=5000, debug=True)

