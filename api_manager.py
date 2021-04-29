import urllib
from threading import Thread
from time import sleep
from datetime import datetime
import urllib.request
from json import loads
from collections import deque
from logging_decorators import logged_class, logged_initializer, logged_class_function
from itertools import islice


@logged_class
class ApiManager:

    @logged_initializer
    def __init__(self, config):
        self.config = config
        self.logger.set_level(self.config['log_level'])
        self.frame_id = 0
        self.frames = deque(maxlen=config['frames']*2)
        self.is_warm = False
        api_update_process = Thread(target=self.update, daemon=True)
        api_update_process.start()

    @logged_class_function
    def update(self):
        # Setup API connection
        url = f"https://api.nomics.com/v1/currencies/ticker?key={self.config['api_key']}" \
              f"&ids=BTC&interval=1d,30d&convert=EUR"

        while True:
            # Get time at start of call
            api_call_start_time = datetime.now()

            # Make the API call
            # TODO Error handling on url timeout / fail
            request_return = None
            while True:
                try:
                    request_return = urllib.request.urlopen(url, timeout=2).read().decode()
                    break
                except:
                    self.logger.error('Failed to get frame data, retrying')
                    sleep(1)
                    continue

            stripped_request_return = request_return[1:-2]
            request = loads(stripped_request_return)

            # Get the frame data
            frame_data = {}
            for key in self.config['keys_to_save']:
                value = request[key]
                frame_data[key] = float(value)
            asset_value = request['price']
            frame_data['dollar_to_asset_ratio'] = 1 / float(asset_value)

            # Assign frame ID
            frame_data['frame_id'] = self.frame_id
            self.frame_id += 1

            # Store as internal frame data
            self.frames.appendleft(frame_data)

            # Check if api_manager is warmed up (double the frame window)
            if self.is_warm:
                pass
            elif len(self.frames) == self.frames.maxlen:
                self.is_warm = True
            else:
                if len(self.frames) % 100 == 0:
                    self.logger.progress(f'Warming up frame {len(self.frames)} of {self.frames.maxlen}')

            # Get appropriate time to wait
            api_call_end_time = datetime.now()
            time_to_sleep = 1 - (api_call_end_time - api_call_start_time).microseconds / 1000000
            sleep(time_to_sleep)

    # TODO make ability to get an arbitrary window
    @logged_class_function
    def get_window(self):
        window_size = self.config['frames']
        return list(islice(self.frames, 0, window_size))

    def get_catchup_window(self):
        return list(self.frames)
