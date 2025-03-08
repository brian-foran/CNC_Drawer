from flask import Flask, request, render_template
from API_Files.aws_s3 import upload_to_s3
import API_Files.update_photon as update_photon
from API_Files.update_pages import push_env_json

import sys
import os
from server_CNC_master import cnc_machine


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_script', methods=['GET'])
def run_script():
    # Add code here to run your Python script
    topic = request.args.get('topic')
    topic = topic.replace("_", " ")

    #check if it is just a test
    if topic == "test":
        print("Test mode")
        #update_photon.write_to_particle_variable("CNC_Start")
        return 'Test mode'
    
    update_photon.write_to_particle_variable("CNC_Start")
    com_port = 3
    print(topic)

    video_file = cnc_machine(topic, com_port)

    if video_file:
        upload_to_s3(video_file)
        print("Video uploaded to GitHub Pages!")
        push_env_json(video_file, topic) 
    
    else:
        print("Video not uploaded to GitHub Pages.")
        return 'Script failed to execute'

    update_photon.write_to_particle_variable("CNC_Done")

    print("done")
    return 'Script executed successfully!'

if __name__ == '__main__':
    #app.run(host='192.168.1.136', port=5000, debug=True)
    app.run(host="0.0.0.0", port=5000, debug=True)

