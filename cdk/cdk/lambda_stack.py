from aws_cdk import (
    CfnOutput,
    Duration,
    Stack,
    aws_apigateway as apigateway,
    aws_lambda as _lambda,
    aws_ssm as ssm,
)
from constructs import Construct

class LambdaStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Retrieve parameter store values
        openai_key_param = ssm.StringParameter.from_string_parameter_name(
            self, "OpenAIKey", string_parameter_name="/lambda/openai/key"
        )

        assistant_id_param = ssm.StringParameter.from_string_parameter_name(
            self, "AssistantID", string_parameter_name="/lambda/openai/assistantid"
        )

        # Define the Lambda function
        lambda_function = _lambda.Function(
            self,
            "OpenAIHandler",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="chat_handler.lambda_handler",
            code=_lambda.Code.from_asset("open_ai_handler.zip"),
            environment={
                "OPENAI_API_KEY": openai_key_param.string_value,
                "ASSISTANT_ID": assistant_id_param.string_value,
            },
            timeout=Duration.seconds(10)
        )
        
        api = apigateway.LambdaRestApi(
            self,
            "ChatAPI",
            handler = lambda_function,
            proxy = False,
        )
        chat_resource = api.root.add_resource("chat")
        chat_resource.add_method("POST")

        CfnOutput(
            self,
            "ChatAPIUrl",
            value=api.url,
            description="The base URL for the Chat API",
        )
