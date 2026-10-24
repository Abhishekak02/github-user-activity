import sys
import http.client
import json

# args = sys.argv
#
# if len(args) != 2:
#     print("Usage: python main.py <username>")
# else:
#     print("Username:", args[1])


conn = http.client.HTTPSConnection("api.github.com")

headers = {
    "User-Agent": "github-user-activity"
}

conn.request("GET", "/users/Abhishekak02/events", headers=headers)

response = conn.getresponse()

raw_data = response.read().decode()
# print(type(raw_data))


event = json.loads(raw_data)

# for event in data:
#     print(
#         f"Event type: {event['type']}\n",
#         f"Event repo and name: {event['repo']['name']}\n",
#         f"Event payload: {event['payload']}"
#     )


def format_event(event):
    handlers = {
        "PushEvent": handle_push,
        "CreateEvent": handle_create
    }
#
#
def handle_push(event):
    print("This is a pushevent.")

def handle_create(event):
    print("This is a create event.")
