from flask import Flask, request, render_template
from API_Files.aws_s3 import upload_to_s3
import API_Files.update_photon as update_photon
from API_Files.update_pages import push_env_json

import sys
import os
from server_CNC_master import cnc_machine
import threading


app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

def run_CNC(topic, port = 3):
    topic = topic.replace("_", " ")

    #allow user to input that it is local - will not upload to s3 or update the env.json
    if topic.endswith(".local"):
        local = True
    else:
        local = False


    #check if it is just a test
    if topic == "test":
        print("Test mode")
        return 'Test mode'
    
    update_photon.write_to_particle_variable("CNC_Start")
    com_port = 3
    print(topic)

    try:
        video_file = cnc_machine(topic, local, image = None)

        if video_file:
            s3_url = upload_to_s3(video_file)
            print("Video uploaded to GitHub Pages!")
            if s3_url:
                push_env_json(s3_url, topic)
            else:
                print("Video not uploaded to S3")
                return 'Script failed to execute'
        
        else:
            print("Video not uploaded to GitHub Pages.")
            return 'Script failed to execute'
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return 'Script failed to execute'

    update_photon.write_to_particle_variable("CNC_Done")

    print("done")
    return 'Script executed successfully!'

@app.route('/run_script', methods=['GET'])
def run_script():
    # Add code here to run your Python script
    threading.Thread(target=run_CNC, args=(request.args.get('topic'), 3)).start()

    print("Script started and running in thread!")
    return 'Script started!'
    
def run_image_upload_cnc(file_path):   
    # Start CNC script with the new image
    try:
        video_file = cnc_machine("Local", local = True, image = file_path)
    except Exception as e:
        print(f"An error occurred: {e}")
        return 'Image Processing failed to execute'   

@app.route("/upload", methods=["POST"])
def upload_file():
    """Handles image uploads from users."""
    if "file" not in request.files:
        return "No file part", 400

    file = request.files["file"]
    if file.filename == "":
        return "No selected file", 400
    
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    print(f"File saved: {file_path}")
    
    threading.Thread(target=run_image_upload_cnc, args=(file_path,)).start()

    return "File uploaded and processing started!", 200

if __name__ == '__main__':
    #app.run(host='192.168.1.136', port=5000, debug=True)
    app.run(host="0.0.0.0", port=5000, debug=True)

