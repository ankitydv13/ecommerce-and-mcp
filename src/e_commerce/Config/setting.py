from pydantic_settings import BaseSettings , SettingsConfigDict



class Setting(BaseSettings):
    
    DB_HOST : str = "localhost"
    DB_PORT : int = 5432
    DB_NAME : str = "ecommerce"
    DB_USER : str = "postgres"
    DB_PASSWORD :  str = "Cfg@1234567"

    model_config = SettingsConfigDict(env_file=".env" , extra="ignore") 

setting = Setting()