from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "AI Fact Checking Agent"
    app_env: str = "development"
    debug: bool = True
    database_url: str = "sqlite:///./factcheck.db"
    llm_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    tavily_api_key: str = ""
    google_fact_check_api_key: str = ""
    rag_persist_directory: str = "./data/knowledge_base"
    embedding_model: str = "all-MiniLM-L6-v2"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
