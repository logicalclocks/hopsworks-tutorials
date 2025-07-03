import os
import random

from locust import FastHttpUser
from locust.env import Environment

class FeatureStoreUser(FastHttpUser):
    abstract = True

    def __init__(
            self,
            environment: Environment,
    ):
        super().__init__(environment)
