<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>MLBB RPG: Эпоха Возрождения ULTIMATE</title>
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
    <style>
        :root { 
            --bg: #030308; --panel: #0a0a18; --border: #445577; 
            --acc: #ffcc00; --hp: #ff4444; --mana: #44aaff; --gold: #ffdd44;
            --rarity: #a5f;
        }
        * { box-sizing: border-box; user-select: none; }
        body { 
            font-family: 'Press Start 2P', cursive; background: var(--bg); color: #e0e0f0; 
            margin: 0; padding: 0; font-size: 10px; text-align: center; overflow: hidden; 
            height: 100vh; display: flex; justify-content: center; align-items: center;
        }
        #game { 
            width: 100%; max-width: 800px; height: 100%; max-height: 100vh;
            background: radial-gradient(circle at center, #111126 0%, #030308 100%);
            border: 6px solid var(--border); box-shadow: 0 0 50px rgba(80,60,255,0.5);
            padding: 12px; position: relative; display: flex; flex-direction: column;
        }
        .screen { display: none; height: 100%; flex-direction: column; overflow-y: auto; padding-right: 4px; }
        .screen.active { display: flex; animation: fade 0.3s ease-out; }
        @keyframes fade { from { opacity: 0; transform: scale(0.98); } to { opacity: 1; transform: scale(1); } }

        h1 { font-size: 18px; color: var(--acc); text-shadow: 0 0 10px var(--acc); margin: 10px 0; }
        h2 { font-size: 11px; color: #aaa; margin: 5px 0; }
        
        .btn { 
            background: linear-gradient(#25254a, #15152b); border: 3px outset #6677aa; color: #fff; padding: 12px; 
            margin: 4px 0; cursor: pointer; font-family: 'Press Start 2P', cursive; font-size: 9px; text-transform: uppercase; width: 100%;
            border-radius: 4px; box-shadow: 0 4px 0 #000; position: relative;
        }
        .btn:parent { outline: none; }
        .btn:active { border-style: inset; transform: translateY(3px); box-shadow: 0 1px 0 #000; }
        .btn:disabled { opacity: 0.4; cursor: not-allowed; transform: none !important; box-shadow: 0 4px 0 #000 !important; border-style: outset !important; }
        
        .panel { background: var(--panel); border: 3px solid var(--border); padding: 12px; border-radius: 6px; margin: 6px 0; }
        
        /* Сетка карты */
        #map-grid { 
            display: grid; grid-template-columns: repeat(11, 1fr); gap: 3px; 
            background: #05050a; padding: 8px; border: 4px solid #223; flex: 1; 
            align-content: center; justify-content: center; border-radius: 6px;
        }
        .tile { 
            aspect-ratio: 1; display: flex; align-items: center; justify-content: center; 
            font-size: 16px; background: #111511; border: 1px solid #223; cursor: pointer; 
            border-radius: 3px; transition: background 0.1s;
        }
        .tile.wall { background: #0c0c12; color: #334; cursor: not-allowed; }
        .tile.visible { filter: brightness(1); }
        .tile.fog { filter: brightness(0.2); background: #000 !important; }
        
        /* Боевой экран */
        #battle-area { height: 160px; background: #05050d; border: 4px solid #400; position: relative; border-radius: 6px; overflow: hidden; margin-bottom: 6px;}
        .fighter { position: absolute; bottom: 20px; font-size: 50px; transition: all 0.2s ease; width: 60px; height: 60px; display:flex; align-items:center; justify-content:center; }
        #player-sprite { left: 15%; }
        #enemy-sprite { right: 15%; transform: scaleX(-1); }
        .hp-bar-container { width: 100px; height: 10px; background: #300; border: 1px solid #fff; position: absolute; bottom: 85px; border-radius: 2px;}
        .hp-bar { height: 100%; background: var(--hp); width: 100%; transition: width 0.2s; }
        
        /* Инвентарь */
        .inv-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 6px; margin-top: 8px; }
        .inv-slot { aspect-ratio: 1; background: #05050f; border: 2px dashed #445; display: flex; align-items: center; justify-content: center; font-size: 20px; cursor: pointer; border-radius: 4px; }
        .inv-slot:hover { border-color: var(--acc); }

        /* Лог битвы */
        #battle-log { height: 100px; overflow-y: auto; font-size: 8px; text-align: left; line-height: 1.4; background: #020205; }
        
        /* Скроллбар */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: var(--panel); }
        ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
    </style>
</head>
<body>
<div id="game">
    <div id="toasts" style="position:absolute;top:10px;left:12px;right:12px;z-index:1000;display:flex;flex-direction:column;gap:4px;pointer-events:none;"></div>

    <div id="scr-menu" class="screen active">
        <h1>MLBB RPG</h1>
        <h2>ЭПОХА ВОЗРОЖДЕНИЯ ULTIMATE</h2>
        <div style="font-size:70px;margin:15px 0; animation: pulse 2s infinite alternate;">🌌</div>
        <div class="panel" style="display:flex; flex-direction:column; flex:1; justify-content: center;">
            <button class="btn" style="font-size:12px;padding:16px;color:var(--acc);" onclick="Game.newGame()">НОВАЯ ИГРА</button>
            <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:4px; margin: 4px 0;">
                <button class="btn" onclick="Game.load(1)">Слот 1</button>
                <button class="btn" onclick="Game.load(2)">Слот 2</button>
                <button class="btn" onclick="Game.load(3)">Слот 3</button>
            </div>
            <button class="btn" onclick="UI.openHeroSelect()">ВЫБОР ГЕРОЯ</button>
            <button class="btn" onclick="UI.show('scr-lore')">ЛОР МИРА</button>
        </div>
    </div>

    <div id="scr-hero" class="screen">
        <h1>ВЫБОР ГЕРОЯ</h1>
        <div style="display:flex; align-items:center; justify-content:space-between; margin: 10px 0;">
            <button class="btn" style="width:25%" onclick="Game.prevHero()">←</button>
            <div id="hero-sprite" style="font-size:70px; width:50%;">⚔️</div>
            <button class="btn" style="width:25%" onclick="Game.nextHero()">→</button>
        </div>
        <div id="hero-info" class="panel" style="text-align:left; line-height:1.6; flex:1;"></div>
        <button class="btn" style="color:var(--acc)" onclick="UI.show('scr-menu')">ПОДТВЕРДИТЬ И ВЕРНУТЬСЯ</button>
    </div>

    <div id="scr-lore" class="screen">
        <h1>ЭПОХА ВОЗРОЖДЕНИЯ</h1>
        <div class="panel" style="flex:1;overflow-y:auto;text-align:left;line-height:1.7; font-size:8px;">
            <p style="color:var(--acc)">> Тамуз — Король Бездны — расколол Мобию.</p>
            <p>> Древние Владыки Света пали, оставив лишь Сумеречные Осколки.</p>
            <p>> Вы — последний Избранный. Ваша цель — спуститься на 5-й ярус преисподней, собрать Кристаллы Рассвета и навечно запечатать Врата Ада.</p>
            <p style="color:#ff4444">> Помните: смерть здесь окончательна. Берегите Священную Пыль для крафта реликвий в лагере.</p>
        </div>
        <button class="btn" onclick="UI.show('scr-menu')">НАЗАД</button>
    </div>

    <div id="scr-adv" class="screen">
        <div class="panel" style="display:grid; grid-template-columns: 1fr 1fr 1fr; font-size:8px; padding:8px; gap:4px; text-align:center;">
            <div>❤️ HP: <span id="a-hp" style="color:var(--hp)"></span></div>
            <div>💰 ЗОЛОТО: <span id="a-gld" style="color:var(--gold)"></span></div>
            <div>🔮 ЯРУС: <span id="a-floor" style="color:var(--mana)"></span></div>
        </div>
        <div id="map-grid"></div>
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:6px;">
            <button class="btn" onclick="Camp.open()">🏕️ ЛАГЕРЬ И ИНВЕНТАРЬ</button>
            <button class="btn" onclick="UI.show('scr-quests')">📜 КВЕСТЫ (<span id="q-count">0</span>)</button>
        </div>
    </div>

    <div id="scr-camp" class="screen">
        <h1>УБЕЖИЩЕ РАССВЕТА</h1>
        <div class="panel" style="text-align:left; font-size:8px; display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
            <div>
                <p>ГЕРОЙ: <span id="c-name" style="color:var(--acc)"></span></p>
                <p>УРОВЕНЬ: <span id="c-lvl"></span></p>
                <p>ОПЫТ: <span id="c-xp"></span></p>
                <p>УРОН: <span id="c-dmg" style="color:var(--hp)"></span></p>
                <p>ЗАЩИТА: <span id="c-def" style="color:var(--mana)"></span></p>
            </div>
            <div>
                <p style="color:var(--acc)">Свободные очки: <span id="stat-points">0</span></p>
                <button class="btn" style="padding:4px; font-size:8px;" onclick="Game.levelUp('str')">+⚔️ Атака (+3)</button>
                <button class="btn" style="padding:4px; font-size:8px;" onclick="Game.levelUp('vit')">+❤️ Здоровье (+25)</button>
                <button class="btn" style="padding:4px; font-size:8px;" onclick="Game.levelUp('def')">+🛡️ Защита (+2)</button>
            </div>
        </div>
        <div class="panel" style="text-align:left;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h2 style="margin:0;">РЮКЗАК И СНАРЯЖЕНИЕ</h2>
                <span style="font-size:7px;color:#8aa">Пыль: <span id="c-dust" style="color:#a5f">0</span></span>
            </div>
            <div id="inventory" class="inv-grid"></div>
            <button class="btn" style="margin-top:10px; background:linear-gradient(#4a154b, #270329)" onclick="Camp.craft()">✨ СВЯЩЕННЫЙ КРАФТ (25 ПЫЛИ)</button>
        </div>
        <button class="btn" style="color:var(--gold)" onclick="UI.show('scr-adv')">ВЕРНУТЬСЯ НА КАРТУ</button>
    </div>

    <div id="scr-bat" class="screen">
        <h1 style="color:var(--hp); margin-bottom:2px;">АРЕНА СМЕРТИ</h1>
        <div id="bat-enemy-name" style="font-size:9px; color:#aaa; margin-bottom:6px;">Враг</div>
        
        <div id="battle-area">
            <div class="hp-bar-container" style="left:10%;"><div id="p-hp-bar" class="hp-bar"></div></div>
            <div id="player-sprite" class="fighter">⚔️</div>
            
            <div class="hp-bar-container" style="right:10%;"><div id="e-hp-bar" class="hp-bar"></div></div>
            <div id="enemy-sprite" class="fighter">👹</div>
        </div>
        
        <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:4px;">
            <button id="b-btn-1" class="btn" onclick="Combat.act(1)">⚔️ Базовая</button>
            <button id="b-btn-2" class="btn" onclick="Combat.act(2)">✨ Навык</button>
            <button id="b-btn-3" class="btn" onclick="Combat.act(3)">☄️ УЛЬТ</button>
        </div>
        <div id="battle-log" class="panel"></div>
    </div>

    <div id="scr-quests" class="screen">
        <h1>ЖУРНАЛ ЗАДАНИЙ</h1>
        <div class="panel" id="quest-list" style="flex:1;overflow-y:auto;text-align:left; font-size:8px; line-height:1.6;"></div>
        <button class="btn" onclick="UI.show('scr-adv')">НАЗАД</button>
    </div>
</div>

<script>
// ==================== СИСТЕМА ДВИЖКА AUDIO (СИНТЕЗАТОР WEBAUDIO) ====================
const Snd = {
    ctx: null,
    init() { if(!this.ctx) this.ctx = new (window.AudioContext || window.webkitAudioContext)(); },
    play(type) {
        this.init(); if(!this.ctx) return;
        const o = this.ctx.createOscillator(), g = this.ctx.createGain();
        o.connect(g); g.connect(this.ctx.destination);
        const t = this.ctx.currentTime;
        if(type==='hit') {
            o.type = 'sawtooth'; o.frequency.setValueAtTime(120, t); o.frequency.exponentialRampToValueAtTime(40, t+0.15);
            g.gain.setValueAtTime(0.3, t); g.gain.linearRampToValueAtTime(0, t+0.15); o.start(t); o.stop(t+0.15);
        } else if(type==='skill') {
            o.type = 'triangle'; o.frequency.setValueAtTime(300, t); o.frequency.exponentialRampToValueAtTime(600, t+0.2);
            g.gain.setValueAtTime(0.2, t); g.gain.linearRampToValueAtTime(0, t+0.2); o.start(t); o.stop(t+0.2);
        } else if(type==='ult') {
            o.type = 'square'; o.frequency.setValueAtTime(150, t); o.frequency.linearRampToValueAtTime(900, t+0.4);
            g.gain.setValueAtTime(0.4, t); g.gain.linearRampToValueAtTime(0, t+0.4); o.start(t); o.stop(t+0.4);
        } else if(type==='loot') {
            o.type = 'sine'; o.frequency.setValueAtTime(400, t); o.frequency.setValueAtTime(600, t+0.08); o.frequency.setValueAtTime(900, t+0.16);
            g.gain.setValueAtTime(0.2, t); g.gain.linearRampToValueAtTime(0, t+0.25); o.start(t); o.stop(t+0.25);
        }
    }
};

// ==================== БАЗА ДАННЫХ ИГРЫ ====================
const DB = {
    heroes: [
        { id:'alu', n:'АЛУКАРД', spr:'⚔️', hp:260, dmg:32, def:12, desc:'Боец. Вампиризм: возвращает 30% нанесённого урона в виде здоровья.', sk: 'Рассекающий удар (х1.8)', ult: 'Сумеречная Охота (х3.5)' },
        { id:'mia', n:'МИЯ', spr:'🏹', hp:180, dmg:40, def:6, desc:'Стрелок. Сила Крита: Огромный шанс нанести х2 урон базовой атакой.', sk: 'Стрела Затмения (х1.5)', ult: 'Скрытый Натиск (х4.0)' },
        { id:'tig', n:'ТИГРИЛ', spr:'🛡️', hp:340, dmg:22, def:22, desc:'Танк. Абсолютная Броня: Снижает весь входящий урон на дополнительные 5 единиц.', sk: 'Удар Волны (х1.4)', ult: 'Имплозия земли (х2.8)' },
        { id:'gus', n:'ГОССЕН', spr:'🗡️', hp:190, dmg:36, def:8, desc:'Ассасин. Комбо-удар: Навыки не тратят кулдауны при убийствах.', sk: 'Бросок кинжала (х2.0)', ult: 'Теневое Клеймо (х4.2)' },
        { id:'eud', n:'ЭЙДОРА', spr:'⚡', hp:160, dmg:44, def:5, desc:'Маг. Сверхпроводник: Навык 2 парализует врага на следующий ход.', sk: 'Цепная Молния (х2.3)', ult: 'Гнев Молнии (х4.8)' },
        { id:'zil', n:'ЗИЛОНГ', spr:'🐉', hp:220, dmg:31, def:10, desc:'Воин. Яростный Натиск: Каждая третья базовая атака бьет дважды.', sk: 'Копейный бросок (х1.7)', ult: 'Воин Дракона (х3.8)' },
        { id:'fra', n:'ФРАНКО', spr:'🪝', hp:360, dmg:20, def:18, desc:'Танк-Контроль. Раз в бой полностью блокирует первую атаку врага.', sk: 'Железный Хук (х1.5)', ult: 'Охота на Ведьм (х3.0)' },
        { id:'sab', n:'САБЕР', spr:'🤺', hp:185, dmg:38, def:7, desc:'Убийца. Игнорирует 50% защиты цели при любых атаках.', sk: 'Летящие Клинки (х1.8)', ult: 'Тройной Удар (х4.5)' }
    ],
    enemies: [
        { n: "Гоблин-разведчик", hp: 100, dmg: 14, def: 4, spr: "👺", ai: "base" },
        { n: "Чумной Волк", hp: 130, dmg: 19, def: 6, spr: "🐺", ai: "rage" },
        { n: "Пещерный Паук", hp: 160, dmg: 24, def: 8, spr: "🕷️", ai: "poison" },
        { n: "Каменный Голем", hp: 280, dmg: 28, def: 20, spr: "🪨", ai: "heavy" },
        { n: "Лорд Тамуз [БОСС]", hp: 666, dmg: 45, def: 30, spr: "🔥", ai: "boss" }
    ],
    items: [
        { n: "Клинок Отчаяния", spr: "🗡️", stat: "dmg", v: 15, desc: "+15 Атака" },
        { n: "Щит Афины", spr: "🛡️", stat: "def", v: 10, desc: "+10 Защита" },
        { n: "Крылья Королевы", spr: "🪽", stat: "hp", v: 80, desc: "+80 ОЗ" },
        { n: "Метеор Розы", spr: "🌹", stat: "dmg", v: 8, desc: "+8 Атака" }
    ]
};

// ==================== СОСТОЯНИЕ ИГРЫ ====================
let Game = {
    hIdx: 0,
    zIdx: 0,
    p: null,
    statPoints: 0,
    quests: [],

    newGame() {
        Snd.play('skill');
        this.zIdx = 0;
        this.statPoints = 0;
        const h = DB.heroes[this.hIdx];
        this.p = {
            id: h.id, n: h.n, spr: h.spr, lvl: 1, xp: 0, nxp: 100,
            hp: h.hp, mhp: h.hp, dmg: h.dmg, def: h.def,
            gld: 150, dust: 20, inv: Array(12).fill(null)
        };
        this.quests = [
            { id: 1, n: "Зачистка этажа", cur: 0, max: 3, type: "kill", reward: 60, done: false },
            { id: 2, n: "Искатель Сокровищ", cur: 0, max: 2, type: "loot", reward: 40, done: false },
            { id: 3, n: "Убийца Тамуза", cur: 0, max: 1, type: "boss", reward: 999, done: false }
        ];
        Map.generate();
        UI.show('scr-adv');
        UI.updateAdv();
        UI.toast("Вы ступили во тьму подземелья Мобии!");
    },

    nextHero() { this.hIdx = (this.hIdx + 1) % DB.heroes.length; UI.updateHeroScreen(); },
    prevHero() { this.hIdx = (this.hIdx - 1 + DB.heroes.length) % DB.heroes.length; UI.updateHeroScreen(); },

    levelUp(stat) {
        if(this.statPoints <= 0) return;
        this.statPoints--;
        if(stat === 'str') this.p.dmg += 3;
        if(stat === 'vit') { this.p.mhp += 25; this.p.hp += 25; }
        if(stat === 'def') this.p.def += 2;
        Snd.play('loot');
        Camp.open();
    },

    addXp(amt) {
        this.p.xp += amt;
        if(this.p.xp >= this.p.nxp) {
            this.p.xp -= this.p.nxp;
            this.p.lvl++;
            this.p.nxp = Math.floor(this.p.nxp * 1.4);
            this.statPoints += 3;
            this.p.mhp += 15;
            this.p.hp = this.p.mhp;
            UI.toast(`🌟 УРОВЕНЬ ПОВЫШЕН! Текущий: ${this.p.lvl}`, "#0f0");
        }
    },

    checkQuests(type) {
        this.quests.forEach(q => {
            if(!q.done && q.type === type) {
                q.cur++;
                if(q.cur >= q.max) {
                    q.done = true;
                    this.p.gld += q.reward;
                    UI.toast(`📜 Квест "${q.n}" выполнен! +${q.reward}💰`, varColor='var(--gold)');
                }
            }
        });
        document.getElementById('q-count').textContent = this.quests.filter(q=>!q.done).length;
    },

    save(slot) {
        const data = { hIdx: this.hIdx, zIdx: this.zIdx, p: this.p, statPoints: this.statPoints, quests: this.quests };
        localStorage.setItem(`mlbb_rpg_save_${slot}`, JSON.stringify(data));
        UI.toast(`Игра сохранена в Слот ${slot}`, "var(--mana)");
    },

    load(slot) {
        const raw = localStorage.getItem(`mlbb_rpg_save_${slot}`);
        if(!raw) return UI.toast("Слот пуст!", "#f44");
        const data = JSON.parse(raw);
        this.hIdx = data.hIdx; this.zIdx = data.zIdx; this.p = data.p; this.statPoints = data.statPoints; this.quests = data.quests;
        UI.show('scr-adv');
        UI.updateAdv();
        UI.toast("Игра успешно загружена!", "#0f0");
    }
};

// ==================== ПРОЦЕДУРНАЯ КАРТА ПОДЗЕМЕЛИЙ ====================
const Map = {
    grid: [], px: 5, py: 5,
    generate() {
        this.grid = Array(11).fill().map(() => Array(11).fill(1)); // 1 - Стена
        
        // Генерация путей случайным блужданием
        let cx = 5, cy = 5;
        this.grid[cy][cx] = 0; // 0 - Пусто
        
        for(let i=0; i<60; i++) {
            const dir = [{x:0,y:1},{x:0,y:-1},{x:1,y:0},{x:-1,y:0}][Math.floor(Math.random()*4)];
            let nx = cx + dir.x, ny = cy + dir.y;
            if(nx > 0 && nx < 10 && ny > 0 && ny < 10) {
                cx = nx; cy = ny;
                this.grid[cy][cx] = 0;
            }
        }
        
        this.px = 5; this.py = 5;
        this.grid[5][5] = 0;

        // Расстановка врагов, сундуков и лестницы
        let positions = [];
        for(let y=1; y<10; y++) {
            for(let x=1; x<10; x++) {
                if(this.grid[y][x] === 0 && !(x===5 && y===5)) positions.push({x, y});
            }
        }
        
        positions.sort(() => Math.random() - 0.5);

        // Распределяем сущности
        if(positions.length > 0) {
            const exit = positions.pop();
            this.grid[exit.y][exit.x] = 5; // Лестница вниз
        }
        
        let count = 0;
        while(positions.length > 0 && count < 7) {
            const pos = positions.pop();
            this.grid[pos.y][pos.x] = Math.random() < 0.65 ? 2 : 4; // 2 - Враг, 4 - Сундук
            count++;
        }
        
        // Если это финальный этаж, ставим Босса вместо лестницы
        if(Game.zIdx === 4) {
            for(let y=0; y<11; y++){
                for(let x=0; x<11; x++){
                    if(this.grid[y][x] === 5) this.grid[y][x] = 6; // 6 - Босс Тамуз
                }
            }
        }
        this.draw();
    },

    draw() {
        const gridEl = document.getElementById('map-grid');
        gridEl.innerHTML = '';
        for(let y=0; y<11; y++) {
            for(let x=0; x<11; x++) {
                const el = document.createElement('div');
                el.className = 'tile';
                
                // Подсчет тумана войны (видимость в радиусе 2 клеток)
                const dist = Math.abs(x - this.px) + Math.abs(y - this.py);
                if(dist > 2) {
                    el.classList.add('fog');
                } else {
                    el.classList.add('visible');
                }

                if(x === this.px && y === this.py) {
                    el.textContent = Game.p.spr;
                    el.style.background = "#224";
                } else {
                    const type = this.grid[y][x];
                    if(type === 1) { el.classList.add('wall'); el.textContent = '█'; }
                    else if(type === 0) el.textContent = '·';
                    else if(type === 2) el.textContent = '👾';
                    else if(type === 4) el.textContent = '📦';
                    else if(type === 5) el.textContent = '🪜';
                    else if(type === 6) el.textContent = '🔥';
                }

                el.onclick = () => this.click(x, y);
                gridEl.appendChild(el);
            }
        }
    },

    click(x, y) {
        if(Math.abs(x - this.px) > 1 || Math.abs(y - this.py) > 1) return;
        if(this.grid[y][x] === 1) return; // Стены непроходимы

        this.px = x; this.py = y;
        const tileType = this.grid[y][x];

        if(tileType === 2) {
            // Обычная битва
            let pool = DB.enemies.slice(0, 4);
            let e = pool[Math.min(Game.zIdx, pool.length-1)];
            Combat.start(e, false);
            this.grid[y][x] = 0;
        } else if(tileType === 4) {
            // Сундук
            Snd.play('loot');
            let goldReward = 30 + Math.floor(Math.random()*40) + (Game.zIdx * 15);
            let dustReward = 5 + Math.floor(Math.random()*8);
            Game.p.gld += goldReward;
            Game.p.dust += dustReward;
            UI.toast(`Найдено: +${goldReward}💰, +${dustReward}🔮 пыли!`);
            Game.checkQuests('loot');
            this.grid[y][x] = 0;
        } else if(tileType === 5) {
            // Спуск ниже
            Snd.play('skill');
            Game.zIdx++;
            UI.toast(`Вы спустились на ярус ${Game.zIdx + 1}`);
            this.generate();
        } else if(tileType === 6) {
            // БОСС
            Combat.start(DB.enemies[4], true);
            this.grid[y][x] = 0;
        }

        this.draw();
        UI.updateAdv();
    }
};

// ==================== БОЕВАЯ СИСТЕМА (ПРОДВИНУТЫЙ ИИ И КОМБАТ) ====================
const Combat = {
    enemy: null,
    cds: { 2: 0, 3: 0 },
    isBoss: false,
    firstBlock: false,

    start(e, isBossFlag) {
        this.enemy = { ...e, maxHp: e.hp + (Game.zIdx * 60), hp: e.hp + (Game.zIdx * 60), dmg: e.dmg + (Game.zIdx * 4) };
        this.isBoss = isBossFlag;
        this.cds = { 2: 0, 3: 0 };
        this.firstBlock = (Game.p.id === 'fra'); // Пассивка Франко
        
        document.getElementById('bat-enemy-name').textContent = `${this.enemy.n} (Ур.${Game.zIdx+1})`;
        document.getElementById('enemy-sprite').textContent = this.enemy.spr;
        document.getElementById('player-sprite').textContent = Game.p.spr;
        
        document.getElementById('battle-log').innerHTML = '';
        UI.show('scr-bat');
        this.log(`Перед вами восстал ${this.enemy.n}!`, "var(--acc)");
        this.updateBars();
    },

    updateBars() {
        document.getElementById('p-hp-bar').style.width = `${Math.max(0, (Game.p.hp / Game.p.mhp) * 100)}%`;
        document.getElementById('e-hp-bar').style.width = `${Math.max(0, (this.enemy.hp / this.enemy.maxHp) * 100)}%`;
        
        document.getElementById('b-btn-2').disabled = this.cds[2] > 0;
        document.getElementById('b-btn-3').disabled = this.cds[3] > 0;
        
        document.getElementById('b-btn-2').textContent = `✨ Н-к (${this.cds[2]})`;
        document.getElementById('b-btn-3').textContent = `☄️ Ульт (${this.cds[3]})`;
    },

    act(type) {
        // Ход игрока
        let rawDmg = Game.p.dmg;
        let sfx = 'hit';
        let actName = "атаковал";

        if(type === 2) {
            rawDmg = Math.floor(rawDmg * 2.0);
            this.cds[2] = 2; // Кулдаун 2 хода
            sfx = 'skill';
            actName = "применил Навык";
        } else if(type === 3) {
            rawDmg = Math.floor(rawDmg * 4.2);
            this.cds[3] = 4; // Кулдаун 4 хода
            sfx = 'ult';
            actName = "АКТИВИРОВАЛ УЛЬТИМЕЙТ";
        }

        // Пассивка Мии (Крит х2)
        if(type === 1 && Game.p.id === 'mia' && Math.random() < 0.35) {
            rawDmg *= 2;
            this.log("🎯 КРИТИЧЕСКИЙ УДАР МИИ!", "var(--gold)");
        }

        // Вычисление защиты врага
        let finalDef = this.enemy.def;
        if(Game.p.id === 'sab') finalDef = Math.floor(finalDef * 0.5); // Пассивка Сабера

        let totalDmg = Math.max(5, rawDmg - finalDef);
        this.enemy.hp -= totalDmg;
        Snd.play(sfx);
        
        this.log(`Вы ${actName} и нанесли ${totalDmg} урона.`, "#fff");

        // Пассивка Алукарда (Вампиризм)
        if(Game.p.id === 'alu') {
            let heal = Math.floor(totalDmg * 0.3);
            Game.p.hp = Math.min(Game.p.mhp, Game.p.hp + heal);
            this.log(`🩸 Вампиризм Алукарда вернул +${heal} ОЗ.`, "var(--hp)");
        }

        this.animate('player-sprite', 15);

        // Проверка победы
        if(this.enemy.hp <= 0) {
            this.winGame();
            return;
        }

        // Кулдауны тикают
        for(let key in this.cds) { if(this.cds[key] > 0) this.cds[key]--; }

        // Эффект оглушения Эйдоры (Навык 2 заставляет пропустить ход врага)
        if(Game.p.id === 'eud' && type === 2) {
            this.log(`⚡ ${this.enemy.n} парализован током Эйдоры на 1 ход!`, "var(--mana)");
            this.updateBars();
            return;
        }

        // Ход Врага
        setTimeout(() => this.enemyTurn(), 600);
    },

    enemyTurn() {
        if(this.enemy.hp <= 0) return;

        let eDmg = this.enemy.dmg;
        let ai = this.enemy.ai;

        // Поведение ИИ врагов
        if(ai === 'rage' && this.enemy.hp < (this.enemy.maxHp * 0.5)) {
            eDmg = Math.floor(eDmg * 1.5);
            this.log("😡 Волк впал в ярость! Его урон увеличен!", "var(--hp)");
        } else if(ai === 'poison' && Math.random() < 0.4) {
            Game.p.hp -= 10;
            this.log("🕷️ Паук отравил вас кислотой! -10 ОЗ игнорируя защиту.", "#0f0");
        }

        // Расчет защиты игрока
        let playerDef = Game.p.def;
        // Экипировка (Бонусы)
        Game.p.inv.forEach(item => { if(item && item.equipped && item.stat==='def') playerDef += item.v; });

        let finalDmg = Math.max(3, eDmg - playerDef);
        
        if(Game.p.id === 'tig') finalDmg = Math.max(1, finalDmg - 5); // Пассивка Тигрила

        // Пассивка Франко (Блок первого удара)
        if(this.firstBlock) {
            this.firstBlock = false;
            finalDmg = 0;
            this.log("🪝 Франко полностью заблокировал атаку щитом!", "var(--mana)");
        }

        if(finalDmg > 0) {
            Game.p.hp -= finalDmg;
            this.log(`${this.enemy.n} атакует вас на -${finalDmg} ОЗ.`, "var(--hp)");
            Snd.play('hit');
            this.animate('enemy-sprite', -15);
        }

        this.updateBars();

        if(Game.p.hp <= 0) {
            setTimeout(() => this.loseGame(), 400);
        }
    },

    animate(id, offset) {
        const el = document.getElementById(id);
        el.style.transform = `translateX(${offset}px) ${id==='enemy-sprite'?'scaleX(-1)':''}`;
        setTimeout(() => el.style.transform = id==='enemy-sprite'?'scaleX(-1)':'none', 150);
    },

    winGame() {
        this.log("🎉 ПОБЕДА НАД СИЛАМИ ТЬМЫ!", "#0f0");
        let xpGained = 25 + (Game.zIdx * 15);
        let goldGained = 30 + (Game.zIdx * 10);
        Game.p.gld += goldGained;
        Game.addXp(xpGained);
        
        Game.checkQuests('kill');

        if(this.isBoss) {
            Game.checkQuests('boss');
            alert("✨ НЕМЫСЛИМО! Лорд Тамуз свергнут, а врата бездны запечатаны навсегда! Вы прошли игру! ✨");
            UI.show('scr-menu');
            return;
        }

        setTimeout(() => { UI.show('scr-adv'); UI.updateAdv(); }, 1200);
    },

    loseGame() {
        alert(`💀 Ваш герой пал на ${Game.zIdx + 1}-м ярусе подземелья. Тьма поглотила этот мир...`);
        UI.show('scr-menu');
    },

    log(msg, color) {
        const logEl = document.getElementById('battle-log');
        logEl.innerHTML += `<div style="color:${color}; margin-bottom:2px;">> ${msg}</div>`;
        logEl.scrollTop = logEl.scrollHeight;
    }
};

// ==================== СИСТЕМА ЛАГЕРЯ, ИНВЕНТАРЯ И КРАФТА ====================
const Camp = {
    open() {
        UI.show('scr-camp');
        document.getElementById('c-name').textContent = Game.p.n;
        document.getElementById('c-lvl').textContent = Game.p.lvl;
        document.getElementById('c-xp').textContent = `${Game.p.xp}/${Game.p.nxp}`;
        
        let displayDmg = Game.p.dmg;
        let displayDef = Game.p.def;
        let displayHp = Game.p.mhp;
        
        Game.p.inv.forEach(i => {
            if(i && i.equipped) {
                if(i.stat === 'dmg') displayDmg += i.v;
                if(i.stat === 'def') displayDef += i.v;
                if(i.stat === 'hp') displayHp += i.v;
            }
        });

        document.getElementById('c-dmg').textContent = displayDmg;
        document.getElementById('c-def').textContent = displayDef;
        document.getElementById('c-vit').textContent = `${Game.p.hp}/${displayHp}`;
        document.getElementById('stat-points').textContent = Game.statPoints;
        document.getElementById('c-dust').textContent = Game.p.dust;

        this.renderInventory();
    },

    renderInventory() {
        const invEl = document.getElementById('inventory');
        invEl.innerHTML = '';
        
        Game.p.inv.forEach((item, idx) => {
            const slot = document.createElement('div');
            slot.className = 'inv-slot';
            if(item) {
                slot.textContent = item.spr;
                if(item.equipped) slot.style.border = "2px solid var(--acc)";
                slot.onclick = () => this.useItem(idx);
            }
            invEl.appendChild(slot);
        });
    },

    useItem(idx) {
        let item = Game.p.inv[idx];
        if(!item) return;
        
        item.equipped = !item.equipped;
        Snd.play('loot');
        if(item.equipped) {
            UI.toast(`Экипировано: ${item.n}`);
        } else {
            UI.toast(`Снято: ${item.n}`);
        }
        this.open();
    },

    craft() {
        if(Game.p.dust < 25) return UI.toast("Недостаточно священной пыли!", "#f44");
        
        // Поиск пустого слота
        let emptyIdx = Game.p.inv.indexOf(null);
        if(emptyIdx === -1) return UI.toast("Инвентарь заполнен!", "#f44");

        Game.p.dust -= 25;
        let baseItem = DB.items[Math.floor(Math.random() * DB.items.length)];
        // Генерация случайных характеристик реликвии
        let qualityModifier = 1 + Math.floor(Math.random() * Game.p.lvl);
        
        Game.p.inv[emptyIdx] = {
            ...baseItem,
            v: baseItem.v + qualityModifier,
            n: `Древний ${baseItem.n}`,
            equipped: false
        };

        Snd.play('ult');
        UI.toast(`Сковано: ${Game.p.inv[emptyIdx].n}!`, "var(--rarity)");
        this.open();
    }
};

// ==================== ИНТЕРФЕЙС И ОБНОВЛЕНИЕ ЭКРАНОВ ====================
const UI = {
    show(id) {
        document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
        document.getElementById(id).classList.add('active');
        if(id === 'scr-quests') this.updateQuestsScreen();
    },

    openHeroSelect() {
        this.show('scr-hero');
        this.updateHeroScreen();
    },

    updateHeroScreen() {
        const h = DB.heroes[Game.hIdx];
        document.getElementById('hero-sprite').textContent = h.spr;
        document.getElementById('hero-info').innerHTML = `
            <b style="color:var(--acc); font-size:12px;">${h.n}</b><br><br>
            ❤️ ЗДОРОВЬЕ: <span style="color:var(--hp)">${h.hp}</span><br>
            ⚔️ АТАКА: <span style="color:var(--gold)">${h.dmg}</span><br>
            🛡️ ЗАЩИТА: <span style="color:var(--mana)">${h.def}</span><br><br>
            <b>НАВЫК:</b> ${h.sk}<br>
            <b>УЛЬТ:</b> ${h.ult}<br><br>
            <span style="color:#aaa; font-size:8px;">${h.desc}</span>
        `;
    },

    updateAdv() {
        document.getElementById('a-hp').textContent = `${Game.p.hp}/${Game.p.mhp}`;
        document.getElementById('a-gld').textContent = Game.p.gld;
        document.getElementById('a-floor').textContent = `${Game.zIdx + 1}/5`;
        document.getElementById('q-count').textContent = Game.quests.filter(q=>!q.done).length;
    },

    updateQuestsScreen() {
        const qList = document.getElementById('quest-list');
        qList.innerHTML = '';
        Game.quests.forEach(q => {
            const div = document.createElement('div');
            div.style.marginBottom = "8px";
            div.style.color = q.done ? "#666" : "#fff";
            div.innerHTML = `
                <div style="text-decoration: ${q.done?'line-through':'none'}">
                    ${q.done ? '✅' : '📜'} <b>${q.n}</b> (${q.cur}/${q.max})
                </div>
                <div style="font-size:7px; color:var(--gold)">Награда: +${q.reward}💰</div>
            `;
            qList.appendChild(div);
        });
    },

    toast(msg, color = "#fff") {
        const t = document.createElement('div');
        t.style.cssText = `background:rgba(5,5,15,0.95); border:2px solid ${color}; padding:8px 14px; border-radius:4px; color:#fff; font-size:8px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); text-align:left; max-width:90%;`;
        t.textContent = msg;
        document.getElementById('toasts').appendChild(t);
        setTimeout(() => t.remove(), 2500);
    }
};

// Первая принудительная отрисовка экрана выбора
UI.updateHeroScreen();
</script>
</body>
</html>
