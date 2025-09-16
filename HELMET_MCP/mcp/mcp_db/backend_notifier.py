import requests
import json
from typing import Dict, Any


def notify_db_update(data: str) -> Dict[str, Any]:
    """
    Send a POST request to notify backend about database updates.

    Args:
        data: JSON object containing the notification data

    Returns:
        Response from the backend as a dictionary

    Raises:
        requests.RequestException: If the request fails
    """
    url = "http://localhost:8000/notify_db_update"

    try:
        response = requests.post(
            url,
            json={"ding": data},
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        raise
