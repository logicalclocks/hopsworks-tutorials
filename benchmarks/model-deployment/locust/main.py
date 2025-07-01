from locust import main as locust_main, events
from locust.env import Environment

import sys
from werkzeug.middleware.dispatcher import DispatcherMiddleware


@events.init.add_listener
def on_test_start(environment: Environment, **kwargs):
    if environment.web_ui:
        @environment.web_ui.app.route("/health")
        def health():
            return {"status": "ok"}

        wsgi_app = environment.web_ui.app.wsgi_app
        environment.web_ui.app.wsgi_app = DispatcherMiddleware(
            app=wsgi_app, mounts={"/locust": wsgi_app}
        )


def start_locust():
    # Passing this arg helps to rebalance locust users across workers as it scales
    sys.argv.append("--enable-rebalancing")
    locust_main.main()

def app():
    start_locust() 
