web: sh -c 'cd yoloo && daphne yoloo.asgi:application --port $PORT --bind 0.0.0.0 -v2'
worker: python yoloo/manage.py runworker channels --settings=yoloo.settings -v2