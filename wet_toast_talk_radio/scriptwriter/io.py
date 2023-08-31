import uuid


def unique_script_filename(prefix: str):
    """Generate a unique filename for a script file."""
    uuid_str = str(uuid.uuid4())[:6]
    return f"{prefix}-{uuid_str}.jsonl"
