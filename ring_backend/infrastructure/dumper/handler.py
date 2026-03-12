import os
import boto3
import json
from decimal import Decimal

# 初始化数据库连接
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def handler(event, context):
    # 1. EventBridge 传过来的核心数据，永远包裹在 'detail' 这个字段里
    detail = event.get('detail', {})
    
    # 2. 防坑点：DynamoDB 的 Python SDK 不认识普通的小数 (float)，必须转成 Decimal 类型
    if isinstance(detail, str):
        payload = json.loads(detail, parse_float=Decimal)
    else:
        payload = json.loads(json.dumps(detail), parse_float=Decimal)
        
    # 3. 暴力落盘：不管 JSON 里有什么，直接塞进库里！
    table.put_item(Item=payload)
    
    print(f"数据落盘成功: {payload}")
    return {"statusCode": 200}