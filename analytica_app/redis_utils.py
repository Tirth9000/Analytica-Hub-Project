import redis
import json

redis_client = redis.StrictRedis(
    host='redis',
    port=6379,
    db=1
)

def get_session_id(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key

def get_queue_key(session_id):
    return f"data_queue_{session_id}"

def get_upload_id_key(session_id):
    return f"upload_id_{session_id}"

def get_upload_id(session_id):
    key = get_upload_id_key(session_id)
    val = redis_client.get(key)
    return int(val) if val else -1

def set_upload_id(session_id, value):
    key = get_upload_id_key(session_id)
    redis_client.set(key, value)

def get_current_node(session_id):
    queue_key = get_queue_key(session_id)
    upload_id = get_upload_id(session_id)
    data = redis_client.lindex(queue_key, upload_id)
    return json.loads(data) if data else None

def reset_queue_to_current_node_only(session_id):
    queue_key = get_queue_key(session_id)
    upload_id = get_upload_id(session_id)
    if upload_id == -1:
        return
    data = redis_client.lindex(queue_key, upload_id)
    if data:
        redis_client.delete(queue_key)
        redis_client.rpush(queue_key, data)
        set_upload_id(session_id, 0)
        print(f"[Session {session_id}] Queue trimmed to only the current node.")
    else:
        print(f"[Session {session_id}] No data found at current upload_id.")


def push_data(session_id, row, column):
    queue_key = get_queue_key(session_id)
    upload_id = get_upload_id(session_id)
    queue_length = redis_client.llen(queue_key)

    if upload_id < queue_length - 1:
        redis_client.ltrim(queue_key, 0, upload_id)

    data = json.dumps({"row": row, "column": column})
    redis_client.rpush(queue_key, data)
    set_upload_id(session_id, upload_id + 1)
    print(f"[Session {session_id}] Pushed new data at index {upload_id + 1}")


def undo(session_id):
    queue_key = get_queue_key(session_id)
    upload_id = get_upload_id(session_id)
    if upload_id <= 0:
        print(f"[Session {session_id}] Cannot undo.")
        return None

    upload_id -= 1
    set_upload_id(session_id, upload_id)
    data = redis_client.lindex(queue_key, upload_id)
    return json.loads(data) if data else None


def redo(session_id):
    queue_key = get_queue_key(session_id)
    upload_id = get_upload_id(session_id)
    queue_length = redis_client.llen(queue_key)

    if upload_id >= queue_length - 1:
        print(f"[Session {session_id}] Cannot redo.")
        return None

    upload_id += 1
    set_upload_id(session_id, upload_id)
    data = redis_client.lindex(queue_key, upload_id)
    return json.loads(data) if data else None

def clear_user_session_data(session_id):
    queue_key = get_queue_key(session_id)
    upload_id_key = get_upload_id_key(session_id)

    redis_client.delete(queue_key)
    redis_client.delete(upload_id_key)

    print(f"Cleared Redis keys for session: {session_id}")