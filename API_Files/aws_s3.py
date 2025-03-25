import boto3
from botocore.exceptions import NoCredentialsError
from moviepy.video.io.VideoFileClip import VideoFileClip
import os

def convert_to_mp4(file_name):
    """Converts a video file to MP4 format."""
    clip = VideoFileClip(file_name)
    mp4_file_name = file_name.rsplit('.', 1)[0] + '.mp4'
    clip.write_videofile(mp4_file_name, codec='libx264')
    return mp4_file_name

def get_unique_filename(s3_client, bucket_name, base_filename):
    """Generates a unique filename by indexing if the filename already exists in the S3 bucket."""
    base, ext = base_filename.rsplit('.', 1)
    index = 1
    unique_filename = base_filename

    while True:
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=unique_filename)
        if 'Contents' not in response:
            break
        unique_filename = f"{base}_{index}.{ext}"
        index += 1

    return unique_filename

def upload_to_s3(file_name, S3_BUCKET_NAME = "cnc-videos", object_name=None):
    # AWS Credentials (Replace with IAM user credentials)
    AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
    AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')

    if not AWS_ACCESS_KEY or not AWS_SECRET_KEY:
        raise ValueError("Missing AWS credentials! Make sure they're set as environment variables.")
    
    """Uploads a file to an S3 bucket and returns the public URL."""
    
    # Convert to MP4 if the file is not already in MP4 format
    if not file_name.lower().endswith('.mp4'):
        file_name = convert_to_mp4(file_name)

    # Create S3 client
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )

    if object_name is None:
        object_name = file_name  # Use the same file name if no custom name is provided

    # Generate a unique filename if the object name already exists in the bucket
    object_name = get_unique_filename(s3_client, S3_BUCKET_NAME, object_name)

    try:
        # Upload the file
        s3_client.upload_file(file_name, S3_BUCKET_NAME, object_name, ExtraArgs={'ACL': 'public-read'})

        # Construct the public URL
        s3_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{object_name}"
        print(f"Upload successful! Video URL: {s3_url}")
        return s3_url

    except NoCredentialsError:
        print("Error: AWS credentials not found.")
        return None

# Example usage: Upload CNC-generated video
if __name__ == "__main__":
    video_path = "videos/output.avi"  # Path to your recorded video
    video_url = upload_to_s3(video_path)
