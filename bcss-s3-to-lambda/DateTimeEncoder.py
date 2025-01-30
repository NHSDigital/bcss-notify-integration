import json
from datetime import datetime


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()  # or obj.strftime("%Y-%m-%d %H:%M:%S")
        return super().default(obj)
