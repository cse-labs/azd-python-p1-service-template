import logging

from flask import jsonify, Blueprint
from opencensus.trace import config_integration
from opencensus.trace.samplers import AlwaysOnSampler
from opencensus.trace.tracer import Tracer
import randomname

bp = Blueprint("names", __name__)
config_integration.trace_integrations(['logging'])
logging.basicConfig(format='%(asctime)s traceId=%(traceId)s spanId=%(spanId)s %(message)s')
tracer = Tracer(sampler=AlwaysOnSampler())
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

@bp.route("/")
def hello_world():
    # Generate a random name including a first name and adjective
    random_name = randomname.generate()
    with tracer.span(name=__name__):
        logger.info("Random Name Selected: - %s", random_name)

    json = {"name": random_name}

    return jsonify(json)
