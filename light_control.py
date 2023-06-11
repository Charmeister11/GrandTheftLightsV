import requests
import time

# Define the rainbow colors (Hue values ranging from 0 to 65535)
rainbow_colors = [
    8626,  # Red
    20730,  # Orange
    34160,  # Yellow
    44718,  # Green
    53424,  # Blue
    64984,  # Violet
]

# Custom order of lights to reflect how the lights are arranged in real life
custom_order = [1, 2, 3, 6, 5, 4]


def on_off(base_url, light_nr, state):
    """
    Turn on/off the light using the Philips Hue API.
    :param base_url: The base URL to access the Philips Hue API.
    :param light_nr: The number of the light to turn on/off (1-6)
    :param state: The state to set the light to (True/False)
    """
    url = f"{base_url}/{light_nr}/state"
    response = requests.put(url, json={"on": state}, verify=False)
    print(f"PUT request sent to {url}, status code: {response.status_code}")


def set_light_color(base_url, light_id, hue):
    """
    Set the light's color using the Philips Hue API.
    :param base_url: The base URL to access the Philips Hue API.
    :param light_id: The ID of the light to set the color of (1-6)
    :param hue: The hue value to set the light to (0-65535)
    """
    url = f"{base_url}/{light_id}/state"
    response = requests.put(url, json={"hue": hue}, verify=False)
    print(f"Set light {light_id} color, status code: {response.status_code}")


def retrieve_lights(base_url):
    """
    Retrieve the light's information using the Philips Hue API.
    :param base_url: The base URL to access the Philips Hue API.
    :return: JSON object containing information about the lights
    """
    response = requests.get(base_url, verify=False)
    print(f"Get request sent to {base_url}, status code: {response.status_code}")

    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to retrieve lights information.")
        return None


def turn_off_all_lights(base_url, lights, state):
    """
    Turn off all lights using the Philips Hue API.
    :param state: state of the lights (on/off)
    :param lights: JSON object containing information about the lights
    :param base_url: The base URL to access the Philips Hue API.
    """
    # Loop through each light and turn it off
    for light_id in lights:
        requests.put(f"{base_url}/{light_id}/state", json={"on": state}, verify=False)
        print(f"Turned off light {light_id}")


def process_lights(base_url, lights):
    """
    Process the lights using the Philips Hue API.
    :param base_url: The base URL to access the Philips Hue API.
    :param lights: JSON object containing information about the lights
    """
    if lights is not None:
        # Loop through each light and check if it is on, and change its color
        for index, light_id in enumerate(custom_order):
            str_light_id = str(light_id)
            if str_light_id in lights and 'state' in lights[str_light_id]:
                is_on = lights[str_light_id]['state'].get('on', False)
                if not is_on:
                    # Turn on the light if it is not already on
                    on_off(base_url, str_light_id, True)

                # Set the light's color
                if 'hue' in lights[str_light_id]['state']:
                    color = rainbow_colors[index % len(rainbow_colors)]
                    set_light_color(base_url, str_light_id, color)
                    time.sleep(1)  # Optional: sleep 1 second between setting each light to see the change gradually


def get_light_colors(lights):
    """
    Print the colors of the lights.
    :param lights: JSON object containing information about the lights
    """
    for light_id in custom_order:
        str_light_id = str(light_id)
        if str_light_id in lights and 'state' in lights[str_light_id] and 'hue' in lights[str_light_id]['state']:
            hue = lights[str_light_id]['state']['hue']
            print(f"Light {light_id} has hue: {hue}")
