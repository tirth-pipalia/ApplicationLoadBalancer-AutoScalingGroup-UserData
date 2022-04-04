#!/usr/bin/env python3
import os

import aws_cdk as cdk

from auto_scaling.auto_scaling_stack import AutoScalingStack


app = cdk.App()
env_ME = cdk.Environment(account="12_digit_account_no", region="me-south-1")
AutoScalingStack(app, "AutoScalingStack", env=env_ME)

app.synth()
