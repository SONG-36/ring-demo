from aws_cdk import (
    RemovalPolicy,
    aws_dynamodb as dynamodb
)
from constructs import Construct

class DatabaseLayer(Construct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. 创建一张“永远装不满”的 DynamoDB 数据库表
        self.ring_data_table = dynamodb.Table(
            self, "RingDataTable",
            # 2. 分区键 (Partition Key)：相当于我们通过 user_id 来找到某个用户的专属抽屉
            partition_key=dynamodb.Attribute(name="user_id", type=dynamodb.AttributeType.STRING),
            
            # 3. 排序键 (Sort Key)：在用户的抽屉里，数据按时间戳 timestamp 先后排列
            sort_key=dynamodb.Attribute(name="timestamp", type=dynamodb.AttributeType.NUMBER),
            
            # 4. 计费模式：PAY_PER_REQUEST (按需计费)。没人用就不花一分钱，非常适合初创项目
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            
            # 5. 销毁策略：开发测试阶段，当我们删掉架构时，把这张表也一起删干净（生产环境要改成 RETAIN 保留）
            removal_policy=RemovalPolicy.DESTROY 
        )