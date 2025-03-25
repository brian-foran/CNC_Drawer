import requests
import os

def write_to_particle_variable(function_name, value = "0"):
    """
    Writes a value to a Particle Cloud variable.

    :param access_token: Your Particle Cloud access token
    :param device_id: The ID of your Particle device
    :param function_name: The name of the variable to write to
    :param value: The value to write to the variable
    """
    ACCESS_TOKEN = os.getenv('PARTICLE_ACCESS_TOKEN')

    if not ACCESS_TOKEN:
        raise ValueError("Missing API Key! Make sure it's set as an environment variable.")
    
    DEVICE_ID = os.getenv('PARTICLE_DEVICE_ID')
    
    if not ACCESS_TOKEN:
        raise ValueError("Missing Device ID! Make sure it's set as an environment variable.")

    url = f"https://api.particle.io/v1/devices/{DEVICE_ID}/{function_name}"
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}'
    }
    data = {
        'arg': value
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        print(f"Successfully wrote {value} to {function_name}")
    else:
        print(f"Failed to write to {function_name}: {response.status_code} - {response.text}")

# Example usage:
def main():
    
    #FUNCTION_NAME = "ResetCount"
    FUNCTION_NAME = "CNC_Start"
    VALUE = "0"

    write_to_particle_variable(FUNCTION_NAME, VALUE)

    #add start CNC, which increments count and sets CNC active

if __name__ == "__main__":
    write_to_particle_variable("CNC_Done")