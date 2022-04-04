#!/usr/bin/env python3
import os

import aws_cdk as cdk

from auto_scaling.auto_scaling_stack import AutoScalingStack


app = cdk.App()
env_ME = cdk.Environment(account="620228650709", region="me-south-1")
AutoScalingStack(app, "AutoScalingStack", env=env_ME)

app.synth()
