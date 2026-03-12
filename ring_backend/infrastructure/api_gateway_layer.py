from aws_cdk import (
    aws_apigateway as apigw
)
from constructs import Construct

class ApiGatewayLayer(Construct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. 创建一个 REST API 网关
        self.ring_api = apigw.RestApi(
            self, "RingDataIngestionApi",
            rest_api_name="Ring Sensor Ingestion Service",
            description="接收戒指硬件传来的所有时序数据",
            
            # 2. 开启 CORS (跨域请求)，方便以后你用浏览器或本地脚本进行测试
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS
            )
        )

        # 3. 创建一个基础的资源路径，比如：https://xxx.aws.com/prod/data
        self.data_resource = self.ring_api.root.add_resource("data")