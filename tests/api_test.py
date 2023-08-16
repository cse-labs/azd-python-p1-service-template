import random

from src.api import create_app

app = create_app()


def test_generate_name():
    random.seed(1)
    response = app.test_client().get("/")
    assert response.status_code == 200
