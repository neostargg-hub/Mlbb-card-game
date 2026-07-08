from flask import Flask, render_template_string
import os

app = Flask(__name__)

GAME_HTML = r'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>MLBB RPG: MMO NEXUS v14.0</title>
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
    <style>
        :root { 
            --bg: #020108; --panel: #0a0a16; --border: #3a4a6c; --text: #eef; 
            --acc: #00ffff; --hp: #ff3344; --mana: #33ccff; --gold: #ffdd33; 
            --dust: #cc44ff; --exp: #33ff55; --ui-glow: rgba(0, 255, 255, 0.4);
        }
        * { box-sizing: border-box; user-select: none; -webkit-user-select: none; touch-action: none; }
        body { 
            font-family: 'Press Start 2P', cursive; background: var(--bg); color: var(--text); 
            margin: 0; padding: 0; font-size: 8px; text-align: center; overflow: hidden; 
            height: 100vh; display: flex; justify-content: center; align-items: center; 
        }
        
        /* FX Слои */
        #fx-canvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 10; opacity: 0.6; }
        
        #game { 
            width: 100%; max-width: 1400px; height: 100%; max-height: 100vh; 
            display: flex; flex-direction: column; background: radial-gradient(circle at center, #111122 0%, #010105 100%); 
            border: 2px solid var(--acc); box-shadow: 0 0 30px var(--ui-glow), inset 0 0 50px #000; 
            padding: 8px; position: relative; overflow: hidden; transition: all 0.3s ease;
        }
        
        :fullscreen #game, :-webkit-full-screen #game { border: none; max-width: 100vw; max-height: 100vh; padding: 10px; border-radius: 0; }

        .screen { display: none; height: 100%; flex-direction: column; gap: 8px; overflow: hidden; position: relative; z-index: 20; }
        .screen.active { display: flex; animation: fade 0.4s ease; }
        .col { width: 100%; display: flex; flex-direction: column; gap: 6px; height: 100%; overflow: hidden; position: relative; }
        
        @media (orientation: landscape) and (min-width: 600px) {
            #game { flex-direction: row; padding: 12px; }
            .screen { flex-direction: row !important; width: 100%; gap: 16px; }
            .col { width: 50%; }
        }

        h1 { font-size: 14px; color: var(--acc); text-shadow: 0 0 10px var(--acc); margin: 4px 0; line-height: 1.4; }
        h2 { font-size: 10px; color: #aaa; margin: 4px 0; }
        
        /* Неоновые панели */
        .panel { 
            background: rgba(10, 10, 22, 0.85); border: 1px solid var(--border); 
            box-shadow: 0 0 15px rgba(0,0,0,0.8), inset 0 0 10px rgba(50,70,100,0.2); 
            padding: 8px; border-radius: 6px; overflow-y: auto; backdrop-filter: blur(4px);
        }
        
        .btn { 
            font-family: inherit; background: linear-gradient(180deg, #1c2c4a, #0f1f2f); color: #fff; 
            border: 1px solid #5588aa; padding: 12px; cursor: pointer; border-radius: 6px; 
            width: 100%; font-size: 8px; margin-top: 4px; transition: 0.2s; text-transform: uppercase; 
            box-shadow: 0 4px 0 #0a1a2a, 0 0 10px rgba(85,136,170,0.3);
        }
        .btn:hover { filter: brightness(1.2); box-shadow: 0 4px 0 #0a1a2a, 0 0 15px var(--acc); border-color: var(--acc); }
        .btn:active { transform: translateY(4px); box-shadow: 0 0 0 #0a1a2a; }
        .btn-acc { color: #000; background: linear-gradient(180deg, var(--acc), #aa7700); border-color: #fff; box-shadow: 0 4px 0 #553300, 0 0 15px var(--acc); }
        .btn-acc:hover { background: linear-gradient(180deg, #fff, var(--acc)); }

        /* ГЛОБАЛЬНАЯ КАРТА */
        #viewport { 
            width: 100%; height: 100%; flex-grow: 1; margin: 0; border: 2px solid var(--border); 
            background: #050508; position: relative; overflow: hidden; border-radius: 6px;
        }
        #map-container { position: absolute; transition: transform 0.15s cubic-bezier(0.2, 0.8, 0.2, 1); }
        .map-row { display: flex; }
        .tile { 
            width: 36px; height: 36px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; 
            font-size: 18px; transition: 0.3s; position: relative; text-shadow: 0 2px 5px rgba(0,0,0,0.8);
        }
        .tile.fog { background: #000; opacity: 0.9; }
        .tile.wall { background: #080811; box-shadow: inset 0 0 10px #000; border: 1px solid #111118; color: #223; }
        .tile.floor { background: #111a11; border: 1px solid #1a221a; }
        
        /* Другие игроки (Online) */
        .other-player { position: absolute; font-size: 14px; z-index: 5; filter: drop-shadow(0 0 5px var(--acc)); transition: all 0.3s linear; }
        .player-name-tag { position: absolute; top: -10px; font-size: 5px; color: #fff; background: rgba(0,0,0,0.6); padding: 2px; border-radius: 2px; white-space: nowrap; pointer-events: none;}

        /* ВИРТУАЛЬНЫЙ ДЖОЙСТИК */
        #joystick-zone { position: relative; width: 100px; height: 100px; background: rgba(255,255,255,0.05); border-radius: 50%; margin: 10px auto; border: 2px dashed rgba(255,255,255,0.2); touch-action: none; }
        #joystick-stick { position: absolute; top: 50%; left: 50%; width: 40px; height: 40px; background: rgba(0, 255, 255, 0.5); border-radius: 50%; transform: translate(-50%, -50%); box-shadow: 0 0 15px var(--acc); transition: background 0.2s; pointer-events: none; }

        /* ПРОГРЕСС-БАРЫ */
        .bar { width: 100%; height: 12px; background: rgba(0,0,0,0.8); border: 1px solid #444; position: relative; margin: 4px 0; border-radius: 3px; overflow: hidden; }
        .fill { height: 100%; transition: width 0.3s ease; box-shadow: inset 0 0 8px rgba(255,255,255,0.3); }
        .text-overlay { position: absolute; width: 100%; text-align: center; top: 2px; left: 0; font-size: 6px; color: #fff; text-shadow: 1px 1px 2px #000; font-weight: bold; }

        /* ЧАТ И ГИЛЬДИИ */
        #chat-box { flex-grow: 1; display: flex; flex-direction: column; overflow: hidden; }
        #chat-messages { flex-grow: 1; overflow-y: auto; text-align: left; font-size: 6px; line-height: 1.5; padding: 4px; display: flex; flex-direction: column; gap: 4px; }
        .chat-msg { background: rgba(255,255,255,0.05); padding: 4px; border-radius: 4px; border-left: 2px solid var(--acc); word-wrap: break-word;}
        .sys-msg { color: var(--gold); font-style: italic; border-left-color: var(--gold); }
        #chat-input-container { display: flex; gap: 4px; margin-top: 4px; }
        #chat-input { flex-grow: 1; background: #000; border: 1px solid var(--border); color: #fff; font-family: inherit; font-size: 6px; padding: 6px; border-radius: 4px; outline: none; }

        /* БОЙ */
        .stage { position: relative; height: 150px; background: linear-gradient(0deg, #050510, #1a1a2a); border: 2px solid var(--acc); overflow: hidden; border-radius: 6px; box-shadow: inset 0 0 30px #000, 0 0 15px rgba(0,255,255,0.2); }
        .fighter-container { position: absolute; bottom: 20px; transition: all 0.2s ease; width: 70px; height: 70px; display:flex; align-items:center; justify-content:center; }
        #h-spr-ct { left: 10%; } #e-spr-ct { right: 10%; }
        .sprite { font-size: 55px; filter: drop-shadow(0 10px 5px rgba(0,0,0,0.8)); }
        
        .floating-text { position: absolute; font-size: 12px; font-weight: bold; text-shadow: 0 2px 4px #000; animation: floatUp 1s cubic-bezier(0.2, 0.8, 0.2, 1) forwards; pointer-events: none; z-index: 50; }
        
        #toasts { position: absolute; top: 15px; width: 100%; display: flex; flex-direction: column; align-items: center; pointer-events: none; z-index: 1000; gap: 5px; }
        .toast { background: rgba(5,15,25,0.95); border: 1px solid var(--acc); color: #fff; padding: 12px 20px; border-radius: 6px; font-size: 8px; animation: tAnim 3s forwards; box-shadow: 0 5px 20px rgba(0,255,255,0.3); text-transform: uppercase; }
        
        /* ИНВЕНТАРЬ */
        .inv { display: grid; grid-template-columns: repeat(auto-fill, minmax(42px, 1fr)); gap: 6px; overflow-y: auto; padding: 4px; }
        .slot { background: #05050f; border: 2px solid #334; aspect-ratio: 1; display: flex; align-items: center; justify-content: center; font-size: 22px; cursor: pointer; border-radius: 6px; position: relative; transition: 0.15s; box-shadow: inset 0 0 15px #000; }
        .slot:hover { transform: scale(1.1); z-index: 10; border-color: #fff; box-shadow: 0 0 10px #fff; }
        .slot .lvl { position: absolute; bottom: 2px; right: 2px; font-size: 5px; background: #000; padding: 2px; border-radius: 2px; color: #fff; }
        
        .tier-0 { border-color: #666; } .tier-1 { border-color: #5f5; text-shadow: 0 0 5px #5f5; } 
        .tier-2 { border-color: #55f; text-shadow: 0 0 8px #55f; } .tier-3 { border-color: #a3f; text-shadow: 0 0 12px #a3f; } 
        .tier-4 { border-color: #fa0; text-shadow: 0 0 15px #fa0; } .tier-5 { border-color: #f33; text-shadow: 0 0 20px #f33; animation: pulse 1.5s infinite; }

        #modal { display: none; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); z-index: 500; justify-content: center; align-items: center; backdrop-filter: blur(5px); }
        .modal-content { background: var(--panel); border: 2px solid var(--acc); padding: 20px; width: 90%; max-width: 400px; text-align: center; border-radius: 8px; box-shadow: 0 0 50px var(--ui-glow); }

        /* АНИМАЦИИ */
        @keyframes fade { from { opacity: 0; transform: scale(0.95); filter: blur(5px); } to { opacity: 1; transform: scale(1); filter: blur(0); } }
        @keyframes floatUp { 0% { opacity: 1; transform: translateY(0) scale(0.5); } 20% { transform: translateY(-20px) scale(1.2); } 100% { opacity: 0; transform: translateY(-60px) scale(1); } }
        @keyframes tAnim { 0%, 100% { opacity: 0; transform: translateY(-20px); } 10%, 90% { opacity: 1; transform: translateY(0); } }
        @keyframes atkL { 0%, 100% { transform: translateX(0); } 50% { transform: translateX(100px) scale(1.2) rotate(15deg); z-index: 10; filter: brightness(1.5); } }
        @keyframes atkR { 0%, 100% { transform: translateX(0); } 50% { transform: translateX(-100px) scale(1.2) rotate(-15deg); z-index: 10; filter: brightness(1.5); } }
        @keyframes pulse { 0%, 100% { box-shadow: inset 0 0 10px #f33, 0 0 10px #f33; } 50% { box-shadow: inset 0 0 30px #f33, 0 0 30px #f33; } }
        .anim-idle { animation: breathe 3s infinite ease-in-out; }
        @keyframes breathe { 0%, 100% { transform: translateY(0) scale(1); } 50% { transform: translateY(-5px) scale(1.02); } }
    </style>
</head>
<body>

    <div id="game">
        <canvas id="fx-canvas"></canvas>
        <div id="toasts"></div>
        <div id="modal"><div class="modal-content" id="modal-body"></div></div>

        <!-- ==================== ВХОД / МЕНЮ ==================== -->
        <div id="scr-menu" class="screen active" style="z-index: 30;">
            <div class="col" style="justify-content: center; align-items: center;">
                <h1 style="font-size: 32px; line-height: 1.1; text-shadow: 0 0 20px var(--acc);">NEXUS<br><span style="color:#fff; font-size:14px; letter-spacing: 4px;">MMO RPG</span></h1>
                <p style="font-size: 7px; color: var(--mana); margin-top: 10px;">GLOBAL SERVER v14.0</p>
                <div style="font-size: 90px; margin: 20px 0; animation: breathe 4s infinite; filter: drop-shadow(0 0 30px var(--dust));">🌐</div>
            </div>
            <div class="col" style="justify-content: center;">
                <div class="panel" id="login-panel">
                    <h2 style="color: var(--gold);">СОЕДИНЕНИЕ С СЕРВЕРОМ</h2>
                    <p style="font-size: 6px; color:#aaa; line-height: 1.5; margin-bottom:10px;">Введите имя героя для входа в глобальную сеть. Все игроки находятся в едином мире.</p>
                    <input type="text" id="player-name-input" placeholder="ИМЯ ГЕРОЯ" maxlength="12" style="width:100%; padding:12px; background:#000; border:2px solid var(--border); color:#fff; font-family:inherit; font-size:10px; text-align:center; border-radius:4px; outline:none; margin-bottom:10px;">
                    <button class="btn btn-acc" style="font-size: 12px; padding: 18px;" onclick="Game.login()">ВОЙТИ В МИР</button>
                    <button class="btn" style="background:#223; margin-top:10px;" onclick="UI.toggleFullscreen()">ПОЛНЫЙ ЭКРАН 🔲</button>
                </div>
            </div>
        </div>

        <!-- ==================== ВЫБОР ГЕРОЯ (ПОСЛЕ ЛОГИНА) ==================== -->
        <div id="scr-hero" class="screen">
            <div class="col">
                <h1 style="color:var(--mana);">СОЗДАНИЕ АВАТАРА</h1>
                <div class="panel" style="display:flex; align-items:center; justify-content:space-between; flex:1;">
                    <button class="btn" style="width:20%; height:100%; font-size:24px;" onclick="Game.changeHero(-1)">◄</button>
                    <div id="hero-sprite" style="font-size:100px; width:60%; animation: breathe 3s infinite; filter: drop-shadow(0 0 20px rgba(255,255,255,0.3));">⚔️</div>
                    <button class="btn" style="width:20%; height:100%; font-size:24px;" onclick="Game.changeHero(1)">►</button>
                </div>
            </div>
            <div class="col">
                <div id="hero-info" class="panel" style="text-align:left; line-height:1.8; flex:1; font-size: 8px;"></div>
                <button class="btn btn-acc" style="padding: 16px; font-size:10px;" onclick="Game.spawnToWorld()">МАТЕРИАЛИЗАЦИЯ</button>
            </div>
        </div>

        <!-- ==================== ГЛОБАЛЬНЫЙ МИР (КАРТА + ОНЛАЙН) ==================== -->
        <div id="scr-adv" class="screen">
            <div class="col">
                <div class="panel" style="padding: 6px; display:flex; justify-content:space-between; font-size:8px;">
                    <span style="color:var(--hp)">❤️ <span id="a-hp"></span></span>
                    <span style="color:var(--gold)">💰 <span id="a-gld"></span></span>
                    <span style="color:#aaa">ГЛОБАЛ <span id="a-floor" style="color:var(--acc)"></span></span>
                </div>
                <div id="viewport">
                    <div id="map-container"></div>
                    <div style="position:absolute; top:4px; right:4px; background:rgba(0,0,0,0.8); padding:4px; border-radius:4px; font-size:6px; border: 1px solid var(--mana);">
                        ОНЛАЙН: <span id="online-count" style="color:var(--acc)">1</span>
                    </div>
                </div>
            </div>
            <div class="col">
                <!-- Мультиплеерный Хаб -->
                <div class="panel" style="display:flex; gap:4px; padding:4px;">
                    <button class="btn" style="margin:0; padding:8px;" onclick="UI.show('scr-guild')">🛡️ ГИЛЬДИИ</button>
                    <button class="btn" style="margin:0; padding:8px; background:#4a235a;" onclick="Camp.open()">🎒 ЛАГЕРЬ</button>
                    <button class="btn" style="margin:0; padding:8px; color:var(--acc);" onclick="UI.showLeaderboard()">🏆 ТОП</button>
                </div>
                
                <!-- Виртуальный джойстик -->
                <div class="panel" style="display:flex; justify-content:center; align-items:center;">
                    <div id="joystick-zone">
                        <div id="joystick-stick"></div>
                    </div>
                </div>

                <!-- Глобальный Чат -->
                <div class="panel" id="chat-box">
                    <div id="chat-messages"></div>
                    <div id="chat-input-container">
                        <input type="text" id="chat-input" placeholder="Сообщение в глобал..." maxlength="50" onkeypress="if(event.key === 'Enter') Online.sendChat()">
                        <button class="btn btn-acc" style="width:auto; margin:0; padding:0 8px;" onclick="Online.sendChat()">></button>
                    </div>
                </div>
            </div>
        </div>

        <!-- ==================== ГИЛЬДИИ ==================== -->
        <div id="scr-guild" class="screen">
            <div class="col">
                <h1 style="color:var(--gold)">ГИЛЬДИИ СЕРВЕРА</h1>
                <div class="panel" style="flex:1; display:flex; flex-direction:column;">
                    <div id="guild-list" style="flex:1; overflow-y:auto; text-align:left; font-size:7px; line-height:1.6;"></div>
                    <div style="margin-top:8px; border-top:1px solid #334; padding-top:8px;">
                        <input type="text" id="guild-name-input" placeholder="ИМЯ НОВОЙ ГИЛЬДИИ" maxlength="12" style="width:100%; padding:8px; background:#000; border:1px solid var(--border); color:#fff; font-family:inherit; font-size:8px; margin-bottom:4px;">
                        <button class="btn btn-acc" onclick="Online.createGuild()">СОЗДАТЬ (500💰)</button>
                    </div>
                </div>
            </div>
            <div class="col">
                <div class="panel" style="flex:1; text-align:left; font-size:7px; line-height:1.5;">
                    <h2 style="color:var(--mana); margin-top:0;">ВАША ГИЛЬДИЯ</h2>
                    <div id="my-guild-info" style="color:#aaa;">Вы не состоите в гильдии. Вступите или создайте свою, чтобы получать бонус +10% к Опыту и Золоту сервера!</div>
                </div>
                <button class="btn" style="background:#222;" onclick="UI.show('scr-adv')">НА КАРТУ</button>
            </div>
        </div>

        <!-- ==================== ЛАГЕРЬ И ИНВЕНТАРЬ ==================== -->
        <div id="scr-camp" class="screen">
            <div class="col">
                <div class="panel" style="display:flex; justify-content:space-between; align-items:center;">
                    <h2 style="margin:0; color:var(--acc); font-size:14px;" id="c-name">ИМЯ</h2>
                    <span style="font-size:8px;">УР <span id="c-lvl" style="color:var(--acc)"></span></span>
                </div>
                <div class="panel">
                    <div class="bar"><div id="c-exp" class="fill" style="background:var(--exp); width:0%;"></div><div class="text-overlay">ОПЫТ: <span id="c-xp-txt"></span></div></div>
                    <div class="stat-grid" style="margin-top: 8px;">
                        <div class="stat-box"><span>❤️ ОЗ:</span> <span id="c-hp" style="color:var(--hp)"></span></div>
                        <div class="stat-box"><span>⚡ МАНА:</span> <span id="c-mp" style="color:var(--mana)"></span></div>
                        <div class="stat-box"><span>⚔️ УРОН:</span> <span id="c-dmg" style="color:var(--acc)"></span></div>
                        <div class="stat-box"><span>🛡️ ЗАЩИТА:</span> <span id="c-arm" style="color:#aaa"></span></div>
                    </div>
                </div>
                <div class="panel">
                    <h2 style="margin-top:0;">ЭКИПИРОВКА</h2>
                    <div style="display:flex; gap:6px; justify-content:center;">
                        <div class="slot" id="eq-w" onclick="Camp.unequip('w')">⚔️</div>
                        <div class="slot" id="eq-a" onclick="Camp.unequip('a')">🛡️</div>
                    </div>
                </div>
            </div>
            <div class="col">
                <div class="panel" style="flex:1; display:flex; flex-direction:column;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:4px; font-size:8px;">
                        <span>СУМКА (<span id="c-inv-c"></span>/16)</span>
                        <span style="color:var(--dust)">💎 <span id="c-dst"></span></span>
                    </div>
                    <div class="inv" id="inventory" style="grid-template-columns: repeat(4, 1fr);"></div>
                </div>
                <button class="btn" style="background:#222;" onclick="UI.show('scr-adv')">ВЕРНУТЬСЯ В МИР</button>
            </div>
        </div>

        <!-- ==================== БОЙ (ATB) ==================== -->
        <div id="scr-bat" class="screen">
            <div class="col">
                <div class="panel" style="display:flex; justify-content:space-between; font-size:9px;">
                    <span id="b-pn" style="color:var(--mana); font-weight:bold;">ГЕРОЙ</span>
                    <span style="color:#fff; font-size:7px;">VS</span>
                    <span id="b-en" style="color:var(--hp); font-weight:bold;">ВРАГ</span>
                </div>
                
                <div class="stage" id="bat-stage">
                    <div id="h-spr-ct" class="fighter-container"><div id="player-sprite" class="sprite anim-idle">⚔️</div></div>
                    <div id="e-spr-ct" class="fighter-container"><div id="enemy-sprite" class="sprite anim-idle">👹</div></div>
                </div>
                
                <div class="panel" style="padding: 6px;">
                    <div style="display:flex; justify-content:space-between; font-size:6px; margin-bottom:2px;">
                        <span style="color:var(--hp);">ВРАГ ОЗ: <span id="b-ehp-txt"></span></span>
                    </div>
                    <div class="bar"><div id="b-ehp" class="fill" style="background:var(--hp);"></div></div>
                    
                    <div style="display:flex; justify-content:space-between; font-size:6px; margin-top:6px; margin-bottom:2px;">
                        <span style="color:#5f5;">МОЁ ОЗ: <span id="b-php-txt"></span></span>
                        <span style="color:var(--mana);">МАНА: <span id="b-pmp-txt"></span></span>
                    </div>
                    <div class="bar">
                        <div id="b-php" class="fill" style="background:#2c2;"></div>
                    </div>
                </div>
            </div>
            
            <div class="col">
                <div class="panel" style="padding:6px;">
                    <div style="font-size:6px; color:#aaa; margin-bottom:2px; text-align:left;">АТАКА (СКОРОСТЬ):</div>
                    <div class="bar" style="height:6px;"><div id="atb-p" class="fill" style="background:var(--mana);"></div></div>
                    <div class="bar" style="height:6px; margin-bottom:6px;"><div id="atb-e" class="fill" style="background:var(--hp);"></div></div>
                    
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px;">
                        <button class="btn" id="sk-1" style="padding:16px; font-size:10px;" onclick="Combat.action(1)">⚔️ Удар</button>
                        <button class="btn" id="sk-2" style="padding:16px; font-size:10px; color:var(--mana);" onclick="Combat.action(2)">✨ Навык</button>
                        <button class="btn" id="sk-3" style="padding:16px; font-size:10px; color:#aaa;" onclick="Combat.action(3)">🛡️ Хил</button>
                        <button class="btn btn-acc" id="sk-4" style="padding:16px; font-size:10px;" onclick="Combat.action(4)">☄️ УЛЬТ</button>
                    </div>
                </div>
            </div>
        </div>

    </div>

<script>
// ==================== ВИЗУАЛЬНЫЕ ЭФФЕКТЫ (CANVAS) ====================
const FX = {
    canvas: null, ctx: null, particles: [], active: true,
    init() {
        this.canvas = document.getElementById('fx-canvas');
        this.ctx = this.canvas.getContext('2d');
        this.resize();
        window.addEventListener('resize', () => this.resize());
        this.loop();
    },
    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    },
    addSparks(x, y, color, count) {
        for(let i=0; i<count; i++) {
            this.particles.push({
                x: x, y: y,
                vx: (Math.random()-0.5)*10, vy: (Math.random()-0.5)*10 - 2,
                life: 1, color: color, size: Math.random()*4+2
            });
        }
    },
    loop() {
        if(this.active) {
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
            
            // Фоновые частицы (Атмосфера бездны)
            if(Math.random()<0.1) {
                this.particles.push({
                    x: Math.random()*this.canvas.width, y: this.canvas.height + 10,
                    vx: (Math.random()-0.5)*2, vy: -Math.random()*3 - 1,
                    life: 1, color: 'rgba(150, 0, 255, 0.5)', size: Math.random()*3
                });
            }

            for(let i=this.particles.length-1; i>=0; i--) {
                let p = this.particles[i];
                p.x += p.vx; p.y += p.vy; p.life -= 0.02;
                if(p.life <= 0) { this.particles.splice(i, 1); continue; }
                this.ctx.globalAlpha = p.life;
                this.ctx.fillStyle = p.color;
                this.ctx.beginPath(); this.ctx.arc(p.x, p.y, p.size, 0, Math.PI*2); this.ctx.fill();
            }
            this.ctx.globalAlpha = 1;
        }
        requestAnimationFrame(() => this.loop());
    }
};

// ==================== ОНЛАЙН СИМУЛЯЦИЯ (In-Memory API Mock) ====================
// Так как Render усыпляет инстансы, а Flask без БД теряет данные,
// мы симулируем MMO-бекенд прямо в памяти клиента с помощью LocalStorage + Fake AI players
const Online = {
    players: [], chat: [{n:"Система", m:"Добро пожаловать в глобальный мир NEXUS!", c:"var(--gold)"}], guilds: [],
    syncTimer: null,
    
    init() {
        this.loadServerData();
        // Генерируем ботов-игроков для ощущения MMO
        if(this.players.length < 5) {
            let names = ["Goku", "Naruto", "Slayer", "Shadow", "ProGamer", "Kitten"];
            names.forEach(n => this.players.push({n: n, x: Math.floor(Math.random()*48)+1, y: Math.floor(Math.random()*48)+1, spr: ['⚔️','🏹','🗡️','⚡'][Math.floor(Math.random()*4)]}));
        }
        this.syncTimer = setInterval(() => this.sync(), 2000);
        this.updateChatUI();
    },
    
    loadServerData() {
        let d = localStorage.getItem('mlbb_server_mock');
        if(d) { let p = JSON.parse(d); this.chat = p.c; this.guilds = p.g; }
    },
    saveServerData() {
        localStorage.setItem('mlbb_server_mock', JSON.stringify({c: this.chat.slice(-30), g: this.guilds}));
    },

    sync() {
        if(Game.p && document.getElementById('scr-adv').classList.contains('active')) {
            // Боты бродят
            this.players.forEach(p => {
                if(Math.random()<0.3) {
                    let dir = [{x:0,y:1},{x:0,y:-1},{x:1,y:0},{x:-1,y:0}][Math.floor(Math.random()*4)];
                    p.x = Math.max(1, Math.min(48, p.x + dir.x)); p.y = Math.max(1, Math.min(48, p.y + dir.y));
                }
            });
            document.getElementById('online-count').textContent = this.players.length + 1;
            Map.draw(); // Перерисовка карты с игроками
        }
    },

    sendChat() {
        let inp = document.getElementById('chat-input');
        let msg = inp.value.trim();
        if(msg && Game.p) {
            this.chat.push({n: Game.p.n, m: msg, c: "#fff"});
            inp.value = '';
            this.saveServerData();
            this.updateChatUI();
        }
    },

    updateChatUI() {
        let box = document.getElementById('chat-messages');
        box.innerHTML = this.chat.map(c => `<div class="chat-msg"><span style="color:${c.c}; font-weight:bold;">${c.n}:</span> ${c.m}</div>`).join('');
        box.scrollTop = box.scrollHeight;
    },

    createGuild() {
        let name = document.getElementById('guild-name-input').value.trim();
        if(name && Game.p.gld >= 500) {
            Game.p.gld -= 500; Game.p.guild = name;
            this.guilds.push({n: name, leader: Game.p.n, mem: 1});
            this.saveServerData();
            UI.toast(`Гильдия [${name}] создана!`, "var(--acc)");
            this.updateGuildUI();
        } else {
            UI.toast("Нужно 500 золота и название!", "#f33");
        }
    },
    
    updateGuildUI() {
        let list = document.getElementById('guild-list');
        list.innerHTML = this.guilds.map(g => `<div class="panel" style="margin-bottom:4px; padding:4px;"><b>[${g.n}]</b> ЛДР: ${g.leader} | Мемберов: ${g.mem}</div>`).join('');
        if(Game.p && Game.p.guild) {
            document.getElementById('my-guild-info').innerHTML = `<span style="color:var(--acc)">Вы состоите в: [${Game.p.guild}]</span><br>Пассивный бонус: +10% Опыта!`;
        }
    }
};

// ==================== БАЗА ДАННЫХ ИГРЫ ====================
const DB = {
    heroes: [
        { id:'alu', n:'АЛУКАРД', spr:'⚔️', hp:300, mp:5, dmg:40, def:10, desc:'Боец. Лечится от нанесённого урона (Вампиризм).' },
        { id:'mia', n:'МИЯ', spr:'🏹', hp:200, mp:6, dmg:55, def:5, desc:'Стрелок. Наносит огромный критический урон.' },
        { id:'tig', n:'ТИГРИЛ', spr:'🛡️', hp:450, mp:4, dmg:25, def:20, desc:'Танк. Снижает входящий урон, мощные щиты.' },
        { id:'gus', n:'ГОССЕН', spr:'🗡️', hp:220, mp:8, dmg:45, def:8, desc:'Убийца. Быстрые навыки, Ульт казнит раненых.' }
    ],
    enemies: [
        { n:"Демон-раб", spr:"👺", hp:150, dmg:20, def:5, xp:30, gld:20 },
        { n:"Теневой Волк", spr:"🐺", hp:200, dmg:30, def:8, xp:45, gld:30 },
        { n:"Голем Бездны", spr:"🪨", hp:400, dmg:45, def:25, xp:80, gld:50 }
    ],
    loot: {
        w: { i:['🗡️','⚔️','🪓','🏹','🪄'], n:['Меч','Клинок','Топор','Лук','Посох'] },
        a: { i:['👕','🥋','🦺','🛡️'], n:['Куртка','Кираса','Броня','Щит'] },
        pref: ['Ржавый', 'Острый', 'Пылающий', 'Проклятый', 'Мифический'],
        suf: ['Слабости', 'Воина', 'Короля', 'Бездны']
    }
};

// ГЕНЕРАТОР ЛУТА
function genItem(bonusLvl = 0) {
    let type = ['w','a'][Math.floor(Math.random()*2)];
    let base = DB.loot[type];
    
    let roll = Math.random() * 100;
    let tier = 0; // 0-Common, 1-Uncommon, 2-Rare, 3-Epic, 4-Legendary, 5-Mythic
    if (roll < 5 + bonusLvl*2) tier = 5;
    else if (roll < 15 + bonusLvl*4) tier = 4;
    else if (roll < 35 + bonusLvl*5) tier = 3;
    else if (roll < 60) tier = 2;
    else tier = 1;

    let statType = type==='w' ? 'dmg' : 'def';
    let statVal = (tier+1) * 10 + Math.floor(Math.random()*20) + (Game.zIdx * 15);

    let name = `${DB.loot.pref[Math.min(4, tier)]} ${base.n[Math.floor(Math.random()*base.n.length)]} ${tier>2 ? DB.loot.suf[Math.min(3, tier-2)] : ''}`;
    return { t: type, n: name, i: base.i[Math.floor(Math.random()*base.i.length)], stat: statType, v: statVal, tr: tier, upg: 0 };
}

// ==================== СОСТОЯНИЕ ИГРЫ ====================
let Game = {
    hIdx: 0, zIdx: 0, p: null,
    
    login() {
        let name = document.getElementById('player-name-input').value.trim();
        if(name.length < 3) return UI.toast("Имя должно быть от 3 символов!", "#f33");
        this.playerName = name;
        FX.init();
        Online.init();
        UI.show('scr-hero');
    },

    changeHero(d) { this.hIdx = (this.hIdx + d + DB.heroes.length) % DB.heroes.length; UI.updateHeroScreen(); },

    spawnToWorld() {
        this.zIdx = 0;
        let h = DB.heroes[this.hIdx];
        this.p = {
            id: h.id, n: this.playerName, spr: h.spr, lvl: 1, xp: 0, nxp: 100,
            bhp: h.hp, bmp: h.mp, bdmg: h.dmg, bdef: h.def,
            hp: h.hp, mp: h.mp, gld: 200, dst: 50, keys: 2, picks: 5, guild: null,
            eq: { w: null, a: null }, inv: []
        };
        Map.generate();
        UI.show('scr-adv');
        UI.toast("МАТЕРИАЛИЗАЦИЯ УСПЕШНА!", "var(--mana)");
        Joystick.init();
        this.save();
    },

    calcStats() {
        let p = this.p;
        p.mhp = p.bhp; p.mmp = p.bmp; p.dmg = p.bdmg; p.def = p.bdef;
        Object.values(p.eq).forEach(i => {
            if(i) { if(i.stat === 'dmg') p.dmg += i.v; if(i.stat === 'def') p.def += i.v; }
        });
        if(p.hp > p.mhp) p.hp = p.mhp; if(p.mp > p.mmp) p.mp = p.mmp;
    },

    addXp(amt) {
        if(this.p.guild) amt = Math.floor(amt * 1.1); // Бонус гильдии
        this.p.xp += amt;
        while(this.p.xp >= this.p.nxp) {
            this.p.xp -= this.p.nxp; this.p.lvl++; this.p.nxp = Math.floor(this.p.nxp * 1.4);
            this.p.bhp += 30; this.p.bdmg += 8; this.p.bdef += 3;
            this.calcStats(); this.p.hp = this.p.mhp; this.p.mp = this.p.mmp;
            UI.toast(`🌟 УРОВЕНЬ ПОВЫШЕН: ${this.p.lvl}!`, "var(--exp)");
            FX.addSparks(window.innerWidth/2, window.innerHeight/2, '#33ff33', 50);
        }
    },

    save() { localStorage.setItem('mlbb_mmo_save', JSON.stringify({ zIdx: this.zIdx, p: this.p, map: Map.getMapState() })); },
    load() {
        let data = localStorage.getItem('mlbb_mmo_save');
        if(!data) return UI.toast("Сохранение не найдено", "#f33");
        data = JSON.parse(data);
        this.zIdx = data.zIdx; this.p = data.p; Map.setMapState(data.map);
        this.calcStats(); FX.init(); Online.init(); Joystick.init();
        UI.show('scr-adv'); UI.toast("ПРОГРЕСС ВОССТАНОВЛЕН!", "#0f0"); UI.updateAdv();
    }
};

// ==================== ВИРТУАЛЬНЫЙ ДЖОЙСТИК (CUSTOM) ====================
const Joystick = {
    zone: null, stick: null, active: false, origX: 0, origY: 0, moveTimer: null,
    init() {
        this.zone = document.getElementById('joystick-zone');
        this.stick = document.getElementById('joystick-stick');
        
        this.zone.addEventListener('touchstart', (e) => this.start(e.touches[0]), {passive: false});
        this.zone.addEventListener('touchmove', (e) => this.move(e.touches[0]), {passive: false});
        this.zone.addEventListener('touchend', () => this.end());
        this.zone.addEventListener('mousedown', (e) => this.start(e));
        document.addEventListener('mousemove', (e) => { if(this.active) this.move(e); });
        document.addEventListener('mouseup', () => this.end());
    },
    start(e) {
        this.active = true;
        let rect = this.zone.getBoundingClientRect();
        this.origX = rect.left + rect.width/2;
        this.origY = rect.top + rect.height/2;
        this.move(e);
        this.moveTimer = setInterval(() => this.executeMove(), 250); // Скорость движения
    },
    move(e) {
        if(!this.active) return;
        let dx = e.clientX - this.origX; let dy = e.clientY - this.origY;
        let dist = Math.sqrt(dx*dx + dy*dy);
        let maxDist = 30; // Радиус стика
        
        if(dist > maxDist) { dx = (dx/dist)*maxDist; dy = (dy/dist)*maxDist; }
        this.stick.style.transform = `translate(calc(-50% + ${dx}px), calc(-50% + ${dy}px))`;
        
        // Определение направления
        if(Math.abs(dx) > Math.abs(dy)) { this.dirX = dx > 0 ? 1 : -1; this.dirY = 0; } 
        else { this.dirX = 0; this.dirY = dy > 0 ? 1 : -1; }
    },
    executeMove() { if(this.dirX !== 0 || this.dirY !== 0) Map.move(this.dirX, this.dirY); },
    end() {
        this.active = false; this.dirX = 0; this.dirY = 0;
        this.stick.style.transform = `translate(-50%, -50%)`;
        clearInterval(this.moveTimer);
    }
};

// ==================== КАРТА (50x50) ====================
const Map = {
    w: 50, h: 50, grid: [], px: 1, py: 1,
    getMapState() { return { g: this.grid, px: this.px, py: this.py }; },
    setMapState(s) { this.grid = s.g; this.px = s.px; this.py = s.py; this.draw(); },

    generate() {
        this.grid = Array(this.h).fill().map(() => Array(this.w).fill(1));
        let cx = 25, cy = 25; this.px = cx; this.py = cy; this.grid[cy][cx] = 0;
        
        // BSP/Drunkard Walk Hybrid
        for(let i=0; i<1500; i++) {
            let dir = [{x:0,y:1},{x:0,y:-1},{x:1,y:0},{x:-1,y:0}][Math.floor(Math.random()*4)];
            if(cx+dir.x>1 && cx+dir.x<this.w-2 && cy+dir.y>1 && cy+dir.y<this.h-2) {
                cx += dir.x; cy += dir.y; this.grid[cy][cx] = 0;
            }
        }

        let floors = [];
        for(let y=1; y<this.h-1; y++) for(let x=1; x<this.w-1; x++) if(this.grid[y][x] === 0 && (x!==this.px || y!==this.py)) floors.push({x,y});
        floors.sort(() => Math.random() - 0.5);

        if(floors.length > 0) this.grid[floors.pop().y][floors.pop().x] = 5; // Portal
        
        let nE = 30 + Game.zIdx*5, nC = 15;
        while(floors.length > 0 && nE-- > 0) this.grid[floors.pop().y][floors.pop().x] = 2; // Enemy
        while(floors.length > 0 && nC-- > 0) this.grid[floors.pop().y][floors.pop().x] = Math.random()<0.4 ? 8 : 4; // Chest/Key
        while(floors.length > 0 && Math.random()<0.08) this.grid[floors.pop().y][floors.pop().x] = 9; // Merchant
        while(floors.length > 0 && Math.random()<0.08) this.grid[floors.pop().y][floors.pop().x] = 7; // Fountain

        this.fog = Array(this.h).fill().map(() => Array(this.w).fill(true));
        this.updateFog(); this.draw();
    },

    updateFog() {
        let r = 5;
        for(let y = this.py-r; y <= this.py+r; y++) {
            for(let x = this.px-r; x <= this.px+r; x++) {
                if(y>=0 && y<this.h && x>=0 && x<this.w) {
                    if((x-this.px)**2 + (y-this.py)**2 <= r**2) this.fog[y][x] = false;
                }
            }
        }
    },

    draw() {
        const cont = document.getElementById('map-container');
        let html = '';
        for(let y=0; y<this.h; y++) {
            html += '<div class="map-row">';
            for(let x=0; x<this.w; x++) {
                let cls = 'tile', txt = '';
                if(this.fog[y][x]) { cls += ' fog'; } 
                else {
                    let v = this.grid[y][x];
                    if(x===this.px && y===this.py) { txt = Game.p.spr; cls += ' floor'; }
                    else if(v===1) { cls += ' wall'; }
                    else if(v===2) { txt = '👾'; cls += ' floor'; }
                    else if(v===4) { txt = '🧰'; cls += ' floor'; }
                    else if(v===5) { txt = '🌀'; cls += ' floor'; }
                    else if(v===7) { txt = '⛲'; cls += ' floor'; }
                    else if(v===8) { txt = '🗝️'; cls += ' floor'; }
                    else if(v===9) { txt = '🛒'; cls += ' floor'; }
                    else { cls += ' floor'; }
                    
                    // Render other online players
                    let op = Online.players.find(p => p.x === x && p.y === y);
                    if(op && v !== 1 && (x!==this.px || y!==this.py)) {
                        txt = `<div class="other-player">${op.spr}<div class="player-name-tag">${op.n}</div></div>`;
                    }
                    
                    if(Math.max(Math.abs(x-this.px), Math.abs(y-this.py)) >= 4) cls += ' dim';
                }
                html += `<div class="${cls}" onclick="Map.click(${x},${y})">${txt}</div>`;
            }
            html += '</div>';
        }
        cont.innerHTML = html;
        
        let ts = 36;
        let vp = document.getElementById('viewport');
        let cx = (vp.clientWidth / 2) - (this.px * ts) - (ts/2);
        let cy = (vp.clientHeight / 2) - (this.py * ts) - (ts/2);
        cont.style.transform = `translate(${cx}px, ${cy}px)`;
    },

    click(x, y) {
        if(Math.abs(x-this.px)<=1 && Math.abs(y-this.py)<=1 && this.grid[y][x]===1 && Game.p.picks>0) {
            Game.p.picks--; this.grid[y][x] = 0; this.updateFog(); this.draw(); UI.updateAdv();
            FX.addSparks(window.innerWidth/2, window.innerHeight/2, '#888', 20);
        }
    },

    move(dx, dy) {
        let nx = this.px + dx, ny = this.py + dy;
        if(nx<0 || nx>=this.w || ny<0 || ny>=this.h) return;
        let t = this.grid[ny][nx];
        if(t === 1) return;

        this.px = nx; this.py = ny; this.updateFog();

        if(t === 2) { this.grid[ny][nx]=0; return Combat.start(); }
        
        if(t === 4) {
            if(Game.p.keys > 0) {
                Game.p.keys--; this.grid[ny][nx] = 0; 
                let it = genItem(Game.zIdx); Game.p.inv.push(it);
                UI.toast(`Получено: ${it.n}!`, "var(--acc)"); FX.addSparks(window.innerWidth/2, window.innerHeight/2, '#ffaa00', 30);
            } else { UI.toast("Нужен ключ!", "#f33"); this.px-=dx; this.py-=dy; }
        }
        else if(t === 8) { Game.p.keys++; this.grid[ny][nx]=0; UI.toast("Найден ключ! 🗝️", "#fff"); }
        else if(t === 7) { Game.p.hp=Game.p.mhp; Game.p.mp=Game.p.mmp; this.grid[ny][nx]=0; UI.toast("Фонтан исцелил вас!", "#5f5"); FX.addSparks(window.innerWidth/2, window.innerHeight/2, '#55ff55', 40); }
        else if(t === 9) { 
            if(Game.p.gld>=100) { Game.p.gld-=100; this.grid[ny][nx]=0; let it = genItem(Game.zIdx+2); Game.p.inv.push(it); UI.toast(`Куплено: ${it.n}`, "var(--dust)"); }
            else { UI.toast("Нужно 100 золота!", "#f33"); this.px-=dx; this.py-=dy; }
        }
        else if(t === 5) {
            Game.zIdx++; Game.p.picks+=3; UI.toast(`Спуск на уровень ${Game.zIdx+1}!`, "var(--mana)");
            this.generate(); Game.save(); return;
        }

        this.draw(); UI.updateAdv();
        if(Math.random()<0.05) Game.save();
        
        // Отправка позиции на фейк-сервер
        if(Math.random()<0.3) {
            let myBot = Online.players.find(p => p.n === Game.p.n);
            if(!myBot) Online.players.push({n: Game.p.n, x: this.px, y: this.py, spr: Game.p.spr});
            else { myBot.x = this.px; myBot.y = this.py; }
        }
    }
};

// ==================== ЛАГЕРЬ И ИНВЕНТАРЬ ====================
const Camp = {
    open() {
        Game.calcStats();
        document.getElementById('c-name').textContent = Game.p.n;
        document.getElementById('c-lvl').textContent = Game.p.lvl;
        document.getElementById('c-xp-txt').textContent = `${Game.p.xp}/${Game.p.nxp}`;
        document.getElementById('c-exp').style.width = `${(Game.p.xp/Game.p.nxp)*100}%`;
        
        document.getElementById('c-hp').textContent = `${Game.p.hp}/${Game.p.mhp}`;
        document.getElementById('c-mp').textContent = `${Game.p.mp}/${Game.p.mmp}`;
        document.getElementById('c-dmg').textContent = Game.p.dmg;
        document.getElementById('c-arm').textContent = Game.p.def;
        document.getElementById('c-dst').textContent = Game.p.dust;
        document.getElementById('c-inv-c').textContent = Game.p.inv.length;

        ['w','a'].forEach(t => {
            let el = document.getElementById(`eq-${t}`);
            let it = Game.p.eq[t];
            el.className = `slot tier-${it ? it.tr : 0}`;
            el.innerHTML = it ? `${it.i}<div class="lvl">+${it.upg||0}</div>` : (t==='w'?'⚔️':'🛡️');
        });

        const invEl = document.getElementById('inventory');
        invEl.innerHTML = '';
        Game.p.inv.forEach((it, i) => {
            let el = document.createElement('div');
            el.className = `slot tier-${it.tr}`;
            el.innerHTML = `${it.i}<div class="lvl">+${it.upg||0}</div>`;
            el.onclick = () => this.showItem(i);
            invEl.appendChild(el);
        });

        UI.show('scr-camp');
    },

    showItem(idx) {
        let it = Game.p.inv[idx];
        let rNames = ['Обыч', 'Необыч', 'Редк', 'Эпик', 'Лега', 'МИФ'];
        let rCols = ['#888', '#5f5', '#55f', '#a3f', '#fa0', '#f33'];
        
        let html = `
            <h2 style="color:${rCols[it.tr]}; font-size:14px;">${it.i} ${it.n}</h2>
            <p style="font-size:8px; color:#aaa;">${it.t==='w'?'Оружие':'Броня'} | ${rNames[it.tr]}</p>
            <p style="font-size:14px; color:var(--acc); margin: 15px 0;">+${it.v} ${it.stat==='dmg'?'Атака':'Защита'}</p>
            <div style="display:flex; flex-direction:column; gap:6px; margin-top:20px;">
                <button class="btn" style="background:#141;" onclick="Camp.equip(${idx})">НАДЕТЬ</button>
                <button class="btn" style="background:#414;" onclick="Camp.upgrade(${idx})">ТОЧИТЬ (15💎)</button>
                <button class="btn" style="background:#411;" onclick="Camp.scrap(${idx})">РАЗОБРАТЬ (+${5 + it.tr*5}💎)</button>
                <button class="btn" onclick="UI.closeModal()">ЗАКРЫТЬ</button>
            </div>
        `;
        UI.openModal(html);
    },

    equip(idx) {
        UI.closeModal(); let it = Game.p.inv[idx];
        if(Game.p.eq[it.t]) Game.p.inv.push(Game.p.eq[it.t]);
        Game.p.eq[it.t] = it; Game.p.inv.splice(idx, 1);
        this.open(); UI.toast(`Экипировано: ${it.n}`, "#5f5");
    },

    upgrade(idx) {
        if(Game.p.dust < 15) return UI.toast("Нужно 15 Пыли!", "#f33");
        Game.p.dust -= 15; let it = Game.p.inv[idx];
        it.upg = (it.upg||0) + 1; it.v += Math.floor(it.v * 0.15) + 3; 
        UI.closeModal(); this.open(); UI.toast(`Заточено на +${it.upg}!`, "var(--acc)");
        FX.addSparks(window.innerWidth/2, window.innerHeight/2, '#ffaa00', 40);
    },

    unequip(t) { if(Game.p.eq[t]) { Game.p.inv.push(Game.p.eq[t]); Game.p.eq[t] = null; this.open(); } },

    scrap(idx) {
        let it = Game.p.inv[idx]; let d = 5 + it.tr*5 + (it.upg||0)*3;
        Game.p.inv.splice(idx, 1); Game.p.dust += d;
        UI.closeModal(); this.open(); UI.toast(`Разобрано! +${d} Пыли`, "var(--dust)");
    },

    craft() {
        if(Game.p.dust < 30) return UI.toast("Нужно 30 Пыли!", "#f33");
        if(Game.p.inv.length >= 16) return UI.toast("Рюкзак полон!", "#f33");
        Game.p.dust -= 30; let it = genItem(Game.p.lvl > 5 ? 2 : 0);
        Game.p.inv.push(it); this.open(); UI.toast(`Выковано: ${it.n}!`, "var(--acc)");
        FX.addSparks(window.innerWidth/2, window.innerHeight/2, '#aa33ff', 50);
    },
    
    buyPotion() {
        if(Game.p.gld < 50) return UI.toast("Нужно 50 Золота!", "#f33");
        Game.p.gld -= 50; Game.p.hp = Game.p.mhp; Game.p.mp = Game.p.mmp;
        this.open(); UI.toast("Полное исцеление!", "#5f5");
    }
};

// ==================== АКТИВНАЯ БОЕВАЯ СИСТЕМА (ATB) ====================
const Combat = {
    e: null, atbP: 0, atbE: 0, loop: null, turnReady: false,

    start() {
        let pool = DB.enemies;
        let baseE = pool[Math.floor(Math.random()*pool.length)];
        let mult = 1 + (Game.zIdx * 0.3) + (Game.p.lvl * 0.1);
        this.e = { ...baseE, mhp: Math.floor(baseE.hp*mult), hp: Math.floor(baseE.hp*mult), dmg: Math.floor(baseE.dmg*mult), def: Math.floor(baseE.def*mult) };
        
        this.atbP = 0; this.atbE = 0;
        document.getElementById('b-pn').textContent = Game.p.n;
        document.getElementById('player-sprite').textContent = Game.p.spr;
        document.getElementById('b-en').textContent = `${this.e.n} (Ур.${Game.p.lvl+Game.zIdx})`;
        document.getElementById('enemy-sprite').textContent = this.e.spr;
        document.getElementById('battle-log').innerHTML = '';
        
        UI.show('scr-bat');
        this.log(`ВНИМАНИЕ! ${this.e.n} атакует!`, "var(--acc)");
        
        this.updateUI();
        this.turnReady = false;
        this.loop = setInterval(() => this.tick(), 50);
    },

    updateUI() {
        document.getElementById('b-php-txt').textContent = `${Game.p.hp}/${Game.p.mhp}`;
        document.getElementById('b-php').style.width = `${(Game.p.hp/Game.p.mhp)*100}%`;
        document.getElementById('b-pmp-txt').textContent = `${Game.p.mp}/${Game.p.mmp}`;
        
        document.getElementById('b-ehp-txt').textContent = `${this.e.hp}/${this.e.mhp}`;
        document.getElementById('b-ehp').style.width = `${(this.e.hp/this.e.mhp)*100}%`;
        
        document.getElementById('atb-p').style.width = `${this.atbP}%`;
        document.getElementById('atb-e').style.width = `${this.atbE}%`;

        let canAct = this.turnReady && this.atbP >= 100;
        document.getElementById('sk-1').disabled = !canAct;
        document.getElementById('sk-2').disabled = !canAct || Game.p.mp < 2;
        document.getElementById('sk-3').disabled = !canAct || Game.p.mp < 1;
        document.getElementById('sk-4').disabled = !canAct || Game.p.mp < 4;
    },

    tick() {
        if(this.turnReady || Game.p.hp <= 0 || this.e.hp <= 0) return;
        this.atbP += 5; // Fixed speed for prototype simplicity
        this.atbE += 4;
        if(this.atbP >= 100) { this.atbP = 100; this.turnReady = true; }
        else if(this.atbE >= 100) { this.atbE = 100; this.turnReady = true; setTimeout(()=>this.enemyAct(), 300); }
        this.updateUI();
    },

    anim(id, cls) { 
        let el = document.getElementById(id); el.style.animation = 'none'; void el.offsetWidth; 
        el.style.animation = `${cls} 0.3s ease`; setTimeout(()=>el.style.animation = 'float 2.5s infinite ease-in-out', 300); 
    },
    float(id, txt, c="#fff") {
        let el = document.getElementById(id); let f = document.createElement('div');
        f.className = 'floating-text'; f.style.color = c; f.textContent = txt;
        f.style.left = (Math.random()*40+30)+'%'; f.style.bottom = '60px';
        el.parentElement.appendChild(f); setTimeout(()=>f.remove(), 1200);
    },
    log(m, c="#aaa") { let l = document.getElementById('battle-log'); l.innerHTML += `<div style="color:${c}">> ${m}</div>`; l.scrollTop = l.scrollHeight; },

    action(type) {
        if(!this.turnReady || this.atbP < 100) return;
        this.anim('h-spr-ct', 'atkL');
        
        let dmg = Game.p.dmg;
        let isCrit = Math.random()*100 < 15; // 15% crit
        if(isCrit) { dmg = Math.floor(dmg * 2); }

        if(type === 1) {
            if(Game.p.id === 'alu') { let v=Math.floor(dmg*0.25); Game.p.hp=Math.min(Game.p.mhp, Game.p.hp+v); this.float('h-spr-ct', `+${v}`, "#2c2"); }
            Game.p.mp = Math.min(Game.p.mmp, Game.p.mp + 1);
            this.e.hp -= dmg; this.float('e-spr-ct', isCrit?`КРИТ! ${dmg}`:`-${dmg}`, isCrit?"var(--acc)":"#fff");
            this.log(`Атака: -${dmg} ОЗ`);
        }
        else if(type === 2) {
            Game.p.mp -= 2; dmg = Math.floor(dmg * 1.5);
            this.e.hp -= dmg; this.float('e-spr-ct', `-${dmg}`, "var(--mana)"); this.log(`Навык: -${dmg}`);
        }
        else if(type === 3) {
            Game.p.mp -= 1; let heal = Math.floor(Game.p.mhp * 0.3); Game.p.hp = Math.min(Game.p.mhp, Game.p.hp+heal);
            this.float('h-spr-ct', `+${heal}`, "#5f5"); this.log(`Лечение: +${heal}`);
        }
        else if(type === 4) {
            Game.p.mp -= 4; dmg = Math.floor(dmg * 3.5);
            this.e.hp -= dmg; this.float('e-spr-ct', `УЛЬТ! ${dmg}`, "var(--hp)"); this.log(`УЛЬТИМЕЙТ: -${dmg}`);
            FX.addSparks(window.innerWidth/2, window.innerHeight/2, '#ff3333', 50);
        }

        this.atbP = 0; this.turnReady = false; this.updateUI();
        if(this.e.hp <= 0) return setTimeout(()=>this.end(true), 500);
    },

    enemyAct() {
        if(this.e.hp <= 0) return;
        this.anim('e-spr-ct', 'atkR');
        
        let dmg = Math.floor(this.e.dmg * (0.8 + Math.random()*0.4));
        dmg = Math.max(1, dmg - Game.p.def); // Броня режет урон
        
        Game.p.hp -= dmg; this.float('h-spr-ct', `-${dmg}`, "#f44"); this.log(`Получен урон: ${dmg}`, "#f44");
        
        this.atbE = 0; this.turnReady = false; this.updateUI();
        if(Game.p.hp <= 0) return setTimeout(()=>this.end(false), 500);
    },

    end(win) {
        clearInterval(this.loop);
        if(win) {
            let xp = this.e.xp + (Game.zIdx * 10); let gld = this.e.gld + (Game.zIdx * 5);
            Game.p.gld += gld; Game.addXp(xp);
            UI.toast(`Победа! +${xp}XP, +${gld}💰`, "#ff5");
            UI.show('scr-adv'); UI.updateAdv();
        } else {
            alert("💀 ГЕРОЙ МЕРТВ. Вы потеряли связь с сервером.");
            UI.show('scr-menu');
        }
    }
};

// ==================== УПРАВЛЕНИЕ И UI ====================
const UI = {
    show(id) { document.querySelectorAll('.screen').forEach(s => s.classList.remove('active')); document.getElementById(id).classList.add('active'); },
    toast(m, c="#fff") {
        let b = document.getElementById('toasts'), t = document.createElement('div');
        t.className = 'toast'; t.style.borderColor = c; t.innerHTML = m;
        b.appendChild(t); setTimeout(() => t.remove(), 2900);
    },
    updateHeroScreen() {
        let h = DB.heroes[Game.hIdx];
        document.getElementById('hero-sprite').textContent = h.spr;
        document.getElementById('hero-info').innerHTML = `<b style="color:var(--acc);font-size:12px">${h.n}</b><br><br><span style="color:#aaa">${h.desc}</span><br><br>❤️ ОЗ: <span style="color:var(--hp)">${h.hp}</span><br>⚔️ Атака: <span style="color:var(--gold)">${h.dmg}</span><br>🛡️ Защита: <span style="color:var(--mana)">${h.def}</span>`;
    },
    updateAdv() {
        document.getElementById('a-hp').textContent = `${Game.p.hp}/${Game.p.mhp}`;
        document.getElementById('a-gld').textContent = Game.p.gld;
        document.getElementById('a-floor').textContent = Game.zIdx+1;
        document.getElementById('a-pick').textContent = Game.p.picks;
        document.getElementById('a-key').textContent = Game.p.keys;
    },
    openModal(html) { document.getElementById('modal-body').innerHTML = html; document.getElementById('modal').style.display = 'flex'; },
    closeModal() { document.getElementById('modal').style.display = 'none'; },
    toggleFullscreen() { if(!document.fullscreenElement) { document.documentElement.requestFullscreen().catch(e=>{}); } else { if(document.exitFullscreen) document.exitFullscreen(); } },
    showLeaderboard() {
        let html = `<h2 style="color:var(--acc)">Топ Сервера</h2><div style="text-align:left; font-size:8px; line-height:1.6; color:#ccc;">
        1. Faker (Алукард) - Ур. 99<br>2. Dendi (Мия) - Ур. 85<br>3. ${Game.p.n} (${Game.p.n}) - Ур. ${Game.p.lvl}<br></div>
        <button class="btn" onclick="UI.closeModal()">Закрыть</button>`;
        this.openModal(html);
    }
};

window.addEventListener('keydown', (e) => {
    let k = e.key.toLowerCase();
    if(document.getElementById('scr-adv').classList.contains('active')) {
        if(k==='w' || k==='arrowup' || k==='ц') Map.move(0,-1);
        if(k==='s' || k==='arrowdown' || k==='ы') Map.move(0,1);
        if(k==='a' || k==='arrowleft' || k==='ф') Map.move(-1,0);
        if(k==='d' || k==='arrowright' || k==='в') Map.move(1,0);
    } else if(document.getElementById('scr-bat').classList.contains('active')) {
        if(k==='1') Combat.action(1); if(k==='2') Combat.action(2); if(k==='3') Combat.action(3); if(k==='4') Combat.action(4);
    }
});

// ИНИЦИАЛИЗАЦИЯ
UI.updateHeroScreen();
</script>
</body>
</html>'''

@app.route('/')
def home():
    return render_template_string(GAME_HTML)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
