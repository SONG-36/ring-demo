from aws_cdk import (
    aws_events as events
)
from constructs import Construct

class EventBusLayer(Construct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. 创建一条智能戒指专属的“自定义事件总线”
        self.ring_event_bus = events.EventBus(
            self, "RingEventBus",
            event_bus_name="RingSensorDataBus"
        )