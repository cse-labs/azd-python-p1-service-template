import random
import os

from src.api import create_app

app = create_app()

def test_generate_name():
    random.seed(1)
    os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"] = "xxxx"
    response = app.test_client().get("/")
    assert response.status_code == 200
