import redis
import json

redis_client = redis.StrictRedis(
    host='redis',
    port=6379,
    db=1
)


def check_key(file_id):
    result = redis_client.exists(file_id)
    return result
    
def get_pointer_key(file_id):
    return f"pointerKey_{file_id}"

def get_index_value(file_id):
    key = get_pointer_key(file_id)
    index_value = redis_client.get(key)
    return int(index_value) if index_value else -1 

def push_data(file_id, rows, columns):
    key = get_pointer_key(file_id)
    index_value = get_index_value(file_id)
    queue_length = redis_client.llen(file_id)
    
    if index_value < queue_length -1:
        redis_client.ltrim(file_id, 0, index_value)

    data = json.dumps({'rows': rows, 'columns': columns})
    redis_client.rpush(file_id, data)
    redis_client.set(key, index_value+1)

def undo(file_id):
    index_value = get_index_value(file_id)
    key = get_pointer_key(file_id)
    if index_value == 0:
        data = redis_client.lindex(file_id, index_value)
        return json.loads(data) if data else None

    index_value -= 1
    redis_client.set(key, index_value)
    data = redis_client.lindex(file_id, index_value)
    return json.loads(data) if data else None

def redo(file_id):
    key = get_pointer_key(file_id)
    index_value = get_index_value(file_id)
    queue_length = redis_client.llen(file_id)

    if index_value >= queue_length - 1:
        return None

    index_value += 1
    redis_client.set(key, index_value)
    data = redis_client.lindex(file_id, index_value)
    return json.loads(data) if data else None

def get_current_node(file_id):
    index_value = get_index_value(file_id)
    data = redis_client.lindex(file_id, index_value)
    return json.loads(data) if data else None

def reset_queue_to_current_node_only(file_id):
    key = get_pointer_key(file_id)
    index_value = get_index_value(file_id)
    if index_value == -1:
        return
    data = redis_client.lindex(file_id, index_value)
    if data:
        redis_client.delete(file_id)
        redis_client.rpush(file_id, data)
        redis_client.set(key, 0)
    else:
        print(f"[Session {key}] No data found at current upload_id.")
        
def clear_queue_data(file_id):
    key = get_pointer_key(file_id)
    redis_client.delete(file_id)
    redis_client.delete(key)

def clear_all():
    redis_client.flushdb()