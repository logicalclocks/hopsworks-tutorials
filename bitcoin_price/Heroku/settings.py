USE_FEATURE_STORE = 1 # if 1 (aka True), we will be connecting to the FS and
                      # inserting Feature Groups

PARSE_NEW_TWEETS =  1 # if 0 (aka False), only BTC timeseries data will be parsed
                   # and processed. Twitter API will not be used.
LOCALLY = 0 # if 0 (aka False), environmental vars will be NOT parsed from
            # .env file in this dir but from Heroku environment itself.
