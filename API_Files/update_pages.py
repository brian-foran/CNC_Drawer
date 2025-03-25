import os
import subprocess
import json

def push_env_json(new_url, new_topic, commit_message="Update env.json"):
    repo_path = r"C:\Users\bfora\Documents\GitHub\draw"
    """Creates env.json, pushes edits in the given repository, and returns to the original directory."""
    original_path = r"C:\Users\bfora\Documents\GitHub\CNC_DRAWER"
    try:
        # Ensure we're in the correct repo directory
        os.chdir(repo_path)
        
        # Create the env.json file with the desired dictionary format
        with open('env.json', 'r') as file:
            env_data = json.load(file)        
        env_data["video_4"] = env_data["video_3"]
        env_data["video_3"] = env_data["video_2"]
        env_data["video_2"] = env_data["video_1"]
        env_data["video_1"] = {"video_url": new_url,
                               "video_topic": new_topic}

        with open("env.json", "w") as f:
            json.dump(env_data, f, indent=4)
        
        # Add the file to staging
        subprocess.run(["git", "add", "env.json"], check=True)
        
        # Commit the change
        subprocess.run(["git", "commit", "-m", commit_message], check=True)

        # Pull the latest changes from the remote repository
        subprocess.run(["git", "pull", "--rebase"], check=True)
        
        # Push the commit to the repository
        subprocess.run(["git", "push"], check=True)
        
        print("Successfully pushed env.json changes.")
    except subprocess.CalledProcessError as e:
        print(f"Error during Git operation: {e}")
    finally:
        # Return to the original directory
        os.chdir(original_path)

if __name__ == "__main__":
    # Set your local repository path here
    push_env_json("https://cnc-videos.s3.amazonaws.com/videos/output_4.mp4","Cool Panda")


