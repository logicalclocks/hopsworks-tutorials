PARSE_NEW_TWEETS =  1 # if 0 (aka False), only BTC timeseries data will be parsed
                   # and processed. Twitter API will not be used.
LOCALLY = 1 # if 0 (aka False), environmental vars will be NOT parsed from
            # .env file in this dir but from Heroku environment itself.
            # Use LOCALLY = 1 when you run streamlit_app.py locally.
