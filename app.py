from flask import Flask, render_template_string

app = Flask(__name__)

GAME_HTML = r'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>MLBB RPG: ABYSSAL ASCENSION v13.0</title>
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
    <style>
        :root { 
            --bg: #020205; --panel: #0a0a14; --border: #3a3a5c; --text: #e0e0f0; 
            --acc: #ffaa00; --hp: #ff3333; --mana: #33aaff; --gold: #ffdd33; 
            --dust: #aa33ff; --exp: #33ff33; --stamina: #ff8833;
        }
        * { box-sizing: border-box; user-select: none; -webkit-user-select: none; }
        body { 
            font-family: 'Press Start 2P', cursive; background: var(--bg); color: var(--text); 
            margin: 0; padding: 0; font-size: 8px; text-align: center; overflow: hidden; 
            height: 100vh; display: flex; justify-content: center; align-items: center; 
        }
        #game { 
            width: 100%; max-width: 1400px; height: 100%; max-height: 100vh; 
            display: flex; flex-direction: column; background: radial-gradient(circle at center, #111122 0%, #010103 100%); 
            border: 4px solid var(--border); box-shadow: 0 0 60px rgba(0,0,0,0.9); 
            padding: 8px; position: relative; overflow: hidden; transition: all 0.3s ease;
        }
        
        :fullscreen #game, :-webkit-full-screen #game { border: none; max-width: 100vw; max-height: 100vh; padding: 10px; border-radius: 0; }

        .screen { display: none; height: 100%; flex-direction: column; gap: 8px; overflow: hidden; }
        .screen.active { display: flex; animation: fade 0.4s ease; }
        .col { width: 100%; display: flex; flex-direction: column; gap: 6px; height: 100%; overflow: hidden; }
        
        @media (orientation: landscape) and (min-width: 600px) {
            #game { flex-direction: row; padding: 12px; }
            .screen { flex-direction: row !important; width: 100%; gap: 16px; }
            .col { width: 50%; }
        }

        h1 { font-size: 16px; color: var(--acc); text-shadow: 2px 2px #000; margin: 4px 0; line-height: 1.4; }
        h2 { font-size: 10px; color: #aaa; margin: 4px 0; }
        .panel { background: var(--panel); border: 2px solid var(--border); box-shadow: 4px 4px 0px #000; padding: 8px; border-radius: 4px; overflow-y: auto; }
        
        .btn { 
            font-family: inherit; background: linear-gradient(180deg, #1c1c3a, #0f0f1f); color: #fff; 
            border: 2px outset #556688; padding: 12px; cursor: pointer; border-radius: 4px; 
            width: 100%; font-size: 8px; margin-top: 4px; transition: 0.1s; text-transform: uppercase; text-shadow: 1px 1px #000;
        }
        .btn:hover { background: linear-gradient(180deg, #2a2a50, #15152b); border-color: #7788aa; }
        .btn:active { border-style: inset; background: #0a0a14; transform: translateY(2px); }
        .btn:disabled { opacity: 0.3; cursor: not-allowed; filter: grayscale(1); transform: none; }
        .btn-acc { color: var(--acc); border-color: #886600; }
        
        /* ГЛОБАЛЬНАЯ КАРТА (КАМЕРА) */
        #viewport { 
            width: 100%; height: 100%; flex-grow: 1; margin: 0; border: 4px solid #334; 
            background: #000; position: relative; overflow: hidden; box-shadow: inset 0 0 40px #000; border-radius: 4px;
        }
        #map-container { position: absolute; transition: transform 0.2s linear; }
        .map-row { display: flex; }
        .tile { 
            width: 32px; height: 32px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; 
            font-size: 18px; background: #111a11; border: 1px solid #1a221a; transition: 0.2s; position: relative;
        }
        .tile.fog { background: #000; filter: brightness(0); border-color: #000; }
        .tile.dim { filter: brightness(0.4); }
        .tile.wall { background: #0c0c12; color: #223; box-shadow: inset 0 0 5px #000; border-color: #111; }

        .dpad { display: grid; grid-template-columns: repeat(3, 1fr); width: 100%; max-width: 220px; margin: auto; gap: 6px; }
        .dbtn { font-family: inherit; font-size: 20px; background: #252542; color: #fff; border: 3px outset #558; padding: 15px 0; border-radius: 8px; }
        .dbtn:active { border-style: inset; background: #15152b; color: var(--acc); }

        .bar { width: 100%; height: 12px; background: #111; border: 1px solid #555; position: relative; margin: 4px 0; border-radius: 2px; box-shadow: inset 0 0 5px #000; }
        .fill { height: 100%; transition: width 0.3s ease; }
        .text-overlay { position: absolute; width: 100%; text-align: center; top: 2px; left: 0; font-size: 6px; color: #fff; text-shadow: 1px 1px #000; }

        /* БОЙ */
        .stage { position: relative; height: 140px; background: #020208; border: 2px solid #333; overflow: hidden; border-radius: 4px; box-shadow: inset 0 0 20px #000; }
        .sprite { font-size: 50px; position: absolute; bottom: 20px; width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; filter: drop-shadow(0 5px 5px rgba(0,0,0,0.8)); transition: all 0.2s ease; }
        #h-spr { left: 15%; transform: scaleX(-1); } #e-spr { right: 15%; }
        
        .floating-text { position: absolute; font-size: 10px; font-weight: bold; text-shadow: 1px 1px 0 #000; animation: floatUp 1.2s forwards; pointer-events: none; z-index: 50; }
        .status-badge { position: absolute; top: -10px; font-size: 12px; display: flex; gap: 2px; }
        
        #toasts { position: absolute; top: 15px; width: 100%; display: flex; flex-direction: column; align-items: center; pointer-events: none; z-index: 1000; gap: 5px; }
        .toast { background: rgba(5,5,15,0.95); border: 2px solid var(--acc); color: #fff; padding: 10px 20px; border-radius: 4px; font-size: 8px; animation: tAnim 3s forwards; box-shadow: 0 5px 15px rgba(0,0,0,0.9); }
        
        /* ИНВЕНТАРЬ И СКИЛЛЫ */
        .inv { display: grid; grid-template-columns: repeat(auto-fill, minmax(40px, 1fr)); gap: 4px; margin: 4px 0; overflow-y: auto; max-height: 180px; padding: 4px; }
        .slot { background: #05050f; border: 2px solid #333; aspect-ratio: 1; display: flex; align-items: center; justify-content: center; font-size: 20px; cursor: pointer; border-radius: 4px; position: relative; transition: 0.1s; box-shadow: inset 0 0 10px #000; }
        .slot:hover { transform: scale(1.05); z-index: 10; border-color: #fff; }
        .slot .lvl { position: absolute; bottom: 2px; right: 2px; font-size: 6px; background: rgba(0,0,0,0.8); padding: 2px; border-radius: 2px; color: #fff; }
        .slot .eq-mark { position: absolute; top: 2px; left: 2px; font-size: 6px; color: #5f5; }
        
        .tier-0 { border-color: #666; } .tier-1 { border-color: #5f5; box-shadow: inset 0 0 5px #5f5; } 
        .tier-2 { border-color: #55f; box-shadow: inset 0 0 10px #55f; } .tier-3 { border-color: #a3f; box-shadow: inset 0 0 15px #a3f; } 
        .tier-4 { border-color: #fa0; box-shadow: inset 0 0 20px #fa0; } .tier-5 { border-color: #f33; box-shadow: inset 0 0 25px #f33; animation: pulse 2s infinite; }

        .stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 4px; font-size: 7px; text-align: left; }
        .stat-box { background: rgba(0,0,0,0.6); padding: 6px; border: 1px solid #334; border-radius: 2px; display: flex; justify-content: space-between; }

        #modal { display: none; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); z-index: 500; justify-content: center; align-items: center; }
        .modal-content { background: var(--panel); border: 4px solid var(--acc); padding: 20px; width: 90%; max-width: 450px; text-align: center; border-radius: 8px; box-shadow: 0 0 40px #000; max-height: 90vh; overflow-y: auto; }

        /* АНИМАЦИИ */
        @keyframes fade { from { opacity: 0; transform: scale(0.98); } to { opacity: 1; transform: scale(1); } }
        @keyframes floatUp { 0% { opacity: 1; transform: translateY(0) scale(1); } 100% { opacity: 0; transform: translateY(-50px) scale(1.5); } }
        @keyframes tAnim { 0%, 100% { opacity: 0; transform: translateY(-20px); } 10%, 90% { opacity: 1; transform: translateY(0); } }
        @keyframes atkL { 0%, 100% { left: 15%; } 50% { left: 45%; transform: scaleX(-1) scale(1.5) rotate(20deg); z-index: 10; } }
        @keyframes atkR { 0%, 100% { right: 15%; } 50% { right: 45%; transform: scale(1.5) rotate(-20deg); z-index: 10; } }
        @keyframes pulse { 0%, 100% { filter: brightness(1); } 50% { filter: brightness(1.6); } }
        @keyframes shake { 0%, 100% { transform: translateX(0); } 25% { transform: translateX(-5px); } 75% { transform: translateX(5px); } }
        .anim-idle { animation: float 2.5s infinite ease-in-out; }
        @keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-8px); } }
    </style>
</head>
<body>

    <div id="game">
        <div id="toasts"></div>
        
        <div id="modal">
            <div class="modal-content" id="modal-body"></div>
        </div>

        <!-- ==================== МЕНЮ ==================== -->
        <div id="scr-menu" class="screen active">
            <div class="col" style="justify-content: center; align-items: center;">
                <h1 style="font-size: 28px; line-height: 1.2;">MLBB RPG<br><span style="color:#fff; font-size:12px;">ABYSSAL ASCENSION</span></h1>
                <p style="font-size: 6px; color: #8a8ab0; margin-top: 10px;">MEGA BUILD v13.0</p>
                <div style="font-size: 80px; margin: 30px 0; animation: float 4s infinite;">🌌</div>
            </div>
            <div class="col" style="justify-content: center;">
                <div class="panel">
                    <button class="btn btn-acc" style="font-size: 14px; padding: 20px;" onclick="Game.newGame()">НОВАЯ ИГРА</button>
                    <button class="btn" onclick="Game.load()">ПРОДОЛЖИТЬ (АВТОСОХРАНЕНИЕ)</button>
                    <button class="btn" onclick="UI.show('scr-hero')">ВЫБОР КЛАССА</button>
                    <button class="btn" style="background:#223;" onclick="UI.toggleFullscreen()">ПОЛНЫЙ ЭКРАН 🔲</button>
                </div>
            </div>
        </div>

        <!-- ==================== ВЫБОР ГЕРОЯ ==================== -->
        <div id="scr-hero" class="screen">
            <div class="col">
                <h1>ВЫБОР ЧЕМПИОНА</h1>
                <div class="panel" style="display:flex; align-items:center; justify-content:space-between; flex:1;">
                    <button class="btn" style="width:25%; height:100%; font-size:20px;" onclick="Game.changeHero(-1)">◄</button>
                    <div id="hero-sprite" style="font-size:90px; width:50%; animation: float 3s infinite;">⚔️</div>
                    <button class="btn" style="width:25%; height:100%; font-size:20px;" onclick="Game.changeHero(1)">►</button>
                </div>
            </div>
            <div class="col">
                <div id="hero-info" class="panel" style="text-align:left; line-height:1.6; flex:1; font-size: 8px;"></div>
                <button class="btn btn-acc" onclick="UI.show('scr-menu')">ПРИНЯТЬ СУДЬБУ</button>
            </div>
        </div>

        <!-- ==================== КАРТА ==================== -->
        <div id="scr-adv" class="screen">
            <div class="col">
                <div class="panel" style="padding: 6px; display:flex; justify-content:space-between; font-size:8px;">
                    <span style="color:var(--hp)">❤️ <span id="a-hp"></span></span>
                    <span style="color:var(--mana)">⚡ <span id="a-mp"></span></span>
                    <span style="color:var(--gold)">💰 <span id="a-gld"></span></span>
                    <span style="color:#aaa">Этаж <span id="a-floor" style="color:var(--acc)"></span></span>
                </div>
                <div id="viewport">
                    <div id="map-container"></div>
                </div>
                <div class="panel" style="padding: 4px; font-size: 6px; color: #888; text-align:left; display:flex; justify-content:space-between;">
                    <span id="a-loc" style="color:#fff"></span>
                    <span>Кирки: <span id="a-pick" style="color:#fff"></span> ⛏️ | Ключи: <span id="a-key" style="color:#fff"></span> 🗝️</span>
                </div>
            </div>
            <div class="col">
                <div class="dpad">
                    <div></div><button class="dbtn" onclick="Map.move(0,-1)">▲</button><div></div>
                    <button class="dbtn" onclick="Map.move(-1,0)">◄</button>
                    <button class="dbtn" style="background:#4a235a; color:var(--acc); font-size:12px;" onclick="Camp.open()">🎒<br><span style="font-size:6px;color:#fff;">ЛАГЕРЬ</span></button>
                    <button class="dbtn" onclick="Map.move(1,0)">►</button>
                    <div></div><button class="dbtn" onclick="Map.move(0,1)">▼</button><div></div>
                </div>
                <div class="panel" id="adv-log" style="flex:1; overflow-y: auto; background: #010104; color: #aaa; font-size: 7px; line-height: 1.5; text-align: left;"></div>
                <button class="btn" style="background:#322;" onclick="UI.show('scr-menu')">МЕНЮ / СОХРАНИТЬ</button>
            </div>
        </div>

        <!-- ==================== ЛАГЕРЬ ==================== -->
        <div id="scr-camp" class="screen">
            <div class="col">
                <div class="panel" style="display:flex; justify-content:space-between; align-items:center;">
                    <h2 style="margin:0; color:var(--acc); font-size:12px;" id="c-name">ИМЯ</h2>
                    <span style="font-size:8px;">УР <span id="c-lvl" style="color:var(--acc)"></span></span>
                </div>
                <div class="panel">
                    <div class="bar"><div id="c-exp" class="fill" style="background:var(--exp); width:0%;"></div><div class="text-overlay">ОПЫТ: <span id="c-xp-txt"></span></div></div>
                    <div class="stat-grid" style="margin-top: 8px;">
                        <div class="stat-box"><span>❤️ ОЗ:</span> <span id="c-hp" style="color:var(--hp)"></span></div>
                        <div class="stat-box"><span>⚡ МАНА:</span> <span id="c-mp" style="color:var(--mana)"></span></div>
                        <div class="stat-box"><span>⚔️ УРОН:</span> <span id="c-dmg" style="color:var(--acc)"></span></div>
                        <div class="stat-box"><span>🛡️ ЗАЩИТА:</span> <span id="c-arm" style="color:#aaa"></span></div>
                        <div class="stat-box"><span>💨 СКОРОСТЬ:</span> <span id="c-spd" style="color:#f8f"></span></div>
                        <div class="stat-box"><span>🎯 КРИТ:</span> <span id="c-crt" style="color:#ff5"></span>%</div>
                    </div>
                    <button class="btn btn-acc" style="margin-top:8px;" onclick="Skills.open()">🌳 ДРЕВО НАВЫКОВ (<span id="c-sp">0</span>)</button>
                </div>
                <div class="panel">
                    <h2 style="margin-top:0;">ЭКИПИРОВКА</h2>
                    <div style="display:flex; gap:6px; justify-content:center;">
                        <div class="slot" id="eq-w" onclick="Camp.unequip('w')">⚔️</div>
                        <div class="slot" id="eq-a" onclick="Camp.unequip('a')">🛡️</div>
                        <div class="slot" id="eq-r" onclick="Camp.unequip('r')">🔮</div>
                    </div>
                </div>
            </div>
            <div class="col">
                <div class="panel" style="flex:1; display:flex; flex-direction:column;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:4px; font-size:8px;">
                        <span>ИНВЕНТАРЬ (<span id="c-inv-c"></span>/24)</span>
                        <span style="color:var(--dust)">💎 <span id="c-dst"></span></span>
                    </div>
                    <div class="inv" id="inventory"></div>
                </div>
                <div style="display:flex; gap:4px;">
                    <button class="btn" style="color:var(--dust);" onclick="Camp.craft()">🛠️ КУЗНЯ (30💎)</button>
                    <button class="btn" style="color:var(--hp);" onclick="Camp.buyPotion()">🧪 ЗЕЛЬЕ (50💰)</button>
                </div>
                <button class="btn" style="background:#222;" onclick="UI.show('scr-adv')">НА КАРТУ</button>
            </div>
        </div>

        <!-- ==================== БОЙ ==================== -->
        <div id="scr-bat" class="screen">
            <div class="col">
                <div class="panel" style="display:flex; justify-content:space-between; font-size:9px;">
                    <span id="b-pn" style="color:var(--mana); font-weight:bold;">ГЕРОЙ</span>
                    <span style="color:#fff; font-size:7px;">VS</span>
                    <span id="b-en" style="color:var(--hp); font-weight:bold;">ВРАГ</span>
                </div>
                
                <div class="stage" id="bat-stage">
                    <div class="status-badge" id="p-buffs" style="left:10px;"></div>
                    <div class="status-badge" id="e-buffs" style="right:10px;"></div>
                    
                    <div id="player-sprite" class="sprite anim-idle">⚔️</div>
                    <div id="enemy-sprite" class="sprite anim-idle">👹</div>
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
                        <div id="b-psh" class="fill" style="background:#77a; position:absolute; top:0; left:0; opacity:0.8; width:0%;"></div>
                    </div>
                </div>
            </div>
            
            <div class="col">
                <!-- ATB ТАЙМЕРЫ -->
                <div class="panel" style="padding:4px;">
                    <div style="font-size:6px; color:#aaa; margin-bottom:2px; text-align:left;">ИНДИКАТОР ХОДА (СКОРОСТЬ):</div>
                    <div class="bar" style="height:6px;"><div id="atb-p" class="fill" style="background:var(--mana);"></div></div>
                    <div class="bar" style="height:6px;"><div id="atb-e" class="fill" style="background:var(--hp);"></div></div>
                </div>
                
                <div class="panel" id="battle-log" style="flex:1;"></div>
                
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px;">
                    <button class="btn" id="sk-1" onclick="Combat.action(1)">⚔️ Атака</button>
                    <button class="btn" id="sk-2" onclick="Combat.action(2)">✨ Навык (2⚡)</button>
                    <button class="btn" id="sk-3" onclick="Combat.action(3)">🛡️ Блок (1⚡)</button>
                    <button class="btn btn-acc" id="sk-4" onclick="Combat.action(4)">☄️ УЛЬТ (4⚡)</button>
                </div>
            </div>
        </div>

    </div>

<script>
// ==================== АУДИО ДВИЖОК ====================
const Snd = {
    ctx: null, on: true, mOn: true,
    init() { if(!this.ctx && this.on) { this.ctx = new (window.AudioContext || window.webkitAudioContext)(); } },
    play(type) {
        if(!this.on) return; this.init(); if(!this.ctx) return;
        const o = this.ctx.createOscillator(), g = this.ctx.createGain();
        o.connect(g); g.connect(this.ctx.destination);
        const t = this.ctx.currentTime;
        if(type==='hit') { o.type='sawtooth'; o.frequency.setValueAtTime(150, t); o.frequency.exponentialRampToValueAtTime(40, t+0.1); g.gain.setValueAtTime(0.2, t); g.gain.linearRampToValueAtTime(0, t+0.1); o.start(t); o.stop(t+0.1); }
        else if(type==='crit') { o.type='square'; o.frequency.setValueAtTime(300, t); o.frequency.exponentialRampToValueAtTime(100, t+0.2); g.gain.setValueAtTime(0.3, t); g.gain.linearRampToValueAtTime(0, t+0.2); o.start(t); o.stop(t+0.2); }
        else if(type==='skill') { o.type='triangle'; o.frequency.setValueAtTime(400, t); o.frequency.linearRampToValueAtTime(800, t+0.2); g.gain.setValueAtTime(0.2, t); g.gain.linearRampToValueAtTime(0, t+0.2); o.start(t); o.stop(t+0.2); }
        else if(type==='ult') { o.type='sawtooth'; o.frequency.setValueAtTime(100, t); o.frequency.linearRampToValueAtTime(600, t+0.5); g.gain.setValueAtTime(0.4, t); g.gain.linearRampToValueAtTime(0, t+0.5); o.start(t); o.stop(t+0.5); }
        else if(type==='loot') { o.type='sine'; o.frequency.setValueAtTime(500, t); o.frequency.setValueAtTime(800, t+0.1); g.gain.setValueAtTime(0.2, t); g.gain.linearRampToValueAtTime(0, t+0.2); o.start(t); o.stop(t+0.2); }
        else if(type==='err') { o.type='sawtooth'; o.frequency.setValueAtTime(100, t); g.gain.setValueAtTime(0.2, t); g.gain.linearRampToValueAtTime(0, t+0.15); o.start(t); o.stop(t+0.15); }
        else if(type==='step') { o.type='triangle'; o.frequency.setValueAtTime(80, t); g.gain.setValueAtTime(0.05, t); g.gain.linearRampToValueAtTime(0, t+0.05); o.start(t); o.stop(t+0.05); }
    }
};

// ==================== БАЗА ДАННЫХ ====================
const DB = {
    heroes: [
        { id:'alu', n:'АЛУКАРД', spr:'⚔️', hp:280, mp:4, dmg:35, def:15, spd:10, crt:10, desc:'Боец. Лечится от атак.' },
        { id:'mia', n:'МИЯ', spr:'🏹', hp:190, mp:5, dmg:45, def:8, spd:18, crt:30, desc:'Стрелок. Высокая скорость и крит.' },
        { id:'tig', n:'ТИГРИЛ', spr:'🛡️', hp:380, mp:4, dmg:24, def:25, spd:6, crt:5, desc:'Танк. Крепкая броня, мощные щиты.' },
        { id:'gus', n:'ГОССЕН', spr:'🗡️', hp:210, mp:6, dmg:40, def:10, spd:22, crt:20, desc:'Убийца. Очень быстрый, частые ходы.' },
        { id:'eud', n:'ЭЙДОРА', spr:'⚡', hp:170, mp:8, dmg:50, def:6, spd:12, crt:15, desc:'Маг. Огромный урон навыками.' }
    ],
    enemies: [
        { n:"Гоблин", spr:"👺", hp:100, dmg:15, def:5, spd:10, xp:25, gld:15 },
        { n:"Паук", spr:"🕷️", hp:140, dmg:22, def:8, spd:15, xp:35, gld:25 },
        { n:"Голем", spr:"🪨", hp:300, dmg:35, def:25, spd:5, xp:60, gld:40 },
        { n:"Демон", spr:"👹", hp:450, dmg:55, def:20, spd:18, xp:100, gld:70 }
    ],
    bosses: [
        { n:"Тёмный Лорд ТАМУЗ", spr:"🔥", hp:1500, dmg:90, def:40, spd:20, xp:1000, gld:500 }
    ],
    loot: {
        w: { i:['🗡️','⚔️','🪓','🏹','🪄'], n:['Меч','Клинок','Топор','Лук','Посох'] },
        a: { i:['👕','🥋','🦺','🛡️'], n:['Куртка','Кираса','Броня','Щит'] },
        r: { i:['📿','🔮','💍','👑'], n:['Амулет','Сфера','Кольцо','Корона'] },
        pref: ['Ржавый', 'Острый', 'Магический', 'Пылающий', 'Святой', 'Проклятый', 'Мифический'],
        suf: ['Слабости', 'Ученика', 'Воина', 'Короля', 'Дракона', 'Бездны']
    }
};

// ==================== ГЕНЕРАТОР ЛУТА ====================
function genItem(bonusLvl = 0) {
    let type = ['w','a','r'][Math.floor(Math.random()*3)];
    let base = DB.loot[type];
    
    let roll = Math.random() * 100;
    let tier = 0; // 0-Common, 1-Uncommon, 2-Rare, 3-Epic, 4-Legendary, 5-Mythic
    if (roll < 3 + bonusLvl*2) tier = 5;
    else if (roll < 10 + bonusLvl*4) tier = 4;
    else if (roll < 25 + bonusLvl*5) tier = 3;
    else if (roll < 50 + bonusLvl*5) tier = 2;
    else if (roll < 80) tier = 1;

    let statType = type==='w' ? 'dmg' : (type==='a' ? 'def' : ['hp','mp','spd','crt'][Math.floor(Math.random()*4)]);
    let statVal = (tier+1) * 8 + Math.floor(Math.random()*15) + (Game.zIdx * 10);
    if(statType === 'hp') statVal *= 3;
    if(statType === 'crt' || statType === 'spd') statVal = Math.floor(statVal / 4) + 1;

    let pref = DB.loot.pref[Math.min(DB.loot.pref.length-1, tier + Math.floor(Math.random()*2))];
    let suf = DB.loot.suf[Math.min(DB.loot.suf.length-1, tier + Math.floor(Math.random()*2))];
    let name = `${pref} ${base.n[Math.floor(Math.random()*base.n.length)]} ${tier>2 ? suf : ''}`;

    return { t: type, n: name, i: base.i[Math.floor(Math.random()*base.i.length)], stat: statType, v: statVal, tr: tier, upg: 0 };
}

// ==================== СОСТОЯНИЕ ИГРЫ ====================
let Game = {
    hIdx: 0, zIdx: 0, p: null,
    
    newGame() {
        Snd.play('skill');
        this.zIdx = 0;
        let h = DB.heroes[this.hIdx];
        this.p = {
            id: h.id, n: h.n, spr: h.spr, lvl: 1, xp: 0, nxp: 100, sp: 0,
            bhp: h.hp, bmp: h.mp, bdmg: h.dmg, bdef: h.def, bspd: h.spd, bcrt: h.crt,
            hp: h.hp, mp: h.mp, gld: 100, dst: 20, keys: 1, picks: 3,
            eq: { w: null, a: null, r: null }, inv: [],
            skills: { splash: 0, regen: 0, pierce: 0 } // Прокачка скиллов
        };
        Map.generate();
        UI.show('scr-adv');
        UI.toast("Игра начата! Спускайтесь в Бездну.", "#0f0");
        this.save();
    },

    changeHero(d) { this.hIdx = (this.hIdx + d + DB.heroes.length) % DB.heroes.length; UI.updateHeroScreen(); Snd.play('step'); },

    calcStats() {
        let p = this.p;
        p.mhp = p.bhp; p.mmp = p.bmp; p.dmg = p.bdmg; p.def = p.bdef; p.spd = p.bspd; p.crt = p.bcrt;
        Object.values(p.eq).forEach(i => {
            if(i) {
                if(i.stat === 'hp') p.mhp += i.v; if(i.stat === 'mp') p.mmp += i.v;
                if(i.stat === 'dmg') p.dmg += i.v; if(i.stat === 'def') p.def += i.v;
                if(i.stat === 'spd') p.spd += i.v; if(i.stat === 'crt') p.crt += i.v;
            }
        });
        if(p.hp > p.mhp) p.hp = p.mhp;
        if(p.mp > p.mmp) p.mp = p.mmp;
    },

    addXp(amt) {
        this.p.xp += amt;
        while(this.p.xp >= this.p.nxp) {
            this.p.xp -= this.p.nxp;
            this.p.lvl++;
            this.p.nxp = Math.floor(this.p.nxp * 1.5);
            this.p.sp += 2;
            this.p.bhp += 20; this.p.bdmg += 5; this.p.bdef += 2;
            this.calcStats();
            this.p.hp = this.p.mhp; this.p.mp = this.p.mmp;
            Snd.play('ult');
            UI.toast(`🌟 НОВЫЙ УРОВЕНЬ: ${this.p.lvl}! (+2 очка навыков)`, "#ff5");
        }
    },

    save() {
        localStorage.setItem('mlbb_mega_save', JSON.stringify({ hIdx: this.hIdx, zIdx: this.zIdx, p: this.p, map: Map.getMapState() }));
        UI.toast("Прогресс автосохранен", "#55f");
    },

    load() {
        let data = localStorage.getItem('mlbb_mega_save');
        if(!data) return UI.toast("Сохранение не найдено", "#f44");
        data = JSON.parse(data);
        this.hIdx = data.hIdx; this.zIdx = data.zIdx; this.p = data.p;
        Map.setMapState(data.map);
        this.calcStats();
        UI.show('scr-adv');
        UI.toast("Игра загружена!", "#0f0");
        UI.updateAdv();
    }
};

// ==================== ГЛОБАЛЬНАЯ КАРТА (50x50 со скроллом) ====================
const Map = {
    w: 40, h: 40, grid: [], px: 1, py: 1,
    
    getMapState() { return { g: this.grid, px: this.px, py: this.py }; },
    setMapState(s) { this.grid = s.g; this.px = s.px; this.py = s.py; this.draw(); },

    generate() {
        // Cellular Automata generation
        this.grid = Array(this.h).fill().map(() => Array(this.w).fill(1)); // 1-wall
        
        // Random carve
        let cx = Math.floor(this.w/2), cy = Math.floor(this.h/2);
        this.px = cx; this.py = cy;
        this.grid[cy][cx] = 0;

        for(let i=0; i<800; i++) {
            let dir = [{x:0,y:1},{x:0,y:-1},{x:1,y:0},{x:-1,y:0}][Math.floor(Math.random()*4)];
            if(cx+dir.x>1 && cx+dir.x<this.w-2 && cy+dir.y>1 && cy+dir.y<this.h-2) {
                cx += dir.x; cy += dir.y;
                this.grid[cy][cx] = 0; // Floor
            }
        }

        // Place entities
        let floors = [];
        for(let y=1; y<this.h-1; y++) for(let x=1; x<this.w-1; x++) if(this.grid[y][x] === 0 && (x!==this.px || y!==this.py)) floors.push({x,y});
        floors.sort(() => Math.random() - 0.5);

        if(floors.length > 0) {
            let exit = floors.pop();
            this.grid[exit.y][exit.x] = Game.zIdx === 4 ? 6 : 5; // 5-Stairs, 6-Boss
        }

        let numEnemies = 20 + Game.zIdx*5;
        let numChests = 10 + Game.zIdx*2;
        
        while(floors.length > 0 && numEnemies-- > 0) { let p = floors.pop(); this.grid[p.y][p.x] = 2; } // 2-Enemy
        while(floors.length > 0 && numChests-- > 0) { let p = floors.pop(); this.grid[p.y][p.x] = Math.random()<0.3 ? 8 : 4; } // 4-Chest, 8-Key
        while(floors.length > 0 && Math.random()<0.05) { let p = floors.pop(); this.grid[p.y][p.x] = 9; } // 9-Merchant
        while(floors.length > 0 && Math.random()<0.05) { let p = floors.pop(); this.grid[p.y][p.x] = 7; } // 7-Fountain

        // Init fog
        this.fog = Array(this.h).fill().map(() => Array(this.w).fill(true));
        this.updateFog();
        this.draw();
    },

    updateFog() {
        let r = 4; // Радиус обзора
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
                if(this.fog[y][x]) {
                    cls += ' fog';
                } else {
                    let v = this.grid[y][x];
                    if(x===this.px && y===this.py) { txt = Game.p.spr; cls += ' visible'; }
                    else if(v===1) { cls += ' wall'; }
                    else if(v===2) { txt = '👾'; }
                    else if(v===4) { txt = '🧰'; }
                    else if(v===5) { txt = '🪜'; }
                    else if(v===6) { txt = '🔥'; }
                    else if(v===7) { txt = '⛲'; }
                    else if(v===8) { txt = '🗝️'; }
                    else if(v===9) { txt = '🛒'; }
                    
                    let dist = Math.max(Math.abs(x-this.px), Math.abs(y-this.py));
                    if(dist >= 4) cls += ' dim';
                }
                html += `<div class="${cls}" id="t_${x}_${y}" onclick="Map.click(${x},${y})">${txt}</div>`;
            }
            html += '</div>';
        }
        cont.innerHTML = html;
        this.centerCamera();
    },

    centerCamera() {
        const vp = document.getElementById('viewport');
        const cont = document.getElementById('map-container');
        const ts = 32; // tile size
        let cx = (vp.clientWidth / 2) - (this.px * ts) - (ts/2);
        let cy = (vp.clientHeight / 2) - (this.py * ts) - (ts/2);
        cont.style.transform = `translate(${cx}px, ${cy}px)`;
    },

    log(m, c="#aaa") { let l = document.getElementById('adv-log'); l.innerHTML += `<div style="color:${c}">> ${m}</div>`; l.scrollTop = l.scrollHeight; },

    click(x, y) {
        if(Math.abs(x-this.px)<=1 && Math.abs(y-this.py)<=1 && this.grid[y][x]===1 && Game.p.picks>0) {
            Game.p.picks--; this.grid[y][x] = 0; Snd.play('hit'); this.log("Стена пробита киркой!", "#fff"); this.updateFog(); this.draw(); UI.updateAdv();
        }
    },

    move(dx, dy) {
        let nx = this.px + dx, ny = this.py + dy;
        if(nx<0 || nx>=this.w || ny<0 || ny>=this.h) return;
        let t = this.grid[ny][nx];
        if(t === 1) return; // Wall

        this.px = nx; this.py = ny;
        Snd.play('step');
        this.updateFog();

        if(t === 2) { this.grid[ny][nx]=0; return Combat.start(false); }
        if(t === 6) { this.grid[ny][nx]=0; return Combat.start(true); }
        
        if(t === 4) {
            if(Game.p.keys > 0) {
                Game.p.keys--; this.grid[ny][nx] = 0; Snd.play('loot');
                let it = genItem(Game.zIdx); Game.p.inv.push(it);
                UI.toast(`Из сундука получено: ${it.n}!`, "var(--acc)");
                this.log(`Найден предмет: ${it.n}`);
            } else { this.log("Нужен ключ для сундука!", "#f44"); Snd.play('err'); this.px-=dx; this.py-=dy; }
        }
        else if(t === 8) { Game.p.keys++; this.grid[ny][nx]=0; Snd.play('loot'); this.log("Найден ключ! 🗝️", "#fff"); }
        else if(t === 7) { Game.p.hp=Game.p.mhp; Game.p.mp=Game.p.mmp; this.grid[ny][nx]=0; Snd.play('skill'); UI.toast("Фонтан восстановил силы!", "#5f5"); }
        else if(t === 9) { 
            if(Game.p.gld>=100) { Game.p.gld-=100; this.grid[ny][nx]=0; let it = genItem(Game.zIdx+2); Game.p.inv.push(it); Snd.play('loot'); UI.toast(`Торговец продал: ${it.n}`, "#a5f"); }
            else { this.log("У торговца вещи по 100 золота!", "#f44"); Snd.play('err'); this.px-=dx; this.py-=dy; }
        }
        else if(t === 5) {
            Snd.play('ult'); Game.zIdx++; Game.p.picks+=2;
            UI.toast(`Спуск на уровень ${Game.zIdx+1}!`, "var(--mana)");
            this.generate(); Game.save(); return;
        }

        this.draw();
        UI.updateAdv();
        if(Math.random()<0.05) Game.save(); // Рандомный автосейв
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
        document.getElementById('c-spd').textContent = Game.p.spd;
        document.getElementById('c-crt').textContent = Game.p.crt;
        
        document.getElementById('stat-points').textContent = Game.p.sp;
        document.getElementById('c-dust').textContent = Game.p.dust;
        document.getElementById('c-inv-c').textContent = Game.p.inv.length;

        ['w','a','r'].forEach(t => {
            let el = document.getElementById(`eq-${t}`);
            let it = Game.p.eq[t];
            el.className = `slot tier-${it ? it.tr : 0}`;
            el.innerHTML = it ? `${it.i}<div class="lvl">+${it.upg||0}</div>` : (t==='w'?'⚔️':t==='a'?'🛡️':'🔮');
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
        let rNames = ['Обычное', 'Необычное', 'Редкое', 'Эпическое', 'Легендарное', 'МИФИЧЕСКОЕ'];
        let rCols = ['#888', '#5f5', '#55f', '#a3f', '#fa0', '#f33'];
        let statNames = {dmg:"Атака", def:"Защита", hp:"ОЗ", mp:"Мана", spd:"Скорость", crt:"Крит %"};
        
        let html = `
            <h2 style="color:${rCols[it.tr]}; font-size:12px;">${it.i} ${it.n}</h2>
            <p style="font-size:8px; color:#aaa;">Тип: ${it.t==='w'?'Оружие':it.t==='a'?'Броня':'Реликвия'} | Редкость: ${rNames[it.tr]}</p>
            <p style="font-size:12px; color:var(--acc); margin: 15px 0;">+${it.v} ${statNames[it.stat]}</p>
            <p style="font-size:8px; color:var(--mana);">Уровень заточки: +${it.upg||0}</p>
            <div style="display:flex; flex-direction:column; gap:6px; margin-top:20px;">
                <button class="btn" style="background:#141;" onclick="Camp.equip(${idx})">НАДЕТЬ</button>
                <button class="btn" style="background:#414;" onclick="Camp.upgrade(${idx})">УЛУЧШИТЬ (15💎)</button>
                <button class="btn" style="background:#411;" onclick="Camp.scrap(${idx})">РАЗОБРАТЬ (+${5 + it.tr*5}💎)</button>
                <button class="btn" onclick="UI.closeModal()">ЗАКРЫТЬ</button>
            </div>
        `;
        UI.openModal(html);
    },

    equip(idx) {
        UI.closeModal(); Snd.play('step');
        let it = Game.p.inv[idx];
        if(Game.p.eq[it.t]) Game.p.inv.push(Game.p.eq[it.t]);
        Game.p.eq[it.t] = it;
        Game.p.inv.splice(idx, 1);
        this.open(); UI.toast(`Экипировано: ${it.n}`, "#5f5");
    },

    upgrade(idx) {
        if(Game.p.dust < 15) return UI.toast("Нужно 15 Пыли!", "#f44");
        Game.p.dust -= 15;
        let it = Game.p.inv[idx];
        it.upg = (it.upg||0) + 1;
        it.v += Math.floor(it.v * 0.1) + 2; // +10% статов + 2
        Snd.play('skill'); UI.closeModal(); this.open();
        UI.toast(`Улучшено до +${it.upg}!`, "var(--acc)");
    },

    unequip(t) {
        if(Game.p.eq[t]) {
            Game.p.inv.push(Game.p.eq[t]);
            Game.p.eq[t] = null;
            Snd.play('step'); this.open();
        }
    },

    scrap(idx) {
        let it = Game.p.inv[idx]; let d = 5 + it.tr*5 + (it.upg||0)*2;
        Game.p.inv.splice(idx, 1); Game.p.dust += d;
        Snd.play('loot'); UI.closeModal(); this.open();
        UI.toast(`Разобрано! +${d} Пыли`, "var(--dust)");
    },

    craft() {
        if(Game.p.dust < 30) return UI.toast("Нужно 30 Пыли для крафта!", "#f44");
        Game.p.dust -= 30; Snd.play('ult');
        let it = genItem(Game.p.lvl > 10 ? 3 : 1);
        Game.p.inv.push(it); this.open();
        UI.toast(`Выковано: ${it.n}!`, "var(--acc)");
    },
    
    buyPotion() {
        if(Game.p.gld < 50) return UI.toast("Нужно 50 Золота!", "#f44");
        Game.p.gld -= 50; Game.p.hp = Game.p.mhp; Game.p.mp = Game.p.mmp;
        Snd.play('skill'); this.open(); UI.toast("Здоровье и Мана полностью восстановлены!", "#5f5");
    }
};

const Skills = {
    open() {
        let s = Game.p.skills;
        let html = `
            <h2 style="color:var(--acc)">ДРЕВО ТАЛАНТОВ</h2>
            <p style="font-size:8px; margin-bottom:15px;">Очки навыков: ${Game.p.sp}</p>
            <div style="display:flex; flex-direction:column; gap:8px;">
                <button class="btn" onclick="Skills.upg('splash')">Удар по площади (Ур. ${s.splash}) - Шанс 10% нанести доп урон.</button>
                <button class="btn" onclick="Skills.upg('regen')">Регенерация (Ур. ${s.regen}) - Восст. ОЗ каждый ход.</button>
                <button class="btn" onclick="Skills.upg('pierce')">Пробивание (Ур. ${s.pierce}) - Игнор брони.</button>
            </div>
            <button class="btn" style="margin-top:15px" onclick="UI.closeModal()">ЗАКРЫТЬ</button>
        `;
        UI.openModal(html);
    },
    upg(id) {
        if(Game.p.sp <= 0) return UI.toast("Нет очков навыков!", "#f44");
        Game.p.sp--; Game.p.skills[id]++; Snd.play('loot');
        this.open(); Camp.open();
    }
};

// ==================== АКТИВНАЯ БОЕВАЯ СИСТЕМА (ATB) ====================
const Combat = {
    e: null, isBoss: false,
    atbP: 0, atbE: 0,
    bufP: { shld: 0, psn: 0, brn: 0 },
    bufE: { psn: 0, brn: 0, stn: 0 },
    loop: null, turnReady: false,

    start(boss) {
        this.isBoss = boss;
        let pool = boss ? DB.bosses : DB.enemies;
        let baseE = pool[Math.floor(Math.random()*pool.length)];
        
        // Скалирование врага
        let mult = 1 + (Game.zIdx * 0.4) + (Game.p.lvl * 0.1);
        this.e = { ...baseE, mhp: Math.floor(baseE.hp*mult), hp: Math.floor(baseE.hp*mult), dmg: Math.floor(baseE.dmg*mult), def: Math.floor(baseE.def*mult), spd: baseE.spd + Game.zIdx };
        
        this.atbP = 0; this.atbE = 0;
        this.bufP = { shld: 0, psn: 0, brn: 0 };
        this.bufE = { psn: 0, brn: 0, stn: 0 };
        
        document.getElementById('b-pn').textContent = Game.p.n;
        document.getElementById('player-sprite').textContent = Game.p.spr;
        document.getElementById('b-en').textContent = `${this.e.n} (Ур.${Game.p.lvl+Game.zIdx})`;
        document.getElementById('enemy-sprite').textContent = this.e.spr;
        document.getElementById('battle-log').innerHTML = '';
        
        UI.show('scr-bat');
        this.log(`ОПАСНОСТЬ! ${this.e.n} преграждает путь!`, "#ff5");
        Snd.play('err');
        
        this.updateUI();
        this.turnReady = false;
        this.loop = setInterval(() => this.tick(), 50);
    },

    updateUI() {
        document.getElementById('b-php-txt').textContent = `${Game.p.hp}/${Game.p.mhp}`;
        document.getElementById('b-php').style.width = `${(Game.p.hp/Game.p.mhp)*100}%`;
        document.getElementById('b-pmp-txt').textContent = `${Game.p.mp}/${Game.p.mmp}`;
        document.getElementById('b-psh').style.width = `${Math.min(100, (this.bufP.shld/Game.p.mhp)*100)}%`;
        
        document.getElementById('b-ehp-txt').textContent = `${this.e.hp}/${this.e.mhp}`;
        document.getElementById('b-ehp').style.width = `${(this.e.hp/this.e.mhp)*100}%`;
        
        document.getElementById('atb-p').style.width = `${this.atbP}%`;
        document.getElementById('atb-e').style.width = `${this.atbE}%`;

        // Кнопки
        let canAct = this.turnReady && this.atbP >= 100;
        document.getElementById('sk-1').disabled = !canAct;
        document.getElementById('sk-2').disabled = !canAct || Game.p.mp < 2;
        document.getElementById('sk-3').disabled = !canAct || Game.p.mp < 1;
        document.getElementById('sk-4').disabled = !canAct || Game.p.mp < 4;
        
        // Баффы
        document.getElementById('p-buffs').innerHTML = (this.bufP.psn>0?'☠️':'')+(this.bufP.brn>0?'🔥':'')+(this.bufP.shld>0?'🛡️':'');
        document.getElementById('e-buffs').innerHTML = (this.bufE.psn>0?'☠️':'')+(this.bufE.brn>0?'🔥':'')+(this.bufE.stn>0?'⚡':'');
    },

    tick() {
        if(this.turnReady || Game.p.hp <= 0 || this.e.hp <= 0) return;

        this.atbP += Game.p.spd * 0.1;
        this.atbE += this.e.spd * 0.1;

        if(this.atbP >= 100) { this.atbP = 100; this.turnReady = true; this.processEffects(true); }
        else if(this.atbE >= 100) { this.atbE = 100; this.turnReady = true; this.processEffects(false); setTimeout(()=>this.enemyAct(), 500); }

        this.updateUI();
    },

    processEffects(isPlayer) {
        let b = isPlayer ? this.bufP : this.bufE;
        let t = isPlayer ? Game.p : this.e;
        let id = isPlayer ? 'player-sprite' : 'enemy-sprite';
        
        if(b.psn > 0) { b.psn--; let d=Math.floor(t.mhp*0.05); t.hp-=d; this.float(id, `-${d} ЯД`, "#5f5"); }
        if(b.brn > 0) { b.brn--; let d=Math.floor(t.mhp*0.08); t.hp-=d; this.float(id, `-${d} ОЖОГ`, "#fa0"); }
        if(b.stn > 0) { b.stn--; this.float(id, "ОГЛУШЕН", "#fff"); if(!isPlayer) { this.atbE = 0; this.turnReady = false; } }
        
        if(isPlayer && Game.p.skills.regen > 0) {
            let h = Game.p.skills.regen * 10; Game.p.hp = Math.min(Game.p.mhp, Game.p.hp + h); this.float(id, `+${h}`, "#2c2");
        }
    },

    anim(id, cls) { 
        let el = document.getElementById(id); el.style.animation = 'none'; void el.offsetWidth; 
        el.style.animation = `${cls} 0.3s ease`; setTimeout(()=>el.style.animation = 'float 2.5s infinite', 300); 
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
        this.anim('player-sprite', 'atkL');
        
        let dmg = Game.p.dmg;
        if(Game.p.skills.pierce > 0) dmg += Game.p.skills.pierce * 10;

        let isCrit = Math.random()*100 < Game.p.crt;
        if(isCrit) { dmg = Math.floor(dmg * 2); Snd.play('crit'); } else Snd.play('hit');

        if(type === 1) {
            if(Game.p.id === 'alu') { let v=Math.floor(dmg*0.25); Game.p.hp=Math.min(Game.p.mhp, Game.p.hp+v); this.float('player-sprite', `+${v}`, "#2c2"); }
            Game.p.mp = Math.min(Game.p.mmp, Game.p.mp + (Game.p.id==='gus'?2:1));
            this.e.hp -= dmg; this.float('enemy-sprite', isCrit?`КРИТ! ${dmg}`:`-${dmg}`, isCrit?"var(--acc)":"#fff");
            this.log(`Атака: -${dmg} ОЗ`);
            
            if(Game.p.skills.splash > 0 && Math.random()<0.3) { let spl = Math.floor(dmg*0.5); this.e.hp-=spl; this.float('enemy-sprite', `SPLASH ${spl}`, "#fa0"); }
        }
        else if(type === 2) {
            Game.p.mp -= 2; Snd.play('skill');
            dmg = Math.floor(dmg * 1.5);
            if(Game.p.id === 'eud') { this.bufE.stn = 1; this.log("Враг парализован!", "#5af"); }
            else if(Game.p.id === 'mia') { this.bufE.psn = 2; this.log("Отравленная стрела!", "#5f5"); }
            this.e.hp -= dmg; this.float('enemy-sprite', `-${dmg}`, "var(--mana)"); this.log(`Навык: -${dmg}`);
        }
        else if(type === 3) {
            Game.p.mp -= 1; Snd.play('step');
            let s = Math.floor(Game.p.mhp * 0.2) + Game.p.def;
            if(Game.p.id === 'tig') s = Math.floor(s * 1.5);
            this.bufP.shld += s; this.float('player-sprite', `+${s} ЩИТ`, "#aaa"); this.log(`Защита: +${s}`);
        }
        else if(type === 4) {
            Game.p.mp -= 4; Snd.play('ult');
            dmg = Math.floor(dmg * 3.5);
            if(Game.p.id === 'gus' && this.e.hp < this.e.mhp/2) { dmg = Math.floor(dmg * 1.5); this.log("ФАТАЛЬНАЯ КАЗНЬ!", "#f33"); }
            this.e.hp -= dmg; this.float('enemy-sprite', `УЛЬТ! ${dmg}`, "var(--hp)"); this.log(`УЛЬТИМЕЙТ: -${dmg}`);
            document.getElementById('battle-area').style.animation = "shake 0.3s"; setTimeout(()=>document.getElementById('battle-area').style.animation="none", 300);
        }

        this.atbP = 0; this.turnReady = false; this.updateUI();
        if(this.e.hp <= 0) return setTimeout(()=>this.end(true), 500);
    },

    enemyAct() {
        if(this.e.hp <= 0) return;
        this.anim('enemy-sprite', 'atkR');
        
        if(Math.random()*100 < Game.p.dod) {
            this.float('player-sprite', "УКЛОНЕНИЕ", "#8ff"); this.log("Враг промахнулся!", "#8ff"); Snd.play('step');
        } else {
            let dmg = Math.floor(this.e.dmg * (0.8 + Math.random()*0.4));
            dmg = Math.max(1, dmg - Game.p.def); // Броня режет урон
            
            // Спец атаки боссов
            if(this.isBoss && Math.random() < 0.3) {
                dmg = Math.floor(dmg * 1.5); this.bufP.brn = 3; this.log("БОСС: ИСПЕПЕЛЯЮЩИЙ УДАР!", "#f44");
                document.getElementById('battle-area').style.animation = "shake 0.5s"; setTimeout(()=>document.getElementById('battle-area').style.animation="none", 500);
            }

            if(this.bufP.shld > 0) {
                if(this.bufP.shld >= dmg) { this.bufP.shld -= dmg; dmg = 0; this.float('player-sprite', "БЛОК", "#aaa"); }
                else { dmg -= this.bufP.shld; this.bufP.shld = 0; }
            }
            if(dmg > 0) {
                Game.p.hp -= dmg; this.float('player-sprite', `-${dmg}`, "#f44"); Snd.play('err'); this.log(`Получен урон: ${dmg}`);
            }
        }
        
        this.atbE = 0; this.turnReady = false; this.updateUI();
        if(Game.p.hp <= 0) return setTimeout(()=>this.end(false), 500);
    },

    end(win) {
        clearInterval(this.loop);
        if(win) {
            let xp = this.e.xp + (Game.zIdx * 10); let gld = this.e.gld + (Game.zIdx * 5);
            Game.p.gld += gld; Game.addXp(xp);
            UI.toast(`Победа! +${xp}XP, +${gld}💰`, "#ff5");
            if(this.isBoss) {
                alert("👑 ВЫ ПОВЕРГЛИ ТАМУЗА И ЗАПЕЧАТАЛИ БЕЗДНУ! ИГРА ПРОЙДЕНА! 👑");
                Game.zIdx = 0; Game.newGame(); return UI.show('scr-menu');
            }
            Snd.play('loot');
            UI.show('scr-adv'); UI.updateAdv();
        } else {
            alert("💀 ГЕРОЙ МЕРТВ. МОБИЯ ПАЛА ВО ТЬМУ.");
            UI.show('scr-menu');
        }
    }
};

// ==================== УПРАВЛЕНИЕ И UI ====================
const UI = {
    show(id) { document.querySelectorAll('.screen').forEach(s => s.classList.remove('active')); document.getElementById(id).classList.add('active'); Snd.play('step'); },
    toast(m, c="#fff") {
        let b = document.getElementById('toasts'), t = document.createElement('div');
        t.className = 'toast'; t.style.borderColor = c; t.innerHTML = m;
        b.appendChild(t); setTimeout(() => t.remove(), 2900);
    },
    openHeroSelect() { this.show('scr-hero'); this.updateHeroScreen(); },
    updateHeroScreen() {
        let h = DB.heroes[Game.hIdx];
        document.getElementById('hero-sprite').textContent = h.spr;
        document.getElementById('hero-info').innerHTML = `<b style="color:var(--acc);font-size:12px">${h.n}</b><br><br><span style="color:#aaa">${h.desc}</span><br><br>❤️ ОЗ: <span style="color:var(--hp)">${h.hp}</span><br>⚔️ Атака: <span style="color:var(--gold)">${h.dmg}</span><br>🛡️ Защита: <span style="color:var(--mana)">${h.def}</span><br>💨 Скорость: <span style="color:#f8f">${h.spd}</span><br>🎯 Крит: <span style="color:#ff5">${h.crt}%</span><br><br><b style="color:var(--mana)">Навык:</b> ${h.sk}<br><b style="color:var(--hp)">УЛЬТ:</b> ${h.ult}`;
    },
    updateAdv() {
        document.getElementById('a-hp').textContent = `${Game.p.hp}/${Game.p.mhp}`;
        document.getElementById('a-gld').textContent = Game.p.gld;
        document.getElementById('a-floor').textContent = Game.zIdx+1;
        document.getElementById('a-pick').textContent = Game.p.picks;
        document.getElementById('a-key').textContent = Game.p.keys;
        document.getElementById('q-count').textContent = Game.quests.filter(q=>!q.done).length;
    },
    openModal(html) { document.getElementById('modal-body').innerHTML = html; document.getElementById('modal').style.display = 'flex'; },
    closeModal() { document.getElementById('modal').style.display = 'none'; },
    toggleFullscreen() { if(!document.fullscreenElement) { document.documentElement.requestFullscreen().catch(e=>{}); } else { if(document.exitFullscreen) document.exitFullscreen(); } }
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
    # Оптимизировано для Render: использование порта из переменных окружения
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
