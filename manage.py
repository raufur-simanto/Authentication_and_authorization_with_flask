from aws_lambda_wsgi import response
from project import create_app
app = create_app()

def lambda_handler(event, context):
    """
    Lambda handler that will handle the API Gateway events
    """
    return response(app, event, context)

if "__name__" == "__main__":
    app.run(host='0.0.0.0', port=5000)