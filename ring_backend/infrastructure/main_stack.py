from aws_cdk import (
    Stack,
    aws_iam as iam,
    aws_apigateway as apigw,
    aws_lambda as _lambda,          # 新增：Lambda 模块
    aws_events as events,
    aws_events_targets as targets   # 新增：总线靶子模块
)

from constructs import Construct

from .api_gateway_layer import ApiGatewayLayer
from .event_bus_layer import EventBusLayer
from .database_layer import DatabaseLayer

class RingBackendStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. 把三个“零件”插到主板上并实例化
        api_layer = ApiGatewayLayer(self, "ApiLayer")
        bus_layer = EventBusLayer(self, "BusLayer")
        db_layer = DatabaseLayer(self, "DbLayer")

        # 2. 颁发“通行证”：赋予大门（API Gateway）向总线（EventBus）发消息的 IAM 权限
        api_gw_role = iam.Role(
            self, "ApiGatewayToEventBusRole",
            assumed_by=iam.ServicePrincipal("apigateway.amazonaws.com")
        )
        # 让总线允许这个角色写入事件
        bus_layer.ring_event_bus.grant_put_events_to(api_gw_role)

        # 3. 核心硬连线：造一根“转接线”，把用户上传的 JSON 打包成总线能看懂的事件格式
        integration_response = apigw.IntegrationResponse(
            status_code="200",
            response_templates={"application/json": '{"message": "Ring data received and routed to bus!"}'}
        )
        
        # 魔法配置：API Gateway 直连 EventBridge
        put_event_integration = apigw.AwsIntegration(
            service="events",
            action="PutEvents",
            integration_http_method="POST",
            options=apigw.IntegrationOptions(
                credentials_role=api_gw_role,
                request_parameters={
                    "integration.request.header.X-Amz-Target": "'AWSEvents.PutEvents'",
                    "integration.request.header.Content-Type": "'application/x-amz-json-1.1'"
                },
                # 这里用的是 VTL 模板语法，作用是把设备发来的 JSON 塞进 Detail 字段里扔给总线
                request_templates={
                    "application/json": f"""
                    {{
                        "Entries": [
                            {{
                                "Source": "ring.device.api",
                                "DetailType": "RawSensorData",
                                "Detail": "$util.escapeJavaScript($input.json('$'))",
                                "EventBusName": "{bus_layer.ring_event_bus.event_bus_name}"
                            }}
                        ]
                    }}
                    """
                },
                integration_responses=[integration_response]
            )
        )

        # 4. 把这根转接线，插到我们大门的 POST 接口上
        api_layer.data_resource.add_method(
            "POST", 
            put_event_integration,
            method_responses=[apigw.MethodResponse(status_code="200")]
        )

        # 5. 雇佣搬运工 (Lambda)：指向我们刚才写的 dumper 文件夹
        dumper_lambda = _lambda.Function(
            self, "DataDumperFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.handler",
            code=_lambda.Code.from_asset("ring_backend/infrastructure/dumper"),
            environment={
                "TABLE_NAME": db_layer.ring_data_table.table_name # 把数据库名字当环境变量告诉 Lambda
            }
        )

        # 6. 赋予权限：允许搬运工向数据库写数据
        db_layer.ring_data_table.grant_write_data(dumper_lambda)

        # 7. 制定总线规则：只要包裹来源 (source) 是 "ring.device.api"，就把靶子指向搬运工
        rule = events.Rule(
            self, "RouteToDbRule",
            event_bus=bus_layer.ring_event_bus,
            event_pattern=events.EventPattern(
                source=["ring.device.api"]
            )
        )
        rule.add_target(targets.LambdaFunction(dumper_lambda))