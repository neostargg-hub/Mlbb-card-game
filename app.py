from flask import Flask, render_template_string

app = Flask(__name__)

GAME_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>MLBB RPG: Эпоха Возрождения — v11.0</title>
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
    <style>
        :root { --bg: #030308; --panel: #090912; --border: #3d3d5c; --txt: #e0e0f0; --acc: #ffff55; --hp: #ff4444; --mana: #55aaff; --dust: #aa55ff; --gold: #ffff55; }
        * { box-sizing: border-box; }
        body { font-family: 'Press Start 2P', cursive; background: var(--bg); color: var(--txt); margin: 0; padding: 5px; font-size: 7px; text-align: center; overflow: hidden; user-select: none; -webkit-user-select: none; height: 100vh; display: flex; justify-content: center; align-items: center; }
        
        #game { width: 100%; max-width: 480px; height: 100%; max-height: 800px; display: flex; flex-direction: column; background: linear-gradient(135deg, #0b0b1a, #030308); border: 4px solid #557; box-shadow: 0 0 50px rgba(0,0,0,0.9); padding: 8px; position: relative; overflow: hidden; }
        .screen { display: none; height: 100%; flex-direction: column; justify-content: space-between; }
        .screen.active { display: flex; animation: fade 0.3s ease; }
        .col { width: 100%; display: flex; flex-direction: column; justify-content: space-between; gap: 4px; }
        
        @media (orientation: landscape) and (min-width: 600px) {
            #game { max-width: 960px; max-height: 480px; flex-direction: row; padding: 10px; }
            .screen { flex-direction: row !important; width: 100%; gap: 14px; }
            .col { width: 49%; height: 100%; }
        }

        h1 { font-size: 10px; color: var(--acc); text-shadow: 2px 2px #000; margin: 3px 0; line-height: 1.4; }
        .panel { background: var(--panel); border: 2px solid var(--border); box-shadow: 3px 3px 0px #000; padding: 6px; position: relative; }
        
        .btn { font-family: inherit; background: #1c1c3a; color: #d4af37; border: 3px outset #4a4a88; padding: 10px; cursor: pointer; border-radius: 4px; width: 100%; font-size: 8px; margin-top: 4px; transition: 0.1s; }
        .btn:active { border-style: inset; background: #111124; }
        .btn:disabled { opacity: 0.4; cursor: not-allowed; filter: grayscale(1); border-style: solid; }
        
        #viewport { width: 100%; max-width: 280px; margin: 4px auto; border: 3px solid #446; background: #000; padding: 2px; box-shadow: inset 0 0 20px #000; }
        #map-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 2px; width: 100%; }
        .tile { aspect-ratio: 1; display: flex; align-items: center; justify-content: center; font-size: 15px; background: #121e12; border-radius: 2px; transition: 0.2s; cursor: pointer; }
        .dim-1 { opacity: 0.7; filter: brightness(0.7); } .dim-2 { opacity: 0.3; filter: brightness(0.4); } .dim-3 { opacity: 0.05; filter: brightness(0.1); }
        .wall { background: #1a1a24; color: #445; }

        .dpad { display: grid; grid-template-columns: repeat(3, 1fr); width: 140px; margin: 2px auto; gap: 4px; }
        .dbtn { font-family: inherit; font-size: 16px; background: #252542; color: #fff; border: 2px outset #558; padding: 10px 0; border-radius: 6px; }
        .dbtn:active { border-style: inset; background: #15152b; color: var(--acc); }

        .bar { width: 100%; height: 12px; background: #111; border: 2px solid #fff; position: relative; margin: 3px 0; }
        .fill { height: 100%; transition: width 0.3s ease; }
        .text-overlay { position: absolute; width: 100%; text-align: center; top: 1px; left: 0; font-size: 6px; color: #fff; text-shadow: 1px 1px #000; }

        .stage { position: relative; height: 100px; background: #020208; border: 2px solid #333; overflow: hidden; }
        .sprite { font-size: 42px; position: absolute; bottom: 8px; width: 50px; height: 50px; display: flex; align-items: center; justify-content: center; }
        #h-spr { left: 15%; transform: scaleX(-1); } #e-spr { right: 15%; }
        
        .floating-text { position: absolute; font-size: 8px; font-weight: bold; text-shadow: 1px 1px 0 #000; animation: floatUp 1s forwards; pointer-events: none; z-index: 50; }
        
        #toasts { position: absolute; top: 10px; width: 100%; display: flex; flex-direction: column; align-items: center; pointer-events: none; z-index: 100; }
        .toast { background: rgba(10,10,25,0.95); border: 2px solid var(--acc); color: #fff; padding: 8px; margin-bottom: 4px; border-radius: 4px; font-size: 6px; animation: tAnim 2s forwards; }
        
        .inv { display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px; margin: 4px 0; }
        .slot { background: #05050f; border: 2px solid #333; height: 42px; display: flex; align-items: center; justify-content: center; font-size: 18px; cursor: pointer; border-radius: 4px; position: relative; }
        .slot span { position: absolute; bottom: 2px; right: 2px; font-size: 5px; background: #000; padding: 1px; border-radius: 2px; }
        .tier-0 { border-color: #aaa; } .tier-1 { border-color: #55f; } .tier-2 { border-color: #a3f; } .tier-3 { border-color: #fa0; box-shadow: inset 0 0 8px #fa0; }

        #modal { display: none; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 200; justify-content: center; align-items: center; }
        .modal-content { background: var(--panel); border: 3px solid var(--acc); padding: 15px; width: 80%; text-align: center; }

        @keyframes fade { from { opacity: 0; } to { opacity: 1; } }
        @keyframes floatUp { 0% { opacity: 1; transform: translateY(0) scale(1); } 100% { opacity: 0; transform: translateY(-30px) scale(1.5); } }
        @keyframes tAnim { 0%, 100% { opacity: 0; transform: translateY(-10px); } 10%, 90% { opacity: 1; transform: translateY(0); } }
        @keyframes atkL { 0%, 100% { left: 15%; } 50% { left: 45%; transform: scaleX(-1) scale(1.3) rotate(15deg); } }
        @keyframes atkR { 0%, 100% { right: 15%; } 50% { right: 45%; transform: scale(1.3) rotate(-15deg); } }
        .anim-idle { animation: float 2s infinite ease-in-out; }
        @keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-5px); } }
    </style>
</head>
<body>

    <div id="game">
        <div id="toasts"></div>
        
        <!-- МОДАЛЬНОЕ ОКНО ЛАВЕЛ-АПА -->
        <div id="modal">
            <div class="modal-content">
                <h1 style="color:#55ff55;">УРОВЕНЬ ПОВЫШЕН!</h1>
                <p style="font-size: 6px; color: #aaa; margin: 10px 0;">Выберите улучшение характеристик:</p>
                <button class="btn" onclick="Game.lvlUpStat('hp')">❤️ +25 Макс ОЗ</button>
                <button class="btn" onclick="Game.lvlUpStat('dmg')">⚔️ +5 Урон</button>
                <button class="btn" onclick="Game.lvlUpStat('mana')">⚡ +1 Макс Мана</button>
            </div>
        </div>

        <!-- ГЛАВНОЕ МЕНЮ -->
        <div id="scr-menu" class="screen active">
            <div class="col" style="justify-content: center;">
                <h1>MLBB RPG:<br>ЭПОХА<br>ВОЗРОЖДЕНИЯ</h1>
                <p style="font-size: 5px; color: #8a8ab0;">ВЕРСИЯ 11.0 ULTIMATE</p>
                <div style="font-size: 45px; margin: 20px 0; animation: float 3s infinite;">🌌</div>
            </div>
            <div class="col" style="justify-content: center;">
                <button class="btn" onclick="Game.start()">НАЧАТЬ ПУТЬ</button>
                <button class="btn" onclick="UI.show('scr-set')">ГЕРОИ</button>
            </div>
        </div>

        <!-- НАСТРОЙКИ / ГЕРОИ -->
        <div id="scr-set" class="screen">
            <div class="col">
                <h1>ГЕРОИ</h1>
                <div class="panel">
                    <div style="margin-bottom:8px;">КЛАСС: <button class="btn" style="padding:6px; background:#334;" onclick="Game.nextHero()" id="cfg-hero">АЛУКАРД</button></div>
                    <div style="margin-bottom:8px;">ЗВУК: <button class="btn" style="padding:6px; background:#334;" onclick="Audio.tog('sfx')" id="cfg-sfx">ВКЛ</button></div>
                    <div style="margin-bottom:8px;">МУЗЫКА: <button class="btn" style="padding:6px; background:#334;" onclick="Audio.tog('music')" id="cfg-mus">ВКЛ</button></div>
                </div>
            </div>
            <div class="col">
                <div class="panel" id="hero-desc" style="font-size:6px; color:#bbb; line-height:1.6; flex-grow:1;"></div>
                <button class="btn" onclick="UI.show(Game.isPlaying ? 'scr-adv' : 'scr-menu')">НАЗАД</button>
            </div>
        </div>

        <!-- КАРТА -->
        <div id="scr-adv" class="screen">
            <div class="col">
                <div style="display:flex; justify-content:space-between; font-size:6px; padding:4px; background:#000; border:1px solid #333;">
                    <span style="color:var(--hp)">❤️ <span id="a-hp">100</span></span>
                    <span style="color:var(--gold)">💰 <span id="a-gld">0</span></span>
                    <span style="color:var(--dust)">💎 <span id="a-dst">0</span></span>
                    <span style="color:#aaa">🗝️ <span id="a-key">0</span></span>
                </div>
                <div id="viewport"><div id="map-grid"></div></div>
                <div style="font-size: 5px; color: #888; text-align:left; padding: 2px;">Этаж: <span id="a-lvl" style="color:var(--acc)">1</span> | Нажмите на стену рядом, чтобы сломать (Кирок: <span id="a-pick">3</span>)</div>
            </div>
            <div class="col" style="justify-content: flex-end;">
                <div class="dpad">
                    <div></div><button class="dbtn" onclick="Map.move(0,-1)">▲</button><div></div>
                    <button class="dbtn" onclick="Map.move(-1,0)">◄</button>
                    <button class="dbtn" style="background:#4a235a; color:var(--acc); font-size:12px;" onclick="Camp.open()">🎒</button>
                    <button class="dbtn" onclick="Map.move(1,0)">►</button>
                    <div></div><button class="dbtn" onclick="Map.move(0,1)">▼</button><div></div>
                </div>
                <button class="btn" style="background:#151515;" onclick="UI.show('scr-set')">МЕНЮ</button>
            </div>
        </div>

        <!-- ЛАГЕРЬ -->
        <div id="scr-camp" class="screen">
            <div class="col">
                <h1 style="color:#5f5;">ГЕРОЙ</h1>
                <div class="panel" style="font-size:6px; line-height:1.6; text-align:left;">
                    <div style="color:#fff;">КЛАСС: <span id="c-cls" style="color:var(--mana)">-</span> (<span id="c-lvl">1</span> УР)</div>
                    <div>УРОН: <span id="c-dmg" style="color:var(--hp)">0</span> | ОЗ: <span id="c-hp" style="color:var(--hp)">0</span></div>
                    <div>МАНА: <span id="c-mana" style="color:var(--mana)">0</span> | КРИТ: <span id="c-crit" style="color:var(--acc)">0</span>%</div>
                    <div class="bar"><div id="c-exp" class="fill" style="background:var(--dust); width:0%;"></div><div class="text-overlay">ОПЫТ</div></div>
                </div>
                <div style="display:flex; gap:4px;">
                    <div class="slot" id="eq-w" style="width:33%; font-size:14px;" onclick="Camp.uneq('w')">⚔️</div>
                    <div class="slot" id="eq-a" style="width:33%; font-size:14px;" onclick="Camp.uneq('a')">🛡️</div>
                    <div class="slot" id="eq-r" style="width:33%; font-size:14px;" onclick="Camp.uneq('r')">🔮</div>
                </div>
            </div>
            <div class="col">
                <div class="panel" style="flex-grow:1;">
                    <div style="font-size:5px; color:#aaa; margin-bottom:4px;">ИНВЕНТАРЬ (Зажми для разбора):</div>
                    <div class="inv" id="inv-list"></div>
                </div>
                <div style="display:flex; gap:4px;">
                    <button class="btn" style="color:var(--dust); padding:6px;" onclick="Camp.craft()">КРАФТ(20💎)</button>
                    <button class="btn" style="color:var(--hp); padding:6px;" onclick="Camp.heal()">ЗЕЛЬЕ(20💰)</button>
                </div>
                <button class="btn" style="background:#222;" onclick="UI.show('scr-adv')">НА КАРТУ</button>
            </div>
        </div>

        <!-- БОЙ -->
        <div id="scr-bat" class="screen">
            <div class="col">
                <h1 style="color:var(--hp);">БИТВА</h1>
                <div class="panel" style="flex-grow:1; display:flex; flex-direction:column; justify-content:space-between;">
                    <div style="display:flex; justify-content:space-between; font-size:6px;">
                        <span id="b-pn" style="color:var(--mana)">ГЕРОЙ</span>
                        <span id="b-en" style="color:var(--hp)">ВРАГ</span>
                    </div>
                    <div class="stage" id="bat-stage">
                        <div id="h-spr" class="sprite anim-idle">⚔️</div>
                        <div id="e-spr" class="sprite anim-idle">👾</div>
                    </div>
                    <div class="bar">
                        <div id="b-ehp" class="fill" style="background:var(--hp); width:100%;"></div>
                        <div class="text-overlay" id="b-ehp-txt">100/100</div>
                    </div>
                </div>
            </div>
            <div class="col">
                <div class="panel" id="log" style="height:60px; overflow-y:auto; background:#010104; color:#aaa; font-size:5.5px; line-height:1.6; text-align:left;"></div>
                <div class="panel">
                    <div class="bar" style="margin-bottom:6px;">
                        <div id="b-php" class="fill" style="background:#2c2; width:100%;"></div>
                        <div id="b-psh" class="fill" style="background:#777; width:0%; position:absolute; top:0; left:0;"></div>
                        <div class="text-overlay" id="b-php-txt">100/100</div>
                    </div>
                    <div style="font-size:6px; color:var(--mana); margin-bottom:4px; text-align:left;">⚡ Мана: <span id="b-pm"></span></div>
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:4px;">
                        <button class="btn" id="sk-1" style="margin:0; color:#fff;" onclick="Combat.act(1)">[1] Атака</button>
                        <button class="btn" id="sk-2" style="margin:0; color:var(--mana);" onclick="Combat.act(2)">[2] Магия</button>
                        <button class="btn" id="sk-3" style="margin:0; color:#aaa;" onclick="Combat.act(3)">[3] Защита</button>
                        <button class="btn" id="sk-4" style="margin:0; color:var(--acc);" onclick="Combat.act(4)">[4] УЛЬТ</button>
                    </div>
                </div>
            </div>
        </div>

    </div>

    <script>
        // --- БАЗА ДАННЫХ И КОНСТАНТЫ ---
        const DB = {
            heroes: [
                { id: 'alu', n: "АЛУКАРД", hp: 150, dmg: 20, mp: 3, crt: 10, spr: "⚔️", d: "Боец. Вампиризм при атаке." },
                { id: 'mia', n: "МИЯ", hp: 120, dmg: 25, mp: 3, crt: 35, spr: "🏹", d: "Стрелок. Высокий шанс крита." },
                { id: 'tig', n: "ТИГРИЛ", hp: 220, dmg: 14, mp: 3, crt: 5, spr: "🛡️", d: "Танк. Бонус к щитам." },
                { id: 'gus', n: "ГОССЕН", hp: 130, dmg: 24, mp: 4, crt: 20, spr: "🗡️", d: "Ассасин. Смертельный ульт." },
                { id: 'nan', n: "НАНА", hp: 110, dmg: 18, mp: 5, crt: 10, spr: "🪃", d: "Маг. Магия оглушает врага." }
            ],
            zones: [
                { n: "Темный Лес", w: "🌲", f: "#121e12", m: [{n:"Гоблин", h:70, d:10, s:"👺", ef:"none"}, {n:"Паук", h:50, d:8, s:"🕷️", ef:"psn"}] },
                { n: "Снежный Пик", w: "❄️", f: "#1a2a3a", m: [{n:"Йети", h:140, d:18, s:"⛄", ef:"stun"}, {n:"Волк", h:100, d:25, s:"🐺", ef:"none"}] },
                { n: "Руины Бездны", w: "🗿", f: "#2a1a2a", m: [{n:"Демон", h:250, d:35, s:"👹", ef:"brn"}, {n:"Гаргулья", h:300, d:20, s:"🦇", ef:"none"}] },
                { n: "Логово Лорда", w: "🌋", f: "#3a1a1a", m: [{n:"ЛОРД", h:800, d:50, s:"👑", ef:"stun"}] }
            ],
            loot: {
                w: { ico:['🗡️','⚔️','🪓','🏹'], n:['Меч','Клинок','Топор','Лук'] },
                a: { ico:['👕','🥋','🦺','🛡️'], n:['Куртка','Доспех','Броня','Накидка'] },
                r: { ico:['📿','🔮','💍','🧿'], n:['Амулет','Око','Кольцо','Талисман'] },
                pref: ['Ржавый', 'Острый', 'Магический', 'Проклятый', 'Святой', 'Древний'],
                suf: ['Ученика', 'Охотника', 'Короля', 'Бездны', 'Дракона']
            }
        };

        // --- ГЕНЕРАТОР ЛУТА ---
        function genItem(tierBonus = 0) {
            let type = ['w','a','r'][Math.floor(Math.random()*3)];
            let tObj = DB.loot[type];
            let tier = Math.min(3, Math.floor(Math.random()*100) < (20 + tierBonus*20) ? (Math.random()<0.2?3:Math.random()<0.5?2:1) : 0);
            let stat = (tier+1) * 10 + Math.floor(Math.random()*15) + (Game.zIdx * 5);
            let name = `${DB.loot.pref[Math.floor(Math.random()*DB.loot.pref.length)]} ${tObj.n[Math.floor(Math.random()*tObj.n.length)]}`;
            if(tier > 1) name += ` ${DB.loot.suf[Math.floor(Math.random()*DB.loot.suf.length)]}`;
            return { t: type, n: name, i: tObj.ico[Math.floor(Math.random()*tObj.ico.length)], s: stat, tr: tier };
        }

        // --- АУДИО ---
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
                let tData = name==='adv' ? {t:600, s:[220,261,329,440,392,329,261,329], tp:'sine'} : {t:250, s:[164,164,349,164,196,164,293,164], tp:'sawtooth'};
                this.tmr = setInterval(() => {
                    let n = tData.s[this.stp%tData.s.length];
                    if(this.mus) {
                        let o=this.c.createOscillator(), g=this.c.createGain(); o.type=tData.tp; o.frequency.value=n;
                        g.gain.setValueAtTime(0.015, this.c.currentTime); g.gain.exponentialRampToValueAtTime(0.001, this.c.currentTime+(tData.t/1000));
                        o.connect(g); g.connect(this.c.destination); o.start(); o.stop(this.c.currentTime+(tData.t/1000));
                    }
                    this.stp++;
                }, tData.t);
            },
            fx: { stp:()=>Audio.tone(120,'triangle',0.05,0.01), hit:()=>Audio.tone(150,'square',0.1,0.04),
                  lt:()=>{Audio.tone(600,'sine',0.1); setTimeout(()=>Audio.tone(800,'sine',0.2),100);},
                  er:()=>Audio.tone(100,'sawtooth',0.2,0.04), mg:()=>Audio.tone(500,'triangle',0.3,0.03) }
        };

        // --- СОСТОЯНИЕ ---
        const Game = {
            isPlaying: false, hIdx: 0, zIdx: 0,
            p: { lvl:1, xp:0, nxp:100, hp:0, mhp:0, mp:0, mmp:0, dmg:0, crt:0, gld:50, dst:10, key:0, pick:3, eq:{w:null,a:null,r:null}, inv:[], buff:0 },
            
            hero() { return DB.heroes[this.hIdx]; },
            nextHero() { this.hIdx = (this.hIdx+1)%DB.heroes.length; Audio.init(); UI.updSet(); },
            
            calcStats() {
                let h = this.hero();
                this.p.mhp = h.hp + (this.p.lvl-1)*25 + (this.p.eq.r ? this.p.eq.r.s : 0);
                this.p.dmg = h.dmg + (this.p.lvl-1)*5 + (this.p.eq.w ? this.p.eq.w.s : 0) + this.p.buff;
                this.p.mmp = h.mp + Math.floor(this.p.lvl/3);
                this.p.crt = h.crt + (this.p.eq.a ? Math.floor(this.p.eq.a.s/5) : 0);
            },
            
            start() {
                Audio.init(); this.isPlaying = true; this.zIdx = 0;
                let h = this.hero();
                this.p = { lvl:1, xp:0, nxp:100, hp:h.hp, mp:h.mp, gld:30, dst:5, key:0, pick:3, eq:{w:null,a:null,r:null}, inv:[], buff:0 };
                this.calcStats(); this.p.hp = this.p.mhp; this.p.mp = this.p.mmp;
                Map.gen(); UI.show('scr-adv'); UI.tst("Акт I: Начало", "#ff5");
            },

            addXp(v) {
                this.p.xp += v;
                if(this.p.xp >= this.p.nxp) {
                    this.p.xp -= this.p.nxp; this.p.nxp = Math.floor(this.p.nxp * 1.5); this.p.lvl++;
                    document.getElementById('modal').style.display = 'flex'; Audio.fx.lt();
                }
            },
            
            lvlUpStat(stat) {
                let h = this.hero();
                if(stat==='hp') h.hp += 25; else if(stat==='dmg') h.dmg += 5; else if(stat==='mana') h.mp += 1;
                this.calcStats(); this.p.hp = this.p.mhp; this.p.mp = this.p.mmp;
                document.getElementById('modal').style.display = 'none'; UI.tst("Сила возросла!", "#a5f"); UI.updAdv();
            }
        };

        // --- КАРТА ---
        const Map = {
            g: [], sz: 20, px: 2, py: 2,
            gen() {
                this.g = []; Audio.play('adv'); Game.p.buff = 0;
                for(let y=0; y<this.sz; y++) {
                    let r = [];
                    for(let x=0; x<this.sz; x++) {
                        if(x===0||y===0||x===this.sz-1||y===this.sz-1) r.push(1);
                        else {
                            let rnd = Math.random();
                            // 0:Пол, 1:Стена, 2:Моб, 3:Выход, 4:Монета, 5:Хил, 6:Магаз, 7:Сундук, 8:Ключ, 9:Ловушка, 10:Алтарь
                            if(rnd<0.18) r.push(1); else if(rnd<0.24) r.push(2); else if(rnd<0.26) r.push(4);
                            else if(rnd<0.28) r.push(5); else if(rnd<0.29) r.push(6); else if(rnd<0.31) r.push(7);
                            else if(rnd<0.33) r.push(8); else if(rnd<0.35) r.push(9); else if(rnd<0.36) r.push(10);
                            else r.push(0);
                        }
                    }
                    this.g.push(r);
                }
                this.g[this.sz-2][this.sz-2] = 3; this.g[2][2] = 0; this.g[2][3] = 0; this.g[3][2] = 0;
                this.px = 2; this.py = 2; UI.updAdv();
            },
            draw() {
                let htm = "", z = DB.zones[Game.zIdx];
                for(let y = this.py-3; y <= this.py+3; y++) {
                    for(let x = this.px-3; x <= this.px+3; x++) {
                        let d = Math.max(Math.abs(x-this.px), Math.abs(y-this.py));
                        let cls = d===3?"dim-3":d===2?"dim-2":d===1?"dim-1":"";
                        
                        if(y<0||y>=this.sz||x<0||x>=this.sz) { htm += `<div class="tile wall ${cls}">${z.w}</div>`; continue; }
                        
                        let v = this.g[y][x], c = "";
                        if(x===this.px && y===this.py) { c = Game.hero().spr; cls = ""; }
                        else if(v===1) { c = z.w; cls += " wall"; }
                        else if(v===2) c = "👾"; else if(v===3) c = "🌀"; else if(v===4) c = "💰";
                        else if(v===5) c = "⛲"; else if(v===6) c = "🛒"; else if(v===7) c = "🧰";
                        else if(v===8) c = "🗝️"; else if(v===9) c = "🪤"; else if(v===10) c = "⛩️";

                        htm += `<div class="tile ${cls}" style="background:${v===1?'':z.f}" onclick="Map.click(${x},${y})">${c}</div>`;
                    }
                }
                document.getElementById('map-grid').innerHTML = htm;
            },
            click(x, y) {
                if(this.g[y][x] === 1 && Math.abs(x-this.px)<=1 && Math.abs(y-this.py)<=1 && Game.p.pick>0) {
                    Game.p.pick--; this.g[y][x] = 0; UI.tst("Стена разрушена!", "#aaa"); Audio.fx.hit(); UI.updAdv();
                }
            },
            move(dx, dy) {
                let tx = this.px+dx, ty = this.py+dy, tile = this.g[ty][tx];
                if(tile === 1) return; // Стена
                
                this.px = tx; this.py = ty; Audio.fx.stp();
                if(tile === 2) return Combat.start();
                if(tile === 3) { 
                    Game.zIdx++; 
                    if(Game.zIdx >= DB.zones.length) { alert("ВЫ ПРОШЛИ ИГРУ!"); return UI.show('scr-menu'); }
                    UI.tst(`Спуск на уровень ${Game.zIdx+1}`, "#a5f"); Game.p.pick+=1; this.gen(); return; 
                }
                if(tile === 4) { let g=10+Math.floor(Math.random()*20); Game.p.gld+=g; UI.tst(`+${g}💰`, "var(--gold)"); Audio.fx.lt(); this.g[ty][tx]=0; }
                if(tile === 5) { Game.p.hp=Game.p.mhp; UI.tst("Исцеление!", "#5f5"); Audio.fx.lt(); this.g[ty][tx]=0; }
                if(tile === 6) { if(Game.p.gld>=50){ Game.p.gld-=50; let i=genItem(1); Game.p.inv.push(i); UI.tst(`Куплено: ${i.n}`, "#fa0"); Audio.fx.lt(); } else { UI.tst("Нужно 50💰", "#f44"); Audio.fx.er(); } this.g[ty][tx]=0; }
                if(tile === 7) { if(Game.p.key>0){ Game.p.key--; let i=genItem(2); Game.p.inv.push(i); UI.tst(`Из сундука: ${i.n}`, "#a5f"); Audio.fx.lt(); this.g[ty][tx]=0; } else { UI.tst("Нужен ключ 🗝️", "#f44"); Audio.fx.er(); this.px-=dx; this.py-=dy; } }
                if(tile === 8) { Game.p.key++; UI.tst("Найден ключ!", "#fff"); Audio.fx.lt(); this.g[ty][tx]=0; }
                if(tile === 9) { let d=Math.floor(Game.p.mhp*0.15); Game.p.hp-=d; UI.tst(`Ловушка! -${d} ОЗ`, "#f44"); Audio.fx.er(); this.g[ty][tx]=0; if(Game.p.hp<=0) Combat.end(false); }
                if(tile === 10){ Game.p.buff+=10; Game.calcStats(); UI.tst("Благословение: +10 Урон", "#ff5"); Audio.fx.mg(); this.g[ty][tx]=0; }
                UI.updAdv();
            }
        };

        // --- ЛАГЕРЬ ---
        const Camp = {
            open() {
                Game.calcStats(); let p = Game.p;
                document.getElementById('c-cls').innerText = Game.hero().n;
                document.getElementById('c-lvl').innerText = p.lvl;
                document.getElementById('c-hp').innerText = `${p.hp}/${p.mhp}`;
                document.getElementById('c-dmg').innerText = p.dmg;
                document.getElementById('c-mana').innerText = `${p.mp}/${p.mmp}`;
                document.getElementById('c-crit').innerText = p.crt;
                document.getElementById('c-exp').style.width = `${(p.xp/p.nxp)*100}%`;
                
                ['w','a','r'].forEach(t => {
                    let e = p.eq[t];
                    document.getElementById(`eq-${t}`).innerHTML = e ? `${e.i}<span>+${e.s}</span>` : (t==='w'?'⚔️':t==='a'?'🛡️':'🔮');
                    document.getElementById(`eq-${t}`).className = `slot tier-${e?e.tr:0}`;
                });

                let htm = "";
                p.inv.forEach((it, i) => { htm += `<div class="slot tier-${it.tr}" onmousedown="Camp.prs(${i})" onmouseup="Camp.rls()" onmouseleave="Camp.rls()" ontouchstart="Camp.prs(${i})" ontouchend="Camp.rls()">${it.i}<span>+${it.s}</span></div>`; });
                document.getElementById('inv-list').innerHTML = htm;
                UI.show('scr-camp');
            },
            equip(idx) {
                Audio.fx.stp(); let it = Game.p.inv[idx];
                if(Game.p.eq[it.t]) Game.p.inv.push(Game.p.eq[it.t]);
                Game.p.eq[it.t] = it; Game.p.inv.splice(idx, 1);
                UI.tst(`Надето: ${it.n}`, "#5f5"); this.open();
            },
            uneq(t) { if(Game.p.eq[t]) { Game.p.inv.push(Game.p.eq[t]); Game.p.eq[t] = null; Audio.fx.stp(); this.open(); } },
            
            pTmr: null, pIdx: -1,
            prs(i) { this.pIdx = i; this.pTmr = setTimeout(() => { let it=Game.p.inv[i]; let d=5+(it.tr*5); Game.p.inv.splice(i,1); Game.p.dst+=d; UI.tst(`Слом: +${d}💎`, "#a5f"); Audio.fx.lt(); this.pIdx=-1; this.open(); }, 600); },
            rls() { if(this.pTmr){ clearTimeout(this.pTmr); this.pTmr=null; if(this.pIdx>-1) this.equip(this.pIdx); } },
            
            craft() { if(Game.p.dst>=20){ Game.p.dst-=20; let it=genItem(1); Game.p.inv.push(it); UI.tst(`Крафт: ${it.n}`, "#a5f"); Audio.fx.lt(); this.open(); } else { UI.tst("Мало пыли!", "#f44"); Audio.fx.er(); } },
            heal() { if(Game.p.gld>=20){ Game.p.gld-=20; Game.p.hp=Game.p.mhp; UI.tst("Исцеление!", "#5f5"); Audio.fx.lt(); this.open(); } else { UI.tst("Мало золота!", "#f44"); Audio.fx.er(); } }
        };

        // --- БОЙ ---
        const Combat = {
            e: null, sh: 0, trn: 'p', pEf: {psn:0, brn:0, stn:0}, eEf: {psn:0, brn:0, stn:0},
            start() {
                Audio.play('bat'); document.getElementById('log').innerHTML = "";
                let pool = DB.zones[Game.zIdx].m;
                this.e = { ...pool[Math.floor(Math.random()*pool.length)] }; this.e.mhp = this.e.h;
                
                Game.p.mp = Game.p.mmp; this.sh = (Game.hero().id==='tig') ? 50 : 0; this.trn = 'p';
                this.pEf = {psn:0, brn:0, stn:0}; this.eEf = {psn:0, brn:0, stn:0};
                
                document.getElementById('b-pn').innerText = Game.hero().n; document.getElementById('h-spr').innerText = Game.hero().spr;
                document.getElementById('b-en').innerText = this.e.n; document.getElementById('e-spr').innerText = this.e.s;
                
                this.upd(); UI.show('scr-bat'); this.log("БОЙ НАЧАЛСЯ!", "#ff5");
            },
            upd() {
                let p = Game.p;
                document.getElementById('b-php-txt').innerText = `${p.hp}/${p.mhp}`; document.getElementById('b-php').style.width = `${(p.hp/p.mhp)*100}%`;
                document.getElementById('b-psh').style.width = `${(this.sh/p.mhp)*100}%`; document.getElementById('b-pm').innerText = `${p.mp}/${p.mmp}`;
                document.getElementById('b-ehp-txt').innerText = `${this.e.h}/${this.e.mhp}`; document.getElementById('b-ehp').style.width = `${(this.e.h/this.e.mhp)*100}%`;
                
                let my = (this.trn === 'p');
                document.getElementById('sk-1').disabled = !my; document.getElementById('sk-2').disabled = (!my || p.mp<1);
                document.getElementById('sk-3').disabled = (!my || p.mp<1); document.getElementById('sk-4').disabled = (!my || p.mp<3);
            },
            log(m, c="#aaa") { let b = document.getElementById('log'); b.innerHTML += `<div style="color:${c}">> ${m}</div>`; b.scrollTop = b.scrollHeight; },
            anim(id, cls) { let el = document.getElementById(id); el.classList.remove('anim-idle'); el.classList.add(cls); setTimeout(()=>{ el.classList.remove(cls); el.classList.add('anim-idle'); }, 300); },
            float(id, txt, col) { 
                let tgt = document.getElementById(id); let f = document.createElement('div');
                f.className = 'floating-text'; f.style.color = col; f.innerText = txt;
                f.style.left = (Math.random()*40+30)+'%'; f.style.top = (Math.random()*40+20)+'%';
                tgt.parentElement.appendChild(f); setTimeout(()=>f.remove(), 1000);
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

                this.anim('h-spr', 'atkL'); Audio.fx.hit();
                let dmg = p.dmg, isCrit = (Math.random()*100 < p.crt);
                if(isCrit) dmg = Math.floor(dmg * 1.5);

                if(ty===1) {
                    if(h.id==='alu') { let v=Math.floor(dmg*0.3); p.hp=Math.min(p.mhp, p.hp+v); this.float('h-spr', `+${v}`, "#2c2"); }
                    this.e.h -= dmg; p.mp = Math.min(p.mmp, p.mp+1);
                    this.float('e-spr', isCrit?`КРИТ! ${dmg}`:`-${dmg}`, isCrit?"var(--acc)":"#fff");
                }
                else if(ty===2) {
                    p.mp -= 1; Audio.fx.mg();
                    if(h.id==='nan') { dmg=Math.floor(dmg*0.8); this.eEf.stn=1; this.log("Враг оглушен!", "#5af"); }
                    else dmg = Math.floor(dmg * 1.5);
                    this.e.h -= dmg; this.float('e-spr', `-${dmg}`, "var(--mana)");
                }
                else if(ty===3) {
                    p.mp -= 1; let s = Math.floor(p.mhp*0.2 * (h.id==='tig'?1.5:1)); this.sh += s; Audio.fx.stp();
                    this.float('h-spr', `+${s} ЩИТ`, "#aaa"); this.log("Установлен щит", "#aaa");
                }
                else if(ty===4) {
                    p.mp -= 3; dmg = Math.floor(dmg*2.5); Audio.fx.mg();
                    if(h.id==='gus' && this.e.h < this.e.mhp*0.4) dmg = Math.floor(dmg*2);
                    this.e.h -= dmg; this.float('e-spr', `УЛЬТ! ${dmg}`, "var(--hp)");
                }

                if(this.e.h <= 0) return this.end(true);
                this.endTurn();
            },
            
            endTurn() { this.trn = 'e'; this.upd(); setTimeout(() => this.eAct(), 800); },
            
            eAct() {
                if(this.procEf(false)) { this.trn='p'; this.upd(); return; }
                this.anim('e-spr', 'atkR');
                
                let d = Math.floor(this.e.d * (0.8 + Math.random()*0.4));
                if(this.e.ef === 'psn' && Math.random()<0.3) { this.pEf.psn = 3; this.float('h-spr', "ОТРАВЛЕН", "#5f5"); }
                if(this.e.ef === 'stn' && Math.random()<0.2) { this.pEf.stn = 1; this.float('h-spr', "ОГЛУШЕН", "#fff"); }
                if(this.e.ef === 'brn' && Math.random()<0.3) { this.pEf.brn = 2; this.float('h-spr', "ПОДЖОГ", "#fa0"); }
                
                if(this.sh > 0) {
                    if(this.sh >= d) { this.sh -= d; d = 0; this.float('h-spr', "БЛОК", "#aaa"); }
                    else { d -= this.sh; this.sh = 0; }
                }
                if(d > 0) { Game.p.hp -= d; this.float('h-spr', `-${d}`, "#f44"); Audio.fx.er(); }
                
                if(Game.p.hp <= 0) return this.end(false);
                this.trn = 'p'; this.upd();
            },
            
            end(win) {
                if(win) {
                    let xp = 30 + Game.zIdx*20, g = 10 + Math.floor(Math.random()*15);
                    Game.p.gld += g; UI.tst(`Победа! +${xp}XP | +${g}💰`, "#ff5");
                    Map.g[Map.py][Map.px] = 0; Map.draw(); Audio.play('adv'); UI.show('scr-adv');
                    Game.addXp(xp);
                } else {
                    alert("ПОРАЖЕНИЕ. Ваш путь окончен."); Audio.play(null); UI.show('scr-menu');
                }
            }
        };

        // --- ИНТЕРФЕЙС И УПРАВЛЕНИЕ ---
        const UI = {
            show(id) { document.querySelectorAll('.screen').forEach(s => s.classList.remove('active')); document.getElementById(id).classList.add('active'); Audio.fx.stp(); if(id==='scr-set') this.updSet(); },
            updSet() {
                let h = Game.hero();
                document.getElementById('cfg-hero').innerText = h.n; document.getElementById('cfg-sfx').innerText = Audio.sfx?"ВКЛ":"ВЫКЛ"; document.getElementById('cfg-mus').innerText = Audio.mus?"ВКЛ":"ВЫКЛ";
                document.getElementById('hero-desc').innerHTML = `${h.d}<br><br><span style='color:var(--hp)'>Баз. ОЗ: ${h.hp}</span><br><span style='color:var(--hp)'>Баз. Урон: ${h.dmg}</span><br><span style='color:var(--mana)'>Баз. Мана: ${h.mp}</span><br><span style='color:var(--acc)'>Баз. Крит: ${h.crt}%</span>`;
            },
            updAdv() {
                document.getElementById('a-hp').innerText = `${Game.p.hp}/${Game.p.mhp}`; document.getElementById('a-gld').innerText = Game.p.gld;
                document.getElementById('a-dst').innerText = Game.p.dst; document.getElementById('a-key').innerText = Game.p.key;
                document.getElementById('a-lvl').innerText = Game.zIdx+1; document.getElementById('a-pick').innerText = Game.p.pick;
                Map.draw();
            },
            tst(m, c="#fff") {
                let b = document.getElementById('toasts'), t = document.createElement('div');
                t.className = 'toast'; t.style.borderColor = c; t.innerText = m;
                b.appendChild(t); setTimeout(() => t.remove(), 1900);
            }
        };

        window.addEventListener('keydown', (e) => {
            if(document.getElementById('scr-adv').classList.contains('active')) {
                if(['w','ArrowUp'].includes(e.key)) Map.move(0,-1); if(['s','ArrowDown'].includes(e.key)) Map.move(0,1);
                if(['a','ArrowLeft'].includes(e.key)) Map.move(-1,0); if(['d','ArrowRight'].includes(e.key)) Map.move(1,0);
            } else if(document.getElementById('scr-bat').classList.contains('active')) {
                if(['1','2','3','4'].includes(e.key)) Combat.act(parseInt(e.key));
            }
        });

        UI.updSet();
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(GAME_HTML)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
