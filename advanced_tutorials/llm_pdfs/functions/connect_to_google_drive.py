from apiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools


# Define path variables
credentials_file_path = '../credentials/credentials.json'
clientsecret_file_path = '../credentials/client_secret.json'

# Define API scope
SCOPE = 'https://www.googleapis.com/auth/drive'

# Define store
store = file.Storage(credentials_file_path)
credentials = store.get()
# Get access token
if not credentials or credentials.invalid:
    flow = client.flow_from_clientsecrets(clientsecret_file_path, SCOPE)
    credentials = tools.run_flow(flow, store)