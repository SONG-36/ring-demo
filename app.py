#!/usr/bin/env python3
import os
import sys

sys.path.append(os.path.dirname(__file__))

import aws_cdk as cdk
from ring_backend.infrastructure.main_stack import RingBackendStack

app = cdk.App()

# 实例化咱们拼装好的主板
RingBackendStack(app, "RingBackend-Sprint1")

app.synth()