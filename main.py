import sys
import http.client
import json
from urllib.parse import quote


# -------------------------
# Event Handlers
# -------------------------

def handle_push(event):
    repo = event.get("repo", {}).get("name", "unknown repository")
    payload = event.get("payload", {})

    ref = payload.get("ref", "")
    branch = ref.removeprefix("refs/heads/") or "unknown branch"

    return f"Pushed changes to {repo} on {branch}"


def handle_create(event):
    repo = event.get("repo", {}).get("name", "unknown repository")
    payload = event.get("payload", {})

    ref_type = payload.get("ref_type", "resource")
    ref = payload.get("ref") or "unknown"

    return f"Created {ref_type} {ref} in {repo}"


def handle_unknown(event):
    event_type = event.get("type", "UnknownEvent")
    repo = event.get("repo", {}).get("name", "unknown repository")

    return f"{event_type} occurred in {repo}"


# -------------------------
# Event Handler Mapping
# -------------------------

HANDLERS = {
    "PushEvent": handle_push,
    "CreateEvent": handle_create,
}


# -------------------------
# Format One Event
# -------------------------

def format_event(event):
    event_type = event.get("type", "")
    handler = HANDLERS.get(event_type, handle_unknown)

    return handler(event)


# -------------------------
# Fetch Events from GitHub
# -------------------------

def fetch_events(username):
    conn = http.client.HTTPSConnection(
        "api.github.com",
        timeout=10
    )

    try:
        path = f"/users/{quote(username, safe='')}/events"

        headers = {
            "User-Agent": "github-user-activity",
            "Accept": "application/vnd.github+json",
        }

        conn.request("GET", path, headers=headers)
        response = conn.getresponse()

        raw_data = response.read().decode("utf-8")

        if response.status != 200:
            raise RuntimeError(
                f"GitHub API error: {response.status} "
                f"{response.reason}"
            )

        events = json.loads(raw_data)

        if not isinstance(events, list):
            raise ValueError("Unexpected response format from GitHub.")

        return events

    finally:
        conn.close()


# -------------------------
# Main Program
# -------------------------

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <username>")
        sys.exit(1)

    username = sys.argv[1]

    try:
        events = fetch_events(username)

    except (OSError, http.client.HTTPException) as error:
        print(f"Network error: {error}")
        sys.exit(1)

    except RuntimeError as error:
        print(error)
        sys.exit(1)

    except (json.JSONDecodeError, ValueError) as error:
        print(f"Could not process GitHub response: {error}")
        sys.exit(1)

    if not events:
        print(f"No recent public activity found for {username}.")
        return

    print(f"Recent GitHub activity for {username}:\n")

    for event in events:
        print(f"- {format_event(event)}")


if __name__ == "__main__":
    main()
