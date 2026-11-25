from datetime import datetime, timezone
from uuid import uuid4


def new_id():
    return str(uuid4())


def now_iso():
    return datetime.now(timezone.utc).isoformat()
