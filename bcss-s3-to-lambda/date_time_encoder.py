import json
from datetime import datetime


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()  # or obj.strftime("%Y-%m-%d %H:%M:%S")
        return super().default(o)
