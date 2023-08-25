import os

from flask import Flask
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.ext.flask.flask_middleware import FlaskMiddleware
from opencensus.trace.samplers import ProbabilitySampler
from . import app

def create_app():
    flask = Flask(__name__)
    flask.register_blueprint(app.bp, threaded=True)

    if 'APPLICATIONINSIGHTS_CONNECTION_STRING' in os.environ:
        app_insights_connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
        _ = FlaskMiddleware(
            flask,
            exporter=AzureExporter(connection_string=app_insights_connection_string),
            sampler=ProbabilitySampler(rate=1.0),
        )

    return flask
