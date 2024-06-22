import requests

launch_base_url = "https://lldev.thespacedevs.com/2.2.0/launch/"
upcoming_launch_url = requests.get(f"{launch_base_url}upcoming/")

if upcoming_launch_url.status_code == 200:
    print(upcoming_launch_url.json)