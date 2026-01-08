from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    supabase_url: str = ""
    supabase_anon_key: str = ""
    sqlite_db_path: str = "./backend/data.db"

    class Config:
        env_file = ".env"

settings = Settings()
