from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    supabase_url: str
    supabase_secret_key: str
    supabase_jwks_url: str
    orcarouter_api_key: str

    class Config:
        env_file = ".env"
        # maps env var SUPABASE_URL -> supabase_url, etc.
        case_sensitive = False


settings = Settings()