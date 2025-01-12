import redis
import pickle
import pandas as pd
from django.conf import settings

redis_client = redis.StrictRedis(
    host='redis',
    port=6379,
    db=1
)

def store_dataframe_in_redis(df: pd.DataFrame, key: str):
    print('stored')
    df_pickle = pickle.dumps(df)
    redis_client.set(key, df_pickle)

def get_dataframe_from_redis_pickle(key: str) -> pd.DataFrame:
    df_pickle = redis_client.get(key)
    if df_pickle:
        print('retrived')
        return pickle.loads(df_pickle)
    return None