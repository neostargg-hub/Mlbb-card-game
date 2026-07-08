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
# =========================
# ОБНОВЛЕНИЕ ПЕРСОНАЖА
# =========================

@app.route("/api/save", methods=["POST"])
def save_player():

    data = request.json

    nickname = data["nickname"]

    player = Player.query.filter_by(
        nickname=nickname
    ).first()

    if player is None:

        return jsonify({
            "status": "error"
        })

    player.level = data.get("level", player.level)
    player.xp = data.get("xp", player.xp)
    player.gold = data.get("gold", player.gold)

    player.hp = data.get("hp", player.hp)
    player.max_hp = data.get("max_hp", player.max_hp)

    player.mana = data.get("mana", player.mana)
    player.max_mana = data.get("max_mana", player.max_mana)

    player.attack = data.get("attack", player.attack)
    player.defense = data.get("defense", player.defense)

    player.pos_x = data.get("x", player.pos_x)
    player.pos_y = data.get("y", player.pos_y)

    if "inventory" in data:
        player.set_inventory(data["inventory"])

    if "equipment" in data:
        player.set_equipment(data["equipment"])

    if "quests" in data:
        player.set_quests(data["quests"])

    db.session.commit()

    return jsonify({
        "status": "ok"
    })


# =========================
# SOCKET.IO
# =========================

@socketio.on("connect")
def socket_connect():

    print("Новое подключение")


@socketio.on("join")
def socket_join(data):

    nickname = data["nickname"]

    player = Player.query.filter_by(
        nickname=nickname
    ).first()

    if player is None:
        return

    ONLINE_PLAYERS[nickname] = {

        "nickname": nickname,

        "hero": player.hero,

        "x": player.pos_x,

        "y": player.pos_y,

        "level": player.level

    }

    emit(

        "current_players",

        list(ONLINE_PLAYERS.values())

    )

    emit(

        "player_join",

        ONLINE_PLAYERS[nickname],

        broadcast=True,

        include_self=False

    )


@socketio.on("move")
def socket_move(data):

    nickname = data["nickname"]

    if nickname not in ONLINE_PLAYERS:
        return

    ONLINE_PLAYERS[nickname]["x"] = data["x"]
    ONLINE_PLAYERS[nickname]["y"] = data["y"]

    player = Player.query.filter_by(
        nickname=nickname
    ).first()

    if player:

        player.pos_x = data["x"]
        player.pos_y = data["y"]

        db.session.commit()

    emit(

        "player_move",

        ONLINE_PLAYERS[nickname],

        broadcast=True,

        include_self=False

    )
    # =========================
# ГЛОБАЛЬНЫЙ ЧАТ
# =========================

@socketio.on("chat")
def socket_chat(data):

    nickname = data.get("nickname", "Игрок")

    message = data.get("message", "").strip()

    if not message:
        return

    if len(message) > 200:
        message = message[:200]

    emit(
        "chat",
        {
            "nickname": nickname,
            "message": message
        },
        broadcast=True
    )


# =========================
# ОТКЛЮЧЕНИЕ ИГРОКА
# =========================

@socketio.on("leave")
def socket_leave(data):

    nickname = data.get("nickname")

    if nickname in ONLINE_PLAYERS:

        del ONLINE_PLAYERS[nickname]

        emit(
            "player_leave",
            {
                "nickname": nickname
            },
            broadcast=True
        )


@socketio.on("disconnect")
def socket_disconnect():

    print("Игрок отключился")


# =========================
# МОНСТРЫ
# =========================

MONSTERS = [

    {
        "id": 1,
        "name": "Лесной слизень",
        "hp": 40,
        "attack": 6,
        "gold": 10,
        "xp": 8
    },

    {
        "id": 2,
        "name": "Гоблин",
        "hp": 75,
        "attack": 12,
        "gold": 20,
        "xp": 15
    },

    {
        "id": 3,
        "name": "Скелет",
        "hp": 95,
        "attack": 18,
        "gold": 30,
        "xp": 24
    },

    {
        "id": 4,
        "name": "Орк",
        "hp": 170,
        "attack": 28,
        "gold": 55,
        "xp": 45
    }

]


@app.route("/api/random_monster")
def random_monster():

    return jsonify(random.choice(MONSTERS))


# =========================
# ЛУТ
# =========================

ITEMS = [

    "Малое зелье",

    "Большое зелье",

    "Железный меч",

    "Стальной меч",

    "Кожаная броня",

    "Железный шлем",

    "Кольцо силы",

    "Амулет жизни"

]


@app.route("/api/random_loot")
def random_loot():

    return jsonify({

        "item": random.choice(ITEMS)

    })


# =========================
# РЕЙТИНГ
# =========================

@app.route("/api/leaderboard")
def leaderboard():

    players = Player.query.order_by(
        Player.level.desc(),
        Player.xp.desc()
    ).limit(20).all()

    return jsonify([

        p.to_dict()

        for p in players

    ])


# =========================
# СОЗДАНИЕ БАЗЫ
# =========================

with app.app_context():

    db.create_all()


# =========================
# ЗАПУСК
# =========================

if __name__ == "__main__":

    print("=" * 40)
    print("MLBB RPG SERVER")
    print("=" * 40)

    socketio.run(

        app,

        host="0.0.0.0",

        port=5000,

        debug=True

    )
