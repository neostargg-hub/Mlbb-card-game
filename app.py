from flask import Flask, render_template_string
import os

app = Flask(__name__)

# Использование блока raw гарантирует, что Flask не споткнется о фигурные скобки CSS и JS
GAME_HTML = """
{% raw %}
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>MLBB RPG: СИМФОНИЯ ЭЛЕМЕНТОВ v15.0</title>
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
    <style>
        :root { 
            --bg: #030308; --panel: #0a0a18; --border: #445577; 
            --acc: #ffcc00; --hp: #ff4444; --mana: #44aaff; --gold: #ffdd44;
            --dust: #aa55ff; --exp: #22cc22;
        }
        * { box-sizing: border-box; user-select: none; -webkit-user-select: none; }
        body { 
            font-family: 'Press Start 2P', cursive; background: var(--bg); color: #e0e0f0; 
            margin: 0; padding: 0; font-size: 8px; text-align: center; overflow: hidden; 
            height: 100vh; display: flex; justify-content: center; align-items: center;
        }
        #game { 
            width: 100%; max-width: 100vw; height: 100%; max-height: 100vh;
            background: radial-gradient(circle at center, #11112b 0%, #030308 100%);
            border: 4px solid var(--border); padding: 8px; position: relative; display: flex; flex-direction: column;
        }
        
        /* Полноэкранный режим */
        :fullscreen #game, :-webkit-full-screen #game { border: none; padding: 10px; }

        .screen { display: none; height: 100%; flex-direction: column; justify-content: space-between; }
        .screen.active { display: flex; animation: fade 0.3s ease-out; }
        @keyframes fade { from { opacity: 0; transform: scale(0.98); } to { opacity: 1; transform: scale(1); } }

        h1 { font-size: 16px; color: var(--acc); text-shadow: 0 0 10px var(--acc); margin: 6px 0; }
        h2 { font-size: 10px; color: #aaa; margin: 4px 0; }
        
        .btn { 
            background: linear-gradient(#25254a, #15152b); border: 3px outset #6677aa; color: #fff; padding: 12px; 
            margin: 4px 0; cursor: pointer; font-family: 'Press Start 2P', cursive; font-size: 9px; text-transform: uppercase; width: 100%;
            border-radius: 4px; box-shadow: 0 4px 0 #000; position: relative;
        }
        .btn:active { border-style: inset; transform: translateY(2px); box-shadow: 0 2px 0 #000; }
        .btn:disabled { opacity: 0.4; cursor: not-allowed; transform: none !important; box-shadow: 0 4px 0 #000 !important; }
        
        .panel { background: var(--panel); border: 2px solid var(--border); padding: 10px; border-radius: 6px; margin: 4px 0; }
        
        /* ТРЕХЗОННЫЙ РАЗДЕЛЬНЫЙ ИНТЕРФЕЙС КАРТЫ */
        .adventure-layout { display: flex; width: 100%; height: 100%; gap: 8px; align-items: center; justify-content: space-between; }
        
        .side-pad { 
            width: 22%; height: 100%; display: flex; flex-direction: column; 
            justify-content: center; gap: 8px; padding: 5px;
        }
        
        .center-viewport { 
            width: 54%; height: 100%; display: flex; flex-direction: column; 
            justify-content: space-between; flex-grow: 1;
        }

        /* Кнопки разделённого пульта движения */
        .pad-btn { 
            font-family: 'Press Start 2P', cursive; font-size: 14px; color: #fff;
            background: #1f1f3d; border: 3px outset #5566aa; border-radius: 8px;
            padding: 16px 0; width: 100%; cursor: pointer; box-shadow: 0 4px 0 #000;
        }
        .pad-btn:active { border-style: inset; background: #111124; transform: translateY(2px); box-shadow: 0 1px 0 #000; color: var(--acc); }
        .pad-btn.action-btn { background: #3d1c44; border-color: #aa55aa; font-size: 8px; padding: 12px 0; }

        /* Движок камеры */
        #viewport { 
            width: 100%; flex-grow: 1; border: 3px solid #3d3d5c; 
            background: #010103; position: relative; overflow: hidden; border-radius: 6px;
            box-shadow: inset 0 0 20px #000;
        }
        #map-container { position: absolute; transition: transform 0.15s cubic-bezier(0.1, 0.8, 0.1, 1); }
        .map-row { display: flex; }
        .tile { 
            width: 34px; height: 36px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; 
            font-size: 16px; background: #111b11; border: 1px solid #1a241a; border-radius: 2px;
        }
        .tile.wall { background: #0b0b12; color: #2d2d3d; border-color: #000; }
        .tile.fog { background: #000 !important; filter: brightness(0); border-color: #000 !important; }
        .tile.dim { filter: brightness(0.4); }

        /* Прогресс-бары */
        .bar-container { width: 100%; height: 12px; background: #111; border: 2px solid #fff; position: relative; margin: 3px 0; border-radius: 2px; }
        .bar-fill { height: 100%; transition: width 0.2s ease; }
        .bar-text { position: absolute; width: 100%; text-align: center; top: 1px; left: 0; font-size: 6px; color: #fff; text-shadow: 1px 1px #000; font-weight: bold; }

        /* Рюкзак и кузница */
        .inv-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 5px; margin: 6px 0; }
        .inv-slot { aspect-ratio: 1; background: #05050f; border: 2px solid #334; display: flex; flex-direction: column; align-items: center; justify-content: center; font-size: 18px; cursor: pointer; border-radius: 4px; position: relative; }
        .inv-slot span { position: absolute; bottom: 1px; right: 2px; font-size: 5px; color: #aaa; }
        .tier-1 { border-color: #5f5; } .tier-2 { border-color: #55f; } .tier-3 { border-color: #a3f; } .tier-4 { border-color: #fa0; box-shadow: inset 0 0 5px #fa0; }

        /* Арена */
        #battle-area { height: 130px; background: #020207; border: 3px solid #511; position: relative; border-radius: 6px; overflow: hidden; }
        .fighter { position: absolute; bottom: 15px; font-size: 45px; transition: transform 0.15s ease; width: 50px; height: 50px; display: flex; align-items: center; justify-content: center; }
        #player-sprite { left: 15%; transform: scaleX(-1); }
        #enemy-sprite { right: 15%; }
        .floating-text { position: absolute; font-size: 9px; font-weight: bold; text-shadow: 1px 1px #000; animation: floatUp 1s forwards; pointer-events: none; z-index: 100; }
        
        #battle-log { height: 75px; overflow-y: auto; background: #010103; color: #4aff4a; padding: 4px; text-align: left; border: 2px solid var(--border); font-size: 6px; line-height: 1.4; }
        #toasts { position: absolute; top: 8px; width: 100%; display: flex; flex-direction: column; align-items: center; pointer-events: none; z-index: 2000; }
        .toast { background: rgba(5,5,15,0.95); border: 2px solid var(--acc); color: #fff; padding: 8px 12px; margin-bottom: 3px; border-radius: 4px; font-size: 7px; animation: tAnim 2.2s forwards; }

        @keyframes floatUp { 0% { opacity: 1; transform: translateY(0); } 100% { opacity: 0; transform: translateY(-35px) scale(1.3); } }
        @keyframes tAnim { 0%, 100% { opacity: 0; transform: translateY(-10px); } 10%, 90% { opacity: 1; transform: translateY(0); } }
        @keyframes strikeL { 0%, 100% { left: 15%; } 50% { left: 40%; transform: scaleX(-1) scale(1.2); } }
        @keyframes strikeR { 0%, 100% { right: 15%; } 50% { right: 40%; transform: scale(1.2); } }
        .idle-anim { animation: breathe 2.5s infinite ease-in-out; }
        @keyframes breathe { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-4px); } }
    </style>
</head>
<body>
<div id="game">
    <div id="toasts"></div>

    <div id="scr-menu" class="screen active">
        <h1>MLBB RPG</h1>
        <h2>ЭПОХА ВОЗРОЖДЕНИЯ v15.0</h2>
        <div style="font-size:60px; margin: 20px 0; animation: breathe 3s infinite alternate;">🌌</div>
        <div class="panel" style="display:flex; flex-direction:column; justify-content:center; flex:1;">
            <button class="btn btn-acc" style="font-size:12px; padding:15px;" onclick="Game.start()">НОВАЯ ИГРА</button>
            <button class="btn" onclick="Game.load()">ПРОДОЛЖИТЬ АВТОСОХРАНЕНИЕ</button>
            <button class="btn" onclick="UI.show('scr-hero-select')">ВЫБОР КЛАССА ГЕРОЯ</button>
            <button class="btn" style="background:#223;" onclick="UI.toggleFullscreen()">ПОЛНЫЙ ЭКРАН 🔲</button>
        </div>
    </div>

    <div id="scr-hero-select" class="screen">
        <h1>ВЫБОР ГЕРОЯ</h1>
        <div style="display:flex; align-items:center; justify-content:space-between; margin: 10px 0;">
            <button class="btn" style="width:20%" onclick="Game.cycleHero(-1)">◀</button>
            <div id="hero-show-sprite" style="font-size:80px; width:50%; animation: breathe 2s infinite;">⚔️</div>
            <button class="btn" style="width:20%" onclick="Game.cycleHero(1)">▶</button>
        </div>
        <div id="hero-show-info" class="panel" style="text-align:left; line-height:1.5; font-size:7.5px; flex:1;"></div>
        <button class="btn btn-acc" onclick="UI.show('scr-menu')">ПОДТВЕРДИТЬ</button>
    </div>

    <div id="scr-adv" class="screen">
        <div class="adventure-layout">
            
            <div class="side-pad">
                <button class="pad-btn" onclick="Map.move(0, -1)">▲</button>
                <button class="pad-btn" onclick="Map.move(-1, 0)">◀</button>
                <button class="pad-btn" onclick="Map.move(0, 1)">▼</button>
                <button class="pad-btn action-btn" onclick="Camp.open()">🎒 СУМКА</button>
            </div>
            
            <div class="center-viewport">
                <div class="panel" style="display:grid; grid-template-columns: 1fr 1fr 1fr; font-size:7px; padding:6px; margin:0 0 4px 0; text-align:center;">
                    <div>❤️ HP: <span id="a-hp" style="color:var(--hp)"></span></div>
                    <div>💰 GOLD: <span id="a-gld" style="color:var(--gold)"></span></div>
                    <div>🎯 ЭТАЖ: <span id="a-floor" style="color:var(--mana)"></span></div>
                </div>
                <div id="viewport">
                    <div id="map-container"></div>
                </div>
                <div class="panel" style="padding:4px; font-size:5.5px; color:#aaa; margin:4px 0 0 0; display:flex; justify-content:space-between;">
                    <span>Кирки: <span id="a-picks" style="color:#fff"></span> ⛏️ | Ключи: <span id="a-keys" style="color:#fff"></span> 🗝️</span>
                    <span>Квесты: <span id="a-quests" style="color:var(--acc)"></span></span>
                </div>
            </div>
            
            <div class="side-pad">
                <button class="pad-btn" onclick="Map.move(0, -1)">▲</button>
                <button class="pad-btn" onclick="Map.move(1, 0)">▶</button>
                <button class="pad-btn" onclick="Map.move(0, 1)">▼</button>
                <button class="pad-btn action-btn" style="background:#441111; border-color:#993333;" onclick="UI.show('scr-menu')">🚪 МЕНЮ</button>
            </div>
            
        </div>
    </div>

    <div id="scr-camp" class="screen">
        <h1>СНАРЯЖЕНИЕ И КУЗНИЦА</h1>
        <div class="panel" style="text-align:left; font-size:7px; display:grid; grid-template-columns: 1fr 1fr; gap:8px;">
            <div>
                <p>КЛАСС: <span id="c-name" style="color:var(--mana)"></span> (УР. <span id="c-lvl"></span>)</p>
                <p>АТАКА: <span id="c-dmg" style="color:var(--hp)"></span> | ЗАЩИТА: <span id="c-def" style="color:var(--mana)"></span></p>
                <div class="bar-container" style="height:8px; margin-top:4px;"><div id="c-exp-bar" class="bar-fill" style="background:var(--dust)"></div></div>
            </div>
            <div>
                <p style="color:var(--acc)">Свободные очки: <span id="c-sp">0</span></p>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:2px;">
                    <button class="btn" style="padding:5px; font-size:6px;" onclick="Game.distributeStat('dmg')">+⚔️ Сила</button>
                    <button class="btn" style="padding:5px; font-size:6px;" onclick="Game.distributeStat('hp')">+❤️ Жизнь</button>
                </div>
            </div>
        </div>
        <div class="panel">
            <div style="display:flex; justify-content:space-between; font-size:7px; margin-bottom:4px;">
                <span>ТВОЯ СУМКА</span>
                <span>Пыль: <span id="c-dust" style="color:var(--dust)">0</span>💎</span>
            </div>
            <div style="display:flex; gap:6px; justify-content:center; margin-bottom:8px;">
                <div class="inv-slot" id="eq-w" style="width:45%; font-size:7px;" onclick="Camp.unequip('w')">⚔️ Оружие</div>
                <div class="inv-slot" id="eq-a" style="width:45%; font-size:7px;" onclick="Camp.unequip('a')">🛡️ Доспех</div>
            </div>
            <div class="inv-grid" id="inventory-container"></div>
        </div>
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:4px;">
            <button class="btn" style="color:var(--dust)" onclick="Camp.craft()">🔨 КУЗНИЦА (25 Пыли)</button>
            <button class="btn" style="color:var(--hp)" onclick="Camp.buyPotion()">🧪 КУПИТЬ ЗЕЛЬЕ (25💰)</button>
        </div>
        <button class="btn" onclick="UI.show('scr-adv')">ВЕРНУТЬСЯ К ИССЛЕДОВАНИЮ</button>
    </div>

    <div id="scr-battle" class="screen">
        <h1 style="color:var(--hp);">АРЕНА БЕЗДНЫ</h1>
        <div id="battle-area">
            <div id="player-sprite" class="fighter idle-anim">🏃‍♂️</div>
            <div id="enemy-sprite" class="fighter idle-anim">👾</div>
        </div>
        <div class="panel" style="padding:4px; margin:2px 0;">
            <div style="display:flex; justify-content:space-between; font-size:6px; margin-bottom:2px;">
                <span>МОЁ ОЗ: <span id="b-php-txt"></span></span>
                <span>ВРАГ ОЗ: <span id="b-ehp-txt"></span></span>
            </div>
            <div class="bar-container"><div id="b-php" class="bar-fill" style="background:#22cc22;"></div></div>
            <div class="bar-container"><div id="b-ehp" class="bar-fill" style="background:var(--hp);"></div></div>
            
            <div style="display:flex; justify-content:space-between; font-size:6px; margin-top:4px;">
                <div class="bar-container" style="width:45%; height:6px;"><div id="atb-p" class="bar-fill" style="background:var(--mana);"></div></div>
                <div class="bar-container" style="width:45%; height:6px;"><div id="atb-e" class="bar-fill" style="background:var(--stamina);"></div></div>
            </div>
        </div>
        <div id="battle-log" class="panel"></div>
        <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:2px;">
            <button class="btn" id="sk-1" onclick="Combat.action(1)">⚔️ Удар</button>
            <button class="btn" id="sk-2" onclick="Combat.action(2)">✨ Скилл</button>
            <button class="btn" id="sk-3" onclick="Combat.action(3)">🛡️ Щит</button>
            <button class="btn btn-acc" id="sk-4" onclick="Combat.action(4)">☄️ УЛЬТ</button>
        </div>
    </div>

    <div id="scr-quests" class="screen">
        <h1>ЖУРНАЛ ЗАДАНИЙ МОНИИ</h1>
        <div class="panel" id="quest-list" style="flex:1; overflow-y:auto; text-align:left; font-size:8px; line-height:1.6;"></div>
        <button class="btn" onclick="UI.show('scr-adv')">НАЗАД К КАРТЕ</button>
    </div>

</div>

<script>
// ==================== ЗВУКОВОЙ ПРОЦЕДУРНЫЙ ДВИЖОК ====================
const AudioEngine = {
    ctx: null,
    init() { if(!this.ctx) this.ctx = new (window.AudioContext || window.webkitAudioContext)(); },
    play(type) {
        this.init(); if(!this.ctx) return;
        const o = this.ctx.createOscillator(), g = this.ctx.createGain();
        o.connect(g); g.connect(this.ctx.destination);
        const t = this.ctx.currentTime;
        if(type==='step') { o.type='triangle'; o.frequency.setValueAtTime(90, t); g.gain.setValueAtTime(0.06, t); g.gain.linearRampToValueAtTime(0, t+0.05); o.start(t); o.stop(t+0.05); }
        else if(type==='hit') { o.type='sawtooth'; o.frequency.setValueAtTime(140, t); o.frequency.linearRampToValueAtTime(30, t+0.1); g.gain.setValueAtTime(0.2, t); g.gain.linearRampToValueAtTime(0, t+0.1); o.start(t); o.stop(t+0.1); }
        else if(type==='loot') { o.type='sine'; o.frequency.setValueAtTime(440, t); o.frequency.setValueAtTime(660, t+0.08); g.gain.setValueAtTime(0.15, t); g.gain.linearRampToValueAtTime(0, t+0.2); o.start(t); o.stop(t+0.2); }
        else if(type==='ult') { o.type='square'; o.frequency.setValueAtTime(100, t); o.frequency.linearRampToValueAtTime(800, t+0.4); g.gain.setValueAtTime(0.3, t); g.gain.linearRampToValueAtTime(0, t+0.4); o.start(t); o.stop(t+0.4); }
    }
};

// ==================== БАЗА ДАННЫХ RPG ====================
const DB = {
    heroes: [
        { id:'alu', n:'АЛУКАРД', spr:'⚔️', hp:250, dmg:34, def:12, desc:'Боец. Пассивный вампиризм: возвращает 25% здоровья от ударов мечом.' },
        { id:'mia', n:'МИЯ', spr:'🏹', hp:180, dmg:42, def:7, desc:'Стрелок. Шанс крита: 30% вероятность нанести х2 урон стрелой.' },
        { id:'tig', n:'ТИГРИЛ', spr:'🛡️', hp:350, dmg:24, def:24, desc:'Танк. Абсолютный Бастион: Снижает весь получаемый урон на 4 единицы.' },
        { id:'gus', n:'ГОССЕН', spr:'🗡️', hp:200, dmg:38, def:9, desc:'Убийца. Скоростное комбо: Кулдауны на навыки снижены.' }
    ],
    enemies: [
        { n:"Миньон Бездны", spr:"👺", hp:110, dmg:16, def:6, xp:30, gld:20 },
        { n:"Адский Волк", spr:"🐺", hp:150, dmg:22, def:10, xp:45, gld:30 },
        { n:"Голем Скал", spr:"🪨", hp:320, dmg:34, def:25, xp:75, gld:55 },
        { n:"ТАМУЗ [ГЕНЕРАЛ]", spr:"🔥", hp:1200, dmg:70, def:45, xp:999, gld:500, isBoss: true }
    ],
    lootTable: [
        { type:'w', name:'Меч Легиона', icon:'🗡️', stat:'dmg', v:12, rare:'common' },
        { type:'w', name:'Клинок Отчаяния', icon:'⚔️', stat:'dmg', v:42, rare:'legend' },
        { type:'a', name:'Кираса Воина', icon:'👕', stat:'def', v:10, rare:'common' },
        { type:'a', name:'Бессмертие', icon:'🛡️', stat:'def', v:35, rare:'legend' }
    ]
};

// ГЕНЕРАТОР ПРЕДМЕТОВ
function generateItem(zoneLvl) {
    let base = DB.lootTable[Math.floor(Math.random()*DB.lootTable.length)];
    let modifier = 1 + Math.floor(Math.random()*5) + (zoneLvl * 6);
    return { ...base, v: base.v + modifier, n: `Модерн. ${base.name}`, upg: 0 };
}

// ==================== ЛОГИКА СОСТОЯНИЯ ГЕРОЯ ====================
let Game = {
    hIdx: 0, zIdx: 0, p: null, quests: [],
    start() {
        this.zIdx = 0; let h = DB.heroes[this.hIdx];
        this.p = {
            id: h.id, n: h.n, spr: h.spr, lvl: 1, xp: 0, nxp: 100, sp: 0,
            bhp: h.hp, mhp: h.hp, hp: h.hp, bdmg: h.dmg, dmg: h.dmg, bdef: h.def, def: h.def,
            gld: 150, dust: 20, keys: 1, picks: 3, eq: { w: null, a: null }, inv: []
        };
        this.quests = [
            { id: 1, name: "Очистка ярусов Бездны", cur: 0, max: 3, type: "kill", gld: 60, done: false },
            { id: 2, name: "Охотник за сундуками", cur: 0, max: 2, type: "loot", gld: 50, done: false }
        ];
        Map.generate(); UI.show('scr-adv'); UI.updateAdv(); UI.toast("Вы спустились в Братство Рассвета!");
    },
    cycleHero(d) { this.hIdx = (this.hIdx + d + DB.heroes.length) % DB.heroes.length; UI.updateHeroScreen(); },
    calcStats() {
        let p = this.p; p.mhp = p.bhp; p.dmg = p.bdmg; p.def = p.bdef;
        if(p.eq.w) p.dmg += p.eq.w.v; if(p.eq.a) p.def += p.eq.a.v;
        if(p.hp > p.mhp) p.hp = p.mhp;
    },
    distributeStat(type) {
        if(this.p.sp <= 0) return;
        this.p.sp--;
        if(type==='dmg') this.p.bdmg += 3;
        if(type==='hp') { this.p.bhp += 25; this.p.hp += 25; }
        this.calcStats(); Camp.open(); AudioEngine.play('loot');
    },
    addXp(amt) {
        this.p.xp += amt;
        if(this.p.xp >= this.p.nxp) {
            this.p.xp -= this.p.nxp; this.p.lvl++; this.p.sp += 2; this.p.nxp = Math.floor(this.p.nxp * 1.5);
            this.p.bhp += 15; this.calcStats(); this.p.hp = this.p.mhp;
            UI.toast(`✨ УРОВЕНЬ ПОВЫШЕН: ${this.p.lvl}!`, "#33ff33"); AudioEngine.play('ult');
        }
    },
    checkQuests(type) {
        this.quests.forEach(q => {
            if(!q.done && q.type === type) {
                q.cur++; if(q.cur >= q.max) { q.done = true; this.p.gld += q.gld; UI.toast(`📜 Задание "${q.name}" выполнено! +${q.gld}💰`, "var(--gold)"); }
            }
        });
    },
    save() { localStorage.setItem('mlbb_v15_save', JSON.stringify({ zIdx: this.zIdx, p: this.p, quests: this.quests })); },
    load() {
        let raw = localStorage.getItem('mlbb_v15_save'); if(!raw) return UI.toast("Сохранение не найдено", "#ff4444");
        let d = JSON.parse(raw); this.zIdx = d.zIdx; this.p = d.p; this.quests = d.quests;
        this.calcStats(); Map.generate(); UI.show('scr-adv'); UI.updateAdv(); UI.toast("Прогресс успешно восстановлен!");
    }
};

// ==================== ДВИЖОК КАРТЫ (50х50) ====================
const Map = {
    w: 40, h: 40, grid: [], px: 5, py: 5, fog: [],
    generate() {
        this.grid = Array(this.h).fill().map(() => Array(this.w).fill(1));
        let cx = 20, cy = 20; this.px = cx; this.py = cy; this.grid[cy][cx] = 0;
        
        for(let i=0; i<900; i++) {
            let dir = [{x:0,y:1},{x:0,y:-1},{x:1,y:0},{x:-1,y:0}][Math.floor(Math.random()*4)];
            if(cx+dir.x>1 && cx+dir.x<this.w-2 && cy+dir.y>1 && cy+dir.y<this.h-2) { cx+=dir.x; cy+=dir.y; this.grid[cy][cx]=0; }
        }
        let floors = [];
        for(let y=1; y<this.h-1; y++) for(let x=1; x<this.w-1; x++) if(this.grid[y][x]===0 && (x!==this.px || y!==this.py)) floors.push({x,y});
        floors.sort(() => Math.random() - 0.5);

        if(floors.length > 0) this.grid[floors.pop().y][floors.pop().x] = Game.zIdx === 4 ? 6 : 5; // 5-Выход, 6-Босс
        let nE = 20, nC = 12;
        while(floors.length > 0 && nE-- > 0) this.grid[floors.pop().y][floors.pop().x] = 2; // Моб
        while(floors.length > 0 && nC-- > 0) this.grid[floors.pop().y][floors.pop().x] = Math.random()<0.3 ? 8 : 4; // Сундук/Ключ
        while(floors.length > 0 && Math.random()<0.04) this.grid[floors.pop().y][floors.pop().x] = 9; // Торговец
        while(floors.length > 0 && Math.random()<0.04) this.grid[floors.pop().y][floors.pop().x] = 7; // Фонтан

        this.fog = Array(this.h).fill().map(() => Array(this.w).fill(true));
        this.updateFog(); this.draw();
    },
    updateFog() {
        let r = 4;
        for(let y=this.py-r; y<=this.py+r; y++) {
            for(let x=this.px-r; x<=this.px+r; x++) {
                if(y>=0 && y<this.h && x>=0 && x<this.w) { if((x-this.px)**2 + (y-this.py)**2 <= r**2) this.fog[y][x]=false; }
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
                    else if(v===1) cls += ' wall';
                    else if(v===2) txt = '👾';
                    else if(v===4) txt = '🧰';
                    else if(v===5) txt = '🪜';
                    else if(v===6) txt = '🔥';
                    else if(v===7) txt = ' fountains  fountains ⛲';
                    else if(v===8) txt = '🗝️';
                    else if(v===9) txt = '🛒';
                    if(Math.max(Math.abs(x-this.px), Math.abs(y-this.py)) >= 3) cls += ' dim';
                }
                html += `<div class="${cls}" onclick="Map.click(${x},${y})">${txt}</div>`;
            }
            html += '</div>';
        }
        cont.innerHTML = html;
        let ts = 36, vp = document.getElementById('viewport');
        let cx = (vp.clientWidth / 2) - (this.px * ts) - (ts/2);
        let cy = (vp.clientHeight / 2) - (this.py * ts) - (ts/2);
        cont.style.transform = `translate(${cx}px, ${cy}px)`;
    },
    click(x, y) {
        if(Math.abs(x-this.px)<=1 && Math.abs(y-this.py)<=1 && this.grid[y][x]===1 && Game.p.picks>0) {
            Game.p.picks--; this.grid[y][x]=0; AudioEngine.play('hit'); this.updateFog(); this.draw(); UI.updateAdv();
        }
    },
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
                let it = generateItem(Game.zIdx); Game.p.inv.push(it); UI.toast(`Найдено: ${it.n}!`, "var(--acc)");
                Game.checkQuests('loot');
            } else { UI.toast("Нужен ключ! 🗝️", "#ff4444"); this.px-=dx; this.py-=dy; }
        }
        else if(tile === 8) { Game.p.keys++; this.grid[ny][nx]=0; AudioEngine.play('loot'); UI.toast("Подобран ключ!"); }
        else if(tile === 7) { Game.p.hp=Game.p.mhp; this.grid[ny][nx]=0; AudioEngine.play('loot'); UI.toast("Живительный источник исцелил раны!", "#5f5"); }
        else if(tile === 9) {
            if(Game.p.gld >= 80) { Game.p.gld -= 80; this.grid[ny][nx]=0; let it = generateItem(Game.zIdx+1); Game.p.inv.push(it); UI.toast(`Куплено: ${it.n}`, "var(--dust)"); }
            else { UI.toast("Не хватает золота (80💰)", "#ff4444"); this.px-=dx; this.py-=dy; }
        }
        else if(tile === 5) {
            Game.zIdx++; Game.p.picks += 2; UI.toast(`Спуск на этаж ${Game.zIdx+1}!`); this.generate(); Game.save(); return;
        }
        this.draw(); UI.updateAdv();
    }
};

// ==================== ИНВЕНТАРЬ И ОПЦИИ ЛАГЕРЯ ====================
const Camp = {
    open() {
        Game.calcStats();
        document.getElementById('c-name').textContent = Game.p.n;
        document.getElementById('c-lvl').textContent = Game.p.lvl;
        document.getElementById('c-xp-txt').textContent = `${Game.p.xp}/${Game.p.nxp}`;
        document.getElementById('c-exp-bar').style.width = `${(Game.p.xp/Game.p.nxp)*100}%`;
        document.getElementById('c-hp').textContent = `${Game.p.hp}/${Game.p.mhp}`;
        document.getElementById('c-dmg').textContent = Game.p.dmg;
        document.getElementById('c-def').textContent = Game.p.def;
        document.getElementById('c-sp').textContent = Game.p.sp;
        document.getElementById('c-dust').textContent = Game.p.dust;
        document.getElementById('c-inv-c').textContent = Game.p.inv.length;

        document.getElementById('eq-w').innerHTML = Game.p.eq.w ? `${Game.p.eq.w.i} +${Game.p.eq.w.v}` : '⚔️ Оружие';
        document.getElementById('eq-a').innerHTML = Game.p.eq.a ? `${Game.p.eq.a.i} +${Game.p.eq.a.v}` : '🛡️ Доспех';

        const container = document.getElementById('inventory-container'); container.innerHTML = '';
        Game.p.inv.forEach((it, i) => {
            let slot = document.createElement('div'); slot.className = 'inv-slot';
            slot.innerHTML = `${it.i}<span style="font-size:4px;">+${it.v}</span>`;
            slot.onclick = () => this.showItem(i); container.appendChild(slot);
        });
        UI.show('scr-camp');
    },
    showItem(idx) {
        let it = Game.p.inv[idx];
        let html = `
            <h2>${it.i} ${it.n}</h2>
            <p style="font-size:12px; color:var(--acc); margin:10px 0;">Мощь модификатора: +${it.v}</p>
            <button class="btn" style="background:#141;" onclick="Camp.equip(${idx})">НАДЕТЬ</button>
            <button class="btn" style="background:#411;" onclick="Camp.scrap(${idx})">РАЗОБРАТЬ (+8💎)</button>
            <button class="btn" onclick="UI.closeModal()">ОТМЕНА</button>
        `;
        UI.openModal(html);
    },
    equip(idx) {
        UI.closeModal(); let it = Game.p.inv[idx];
        if(Game.p.eq[it.type]) Game.p.inv.push(Game.p.eq[it.type]);
        Game.p.eq[it.type] = it; Game.p.inv.splice(idx,1); this.open(); UI.toast("Предмет экипирован!");
    },
    scrap(idx) { Game.p.inv.splice(idx,1); Game.p.dust += 8; UI.closeModal(); this.open(); UI.toast("Разобрано на пыль! +8💎"); },
    unequip(type) { if(Game.p.eq[type]) { Game.p.inv.push(Game.p.eq[type]); Game.p.eq[type] = null; this.open(); } },
    craft() {
        if(Game.p.dust < 25) return UI.toast("Мало пыли для кузни!", "#f44");
        if(Game.p.inv.length >= 16) return UI.toast("Рюкзак полон!", "#f44");
        Game.p.dust -= 25; let it = generateItem(Game.zIdx); Game.p.inv.push(it); this.open(); UI.toast(`Выковано: ${it.n}`);
    },
    buyPotion() {
        if(Game.p.gld < 25) return UI.toast("Не хватает золота!", "#f44");
        Game.p.gld -= 25; Game.p.hp = Game.p.mhp; this.open(); UI.toast("Здоровье восполнено!", "#5f5");
    }
};

// ==================== БОЕВАЯ СИСТЕМА ДИНАМИКИ ХОДОВ ====================
const Combat = {
    e: null, atbP: 0, atbE: 0, loop: null, turnReady: false, isBoss: false,
    start(bossMode) {
        this.isBoss = bossMode; let pool = DB.enemies;
        let baseE = bossMode ? pool[3] : pool[Math.floor(Math.random()*3)];
        let scale = 1 + (Game.zIdx * 0.4);
        this.e = { ...baseE, maxHp: Math.floor(baseE.hp*scale), hp: Math.floor(baseE.hp*scale), dmg: Math.floor(baseE.dmg*scale), def: Math.floor(baseE.def*scale) };
        
        this.atbP = 0; this.atbE = 0; this.turnReady = false;
        document.getElementById('bt-player-name').textContent = Game.p.n;
        document.getElementById('bt-enemy-name').textContent = `${this.e.n} [Этаж ${Game.zIdx+1}]`;
        document.getElementById('battle-log').innerHTML = '';
        
        UI.show('scr-battle'); this.log(`Вы встретили опасного врага: ${this.e.n}`, "var(--acc)");
        this.updateUI();
        this.loop = setInterval(() => this.tick(), 60);
    },
    updateUI() {
        document.getElementById('b-php-txt').textContent = `${Game.p.hp}/${Game.p.mhp}`;
        document.getElementById('b-php').style.width = `${(Game.p.hp/Game.p.mhp)*100}%`;
        document.getElementById('b-ehp-txt').textContent = `${this.e.hp}/${this.e.maxHp}`;
        document.getElementById('b-ehp').style.width = `${(this.e.hp/this.e.maxHp)*100}%`;
        document.getElementById('atb-p').style.width = `${this.atbP}%`;
        document.getElementById('atb-e').style.width = `${this.atbE}%`;

        let canAct = this.turnReady && this.atbP >= 100;
        document.getElementById('sk-1').disabled = !canAct;
        document.getElementById('sk-2').disabled = !canAct;
        document.getElementById('sk-3').disabled = !canAct;
        document.getElementById('sk-4').disabled = !canAct;
    },
    tick() {
        if(this.turnReady || Game.p.hp <= 0 || this.e.hp <= 0) return;
        this.atbP += 6; this.atbE += 5; // Симуляция накопления шкал скорости
        if(this.atbP >= 100) { this.atbP = 100; this.turnReady = true; }
        else if(this.atbE >= 100) { this.atbE = 100; this.turnReady = true; setTimeout(() => this.enemyAct(), 400); }
        this.updateUI();
    },
    float(id, txt, c="#fff") {
        let el = document.getElementById(id); let f = document.createElement('div');
        f.className = 'floating-text'; f.style.color = c; f.textContent = txt;
        f.style.left = (Math.random()*20+25)+'%'; el.parentElement.appendChild(f); setTimeout(()=>f.remove(), 1000);
    },
    log(m, c="#aaa") { let l = document.getElementById('battle-log'); l.innerHTML += `<div>> ${m}</div>`; l.scrollTop = l.scrollHeight; },
    action(type) {
        if(!this.turnReady || this.atbP < 100) return;
        let dmg = Game.p.dmg;
        
        // Спецэффект удара
        document.getElementById('player-sprite').style.transform = 'translateX(40px) scaleX(-1)';
        setTimeout(() => document.getElementById('player-sprite').style.transform = 'scaleX(-1)', 150);

        if(type === 1) {
            let final = Math.max(3, dmg - this.e.def); this.e.hp = Math.max(0, this.e.hp - final);
            if(Game.p.id === 'alu') { let v = Math.floor(final*0.25); Game.p.hp = Math.min(Game.p.mhp, Game.p.hp+v); this.float('player-sprite', `+${v}`, "#2c2"); }
            this.float('enemy-sprite', `-${final}`); this.log(`Обычный выпад мечом: -${final} ОЗ врагу.`); AudioEngine.play('hit');
        } else if(type === 2) {
            let final = Math.floor(dmg * 1.8); this.e.hp = Math.max(0, this.e.hp - final);
            this.float('enemy-sprite', `-${final}!`, "var(--mana)"); this.log(`Использован Навык класса: нанес ${final} урона.`); AudioEngine.play('skill');
        } else if(type === 3) {
            let shield = Math.floor(Game.p.mhp * 0.25); Game.p.hp = Math.min(Game.p.mhp, Game.p.hp + shield);
            this.float('player-sprite', `+${shield}`, "#55ff55"); this.log(`Священный щит восстановил +${shield} ОЗ.`); AudioEngine.play('loot');
        } else if(type === 4) {
            let final = Math.floor(dmg * 3.6); this.e.hp = Math.max(0, this.e.hp - final);
            this.float('enemy-sprite', `КРИТ! ${final}`, "var(--hp)"); this.log(`🔥 УЛЬТИМЕЙТ РЫЦАРЯ: сокрушил врага на -${final} ОЗ!`); AudioEngine.play('ult');
        }

        this.atbP = 0; this.turnReady = false; this.updateUI();
        if(this.e.hp <= 0) return setTimeout(() => this.end(true), 400);
    },
    enemyAct() {
        if(this.e.hp <= 0 || Game.p.hp <= 0) return;
        document.getElementById('enemy-sprite').style.transform = 'translateX(-40px)';
        setTimeout(() => document.getElementById('enemy-sprite').style.transform = 'none', 150);

        let eDmg = Math.max(2, this.e.dmg - Game.p.def);
        if(Game.p.id === 'tig') eDmg = Math.max(1, eDmg - 4);

        Game.p.hp = Math.max(0, Game.p.hp - eDmg);
        this.float('player-sprite', `-${eDmg}`, "#f44"); this.log(`${this.e.n} бьет в ответ: нанес -${eDmg} ОЗ.`, "#ff5555");
        AudioEngine.play('hit');

        this.atbE = 0; this.turnReady = false; this.updateUI();
        if(Game.p.hp <= 0) return setTimeout(() => this.end(false), 400);
    },
    end(win) {
        clearInterval(this.loop);
        if(win) {
            Game.p.gld += this.e.gld; Game.addXp(this.e.xp);
            UI.toast(`Победа! +${this.e.xp}XP, +${this.e.gld}💰`, "#ff5");
            Game.checkQuests('kill');
            if(this.isBoss) {
                alert("🏆 ПОБЕДА! Генерал бездны повержен, тучи над Монией рассеялись! Вы прошли игру!");
                Game.zIdx = 0; UI.show('scr-menu'); return;
            }
            UI.show('scr-adv'); Map.draw();
        } else {
            alert("💀 Вы пали в бою. Душа героя возвращается в лобби."); UI.show('scr-menu');
        }
    }
};

// ==================== УПРАВЛЕНИЕ И ИНТЕРФЕЙС UI ====================
const UI = {
    show(id) { document.querySelectorAll('.screen').forEach(s => s.classList.remove('active')); document.getElementById(id).classList.add('active'); if(id==='scr-quests') this.updateQuests(); },
    updateHeroScreen() {
        let h = DB.heroes[Game.hIdx]; document.getElementById('hero-show-sprite').textContent = h.spr;
        document.getElementById('hero-show-info').innerHTML = `<b style="font-size:11px;color:var(--acc);">${h.n}</b><br><br>${h.desc}<br><br>❤️ Стартовое ОЗ: ${h.hp}<br>⚔️ Стартовая Атака: ${h.dmg}<br>🛡️ Стартовая Защита: ${h.def}`;
    },
    updateAdv() {
        document.getElementById('a-hp').textContent = `${Game.p.hp}/${Game.p.mhp}`;
        document.getElementById('a-gld').textContent = Game.p.gld; document.getElementById('a-floor').textContent = `${Game.zIdx+1}/5`;
        document.getElementById('a-picks').textContent = Game.p.picks; document.getElementById('a-keys').textContent = Game.p.keys;
        document.getElementById('a-quests').textContent = `${Game.quests.filter(q=>!q.done).length} шт`;
    },
    updateQuests() {
        const list = document.getElementById('quest-list'); list.innerHTML = '';
        Game.quests.forEach(q => {
            list.innerHTML += `<div style="margin-bottom:6px; color:${q.done?'#555':'#fff'}">${q.done?'✅':'📜'} <b>${q.name}</b> (${q.cur}/${q.max})<br><span style="color:var(--gold)">Награда: +${q.gld} золота</span></div>`;
        });
    },
    openModal(html) { document.getElementById('modal-body').innerHTML = html; document.getElementById('modal').style.display = 'flex'; },
    closeModal() { document.getElementById('modal').style.display = 'none'; },
    toggleFullscreen() { if(!document.fullscreenElement) document.documentElement.requestFullscreen().catch(()=>{}); else document.exitFullscreen(); }
};

// Хоткеи для ПК
window.addEventListener('keydown', (e) => {
    let k = e.key.toLowerCase();
    if(document.getElementById('scr-adv').classList.contains('active')) {
        if(k==='w' || k==='arrowup' || k==='ц') Map.move(0,-1); if(k==='s' || k==='arrowdown' || k==='ы') Map.move(0,1);
        if(k==='a' || k==='arrowleft' || k==='ф') Map.move(-1,0); if(k==='d' || k==='arrowright' || k==='в') Map.move(1,0);
    } else if(document.getElementById('scr-battle').classList.contains('active')) {
        if(k==='1') Combat.action(1); if(k==='2') Combat.action(2); if(k==='3') Combat.action(3); if(k==='4') Combat.action(4);
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
    # Автоматическое считывание портов для стабильной сборки на Render
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
