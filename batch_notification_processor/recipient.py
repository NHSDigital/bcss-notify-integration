from types import SimpleNamespace
from typing import TypeAlias

ATTR_NAMES = [
    "nhs_number",
    "message_id",
    "batch_id",
    "routing_plan_id",
    "message_status",
    "variable_text_1",
    "address_line_1",
    "address_line_2",
    "address_line_3",
    "address_line_4",
    "address_line_5",
    "postcode",
    "gp_practice_name",
]

Recipient: TypeAlias = SimpleNamespace

def make_recipient(attrs: list) -> SimpleNamespace:
    data = {
        attr_name: attrs[idx] if idx < len(attrs) else None
        for idx, attr_name in enumerate(ATTR_NAMES)
    }
    return SimpleNamespace(**data)
