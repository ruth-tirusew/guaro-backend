import uuid

def convert_uuid_to_string(v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v