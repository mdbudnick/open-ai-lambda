#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cdk.lambda_stack import LambdaStack


app = cdk.App()
LambdaStack(app, "LambdaStack", env={"region": "us-east-1"})

app.synth()
