from locust import task
from locust.env import Environment

from users.base_user import FeatureStoreUser


class FeatureStoreOnlineUser(FeatureStoreUser):
    def __init__(
        self,
        environment: Environment,
    ):
        self.host = "<YOUR_HOST_IP>" 

        self.headers = {
            "Host": "<YOUR_HOST_HEADER>",
            'Authorization': 'ApiKey <YOUR_API_KEY>',
        }

        super().__init__(
            environment=environment,
        )

    @task
    def query_rest(self):
        
        data = {'instances': [{'cc_num': 4307206161394478},
            {'cc_num': 4991539658091830},
            {'cc_num': 4556426990917111},
            {'cc_num': 4897277640695450},
            {'cc_num': 4123638178254919},
            {'cc_num': 4215909337633098},
            {'cc_num': 4883806594247243},
            {'cc_num': 4565376751743421},
            {'cc_num': 4134800299253298},
            {'cc_num': 4598649623090127},
            {'cc_num': 4454908897243389},
            {'cc_num': 4628483972728572},
            {'cc_num': 4837617840384848},
            {'cc_num': 4359225696258815},
            {'cc_num': 4758035858626403},
            {'cc_num': 4689840185625851},
            {'cc_num': 4893428073388709},
            {'cc_num': 4899899195688156},
            {'cc_num': 4564193664676304},
            {'cc_num': 4834372953306161},
            {'cc_num': 4277322646120192},
            {'cc_num': 4536307339137659},
            {'cc_num': 4322617096913250},
            {'cc_num': 4382251375646022},
            {'cc_num': 4167653876012714}]}

        self.client.request(
            "POST",
            "v1/models/deploymentasyncrdrs:predict",
            headers=self.headers,
            json=data,
        )
