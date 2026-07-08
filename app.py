from flask import Flask, render_template_string
import os

app = Flask(__name__)

# Весь код игры обернут в raw, чтобы Flask не конфликтовал с JavaScript
GAME_HTML = """{% raw %}
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>MLBB RPG: ULTIMATE NEXUS</title>
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
    <style>
        :root { 
            --bg: #030308; --panel: rgba(15, 15, 25, 0.95); --border: #445588; 
            --acc: #00ffff; --hp: #ff3344; --mana: #33ccff; --gold: #ffdd33;
            --dust: #cc44ff; --exp: #33ff55;
        }
        * { box-sizing: border-box; user-select: none; -webkit-user-select: none; touch-action: manipulation; }
        body { 
            font-family: 'Press Start 2P', cursive; background: var(--bg); color: #e0e0f0; 
            margin: 0; padding: 0; font-size: 8px; text-align: center; overflow: hidden; 
            height: 100vh; width: 100vw; display: flex; justify-content: center; align-items: center;
        }
        
        #game-wrapper { 
            width: 100%; max-width: 1000px; height: 100%; max-height: 100vh;
            background: radial-gradient(circle at center, #111122 0%, #030308 100%);
            border: 2px solid var(--border); box-shadow: 0 0 30px rgba(0, 255, 255, 0.2);
            position: relative; display: flex; flex-direction: column; overflow: hidden;
        }

        /* Адаптация под полный экран телефона */
        :fullscreen #game-wrapper, :-webkit-full-screen #game-wrapper { border: none; }

        .screen { display: none; height: 100%; width: 100%; padding: 8px; }
        .screen.active { display: flex; flex-direction: row; gap: 8px; animation: fade 0.3s ease-out; }
        @keyframes fade { from { opacity: 0; filter: blur(4px); } to { opacity: 1; filter: blur(0); } }

        /* ИДЕАЛЬНОЕ УПРАВЛЕНИЕ: ДВА ПУЛЬТА ПО БОКАМ, ЭКРАН ПО ЦЕНТРУ */
        .side-controls { 
            width: 80px; height: 100%; display: flex; flex-direction: column; 
            justify-content: center; gap: 8px; flex-shrink: 0; z-index: 10;
        }
        .center-view { 
            flex-grow: 1; height: 100%; display: flex; flex-direction: column; 
            justify-content: space-between; overflow: hidden; position: relative;
        }

        /* Кнопки геймпада */
        .btn-pad {
            background: linear-gradient(180deg, #25254a, #15152b); border: 2px solid #5566aa;
            color: #fff; font-family: 'Press Start 2P', cursive; font-size: 16px;
            padding: 16px 0; border-radius: 8px; cursor: pointer; box-shadow: 0 6px 0 #0a0a14;
            transition: 0.1s; display: flex; align-items: center; justify-content: center;
        }
        .btn-pad:active { transform: translateY(4px); box-shadow: 0 2px 0 #0a0a14; background: #111122; color: var(--acc); border-color: var(--acc); }
        .btn-action { font-size: 10px; padding: 12px 0; background: linear-gradient(180deg, #4a153a, #2b0b22); border-color: #aa5588; }
        .btn-action:active { color: var(--gold); border-color: var(--gold); }

        /* Обычные кнопки UI */
        .btn-ui {
            background: #1c2c4a; border: 2px solid var(--border); color: #fff; padding: 12px;
            font-family: inherit; font-size: 8px; cursor: pointer; border-radius: 4px;
            box-shadow: 0 4px 0 #0a0a14; transition: 0.1s; text-transform: uppercase; width: 100%; margin: 4px 0;
        }
        .btn-ui:active { transform: translateY(2px); box-shadow: 0 2px 0 #0a0a14; }
        .btn-ui.glow { border-color: var(--acc); color: var(--acc); box-shadow: 0 4px 0 #005555, 0 0 10px rgba(0,255,255,0.4); }

        .panel { background: var(--panel); border: 2px solid var(--border); border-radius: 6px; padding: 8px; box-shadow: inset 0 0 15px rgba(0,0,0,0.8); }

        /* Карта (Вьюпорт) */
        #viewport {
            flex-grow: 1; border: 3px solid #445588; background: #000; border-radius: 8px;
            position: relative; overflow: hidden; box-shadow: inset 0 0 40px #000;
        }
        #map-container { position: absolute; transition: transform 0.15s linear; }
        .map-row { display: flex; }
        .tile { 
            width: 40px; height: 40px; flex-shrink: 0; display: flex; align-items: center; justify-content: center;
            font-size: 20px; background: #0a140a; border: 1px solid #111a11; text-shadow: 0 2px 5px rgba(0,0,0,0.8);
        }
        .tile.wall { background: #0a0a10; border-color: #05050a; color: #1a1a24; }
        .tile.fog { background: #000; filter: brightness(0); border-color: #000; }
        .tile.dim { filter: brightness(0.4); }

        /* Прогресс-бары */
        .bar { width: 100%; height: 14px; background: #111; border: 1px solid #555; position: relative; border-radius: 3px; margin: 2px 0; overflow: hidden; }
        .fill { height: 100%; transition: width 0.2s ease; }
        .bar-txt { position: absolute; width: 100%; text-align: center; top: 2px; left: 0; font-size: 7px; color: #fff; text-shadow: 1px 1px 0 #000; }

        /* Боевая арена */
        #battle-stage { 
            flex-grow: 1; border: 3px solid #882222; border-radius: 8px; background: linear-gradient(to top, #1a0a0a, #05050a);
            position: relative; overflow: hidden; box-shadow: inset 0 0 50px #000;
        }
        .fighter { position: absolute; bottom: 15px; font-size: 60px; filter: drop-shadow(0 5px 5px rgba(0,0,0,0.8)); transition: 0.2s; }
        #f-player { left: 15%; transform: scaleX(-1); }
        #f-enemy { right: 15%; }
        
        .dmg-pop { position: absolute; font-size: 14px; font-weight: bold; text-shadow: 2px 2px 0 #000; pointer-events: none; z-index: 100; animation: pop 1s forwards ease-out; }
        @keyframes pop { 0% { opacity: 1; transform: translateY(0) scale(0.5); } 20% { transform: translateY(-20px) scale(1.2); } 100% { opacity: 0; transform: translateY(-60px) scale(1); } }

        /* Лог и тосты */
        #log-box { height: 60px; overflow-y: auto; font-size: 6px; text-align: left; color: #aaa; line-height: 1.5; padding: 4px; }
        #toasts { position: absolute; top: 10px; width: 100%; display: flex; flex-direction: column; align-items: center; z-index: 1000; pointer-events: none; gap: 4px; }
        .toast { background: rgba(0,0,0,0.9); border: 2px solid var(--acc); color: #fff; padding: 10px 20px; font-size: 8px; border-radius: 6px; box-shadow: 0 4px 15px rgba(0,255,255,0.3); animation: tAnim 2.5s forwards; }
        @keyframes tAnim { 0%, 100% { opacity: 0; transform: translateY(-20px); } 10%, 90% { opacity: 1; transform: translateY(0); } }

        /* Инвентарь */
        .inv-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px; margin-top: 4px; overflow-y: auto; max-height: 180px;}
        .inv-slot { aspect-ratio: 1; background: #000; border: 2px solid #334; display: flex; align-items: center; justify-content: center; font-size: 24px; cursor: pointer; border-radius: 4px; position: relative; }
        .inv-slot:hover { border-color: #fff; }
        .inv-lvl { position: absolute; bottom: 2px; right: 2px; font-size: 6px; background: rgba(0,0,0,0.8); padding: 2px; color: #fff; }
        
        .t-0 { border-color: #777; } .t-1 { border-color: #5f5; box-shadow: inset 0 0 5px #5f5; } 
        .t-2 { border-color: #55f; box-shadow: inset 0 0 10px #55f; } .t-3 { border-color: #a3f; box-shadow: inset 0 0 15px #a3f; } 
        .t-4 { border-color: #fa0; box-shadow: inset 0 0 20px #fa0; } .t-5 { border-color: #f33; box-shadow: inset 0 0 25px #f33; animation: blink 1.5s infinite; }
        @keyframes blink { 0%, 100% { filter: brightness(1); } 50% { filter: brightness(1.5); } }

        /* Модалка */
        #modal { display: none; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); z-index: 500; justify-content: center; align-items: center; }
        .modal-box { background: var(--panel); border: 2px solid var(--acc); padding: 15px; border-radius: 8px; max-width: 400px; width: 90%; box-shadow: 0 0 40px rgba(0,255,255,0.2); }
    </style>
</head>
<body>

<div id="game-wrapper">
    <div id="toasts"></div>
    
    <div id="modal">
        <div class="modal-box" id="modal-content"></div>
    </div>

    <!-- ==================== ЭКРАН 1: ГЛАВНОЕ МЕНЮ ==================== -->
    <div id="scr-menu" class="screen active" style="flex-direction: column; justify-content: center; align-items: center;">
        <h1 style="font-size: 32px; line-height: 1.2;">MLBB RPG<br><span style="color:#fff; font-size: 14px;">ULTIMATE NEXUS</span></h1>
        <div style="font-size: 80px; margin: 20px 0; filter: drop-shadow(0 0 20px var(--acc));">🌌</div>
        <div style="width: 100%; max-width: 300px; display: flex; flex-direction: column; gap: 8px;">
            <button class="btn-ui glow" style="font-size: 12px; padding: 16px;" onclick="Game.initNew()">НОВАЯ ИГРА</button>
            <button class="btn-ui" onclick="Game.load()">ПРОДОЛЖИТЬ ИГРУ</button>
            <button class="btn-ui" onclick="UI.show('scr-hero')">ВЫБОР ГЕРОЯ</button>
            <button class="btn-ui" style="background:#223;" onclick="UI.fullscreen()">ПОЛНЫЙ ЭКРАН 🔲</button>
        </div>
    </div>

    <!-- ==================== ЭКРАН 2: ВЫБОР ГЕРОЯ ==================== -->
    <div id="scr-hero" class="screen" style="flex-direction: column; justify-content: center; align-items: center;">
        <h1 style="color:var(--mana)">ВЫБОР ЧЕМПИОНА</h1>
        <div class="panel" style="width: 100%; max-width: 400px; display: flex; align-items: center; justify-content: space-between; margin: 20px 0;">
            <button class="btn-ui" style="width: 60px; font-size: 16px;" onclick="Game.switchHero(-1)">◀</button>
            <div id="hero-display-spr" style="font-size: 80px; filter: drop-shadow(0 0 10px #fff);">⚔️</div>
            <button class="btn-ui" style="width: 60px; font-size: 16px;" onclick="Game.switchHero(1)">▶</button>
        </div>
        <div class="panel" id="hero-display-info" style="width: 100%; max-width: 400px; text-align: left; line-height: 1.8;"></div>
        <button class="btn-ui glow" style="max-width: 400px; margin-top: 10px;" onclick="UI.show('scr-menu')">В МЕНЮ</button>
    </div>

    <!-- ==================== ЭКРАН 3: КАРТА И ПРИКЛЮЧЕНИЕ ==================== -->
    <div id="scr-adv" class="screen">
        <!-- ЛЕВЫЙ ПУЛЬТ -->
        <div class="side-controls">
            <button class="pad-btn" onclick="Map.move(0, -1)">▲</button>
            <button class="pad-btn" onclick="Map.move(-1, 0)">◀</button>
            <button class="pad-btn" onclick="Map.move(0, 1)">▼</button>
            <button class="pad-btn action-btn" onclick="Camp.open()">🎒 СУМКА</button>
        </div>
        
        <!-- ЦЕНТРАЛЬНАЯ КАРТА -->
        <div class="center-view">
            <div class="panel" style="display:flex; justify-content:space-between; padding:6px; font-size:8px; margin:0;">
                <span style="color:var(--hp)">❤️ <span id="ui-hp"></span></span>
                <span style="color:var(--gold)">💰 <span id="ui-gld"></span></span>
                <span style="color:var(--mana)">Этаж <span id="ui-flr"></span></span>
            </div>
            
            <div id="viewport"><div id="map-container"></div></div>
            
            <div class="panel" style="padding:4px 8px; font-size:6.5px; color:#aaa; margin:0; display:flex; justify-content:space-between;">
                <span>Кирки: <span id="ui-pick" style="color:#fff"></span>⛏️</span>
                <span>Ключи: <span id="ui-key" style="color:#fff"></span>🗝️</span>
            </div>
        </div>
        
        <!-- ПРАВЫЙ ПУЛЬТ -->
        <div class="side-controls">
            <button class="pad-btn" onclick="Map.move(0, -1)">▲</button>
            <button class="pad-btn" onclick="Map.move(1, 0)">▶</button>
            <button class="pad-btn" onclick="Map.move(0, 1)">▼</button>
            <button class="pad-btn action-btn" style="background:#4a1111; border-color:#883333;" onclick="Game.saveAndExit()">🚪 ВЫХОД</button>
        </div>
    </div>

    <!-- ==================== ЭКРАН 4: ЛАГЕРЬ И ИНВЕНТАРЬ ==================== -->
    <div id="scr-camp" class="screen">
        <div class="center-view" style="width: 48%; flex-grow: 0;">
            <div class="panel">
                <h2 style="color:var(--acc); font-size:12px; margin:0 0 8px 0;" id="c-name">ГЕРОЙ</h2>
                <div class="bar"><div id="c-xp-bar" class="fill" style="background:var(--exp);"></div><div class="bar-txt">ОПЫТ: <span id="c-xp-txt"></span></div></div>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:6px; text-align:left; font-size:8px; margin-top:8px;">
                    <div>УРОВЕНЬ: <span id="c-lvl" style="color:var(--acc)"></span></div>
                    <div>ОЗ: <span id="c-hp" style="color:var(--hp)"></span></div>
                    <div>АТАКА: <span id="c-dmg" style="color:var(--gold)"></span></div>
                    <div>БРОНЯ: <span id="c-def" style="color:var(--mana)"></span></div>
                </div>
                <div style="margin-top:10px; border-top:1px solid #334; padding-top:10px;">
                    <p style="color:var(--gold); font-size:7px; margin-bottom:6px;">Очки прокачки: <span id="c-sp"></span></p>
                    <div style="display:flex; gap:4px;">
                        <button class="btn-ui" onclick="Game.addStat('dmg')">+⚔️ Атака</button>
                        <button class="btn-ui" onclick="Game.addStat('hp')">+❤️ Здоровье</button>
                    </div>
                </div>
            </div>
            <div class="panel" style="flex-grow:1; display:flex; flex-direction:column; justify-content:center;">
                <h2 style="margin:0 0 10px 0;">НАДЕТО</h2>
                <div style="display:flex; justify-content:center; gap:10px;">
                    <div class="inv-slot" id="eq-w" onclick="Camp.uneq('w')">⚔️</div>
                    <div class="inv-slot" id="eq-a" onclick="Camp.uneq('a')">🛡️</div>
                </div>
            </div>
        </div>
        
        <div class="center-view" style="width: 50%;">
            <div class="panel" style="flex-grow:1; display:flex; flex-direction:column;">
                <div style="display:flex; justify-content:space-between; font-size:8px; margin-bottom:4px;">
                    <span>СУМКА</span><span>Пыль: <span id="c-dust" style="color:var(--dust)"></span>💎</span>
                </div>
                <div class="inv-grid" id="inv-container"></div>
            </div>
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px;">
                <button class="btn-ui" style="background:#313; border-color:var(--dust);" onclick="Camp.craft()">🛠️ КУЗНЯ (30💎)</button>
                <button class="btn-ui" style="background:#131; border-color:var(--hp);" onclick="Camp.heal()">🧪 ЗЕЛЬЕ (50💰)</button>
            </div>
            <button class="btn-ui glow" style="padding:16px;" onclick="UI.show('scr-adv')">ВЕРНУТЬСЯ НА КАРТУ</button>
        </div>
    </div>

    <!-- ==================== ЭКРАН 5: БОЙ ==================== -->
    <div id="scr-battle" class="screen">
        <div class="side-controls">
            <!-- Левые боевые хоткеи для пальца -->
            <button class="pad-btn" style="background:#422;" onclick="Combat.act(1)">⚔️<br><span style="font-size:6px; margin-top:4px; display:block;">УДАР</span></button>
            <button class="pad-btn" style="background:#224;" onclick="Combat.act(2)">✨<br><span style="font-size:6px; margin-top:4px; display:block;">СКИЛЛ</span></button>
        </div>
        
        <div class="center-view">
            <div class="panel" style="display:flex; justify-content:space-between; font-size:8px; padding:6px; margin:0;">
                <span id="b-pname" style="color:var(--mana);">ГЕРОЙ</span>
                <span style="color:#666">VS</span>
                <span id="b-ename" style="color:var(--hp);">ВРАГ</span>
            </div>
            
            <div id="battle-stage">
                <div id="f-player" class="fighter idle-anim">🏃‍♂️</div>
                <div id="f-enemy" class="fighter idle-anim">👾</div>
            </div>
            
            <div class="panel" style="margin:0; padding:6px;">
                <div class="bar"><div id="b-php-bar" class="fill" style="background:#2c2;"></div><div class="bar-txt" id="b-php-txt"></div></div>
                <div class="bar"><div id="b-ehp-bar" class="fill" style="background:var(--hp);"></div><div class="bar-txt" id="b-ehp-txt"></div></div>
            </div>
            
            <div id="log-box" class="panel" style="flex-grow:1; margin:0;"></div>
        </div>
        
        <div class="side-controls">
            <!-- Правые боевые хоткеи для пальца -->
            <button class="pad-btn" style="background:#242;" onclick="Combat.act(3)">🛡️<br><span style="font-size:6px; margin-top:4px; display:block;">БЛОК</span></button>
            <button class="pad-btn glow" style="background:#440; border-color:var(--acc);" onclick="Combat.act(4)">☄️<br><span style="font-size:6px; margin-top:4px; display:block; color:var(--acc);">УЛЬТ</span></button>
        </div>
    </div>

</div>

<script>
// ==================== АУДИО ДВИЖОК ====================
const Snd = {
    ctx: null,
    init() { if(!this.ctx) this.ctx = new (window.AudioContext || window.webkitAudioContext)(); },
    play(type) {
        this.init(); if(!this.ctx) return;
        const o = this.ctx.createOscillator(), g = this.ctx.createGain();
        o.connect(g); g.connect(this.ctx.destination);
        const t = this.ctx.currentTime;
        if(type==='step') { o.type='triangle'; o.frequency.setValueAtTime(100, t); g.gain.setValueAtTime(0.05, t); g.gain.linearRampToValueAtTime(0, t+0.05); o.start(t); o.stop(t+0.05); }
        else if(type==='hit') { o.type='sawtooth'; o.frequency.setValueAtTime(160, t); o.frequency.exponentialRampToValueAtTime(40, t+0.1); g.gain.setValueAtTime(0.2, t); g.gain.linearRampToValueAtTime(0, t+0.1); o.start(t); o.stop(t+0.1); }
        else if(type==='loot') { o.type='sine'; o.frequency.setValueAtTime(400, t); o.frequency.setValueAtTime(600, t+0.08); g.gain.setValueAtTime(0.15, t); g.gain.linearRampToValueAtTime(0, t+0.2); o.start(t); o.stop(t+0.2); }
        else if(type==='ult') { o.type='square'; o.frequency.setValueAtTime(80, t); o.frequency.linearRampToValueAtTime(800, t+0.4); g.gain.setValueAtTime(0.3, t); g.gain.linearRampToValueAtTime(0, t+0.4); o.start(t); o.stop(t+0.4); }
    }
};

// ==================== БАЗА ДАННЫХ ИГРЫ ====================
const DB = {
    heroes: [
        { id:'alu', n:'АЛУКАРД', spr:'⚔️', hp:320, dmg:45, def:15, desc:'Боец. Лечится на 25% от нанесенного врагу урона.' },
        { id:'mia', n:'МИЯ', spr:'🏹', hp:220, dmg:55, def:8, desc:'Стрелок. Имеет 30% шанс нанести двойной критический урон.' },
        { id:'tig', n:'ТИГРИЛ', spr:'🛡️', hp:450, dmg:30, def:30, desc:'Танк. Снижает весь получаемый урон на 5 единиц.' },
        { id:'gus', n:'ГОССЕН', spr:'🗡️', hp:240, dmg:50, def:12, desc:'Убийца. Ультимейт наносит х1.5 урона, если у врага мало ОЗ.' },
        { id:'eud', n:'ЭЙДОРА', spr:'⚡', hp:200, dmg:65, def:10, desc:'Маг. Навыки наносят колоссальный магический урон.' },
        { id:'zil', n:'ЗИЛОНГ', spr:'🐉', hp:280, dmg:42, def:16, desc:'Воин. Шанс 20% атаковать дважды за один ход.' },
        { id:'fra', n:'ФРАНКО', spr:'🪝', hp:480, dmg:25, def:28, desc:'Танк. Генерирует усиленные щиты во время боя.' },
        { id:'sab', n:'САБЕР', spr:'🤺', hp:230, dmg:48, def:11, desc:'Ассасин. Атаки игнорируют 50% защиты противника.' }
    ],
    enemies: [
        { n:"Миньон", spr:"👺", hp:120, dmg:20, def:5, xp:35, gld:20 },
        { n:"Теневой Волк", spr:"🐺", hp:180, dmg:30, def:10, xp:50, gld:35 },
        { n:"Голем Скал", spr:"🪨", hp:350, dmg:45, def:30, xp:90, gld:60 },
        { n:"Демон Бездны", spr:"👹", hp:500, dmg:65, def:25, xp:150, gld:90 },
        { n:"ЛОРД ТАМУЗ", spr:"🔥", hp:2000, dmg:100, def:50, xp:9999, gld:999, boss:true }
    ],
    loot: {
        w: { i:['🗡️','⚔️','🪓','🏹','🪄'], n:['Меч','Клинок','Топор','Лук','Посох'] },
        a: { i:['👕','🥋','🦺','🛡️'], n:['Куртка','Кираса','Броня','Щит'] },
        pref: ['Ржавый', 'Крепкий', 'Магический', 'Пылающий', 'Священный', 'Мифический'],
        suf: ['Новичка', 'Солдата', 'Короля', 'Дракона', 'Бездны']
    }
};

function genItem(bonusLvl) {
    let type = Math.random() < 0.5 ? 'w' : 'a';
    let base = DB.loot[type];
    
    let roll = Math.random() * 100;
    let tier = 0; // 0-Common .. 5-Mythic
    if (roll < 3 + bonusLvl*2) tier = 5;
    else if (roll < 12 + bonusLvl*4) tier = 4;
    else if (roll < 30 + bonusLvl*5) tier = 3;
    else if (roll < 60) tier = 2;
    else tier = 1;

    let statVal = (tier+1) * 12 + Math.floor(Math.random()*25) + (Game.zIdx * 15);
    let name = `${DB.loot.pref[Math.min(5, tier)]} ${base.n[Math.floor(Math.random()*base.n.length)]} ${tier>2 ? DB.loot.suf[Math.min(4, tier-2)] : ''}`;

    return { t: type, n: name, i: base.i[Math.floor(Math.random()*base.i.length)], v: statVal, tr: tier, upg: 0 };
}

// ==================== СОСТОЯНИЕ ИГРЫ ====================
let Game = {
    hIdx: 0, zIdx: 0, p: null,
    
    initNew() {
        Snd.init(); this.zIdx = 0; let h = DB.heroes[this.hIdx];
        this.p = {
            id: h.id, n: h.n, spr: h.spr, lvl: 1, xp: 0, nxp: 120, sp: 0,
            bhp: h.hp, mhp: h.hp, hp: h.hp, bdmg: h.dmg, dmg: h.dmg, bdef: h.def, def: h.def,
            gld: 200, dst: 30, keys: 2, picks: 5, eq: { w: null, a: null }, inv: []
        };
        Map.gen(); UI.show('scr-adv'); UI.updateAdv(); UI.toast("Акт I: Врата открыты!", "#0f0");
    },
    
    cycleHero(d) { this.hIdx = (this.hIdx + d + DB.heroes.length) % DB.heroes.length; UI.updateHeroScreen(); Snd.play('step'); },
    
    calcStats() {
        let p = this.p; p.mhp = p.bhp; p.dmg = p.bdmg; p.def = p.bdef;
        if(p.eq.w) p.dmg += p.eq.w.v; if(p.eq.a) p.def += p.eq.a.v;
        if(p.hp > p.mhp) p.hp = p.mhp;
    },
    
    addStat(type) {
        if(this.p.sp <= 0) return;
        this.p.sp--;
        if(type==='dmg') this.p.bdmg += 4;
        if(type==='hp') { this.p.bhp += 35; this.p.hp += 35; }
        this.calcStats(); Camp.open(); Snd.play('loot');
    },

    addXp(amt) {
        this.p.xp += amt;
        while(this.p.xp >= this.p.nxp) {
            this.p.xp -= this.p.nxp; this.p.lvl++; this.p.sp += 2; this.p.nxp = Math.floor(this.p.nxp * 1.4);
            this.p.bhp += 20; this.p.bdmg += 5; this.p.bdef += 2;
            this.calcStats(); this.p.hp = this.p.mhp; Snd.play('ult');
            UI.toast(`🌟 УРОВЕНЬ ПОВЫШЕН: ${this.p.lvl}!`, "#3f3");
        }
    },

    saveAndExit() {
        localStorage.setItem('mlbb_v16_save', JSON.stringify({ hIdx: this.hIdx, zIdx: this.zIdx, p: this.p, map: Map.getState() }));
        UI.show('scr-menu'); UI.toast("Прогресс сохранен!", "#55f");
    },
    
    load() {
        let raw = localStorage.getItem('mlbb_v16_save');
        if(!raw) return UI.toast("Нет сохранений!", "#f33");
        let data = JSON.parse(raw);
        this.hIdx = data.hIdx; this.zIdx = data.zIdx; this.p = data.p;
        Map.setState(data.map); this.calcStats();
        UI.show('scr-adv'); UI.updateAdv(); UI.toast("Игра загружена!", "#0f0");
    }
};

// ==================== КАРТА (40x40) ====================
const Map = {
    w: 40, h: 40, grid: [], px: 1, py: 1, fog: [],
    
    getState() { return { g: this.grid, px: this.px, py: this.py, fog: this.fog }; },
    setState(s) { this.grid = s.g; this.px = s.px; this.py = s.py; this.fog = s.fog; this.draw(); },

    gen() {
        this.grid = Array(this.h).fill().map(() => Array(this.w).fill(1));
        let cx = 20, cy = 20; this.px = cx; this.py = cy; this.grid[cy][cx] = 0;
        
        for(let i=0; i<1000; i++) {
            let dir = [{x:0,y:1},{x:0,y:-1},{x:1,y:0},{x:-1,y:0}][Math.floor(Math.random()*4)];
            if(cx+dir.x>1 && cx+dir.x<this.w-2 && cy+dir.y>1 && cy+dir.y<this.h-2) { cx += dir.x; cy += dir.y; this.grid[cy][cx] = 0; }
        }

        let floors = [];
        for(let y=1; y<this.h-1; y++) for(let x=1; x<this.w-1; x++) if(this.grid[y][x] === 0 && (x!==this.px || y!==this.py)) floors.push({x,y});
        floors.sort(() => Math.random() - 0.5);

        if(floors.length > 0) this.grid[floors.pop().y][floors.pop().x] = Game.zIdx === 4 ? 6 : 5; // Босс или Выход
        
        let nE = 25 + Game.zIdx*5, nC = 15;
        while(floors.length > 0 && nE-- > 0) this.grid[floors.pop().y][floors.pop().x] = 2; // Моб
        while(floors.length > 0 && nC-- > 0) this.grid[floors.pop().y][floors.pop().x] = Math.random()<0.35 ? 8 : 4; // Ключ/Сундук
        while(floors.length > 0 && Math.random()<0.05) this.grid[floors.pop().y][floors.pop().x] = 9; // Торговец
        while(floors.length > 0 && Math.random()<0.05) this.grid[floors.pop().y][floors.pop().x] = 7; // Фонтан

        this.fog = Array(this.h).fill().map(() => Array(this.w).fill(true));
        this.updateFog(); this.draw();
    },

    updateFog() {
        let r = 5;
        for(let y = this.py-r; y <= this.py+r; y++) {
            for(let x = this.px-r; x <= this.px+r; x++) {
                if(y>=0 && y<this.h && x>=0 && x<this.w) { if((x-this.px)**2 + (y-this.py)**2 <= r**2) this.fog[y][x] = false; }
            }
        }
    },

    draw() {
        const cont = document.getElementById('map-container'); let html = '';
        for(let y=0; y<this.h; y++) {
            html += '<div class="map-row">';
            for(let x=0; x<this.w; x++) {
                let cls = 'tile', txt = '';
                if(this.fog[y][x]) { cls += ' fog'; }
                else {
                    let v = this.grid[y][x];
                    if(x===this.px && y===this.py) { txt = Game.p.spr; }
                    else if(v===1) { cls += ' wall'; }
                    else if(v===2) { txt = '👾'; }
                    else if(v===4) { txt = '🧰'; }
                    else if(v===5) { txt = '🪜'; }
                    else if(v===6) { txt = '🔥'; }
                    else if(v===7) { txt = '⛲'; }
                    else if(v===8) { txt = '🗝️'; }
                    else if(v===9) { txt = '🛒'; }
                    
                    if(Math.max(Math.abs(x-this.px), Math.abs(y-this.py)) >= 4) cls += ' dim';
                }
                html += `<div class="${cls}" onclick="Map.click(${x},${y})">${txt}</div>`;
            }
            html += '</div>';
        }
        cont.innerHTML = html;
        
        let ts = 40, vp = document.getElementById('viewport');
        let cx = (vp.clientWidth / 2) - (this.px * ts) - (ts/2);
        let cy = (vp.clientHeight / 2) - (this.py * ts) - (ts/2);
        cont.style.transform = `translate(${cx}px, ${cy}px)`;
    },

    click(x, y) {
        if(Math.abs(x-this.px)<=1 && Math.abs(y-this.py)<=1 && this.grid[y][x]===1 && Game.p.picks>0) {
            Game.p.picks--; this.grid[y][x]=0; Snd.play('hit'); this.updateFog(); this.draw(); UI.updateAdv();
        }
    },

    move(dx, dy) {
        let nx = this.px + dx, ny = this.py + dy;
        if(nx<0 || nx>=this.w || ny<0 || ny>=this.h) return;
        let t = this.grid[ny][nx]; if(t === 1) return;

        this.px = nx; this.py = ny; Snd.play('step'); this.updateFog();

        if(t === 2) { this.grid[ny][nx]=0; return Combat.start(false); }
        if(t === 6) { this.grid[ny][nx]=0; return Combat.start(true); }
        
        if(t === 4) {
            if(Game.p.keys > 0) {
                Game.p.keys--; this.grid[ny][nx]=0; Snd.play('loot');
                let it = genItem(Game.zIdx); Game.p.inv.push(it); UI.toast(`Лут: ${it.n}!`, "var(--acc)");
            } else { UI.toast("Нужен ключ! 🗝️", "#f33"); this.px-=dx; this.py-=dy; }
        }
        else if(t === 8) { Game.p.keys++; this.grid[ny][nx]=0; Snd.play('loot'); UI.toast("Ключ найден! 🗝️"); }
        else if(t === 7) { Game.p.hp=Game.p.mhp; this.grid[ny][nx]=0; Snd.play('skill'); UI.toast("Исцеление!", "#5f5"); }
        else if(t === 9) { 
            if(Game.p.gld>=120) { Game.p.gld-=120; this.grid[ny][nx]=0; let it = genItem(Game.zIdx+2); Game.p.inv.push(it); Snd.play('loot'); UI.toast(`Куплено: ${it.n}`, "var(--dust)"); }
            else { UI.toast("Нужно 120 золота!", "#f33"); this.px-=dx; this.py-=dy; }
        }
        else if(t === 5) {
            Game.zIdx++; Game.p.picks+=3; UI.toast(`Глубина ${Game.zIdx+1}!`, "var(--mana)");
            this.gen(); Game.save(); return;
        }

        this.draw(); UI.updateAdv();
    }
};

// ==================== ЛАГЕРЬ ====================
const Camp = {
    open() {
        Game.calcStats();
        document.getElementById('c-name').textContent = Game.p.n; document.getElementById('c-lvl').textContent = Game.p.lvl;
        document.getElementById('c-xp-txt').textContent = `${Game.p.xp}/${Game.p.nxp}`; document.getElementById('c-exp-bar').style.width = `${(Game.p.xp/Game.p.nxp)*100}%`;
        document.getElementById('c-hp').textContent = `${Game.p.hp}/${Game.p.mhp}`; document.getElementById('c-dmg').textContent = Game.p.dmg;
        document.getElementById('c-def').textContent = Game.p.def; document.getElementById('c-sp').textContent = Game.p.sp;
        document.getElementById('c-dust').textContent = Game.p.dust;

        ['w','a'].forEach(t => {
            let el = document.getElementById(`eq-${t}`); let it = Game.p.eq[t];
            el.className = `inv-slot t-${it ? it.tr : 0}`;
            el.innerHTML = it ? `${it.i}<div class="inv-lvl">+${it.upg}</div>` : (t==='w'?'⚔️':'🛡️');
        });

        const invEl = document.getElementById('inventory-container'); invEl.innerHTML = '';
        Game.p.inv.forEach((it, i) => {
            let slot = document.createElement('div'); slot.className = `inv-slot t-${it.tr}`;
            slot.innerHTML = `${it.i}<div class="inv-lvl">+${it.upg}</div>`;
            slot.onclick = () => this.showItem(i); invEl.appendChild(slot);
        });
        UI.show('scr-camp');
    },

    showItem(idx) {
        let it = Game.p.inv[idx]; let rNames = ['Обыч', 'Необыч', 'Редк', 'Эпик', 'Лега', 'МИФ']; let rCols = ['#888', '#5f5', '#55f', '#a3f', '#fa0', '#f33'];
        let html = `
            <h2 style="color:${rCols[it.tr]}; font-size:12px;">${it.i} ${it.n}</h2>
            <p style="font-size:7px; color:#aaa;">${it.t==='w'?'Оружие':'Броня'} | ${rNames[it.tr]}</p>
            <p style="font-size:14px; color:var(--acc); margin: 15px 0;">+${it.v} ${it.stat==='dmg'?'Атака':'Защита'}</p>
            <div style="display:flex; flex-direction:column; gap:6px; margin-top:20px;">
                <button class="btn" style="background:#141;" onclick="Camp.equip(${idx})">НАДЕТЬ</button>
                <button class="btn" style="background:#414;" onclick="Camp.upgrade(${idx})">ТОЧИТЬ (15💎)</button>
                <button class="btn" style="background:#411;" onclick="Camp.scrap(${idx})">РАЗОБРАТЬ (+${5 + it.tr*5}💎)</button>
                <button class="btn" onclick="UI.closeModal()">ОТМЕНА</button>
            </div>
        `;
        UI.openModal(html);
    },

    equip(idx) { UI.closeModal(); let it = Game.p.inv[idx]; if(Game.p.eq[it.t]) Game.p.inv.push(Game.p.eq[it.t]); Game.p.eq[it.t] = it; Game.p.inv.splice(idx, 1); Snd.play('step'); this.open(); UI.toast(`Надето: ${it.n}`); },
    upgrade(idx) {
        if(Game.p.dust < 15) return UI.toast("Мало Пыли!", "#f33");
        Game.p.dust -= 15; let it = Game.p.inv[idx]; it.upg++; it.v += Math.floor(it.v * 0.15) + 4; 
        UI.closeModal(); this.open(); UI.toast(`Заточка +${it.upg}!`, "var(--acc)"); Snd.play('skill');
    },
    uneq(t) { if(Game.p.eq[t]) { Game.p.inv.push(Game.p.eq[t]); Game.p.eq[t] = null; this.open(); } },
    scrap(idx) { let it = Game.p.inv[idx]; let d = 5 + it.tr*5 + it.upg*3; Game.p.inv.splice(idx, 1); Game.p.dust += d; UI.closeModal(); this.open(); UI.toast(`Разобрано! +${d}💎`, "var(--dust)"); Snd.play('loot'); },
    craft() {
        if(Game.p.dust < 25) return UI.toast("Мало пыли!", "#f33");
        Game.p.dust -= 25; let it = genItem(Game.p.lvl > 8 ? 2 : 0); Game.p.inv.push(it); this.open(); UI.toast(`Выковано: ${it.n}!`, "var(--acc)"); Snd.play('ult');
    },
    buyPotion() {
        if(Game.p.gld < 50) return UI.toast("Мало золота!", "#f33");
        Game.p.gld -= 50; Game.p.hp = Game.p.mhp; this.open(); UI.toast("ОЗ восстановлено!", "#5f5"); Snd.play('skill');
    }
};

// ==================== БОЕВАЯ СИСТЕМА ====================
const Combat = {
    e: null, isBoss: false,
    start(bossMode) {
        this.isBoss = bossMode; let pool = DB.enemies;
        let baseE = bossMode ? pool[4] : pool[Math.floor(Math.random()*4)];
        let scale = 1 + (Game.zIdx * 0.4);
        this.e = { ...baseE, maxHp: Math.floor(baseE.hp*scale), hp: Math.floor(baseE.hp*scale), dmg: Math.floor(baseE.dmg*scale), def: Math.floor(baseE.def*scale) };
        
        document.getElementById('b-pname').textContent = Game.p.n; document.getElementById('b-ename').textContent = `${this.e.n} [Ур.${Game.zIdx+1}]`;
        document.getElementById('player-sprite').textContent = Game.p.spr; document.getElementById('enemy-sprite').textContent = this.e.spr;
        document.getElementById('battle-log').innerHTML = '';
        
        UI.show('scr-battle'); this.log(`СХВАТКА! ${this.e.n} нападает!`, "var(--acc)");
        this.updateUI();
    },
    updateUI() {
        document.getElementById('b-php-txt').textContent = `${Game.p.hp}/${Game.p.mhp}`; document.getElementById('b-php-bar').style.width = `${(Game.p.hp/Game.p.mhp)*100}%`;
        document.getElementById('b-ehp-txt').textContent = `${this.e.hp}/${this.e.maxHp}`; document.getElementById('b-ehp-bar').style.width = `${(this.e.hp/this.e.maxHp)*100}%`;
    },
    anim(id, cls) { 
        let el = document.getElementById(id); el.style.animation = 'none'; void el.offsetWidth; 
        el.style.animation = `${cls} 0.25s ease`; setTimeout(()=>el.style.animation = 'breathe 2.5s infinite ease-in-out', 250); 
    },
    float(id, txt, c="#fff") {
        let el = document.getElementById(id); let f = document.createElement('div');
        f.className = 'dmg-pop'; f.style.color = c; f.textContent = txt;
        f.style.left = (Math.random()*20+25)+'%'; el.parentElement.appendChild(f); setTimeout(()=>f.remove(), 1000);
    },
    log(m, c="#aaa") { let l = document.getElementById('battle-log'); l.innerHTML += `<div>> ${m}</div>`; l.scrollTop = l.scrollHeight; },
    
    act(type) {
        let dmg = Game.p.dmg; this.anim('f-player', 'strikeL');
        
        if(type === 1) {
            let isCrit = Math.random()*100 < (Game.p.id==='mia'?30:5);
            if(isCrit) dmg = Math.floor(dmg * 2);
            if(Game.p.id==='zil' && Math.random()<0.2) dmg = Math.floor(dmg * 1.8);
            
            let final = Math.max(3, dmg - this.e.def); this.e.hp = Math.max(0, this.e.hp - final);
            if(Game.p.id === 'alu') { let v=Math.floor(final*0.25); Game.p.hp=Math.min(Game.p.mhp, Game.p.hp+v); this.float('f-player', `+${v}`, "#2c2"); }
            
            this.float('f-enemy', isCrit?`КРИТ! ${final}`:`-${final}`, isCrit?"var(--acc)":"#fff"); this.log(`Атака: -${final} ОЗ.`); Snd.play(isCrit?'ult':'hit');
        } else if(type === 2) {
            let final = Math.floor(dmg * 1.6); this.e.hp = Math.max(0, this.e.hp - final);
            this.float('f-enemy', `-${final}!`, "var(--mana)"); this.log(`Скилл: -${final} ОЗ.`); Snd.play('skill');
        } else if(type === 3) {
            let heal = Math.floor(Game.p.mhp * 0.2); Game.p.hp = Math.min(Game.p.mhp, Game.p.hp+heal);
            this.float('f-player', `+${heal}`, "#5f5"); this.log(`Защита восстановила: +${heal} ОЗ.`); Snd.play('loot');
        } else if(type === 4) {
            let final = Math.floor(dmg * 3.5); if(Game.p.id==='gus' && this.e.hp < this.e.maxHp/2) final = Math.floor(final * 1.5);
            this.e.hp = Math.max(0, this.e.hp - final);
            this.float('f-enemy', `УЛЬТ! ${final}`, "var(--hp)"); this.log(`УЛЬТИМЕЙТ: -${final} ОЗ!`); Snd.play('ult');
        }

        this.updateUI();
        if(this.e.hp <= 0) return setTimeout(() => this.end(true), 400);
        
        // Отключение кнопок на время хода врага
        for(let i=1;i<=4;i++) document.getElementById(`sk-${i}`).disabled = true;
        setTimeout(() => this.enemyAct(), 600);
    },
    enemyAct() {
        if(this.e.hp <= 0 || Game.p.hp <= 0) return;
        this.anim('f-enemy', 'strikeR');

        let eDmg = Math.max(5, this.e.dmg - Game.p.def);
        if(Game.p.id === 'tig') eDmg = Math.max(1, eDmg - 5);
        if(Game.p.id === 'fra' && Math.random()<0.25) { eDmg = 0; this.log("Франко заблокировал удар!", "#5af"); this.float('f-player', "БЛОК", "#5af"); Snd.play('step'); }

        if(eDmg > 0) {
            Game.p.hp = Math.max(0, Game.p.hp - eDmg); this.float('f-player', `-${eDmg}`, "#f44"); this.log(`${this.e.n} атакует: -${eDmg} ОЗ.`, "#f44"); Snd.play('hit');
        }
        
        this.updateUI();
        for(let i=1;i<=4;i++) document.getElementById(`sk-${i}`).disabled = false;
        if(Game.p.hp <= 0) return setTimeout(() => this.end(false), 400);
    },
    end(win) {
        if(win) {
            Game.p.gld += this.e.gld; Game.addXp(this.e.xp); UI.toast(`Победа! +${this.e.xp}XP, +${this.e.gld}💰`, "#ff5");
            if(this.isBoss) { alert("🏆 ВЫ ЗАПЕЧАТАЛИ БЕЗДНУ! ИГРА ПРОЙДЕНА!"); Game.zIdx = 0; UI.show('scr-menu'); return; }
            UI.show('scr-adv'); Map.draw();
        } else { alert("💀 ГЕРОЙ МЕРТВ. Вы потеряли прогресс на этом этаже."); UI.show('scr-menu'); }
    }
};

// ==================== УПРАВЛЕНИЕ UI ====================
const UI = {
    show(id) { document.querySelectorAll('.screen').forEach(s => s.classList.remove('active')); document.getElementById(id).classList.add('active'); },
    toast(m, c="#fff") {
        let b = document.getElementById('toasts'), t = document.createElement('div');
        t.className = 'toast'; t.style.borderColor = c; t.innerHTML = m;
        b.appendChild(t); setTimeout(() => t.remove(), 2400);
    },
    openHeroSelect() { this.show('scr-hero-select'); this.updateHeroScreen(); },
    updateHeroScreen() {
        let h = DB.heroes[Game.hIdx]; document.getElementById('hero-show-sprite').textContent = h.spr;
        document.getElementById('hero-show-info').innerHTML = `<b style="color:var(--acc);font-size:12px">${h.n}</b><br><br><span style="color:#aaa">${h.desc}</span><br><br>❤️ ОЗ: <span style="color:var(--hp)">${h.hp}</span><br>⚔️ Атака: <span style="color:var(--gold)">${h.dmg}</span><br>🛡️ Защита: <span style="color:var(--mana)">${h.def}</span>`;
    },
    updateAdv() {
        document.getElementById('a-hp').textContent = `${Game.p.hp}/${Game.p.mhp}`; document.getElementById('a-gld').textContent = Game.p.gld;
        document.getElementById('a-floor').textContent = `${Game.zIdx+1}/5`; document.getElementById('a-picks').textContent = Game.p.picks;
        document.getElementById('a-keys').textContent = Game.p.keys;
    },
    openModal(html) { document.getElementById('modal-content').innerHTML = html; document.getElementById('modal').style.display = 'flex'; },
    closeModal() { document.getElementById('modal').style.display = 'none'; },
    fullscreen() { if(!document.fullscreenElement) document.documentElement.requestFullscreen().catch(()=>{}); else document.exitFullscreen(); }
};

// Поддержка ПК клавиатуры для теста
window.addEventListener('keydown', (e) => {
    let k = e.key.toLowerCase();
    if(document.getElementById('scr-adv').classList.contains('active')) {
        if(k==='w' || k==='arrowup') Map.move(0,-1); if(k==='s' || k==='arrowdown') Map.move(0,1);
        if(k==='a' || k==='arrowleft') Map.move(-1,0); if(k==='d' || k==='arrowright') Map.move(1,0);
    } else if(document.getElementById('scr-battle').classList.contains('active')) {
        if(k==='1') Combat.act(1); if(k==='2') Combat.act(2); if(k==='3') Combat.act(3); if(k==='4') Combat.act(4);
    }
});

UI.updateHeroScreen();
</script>
</body>
</html>
{% endraw %}
"""

@app.route('/')
def home():
    return render_template_string(GAME_HTML)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
