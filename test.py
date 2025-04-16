import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

queue_name = "data_queue"
upload_id = -1  # -1 means no data yet


def push_data(row, column):
    global upload_id
    data = json.dumps({
        "row": row,
        "column": column
    })

    # Push to Redis list
    redis_client.rpush(queue_name, data)

    # Update pointer to latest index
    upload_id = redis_client.llen(queue_name) - 1
    print(f"Pushed: {data}")


def undo():
    global upload_id
    if upload_id <= 0:
        print("Cannot undo anymore.")
        return None

    upload_id -= 1
    data = redis_client.lindex(queue_name, upload_id)
    if data:
        print(f"Undo → Position: {upload_id}")
        return json.loads(data)
    return None


def redo():
    global upload_id
    queue_length = redis_client.llen(queue_name)

    if upload_id >= queue_length - 1:
        print("No more redo steps.")
        return None

    upload_id += 1
    data = redis_client.lindex(queue_name, upload_id)
    if data:
        print(f"Redo → Position: {upload_id}")
        return json.loads(data)
    return None


def current():
    if upload_id == -1:
        return None
    data = redis_client.lindex(queue_name, upload_id)
    return json.loads(data) if data else None
    
    
    
push_data(1, 1)
push_data(2, 2)
push_data(3, 3)
push_data(4, 4)
push_data(5, 5)

print(current())   # Shows data at upload_id = 4 (last one)

undo()             # Moves to 3rd item (upload_id = 3)
undo()             # Moves to 2nd item (upload_id = 2)

print(current())   # Shows data at current position

redo()             # Moves to 3rd item (upload_id = 3 again)