from flask import Flask, render_template_string

app = Flask(__name__)

GAME_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>MLBB RPG: Симфония Элементов — v10.0</title>
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-main: #030308; --bg-panel: #090912; --border: #3d3d5c;
            --text-main: #e0e0f0; --accent: #ffff55; --hp: #ff4444;
            --mana: #55aaff; --dust: #aa55ff; --gold: #ffff55;
        }
        *, *::before, *::after { box-sizing: border-box; }
        body {
            font-family: 'Press Start 2P', cursive; background-color: var(--bg-main); color: var(--text-main);
            margin: 0; padding: 5px; font-size: 7px; text-align: center; overflow: hidden;
            user-select: none; -webkit-user-select: none;
            height: 100vh; display: flex; justify-content: center; align-items: center;
        }
        
        #game-container {
            width: 100%; max-width: 460px; height: 100%; max-height: 780px;
            display: flex; flex-direction: column; justify-content: space-between;
            background: linear-gradient(135deg, #0b0b1a 0%, #030308 100%);
            border: 4px solid #555577; box-shadow: 0 0 50px rgba(0,0,0,0.95);
            padding: 8px; position: relative; overflow: hidden;
        }
        
        .screen { display: none; height: 100%; flex-direction: column; justify-content: space-between; }
        .screen.active { display: flex; animation: fadeIn 0.3s ease-out; }
        .col-left, .col-right { width: 100%; display: flex; flex-direction: column; justify-content: space-between; }
        
        @media (orientation: landscape) and (min-width: 550px) {
            #game-container { max-width: 920px; max-height: 450px; flex-direction: row; padding: 10px; }
            .screen { flex-direction: row !important; width: 100%; gap: 14px; }
            .col-left, .col-right { width: 49%; height: 100%; }
        }

        h1 { font-size: 10px; color: var(--accent); text-shadow: 2px 2px #000; margin: 3px 0; letter-spacing: 1px; line-height: 1.4; }
        .panel { background-color: var(--bg-panel); border: 2px solid var(--border); box-shadow: 3px 3px 0px #000; padding: 6px; margin-bottom: 4px; position: relative; }
        
        /* КАРТА И ОСВЕЩЕНИЕ */
        #viewport-container {
            width: 100%; max-width: 250px; margin: 4px auto;
            border: 3px solid #444466; background: #000; padding: 2px;
            box-shadow: inset 0 0 15px #000;
        }
        #map-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 2px; width: 100%; }
        .map-tile {
            aspect-ratio: 1; display: flex; align-items: center; justify-content: center;
            font-size: 14px; background: #121e12; border-radius: 2px;
            transition: opacity 0.3s ease, transform 0.1s;
        }
        .dimmed-1 { opacity: 0.6; filter: brightness(0.6); }
        .dimmed-2 { opacity: 0.2; filter: brightness(0.3); }
        .dimmed-3 { opacity: 0.05; filter: brightness(0.1); }
        .tile-wall { background: #1a1a24; color: #445; }

        /* ИНТЕРФЕЙС И КНОПКИ */
        .btn { font-family: 'Press Start 2P'; background: #1c1c3a; color: #d4af37; border: 3px outset #4a4a88; padding: 10px; cursor: pointer; border-radius: 4px; width: 100%; font-size: 8px; margin-top: 4px; }
        .btn:active { border-style: inset; background: #111124; }
        .btn:disabled { opacity: 0.3; cursor: not-allowed; filter: grayscale(1); }
        
        .dpad-container { display: grid; grid-template-columns: repeat(3, 1fr); width: 140px; margin: 2px auto; gap: 5px; }
        .dpad-btn { font-family: 'Press Start 2P'; font-size: 16px; background: #252542; color: #fff; border: 2px outset #555588; padding: 12px 0; cursor: pointer; border-radius: 6px; }
        .dpad-btn:active { border-style: inset; background: #15152b; color: var(--accent); }

        .bar-wrap { width: 100%; height: 10px; background-color: #111; border: 2px solid #fff; position: relative; margin: 2px 0; }
        .bar-fill { height: 100%; transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1); }

        #log { height: 60px; overflow-y: auto; background: #010104; color: #aaa; padding: 5px; text-align: left; border: 2px solid var(--border); font-size: 5.5px; line-height: 1.6; }
        
        .stage-container { position: relative; height: 90px; background: #020208; border: 2px solid #333; margin: 4px 0; overflow: hidden; }
        .sprite { font-size: 38px; position: absolute; bottom: 8px; width: 50px; height: 50px; display: flex; align-items: center; justify-content: center; }
        #hero-sprite { left: 15%; transform: scaleX(-1); } #enemy-sprite { right: 15%; }

        /* АНИМАЦИИ */
        @keyframes fadeIn { from { opacity: 0; transform: scale(0.98); } to { opacity: 1; transform: scale(1); } }
        .anim-float { animation: float 2s infinite ease-in-out; }
        .anim-atk-l { animation: strikeL 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
        .anim-atk-r { animation: strikeR 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
        @keyframes float { 0%, 100% { transform: translateY(0) scaleX(-1); } 50% { transform: translateY(-5px) scaleX(-1); } }
        @keyframes strikeL { 0%, 100% { left: 15%; } 50% { left: 45%; transform: scaleX(-1) scale(1.3) rotate(15deg); z-index: 10; } }
        @keyframes strikeR { 0%, 100% { right: 15%; } 50% { right: 45%; transform: scale(1.3) rotate(-15deg); z-index: 10; } }

        /* ВСПЛЫВАЮЩИЕ УВЕДОМЛЕНИЯ (TOASTS) */
        #toast-container { position: absolute; top: 10px; left: 0; width: 100%; display: flex; flex-direction: column; align-items: center; pointer-events: none; z-index: 100; }
        .toast { background: rgba(10, 10, 25, 0.95); border: 2px solid var(--accent); color: #fff; padding: 8px 12px; margin-bottom: 5px; border-radius: 4px; font-size: 6px; box-shadow: 0 4px 10px rgba(0,0,0,0.8); animation: toastAnim 2.5s forwards; }
        @keyframes toastAnim { 0% { opacity: 0; transform: translateY(-20px); } 10% { opacity: 1; transform: translateY(0); } 90% { opacity: 1; transform: translateY(0); } 100% { opacity: 0; transform: translateY(-20px); } }
        
        .inv-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px; margin: 4px 0; }
        .inv-slot { background: #05050f; border: 2px solid #333; height: 38px; display: flex; align-items: center; justify-content: center; font-size: 16px; cursor: pointer; border-radius: 4px; }
        .legend { border-color: #d4af37; box-shadow: inset 0 0 8px rgba(212,175,55,0.5); }
    </style>
</head>
<body>

    <div id="game-container">
        <div id="toast-container"></div>

        <!-- ГЛАВНОЕ МЕНЮ -->
        <div id="screen-menu" class="screen active">
            <div class="col-left" style="justify-content: center;">
                <h1>MLBB RPG:<br>СИМФОНИЯ<br>ЭЛЕМЕНТОВ</h1>
                <p style="font-size: 5px; color: #8a8ab0; margin-top: 10px;">ВЕРСИЯ 10.0 ULTIMATE</p>
                <div style="font-size: 40px; margin: 20px 0; animation: float 3s infinite ease-in-out;">🌌</div>
            </div>
            <div class="col-right" style="justify-content: center; gap: 8px;">
                <button class="btn" onclick="Game.start()">НАЧАТЬ ПУТЬ</button>
                <button class="btn" onclick="UI.switchScreen('screen-settings')">ГЕРОИ И НАСТРОЙКИ</button>
            </div>
        </div>

        <!-- НАСТРОЙКИ -->
        <div id="screen-settings" class="screen">
            <div class="col-left">
                <h1>НАСТРОЙКИ</h1>
                <div class="panel" style="text-align: left;">
                    <div style="margin-bottom:10px;">ГЕРОЙ: <button class="btn" style="padding:6px; background:#32324e;" onclick="Game.nextHero()" id="cfg-hero">АЛУКАРД</button></div>
                    <div style="margin-bottom:10px;">ЗВУК: <button class="btn" style="padding:6px; background:#32324e;" onclick="Audio.toggle('sfx')" id="cfg-sfx">ВКЛ</button></div>
                    <div style="margin-bottom:10px;">МУЗЫКА: <button class="btn" style="padding:6px; background:#32324e;" onclick="Audio.toggle('music')" id="cfg-music">ВКЛ</button></div>
                </div>
            </div>
            <div class="col-right">
                <div class="panel" id="hero-desc" style="font-size:6px; color:#bbb; line-height:1.6; flex-grow:1;"></div>
                <button class="btn" onclick="UI.switchScreen(Game.state.isPlaying ? 'screen-adventure' : 'screen-menu')">НАЗАД</button>
            </div>
        </div>

        <!-- КАРТА ИССЛЕДОВАНИЯ -->
        <div id="screen-adventure" class="screen">
            <div class="col-left">
                <div style="display:flex; justify-content:space-between; font-size:6px; padding:4px; background:#000; border:1px solid #333;">
                    <span style="color:var(--hp)">❤️ <span id="adv-hp">100</span></span>
                    <span style="color:var(--gold)">💰 <span id="adv-gold">0</span></span>
                    <span style="color:var(--dust)">💎 <span id="adv-dust">0</span></span>
                </div>
                <div id="viewport-container"><div id="map-grid"></div></div>
            </div>
            <div class="col-right" style="justify-content: flex-end;">
                <div class="dpad-container">
                    <div></div><button class="dpad-btn" onclick="Map.move(0, -1)">▲</button><div></div>
                    <button class="dpad-btn" onclick="Map.move(-1, 0)">◄</button>
                    <button class="dpad-btn" style="background:#4a235a; color:var(--accent); font-size:12px;" onclick="Camp.open()">🎒</button>
                    <button class="dpad-btn" onclick="Map.move(1, 0)">►</button>
                    <div></div><button class="dpad-btn" onclick="Map.move(0, 1)">▼</button><div></div>
                </div>
                <button class="btn" style="background:#151515;" onclick="UI.switchScreen('screen-settings')">МЕНЮ</button>
            </div>
        </div>

        <!-- ИНВЕНТАРЬ И ЛАГЕРЬ -->
        <div id="screen-camp" class="screen">
            <div class="col-left">
                <h1 style="color:#55ff55;">СНАРЯЖЕНИЕ</h1>
                <div class="panel" style="font-size:6px; line-height:1.6; text-align:left;">
                    <div style="color:#fff;">КЛАСС: <span id="camp-hero" style="color:var(--mana)">-</span> (<span id="camp-lvl">1</span> УР)</div>
                    <div>УРОН: <span id="camp-dmg" style="color:var(--hp)">0</span> | ОЗ: <span id="camp-hp" style="color:var(--hp)">0</span></div>
                    <div class="bar-wrap"><div id="camp-exp" class="bar-fill" style="background:var(--dust); width:0%;"></div></div>
                </div>
                <div style="display:flex; gap:4px;">
                    <div class="inv-slot" id="eq-weap" style="width:33%; font-size:8px;" onclick="Camp.unequip('weapon')">⚔️</div>
                    <div class="inv-slot" id="eq-arm" style="width:33%; font-size:8px;" onclick="Camp.unequip('armor')">🛡️</div>
                    <div class="inv-slot" id="eq-art" style="width:33%; font-size:8px;" onclick="Camp.unequip('artifact')">🔮</div>
                </div>
            </div>
            <div class="col-right">
                <div class="panel" style="flex-grow:1;">
                    <div style="font-size:5px; color:#aaa;">ИНВЕНТАРЬ (Зажми для разбора):</div>
                    <div class="inv-grid" id="inv-list"></div>
                </div>
                <div style="display:flex; gap:4px;">
                    <button class="btn" style="color:var(--dust); padding:6px;" onclick="Camp.craft()">КРАФТ (15💎)</button>
                    <button class="btn" style="color:var(--hp); padding:6px;" onclick="Camp.heal()">ЗЕЛЬЕ (15💰)</button>
                </div>
                <button class="btn" style="background:#222;" onclick="UI.switchScreen('screen-adventure')">НА КАРТУ</button>
            </div>
        </div>

        <!-- БОЕВАЯ АРЕНА -->
        <div id="screen-battle" class="screen">
            <div class="col-left">
                <h1 style="color:var(--hp);">БИТВА</h1>
                <div class="panel" style="flex-grow:1; display:flex; flex-direction:column; justify-content:space-between;">
                    <div style="display:flex; justify-content:space-between; font-size:6px;">
                        <span id="bt-p-name" style="color:var(--mana)">ГЕРОЙ</span>
                        <span id="bt-e-name" style="color:var(--hp)">ВРАГ</span>
                    </div>
                    <div class="stage-container">
                        <div id="hero-sprite" class="sprite anim-float">⚔️</div>
                        <div id="enemy-sprite" class="sprite">👾</div>
                    </div>
                    <div class="bar-wrap"><div id="bt-e-hp" class="bar-fill" style="background:var(--hp); width:100%;"></div></div>
                </div>
            </div>
            <div class="col-right">
                <div class="panel" id="log">Бой начинается...</div>
                <div class="panel">
                    <div style="display:flex; justify-content:space-between; font-size:6px; margin-bottom:2px;">
                        <span style="color:var(--hp);">ОЗ: <span id="bt-p-hp-text">100</span></span>
                        <span style="color:var(--mana);">⚡ <span id="bt-p-mana">3/3</span></span>
                    </div>
                    <div class="bar-wrap" style="margin-bottom:6px;">
                        <div id="bt-p-hp" class="bar-fill" style="background:#22cc22; width:100%;"></div>
                        <div id="bt-p-shield" class="bar-fill" style="background:#777; width:0%; position:absolute; top:0; left:0;"></div>
                    </div>
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:4px;">
                        <button class="btn" id="sk-1" style="margin:0; color:#fff;" onclick="Combat.useSkill(1)">[1] Атака</button>
                        <button class="btn" id="sk-2" style="margin:0; color:var(--mana);" onclick="Combat.useSkill(2)">[2] Магия</button>
                        <button class="btn" id="sk-3" style="margin:0; color:#aaa;" onclick="Combat.useSkill(3)">[3] Защита</button>
                        <button class="btn" id="sk-4" style="margin:0; color:var(--accent);" onclick="Combat.useSkill(4)">[4] УЛЬТ</button>
                    </div>
                </div>
            </div>
        </div>

    </div>

    <script>
        /**
         * v10.0 "Симфония Элементов" - Идеальная организация
         */
        
        // --- 1. ДАННЫЕ И БАЗА ---
        const DB = {
            heroes: {
                'алукард': { name: "АЛУКАРД", hp: 140, dmg: 18, sprite: "⚔️", desc: "БОЕЦ. Вампиризм с атак. Магия: Огонь." },
                'мия': { name: "МИЯ", hp: 110, dmg: 25, sprite: "🏹", desc: "СТРЕЛОК. Шанс крита 30%. Магия: Лед (Стан)." },
                'тигрил': { name: "ТИГРИЛ", hp: 200, dmg: 14, sprite: "🛡️", desc: "ТАНК. Начинает со щитом. Усиленные блоки." },
                'госсен': { name: "ГОССЕН", hp: 120, dmg: 22, sprite: "🗡️", desc: "УБИЙЦА. Быстрый реген маны. Добив. ульта." }
            },
            loot: [
                { type: 'weapon', name: 'Меч Охотника', icon: '🗡️', stat: 12, rare: 'common' },
                { type: 'weapon', name: 'Клинок Отчаяния', icon: '⚔️', stat: 45, rare: 'legend' },
                { type: 'armor', name: 'Кираса', icon: '👕', stat: 10, rare: 'common' },
                { type: 'armor', name: 'Крылья Королевы', icon: '🦇', stat: 35, rare: 'legend' },
                { type: 'artifact', name: 'Амулет', icon: '📿', stat: 30, rare: 'common' },
                { type: 'artifact', name: 'Око Дракона', icon: '🔮', stat: 100, rare: 'legend' }
            ],
            zones: [
                { name: "Темный Лес", wall: "🌲", floor: "#121e12", mobs: [{ name: "Гоблин", hp: 60, dmg: [6, 12], sprite: "👺", elem: 'fire' }] },
                { name: "Снежный Пик", wall: "❄️", floor: "#1a2a3a", mobs: [{ name: "Йети", hp: 120, dmg: [12, 20], sprite: "⛄", elem: 'ice' }] },
                { name: "Вулкан Ужаса", wall: "🌋", floor: "#3a1a1a", mobs: [{ name: "ЛОРД", hp: 600, dmg: [40, 60], sprite: "👑", elem: 'fire' }] }
            ]
        };

        // --- 2. АУДИО ДВИЖОК (СЕКВЕНСОР) ---
        const Audio = {
            ctx: null, sfx: true, music: true, seqTimer: null, step: 0, currentTrack: null,
            notes: { E3: 164.8, G3: 196, A3: 220, C4: 261.6, D4: 293.7, E4: 329.6, F4: 349.2, G4: 392, A4: 440 },
            tracks: {
                explore: { tempo: 500, seq: ['A3', 'C4', 'E4', 'A4', 'G4', 'E4', 'C4', 'E4'], type: 'sine' },
                battle: { tempo: 220, seq: ['E3', 'E3', 'F4', 'E3', 'G3', 'E3', 'D4', 'E3'], type: 'sawtooth' }
            },
            init() { 
                if (!this.ctx) { this.ctx = new (window.AudioContext || window.webkitAudioContext)(); }
                if (this.ctx.state === 'suspended') this.ctx.resume();
            },
            toggle(type) { this[type] = !this[type]; UI.updateSettings(); if(type==='music') this.playTrack(this.currentTrackName); },
            playTone(freq, type, duration, vol=0.03) {
                if (!this.sfx || !this.ctx) return; this.init();
                let osc = this.ctx.createOscillator(), gain = this.ctx.createGain();
                osc.type = type; osc.frequency.setValueAtTime(freq, this.ctx.currentTime);
                gain.gain.setValueAtTime(vol, this.ctx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + duration);
                osc.connect(gain); gain.connect(this.ctx.destination);
                osc.start(); osc.stop(this.ctx.currentTime + duration);
            },
            playTrack(name) {
                this.currentTrackName = name; clearInterval(this.seqTimer); this.step = 0;
                if (!this.music || !name) return; this.init();
                let tr = this.tracks[name]; this.currentTrack = tr;
                this.seqTimer = setInterval(() => {
                    let note = tr.seq[this.step % tr.seq.length];
                    if(note && this.music) {
                        let osc = this.ctx.createOscillator(), gain = this.ctx.createGain();
                        osc.type = tr.type; osc.frequency.value = this.notes[note];
                        gain.gain.setValueAtTime(0.015, this.ctx.currentTime);
                        gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + (tr.tempo/1000));
                        osc.connect(gain); gain.connect(this.ctx.destination);
                        osc.start(); osc.stop(this.ctx.currentTime + (tr.tempo/1000));
                    }
                    this.step++;
                }, tr.tempo);
            },
            fx: {
                step: () => Audio.playTone(120, 'triangle', 0.05, 0.01),
                hit: () => Audio.playTone(150, 'square', 0.1, 0.03),
                loot: () => { Audio.playTone(600, 'sine', 0.1); setTimeout(()=>Audio.playTone(800, 'sine', 0.2), 100); },
                err: () => Audio.playTone(100, 'sawtooth', 0.2, 0.03)
            }
        };

        // --- 3. СОСТОЯНИЕ ИГРЫ ---
        const Game = {
            state: { isPlaying: false, hero: 'алукард', zIdx: 0 },
            player: { lvl: 1, exp: 0, nExp: 100, hp: 0, maxHp: 0, mana: 3, gold: 50, dust: 5, eq: {weapon:null, armor:null, artifact:null}, inv: [] },
            
            getHero() { return DB.heroes[this.state.hero]; },
            getMaxHp() { let b = this.getHero().hp + (this.player.lvl-1)*20; if(this.player.eq.artifact) b+=this.player.eq.artifact.stat; return b; },
            getDmg() { let b = this.getHero().dmg + (this.player.lvl-1)*5; if(this.player.eq.weapon) b+=this.player.eq.weapon.stat; return b; },
            
            nextHero() { 
                let keys = Object.keys(DB.heroes); 
                this.state.hero = keys[(keys.indexOf(this.state.hero) + 1) % keys.length]; 
                Audio.init(); UI.updateSettings(); 
            },
            
            start() {
                Audio.init(); this.state.isPlaying = true; this.state.zIdx = 0;
                this.player = { lvl: 1, exp: 0, nExp: 100, mana: 3, gold: 30, dust: 5, eq:{weapon:null, armor:null, artifact:null}, inv: [] };
                this.player.maxHp = this.getMaxHp(); this.player.hp = this.player.maxHp;
                Map.generate(this.state.zIdx); UI.switchScreen('screen-adventure');
                UI.toast("Глава 1: Путь начинается", "#ffff55");
            }
        };

        // --- 4. ГЕНЕРАЦИЯ И КАРТА ---
        const Map = {
            grid: [], size: 20, px: 2, py: 2,
            generate(zIdx) {
                this.grid = []; Audio.playTrack('explore');
                for(let y=0; y<this.size; y++) {
                    let r = [];
                    for(let x=0; x<this.size; x++) {
                        if(x===0||y===0||x===this.size-1||y===this.size-1) r.push(1); // Стена
                        else {
                            let rnd = Math.random();
                            if(rnd<0.15) r.push(1); // Препятствие
                            else if(rnd<0.22) r.push(2); // Враг
                            else if(rnd<0.26) r.push(4); // Лут
                            else if(rnd<0.27) r.push(5); // Хилка
                            else if(rnd<0.28) r.push(6); // Торговец
                            else r.push(0); // Пол
                        }
                    }
                    this.grid.push(r);
                }
                this.grid[this.size-2][this.size-2] = 3; // Выход
                this.grid[2][2] = 0; this.px = 2; this.py = 2;
                this.draw();
            },
            draw() {
                let html = ""; let z = DB.zones[Game.state.zIdx];
                let maxHp = Game.getMaxHp(); if(Game.player.hp > maxHp) Game.player.hp = maxHp;
                
                document.getElementById('adv-hp').innerText = `${Game.player.hp}/${maxHp}`;
                document.getElementById('adv-gold').innerText = Game.player.gold;
                document.getElementById('adv-dust').innerText = Game.player.dust;

                for(let y = this.py - 3; y <= this.py + 3; y++) {
                    for(let x = this.px - 3; x <= this.px + 3; x++) {
                        let dist = Math.max(Math.abs(x - this.px), Math.abs(y - this.py));
                        let dimClass = dist === 3 ? "dimmed-3" : (dist === 2 ? "dimmed-2" : (dist === 1 ? "dimmed-1" : ""));
                        
                        if(y<0||y>=this.size||x<0||x>=this.size) { html += `<div class="map-tile tile-wall ${dimClass}">${z.wall}</div>`; continue; }
                        
                        let v = this.grid[y][x]; let cnt = "", cls = dimClass;
                        if(x===this.px && y===this.py) { cnt = Game.getHero().sprite; cls = ""; }
                        else if(v===1) { cnt = z.wall; cls += " tile-wall"; }
                        else if(v===2) cnt = "👾"; else if(v===3) cnt = "🌀"; 
                        else if(v===4) cnt = "🎁"; else if(v===5) cnt = "⛲"; else if(v===6) cnt = "🛒";

                        html += `<div class="map-tile ${cls}" style="background:${v===1?'':z.floor}">${cnt}</div>`;
                    }
                }
                document.getElementById('map-grid').innerHTML = html;
            },
            move(dx, dy) {
                let tx = this.px+dx, ty = this.py+dy;
                if(this.grid[ty][tx] !== 1) {
                    this.px = tx; this.py = ty; Audio.fx.step();
                    let tile = this.grid[ty][tx];
                    if(tile === 2) return Combat.start();
                    if(tile === 3) { 
                        Game.state.zIdx++; 
                        if(Game.state.zIdx >= DB.zones.length) { alert("ПОБЕДА!"); return UI.switchScreen('screen-menu'); }
                        UI.toast("Вы спустились глубже...", "#aa55ff"); this.generate(Game.state.zIdx); return; 
                    }
                    if(tile === 4) { 
                        let g = 15 + Math.floor(Math.random()*15); Game.player.gold += g; Game.player.dust += 2;
                        UI.toast(`Найдено: ${g}💰 и 2💎`, "#ffff55"); Audio.fx.loot(); this.grid[ty][tx]=0; 
                    }
                    if(tile === 5) { Game.player.hp = Game.getMaxHp(); UI.toast("Здоровье восстановлено!", "#55ff55"); Audio.fx.loot(); this.grid[ty][tx]=0; }
                    if(tile === 6) { this.shop(); this.grid[ty][tx]=0; }
                    this.draw();
                }
            },
            shop() {
                if(Game.player.gold >= 40) {
                    Game.player.gold -= 40; let item = DB.loot[Math.floor(Math.random()*DB.loot.length)];
                    Game.player.inv.push(item); UI.toast(`Торговец продал: ${item.icon} ${item.name}`, "#ffaa00"); Audio.fx.loot();
                } else { UI.toast("Торговец: Нужно 40💰!", "#ff5555"); Audio.fx.err(); }
            }
        };

        // --- 5. ЛАГЕРЬ И ИНВЕНТАРЬ ---
        const Camp = {
            open() {
                let p = Game.player; p.maxHp = Game.getMaxHp();
                document.getElementById('camp-hero').innerText = Game.getHero().name;
                document.getElementById('camp-lvl').innerText = p.lvl;
                document.getElementById('camp-dmg').innerText = Game.getDmg();
                document.getElementById('camp-hp').innerText = `${p.hp}/${p.maxHp}`;
                document.getElementById('camp-exp').style.width = `${(p.exp/p.nExp)*100}%`;
                
                ['weapon','armor','artifact'].forEach(t => {
                    document.getElementById(`eq-${t.substring(0,3)}`).innerHTML = p.eq[t] ? `<div style='font-size:16px'>${p.eq[t].icon}</div><div style='font-size:5px'>+${p.eq[t].stat}</div>` : (t==='weapon'?'⚔️':t==='armor'?'🛡️':'🔮');
                });

                let html = "";
                p.inv.forEach((it, i) => { html += `<div class="inv-slot ${it.rare}" onmousedown="Camp.press(${i})" onmouseup="Camp.release()" onmouseleave="Camp.release()" ontouchstart="Camp.press(${i})" ontouchend="Camp.release()">${it.icon}</div>`; });
                document.getElementById('inv-list').innerHTML = html;
                UI.switchScreen('screen-camp');
            },
            equip(idx) {
                Audio.fx.step(); let it = Game.player.inv[idx];
                if(Game.player.eq[it.type]) Game.player.inv.push(Game.player.eq[it.type]);
                Game.player.eq[it.type] = it; Game.player.inv.splice(idx, 1);
                UI.toast(`Надето: ${it.name}`, "#55ff55"); this.open();
            },
            unequip(type) { if(Game.player.eq[type]) { Game.player.inv.push(Game.player.eq[type]); Game.player.eq[type] = null; Audio.fx.step(); this.open(); } },
            
            pTimer: null,
            press(idx) { this.pTimer = setTimeout(() => { Game.player.inv.splice(idx,1); Game.player.dust += 5; UI.toast("Разобрано! +5💎", "#aa55ff"); Audio.fx.loot(); this.open(); }, 600); },
            release() { if(this.pTimer){ clearTimeout(this.pTimer); this.pTimer=null; this.equip(arguments[0] || 0); } }, // Упрощенный хак для тапов
            
            craft() { if(Game.player.dust>=15){ Game.player.dust-=15; let it = DB.loot[Math.floor(Math.random()*DB.loot.length)]; Game.player.inv.push(it); UI.toast(`Скрафчено: ${it.icon}`, "#aa55ff"); Audio.fx.loot(); this.open(); } else { UI.toast("Мало пыли!", "#ff4444"); Audio.fx.err(); } },
            heal() { if(Game.player.gold>=15){ Game.player.gold-=15; Game.player.hp = Game.getMaxHp(); UI.toast("Вы исцелены!", "#55ff55"); Audio.fx.loot(); this.open(); } else { UI.toast("Мало золота!", "#ff4444"); Audio.fx.err(); } }
        };

        // --- 6. БОЕВАЯ СИСТЕМА ---
        const Combat = {
            enemy: null, shield: 0, turn: 'player', logBox: null,
            start() {
                Audio.playTrack('battle'); this.logBox = document.getElementById('log'); this.logBox.innerHTML = "";
                let pool = DB.zones[Game.state.zIdx].mobs;
                this.enemy = { ...pool[Math.floor(Math.random()*pool.length)] }; this.enemy.maxHp = this.enemy.hp;
                
                Game.player.mana = 3; this.shield = (Game.state.hero === 'тигрил') ? 50 : 0; this.turn = 'player';
                
                document.getElementById('bt-p-name').innerText = Game.getHero().name;
                document.getElementById('hero-sprite').innerText = Game.getHero().sprite;
                document.getElementById('bt-e-name').innerText = this.enemy.name;
                document.getElementById('enemy-sprite').innerText = this.enemy.sprite;
                
                this.updateUI(); UI.switchScreen('screen-battle'); this.log("Битва началась!", "#ffff55");
            },
            updateUI() {
                let p = Game.player; p.maxHp = Game.getMaxHp();
                document.getElementById('bt-p-hp-text').innerText = `${p.hp}/${p.maxHp}`;
                document.getElementById('bt-p-hp').style.width = `${(p.hp/p.maxHp)*100}%`;
                document.getElementById('bt-p-shield').style.width = `${(this.shield/p.maxHp)*100}%`;
                document.getElementById('bt-p-mana').innerText = `${p.mana}/4`;
                document.getElementById('bt-e-hp').style.width = `${(this.enemy.hp/this.enemy.maxHp)*100}%`;
                
                let my = (this.turn === 'player');
                document.getElementById('sk-1').disabled = !my;
                document.getElementById('sk-2').disabled = !my || p.mana < 1;
                document.getElementById('sk-3').disabled = !my || p.mana < 1;
                document.getElementById('sk-4').disabled = !my || p.mana < 3;
            },
            log(msg, col="#aaa") { this.logBox.innerHTML += `<div style="color:${col}; margin-bottom:2px;">> ${msg}</div>`; this.logBox.scrollTop = this.logBox.scrollHeight; },
            anim(id, cls) { let el = document.getElementById(id); el.classList.remove('anim-float'); el.classList.add(cls); setTimeout(()=>{ el.classList.remove(cls); el.classList.add('anim-float'); }, 300); },
            
            useSkill(type) {
                if(this.turn !== 'player') return;
                let dmg = Game.getDmg(), p = Game.player, hero = Game.state.hero;
                this.anim('hero-sprite', 'anim-atk-l'); Audio.fx.hit();

                if(type===1) {
                    let d = Math.floor(dmg*(hero==='мия'&&Math.random()<0.3 ? 2 : 1));
                    this.enemy.hp -= d; p.mana = Math.min(4, p.mana+(hero==='госсен'?2:1));
                    if(hero==='алукард') { let l=Math.floor(d*0.3); p.hp=Math.min(p.maxHp, p.hp+l); this.log(`Вампиризм: +${l}ОЗ`, "#55ff55"); }
                    this.log(`Атака: -${d} урона`, "#ff5555");
                }
                else if(type===2) {
                    p.mana -= 1; let d = Math.floor(dmg*1.5); this.enemy.hp -= d;
                    this.log(`Магия: -${d} урона`, "var(--mana)");
                }
                else if(type===3) {
                    p.mana -= 1; let s = Math.floor((20 + (p.eq.armor?p.eq.armor.stat:0))*(hero==='тигрил'?2:1.2)); this.shield += s;
                    this.log(`Щит активирован: +${s}`, "#aaaaaa"); Audio.fx.step();
                }
                else if(type===4) {
                    p.mana -= 3; let d = Math.floor(dmg*3); if(hero==='госсен' && this.enemy.hp < this.enemy.maxHp/2) d = Math.floor(d*1.5);
                    this.enemy.hp -= d; this.log(`УЛЬТИМЕЙТ: -${d} урона!`, "var(--accent)");
                }

                if(this.enemy.hp <= 0) return this.end(true);
                this.turn = 'enemy'; this.updateUI(); setTimeout(() => this.enemyTurn(), 800);
            },
            enemyTurn() {
                this.anim('enemy-sprite', 'anim-atk-r');
                let d = this.enemy.dmg[0] + Math.floor(Math.random()*(this.enemy.dmg[1]-this.enemy.dmg[0]));
                
                if(this.shield > 0) {
                    if(this.shield >= d) { this.shield -= d; d = 0; this.log("Урон полностью заблокирован!", "#aaa"); }
                    else { d -= this.shield; this.shield = 0; }
                }
                if(d > 0) { Game.player.hp -= d; this.log(`${this.enemy.name} бьет: -${d} ОЗ`, "#ff4444"); Audio.fx.err(); }
                
                if(Game.player.hp <= 0) return this.end(false);
                this.turn = 'player'; this.updateUI();
            },
            end(win) {
                if(win) {
                    let xp = 40 + Game.state.zIdx*20; let g = 10 + Math.floor(Math.random()*15);
                    Game.player.exp += xp; Game.player.gold += g;
                    UI.toast(`Победа! +${xp}XP | +${g}💰`, "#ffff55");
                    if(Game.player.exp >= Game.player.nExp) {
                        Game.player.lvl++; Game.player.exp = 0; Game.player.nExp = Math.floor(Game.player.nExp*1.5);
                        Game.player.hp = Game.getMaxHp(); UI.toast("УРОВЕНЬ ПОВЫШЕН!", "#aa55ff");
                    }
                    Map.grid[Map.py][Map.px] = 0; Map.draw(); Audio.playTrack('explore'); UI.switchScreen('screen-adventure');
                } else {
                    alert("ВЫ ПОГИБЛИ. Мир поглощен Бездной."); Audio.playTrack(null); UI.switchScreen('screen-menu');
                }
            }
        };

        // --- 7. UI ДВИЖОК ---
        const UI = {
            switchScreen(id) {
                document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
                document.getElementById(id).classList.add('active'); Audio.fx.step();
                if(id==='screen-settings') this.updateSettings();
            },
            updateSettings() {
                let h = Game.getHero();
                document.getElementById('cfg-hero').innerText = h.name;
                document.getElementById('cfg-sfx').innerText = Audio.sfx ? "ВКЛ" : "ВЫКЛ";
                document.getElementById('cfg-music').innerText = Audio.music ? "ВКЛ" : "ВЫКЛ";
                document.getElementById('hero-desc').innerHTML = `${h.desc}<br><br><span style='color:var(--hp)'>Баз. ОЗ: ${h.hp}</span><br><span style='color:var(--accent)'>Баз. Урон: ${h.dmg}</span>`;
            },
            toast(msg, color="#fff") {
                let box = document.getElementById('toast-container');
                let t = document.createElement('div'); t.className = 'toast';
                t.style.borderColor = color; t.innerText = msg;
                box.appendChild(t); setTimeout(() => t.remove(), 2400);
            }
        };

        // УПРАВЛЕНИЕ КЛАВИАТУРОЙ
        window.addEventListener('keydown', (e) => {
            if(document.getElementById('screen-adventure').classList.contains('active')) {
                if(['w','ArrowUp'].includes(e.key)) Map.move(0, -1);
                if(['s','ArrowDown'].includes(e.key)) Map.move(0, 1);
                if(['a','ArrowLeft'].includes(e.key)) Map.move(-1, 0);
                if(['d','ArrowRight'].includes(e.key)) Map.move(1, 0);
            } else if(document.getElementById('screen-battle').classList.contains('active')) {
                if(['1','2','3','4'].includes(e.key)) Combat.useSkill(parseInt(e.key));
            }
        });

        UI.updateSettings();
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(GAME_HTML)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
