import os
from dotenv import load_dotenv


class Config:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            load_dotenv('.env', override=True)
        return cls._instance


    def __init__(self):
        self.sqlite_url = os.getenv('SQLITE_URL')
        self.postgresql_url = os.getenv('POSTGRESQL_URL')
        self.access_token_expire_minutes = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')
        self.refresh_token_expire_minutes = os.getenv('REFRESH_TOKEN_EXPIRE_MINUTES')
        self.access_token_secret_key = os.getenv("ACCESS_TOKEN_SECRET_KEY")
        self.refresh_token_secret_key = os.getenv("REFRESH_TOKEN_SECRET_KEY")
        self.token_algorithm = os.getenv("TOKEN_ALGORITHM")
        

    @property
    def SQLITE_URL(self):
        if self.sqlite_url:
            return self.sqlite_url

    @property
    def POSTGRESQL_URL(self):
        if self.postgresql_url:
            return self.postgresql_url
    
    @property
    def ACCESS_TOKEN_SECRET_KEY(self):
        if self.access_token_secret_key:
            return self.access_token_secret_key

    @property
    def REFRESH_TOKEN_SECRET_KEY(self):
        if self.refresh_token_secret_key:
            return self.refresh_token_secret_key
    
    @property
    def ACCESS_TOKEN_EXPIRE_MINUTES(self):
        if self.access_token_expire_minutes:
            return float(self.access_token_expire_minutes)
        else:
            return float(15)

    @property
    def REFRESH_TOKEN_EXPIRE_MINUTES(self):
        if self.refresh_token_expire_minutes:
            return float(self.refresh_token_expire_minutes)
        else:
            return float(420)

    @property
    def TOKEN_ALGORITHM(self):
        if self.token_algorithm:
            return self.token_algorithm


cfg = Config()


if __name__ == "__main__":
    print(os.getenv('SQLITE_URL'))