import requests
import logging
from local_settings import EXPO_ACCESS_TOKEN


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_push_notification(user_profile, token, title, body):
    message = {
        'to': token,
        'sound': 'default',
        'title': title,
        'body': body,
        'data': {'someData': 'goes here'},
    }
    try:
        response = requests.post('https://exp.host/--/api/v2/push/send', json=message, headers={
            'Accept': 'application/json',
            "Authorization": f"Bearer {EXPO_ACCESS_TOKEN}",
            'Accept-Encoding': 'gzip, deflate',
            'Content-Type': 'application/json',
        })
        response_data = response.json()
        # Check if the token is invalid and update if necessary
        if response_data.get('data') and response_data['data']['status'] == 'error':
            user_profile.expo_push_token = None
            user_profile.save()
    except requests.RequestException as e:
        logger.error(f"Network error occurred: {e}")
