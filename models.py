import json

from database import db


class Player(db.Model):

    __tablename__ = "players"

    id = db.Column(db.Integer, primary_key=True)

    nickname = db.Column(db.String(16), unique=True, nullable=False)

    hero = db.Column(db.String(30), nullable=False)

    level = db.Column(db.Integer, default=1)

    xp = db.Column(db.Integer, default=0)

    gold = db.Column(db.Integer, default=150)

    hp = db.Column(db.Integer, default=300)

    max_hp = db.Column(db.Integer, default=300)

    mana = db.Column(db.Integer, default=100)

    max_mana = db.Column(db.Integer, default=100)

    attack = db.Column(db.Integer, default=30)

    defense = db.Column(db.Integer, default=15)

    floor = db.Column(db.Integer, default=1)

    pos_x = db.Column(db.Integer, default=20)

    pos_y = db.Column(db.Integer, default=20)

    inventory = db.Column(
        db.Text,
        default="[]"
    )

    equipment = db.Column(
        db.Text,
        default="{}"
    )

    quests = db.Column(
        db.Text,
        default="[]"
    )

    achievements = db.Column(
        db.Text,
        default="[]"
    )

    def get_inventory(self):
        return json.loads(self.inventory)

    def set_inventory(self, data):
        self.inventory = json.dumps(data)

    def get_equipment(self):
        return json.loads(self.equipment)

    def set_equipment(self, data):
        self.equipment = json.dumps(data)

    def get_quests(self):
        return json.loads(self.quests)

    def set_quests(self, data):
        self.quests = json.dumps(data)

    def to_dict(self):

        return {

            "id": self.id,

            "nickname": self.nickname,

            "hero": self.hero,

            "level": self.level,

            "xp": self.xp,

            "gold": self.gold,

            "hp": self.hp,

            "max_hp": self.max_hp,

            "mana": self.mana,

            "max_mana": self.max_mana,

            "attack": self.attack,

            "defense": self.defense,

            "floor": self.floor,

            "x": self.pos_x,

            "y": self.pos_y,

            "inventory": self.get_inventory(),

            "equipment": self.get_equipment(),

            "quests": self.get_quests()

      }
