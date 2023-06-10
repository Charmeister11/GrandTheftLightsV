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

# Custom order of lights
custom_order = [1, 2, 3, 6, 5, 4]


def on_off(base_url, light_nr, state):
    url = f"{base_url}/{light_nr}/state"
    headers = {}
    data = {"on": state}
    response = requests.put(url, headers=headers, json=data, verify=False)
    print(f"PUT request sent to {url}, status code: {response.status_code}")


def set_light_color(base_url, light_id, hue):
    url = f"{base_url}/{light_id}/state"
    payload = {"hue": hue}
    response = requests.put(url, json=payload, verify=False)
    print(f"Set light {light_id} color, status code: {response.status_code}")


def retrieve_lights(base_url):
    response = requests.get(base_url, verify=False)
    print(f"Get request sent to {base_url}, status code: {response.status_code}")

    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to retrieve lights information.")
        return None


import requests


def turn_off_all_lights(base_url, lights, state):
    """
    Turn off all lights using the Philips Hue API.
    :param state:
    :param lights:
    :param base_url: The base URL to access the Philips Hue API.
    """
    # Loop through each light and turn it off
    for light_id in lights:
        requests.put(f"{base_url}/{light_id}/state", json={"on": state}, verify=False)
        print(f"{base_url}/{light_id}/state")
        print(f"Turned off light {light_id}")


def process_lights(base_url, lights):
    if lights is not None:
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
        for light_id in custom_order:
            str_light_id = str(light_id)
            if str_light_id in lights and 'state' in lights[str_light_id] and 'hue' in lights[str_light_id]['state']:
                hue = lights[str_light_id]['state']['hue']
                print(f"Light {light_id} has hue: {hue}")

def test():
    base_url = "https://192.168.1.247/api/D2FyCAxPndXkL71a6l5PlTuhCM6aCTMf-NSiB7Ns/lights"
    lights = retrieve_lights(base_url=base_url)
    turn_off_all_lights(base_url, lights)
    # process_lights(base_url, lights)
    # get_light_colors(lights)
# test()