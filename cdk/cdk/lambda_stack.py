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

        def add_cors_options(api_resource: apigateway.IResource):
            api_resource.add_method(
                'OPTIONS',
                apigateway.MockIntegration(
                    integration_responses=[
                        apigateway.IntegrationResponse(
                            status_code='200',
                            response_parameters={
                                'method.response.header.Access-Control-Allow-Headers': "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Amz-User-Agent'",
                                'method.response.header.Access-Control-Allow-Origin': "'*'",
                                'method.response.header.Access-Control-Allow-Credentials': "'false'",
                                'method.response.header.Access-Control-Allow-Methods': "'OPTIONS,GET,PUT,POST,DELETE'",
                            }
                        )
                    ],
                    passthrough_behavior=apigateway.PassthroughBehavior.NEVER,
                    request_templates={
                        "application/json": "{\"statusCode\": 200}"
                    },
                ),
                method_responses=[
                    apigateway.MethodResponse(
                        status_code='200',
                        response_parameters={
                            'method.response.header.Access-Control-Allow-Headers': True,
                            'method.response.header.Access-Control-Allow-Methods': True,
                            'method.response.header.Access-Control-Allow-Credentials': True,
                            'method.response.header.Access-Control-Allow-Origin': True,
                        }
                    )
                ]
            )
            add_cors_options(chat_resource)

        CfnOutput(
            self,
            "ChatAPIUrl",
            value=api.url,
            description="The base URL for the Chat API",
        )

        
