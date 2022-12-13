import os, json, sentry_sdk, requests
from flask import Flask, abort, jsonify
from flask_cors import CORS
from smartystreets_python_sdk import StaticCredentials, exceptions, ClientBuilder
from smartystreets_python_sdk.us_street import Lookup as StreetLookup
from smarty import *
from smarty.models.candidate import CandidateSchema
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk import capture_exception

application = app = Flask(__name__)
CORS(app)

'''
TODO:
- Add caching, flask logging via sentry.io, 
- Add middleware to check if requestor is authorized to make this call
- Use the AWS Parameters and Secrets Lambda Extension instead of AWS SDK for secrets manager

Decisions: 
- keep only freeform? yes, for now.
- store constants in a shared file?
'''

CONTENT_TYPE_JSON = "application/json"
CONTENT_TYPE_PLAIN_TEXT = "text/plain"

sentry_sdk.init(
    dsn="https://2b2c4a1149374e3583d261006b29715c@o4504313332170752.ingest.sentry.io/4504313344753664",
    traces_sample_rate=1.0,
    integrations=[
        FlaskIntegration(),
    ]
)


@app.route("/address", methods=["POST"])
def verify_address_freeform(address):
    aws_secret = json.loads(get_secret())
    print(f'My secret is: {aws_secret}')
    AUTH_ID = aws_secret['nimbus-smarty-auth-id']
    AUTH_TOKEN = aws_secret['nimbus-smarty-auth-token']
    credentials = StaticCredentials(AUTH_ID, AUTH_TOKEN)
    client = ClientBuilder(credentials).with_licenses(
        ["us-core-cloud"]).build_us_street_api_client()
    
    #street = request.json['street']
    street = address
    print(f'Input is: {street}')
    lookup = StreetLookup()
    lookup.street = street

    try:
        client.send_lookup(lookup)
    except exceptions.SmartyException as err:
        print(err)
        capture_exception(err)
        return

    result = lookup.result

    if not result:
        abort(404, description="Resource not found")

    first_candidate = result[0]
    print(vars(first_candidate))
    schema_candidate = CandidateSchema(many=False)
    result_candidate = schema_candidate.dump(first_candidate)
    print("Results for result_candidate: ")
    print(result_candidate)
    print("\n")
    #result = Response(json.dumps(result_candidate), status=200, content_type=CONTENT_TYPE_JSON)
    result = json.dumps(result_candidate)
    return result


@app.route('/debug-sentry', methods=["GET"])
def trigger_error():
    division_by_zero = 1 / 0


def get_secret():
    headers = {"X-Aws-Parameters-Secrets-Token": os.environ.get('AWS_SESSION_TOKEN'), "content-type":"application/json"}
    secret_name = "test/nimbus-ms-smarty/app"
    secrets_extension_http_port = 3001
    region_name = "us-east-1"
    baseURI = "http://localhost:" + str(secrets_extension_http_port)
    #secrets_extension_endpoint = "/secretsmanager/get"
    secrets_extension_endpoint = baseURI + "/secretsmanager/get"
    params = {'secretId': secret_name}

    try:
        # response = requests.get(secrets_extension_endpoint, params=params, headers=headers)
        response = requests.get(secrets_extension_endpoint, params=params, headers=headers)
        response_json = response.json()
        print(f'response is {response_json}')
    except AWS_Exception as e:
        capture_exception(e)
        raise AWS_Exception("Cannot connect to AWS secrets manager.")

    # Decrypts secret using the associated KMS key.
    secret = response_json['SecretString']

    # Your code goes here.
    return secret


class AWS_Exception(Exception):
    status_code = 500
    def __init__(self, message, status_code=None, payload=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload
    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404


@app.errorhandler(AWS_Exception)
def aws_exception(e):
    return jsonify(e.to_dict()), e.status_code


if __name__ == '__main__':
    app.run(host='localhost', port=5020, debug=False)

'''
Documentation
https://flask.palletsprojects.com/en/2.2.x/errorhandling/#returning-api-errors-as-json
https://docs.sentry.io/platforms/python/
https://requests.readthedocs.io/en/latest/user/quickstart/

'''