import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = "CHANGE_ME_SECRET_KEY"

    SQLALCHEMY_DATABASE_URI = \
        "sqlite:///" + os.path.join(BASE_DIR, "instance", "game.db")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    PLAYER_NAME_MIN = 2
    PLAYER_NAME_MAX = 16
