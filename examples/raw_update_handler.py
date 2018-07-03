import logging

from pytdlib.client import Client

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Client(api_id='YOUR_API_ID_HERE',
             api_hash='YOUR_API_HASH_HERE',
             auth_value='YOUR_PHONE_NUMBER_HERE')
app.start()
