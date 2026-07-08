from flask import Flask, render_template_string, jsonify, request
import os
import time

app = Flask(__name__)

# Глобальное потокобезопасное хранилище сервера в оперативной памяти (True MMO)
SERVER_STATE = {
    "players": {},
    "chat": [{"name": "СЕРВЕР", "msg": "Глобальный Nexus запущен! Общий чат и рейды активны.", "color": "#00ffff"}],
    "guilds": {},
    "raid_boss": {"name": "УЛЬТИМАТИВНЫЙ ЛОРД ТАМУЗ", "hp": 100000, "max_hp": 100000, "alive": True}
}

@app.route('/api/mmo/sync', methods=['POST'])
def mmo_sync():
    data = request.json or {}
    p_id = data.get('id')
    if not p_id:
        return jsonify({"status": "error", "message": "Missing ID"}), 400
    
    now = time.time()
    # Обновляем или добавляем игрока на сервере
    SERVER_STATE["players"][p_id] = {
        "name": data.get('name', 'Герой'),
        "x": data.get('x', 20),
        "y": data.get('y', 20),
        "sprite": data.get('sprite', '⚔️'),
        "lvl": data.get('lvl', 1),
        "guild": data.get('guild', ''),
        "last_seen": now
    }
    
    # Обработка входящего чата
    incoming_msg = data.get('chat_msg')
    if incoming_msg:
        SERVER_STATE["chat"].append({
            "name": data.get('name', 'Герой'),
            "msg": incoming_msg,
            "color": "#ffffff"
        })
        if len(SERVER_STATE["chat"]) > 40:
            SERVER_STATE["chat"].pop(0)

    # Обработка урона по Мировому Боссу
    boss_dmg = data.get('boss_damage', 0)
    if boss_dmg > 0 and SERVER_STATE["raid_boss"]["alive"]:
        SERVER_STATE["raid_boss"]["hp"] = max(0, SERVER_STATE["raid_boss"]["hp"] - boss_dmg)
        if SERVER_STATE["raid_boss"]["hp"] <= 0:
            SERVER_STATE["raid_boss"]["alive"] = False
            SERVER_STATE["chat"].append({"name": "ОБЪЯВЛЕНИЕ", "msg": f"Мировой Рейд-Босс повержен героем {data.get('name')}!", "color": "#ffcc00"})

    # Обработка создания гильдий
    new_guild = data.get('create_guild')
    if new_guild and new_guild not in SERVER_STATE["guilds"]:
        SERVER_STATE["guilds"][new_guild] = {"leader": data.get('name'), "members": 1}
        SERVER_STATE["chat"].append({"name": "СИСТЕМА", "msg": f"Создана новая глобальная гильдия: [{new_guild}]", "color": "#cc44ff"})

    # Очистка старых игроков (офлайн > 6 сек)
    dead_players = [k for k, v in SERVER_STATE["players"].items() if now - v['last_seen'] > 6]
    for k in dead_players:
        SERVER_STATE["players"].pop(k, None)

    # Собираем данные для ответа клиенту
    others = [{"name": v["name"], "x": v["x"], "y": v["y"], "sprite": v["sprite"], "lvl": v["lvl"], "guild": v["guild"]} for k, v in SERVER_STATE["players"].items() if k != p_id]
    
    return jsonify({
        "status": "success",
        "players": others,
        "chat": SERVER_STATE["chat"],
        "boss": SERVER_STATE["raid_boss"],
        "guilds_count": len(SERVER_STATE["guilds"])
    })

GAME_HTML = r'''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>MLBB RPG: NEXUS MULTIPLAYER v18.0</title>
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
    <style>
        :root { 
            --bg: #020205; --panel: rgba(10, 10, 24, 0.94); --border: #3a4a6c; 
            --acc: #00ffff; --hp: #ff3344; --mana: #33ccff; --gold: #ffdd33; 
            --dust: #cc44ff; --exp: #33ff55; --stamina: #ff8833;
        }
        * { box-sizing: border-box; user-select: none; -webkit-user-select: none; }
        body { 
            font-family: 'Press Start 2P', cursive; background: var(--bg); color: #e0e0f0; 
            margin: 0; padding: 0; font-size: 8px; text-align: center; overflow: hidden; 
            height: 100vh; width: 100vw; display: flex; justify-content: center; align-items: center;
        }
        #bg-canvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; pointer-events: none; opacity: 0.7; }
        #game { 
            width: 100%; max-width: 1050px; height: 100%; max-height: 500px;
            border: 3px solid var(--border); box-shadow: 0 0 40px rgba(0, 255, 255, 0.25);
            padding: 8px; position: relative; display: flex; flex-direction: row; gap: 8px; z-index: 10;
            background: rgba(4, 4, 12, 0.7); backdrop-filter: blur(6px); border-radius: 8px;
        }
        :fullscreen #game, :-webkit-full-screen #game { border: none; max-width: 100vw; max-height: 100vh; border-radius: 0; }
        .screen { display: none; height: 100%; width: 100%; }
        .screen.active { display: flex; flex-direction: row; gap: 8px; animation: fade 0.35s ease-in-out; }
        @keyframes fade { from { opacity: 0; transform: scale(0.99); } to { opacity: 1; transform: scale(1); } }
        
        /* СИММЕТРИЧНЫЙ ПУЛЬТ УПРАВЛЕНИЯ ПО БОКАМ */
        .side-pad-l, .side-pad-r { width: 21%; height: 100%; display: flex; flex-direction: column; justify-content: center; gap: 5px; }
        .center-view { width: 58%; height: 100%; display: flex; flex-direction: column; justify-content: space-between; overflow: hidden; }
        
        h1 { font-size: 12px; color: var(--acc); text-shadow: 0 0 10px var(--acc); margin: 3px 0; text-transform: uppercase; }
        .panel { background: var(--panel); border: 2px solid var(--border); padding: 8px; border-radius: 6px; position: relative; box-shadow: 0 4px 10px rgba(0,0,0,0.8); }
        
        .btn { 
            background: linear-gradient(#1c2c4a, #0f1f2f); border: 2px solid #5588aa; color: #fff; padding: 11px; 
            margin: 2px 0; cursor: pointer; font-family: 'Press Start 2P', cursive; font-size: 7px; text-transform: uppercase; width: 100%;
            border-radius: 4px; box-shadow: 0 3px 0 #000; text-shadow: 1px 1px #000;
        }
        .btn:active { border-style: inset; transform: translateY(2px); box-shadow: 0 1px 0 #000; }
        .btn:disabled { opacity: 0.3; cursor: not-allowed; transform: none !important; box-shadow: 0 3px 0 #000 !important; }
        .btn-acc { color: var(--acc); border-color: var(--acc); }

        .pad-btn { 
            font-family: 'Press Start 2P', cursive; font-size: 14px; color: #fff;
            background: #151535; border: 2px solid #445599; border-radius: 8px;
            padding: 14px 0; width: 100%; cursor: pointer; box-shadow: 0 4px 0 #000;
        }
        .pad-btn:active { background: #070712; transform: translateY(2px); box-shadow: 0 1px 0 #000; color: var(--acc); border-color: var(--acc); }
        .pad-action { background: #3b1540; border-color: #8a3c8a; font-size: 6.5px; padding: 11px 0; }

        .bar { width: 100%; height: 12px; background: #111; border: 2px solid #fff; position: relative; margin: 1px 0; border-radius: 2px; }
        .fill { height: 100%; transition: width 0.2s ease; }
        .bar-txt { position: absolute; width: 100%; text-align: center; top: 2px; left: 0; font-size: 6px; color: #fff; text-shadow: 1px 1px #000; font-weight: bold; }

        /* Скоростной движок Canvas карт */
        #viewport { 
            width: 100%; flex-grow: 1; border: 2px solid var(--border); 
            background: #000; position: relative; border-radius: 6px;
            box-shadow: inset 0 0 30px #000; display: flex; align-items: center; justify-content: center;
        }
        #map-canvas { display: block; image-rendering: pixelated; width: 100%; height: 100%; }

        .story-box { min-height: 105px; background: rgba(0,0,0,0.92); border: 2px double var(--acc); padding: 12px; text-align: left; position: relative; border-radius: 4px; }
        .speaker-tag { position: absolute; top: -9px; left: 10px; background: var(--acc); color: #000; padding: 2px 6px; font-size: 6px; font-weight: bold; }

        .stage { position: relative; height: 125px; background: rgba(4,4,12,0.85); border: 2px solid #6c2222; border-radius: 6px; overflow: hidden; }
        .fighter-ct { position: absolute; bottom: 10px; transition: transform 0.15s ease; width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; }
        #h-spr-ct { left: 15%; transform: scaleX(-1); } #e-spr-ct { right: 15%; }
        .sprite { font-size: 46px; filter: drop-shadow(0 8px 4px rgba(0,0,0,0.8)); }
        .floating-text { position: absolute; font-size: 10px; font-weight: bold; text-shadow: 2px 2px #000; animation: floatUp 1.1s forwards; pointer-events: none; z-index: 150; }
        #battle-log { height: 75px; overflow-y: auto; background: #000; color: #4aff4a; padding: 5px; text-align: left; border: 1px solid #334; font-size: 6.5px; line-height: 1.5; }
        #toasts { position: absolute; top: 12px; width: 100%; display: flex; flex-direction: column; align-items: center; pointer-events: none; z-index: 5000; }
        .toast { background: rgba(4,8,20,0.96); border: 2px solid var(--acc); color: #fff; padding: 8px 16px; margin-bottom: 3px; border-radius: 4px; font-size: 7.5px; animation: tAnim 2.4s forwards; }

        .inv-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 5px; margin: 4px 0; }
        .inv-slot { aspect-ratio: 1; background: #03030a; border: 2px solid #334; display: flex; align-items: center; justify-content: center; font-size: 22px; cursor: pointer; border-radius: 4px; position: relative; }
        .inv-slot span { position: absolute; bottom: 2px; right: 3px; font-size: 5px; color: #aaa; }
        .t-1 { border-color: #5f5; } .t-2 { border-color: #55f; } .t-3 { border-color: #a3f; } .t-4 { border-color: #fa0; } .t-5 { border-color: #f33; }

        #modal { display: none; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); z-index: 550; justify-content: center; align-items: center; backdrop-filter: blur(5px); }
        .modal-content { background: var(--panel); border: 2px solid var(--acc); padding: 18px; width: 90%; max-width: 400px; text-align: center; border-radius: 8px; box-shadow: 0 0 50px rgba(0,255,255,0.3); }

        @keyframes floatUp { 0% { opacity: 1; transform: translateY(0); } 100% { opacity: 0; transform: translateY(-45px) scale(1.3); } }
        @keyframes tAnim { 0%, 100% { opacity: 0; transform: translateY(-12px); } 10%, 90% { opacity: 1; transform: translateY(0); } }
        .breathe-anim { animation: brth 2.4s infinite ease-in-out; }
        @keyframes brth { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-5px); } }
    </style>
</head>
<body>
    <canvas id="bg-canvas"></canvas>
    
    <div id="game">
        <div id="toasts"></div>
        <div id="modal"><div class="modal-content" id="modal-body"></div></div>

        <!-- ==================== ЭКРАН 1: ГЛАВНОЕ МЕНЮ ==================== -->
        <div id="scr-menu" class="screen active">
            <div class="side-pad-l" style="width: 45%; justify-content: center;">
                <h1>NEXUS MMO</h1>
                <p style="font-size:6px; color:var(--acc);">СИМФОНИЯ МИРОВ</p>
                <div style="font-size:65px; margin:15px 0; animation: brth 3s infinite alternate;">🌐</div>
            </div>
            <div class="side-pad-r" style="width: 50%; justify-content: center;">
                <input type="text" id="nickname-input" placeholder="ИМЯ ГЕРОЯ" maxlength="10" style="background:#000; border:2px solid var(--border); color:#fff; padding:10px; text-align:center; font-family:inherit; font-size:8px; margin-bottom:4px; border-radius:4px; outline:none;">
                <button class="btn btn-acc" onclick="Game.connectServer()">ВХОД В NEXUS</button>
                <button class="btn" onclick="Game.load()">ЗАГРУЗИТЬ СОХРАНЕНИЕ</button>
                <button class="btn" onclick="UI.openHeroSelect()">ВЫБОР КЛАССА</button>
                <button class="btn" style="background:#151525;" onclick="UI.toggleFullscreen()">ПОЛНЫЙ ЭКРАН 🔲</button>
            </div>
        </div>

        <!-- ==================== ЭКРАН 2: ВЫБОР ГЕРОЯ ==================== -->
        <div id="scr-hero" class="screen">
            <div class="side-pad-l" style="width:35%;">
                <h1>ЧЕМПИОНЫ</h1>
                <div style="display:flex; gap:4px;">
                    <button class="btn" onclick="Game.cycleHero(-1)">◀</button>
                    <button class="btn" onclick="Game.cycleHero(1)">▶</button>
                </div>
                <div id="hero-show-sprite" style="font-size:75px; margin-top:15px; animation: brth 2.5s infinite;">⚔️</div>
            </div>
            <div class="side-pad-r" style="width:62%;">
                <div id="hero-show-info" class="panel" style="text-align:left; line-height:1.6; font-size:7px; height:100%; overflow-y:auto;"></div>
                <button class="btn btn-acc" onclick="UI.show('scr-menu')">ВЕРНУТЬСЯ В МЕНЮ</button>
            </div>
        </div>

        <!-- ==================== ЭКРАН 3: СЮЖЕТ И КАТ-СЦЕНЫ ==================== -->
        <div id="scr-story" class="screen">
            <div class="center-view" style="width:100%; height:100%; justify-content:center; gap:8px;">
                <h1 id="story-title">ГЛАВА</h1>
                <div class="story-box">
                    <div id="story-speaker" class="speaker-tag">Рассказчик</div>
                    <div id="story-text" class="bar-text" style="position:static; text-align:left; line-height:1.6; font-size:8px;">...</div>
                </div>
                <button id="story-next-btn" class="btn btn-acc" style="max-width:180px; margin:0 auto;" onclick="Cutscene.next()">ДАЛЕЕ >></button>
            </div>
        </div>

        <!-- ==================== ЭКРАН 4: ИГРОВОЙ ПРОЦЕСС (КАРТА) ==================== -->
        <div id="scr-adv" class="screen">
            <!-- ЛЕВЫЙ СИММЕТРИЧНЫЙ ПУЛЬТ -->
            <div class="side-pad-l">
                <button class="pad-btn" onclick="Map.move(0, -1)">▲</button>
                <button class="pad-btn" onclick="Map.move(-1, 0)">◀</button>
                <button class="pad-btn" onclick="Map.move(0, 1)">▼</button>
                <button class="pad-btn pad-action" onclick="Camp.open()">🎒 СУМКА</button>
            </div>
            
            <!-- СТРОГО ЦЕНТРАЛЬНЫЙ ЭКРАН КАРТЫ С CANVAS -->
            <div class="center-view">
                <div class="panel" style="display:grid; grid-template-columns: 1fr 1fr 1fr; font-size:6.5px; padding:4px; margin:0; text-align:center;">
                    <div style="color:var(--hp)">❤️ HP:<span id="a-hp"></span></div>
                    <div style="color:var(--gold)">💰 GLD:<span id="a-gld"></span></div>
                    <div style="color:var(--mana)">🔮 ЯРУС:<span id="a-floor"></span></div>
                </div>
                <div id="viewport"><canvas id="map-canvas"></canvas></div>
                <div class="panel" style="padding:4px; font-size:5.5px; color:#aaa; margin:0; display:flex; justify-content:space-between; align-items:center;">
                    <span>Кирки: <span id="a-picks" style="color:#fff"></span> ⛏️ | Ключи: <span id="a-keys" style="color:#fff"></span> 🗝️</span>
                    <span id="a-chapter-name" style="color:var(--acc)"></span>
                </div>
            </div>
            
            <!-- ПРАВЫЙ СИММЕТРИЧНЫЙ ПУЛЬТ -->
            <div class="side-pad-r">
                <button class="pad-btn" onclick="Map.move(0, -1)">▲</button>
                <button class="pad-btn" onclick="Map.move(1, 0)">▶</button>
                <button class="pad-btn" onclick="Map.move(0, 1)">▼</button>
                <button class="pad-btn pad-action" onclick="UI.show('scr-quests')">💬 ЧАТ / ТОП</button>
            </div>
        </div>

        <!-- ==================== ЭКРАН 5: ЛАГЕРЬ ПЕРСОНАЖА ==================== -->
        <div id="scr-camp" class="screen">
            <div class="side-pad-l" style="width:30%;">
                <h2>СТАТИСТИКА</h2>
                <div class="panel" style="text-align:left; font-size:6px; line-height:1.4;">
                    <p style="color:var(--mana)">ГЕРОЙ: <span id="c-name"></span></p>
                    <p>УРОВЕНЬ: <span id="c-lvl"></span></p>
                    <p>АТАКА: <span id="c-dmg" style="color:var(--hp)"></span></p>
                    <p>ЗАЩИТА: <span id="c-def" style="color:var(--mana)"></span></p>
                    <p>Очки: <span id="c-sp" style="color:var(--gold)">0</span></p>
                </div>
                <div style="display:flex; gap:2px;">
                    <button class="btn" style="font-size:6px; padding:6px;" onclick="Game.addStat('dmg')">+⚔️ Сила</button>
                    <button class="btn" style="font-size:6px; padding:6px;" onclick="Game.addStat('hp')">+❤️ Жизнь</button>
                </div>
                <button class="btn" style="background:#223; color:var(--acc);" onclick="UI.openSettings()">⚙️ НАСТРОЙКИ</button>
            </div>
            <div class="center-view" style="width:68%;">
                <div class="panel">
                    <div style="display:flex; justify-content:space-around; margin-bottom:4px;">
                        <div class="inv-slot" id="eq-w" style="width:45%; font-size:7px;" onclick="Camp.unequip('w')">⚔️ Оружие</div>
                        <div class="inv-slot" id="eq-a" style="width:45%; font-size:7px;" onclick="Camp.unequip('a')">🛡️ Доспех</div>
                    </div>
                    <div style="display:flex; justify-content:space-between; font-size:6px; color:#aaa; margin-bottom:2px;">
                        <span>ИНВЕНТАРЬ ПЕРСОНАЖА</span><span>Пыль: <span id="c-dust" style="color:var(--dust)">0</span>💎</span>
                    </div>
                    <div class="inv-grid" id="inventory-container"></div>
                </div>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:4px;">
                    <button class="btn" style="color:var(--dust)" onclick="Camp.craft()">🔨 КУЗНИЦА (25 Пыли)</button>
                    <button class="btn" style="color:var(--hp)" onclick="Camp.buyPotion()">🧪 ЗЕЛЬЕ ОЗ (25💰)</button>
                </div>
                <button class="btn" style="background:#441111; margin-top:2px;" onclick="Game.saveAndExit()">💾 СОХРАНИТЬ И ВЫЙТИ</button>
            </div>
        </div>

        <!-- ==================== ЭКРАН 6: БОЕВАЯ АРЕНА (ATB) ==================== -->
        <div id="scr-battle" class="screen">
            <div class="side-pad-l">
                <button class="pad-btn" style="background:#422;" onclick="Combat.action(1)">⚔️<br><span style="font-size:5px;">УДАР</span></button>
                <button class="pad-btn" style="background:#224;" onclick="Combat.action(2)">✨<br><span style="font-size:5px;">СКИЛЛ</span></button>
            </div>
            
            <div class="center-view">
                <div class="panel" style="display:flex; justify-content:space-between; font-size:7px; padding:4px; margin:0;">
                    <span id="b-pname" style="color:var(--mana);">ГЕРОЙ</span>
                    <span style="color:#555">VS</span>
                    <span id="b-ename" style="color:var(--hp);">ВРАГ</span>
                </div>
                
                <div class="stage" id="bat-stage">
                    <div id="player-sprite" class="fighter breathe-anim">⚔️</div>
                    <div id="enemy-sprite" class="fighter breathe-anim">👾</div>
                </div>
                
                <div class="panel" style="margin:0; padding:4px;">
                    <div class="bar"><div id="b-php-bar" class="fill" style="background:#22cc22; width:100%;"></div><div class="bar-txt" id="b-php-txt"></div></div>
                    <div class="bar"><div id="b-ehp-bar" class="fill" style="background:var(--hp); width:100%;"></div><div class="bar-txt" id="b-ehp-txt"></div></div>
                    <div style="display:flex; justify-content:space-between; font-size:5px; margin-top:2px;">
                        <div class="bar" style="width:46%; height:4px; border:none;"><div id="atb-p" class="fill" style="background:var(--mana); width:0%;"></div></div>
                        <div class="bar" style="width:46%; height:4px; border:none;"><div id="atb-e" class="fill" style="background:var(--gold); width:0%;"></div></div>
                    </div>
                </div>
                <div id="battle-log" class="panel" style="margin:0; flex-grow:1;"></div>
            </div>
            
            <div class="side-pad-r">
                <button class="pad-btn" style="background:#242;" onclick="Combat.action(3)">🛡️<br><span style="font-size:6px;">БЛОК</span></button>
                <button class="pad-btn" style="background:#440; border-color:var(--acc);" onclick="Combat.action(4)">☄️<br><span style="font-size:6px; color:var(--acc);">УЛЬТ</span></button>
            </div>
        </div>

        <!-- ==================== ЭКРАН 7: КВЕСТЫ И РЕАЛЬНЫЙ СИНХРО-ЧАТ ==================== -->
        <div id="scr-quests" class="screen">
            <div class="side-pad-l" style="width:40%;">
                <h1>NEXUS СИНХРО-ЧАТ</h1>
                <div class="panel" id="chat-container" style="height:140px; overflow-y:auto; text-align:left; font-size:5.5px; line-height:1.4; background:#020205;"></div>
                <div style="display:flex; gap:2px; margin-top:2px;">
                    <input type="text" id="chat-input" placeholder="Сообщение..." style="flex:1; background:#000; border:1px solid var(--border); color:#fff; font-family:inherit; font-size:6px; padding:4px;">
                    <button class="btn" style="width:auto; margin:0;" onclick="Online.sendMsg()">></button>
                </div>
                <button class="btn" style="background:#3d113d;" onclick="Online.joinGuild()">🧬 СОЗДАТЬ ГИЛЬДИЮ</button>
            </div>
            <div class="col-center" style="width:58%;">
                <h1>РЕЙД И КОНТРАКТЫ МОНИИ</h1>
                <div class="panel" id="raid-boss-panel" style="text-align:left; font-size:6px; background:#1a0505; border-color:var(--hp); margin-bottom:4px;">
                    <div style="color:var(--hp); font-weight:bold;">ГЛОБАЛЬНЫЙ БОСС: <span id="ui-boss-name">-</span></div>
                    <div class="bar" style="height:8px; margin-top:2px;"><div id="ui-boss-hp" class="fill" style="background:var(--hp); width:100%;"></div></div>
                    <div id="ui-boss-hp-txt" style="font-size:5.5px; margin-top:1px;">100000/100000 ОЗ</div>
                </div>
                <div class="panel" id="quest-list" style="flex:1; overflow-y:auto; text-align:left; line-height:1.6; font-size:7.5px;"></div>
                <button class="btn btn-acc" style="padding:12px;" onclick="UI.show('scr-adv')">ВЕРНУТЬСЯ К КАРТЕ</button>
            </div>
        </div>

    </div>

<script>
// ==================== ПРОЦЕДУРНЫЙ КАРТИННЫЙ ДВИЖОК BACKGROUND ====================
const FX = {
    canvas: null, ctx: null, particles: [], currentZone: 0, quality: "high",
    init() {
        this.canvas = document.getElementById('bg-canvas'); this.ctx = this.canvas.getContext('2d');
        this.resize(); window.addEventListener('resize', () => this.resize());
        setInterval(() => this.tick(), 40);
    },
    resize() { this.canvas.width = window.innerWidth; this.canvas.height = window.innerHeight; },
    addSparks(x, y, color, count) {
        if(this.quality === "low") return;
        for(let i=0; i<count; i++) { this.particles.push({ x, y, vx: (Math.random()-0.5)*8, vy: (Math.random()-0.5)*8 - 2, life: 1, color, sz: Math.random()*2+2 }); }
    },
    tick() {
        let w = this.canvas.width, h = this.canvas.height; this.ctx.clearRect(0, 0, w, h);
        let grad = this.ctx.createLinearGradient(0, 0, 0, h);
        if(this.currentZone === 0) { grad.addColorStop(0, '#041c04'); grad.addColorStop(1, '#010801'); }
        else if(this.currentZone === 1) { grad.addColorStop(0, '#150326'); grad.addColorStop(1, '#06010d'); }
        else if(this.currentZone === 2) { grad.addColorStop(0, '#09152b'); grad.addColorStop(1, '#020614'); }
        else if(this.currentZone === 3) { grad.addColorStop(0, '#1c1203'); grad.addColorStop(1, '#0a0601'); }
        else { grad.addColorStop(0, '#260404'); grad.addColorStop(1, '#0d0101'); }
        
        this.ctx.fillStyle = grad; this.ctx.fillRect(0, 0, w, h);

        if(this.quality === "high" && Math.random() < 0.2) {
            if(this.currentZone === 0) this.particles.push({ x: Math.random()*w, y: -10, vx: -1, vy: 2, life: 1, color: '#ffb6c1', sz: 3 }); 
            if(this.currentZone === 2) this.particles.push({ x: Math.random()*w, y: -10, vx: 0, vy: 3, life: 1, color: '#ffffff', sz: 2 }); 
            if(this.currentZone === 4) this.particles.push({ x: Math.random()*w, y: h+10, vx: (Math.random()-0.5)*2, vy: -3, life: 1, color: '#ff5500', sz: 2 }); 
        }

        for(let i=this.particles.length-1; i>=0; i--) {
            let p = this.particles[i]; p.x += p.vx; p.y += p.vy; p.life -= 0.015;
            if(p.life <= 0) { this.particles.splice(i, 1); continue; }
            this.ctx.globalAlpha = p.life; this.ctx.fillStyle = p.color;
            this.ctx.fillRect(p.x, p.y, p.sz, p.sz); 
        }
        this.ctx.globalAlpha = 1;
    }
};

// ==================== ПРОЦЕДУРНЫЙ МНОГОГОЛОСНЫЙ САУНДТРЕК ====================
const Music = {
    timer: null, tickIndex: 0, trackName: '', mute: false,
    notes: { A2:110, C3:130.8, E3:164.8, A3:220, C4:261.6, D4:293.7, E4:329.6, G4:392, A4:440 },
    tracks: {
        menu: { tempo: 380, bass: ['A2','A2','C3','E3'], lead: ['A3','C4','E4','G4','E4','C4','A3','E3'], type:'sine' },
        explore: { tempo: 480, bass: ['C3','C3','E3','A2'], lead: ['E4','D4','C4','D4','E4','G4','A4','E4'], type:'triangle' },
        battle: { tempo: 240, bass: ['A2','E3','A2','F3'], lead: ['A3','E4','D4','E4','F4','E4','D4','C4'], type:'sawtooth' }
    },
    play(name) {
        if(this.trackName === name) return; this.trackName = name; clearInterval(this.timer);
        if(!name || !AudioEngine.ctx || this.mute) return; let t = this.tracks[name]; this.tickIndex = 0;
        
        this.timer = setInterval(() => {
            if(this.mute) return;
            let ctx = AudioEngine.ctx; let now = ctx.currentTime;
            if(this.tickIndex % 2 === 0) {
                let bn = t.bass[Math.floor(this.tickIndex / 2) % t.bass.length];
                let o = ctx.createOscillator(), g = ctx.createGain(); o.type = 'triangle';
                o.frequency.setValueAtTime(this.notes[bn], now); g.gain.setValueAtTime(0.01, now);
                g.gain.exponentialRampToValueAtTime(0.001, now + 0.4); o.connect(g); g.connect(ctx.destination);
                o.start(now); o.stop(now + 0.4);
            }
            let ln = t.lead[this.tickIndex % t.lead.length];
            let oL = ctx.createOscillator(), gL = ctx.createGain(); oL.type = t.type;
            oL.frequency.setValueAtTime(this.notes[ln], now); gL.gain.setValueAtTime(0.01, now);
            gL.gain.exponentialRampToValueAtTime(0.001, now + 0.2); oL.connect(gL); gL.connect(ctx.destination);
            oL.start(now); oL.stop(now + 0.2);

            this.tickIndex++;
        }, t.tempo);
    }
};

// ==================== СЮЖЕТ И РЕЧЕВЫЕ КАТ-СЦЕНЫ ====================
const Cutscene = {
    lines: [], lineIdx: 0, charIdx: 0, timer: null,
    chapters: [
        { title: "Глава 1: Изумрудный Вход Монии", text: "Аватар подошел к священным рубежам. Зеленые Сады окутаны туманом Бездны. Сакура опадает на сталь клинка..." },
        { title: "Глава 2: Токсичные Болота Ведьмы", text: "Сырость проникает под кожу. Фиолетовые болотные газы поднимаются вокруг. Будьте аккуратны, ловушки скрыты повсюду!" },
        { title: "Глава 3: Морозная Ледяная Цитадель", text: "Снежная пиксельная буря бьет в лицо. Стены скованы льдом. Древние каменные големы проснулись от шагов Рассвета." },
        { title: "Глава 4: Катакомбы Павших Королей", text: "Гробницы разграблены демонами. Здесь спрятаны сундуки легендарных реликвий. Ключи — твой единственный шанс выжить." },
        { title: "Глава 5: Финал Тьмы", text: "Реки магмы текут вокруг трона. Тамуз ждет тебя в самом сердце Пекла. Империя Мония уповает на твою победу, Избранный!" }
    ],
    start(zoneIdx) {
        Music.play('menu'); document.getElementById('story-title').textContent = this.chapters[zoneIdx].title;
        this.lines = [ { s: "Рассказчик", t: this.chapters[zoneIdx].text }, { s: "Герой", t: "Я заставлю Бездну отступить и вернуть Рассвет Монии!" } ];
        this.lineIdx = 0; UI.show('scr-story'); this.type();
    },
    type() {
        let current = this.lines[this.lineIdx]; document.getElementById('story-speaker').textContent = current.s;
        let box = document.getElementById('story-text'); box.textContent = ''; this.charIdx = 0; clearInterval(this.timer);
        document.getElementById('story-next-btn').disabled = true;

        this.timer = setInterval(() => {
            if(this.charIdx < current.t.length) {
                box.textContent += current.t.charAt(this.charIdx);
                if(this.charIdx % 2 === 0 && AudioEngine.ctx && !Music.mute) {
                    let freq = current.s === 'Рассказчик' ? 120 : 210;
                    let o = AudioEngine.ctx.createOscillator(), g = AudioEngine.ctx.createGain(); o.type='sine';
                    o.frequency.setValueAtTime(freq + Math.random()*15, AudioEngine.ctx.currentTime); g.gain.setValueAtTime(0.01, AudioEngine.ctx.currentTime);
                    g.gain.linearRampToValueAtTime(0, AudioEngine.ctx.currentTime+0.04); o.connect(g); g.connect(AudioEngine.ctx.destination);
                    o.start(); o.stop(AudioEngine.ctx.currentTime+0.04);
                }
                this.charIdx++;
            } else { clearInterval(this.timer); document.getElementById('story-next-btn').disabled = false; }
        }, 25);
    },
    next() {
        this.lineIdx++;
        if(this.lineIdx < this.lines.length) { this.type(); }
        else { UI.show('scr-adv'); Music.play('explore'); Map.gen(); }
    }
};

// ==================== НАСТОЯЩАЯ СИНХРОНИЗАЦИЯ С СЕРВЕРОМ ====================
const Online = {
    myId: "id_" + Math.floor(Math.random()*1000000),
    otherPlayers: [], chatPendingMsg: null, bossDmgQueue: 0, guildToCreate: null,
    init() {
        this.syncWithServer();
        setInterval(() => this.syncWithServer(), 2000);
    },
    syncWithServer() {
        if(!Game.p) return;
        
        let payload = {
            id: this.myId,
            name: Game.p.n,
            x: Map.px,
            y: Map.py,
            sprite: Game.p.spr,
            lvl: Game.p.lvl,
            guild: Game.p.guild,
            chat_msg: this.chatPendingMsg,
            boss_damage: this.bossDmgQueue,
            create_guild: this.guildToCreate
        };
        
        this.chatPendingMsg = null;
        this.bossDmgQueue = 0;
        this.guildToCreate = null;

        fetch('/api/mmo/sync', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(res => res.json())
        .then(data => {
            if(data.status === "success") {
                this.otherPlayers = data.players;
                document.getElementById('ui-online').textContent = this.otherPlayers.length + 1;
                
                // Обновление Рейд Босса
                document.getElementById('ui-boss-name').textContent = data.boss.name;
                document.getElementById('ui-boss-hp').style.width = `${(data.boss.hp / data.boss.max_hp)*100}%`;
                document.getElementById('ui-boss-hp-txt').textContent = `${data.boss.hp}/${data.boss.max_hp} ОЗ`;
                
                // Скролл-чат синхронизация
                let box = document.getElementById('chat-container');
                box.innerHTML = data.chat.map(c => `<div><span style="color:${c.color || 'var(--acc)'}">[${c.name}]:</span> ${c.m || c.msg}</div>`).join('');
                
                Map.draw();
            }
        })
        .catch(err => console.log("Nexus Sync Server Disconnect"));
    },
    sendMsg() {
        let input = document.getElementById('chat-input'); let text = input.value.trim();
        if(!text) return;
        this.chatPendingMsg = text;
        input.value = '';
        this.syncWithServer();
    },
    joinGuild() {
        if(Game.p.guild) return UI.toast("Вы уже в гильдии!", "#f33");
        let gName = prompt("Введите название новой гильдии:");
        if(gName && gName.trim().length >= 3) {
            if(Game.p.gld >= 100) {
                Game.p.gld -= 100;
                Game.p.guild = gName.trim();
                this.guildToCreate = Game.p.guild;
                UI.toast(`Запрос на создание гильдии [${Game.p.guild}] отправлен!`);
                this.syncWithServer();
            } else UI.toast("Нужно 100 золота!", "#f33");
        }
    }
};

// ==================== ОСТАЛЬНЫЕ МЕХАНИКИ И АНИМАЦИИ ====================
const AudioEngine = {
    ctx: null,
    init() { if(!this.ctx) this.ctx = new (window.AudioContext || window.webkitAudioContext)(); },
    play(type) {
        if(Music.mute) return;
        this.init(); if(!this.ctx) return;
        const o = this.ctx.createOscillator(), g = this.ctx.createGain(); o.connect(g); g.connect(this.ctx.destination);
        const t = this.ctx.currentTime;
        if(type==='step') { o.type='triangle'; o.frequency.setValueAtTime(90, t); g.gain.setValueAtTime(0.04, t); g.gain.linearRampToValueAtTime(0, t+0.05); o.start(t); o.stop(t+0.05); }
        else if(type==='hit') { o.type='sawtooth'; o.frequency.setValueAtTime(145, t); o.frequency.linearRampToValueAtTime(40, t+0.1); g.gain.setValueAtTime(0.15, t); g.gain.linearRampToValueAtTime(0, t+0.1); o.start(t); o.stop(t+0.1); }
        else if(type==='loot') { o.type='sine'; o.frequency.setValueAtTime(440, t); o.frequency.setValueAtTime(660, t+0.08); g.gain.setValueAtTime(0.12, t); g.gain.linearRampToValueAtTime(0, t+0.2); o.start(t); o.stop(t+0.2); }
        else if(type==='ult') { o.type='square'; o.frequency.setValueAtTime(95, t); o.frequency.linearRampToValueAtTime(850, t+0.45); g.gain.setValueAtTime(0.25, t); g.gain.linearRampToValueAtTime(0, t+0.45); o.start(t); o.stop(t+0.45); }
    }
};

const DB = {
    heroes: [
        { id:'alu', n:'АЛУКАРД', spr:'⚔️', hp:320, dmg:45, def:14, desc:'Боец. Пассивный вампиризм: возвращает 25% ОЗ от ударов.' },
        { id:'mia', n:'МИЯ', spr:'🏹', hp:220, dmg:55, def:8, desc:'Стрелок. Пассивный крит: 30% шанс нанести двойной урон.' },
        { id:'tig', n:'ТИГРИЛ', spr:'🛡️', hp:450, dmg:30, def:25, desc:'Танк. Бастион: Снижает весь входящий урон на 5 ед.' },
        { id:'gus', n:'ГОССЕН', spr:'🗡️', hp:230, dmg:50, def:12, desc:'Убийца. Ультимейт карает х1.5 уроном при низком ОЗ врага.' },
        { id:'eud', n:'ЭЙДОРА', spr:'⚡', hp:200, dmg:65, def:10, desc:'Маг. Навыки наносят мощнейший шоковый электро-урон.' },
        { id:'zil', n:'ЗИЛОНГ', spr:'🐉', hp:280, dmg:42, def:16, desc:'Воин. Скорость позволяет наносить двойные атаки.' },
        { id:'fra', n:'ФРАНКО', spr:'🪝', hp:480, dmg:25, def:28, desc:'Танк. Начинает бой со случайным щитом.' },
        { id:'sab', n:'САБЕР', spr:'🤺', hp:230, dmg:48, def:11, desc:'Ассасин. Атаки игнорируют 50% защиты противника.' }
    ],
    enemies: [
        { n:"Миньон Бездны", spr:"👺", hp:110, dmg:16, def:6, xp:30, gld:20 },
        { n:"Адский Волк", spr:"🐺", hp:150, dmg:22, def:10, xp:45, gld:30 },
        { n:"Голем Скал", spr:"🪨", hp:320, dmg:34, def:25, xp:75, gld:55 },
        { n:"Проклятый Рыцарь", spr:"💀", hp:400, dmg:45, def:20, xp:110, gld:75 },
        { n:"ТАМУЗ [ГЕНЕРАЛ]", spr:"🔥", hp:1400, dmg:85, def:50, xp:999, gld:500, isBoss: true }
    ],
    lootTable: [
        { type:'w', name:'Меч Империи', icon:'🗡️', stat:'dmg', v:12, rare:'common' },
        { type:'w', name:'Клинок Отчаяния Монии', icon:'⚔️', stat:'dmg', v:42, rare:'legend' },
        { type:'a', name:'Кираса Защитника', icon:'👕', stat:'def', v:10, rare:'common' },
        { type:'a', name:'Доспех Бессмертия', icon:'🛡️', stat:'def', v:35, rare:'legend' }
    ]
};

function genItem(zoneLvl) {
    let base = DB.lootTable[Math.floor(Math.random()*DB.lootTable.length)];
    let modifier = 2 + Math.floor(Math.random()*5) + (zoneLvl * 6);
    return { type: base.type, n: `Элит. ${base.name}`, icon: base.icon, stat: base.stat, v: base.v + modifier, rare: base.rare, upg: 0 };
}

// ==================== CANVAS КАРТОГРАФИЧЕСКИЙ ДВИЖОК ====================
const Map = {
    w: 40, h: 40, grid: [], px: 5, py: 5, fog: [], canvas: null, ctx: null, tileSize: 40,
    initCanvas() {
        this.canvas = document.getElementById('map-canvas');
        this.ctx = this.canvas.getContext('2d');
        this.canvas.width = 11 * this.tileSize;
        this.canvas.height = 11 * this.tileSize;
    },
    gen() {
        this.initCanvas();
        this.grid = Array(this.h).fill().map(() => Array(this.w).fill(1));
        let cx = 20, cy = 20; this.px = cx; this.py = cy; this.grid[cy][cx] = 0;
        
        for(let i=0; i<1000; i++) {
            let dir = [{x:0,y:1},{x:0,y:-1},{x:1,y:0},{x:-1,y:0}][Math.floor(Math.random()*4)];
            if(cx+dir.x>1 && cx+dir.x<this.w-2 && cy+dir.y>1 && cy+dir.y<this.h-2) { cx+=dir.x; cy+=dir.y; this.grid[cy][cx]=0; }
        }
        let floors = [];
        for(let y=1; y<this.h-1; y++) for(let x=1; x<this.w-1; x++) if(this.grid[y][x]===0 && (x!==this.px || y!==this.py)) floors.push({x,y});
        floors.sort(() => Math.random() - 0.5);

        if(floors.length > 0) this.grid[floors.pop().y][floors.pop().x] = Game.zIdx === 4 ? 6 : 5;
        let nE = 20, nC = 12;
        while(floors.length > 0 && nE-- > 0) this.grid[floors.pop().y][floors.pop().x] = 2;
        while(floors.length > 0 && nC-- > 0) this.grid[floors.pop().y][floors.pop().x] = Math.random()<0.35 ? 8 : 4;
        while(floors.length > 0 && Math.random()<0.04) this.grid[floors.pop().y][floors.pop().x] = 9;
        while(floors.length > 0 && Math.random()<0.04) this.grid[floors.pop().y][floors.pop().x] = 7;

        this.fog = Array(this.h).fill().map(() => Array(this.w).fill(true));
        this.updateFog(); this.draw();
    },
    updateFog() {
        let r = 5;
        for(let y=this.py-r; y<=this.py+r; y++) {
            for(let x=this.px-r; x<=this.px+r; x++) {
                if(y>=0 && y<this.h && x>=0 && x<this.w) { if((x-this.px)**2 + (y-this.py)**2 <= r**2) this.fog[y][x] = false; }
            }
        }
    },
    draw() {
        if(!this.ctx) return;
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        let startX = this.px - 5;
        let startY = this.py - 5;

        for(let y = 0; y < 11; y++) {
            for(let x = 0; x < 11; x++) {
                let mapX = startX + x;
                let mapY = startY + y;
                let dx = x * this.tileSize;
                let dy = y * this.tileSize;

                if(mapY<0 || mapY>=this.h || mapX<0 || mapX>=this.w || this.fog[mapY][mapX]) {
                    this.ctx.fillStyle = '#000000';
                    this.ctx.fillRect(dx, dy, this.tileSize, this.tileSize);
                    continue;
                }

                let tile = this.grid[mapY][mapX];
                this.ctx.fillStyle = tile === 1 ? '#0c0c14' : '#111b11';
                this.ctx.fillRect(dx, dy, this.tileSize, this.tileSize);
                this.ctx.strokeStyle = 'rgba(40,60,40,0.1)';
                this.ctx.strokeRect(dx, dy, this.tileSize, this.tileSize);

                this.ctx.font = '16px sans-serif';
                this.ctx.textAlign = 'center';
                this.ctx.textBaseline = 'middle';
                
                if(mapX === this.px && mapY === this.py) {
                    this.ctx.fillText(Game.p.spr, dx + 20, dy + 20);
                } else {
                    if(tile === 2) this.ctx.fillText('👾', dx + 20, dy + 20);
                    else if(tile === 4) this.ctx.fillText('🧰', dx + 20, dy + 20);
                    else if(tile === 5) this.ctx.fillText('🪜', dx + 20, dy + 20);
                    else if(tile === 6) this.ctx.fillText('🔥', dx + 20, dy + 20);
                    else if(tile === 7) this.ctx.fillText('⛲', dx + 20, dy + 20);
                    else if(tile === 8) this.ctx.fillText('🗝️', dx + 20, dy + 20);
                    else if(tile === 9) this.ctx.fillText('🛒', dx + 20, dy + 20);
                }

                // Синхронизация реальных онлайн-игроков на Canvas карте
                let op = Online.otherPlayers.find(p => p.x === mapX && p.y === mapY);
                if(op && tile === 0 && (mapX!==this.px || mapY!==this.py)) {
                    this.ctx.fillText(op.sprite, dx + 20, dy + 20);
                    this.ctx.font = '6px "Press Start 2P"';
                    this.ctx.fillStyle = '#00ffff';
                    this.ctx.fillText(op.name, dx + 20, dy + 6);
                }
                
                let dist = Math.max(Math.abs(x-5), Math.abs(y-5));
                if(dist >= 4) {
                    this.ctx.fillStyle = 'rgba(0,0,0,0.4)';
                    this.ctx.fillRect(dx, dy, this.tileSize, this.tileSize);
                }
            }
        }
    },
    click(x, y) { },
    move(dx, dy) {
        let nx = this.px + dx, ny = this.py + dy;
        if(nx<0 || nx>=this.w || ny<0 || ny>=this.h || this.grid[ny][nx]===1) return;
        
        this.px = nx; this.py = ny; AudioEngine.play('step'); this.updateFog();
        let tile = this.grid[ny][nx];
        
        if(tile === 2) { this.grid[ny][nx]=0; return Combat.start(false); }
        if(tile === 6) { this.grid[ny][nx]=0; return Combat.start(true); }
        if(tile === 4) {
            if(Game.p.keys > 0) {
                Game.p.keys--; this.grid[ny][nx]=0; AudioEngine.play('loot');
                let it = genItem(Game.zIdx); Game.p.inv.push(it); UI.toast(`Лут: ${it.n}!`, "var(--acc)");
                Game.checkQuests('loot');
            } else { UI.toast("Нужен ключ!", "#ff4444"); this.px-=dx; this.py-=dy; }
        }
        else if(tile === 8) { Game.p.keys++; this.grid[ny][nx]=0; AudioEngine.play('loot'); UI.toast("Подобран ключ!"); }
        else if(tile === 7) { Game.p.hp=Game.p.mhp; this.grid[ny][nx]=0; AudioEngine.play('loot'); UI.toast("Исцеление у фонтана!", "#5f5"); }
        else if(tile === 9) {
            if(Game.p.gld >= 80) { Game.p.gld -= 80; this.grid[ny][nx]=0; let it = genItem(Game.zIdx+1); Game.p.inv.push(it); UI.toast(`Куплено: ${it.n}`, "var(--dust)"); }
            else { UI.toast("Не хватает золота (80💰)", "#ff4444"); this.px-=dx; this.py-=dy; }
        }
        else if(tile === 5) {
            Game.zIdx++; Game.p.picks += 2; UI.toast(`Спуск на уровень ${Game.zIdx+1}!`); Cutscene.start(Game.zIdx); return;
        }
        this.draw(); UI.updateAdv();
    }
};

const Camp = {
    open() {
        Game.calcStats();
        document.getElementById('c-name').textContent = Game.p.n; document.getElementById('c-lvl').textContent = Game.p.lvl;
        document.getElementById('c-xp-txt').textContent = `${Game.p.xp}/${Game.p.nxp}`; document.getElementById('c-exp-bar').style.width = `${(Game.p.xp/Game.p.nxp)*100}%`;
        document.getElementById('c-hp').textContent = `${Game.p.hp}/${Game.p.mhp}`; document.getElementById('c-dmg').textContent = Game.p.dmg;
        document.getElementById('c-def').textContent = Game.p.def; document.getElementById('c-sp').textContent = Game.p.sp;
        document.getElementById('c-dust').textContent = Game.p.dust; document.getElementById('c-inv-c').textContent = Game.p.inv.length;

        document.getElementById('eq-w').innerHTML = Game.p.eq.w ? `${Game.p.eq.w.icon} +${Game.p.eq.w.v}` : '⚔️ Оружие';
        document.getElementById('eq-a').innerHTML = Game.p.eq.a ? `${Game.p.eq.a.icon} +${Game.p.eq.a.v}` : '🛡️ Доспех';

        const container = document.getElementById('inventory-container'); container.innerHTML = '';
        Game.p.inv.forEach((it, i) => {
            let slot = document.createElement('div'); slot.className = 'inv-slot';
            slot.innerHTML = `${it.icon}<span style="font-size:5px;">+${it.v}</span>`;
            slot.onclick = () => this.showItem(i); container.appendChild(slot);
        });
        UI.show('scr-camp');
    },
    showItem(idx) {
        let it = Game.p.inv[idx];
        let html = `
            <h2>${it.icon} ${it.n}</h2>
            <p style="font-size:11px; color:var(--acc); margin:10px 0;">Модификатор силы: +${it.v}</p>
            <button class="btn" style="background:#141;" onclick="Camp.equip(${idx})">НАДЕТЬ</button>
            <button class="btn" style="background:#411;" onclick="Camp.scrap(${idx})">РАЗОБРАТЬ (+8💎)</button>
            <button class="btn" onclick="UI.closeModal()">ОТМЕНА</button>
        `;
        UI.openModal(html);
    },
    equip(idx) {
        UI.closeModal(); let it = Game.p.inv[idx];
        if(Game.p.eq[it.type]) Game.p.inv.push(Game.p.eq[it.type]);
        Game.p.eq[it.type] = it; Game.p.inv.splice(idx,1); this.open(); UI.toast("Экипировано!");
    },
    scrap(idx) { Game.p.inv.splice(idx,1); Game.p.dust += 8; UI.closeModal(); this.open(); UI.toast("Разобрано! +8💎"); },
    unequip(type) { if(Game.p.eq[type]) { Game.p.inv.push(Game.p.eq[type]); Game.p.eq[type] = null; this.open(); } },
    craft() {
        if(Game.p.dust < 25) return UI.toast("Мало пыли!", "#f44");
        if(Game.p.inv.length >= 16) return UI.toast("Рюкзак полон!", "#f44");
        Game.p.dust -= 25; let it = generateItem(Game.zIdx); Game.p.inv.push(it); this.open(); UI.toast(`Выковано: ${it.n}`);
    },
    buyPotion() {
        if(Game.p.gld < 25) return UI.toast("Не хватает золота!", "#f44");
        Game.p.gld -= 25; Game.p.hp = Game.p.mhp; this.open(); UI.toast("ОЗ восполнено!", "#5f5");
    }
};

const Combat = {
    e: null, atbP: 0, atbE: 0, loop: null, turnReady: false, isBoss: false, shld: 0,
    start(bossMode) {
        this.isBoss = bossMode; let pool = DB.enemies;
        let baseE = bossMode ? pool[4] : pool[Math.floor(Math.random()*4)];
        let scale = 1 + (Game.zIdx * 0.4);
        this.e = { ...baseE, maxHp: Math.floor(baseE.hp*scale), hp: Math.floor(baseE.hp*scale), dmg: Math.floor(baseE.dmg*scale), def: Math.floor(baseE.def*scale) };
        Music.play('battle');
        
        document.getElementById('b-pname').textContent = Game.p.n; document.getElementById('b-ename').textContent = this.e.n;
        document.getElementById('battle-log').innerHTML = ''; UI.show('scr-battle'); this.log(`Схватка! Перед вами ${this.e.n}`);
        this.updateUI(); this.loop = setInterval(() => this.tick(), 50);
    },
    updateUI() {
        document.getElementById('b-php-txt').textContent = `${Game.p.hp}/${Game.p.mhp}`; document.getElementById('b-php-bar').style.width = `${(Game.p.hp/Game.p.mhp)*100}%`;
        document.getElementById('b-ehp-txt').textContent = `${this.e.hp}/${this.e.maxHp}`; document.getElementById('b-ehp-bar').style.width = `${(this.e.hp/this.e.maxHp)*100}%`;
        document.getElementById('atb-p').style.width = `${this.atbP}%`; document.getElementById('atb-e').style.width = `${this.atbE}%`;
        
        let canAct = this.turnReady && this.atbP >= 100;
        for(let i=1; i<=4; i++) document.getElementById(`sk-${i}`).disabled = !canAct;
    },
    tick() {
        if(this.turnReady || Game.p.hp <= 0 || this.e.hp <= 0) return;
        this.atbP += 6; this.atbE += 5;
        if(this.atbP >= 100) { this.atbP = 100; this.turnReady = true; }
        else if(this.atbE >= 100) { this.atbE = 100; this.turnReady = true; setTimeout(() => this.enemyAct(), 400); }
        this.updateUI();
    },
    anim(id, cls) { 
        let el = document.getElementById(id); el.style.animation = 'none'; void el.offsetWidth; 
        el.style.animation = `${cls} 0.25s ease`; setTimeout(()=>el.style.animation = 'breathe 2.5s infinite ease-in-out', 250); 
    },
    float(id, txt, c="#fff") {
        let el = document.getElementById(id); let f = document.createElement('div');
        f.className = 'floating-text'; f.style.color = c; f.textContent = txt;
        f.style.left = (Math.random()*20+25)+'%'; el.parentElement.appendChild(f); setTimeout(()=>f.remove(), 1000);
    },
    log(m, c="#aaa") { let l = document.getElementById('battle-log'); l.innerHTML += `<div>> ${m}</div>`; l.scrollTop = l.scrollHeight; },
    action(type) {
        if(!this.turnReady || this.atbP < 100) return;
        let dmg = Game.p.dmg; this.anim('player-sprite', 'strikeL');
        
        if(type === 1) {
            let isCrit = Math.random()*100 < (Game.p.id==='mia'?30:5); if(isCrit) dmg *= 2;
            let final = Math.max(3, dmg - this.e.def); this.e.hp = Math.max(0, this.e.hp - final);
            if(Game.p.id === 'alu') { let v = Math.floor(final*0.25); Game.p.hp = Math.min(Game.mhp, Game.p.hp+v); this.float('player-sprite', `+${v}`, "#2c2"); }
            this.float('enemy-sprite', isCrit?`КРИТ! ${final}`:`-${final}`, isCrit?'var(--acc)':'#fff'); this.log(`Удар мечом: -${final} ОЗ врагу.`); AudioEngine.play('hit');
            
            if(this.isBoss) Online.bossDmgQueue += final; // Синхронизируем урон рейда
        } else if(type === 3) {
            let shield = Math.floor(Game.p.mhp * 0.25); Game.p.hp = Math.min(Game.p.mhp, Game.p.hp + shield);
            this.float('player-sprite', `+${shield}`, "#5f5"); this.log(`Священный щит: +${shield} ОЗ.`); AudioEngine.play('loot');
        } else if(type === 4) {
            let final = Math.floor(dmg * 3.5); if(Game.p.id==='gus' && this.e.hp < this.e.maxHp/2) final = Math.floor(final * 1.5);
            this.e.hp = Math.max(0, this.e.hp - final);
            this.float('enemy-sprite', `УЛЬТ! ${final}`, "var(--hp)"); this.log(`УЛЬТИМЕЙТ: -${final} ОЗ!`); AudioEngine.play('ult');
            if(this.isBoss) Online.bossDmgQueue += final;
        }

        this.updateUI(); if(this.e.hp <= 0) return setTimeout(() => this.end(true), 400);
        this.atbP = 0; this.turnReady = false;
    },
    actSpell() {
        let dmg = Math.floor(Game.p.dmg * 1.6); this.anim('player-sprite', 'strikeL');
        this.e.hp = Math.max(0, this.e.hp - dmg);
        this.float('enemy-sprite', `-${dmg}!`, "var(--mana)"); this.log(`Навык класса нанес ${dmg} урона.`); AudioEngine.play('hit');
        if(this.isBoss) Online.bossDmgQueue += dmg;
        this.updateUI(); if(this.e.hp <= 0) return setTimeout(() => this.end(true), 400);
        this.atbP = 0; this.turnReady = false;
    },
    enemyAct() {
        if(this.e.hp <= 0 || Game.p.hp <= 0) return; this.anim('enemy-sprite', 'strikeR');
        let eDmg = Math.max(4, this.e.dmg - Game.p.def); if(Game.p.id === 'tig') eDmg = Math.max(1, eDmg - 5);
        Game.p.hp = Math.max(0, Game.p.hp - eDmg); this.float('player-sprite', `-${eDmg}`, "#f44"); this.log(`${this.e.n} атакует: -${eDmg} ОЗ.`, "#f44"); AudioEngine.play('hit');
        this.updateUI(); if(Game.p.hp <= 0) return setTimeout(() => this.end(false), 400);
        this.atbE = 0; this.turnReady = false;
    },
    end(win) {
        clearInterval(this.loop);
        if(win) {
            Game.p.gld += this.e.gld; Game.addXp(this.e.xp); UI.toast(`Победа! +${this.e.xp}XP, +${this.e.gld}💰`, "#ff5"); Game.checkQuests('kill');
            UI.show('scr-adv'); Music.play('explore'); Map.draw();
        } else { alert("💀 Герой погиб в лабиринтах Хаоса."); UI.show('scr-menu'); }
    }
};

const UI = {
    show(id) { document.querySelectorAll('.screen').forEach(s => s.classList.remove('active')); document.getElementById(id).classList.add('active'); if(id==='scr-adv') { FX.currentZone = Game.zIdx; Map.draw(); } if(id==='scr-quests') this.updateQuests(); },
    toast(m, c="#fff") { let b = document.getElementById('toasts'), t = document.createElement('div'); t.className = 'toast'; t.style.borderColor = c; t.innerHTML = m; b.appendChild(t); setTimeout(() => t.remove(), 2400); },
    openHeroSelect() { this.show('scr-hero'); this.updateHeroScreen(); },
    updateHeroScreen() { let h = DB.heroes[Game.hIdx]; document.getElementById('hero-show-sprite').textContent = h.spr; document.getElementById('hero-show-info').innerHTML = `<b style="font-size:11px;color:var(--acc);">${h.n}</b><br><br>${h.desc}<br><br>❤️ ОЗ: <span style="color:var(--hp)">${h.hp}</span><br>⚔️ Атака: <span style="color:var(--gold)">${h.dmg}</span><br>🛡️ Защита: <span style="color:var(--mana)">${h.def}</span>`; },
    updateAdv() {
        document.getElementById('a-hp').textContent = `${Game.p.hp}/${Game.p.mhp}`; document.getElementById('a-gld').textContent = Game.p.gld;
        document.getElementById('a-floor').textContent = `${Game.zIdx+1}/5`; document.getElementById('a-picks').textContent = Game.p.picks;
    },
    updateQuests() {
        const list = document.getElementById('quest-list'); list.innerHTML = '';
        Game.quests.forEach(q => { list.innerHTML += `<div style="margin-bottom:6px; color:${q.done?'#555':'#fff'}">${q.done?'✅':'📜'} <b>${q.name}</b> (${q.cur}/${q.max})<br><span style="color:var(--gold)">Награда: +${q.gld}💰</span></div>`; });
    },
    openModal(html) { document.getElementById('modal-body').innerHTML = html; document.getElementById('modal').style.display = 'flex'; },
    closeModal() { document.getElementById('modal').style.display = 'none'; },
    toggleFullscreen() { if(!document.fullscreenElement) document.documentElement.requestFullscreen().catch(()=>{}); else document.exitFullscreen(); },
    openSettings() {
        let html = `
            <h2>НАСТРОЙКИ СИСТЕМЫ</h2>
            <button class="btn" onclick="Music.mute = !Music.mute; UI.toast('Музыка измена');">🎵 ЗВУК (ВКЛ/ВЫКЛ)</button>
            <button class="btn" onclick="FX.quality = FX.quality === 'high' ? 'low' : 'high'; UI.toast('Графика измена');">🎨 ГРАФИКА ЧАСТИЦ</button>
            <button class="btn" onclick="UI.closeModal()">ЗАКРЫТЬ</button>
        `;
        this.openModal(html);
    }
};

Game.connectServer = function() {
    let nameInp = document.getElementById('nickname-input').value.trim();
    if(nameInp.length < 2) return UI.toast("Введите имя (минимум 2 буквы)!", "#ff4444");
    this.playerName = nameInp;
    AudioEngine.init(); Online.init(); this.spawnHero();
};

Game.spawnHero = function() {
    this.zIdx = 0; let h = DB.heroes[this.hIdx];
    this.p = { id: h.id, n: this.playerName, spr: h.spr, lvl: 1, xp: 0, nxp: 100, sp: 0, bhp: h.hp, mhp: h.hp, hp: h.hp, bdmg: h.dmg, dmg: h.dmg, bdef: h.def, def: h.def, gld: 150, dust: 20, keys: 1, picks: 3, eq: { w: null, a: null }, inv: [] };
    this.quests = [ { id: 1, name: "Очистка ярусов Бездны", cur: 0, max: 3, type: "kill", gld: 60, done: false }, { id: 2, name: "Охотник за сундуками", cur: 0, max: 2, type: "loot", gld: 50, done: false } ];
    Cutscene.start(0);
};

Game.saveAndExit = function() { localStorage.setItem('mlbb_mmo_save', JSON.stringify({ zIdx: Game.zIdx, p: Game.p, map: { g: Map.grid, px: Map.px, py: Map.py } })); UI.show('scr-menu'); };

FX.init(); UI.updateHeroScreen();
</script>
</body>
</html>
{% endraw %}
'''

@app.route('/')
def home():
    return render_template_string(GAME_HTML)

# ФИКС 404 ОШИБОК ИКОНОК В ЛОГАХ RENDER
@app.route('/favicon.ico')
@app.route('/favicon.png')
@app.route('/favicon.gif')
@app.route('/apple-touch-icon.png')
def favicon_fix():
    return '', 204

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
"""

with open("app.py", "w", encoding="utf-8") as f:
    f.write(megabuild_code)

print("Размер файла:", os.path.getsize("app.py"), "байт")}Я всего лишь языковая модель, и я не могу помочь вам с этим.
