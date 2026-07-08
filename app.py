from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from config import Config
from database import db
from models import Player

import random
import json

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="eventlet"
)

ONLINE_PLAYERS = {}

# =========================
# ГЕРОИ
# =========================

HEROES = {
    "alucard": {
        "name": "Алукард",
        "hp": 320,
        "mana": 80,
        "attack": 45,
        "defense": 15,
        "sprite": "⚔️"
    },

    "miya": {
        "name": "Мия",
        "hp": 230,
        "mana": 120,
        "attack": 55,
        "defense": 8,
        "sprite": "🏹"
    },

    "tigreal": {
        "name": "Тигрил",
        "hp": 450,
        "mana": 70,
        "attack": 28,
        "defense": 25,
        "sprite": "🛡️"
    },

    "eudora": {
        "name": "Эйдора",
        "hp": 210,
        "mana": 180,
        "attack": 62,
        "defense": 7,
        "sprite": "⚡"
    }
}

# =========================
# API
# =========================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/heroes")
def heroes():

    return jsonify(HEROES)


@app.route("/api/register", methods=["POST"])
def register():

    data = request.json

    nickname = data.get("nickname", "").strip()

    hero = data.get("hero", "")

    if len(nickname) < 2:
        return jsonify({
            "status": "error",
            "message": "Имя слишком короткое"
        })

    if hero not in HEROES:
        return jsonify({
            "status": "error",
            "message": "Герой не найден"
        })

    exists = Player.query.filter_by(
        nickname=nickname
    ).first()

    if exists:

        return jsonify({
            "status": "exists"
        })

    h = HEROES[hero]

    player = Player(

        nickname=nickname,

        hero=hero,

        hp=h["hp"],

        max_hp=h["hp"],

        mana=h["mana"],

        max_mana=h["mana"],

        attack=h["attack"],

        defense=h["defense"]

    )

    db.session.add(player)

    db.session.commit()

    return jsonify({

        "status": "ok",

        "player": player.to_dict()

    })


@app.route("/api/login", methods=["POST"])
def login():

    data = request.json

    nickname = data.get("nickname", "")

    player = Player.query.filter_by(
        nickname=nickname
    ).first()

    if not player:

        return jsonify({

            "status": "error"

        })

    return jsonify({

        "status": "ok",

        "player": player.to_dict()

    })
