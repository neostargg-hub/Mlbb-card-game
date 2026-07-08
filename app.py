from flask import Flask, render_template_string

app = Flask(__name__)

GAME_HTML = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>MLBB RPG: Эпоха Возрождения ULTIMATE</title>
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
    <style>
        :root { 
            --bg: #030308; --panel: #090915; --border: #445; --txt: #e0e0f0; 
            --acc: #ffcc00; --hp: #ff4444; --mana: #55aaff; --dust: #aa55ff; --gold: #ffff55; 
            --exp: #22cc22;
        }
        * { box-sizing: border-box; }
        body { 
            font-family: 'Press Start 2P', cursive; background: var(--bg); color: var(--txt); 
            margin: 0; padding: 0; font-size: 8px; text-align: center; overflow: hidden; 
            user-select: none; -webkit-user-select: none; height: 100vh; display: flex; 
            justify-content: center; align-items: center; 
        }
        
        #game { 
            width: 100%; max-width: 1200px; height: 100%; max-height: 100vh; 
            display: flex; flex-direction: column; background: radial-gradient(circle at center, #111122 0%, #030308 100%); 
            border: 4px solid var(--border); box-shadow: 0 0 50px rgba(0,0,0,0.9); 
            padding: 8px; position: relative; overflow: hidden; transition: all 0.3s ease;
        }
        
        /* Полноэкранный фикс */
        :fullscreen #game { border: none; max-width: 100vw; max-height: 100vh; padding: 10px; border-radius: 0; }
        :-webkit-full-screen #game { border: none; max-width: 100vw; max-height: 100vh; padding: 10px; border-radius: 0; }

        .screen { display: none; height: 100%; flex-direction: column; justify-content: space-between; gap: 8px; }
        .screen.active { display: flex; animation: fade 0.4s ease; }
        .col { width: 100%; display: flex; flex-direction: column; justify-content: space-between; gap: 6px; }
        
        @media (orientation: landscape) and (min-width: 600px) {
            #game { flex-direction: row; padding: 12px; }
            .screen { flex-direction: row !important; width: 100%; gap: 16px; }
            .col { width: 50%; height: 100%; }
        }

        h1, h2, h3 { color: var(--acc); text-shadow: 2px 2px #000; margin: 4px 0; line-height: 1.4; }
        h1 { font-size: 14px; } h2 { font-size: 10px; }
        .panel { background: var(--panel); border: 2px solid var(--border); box-shadow: 4px 4px 0px #000; padding: 8px; position: relative; border-radius: 4px; }
        
        .btn { 
            font-family: inherit; background: #1c1c3a; color: #fff; border: 3px outset #4a4a88; 
            padding: 12px; cursor: pointer; border-radius: 4px; width: 100%; font-size: 8px; 
            margin-top: 4px; transition: 0.1s; text-transform: uppercase; text-shadow: 1px 1px #000;
        }
        .btn:hover { background: #2a2a50; border-color: #66b; }
        .btn:active { border-style: inset; background: #111124; }
        .btn:disabled { opacity: 0.4; cursor: not-allowed; filter: grayscale(1); }
        .btn-acc { color: var(--acc); border-color: #886600; }
        
        /* КАРТА */
        #viewport { 
            width: 100%; max-width: 380px; margin: 4px auto; border: 4px solid #446; 
            background: #000; padding: 2px; box-shadow: inset 0 0 30px #000; flex-grow: 1; 
            display: flex; align-items: center; justify-content: center;
        }
        #map-grid { display: grid; grid-template-columns: repeat(9, 1fr); gap: 2px; width: 100%; aspect-ratio: 1; }
        .tile { 
            aspect-ratio: 1; display: flex; align-items: center; justify-content: center; 
            font-size: 18px; background: #121e12; border-radius: 2px; transition: 0.2s; cursor: pointer; 
        }
        .dim-1 { opacity: 0.8; filter: brightness(0.8); } 
        .dim-2 { opacity: 0.5; filter: brightness(0.5); } 
        .dim-3 { opacity: 0.1; filter: brightness(0.1); }
        .wall { background: #111118; color: #334; box-shadow: inset 0 0 5px #000; }

        .dpad { display: grid; grid-template-columns: repeat(3, 1fr); width: 180px; margin: 4px auto; gap: 6px; }
        .dbtn { font-family: inherit; font-size: 20px; background: #252542; color: #fff; border: 3px outset #558; padding: 14px 0; border-radius: 8px; }
        .dbtn:active { border-style: inset; background: #15152b; color: var(--acc); }

        .bar { width: 100%; height: 14px; background: #111; border: 2px solid #fff; position: relative; margin: 4px 0; border-radius: 2px; }
        .fill { height: 100%; transition: width 0.3s ease; }
        .text-overlay { position: absolute; width: 100%; text-align: center; top: 2px; left: 0; font-size: 7px; color: #fff; text-shadow: 1px 1px #000; }

        /* БОЙ */
        .stage { position: relative; height: 120px; background: #020208; border: 2px solid #333; overflow: hidden; border-radius: 4px; }
        .sprite { font-size: 48px; position: absolute; bottom: 10px; width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; filter: drop-shadow(0 0 5px rgba(0,0,0,0.8)); }
        #h-spr { left: 15%; transform: scaleX(-1); } #e-spr { right: 15%; }
        
        .floating-text { position: absolute; font-size: 10px; font-weight: bold; text-shadow: 1px 1px 0 #000; animation: floatUp 1.2s forwards; pointer-events: none; z-index: 50; }
        
        #toasts { position: absolute; top: 10px; width: 100%; display: flex; flex-direction: column; align-items: center; pointer-events: none; z-index: 100; gap: 4px; }
        .toast { background: rgba(10,10,25,0.95); border: 2px solid var(--acc); color: #fff; padding: 10px 15px; border-radius: 4px; font-size: 8px; animation: tAnim 2.5s forwards; box-shadow: 0 4px 10px rgba(0,0,0,0.8); }
        
        /* ИНВЕНТАРЬ И СТАТЫ */
        .inv { display: grid; grid-template-columns: repeat(5, 1fr); gap: 4px; margin: 6px 0; overflow-y: auto; max-height: 180px; padding: 2px; }
        .slot { background: #05050f; border: 2px solid #333; height: 45px; display: flex; align-items: center; justify-content: center; font-size: 22px; cursor: pointer; border-radius: 4px; position: relative; transition: 0.1s; }
        .slot:hover { transform: scale(1.05); z-index: 10; }
        .slot span { position: absolute; bottom: 2px; right: 2px; font-size: 6px; background: rgba(0,0,0,0.8); padding: 2px; border-radius: 2px; color: #fff; }
        
        .tier-0 { border-color: #888; } 
        .tier-1 { border-color: #5f5; box-shadow: inset 0 0 5px #5f5; } 
        .tier-2 { border-color: #55f; box-shadow: inset 0 0 8px #55f; } 
        .tier-3 { border-color: #a3f; box-shadow: inset 0 0 12px #a3f; } 
        .tier-4 { border-color: #fa0; box-shadow: inset 0 0 15px #fa0; }
        .tier-5 { border-color: #f55; box-shadow: inset 0 0 20px #f55; animation: pulse 2s infinite; }

        .stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 4px; font-size: 6px; text-align: left; }
        .stat-box { background: rgba(0,0,0,0.5); padding: 4px; border: 1px solid #334; border-radius: 2px; }

        #modal { display: none; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); z-index: 200; justify-content: center; align-items: center; }
        .modal-content { background: var(--panel); border: 4px solid var(--acc); padding: 20px; width: 90%; max-width: 400px; text-align: center; border-radius: 8px; box-shadow: 0 0 30px #000; }

        /* АНИМАЦИИ */
        @keyframes fade { from { opacity: 0; transform: scale(0.98); } to { opacity: 1; transform: scale(1); } }
        @keyframes floatUp { 0% { opacity: 1; transform: translateY(0) scale(1); } 100% { opacity: 0; transform: translateY(-40px) scale(1.5); } }
        @keyframes tAnim { 0%, 100% { opacity: 0; transform: translateY(-20px); } 10%, 90% { opacity: 1; transform: translateY(0); } }
        @keyframes atkL { 0%, 100% { left: 15%; } 50% { left: 45%; transform: scaleX(-1) scale(1.4) rotate(20deg); z-index: 10; } }
        @keyframes atkR { 0%, 100% { right: 15%; } 50% { right: 45%; transform: scale(1.4) rotate(-20deg); z-index: 10; } }
        @keyframes pulse { 0%, 100% { filter: brightness(1); } 50% { filter: brightness(1.5); } }
        .anim-idle { animation: float 2.5s infinite ease-in-out; }
        @keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-6px); } }
        
        /* Спецэффекты статусов */
        .status-badge { position: absolute; top: 2px; left: 2px; font-size: 6px; padding: 2px; border-radius: 2px; background: #000; border: 1px solid #fff; z-index: 5; }
    </style>
</head>
<body>

    <div id="game">
        <div id="toasts"></div>
        
        <!-- МОДАЛЬНОЕ ОКНО LEVEL UP -->
        <div id="modal">
            <div class="modal-content">
                <h1 style="color:var(--exp); font-size: 16px; margin-bottom: 15px;">НОВЫЙ УРОВЕНЬ!</h1>
                <p style="font-size: 8px; color: #aaa; margin-bottom: 20px;">Очки характеристик (+1). Выберите путь развития:</p>
                <div style="display:flex; flex-direction:column; gap:8px;">
                    <button class="btn" onclick="Game.lvlUpStat('str')">⚔️ СИЛА (+Урон, +ОЗ)</button>
                    <button class="btn" onclick="Game.lvlUpStat('agi')">💨 ЛОВКОСТЬ (+Крит, +Уклонение)</button>
                    <button class="btn" onclick="Game.lvlUpStat('int')">🧠 ИНТЕЛЛЕКТ (+Мана, +Сила навыков)</button>
                    <button class="btn" onclick="Game.lvlUpStat('vit')">❤️ ЖИВУЧЕСТЬ (++Макс ОЗ, +Щиты)</button>
                </div>
            </div>
        </div>

        <!-- ОКНО ДЕТАЛЕЙ ПРЕДМЕТА -->
        <div id="item-modal" style="display: none; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); z-index: 250; justify-content: center; align-items: center;">
            <div class="modal-content" id="item-details">
                <!-- Заполняется из JS -->
            </div>
        </div>

        <!-- ГЛАВНОЕ МЕНЮ -->
        <div id="scr-menu" class="screen active">
            <div class="col" style="justify-content: center;">
                <h1 style="font-size: 24px;">MLBB RPG</h1>
                <h2>ЭПОХА ВОЗРОЖДЕНИЯ</h2>
                <p style="font-size: 6px; color: #8a8ab0; margin-top: 10px;">MEGA BUILD v12.0</p>
                <div style="font-size: 60px; margin: 30px 0; animation: float 3s infinite;">🌌</div>
            </div>
            <div class="col" style="justify-content: center; gap: 12px;">
                <button class="btn btn-acc" style="font-size: 12px; padding: 15px;" onclick="Game.start()">НОВАЯ ИГРА</button>
                <button class="btn" onclick="Game.load()">ЗАГРУЗИТЬ ИГРУ</button>
                <button class="btn" onclick="UI.show('scr-set')">ВЫБОР ГЕРОЯ</button>
                <button class="btn" style="background:#223;" onclick="UI.toggleFullscreen()">ПОЛНЫЙ ЭКРАН 🔲</button>
            </div>
        </div>

        <!-- ВЫБОР ГЕРОЯ И НАСТРОЙКИ -->
        <div id="scr-set" class="screen">
            <div class="col">
                <h1>НАСТРОЙКИ</h1>
                <div class="panel">
                    <div style="margin-bottom:10px;">КЛАСС: <button class="btn btn-acc" onclick="Game.nextHero()" id="cfg-hero">АЛУКАРД</button></div>
                    <div style="margin-bottom:10px;">ЗВУК: <button class="btn" onclick="Audio.tog('sfx')" id="cfg-sfx">ВКЛ</button></div>
                    <div style="margin-bottom:10px;">МУЗЫКА: <button class="btn" onclick="Audio.tog('mus')" id="cfg-mus">ВКЛ</button></div>
                </div>
            </div>
            <div class="col">
                <div class="panel" style="flex-grow:1; display:flex; flex-direction:column; justify-content:center;">
                    <div id="hero-sprite-big" style="font-size: 40px; margin-bottom: 10px; animation: float 2s infinite;">⚔️</div>
                    <div id="hero-desc" style="font-size:7px; color:#bbb; line-height:1.6; text-align:left; background: rgba(0,0,0,0.5); padding: 10px; border-radius: 4px;"></div>
                </div>
                <button class="btn" onclick="UI.show(Game.isPlaying ? 'scr-adv' : 'scr-menu')">НАЗАД</button>
            </div>
        </div>

        <!-- КАРТА (ИССЛЕДОВАНИЕ) -->
        <div id="scr-adv" class="screen">
            <div class="col">
                <div class="panel" style="padding: 4px; margin-bottom: 2px;">
                    <div style="display:flex; justify-content:space-between; font-size:7px;">
                        <span style="color:var(--hp)">❤️ <span id="a-hp">100</span></span>
                        <span style="color:var(--gold)">💰 <span id="a-gld">0</span></span>
                        <span style="color:var(--dust)">💎 <span id="a-dst">0</span></span>
                        <span style="color:#aaa">🗝️ <span id="a-key">0</span></span>
                    </div>
                </div>
                <div id="viewport"><div id="map-grid"></div></div>
                <div class="panel" style="padding: 4px; margin-top: 2px; font-size: 6px; color: #888; text-align:left;">
                    Локация: <span id="a-loc" style="color:#fff">Лес</span> (Этаж <span id="a-lvl" style="color:var(--acc)">1</span>) | Кирки: <span id="a-pick" style="color:#aaa">3</span> ⛏️
                </div>
            </div>
            <div class="col" style="justify-content: flex-end;">
                <div class="panel" id="adv-log" style="height: 60px; overflow-y: auto; background: #010104; color: #aaa; font-size: 6px; line-height: 1.5; text-align: left; margin-bottom: 4px;"></div>
                <div class="dpad">
                    <div></div><button class="dbtn" onclick="Map.move(0,-1)">▲</button><div></div>
                    <button class="dbtn" onclick="Map.move(-1,0)">◄</button>
                    <button class="dbtn" style="background:#4a235a; color:var(--acc); font-size:14px;" onclick="Camp.open()">🎒</button>
                    <button class="dbtn" onclick="Map.move(1,0)">►</button>
                    <div></div><button class="dbtn" onclick="Map.move(0,1)">▼</button><div></div>
                </div>
                <div style="display:flex; gap:4px; margin-top: 4px;">
                    <button class="btn" style="background:#223;" onclick="Game.save()">💾 СОХРАНИТЬ</button>
                    <button class="btn" style="background:#322;" onclick="UI.show('scr-menu')">В МЕНЮ</button>
                </div>
            </div>
        </div>

        <!-- ЛАГЕРЬ / ИНВЕНТАРЬ -->
        <div id="scr-camp" class="screen">
            <div class="col">
                <h2>ПЕРСОНАЖ</h2>
                <div class="panel">
                    <div style="display:flex; justify-content:space-between; margin-bottom: 4px;">
                        <span style="color:#fff; font-size:8px;">КЛАСС: <span id="c-cls" style="color:var(--mana)">-</span></span>
                        <span style="color:var(--acc); font-size:8px;">УРОВЕНЬ <span id="c-lvl">1</span></span>
                    </div>
                    <div class="bar"><div id="c-exp" class="fill" style="background:var(--exp); width:0%;"></div><div class="text-overlay">ОПЫТ</div></div>
                    
                    <div class="stat-grid" style="margin-top: 8px;">
                        <div class="stat-box">❤️ ОЗ: <span id="c-hp" style="color:var(--hp)">0</span></div>
                        <div class="stat-box">⚡ МАНА: <span id="c-mana" style="color:var(--mana)">0</span></div>
                        <div class="stat-box">⚔️ УРОН: <span id="c-dmg" style="color:var(--acc)">0</span></div>
                        <div class="stat-box">🛡️ БРОНЯ: <span id="c-arm" style="color:#aaa">0</span></div>
                        <div class="stat-box">🎯 КРИТ: <span id="c-crit" style="color:#f8f">0</span>%</div>
                        <div class="stat-box">💨 УКЛОН: <span id="c-dod" style="color:#8ff">0</span>%</div>
                    </div>
                </div>
                <h2>ЭКИПИРОВКА</h2>
                <div style="display:flex; gap:4px;">
                    <div class="slot" id="eq-w" style="width:33%;" onclick="Camp.uneq('w')">⚔️</div>
                    <div class="slot" id="eq-a" style="width:33%;" onclick="Camp.uneq('a')">🛡️</div>
                    <div class="slot" id="eq-r" style="width:33%;" onclick="Camp.uneq('r')">🔮</div>
                </div>
            </div>
            <div class="col">
                <div class="panel" style="flex-grow:1; display:flex; flex-direction:column;">
                    <div style="font-size:6px; color:#aaa; margin-bottom:4px; text-align:left;">ИНВЕНТАРЬ:</div>
                    <div class="inv" id="inv-list" style="flex-grow:1;"></div>
                </div>
                <div style="display:flex; gap:4px;">
                    <button class="btn" style="color:var(--dust);" onclick="Camp.craft()">КРАФТ (25💎)</button>
                    <button class="btn" style="color:var(--hp);" onclick="Camp.buyPotion()">ЗЕЛЬЕ (25💰)</button>
                </div>
                <button class="btn" style="background:#222;" onclick="UI.show('scr-adv')">ВЕРНУТЬСЯ</button>
            </div>
        </div>

        <!-- БОЙ -->
        <div id="scr-bat" class="screen">
            <div class="col">
                <h1 style="color:var(--hp);">БИТВА</h1>
                <div class="panel" style="flex-grow:1; display:flex; flex-direction:column; justify-content:space-between;">
                    <div style="display:flex; justify-content:space-between; font-size:8px;">
                        <span id="b-pn" style="color:var(--mana); font-weight:bold;">ГЕРОЙ</span>
                        <span id="b-en" style="color:var(--hp); font-weight:bold;">ВРАГ</span>
                    </div>
                    <div class="stage" id="bat-stage">
                        <div id="h-spr" class="sprite anim-idle">⚔️<div id="h-badge" class="status-badge" style="display:none;"></div></div>
                        <div id="e-spr" class="sprite anim-idle">👾<div id="e-badge" class="status-badge" style="display:none;"></div></div>
                    </div>
                    <div class="bar" style="height: 16px;">
                        <div id="b-ehp" class="fill" style="background:var(--hp); width:100%;"></div>
                        <div class="text-overlay" id="b-ehp-txt" style="font-size:8px; top:3px;">100/100</div>
                    </div>
                </div>
            </div>
            <div class="col">
                <div class="panel" id="log" style="height:80px; overflow-y:auto; background:#010104; color:#aaa; font-size:6px; line-height:1.6; text-align:left;"></div>
                <div class="panel">
                    <div class="bar" style="height: 16px; margin-bottom:8px;">
                        <div id="b-php" class="fill" style="background:#2c2; width:100%;"></div>
                        <div id="b-psh" class="fill" style="background:#77a; width:0%; position:absolute; top:0; left:0; opacity:0.8;"></div>
                        <div class="text-overlay" id="b-php-txt" style="font-size:8px; top:3px;">100/100</div>
                    </div>
                    <div style="font-size:8px; color:var(--mana); margin-bottom:6px; text-align:left; font-weight:bold;">⚡ МАНА: <span id="b-pm"></span></div>
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px;">
                        <button class="btn" id="sk-1" style="margin:0; color:#fff;" onclick="Combat.act(1)">[1] Атака</button>
                        <button class="btn" id="sk-2" style="margin:0; color:var(--mana);" onclick="Combat.act(2)">[2] Навык</button>
                        <button class="btn" id="sk-3" style="margin:0; color:#aaa;" onclick="Combat.act(3)">[3] Защита</button>
                        <button class="btn btn-acc" id="sk-4" style="margin:0;" onclick="Combat.act(4)">[4] УЛЬТ</button>
                    </div>
                </div>
            </div>
        </div>

    </div>

    <script>
        /**
         * v12.0 MEGA BUILD - The Ultimate Browser RPG
         */
        
        // --- 1. DATABASES ---
        const DB = {
            heroes: [
                { id: 'alu', n: "АЛУКАРД", hp: 180, dmg: 22, mp: 3, crt: 10, dod: 5, spr: "⚔️", d: "Боец. Базовые атаки исцеляют (Вампиризм 20%)." },
                { id: 'mia', n: "МИЯ", hp: 130, dmg: 28, mp: 3, crt: 30, dod: 15, spr: "🏹", d: "Стрелок. Высокий шанс крита. Магия замораживает." },
                { id: 'tig', n: "ТИГРИЛ", hp: 250, dmg: 15, mp: 3, crt: 5, dod: 5, spr: "🛡️", d: "Танк. Начинает бой со щитом. Броня +50%." },
                { id: 'gus', n: "ГОССЕН", hp: 140, dmg: 25, mp: 5, crt: 20, dod: 20, spr: "🗡️", d: "Ассасин. Восстанавливает больше маны. Ульт-казнь." },
                { id: 'eud', n: "ЭЙДОРА", hp: 120, dmg: 20, mp: 6, crt: 10, dod: 5, spr: "⚡", d: "Маг. Магия наносит огромный урон и шокирует." },
                { id: 'zil', n: "ЗИЛОНГ", hp: 160, dmg: 24, mp: 3, crt: 15, dod: 10, spr: "🐉", d: "Воин. Атакует дважды с шансом 30%." },
                { id: 'fra', n: "ФРАНКО", hp: 280, dmg: 12, mp: 3, crt: 5, dod: 0, spr: "🪝", d: "Танк. Огромное здоровье. Оглушает атаками." },
                { id: 'sab', n: "САБЕР", hp: 135, dmg: 26, mp: 4, crt: 25, dod: 15, spr: "🤺", d: "Ассасин. Ульт игнорирует броню врага." }
            ],
            zones: [
                { n: "Окраины Монии", w: "🌲", f: "#121e12", m: [{n:"Гоблин", h:80, d:12, s:"👺", ef:"none"}, {n:"Волк", h:60, d:15, s:"🐺", ef:"none"}] },
                { n: "Токсичное Болото", w: "🍄", f: "#1a2a1a", m: [{n:"Паук", h:100, d:14, s:"🕷️", ef:"psn"}, {n:"Слайм", h:120, d:10, s:"🦠", ef:"psn"}] },
                { n: "Снежные Вершины", w: "❄️", f: "#1a2a3a", m: [{n:"Йети", h:200, d:25, s:"⛄", ef:"stun"}, {n:"Ледяной Дух", h:150, d:30, s:"👻", ef:"none"}] },
                { n: "Руины Древних", w: "🗿", f: "#2a2a2a", m: [{n:"Голем", h:300, d:20, s:"🪨", ef:"none"}, {n:"Гаргулья", h:180, d:35, s:"🦇", ef:"brn"}] },
                { n: "Врата Бездны", w: "🏰", f: "#3a1a1a", m: [{n:"Демон", h:400, d:45, s:"👹", ef:"brn"}, {n:"Суккуб", h:250, d:50, s:"🧛‍♀️", ef:"psn"}] },
                { n: "Ядро Пекла", w: "🌋", f: "#200", m: [{n:"ТАМУЗ", h:1200, d:80, s:"👑", ef:"brn"}] } // BOSS
            ],
            loot: {
                w: { i:['🗡️','⚔️','🪓','🏹','🪄','🔱'], n:['Меч','Клинок','Топор','Лук','Посох','Трезубец'] },
                a: { i:['👕','🥋','🦺','🛡️','👗'], n:['Куртка','Кираса','Броня','Щит','Мантия'] },
                r: { i:['📿','🔮','💍','🧿','👑'], n:['Амулет','Сфера','Кольцо','Талисман','Корона'] },
                pref: ['Ржавый', 'Острый', 'Тяжелый', 'Магический', 'Пылающий', 'Ледяной', 'Ядовитый', 'Святой', 'Проклятый', 'Эпический', 'Легендарный', 'Божественный'],
                suf: ['Новичка', 'Солдата', 'Охотника', 'Убийцы', 'Короля', 'Дракона', 'Бездны', 'Тикси', 'Света', 'Тьмы']
            }
        };

        // --- 2. ПРОЦЕДУРНЫЙ ГЕНЕРАТОР ЛУТА ---
        function genItem(tierBonus = 0) {
            let type = ['w','a','r'][Math.floor(Math.random()*3)];
            let tObj = DB.loot[type];
            
            // Расчет редкости (0-Common, 1-Uncommon, 2-Rare, 3-Epic, 4-Legendary, 5-Mythic)
            let roll = Math.random() * 100;
            let tier = 0;
            if (roll < (5 + tierBonus*5)) tier = 5;
            else if (roll < (15 + tierBonus*10)) tier = 4;
            else if (roll < (30 + tierBonus*15)) tier = 3;
            else if (roll < (55 + tierBonus*15)) tier = 2;
            else if (roll < (80 + tierBonus*10)) tier = 1;

            // Расчет статов базируясь на редкости и текущем уровне зоны
            let baseStat = (tier+1) * 12 + Math.floor(Math.random()*20) + (Game.zIdx * 10);
            
            // Генерация имени
            let pref = DB.loot.pref[Math.min(DB.loot.pref.length-1, tier + Math.floor(Math.random()*3))];
            let suf = DB.loot.suf[Math.min(DB.loot.suf.length-1, Math.floor(tier*1.5) + Math.floor(Math.random()*2))];
            let name = `${pref} ${tObj.n[Math.floor(Math.random()*tObj.n.length)]}`;
            if(tier > 1) name += ` ${suf}`;

            return { t: type, n: name, i: tObj.i[Math.floor(Math.random()*tObj.i.length)], s: baseStat, tr: tier };
        }

        // --- 3. АУДИО СИНТЕЗАТОР ---
        const Audio = {
            c: null, sfx: true, mus: true, tmr: null, stp: 0, trk: null,
            init() { if(!this.c) this.c = new (window.AudioContext||window.webkitAudioContext)(); if(this.c.state==='suspended') this.c.resume(); },
            tog(t) { this[t] = !this[t]; UI.updSet(); if(t==='mus') this.play(this.trk); },
            tone(f, t, d, v=0.03) {
                if(!this.sfx || !this.c) return; this.init();
                let o=this.c.createOscillator(), g=this.c.createGain();
                o.type=t; o.frequency.value=f; g.gain.setValueAtTime(v, this.c.currentTime);
                g.gain.exponentialRampToValueAtTime(0.001, this.c.currentTime+d);
                o.connect(g); g.connect(this.c.destination); o.start(); o.stop(this.c.currentTime+d);
            },
            play(name) {
                this.trk = name; clearInterval(this.tmr); this.stp = 0;
                if(!this.mus || !name) return; this.init();
                
                // Процедурные мелодии
                let tData = name==='adv' 
                    ? {t:800, s:[196, 261, 329, 392, 329, 261], tp:'sine'} // C Major Arp (Спокойно)
                    : {t:300, s:[110, 110, 146, 110, 164, 110, 130, 110], tp:'sawtooth'}; // A Phrygian (Напряженно)
                
                this.tmr = setInterval(() => {
                    let n = tData.s[this.stp%tData.s.length];
                    if(this.mus) {
                        let o=this.c.createOscillator(), g=this.c.createGain(); o.type=tData.tp; o.frequency.value=n;
                        g.gain.setValueAtTime(0.02, this.c.currentTime); g.gain.exponentialRampToValueAtTime(0.001, this.c.currentTime+(tData.t/1000)*0.8);
                        o.connect(g); g.connect(this.c.destination); o.start(); o.stop(this.c.currentTime+(tData.t/1000));
                    }
                    this.stp++;
                }, tData.t);
            },
            fx: { 
                stp:()=>Audio.tone(100,'triangle',0.05,0.01), 
                hit:()=>Audio.tone(120,'square',0.1,0.05),
                crit:()=>{Audio.tone(300,'square',0.05,0.05); setTimeout(()=>Audio.tone(200,'sawtooth',0.1,0.05), 50);},
                lt:()=>{Audio.tone(600,'sine',0.1,0.03); setTimeout(()=>Audio.tone(800,'sine',0.2,0.03),100);},
                er:()=>Audio.tone(80,'sawtooth',0.2,0.05), 
                mg:()=>Audio.tone(400,'triangle',0.3,0.04),
                lvl:()=>{[440,554,659,880].forEach((f,i)=>setTimeout(()=>Audio.tone(f,'sine',0.2,0.04), i*100));}
            }
        };

        // --- 4. ЯДРО ИГРЫ И ХАРАКТЕРИСТИКИ ---
        const Game = {
            isPlaying: false, hIdx: 0, zIdx: 0,
            p: { 
                lvl:1, xp:0, nxp:100, hp:0, mhp:0, mp:0, mmp:0, dmg:0, crt:0, dod:0, arm:0, 
                gld:50, dst:10, key:0, pick:3, eq:{w:null,a:null,r:null}, inv:[], 
                stats: { str:0, agi:0, int:0, vit:0 } 
            },
            
            hero() { return DB.heroes[this.hIdx]; },
            nextHero() { this.hIdx = (this.hIdx+1)%DB.heroes.length; Audio.init(); UI.updSet(); },
            
            calcStats() {
                let h = this.hero();
                // Расчет статов от базовых + атрибуты + вещи
                this.p.mhp = h.hp + (this.p.lvl*15) + (this.p.stats.vit*20) + (this.p.stats.str*5) + (this.p.eq.r ? this.p.eq.r.s : 0);
                this.p.dmg = h.dmg + (this.p.lvl*4) + (this.p.stats.str*4) + (this.p.stats.agi*1) + (this.p.eq.w ? this.p.eq.w.s : 0);
                this.p.mmp = h.mp + Math.floor(this.p.lvl/4) + (this.p.stats.int*1);
                this.p.crt = h.crt + (this.p.stats.agi*2) + (this.p.eq.w && this.p.eq.w.tr>3 ? 10 : 0);
                this.p.dod = h.dod + (this.p.stats.agi*1);
                this.p.arm = (this.p.stats.vit*2) + (this.p.eq.a ? this.p.eq.a.s : 0);
            },
            
            start() {
                Audio.init(); this.isPlaying = true; this.zIdx = 0;
                let h = this.hero();
                this.p = { 
                    lvl:1, xp:0, nxp:100, hp:h.hp, mp:h.mp, 
                    gld:30, dst:5, key:0, pick:3, eq:{w:null,a:null,r:null}, inv:[], 
                    stats: { str:0, agi:0, int:0, vit:0 } 
                };
                this.calcStats(); this.p.hp = this.p.mhp; this.p.mp = this.p.mmp;
                Map.gen(); UI.show('scr-adv'); UI.tst("Акт I: Путешествие начинается", "#ff5");
            },

            addXp(v) {
                this.p.xp += v;
                if(this.p.xp >= this.p.nxp) {
                    this.p.xp -= this.p.nxp; this.p.nxp = Math.floor(this.p.nxp * 1.5); this.p.lvl++;
                    document.getElementById('modal').style.display = 'flex'; Audio.fx.lvl();
                }
            },
            
            lvlUpStat(stat) {
                this.p.stats[stat]++;
                this.calcStats(); this.p.hp = this.p.mhp; this.p.mp = this.p.mmp;
                document.getElementById('modal').style.display = 'none'; UI.tst("Характеристики улучшены!", "#a5f"); UI.updAdv();
            },

            save() {
                let data = { hIdx: this.hIdx, zIdx: this.zIdx, p: this.p, map: {g: Map.g, sz: Map.sz, px: Map.px, py: Map.py} };
                localStorage.setItem('mlbb_rpg_save', JSON.stringify(data));
                UI.tst("ИГРА СОХРАНЕНА", "#5f5"); Audio.fx.lt();
            },

            load() {
                let data = localStorage.getItem('mlbb_rpg_save');
                if(data) {
                    data = JSON.parse(data);
                    this.hIdx = data.hIdx; this.zIdx = data.zIdx; this.p = data.p;
                    Map.g = data.map.g; Map.sz = data.map.sz; Map.px = data.map.px; Map.py = data.map.py;
                    this.isPlaying = true; Audio.init(); this.calcStats(); UI.show('scr-adv'); UI.tst("ИГРА ЗАГРУЖЕНА", "#5f5"); Audio.fx.lt();
                    Map.draw();
                } else {
                    UI.tst("Нет сохранений!", "#f44"); Audio.fx.er();
                }
            }
        };

        // --- 5. КАРТА (BSP-like Dungeon Gen) ---
        const Map = {
            g: [], sz: 24, px: 2, py: 2,
            
            // Простая генерация лабиринта комнатами
            gen() {
                this.g = []; Audio.play('adv');
                for(let y=0; y<this.sz; y++) {
                    let r = []; for(let x=0; x<this.sz; x++) r.push(1); // Заполняем стенами
                    this.g.push(r);
                }

                // Копаем комнаты
                let rooms = [];
                for(let i=0; i<8; i++) {
                    let w = 4 + Math.floor(Math.random()*4); let h = 4 + Math.floor(Math.random()*4);
                    let x = 2 + Math.floor(Math.random()*(this.sz-w-4)); let y = 2 + Math.floor(Math.random()*(this.sz-h-4));
                    rooms.push({x,y,w,h});
                    for(let ry=y; ry<y+h; ry++) { for(let rx=x; rx<x+w; rx++) { this.g[ry][rx] = 0; } }
                }

                // Соединяем комнаты коридорами
                for(let i=0; i<rooms.length-1; i++) {
                    let r1 = rooms[i], r2 = rooms[i+1];
                    let c1 = {x: Math.floor(r1.x+r1.w/2), y: Math.floor(r1.y+r1.h/2)};
                    let c2 = {x: Math.floor(r2.x+r2.w/2), y: Math.floor(r2.y+r2.h/2)};
                    
                    let cx = c1.x, cy = c1.y;
                    while(cx !== c2.x) { this.g[cy][cx] = 0; cx += (c2.x > cx ? 1 : -1); }
                    while(cy !== c2.y) { this.g[cy][cx] = 0; cy += (c2.y > cy ? 1 : -1); }
                }

                // Старт в первой комнате
                this.px = Math.floor(rooms[0].x + rooms[0].w/2); this.py = Math.floor(rooms[0].y + rooms[0].h/2);
                
                // Выход в последней
                this.g[Math.floor(rooms[rooms.length-1].y + rooms[rooms.length-1].h/2)][Math.floor(rooms[rooms.length-1].x + rooms[rooms.length-1].w/2)] = 3;

                // Расставляем объекты
                for(let y=1; y<this.sz-1; y++) {
                    for(let x=1; x<this.sz-1; x++) {
                        if(this.g[y][x] === 0 && (x!==this.px || y!==this.py) && this.g[y][x]!==3) {
                            let rnd = Math.random();
                            // 0:Пол, 1:Стена, 2:Моб, 3:Выход, 4:Монета, 5:Хил, 6:Магаз, 7:Сундук, 8:Ключ, 9:Ловушка, 10:Алтарь, 11:Кирка
                            if(rnd<0.05) this.g[y][x] = 2;
                            else if(rnd<0.08) this.g[y][x] = 4;
                            else if(rnd<0.09) this.g[y][x] = 5;
                            else if(rnd<0.10) this.g[y][x] = 6;
                            else if(rnd<0.12) this.g[y][x] = 7;
                            else if(rnd<0.14) this.g[y][x] = 8;
                            else if(rnd<0.16) this.g[y][x] = 9;
                            else if(rnd<0.17) this.g[y][x] = 10;
                            else if(rnd<0.18) this.g[y][x] = 11;
                        }
                    }
                }
                UI.updAdv();
            },
            draw() {
                let htm = "", z = DB.zones[Game.zIdx];
                let viewR = 4; // Обзор 9x9 (радиус 4)
                
                for(let y = this.py-viewR; y <= this.py+viewR; y++) {
                    for(let x = this.px-viewR; x <= this.px+viewR; x++) {
                        let d = Math.max(Math.abs(x-this.px), Math.abs(y-this.py));
                        let cls = d===4?"dim-3":d===3?"dim-2":d===2?"dim-1":"";
                        
                        if(y<0||y>=this.sz||x<0||x>=this.sz) { htm += `<div class="tile wall ${cls}">${z.w}</div>`; continue; }
                        
                        let v = this.g[y][x], c = "", bg = z.f;
                        if(x===this.px && y===this.py) { c = Game.hero().spr; cls = ""; bg = "#440"; }
                        else if(v===1) { c = z.w; cls += " wall"; bg = ""; }
                        else if(v===2) c = "👾"; else if(v===3) c = "🌀"; else if(v===4) c = "💰";
                        else if(v===5) c = "⛲"; else if(v===6) c = "🛒"; else if(v===7) c = "🧰";
                        else if(v===8) c = "🗝️"; else if(v===9) c = "🪤"; else if(v===10) c = "⛩️";
                        else if(v===11) c = "⛏️";

                        htm += `<div class="tile ${cls}" style="background:${bg}" onclick="Map.click(${x},${y})">${c}</div>`;
                    }
                }
                document.getElementById('map-grid').innerHTML = htm;
            },
            log(m) { let l = document.getElementById('adv-log'); l.innerHTML += `<div>> ${m}</div>`; l.scrollTop = l.scrollHeight; },
            click(x, y) {
                if(this.g[y][x] === 1 && Math.abs(x-this.px)<=1 && Math.abs(y-this.py)<=1 && Game.p.pick>0) {
                    Game.p.pick--; this.g[y][x] = 0; UI.tst("Стена разрушена киркою!", "#aaa"); this.log("Разрушена стена."); Audio.fx.hit(); UI.updAdv();
                }
            },
            move(dx, dy) {
                let tx = this.px+dx, ty = this.py+dy, tile = this.g[ty][tx];
                if(tile === 1) return; // Стена
                
                this.px = tx; this.py = ty; Audio.fx.stp();
                if(tile === 2) return Combat.start();
                if(tile === 3) { 
                    Game.zIdx++; 
                    if(Game.zIdx >= DB.zones.length) { alert("ВЫ ПОБЕДИЛИ В ИГРЕ!"); return UI.show('scr-menu'); }
                    UI.tst(`Этаж ${Game.zIdx+1}`, "#a5f"); Game.p.pick+=1; this.log("Спуск на следующий этаж."); this.gen(); return; 
                }
                if(tile === 4) { let g=15+Math.floor(Math.random()*25); Game.p.gld+=g; UI.tst(`+${g}💰`, "var(--gold)"); this.log(`Найдено ${g} золота.`); Audio.fx.lt(); this.g[ty][tx]=0; }
                if(tile === 5) { Game.p.hp=Game.p.mhp; Game.p.mp=Game.p.mmp; UI.tst("Полное Исцеление!", "#5f5"); this.log("Родник восстановил силы."); Audio.fx.lt(); this.g[ty][tx]=0; }
                if(tile === 6) { if(Game.p.gld>=60){ Game.p.gld-=60; let i=genItem(2); Game.p.inv.push(i); UI.tst(`Куплено: ${i.n}`, "#fa0"); this.log(`Торговец продал ${i.n}.`); Audio.fx.lt(); } else { UI.tst("Нужно 60💰", "#f44"); Audio.fx.er(); } this.g[ty][tx]=0; }
                if(tile === 7) { if(Game.p.key>0){ Game.p.key--; let i=genItem(3); Game.p.inv.push(i); UI.tst(`Из сундука: ${i.n}`, "#a5f"); this.log(`Сундук открыт: ${i.n}.`); Audio.fx.lt(); this.g[ty][tx]=0; } else { UI.tst("Нужен ключ 🗝️", "#f44"); this.log("Сундук заперт."); Audio.fx.er(); this.px-=dx; this.py-=dy; } }
                if(tile === 8) { Game.p.key++; UI.tst("Найден ключ!", "#fff"); this.log("Подобран ключ."); Audio.fx.lt(); this.g[ty][tx]=0; }
                if(tile === 9) { let d=Math.floor(Game.p.mhp*0.2); Game.p.hp-=d; UI.tst(`Ловушка! -${d} ОЗ`, "#f44"); this.log(`Вы наступили в ловушку! Урон: ${d}.`); Audio.fx.er(); this.g[ty][tx]=0; if(Game.p.hp<=0) Combat.end(false); }
                if(tile === 10){ Game.p.mhp+=20; Game.p.hp+=20; UI.tst("Алтарь: +20 Макс ОЗ", "#ff5"); this.log("Алтарь увеличил максимальное здоровье."); Audio.fx.mg(); this.g[ty][tx]=0; }
                if(tile === 11){ Game.p.pick++; UI.tst("Найдена кирка!", "#aaa"); this.log("Подобрана кирка."); Audio.fx.lt(); this.g[ty][tx]=0; }
                UI.updAdv();
            }
        };

        // --- 6. ЛАГЕРЬ И ИНВЕНТАРЬ ---
        const Camp = {
            open() {
                Game.calcStats(); let p = Game.p;
                document.getElementById('c-cls').innerText = Game.hero().n;
                document.getElementById('c-lvl').innerText = p.lvl;
                document.getElementById('c-hp').innerText = `${p.hp}/${p.mhp}`;
                document.getElementById('c-dmg').innerText = p.dmg;
                document.getElementById('c-mana').innerText = `${p.mp}/${p.mmp}`;
                document.getElementById('c-arm').innerText = p.arm;
                document.getElementById('c-crit').innerText = p.crt;
                document.getElementById('c-dod').innerText = p.dod;
                document.getElementById('c-exp').style.width = `${(p.xp/p.nxp)*100}%`;
                
                ['w','a','r'].forEach(t => {
                    let e = p.eq[t];
                    document.getElementById(`eq-${t}`).innerHTML = e ? `${e.i}<span>+${e.s}</span>` : (t==='w'?'⚔️':t==='a'?'🛡️':'🔮');
                    document.getElementById(`eq-${t}`).className = `slot tier-${e?e.tr:0}`;
                });

                let htm = "";
                p.inv.forEach((it, i) => { 
                    htm += `<div class="slot tier-${it.tr}" onclick="Camp.showItem(${i})">${it.i}<span>+${it.s}</span></div>`; 
                });
                document.getElementById('inv-list').innerHTML = htm;
                UI.show('scr-camp');
            },
            showItem(idx) {
                let it = Game.p.inv[idx];
                let rarities = ['Обычное', 'Необычное', 'Редкое', 'Эпическое', 'Легендарное', 'МИФИЧЕСКОЕ'];
                let colors = ['#888', '#5f5', '#55f', '#a3f', '#fa0', '#f55'];
                let html = `
                    <h2 style="color:${colors[it.tr]}">${it.n} ${it.i}</h2>
                    <p style="font-size:8px; margin: 10px 0;">Редкость: ${rarities[it.tr]}</p>
                    <p style="font-size:10px; color:var(--acc); margin: 10px 0;">Мощь: +${it.s}</p>
                    <div style="display:flex; gap:10px; justify-content:center; margin-top:20px;">
                        <button class="btn" style="background:#252;" onclick="Camp.equip(${idx})">НАДЕТЬ</button>
                        <button class="btn" style="background:#522;" onclick="Camp.scrap(${idx})">СЛОМ (+${5 + it.tr*10}💎)</button>
                        <button class="btn" onclick="document.getElementById('item-modal').style.display='none'">ОТМЕНА</button>
                    </div>
                `;
                document.getElementById('item-details').innerHTML = html;
                document.getElementById('item-modal').style.display = 'flex';
                Audio.fx.stp();
            },
            equip(idx) {
                document.getElementById('item-modal').style.display='none';
                Audio.fx.stp(); let it = Game.p.inv[idx];
                if(Game.p.eq[it.t]) Game.p.inv.push(Game.p.eq[it.t]);
                Game.p.eq[it.t] = it; Game.p.inv.splice(idx, 1);
                UI.tst(`Надето: ${it.n}`, "#5f5"); this.open();
            },
            scrap(idx) {
                document.getElementById('item-modal').style.display='none';
                let it = Game.p.inv[idx]; let d = 5 + (it.tr*10); 
                Game.p.inv.splice(idx,1); Game.p.dst += d; 
                UI.tst(`Разобрано! +${d}💎`, "#a5f"); Audio.fx.lt(); this.open();
            },
            uneq(t) { if(Game.p.eq[t]) { Game.p.inv.push(Game.p.eq[t]); Game.p.eq[t] = null; Audio.fx.stp(); this.open(); } },
            craft() { if(Game.p.dst>=25){ Game.p.dst-=25; let it=genItem(2); Game.p.inv.push(it); UI.tst(`Крафт: ${it.n}`, "#a5f"); Audio.fx.lt(); this.open(); } else { UI.tst("Нужно 25 Пыли!", "#f44"); Audio.fx.er(); } },
            buyPotion() { if(Game.p.gld>=25){ Game.p.gld-=25; Game.p.hp=Game.p.mhp; UI.tst("Здоровье восстановлено!", "#5f5"); Audio.fx.lt(); this.open(); } else { UI.tst("Нужно 25 Золота!", "#f44"); Audio.fx.er(); } }
        };

        // --- 7. БОЕВАЯ СИСТЕМА ---
        const Combat = {
            e: null, sh: 0, trn: 'p', pEf: {psn:0, brn:0, stn:0}, eEf: {psn:0, brn:0, stn:0},
            start() {
                Audio.play('bat'); document.getElementById('log').innerHTML = "";
                let pool = DB.zones[Game.zIdx].m;
                this.e = { ...pool[Math.floor(Math.random()*pool.length)] }; 
                // Бафф статов врага от уровня зоны
                this.e.mhp = this.e.h + (Game.zIdx * 50); this.e.h = this.e.mhp;
                this.e.d = this.e.d + (Game.zIdx * 5);

                Game.p.mp = Game.p.mmp; this.sh = (Game.hero().id==='tig') ? 80 : 0; this.trn = 'p';
                this.pEf = {psn:0, brn:0, stn:0}; this.eEf = {psn:0, brn:0, stn:0};
                
                document.getElementById('b-pn').innerText = Game.hero().n; document.getElementById('h-spr').innerHTML = `${Game.hero().spr}<div id="h-badge" class="status-badge" style="display:none;"></div>`;
                document.getElementById('b-en').innerText = this.e.n; document.getElementById('e-spr').innerHTML = `${this.e.s}<div id="e-badge" class="status-badge" style="display:none;"></div>`;
                
                this.upd(); UI.show('scr-bat'); this.log("Начало сражения!", "#ff5");
            },
            upd() {
                let p = Game.p;
                document.getElementById('b-php-txt').innerText = `${p.hp}/${p.mhp}`; document.getElementById('b-php').style.width = `${(p.hp/p.mhp)*100}%`;
                document.getElementById('b-psh').style.width = `${(this.sh/p.mhp)*100}%`; document.getElementById('b-pm').innerText = `${p.mp}/${p.mmp}`;
                document.getElementById('b-ehp-txt').innerText = `${this.e.h}/${this.e.mhp}`; document.getElementById('b-ehp').style.width = `${(this.e.h/this.e.mhp)*100}%`;
                
                let my = (this.trn === 'p');
                document.getElementById('sk-1').disabled = !my; document.getElementById('sk-2').disabled = (!my || p.mp<1);
                document.getElementById('sk-3').disabled = (!my || p.mp<1); document.getElementById('sk-4').disabled = (!my || p.mp<3);

                // Update badges
                let hB = document.getElementById('h-badge'), eB = document.getElementById('e-badge');
                if(this.pEf.psn>0||this.pEf.brn>0||this.pEf.stn>0) { hB.style.display='block'; hB.innerText = this.pEf.stn>0?'⚡':this.pEf.brn>0?'🔥':'☠️'; } else hB.style.display='none';
                if(this.eEf.psn>0||this.eEf.brn>0||this.eEf.stn>0) { eB.style.display='block'; eB.innerText = this.eEf.stn>0?'⚡':this.eEf.brn>0?'🔥':'☠️'; } else eB.style.display='none';
            },
            log(m, c="#aaa") { let b = document.getElementById('log'); b.innerHTML += `<div style="color:${c}">> ${m}</div>`; b.scrollTop = b.scrollHeight; },
            anim(id, cls) { let el = document.getElementById(id); el.classList.remove('anim-idle'); el.classList.add(cls); setTimeout(()=>{ el.classList.remove(cls); el.classList.add('anim-idle'); }, 300); },
            float(id, txt, col) { 
                let tgt = document.getElementById(id); let f = document.createElement('div');
                f.className = 'floating-text'; f.style.color = col; f.innerText = txt;
                f.style.left = (Math.random()*60+20)+'%'; f.style.top = (Math.random()*40+20)+'%';
                tgt.parentElement.appendChild(f); setTimeout(()=>f.remove(), 1200);
            },
            
            procEf(isP) {
                let ef = isP ? this.pEf : this.eEf, t = isP ? Game.p : this.e, tgtId = isP ? 'h-spr' : 'e-spr';
                if(ef.psn>0) { ef.psn--; let d=Math.floor(t.mhp*0.05); t.hp?t.hp-=d:t.h-=d; this.float(tgtId, `-${d}`, "#5f5"); this.log("Урон от яда", "#5f5"); }
                if(ef.brn>0) { ef.brn--; let d=Math.floor(t.mhp*0.08); t.hp?t.hp-=d:t.h-=d; this.float(tgtId, `-${d}`, "#fa0"); this.log("Урон от огня", "#fa0"); }
                if(ef.stn>0) { ef.stn--; this.float(tgtId, "ОГЛУШЕН", "#fff"); this.log("Пропуск хода (Оглушение)", "#fff"); return true; }
                return false;
            },

            act(ty) {
                if(this.trn !== 'p') return;
                let p = Game.p, h = Game.hero();
                if(this.procEf(true)) { this.endTurn(); return; }

                this.anim('h-spr', 'atkL'); 
                let dmg = Math.max(1, p.dmg); 
                let isCrit = (Math.random()*100 < p.crt);
                if(isCrit) { dmg = Math.floor(dmg * 2); Audio.fx.crit(); } else { Audio.fx.hit(); }

                if(ty===1) {
                    if(h.id==='zil' && Math.random()<0.3) { dmg*=2; this.log("ДВОЙНАЯ АТАКА!", "#ff5"); }
                    if(h.id==='alu') { let v=Math.floor(dmg*0.2); p.hp=Math.min(p.mhp, p.hp+v); this.float('h-spr', `+${v}`, "#2c2"); }
                    if(h.id==='fra' && Math.random()<0.2) { this.eEf.stn=1; this.float('e-spr', 'ОГЛУШЕН', '#fff'); }
                    
                    this.e.h -= dmg; p.mp = Math.min(p.mmp, p.mp+(h.id==='gus'?2:1));
                    this.float('e-spr', isCrit?`КРИТ! ${dmg}`:`-${dmg}`, isCrit?"var(--acc)":"#fff");
                    this.log(`Атака: -${dmg} урона`);
                }
                else if(ty===2) {
                    p.mp -= 1; Audio.fx.mg();
                    if(h.id==='mia') { dmg=Math.floor(dmg*0.8); this.eEf.stn=1; this.log("Враг заморожен!", "#5af"); }
                    else if(h.id==='eud') { dmg = Math.floor(dmg * 1.8); this.eEf.stn = Math.random()<0.5?1:0; }
                    else dmg = Math.floor(dmg * 1.5);
                    this.e.h -= dmg; this.float('e-spr', `-${dmg}`, "var(--mana)"); this.log(`Навык: -${dmg} урона`, "var(--mana)");
                }
                else if(ty===3) {
                    p.mp -= 1; let s = Math.floor(p.mhp*0.25 * (h.id==='tig'?1.5:1)) + p.arm; this.sh += s; Audio.fx.stp();
                    this.float('h-spr', `+${s} ЩИТ`, "#aaa"); this.log(`Установлен щит: +${s}`, "#aaa");
                }
                else if(ty===4) {
                    p.mp -= 3; dmg = Math.floor(dmg*3); Audio.fx.mg();
                    if(h.id==='gus' && this.e.h < this.e.mhp*0.3) dmg = Math.floor(dmg*3); // Казнь
                    if(h.id==='sab') dmg += this.e.d; // Игнор брони (доп урон)
                    this.e.h -= dmg; this.float('e-spr', `УЛЬТ! ${dmg}`, "var(--hp)"); this.log(`УЛЬТИМЕЙТ: -${dmg} урона!`, "var(--hp)");
                }

                if(this.e.h <= 0) return this.end(true);
                this.endTurn();
            },
            
            endTurn() { this.trn = 'e'; this.upd(); setTimeout(() => this.eAct(), 800); },
            
            eAct() {
                if(this.procEf(false)) { this.trn='p'; this.upd(); return; }
                this.anim('e-spr', 'atkR');
                
                // Уклонение
                if(Math.random()*100 < Game.p.dod) {
                    this.float('h-spr', 'УКЛОНЕНИЕ', '#8ff'); this.log(`${this.e.n} промахнулся!`, '#8ff'); Audio.fx.stp();
                } else {
                    let d = Math.floor(this.e.d * (0.8 + Math.random()*0.4));
                    // Снижение урона от брони игрока (простая формула)
                    d = Math.max(1, d - Math.floor(Game.p.arm * 0.5));

                    if(this.e.ef === 'psn' && Math.random()<0.3) { this.pEf.psn = 3; this.float('h-spr', "ЯД", "#5f5"); }
                    if(this.e.ef === 'stn' && Math.random()<0.2) { this.pEf.stn = 1; this.float('h-spr', "ОГЛУШЕНИЕ", "#fff"); }
                    if(this.e.ef === 'brn' && Math.random()<0.3) { this.pEf.brn = 3; this.float('h-spr', "ОЖОГ", "#fa0"); }
                    
                    if(this.sh > 0) {
                        if(this.sh >= d) { this.sh -= d; d = 0; this.log("Урон заблокирован щитом!", "#aaa"); }
                        else { d -= this.sh; this.sh = 0; }
                    }
                    if(d > 0) { Game.p.hp -= d; this.float('h-spr', `-${d}`, "#f44"); this.log(`${this.e.n} бьет: -${d} ОЗ`, "#f44"); Audio.fx.er(); }
                }
                
                if(Game.p.hp <= 0) return this.end(false);
                this.trn = 'p'; this.upd();
            },
            
            end(win) {
                if(win) {
                    let xp = 40 + Game.zIdx*25, g = 15 + Math.floor(Math.random()*25);
                    Game.p.gld += g; UI.tst(`Победа! +${xp}XP | +${g}💰`, "#ff5");
                    Map.g[Map.py][Map.px] = 0; Map.draw(); Audio.play('adv'); UI.show('scr-adv');
                    Game.addXp(xp);
                } else {
                    alert("ВЫ ПОГИБЛИ. БЕЗДНА ПОГЛОТИЛА ВАС."); Audio.play(null); UI.show('scr-menu');
                }
            }
        };

        // --- 8. ИНТЕРФЕЙС УПРАВЛЕНИЯ ---
        const UI = {
            show(id) { document.querySelectorAll('.screen').forEach(s => s.classList.remove('active')); document.getElementById(id).classList.add('active'); Audio.fx.stp(); if(id==='scr-set') this.updSet(); },
            updSet() {
                let h = Game.hero();
                document.getElementById('cfg-hero').innerText = h.n; 
                document.getElementById('cfg-sfx').innerText = Audio.sfx?"ВКЛ":"ВЫКЛ"; 
                document.getElementById('cfg-mus').innerText = Audio.mus?"ВКЛ":"ВЫКЛ";
                document.getElementById('hero-sprite-big').innerText = h.spr;
                document.getElementById('hero-desc').innerHTML = `${h.d}<br><br><span style='color:var(--hp)'>ОЗ: ${h.hp}</span><br><span style='color:var(--hp)'>Урон: ${h.dmg}</span><br><span style='color:var(--mana)'>Мана: ${h.mp}</span><br><span style='color:var(--acc)'>Крит: ${h.crt}%</span><br><span style='color:#8ff'>Уклонение: ${h.dod}%</span>`;
            },
            updAdv() {
                document.getElementById('a-hp').innerText = `${Game.p.hp}/${Game.p.mhp}`; document.getElementById('a-gld').innerText = Game.p.gld;
                document.getElementById('a-dst').innerText = Game.p.dst; document.getElementById('a-key').innerText = Game.p.key;
                document.getElementById('a-lvl').innerText = Game.zIdx+1; document.getElementById('a-loc').innerText = DB.zones[Game.zIdx].n;
                document.getElementById('a-pick').innerText = Game.p.pick;
                Map.draw();
            },
            tst(m, c="#fff") {
                let b = document.getElementById('toasts'), t = document.createElement('div');
                t.className = 'toast'; t.style.borderColor = c; t.innerText = m;
                b.appendChild(t); setTimeout(() => t.remove(), 2400);
            },
            toggleFullscreen() {
                if (!document.fullscreenElement) { document.documentElement.requestFullscreen().catch(e => console.log(e)); } 
                else { if (document.exitFullscreen) document.exitFullscreen(); }
            }
        };

        // ХОТКЕИ
        window.addEventListener('keydown', (e) => {
            if(document.getElementById('scr-adv').classList.contains('active')) {
                if(['w','ArrowUp','ц'].includes(e.key.toLowerCase())) Map.move(0,-1); 
                if(['s','ArrowDown','ы'].includes(e.key.toLowerCase())) Map.move(0,1);
                if(['a','ArrowLeft','ф'].includes(e.key.toLowerCase())) Map.move(-1,0); 
                if(['d','ArrowRight','в'].includes(e.key.toLowerCase())) Map.move(1,0);
            } else if(document.getElementById('scr-bat').classList.contains('active')) {
                if(['1','2','3','4'].includes(e.key)) Combat.act(parseInt(e.key));
            }
        });

        UI.updSet();
    </script>
</body>
</html>'''

@app.route('/')
def home():
    return render_template_string(GAME_HTML)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
