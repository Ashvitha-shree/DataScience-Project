"""
config.py
Central configuration loaded from environment variables (.env).
Keeping all settings in one place makes the project easy to explain in a viva:
"everything configurable is here, nothing is hardcoded in business logic."
"""
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
load_dotenv()


class Settings:
    # Database
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "smart_traffic_db")

    SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

    # Auth
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-this-secret-key-in-production")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "120"))

    # Generative AI (optional - falls back to procedural generator if not set)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

    # Model paths
    RF_MODEL_PATH = os.getenv("RF_MODEL_PATH", "ml_module/saved_model/rf_model.pkl")
    LSTM_MODEL_PATH = os.getenv("LSTM_MODEL_PATH", "dl_module/saved_model/lstm_model.h5")
    SLM_MODEL_DIR = os.getenv("SLM_MODEL_DIR", "slm_module/saved_model")

    # Reports
    REPORTS_DIR = os.getenv("REPORTS_DIR", "reports_output")

    # CORS - frontend dev server
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

print("DB_HOST =", repr(Settings.DB_HOST))
print("DB_USER =", repr(Settings.DB_USER))
print("DB_PASSWORD =", repr(Settings.DB_PASSWORD))
print("DATABASE_URL =", Settings.SQLALCHEMY_DATABASE_URL)
settings = Settings()
