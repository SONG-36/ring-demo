import aws_cdk as core
import aws_cdk.assertions as assertions

from ring_backend.ring_backend_stack import RingBackendStack

# example tests. To run these tests, uncomment this file along with the example
# resource in ring_backend/ring_backend_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = RingBackendStack(app, "ring-backend")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
