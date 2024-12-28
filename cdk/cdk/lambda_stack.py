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
            timeout=Duration.seconds(15)
        )
        
        base_api = apigateway.RestApi(self, 'ApiGatewayWithCors',
                                  rest_api_name='ApiGatewayWithCors')

        usage_plan = base_api.add_usage_plan(
            "ChatApiUsagePlan",
            name="ChatAPIUsagePlan",
            throttle=apigateway.ThrottleSettings(
                rate_limit=2,
                burst_limit=5,
            ),
        )

        chat_resource = base_api.root.add_resource(
            'chat',
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_methods=['POST', 'OPTIONS'],
                allow_origins=apigateway.Cors.ALL_ORIGINS)
        )
        lambda_integration = apigateway.LambdaIntegration(
            lambda_function,
            proxy=False,
            integration_responses=[
                apigateway.IntegrationResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': "'*'"
                    }
                )
            ]
        )
        chat_resource.add_method(
            'POST', lambda_integration,
            method_responses=[
                apigateway.MethodResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': True
                    }
                )
            ]
        )

        CfnOutput(
            self,
            "ChatAPIUrl",
            value=base_api.url,
            description="The base URL for the Chat API",
        )

        
