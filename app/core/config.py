from dotenv import load_dotenv
import os

load_dotenv()


class Configuration:
    HUGGING_FACE_API = os.getenv("HUGGING_FACE_API")


config = Configuration()
