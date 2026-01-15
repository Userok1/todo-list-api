<h1>Todo list based on Python</h1>
To set config you should create ".env" file and put values below:

```console
SQLITE_URL="sqlite_db_for_testing"
POSTGRESQL_URL="postgresql_db_url"
ACCESS_TOKEN_EXPIRE_MINUTES="15_minutes_for_example"
REFRESH_TOKEN_EXPIRE_MINUTES="7_days_for_example"
ACCESS_TOKEN_SECRET_KEY="your_secret_key"
REFRESH_TOKEN_SECRET_KEY="your_secret_key"
TOKEN_ALGORITHM="HS256_for_example"
REDIS_URL="your_redis_url"
```
sqlite_url is optional and used for testing purposes

redis_url is required for fastapi_limiter to work

