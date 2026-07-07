from flask import Flask, render_template_string

app = Flask(__name__)

GAME_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>MLBB RPG: Гипер-Эволюция — v9.0</title>
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
    <style>
        *, *::before, *::after { box-sizing: border-box; }
        body {
            font-family: 'Press Start 2P', cursive;
            background-color: #030308;
            color: #e0e0f0;
            margin: 0; padding: 5px; font-size: 7px;
            text-align: center; overflow: hidden;
            user-select: none; -webkit-user-select: none;
            height: 100vh; display: flex; justify-content: center; align-items: center;
        }
        
        #game-container {
            width: 100%; max-width: 460px; height: 100%; max-height: 780px;
            display: flex; flex-direction: column; justify-content: space-between;
            background: linear-gradient(135deg, #0b0b1a 0%, #030308 100%);
            border: 4px solid #555577; box-shadow: 0 0 50px rgba(0,0,0,0.95);
            padding: 8px; position: relative;
        }
        #game-container.fullscreen { max-width: 100vw; max-height: 100vh; border: none; padding: 10px; }
        
        .screen { display: none; height: 100%; flex-direction: column; justify-content: space-between; }
        .screen.active { display: flex; }
        .col-left, .col-right { width: 100%; display: flex; flex-direction: column; justify-content: space-between; }
        
        @media (orientation: landscape) and (min-width: 550px) {
            #game-container { max-width: 920px; max-height: 450px; flex-direction: row; padding: 10px; }
            .screen { flex-direction: row !important; width: 100%; gap: 14px; }
            .col-left { width: 49%; height: 100%; justify-content: space-between; }
            .col-right { width: 49%; height: 100%; justify-content: space-between; }
        }

        h1 { font-size: 10px; color: #ffff55; text-shadow: 2px 2px #000; margin: 3px 0; text-transform: uppercase; letter-spacing: 1px; }
        .subtitle { font-size: 6px; color: #8a8ab0; margin-bottom: 4px; text-transform: uppercase; }
        .panel { background-color: #090912; border: 2px solid #3d3d5c; box-shadow: 3px 3px 0px #000; padding: 6px; margin-bottom: 4px; position: relative; }
        
        /* ОКНО КАМЕРЫ (VIEWPORT 7x7 вместо сжатого 9x9) */
        #viewport-container {
            width: 100%; max-width: 245px; margin: 4px auto;
            border: 3px solid #444466; background: #020205; padding: 2px;
            overflow: hidden; box-shadow: inset 0 0 10px #000;
        }
        #map-grid {
            display: grid; grid-template-columns: repeat(7, 1fr); gap: 3px;
            width: 100%;
        }

        .map-tile {
            aspect-ratio: 1; display: flex; align-items: center; justify-content: center;
            font-size: 13px; background: #121e12; border-radius: 3px; text-shadow: 1px 1px 0 #000;
            transition: all 0.1s ease;
        }
        .tile-wall { background: #222230; }
        .tile-floor { background: #122212; }
        .tile-mine { background: #2d1f18; }
        .tile-waste { background: #362218; }
        .tile-abyss { background: #300a0a; }

        .dpad-container { display: grid; grid-template-columns: repeat(3, 1fr); width: 150px; margin: 2px auto; gap: 5px; }
        .dpad-btn { font-family: 'Press Start 2P'; font-size: 16px; background: #252542; color: #fff; border: 2px outset #555588; padding: 11px 0; cursor: pointer; border-radius: 6px; }
        .dpad-btn:active { border-style: inset; background: #15152b; color: #ffea00; }

        .bar-container { width: 100%; height: 12px; background-color: #111; border: 2px solid #fff; margin-top: 2px; position: relative; }
        .hp-fill { height: 100%; background-color: #cc2222; width: 100%; transition: width 0.2s; }
        .mana-fill { height: 100%; background-color: #1f75fe; width: 100%; transition: width 0.2s; }
        .shield-fill { height: 100%; background-color: #777788; width: 0%; transition: width 0.2s; }
        .exp-fill { height: 100%; background-color: #aa22cc; width: 0%; }

        #log { height: 55px; overflow-y: auto; background: #010104; color: #4aff4a; padding: 4px; text-align: left; border: 2px solid #3d3d5c; font-size: 5.5px; line-height: 1.5; }
        @media (orientation: landscape) { #log { height: 85px; } }
        
        .menu-btn { font-family: 'Press Start 2P', cursive; background-color: #1c1c3a; color: #d4af37; border: 3px outset #4a4a88; padding: 10px; width: 95%; margin: 4px auto; display: block; font-size: 8px; cursor: pointer; border-radius: 4px; }
        .menu-btn:active { border-style: inset; background-color: #111124; }
        
        .cards { display: flex; flex-wrap: wrap; gap: 4px; justify-content: space-between; }
        .card-btn { font-family: 'Press Start 2P', cursive; background-color: #111124; color: #fff; border: 2px outset #3a3a5c; padding: 8px 1px; font-size: 6px; cursor: pointer; width: 49%; min-height: 42px; border-radius: 4px; line-height: 1.4; }
        .card-btn:disabled { opacity: 0.25; cursor: not-allowed; border-color: #222; }
        .attack { color: #ff6666; border-color: #bb4444; } .defend { color: #66b2ff; border-color: #4488cc; } .ultimate { color: #ffff55; border-color: #d4af37; font-weight: bold; }

        .stage-container { position: relative; height: 85px; overflow: hidden; background: #020208; border: 2px solid #333; margin-top: 2px; }
        .sprite { font-size: 36px; position: absolute; bottom: 4px; width: 50px; height: 50px; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
        #hero-sprite { left: 15%; transform: scaleX(-1); }
        #enemy-sprite { right: 15%; }
        
        .float-anim { animation: floatEff 1.6s infinite ease-in-out; }
        .strike-left { animation: strikeL 0.25s ease-in-out; }
        .strike-right { animation: strikeR 0.25s ease-in-out; }
        .flash-red { animation: flashR 0.2s ease-in-out; }
        @keyframes floatEff { 0%, 100% { bottom: 4px; } 50% { bottom: 12px; } }
        @keyframes strikeL { 0% { left: 15%; } 50% { left: 45%; transform: scaleX(-1) scale(1.3); } 100% { left: 15%; } }
        @keyframes strikeR { 0% { right: 15%; } 50% { right: 45%; transform: scale(1.3); } 100% { right: 15%; } }
        @keyframes flashR { 0%, 100% { background: #020208; } 50% { background: #500; } }

        .damage-pop { position: absolute; font-size: 10px; font-weight: bold; color: #ff3333; text-shadow: 2px 2px #000; animation: pUp 0.60s forwards ease-out; z-index: 10; }
        @keyframes pUp { 0% { opacity: 1; transform: translateY(0); } 100% { opacity: 0; transform: translateY(-30px) scale(1.3); } }

        .inv-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px; margin: 4px 0; }
        .inv-slot { background: #05050f; border: 2px solid #333; height: 36px; display: flex; align-items: center; justify-content: center; font-size: 16px; cursor: pointer; border-radius: 4px; position: relative; }
        .common { border-color: #777; } .epic { border-color: #1f75fe; } .legend { border-color: #d4af37; box-shadow: inset 0 0 5px rgba(212,175,55,0.5); }
        .setting-row { display: flex; justify-content: space-between; align-items: center; padding: 7px; border-bottom: 1px solid #222235; }
        .btn-small { padding: 5px 8px; font-family: 'Press Start 2P'; font-size: 6px; background: #32324e; color: #fff; border: 2px outset #555; cursor: pointer; border-radius: 3px; }
        
        .status-badge { position: absolute; top: -2px; right: -2px; font-size: 8px; background: #000; padding: 1px; border-radius: 3px; border: 1px solid red; }
    </style>
</head>
<body>

    <div id="game-container">

        <!-- ЭКРАН 1: ГЛАВНОЕ МЕНЮ -->
        <div id="screen-menu" class="screen active">
            <div class="col-left" style="justify-content: center;">
                <h1 style="font-size: 13px; color: #ffff55; line-height: 1.6;">MLBB RPG:<br>ГИПЕР-ЭВОЛЮЦИЯ</h1>
                <p class="subtitle">Версия 9.0 (Движок Камеры и Стихии)</p>
            </div>
            <div class="col-right" style="justify-content: center;">
                <div style="font-size: 36px; margin: 15px 0; animation: floatEff 2s infinite ease-in-out;">🌋⚡🔮💎</div>
                <button class="menu-btn" onclick="startAdventure()">ИССЛЕДОВАТЬ МИР</button>
                <button class="menu-btn" onclick="switchScreen('screen-settings')">ВЫБОР ГЕРОЯ / НАСТРОЙКИ</button>
            </div>
        </div>

        <!-- ЭКРАН 2: НАСТРОЙКИ И ПЕРСОНАЖИ -->
        <div id="screen-settings" class="screen">
            <div class="col-left">
                <h1>НАСТРОЙКА ОТРЯДА</h1>
                <div class="panel" style="text-align: left; margin: 0;">
                    <div class="setting-row"><span>ГЕРОЙ:</span> <button id="cfg-hero" class="btn-small" style="color:#ffaa00;" onclick="toggleSetting('hero')">АЛУКАРД</button></div>
                    <div class="setting-row"><span>РАЗРЕМЕНИЕ:</span> <button id="cfg-screen" class="btn-small" onclick="toggleSetting('screen')">ОКНО</button></div>
                    <div class="setting-row"><span>ЗВУКИ БИТВЫ:</span> <button id="cfg-sound" class="btn-small" onclick="toggleSetting('sound')">ВКЛ</button></div>
                    <div class="setting-row"><span>ЭМБИЕНТ:</span> <button id="cfg-music" class="btn-small" onclick="toggleSetting('music')">ВКЛ</button></div>
                </div>
            </div>
            <div class="col-right">
                <div class="panel" id="hero-desc-panel" style="font-size:5.5px; text-align:left; color:#bbb; line-height:1.5; min-height: 110px;"></div>
                <button class="menu-btn" onclick="switchScreen('screen-menu')">ПРИМЕНИТЬ И ВЫЙТИ</button>
            </div>
        </div>

        <!-- ЭКРАН 3: КАРТА ИССЛЕДОВАНИЯ -->
        <div id="screen-adventure" class="screen">
            <div class="col-left">
                <div>
                    <h1 id="adv-location-title">ЛОКАЦИЯ 1</h1>
                    <div style="display:flex; justify-content:space-between; font-size:6px; padding: 3px; background: #000; border: 1px solid #222;">
                        <span>❤️ ОЗ: <span id="adv-hp" style="color:#ff5555;">100/100</span></span>
                        <span>💎 ПЫЛЬ: <span id="adv-dust" style="color:#aa55ff;">0</span></span>
                        <span>💰 ЗОЛОТО: <span id="adv-gold" style="color:#ffff55;">0</span></span>
                    </div>
                </div>
                <!-- Контейнер Viewport скроллинга -->
                <div id="viewport-container">
                    <div id="map-grid"></div>
                </div>
            </div>

            <div class="col-right">
                <div style="font-size:5px; color:#8a8ab0; text-align:center; margin-bottom:2px;">
                    Управление: Клавиши <b>W, A, S, D</b> или стрелки!
                </div>
                <div>
                    <div class="dpad-container">
                        <div></div>
                        <button class="dpad-btn" onclick="movePlayer(0, -1)">▲</button>
                        <div></div>
                        <button class="dpad-btn" onclick="movePlayer(-1, 0)">◄</button>
                        <button class="dpad-btn" style="background:#4a235a; font-size:12px; color:#ffff55;" onclick="openCampHub()">🎒</button>
                        <button class="dpad-btn" onclick="movePlayer(1, 0)">►</button>
                        <div></div>
                        <button class="dpad-btn" onclick="movePlayer(0, 1)">▼</button>
                        <div></div>
                    </div>
                </div>
                <button class="menu-btn" style="background:#151515; padding:6px;" onclick="switchScreen('screen-menu')">В МЕНЮ</button>
            </div>
        </div>

        <!-- ЭКРАН 4: ЛАГЕРЬ, КУЗНИЦА, РАЗБОР -->
        <div id="screen-camp" class="screen">
            <div class="col-left">
                <h1 style="color:#55ff55;">СНАРЯЖЕНИЕ И РАЗБОР</h1>
                <div class="panel" style="text-align: left; font-size: 6px; line-height: 1.5; margin: 0;">
                    <div>КЛАСС: <span id="camp-hero" style="color:#6da5ff;">АЛУКАРД</span> (<span id="camp-lvl">1</span> УР)</div>
                    <div>АТАКА: <span id="camp-dmg" style="color:#ff5555;">16</span> | МАГ. ПЫЛЬ: <span id="camp-dust" style="color:#aa55ff;">0</span></div>
                    <div class="bar-container" style="height:6px; margin-top:4px;"><div id="camp-exp-fill" class="exp-fill"></div></div>
                </div>
                <div class="panel" style="margin-top: 4px; padding: 4px;">
                    <div style="display:flex; justify-content: space-between;">
                        <div class="inv-slot" id="slot-weapon" style="width:32%; font-size:6px; text-align:center;" onclick="unequipItem('weapon')">⚔️ Оружие</div>
                        <div class="inv-slot" id="slot-armor" style="width:32%; font-size:6px; text-align:center;" onclick="unequipItem('armor')">🛡️ Доспех</div>
                        <div class="inv-slot" id="slot-artifact" style="width:32%; font-size:6px; text-align:center;" onclick="unequipItem('artifact')">🔮 Реликт</div>
                    </div>
                </div>
            </div>

            <div class="col-right">
                <div class="panel" style="margin: 0;">
                    <div style="font-size: 5px; color:#aaa; margin-bottom: 2px;">ИНВЕНТАРЬ (Клик - Надеть | Зажми на секунду - Разобрать):</div>
                    <div class="inv-grid" id="inventory-container"></div>
                </div>
                <div style="display:flex; gap:4px; margin-top:4px;">
                    <button class="card-btn attack" style="min-height:32px;" onclick="craftFromDust()">🔮 КРАФТ РЕЛИКТА (15 Пыли)</button>
                    <button class="card-btn defend" style="min-height:32px;" onclick="buyHealPotion()">🧪 ЗЕЛЬЕ ОЗ (15💰)</button>
                </div>
                <button class="menu-btn" style="background:#222; padding:6px;" onclick="switchScreen('screen-adventure')">ВЕРНУТЬСЯ НА КАРТУ</button>
            </div>
        </div>

        <!-- ЭКРАН 5: БОЕВАЯ СИСТЕМА (ХОТКЕИ 1,2,3,4) -->
        <div id="screen-battle" class="screen">
            <div class="col-left">
                <h1 style="color:#ff4444;">🔥 ЭЛИКТРИЧЕСКИЙ БОЙ 🔥</h1>
                <div class="panel" id="battle-field" style="margin: 0; flex-grow: 1; display: flex; flex-direction: column; justify-content: space-between;">
                    <div style="display:flex; justify-content:space-between; font-size:6px; font-weight:bold;">
                        <span id="bt-player-name" style="color:#6da5ff;">ГЕРОЙ</span>
                        <div id="player-status-area"></div>
                        <div id="enemy-status-area"></div>
                        <span id="bt-enemy-name" style="color:#ff6d6d;">КРИП</span>
                    </div>
                    <div class="stage-container">
                        <div id="hero-sprite" class="sprite float-anim">⚔️</div>
                        <div id="enemy-sprite" class="sprite float-anim">👾</div>
                    </div>
                    <div>
                        <div style="font-size:5px; margin-bottom:1px; text-align:left;">ЖИЗНЬ ВРАГА: <span id="enemy-hp-text">50/50</span></div>
                        <div class="bar-container" style="height:8px;"><div id="enemy-hp-fill" class="hp-fill"></div></div>
                    </div>
                </div>
            </div>

            <div class="col-right">
                <div class="panel" style="padding:2px; margin-bottom:4px;"><div id="log">Загрузка боевого ИИ...</div></div>

                <div class="panel" id="player-panel" style="margin: 0; padding: 4px;">
                    <div style="display:flex; justify-content:space-between; font-size:6px; font-weight:bold; margin-bottom:2px;">
                        <span>ЗДОРОВЬЕ: <span id="player-hp-text" style="color:#55ff55;">100/100</span></span>
                        <span>ЭНЕРГИЯ: <span id="player-mana-text" style="color:#55aaff;">⚡ 3/3</span></span>
                    </div>
                    <div class="bar-container" style="height:9px;">
                        <div id="player-hp-fill" class="hp-fill" style="background-color:#22cc22;"></div>
                        <div id="player-shield-fill" class="shield-fill" style="position:absolute; top:0; left:0;"></div>
                    </div>
                    <div class="cards" style="margin-top:6px;">
                        <button class="card-btn attack" id="btn-atk1" onclick="useCombatSkill('atk1')">[1] Атака</button>
                        <button class="card-btn attack" id="btn-atk2" onclick="useCombatSkill('atk2')">[2] Стихия</button>
                        <button class="card-btn defend" id="btn-def" onclick="useCombatSkill('def')">[3] Щит</button>
                        <button class="card-btn ultimate" id="btn-ult" onclick="useCombatSkill('ult')">[4] УЛЬТ</button>
                    </div>
                </div>
            </div>
        </div>

    </div>

    <script>
        const heroList = ['алукард', 'мия', 'тигрил', 'госсен'];
        const heroData = {
            'алукард': { name: "АЛУКАРД", maxHp: 130, dmg: 18, sprite: "⚔️", desc: "* Класс: БОЕЦ. Эффект: Пассивный вампиризм 25% со всех атак и ульты." },
            'мия': { name: "МИЯ", maxHp: 105, dmg: 24, sprite: "🏹", desc: "* Класс: СТРЕЛОК. Эффект: 30% шанс нанести х2 критический урон." },
            'тигрил': { name: "ТИГРИЛ", maxHp: 180, dmg: 15, sprite: "🛡️", desc: "* Класс: ТАНК. Эффект: Начинает каждый бой со щитом 50 ОЗ. Эффективность блоков увеличена." },
            'госсен': { name: "ГОССЕН", maxHp: 110, dmg: 22, sprite: "🗡️", desc: "* Класс: УБИЙЦА. Эффект: Быстрый набор энергии (+2 вместо +1). Урон ульты возрастает на раненых целях." }
        };

        let config = { sound: true, music: true, hero: 'алукард', fullscreen: false };
        let player = { lvl: 1, exp: 0, nextExp: 90, gold: 60, dust: 5, baseDmg: 18, hp: 130, maxHp: 130, mana: 3, maxMana: 4, shield: 0, weapon: null, armor: null, artifact: null, status: null };
        let inventory = [{ type: 'potion', name: 'Зелье ОЗ', icon: '🧪', rare: 'common' }];
        let currentZone = 0; let playerX = 2; let playerY = 2;
        let combatActive = false; let currentCreep = null;
        let gameState = { isGameOver: false, currentTurn: 'player' };
        
        // МЕГА-КАРТА 20х20 (Сгенерированная матрица для расширения)
        let megaMap = [];

        const lootTable = [
            { type: 'weapon', name: 'Меч Империи', icon: '🗡️', stat: 10, rare: 'common' },
            { type: 'weapon', name: 'Копьё Дракона', icon: '🔱', stat: 22, rare: 'epic' },
            { type: 'weapon', name: 'Клинок Отчаяния', icon: '⚔️', stat: 50, rare: 'legend' },
            { type: 'armor', name: 'Кираса воина', icon: '👕', stat: 8, rare: 'common' },
            { type: 'armor', name: 'Доспех Демона', icon: '🛡️', stat: 20, rare: 'epic' },
            { type: 'armor', name: 'Бессмертие', icon: '💎', stat: 45, rare: 'legend' },
            { type: 'artifact', name: 'Амулет Силы', icon: '📿', stat: 30, rare: 'common' },
            { type: 'artifact', name: 'Око Дракона', icon: '🔮', stat: 65, rare: 'epic' },
            { type: 'artifact', name: 'Сердце Анубиса', icon: '👑', stat: 120, rare: 'legend' }
        ];

        const zones = [
            { title: "Запретный Легион Монии", tileClass: "tile-floor", wallClass: "tile-wall", wallIcon: "🌲", monsterPool: [{ name: "Гоблин-Поджигатель", hp: 55, sprite: "👺", minDmg: 6, maxDmg: 10, exp: 50, gold: 20, element: 'fire' }] },
            { title: "Ледяная Бездна Ностальгии", tileClass: "tile-mine", wallClass: "tile-wall", wallIcon: "❄️", monsterPool: [{ name: "Снежный Призрак", hp: 95, sprite: "👻", minDmg: 10, maxDmg: 16, exp: 80, gold: 35, element: 'ice' }] },
            { title: "Грозовые Кряжи Кадиэ", tileClass: "tile-waste", wallClass: "tile-wall", wallIcon: "⚡", monsterPool: [{ name: "Элементаль Искр", hp: 160, sprite: "👾", minDmg: 16, maxDmg: 26, exp: 150, gold: 55, element: 'shock' }] },
            { title: "🌋 Вулкан Ужаса Пекла", tileClass: "tile-abyss", wallClass: "tile-wall", wallIcon: "🔥", monsterPool: [{ name: "ТАМУЗ ИСТИННЫЙ", hp: 750, sprite: "👑", minDmg: 50, maxDmg: 70, exp: 9999, gold: 1000, element: 'fire', isBoss: true }] }
        ];

        let audioCtx = null; let musicTimer = null; let musicTicks = 0;
        function initAudio() { if (!audioCtx) { audioCtx = new (window.AudioContext || window.webkitAudioContext)(); runMusicEngine(); } }
        function makeTone(freq, wave, len, vol = 0.015) {
            if (!config.sound || !audioCtx) return;
            if (audioCtx.state === 'suspended') audioCtx.resume();
            let osc = audioCtx.createOscillator(); let gain = audioCtx.createGain();
            osc.type = wave; osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
            gain.gain.setValueAtTime(vol, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + len);
            osc.connect(gain); gain.connect(audioCtx.destination);
            osc.start(); osc.stop(audioCtx.currentTime + len);
        }
        function runMusicEngine() {
            if (musicTimer) clearInterval(musicTimer);
            musicTimer = setInterval(() => {
                if (!config.music || !audioCtx || combatActive) return;
                let scale = [261.63, 311.13, 392.00, 349.23];
                let note = scale[musicTicks % scale.length];
                makeTone(note, 'triangle', 0.18, 0.005); musicTicks++;
            }, 350);
        }

        const audioPack = {
            click: () => makeTone(600, 'sine', 0.05, 0.02),
            step: () => makeTone(120, 'triangle', 0.06, 0.02),
            loot: () => { makeTone(440, 'sine', 0.08, 0.02); setTimeout(() => makeTone(880, 'sine', 0.15, 0.02), 50); },
            heal: () => { makeTone(350, 'sine', 0.1, 0.02); setTimeout(() => makeTone(700, 'sine', 0.2, 0.02), 50); },
            hit: () => makeTone(180, 'sawtooth', 0.08, 0.02),
            block: () => makeTone(400, 'sine', 0.08, 0.03),
            lvlUp: () => { [523, 659, 783, 1046].forEach((f, i) => setTimeout(() => makeTone(f, 'sine', 0.12, 0.02), i*60)); }
        };

        function switchScreen(id) {
            initAudio(); audioPack.click();
            document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
            document.getElementById(id).classList.add('active');
            if(id === 'screen-settings') updateSettingsUI();
        }

        function updateSettingsUI() {
            let h = heroData[config.hero];
            document.getElementById('cfg-hero').innerText = h.name;
            document.getElementById('hero-desc-panel').innerHTML = `${h.desc}<br><br><span style='color:#ff5555'>Макс ОЗ: ${h.maxHp}</span><br><span style='color:#ffaa00'>Атака: ${h.dmg}</span>`;
        }

        function toggleSetting(key) {
            initAudio(); audioPack.click();
            if (key === 'sound' || key === 'music') { config[key] = !config[key]; document.getElementById(`cfg-${key}`).innerText = config[key] ? "ВКЛ" : "ВЫКЛ"; }
            else if (key === 'screen') {
                config.fullscreen = !config.fullscreen; let c = document.getElementById('game-container');
                if (config.fullscreen) { c.classList.add('fullscreen'); document.getElementById('cfg-screen').innerText = "ВЕСЬ ЭКРАН"; if (document.documentElement.requestFullscreen) document.documentElement.requestFullscreen(); }
                else { c.classList.remove('fullscreen'); document.getElementById('cfg-screen').innerText = "ОКНО"; if (document.exitFullscreen && document.fullscreenElement) document.exitFullscreen(); }
            } else if (key === 'hero') {
                let idx = heroList.indexOf(config.hero); config.hero = heroList[(idx + 1) % heroList.length];
                updateSettingsUI();
            }
        }

        function getDynamicMaxHp() {
            let base = heroData[config.hero].maxHp + (player.lvl - 1) * 16;
            if (player.artifact) base += player.artifact.stat;
            return base;
        }

        // ГЕНЕРАТОР МЕГА-КАРТЫ 20х20
        function generateMegaMap(zoneIdx) {
            let size = 20; megaMap = [];
            for (let y = 0; y < size; y++) {
                let row = [];
                for (let x = 0; x < size; x++) {
                    if (x === 0 || y === 0 || x === size - 1 || y === size - 1) { row.push(1); } // Границы
                    else {
                        let r = Math.random();
                        if (r < 0.18) row.push(1); // Стены
                        else if (r < 0.24) row.push(2); // Монстры
                        else if (r < 0.28) row.push(4); // Золото/сундуки
                        else if (r < 0.30) row.push(5); // Источник ОЗ
                        else row.push(0); // Пол
                    }
                }
                megaMap.push(row);
            }
            // Гарантируем выход и точку старта
            megaMap[18][18] = 3; 
            megaMap[2][2] = 0;
            playerX = 2; playerY = 2;
        }

        function startAdventure() {
            let data = heroData[config.hero];
            player.lvl = 1; player.exp = 0; player.nextExp = 90; player.gold = 60; player.dust = 5;
            player.baseDmg = data.dmg; player.weapon = null; player.armor = null; player.artifact = null;
            player.maxHp = getDynamicMaxHp(); player.hp = player.maxHp;
            inventory = [{ type: 'potion', name: 'Зелье ОЗ', icon: '🧪', rare: 'common' }];
            loadZone(0);
        }

        function loadZone(idx) {
            currentZone = idx; if (currentZone >= zones.length) { alert("🏆 ПОБЕДА! Вы прошли Грандиозную Сагу и спасли вселенную MLBB!"); switchScreen('screen-menu'); return; }
            generateMegaMap(currentZone); renderViewport(); switchScreen('screen-adventure');
        }

        // РЕНДЕР ПЛАВАЮЩЕГО VIEWPORT (7x7 Вокруг Игрока)
        function renderViewport() {
            player.maxHp = getDynamicMaxHp();
            document.getElementById('adv-location-title').innerText = `${currentZone+1}/${zones.length}: ${zones[currentZone].title}`;
            document.getElementById('adv-hp').innerText = `${player.hp}/${player.maxHp}`;
            document.getElementById('adv-gold').innerText = player.gold;
            document.getElementById('adv-dust').innerText = player.dust;
            
            let grid = document.getElementById('map-grid'); grid.innerHTML = "";
            let viewRadius = 3; // Окно 7х7 (текущие координаты -3 до +3)
            let z = zones[currentZone];

            for (let y = playerY - viewRadius; y <= playerY + viewRadius; y++) {
                for (let x = playerX - viewRadius; x <= playerX + viewRadius; x++) {
                    let cell = document.createElement('div');
                    // Если выходим за пределы массива мега-карты
                    if (y < 0 || y >= 20 || x < 0 || x >= 20) {
                        cell.className = "map-tile tile-wall"; cell.innerText = z.wallIcon;
                    } else {
                        let code = megaMap[y][x];
                        cell.className = "map-tile " + z.tileClass;
                        if (code === 1) { cell.className = "map-tile " + z.wallClass; cell.innerText = z.wallIcon; }
                        else if (code === 2) cell.innerText = "👾"; 
                        else if (code === 3) cell.innerText = "🎯";
                        else if (code === 4) cell.innerText = "🎁"; 
                        else if (code === 5) cell.innerText = " fountains ⛲";
                        
                        if (x === playerX && y === playerY) {
                            cell.innerText = heroData[config.hero].sprite;
                            cell.style.background = "#4a4a00";
                        }
                    }
                    grid.appendChild(cell);
                }
            }
        }

        function movePlayer(dx, dy) {
            if (combatActive) return; initAudio();
            let tx = playerX + dx, ty = playerY + dy;
            if (tx >= 0 && tx < 20 && ty >= 0 && ty < 20 && megaMap[ty][tx] !== 1) {
                playerX = tx; playerY = ty; audioPack.step();
                let trg = megaMap[playerY][playerX];
                if (trg === 2) { triggerBattle(); return; }
                if (trg === 3) { alert("🎯 Портал переносит вас глубже..."); loadZone(currentZone + 1); return; }
                if (trg === 4) { 
                    let g = Math.floor(Math.random()*25)+20; player.gold += g; 
                    let d = Math.floor(Math.random()*3)+1; player.dust += d;
                    audioPack.loot(); alert(`🎁 Клад! Найдено: +${g}💰 и +${d} Магической пыли!`); 
                    megaMap[playerY][playerX] = 0; 
                }
                if (trg === 5) { player.hp = player.maxHp = getDynamicMaxHp(); audioPack.heal(); alert("⛲ Родник полностью исцелил силы!"); megaMap[playerY][playerX] = 0; }
                renderViewport();
            }
        }

        // SMART КЛАВИАТУРА И ХОТКЕИ КЛАССОВ
        window.addEventListener('keydown', (e) => {
            let advActive = document.getElementById('screen-adventure').classList.contains('active');
            let btlActive = document.getElementById('screen-battle').classList.contains('active');
            
            if (advActive) {
                if (e.key === 'w' || e.key === 'ArrowUp') movePlayer(0, -1);
                if (e.key === 's' || e.key === 'ArrowDown') movePlayer(0, 1);
                if (e.key === 'a' || e.key === 'ArrowLeft') movePlayer(-1, 0);
                if (e.key === 'd' || e.key === 'ArrowRight') movePlayer(1, 0);
            }
            if (btlActive) {
                if (e.key === '1') useCombatSkill('atk1');
                if (e.key === '2') useCombatSkill('atk2');
                if (e.key === '3') useCombatSkill('def');
                if (e.key === '4') useCombatSkill('ult');
            }
        });

        function openCampHub() {
            switchScreen('screen-camp'); player.maxHp = getDynamicMaxHp();
            document.getElementById('camp-hero').innerText = config.hero.toUpperCase();
            document.getElementById('camp-lvl').innerText = player.lvl; 
            document.getElementById('camp-gold').innerText = player.gold;
            document.getElementById('camp-dust').innerText = player.dust;
            document.getElementById('camp-exp-fill').style.width = `${(player.exp / player.nextExp)*100}%`;
            
            let wStat = player.weapon ? player.weapon.stat : 0; 
            document.getElementById('camp-dmg').innerText = player.baseDmg + wStat;
            document.getElementById('slot-weapon').innerText = player.weapon ? `${player.weapon.icon} +${player.weapon.stat}` : '⚔️ Оружие';
            document.getElementById('slot-armor').innerText = player.armor ? `${player.armor.icon} +${player.armor.stat}` : '🛡️ Доспех';
            document.getElementById('slot-artifact').innerText = player.artifact ? `${player.artifact.icon} +${player.artifact.stat} ОЗ` : '🔮 Реликт';
            
            let box = document.getElementById('inventory-container'); box.innerHTML = "";
            inventory.forEach((item, i) => {
                let slot = document.createElement('div'); slot.className = `inv-slot ${item.rare}`;
                slot.innerText = item.icon;
                
                // Обычный клик - экипировать
                slot.onclick = () => { useItem(i); };
                
                // Долгое нажатие - Утилизация на пыль
                let pressTimer;
                slot.onmousedown = slot.ontouchstart = () => {
                    pressTimer = setTimeout(() => {
                        if (item.type !== 'potion') {
                            inventory.splice(i, 1); player.dust += 4;
                            audioPack.loot(); alert(`🔮 Разобрано на 4 ед. Магической пыли!`);
                            openCampHub();
                        }
                    }, 700);
                };
                slot.onmouseup = slot.onmouseleave = slot.ontouchend = () => clearTimeout(pressTimer);

                box.appendChild(slot);
            });
        }

        function useItem(idx) {
            let item = inventory[idx]; audioPack.click();
            if (item.type === 'potion') { player.hp = player.maxHp = getDynamicMaxHp(); alert("🧪 Все ОЗ восполнены!"); inventory.splice(idx, 1); }
            else { 
                if (player[item.type]) inventory.push(player[item.type]); 
                player[item.type] = item; inventory.splice(idx, 1); 
                alert(`Надето: ${item.name} (+${item.stat})`); 
            }
            openCampHub();
        }

        function unequipItem(slot) { if (player[slot]) { inventory.push(player[slot]); player[slot] = null; openCampHub(); } }
        function buyHealPotion() { if (player.gold >= 15) { player.gold -= 15; inventory.push({ type: 'potion', name: 'Зелье', icon: '🧪', rare:'common' }); openCampHub(); } else alert("Мало золота!"); }
        
        function craftFromDust() { 
            if (player.dust >= 15) { 
                player.dust -= 15; 
                let r = { ...lootTable[Math.floor(Math.random() * lootTable.length)] }; 
                inventory.push(r); alert(`🔨 Пыль материализовалась в: ${r.name} (${r.rare.toUpperCase()})`); 
                openCampHub(); 
            } else alert("Недостаточно пыли! Нужно 15 шт. (Зажимай вещи в инвентаре для разбора)"); 
        }

        function setupSkillButtons() {
            let b1 = document.getElementById('btn-atk1'); let b2 = document.getElementById('btn-atk2');
            let b3 = document.getElementById('btn-def'); let b4 = document.getElementById('btn-ult');
            if (config.hero === 'алукард') {
                b1.innerHTML = "[1] Рубка<br>+1⚡ [Вамп]"; b2.innerHTML = "[2] Магма-Взрыв<br>-1⚡ [Поджог]"; b3.innerHTML = "[3] Блок щитом<br>-1⚡"; b4.innerHTML = "[4] ВОЛНА БЕЗДНЫ<br>-3⚡ [Вамп]";
            } else if (config.hero === 'мия') {
                b1.innerHTML = "[1] Стрела<br>+1⚡ [Крит]"; b2.innerHTML = "[2] Ледяной Град<br>-1⚡ [Фриз]"; b3.innerHTML = "[3] Скрытие<br>-1⚡"; b4.innerHTML = "[4] СТРЕЛА РОКА<br>-3⚡";
            } else if (config.hero === 'тигрил') {
                b1.innerHTML = "[1] Удар Света<br>+1⚡"; b2.innerHTML = "[2] Грозовая кара<br>-1⚡ [Шок]"; b3.innerHTML = "[3] Бастион<br>-1⚡ [Усил]"; b4.innerHTML = "[4] ИМПЛОЗИЯ<br>-3⚡ [Стан]";
            } else if (config.hero === 'госсен') {
                b1.innerHTML = "[1] Веер Ножей<br>+2⚡"; b2.innerHTML = "[2] Теневое Пламя<br>-1⚡ [Поджог]"; b3.innerHTML = "[3] Шаг ветра<br>-1⚡"; b4.innerHTML = "[4] КАЗНЬ КЛИНКОВ<br>-3⚡";
            }
        }

        function triggerBattle() {
            combatActive = true; gameState.isGameOver = false; gameState.currentTurn = 'player';
            let pool = zones[currentZone].monsterPool; currentCreep = { ...pool[Math.floor(Math.random() * pool.length)], maxHp: pool[0].hp, status: null };
            player.status = null; player.mana = 3; player.shield = (config.hero === 'тигрил') ? 50 : 0;
            
            document.getElementById('bt-player-name').innerText = heroData[config.hero].name;
            document.getElementById('bt-enemy-name').innerText = currentCreep.name;
            document.getElementById('enemy-sprite').innerText = currentCreep.sprite;
            document.getElementById('hero-sprite').innerText = heroData[config.hero].sprite;
            
            document.getElementById('log').innerHTML = "Эпическое столкновение! Ваш ход.";
            setupSkillButtons(); updateBattleUI(); switchScreen('screen-battle');
        }

        function updateBattleUI() {
            player.maxHp = getDynamicMaxHp();
            document.getElementById('player-hp-text').innerText = `${player.hp}/${player.maxHp}`;
            document.getElementById('player-hp-fill').style.width = `${(player.hp / player.maxHp)*100}%`;
            document.getElementById('player-shield-fill').style.width = `${(player.shield / player.maxHp)*100}%`;
            document.getElementById('player-mana-text').innerText = `⚡ ${player.mana}/${player.maxMana}`;
            document.getElementById('enemy-hp-text').innerText = `${currentCreep.hp}/${currentCreep.maxHp}`;
            document.getElementById('enemy-hp-fill').style.width = `${(currentCreep.hp / currentCreep.maxHp)*100}%`;
            
            document.getElementById('player-status-area').innerText = player.status ? `[${player.status.toUpperCase()}]` : '';
            document.getElementById('enemy-status-area').innerText = currentCreep.status ? `[${currentCreep.status.toUpperCase()}]` : '';

            let myTurn = (gameState.currentTurn === 'player' && !gameState.isGameOver);
            document.getElementById('btn-atk1').disabled = !myTurn; 
            document.getElementById('btn-atk2').disabled = !myTurn || player.mana < 1;
            document.getElementById('btn-def').disabled = !myTurn || player.mana < 1; 
            document.getElementById('btn-ult').disabled = !myTurn || player.mana < 3;
        }

        function addLog(t, c='#fff') { let l = document.getElementById('log'); l.innerHTML += `<br><span style="color:${c}">${t}</span>`; l.scrollTop = l.scrollHeight; }
        function triggerDamageText(v, side) {
            let d = document.createElement('div'); d.className = 'damage-pop'; d.innerText = v; d.style.left = side ? '75%' : '20%'; d.style.bottom = '40px';
            if (v.includes('+') || v.includes('Блок')) d.style.color = '#55ff55'; if (v.includes('💥')) d.style.color = '#ffff55';
            document.getElementById('battle-field').appendChild(d); setTimeout(() => d.remove(), 600);
        }

        // РЕАЛИЗАЦИЯ БОЕВОЙ СИСТЕМЫ И СТИХИЙНОГО СТАТУСА
        function useCombatSkill(sk) {
            if (gameState.isGameOver || gameState.currentTurn !== 'player') return;
            
            // Если игрок заморожен
            if (player.status === 'ice') { player.status = null; addLog("🧊 Вы растопили лед и пропустили ход!", "#66b2ff"); gameState.currentTurn = 'enemy'; setTimeout(enemyTurn, 700); return; }

            // Периодический урон от поджога игрока
            if (player.status === 'fire') { player.hp = Math.max(1, player.hp - 8); triggerDamageText("-8🔥", false); addLog("🔥 Вы горите: -8 ОЗ", "#ff5555"); }

            let spr = document.getElementById('hero-sprite'); let dmg = player.baseDmg + (player.weapon ? player.weapon.stat : 0);
            spr.classList.add('strike-left'); setTimeout(() => spr.classList.remove('strike-left'), 250);

            if (sk === 'atk1') {
                let f = Math.floor(dmg*0.8) + Math.floor(Math.random()*4); let cr = false;
                if (config.hero === 'мия' && Math.random() < 0.30) { f *= 2; cr = true; }
                if (currentCreep.status === 'shock') { f = Math.floor(f*1.4); currentCreep.status = null; addLog("⚡ Разряд Шока сработал!", "#ffff55"); }
                
                currentCreep.hp = Math.max(0, currentCreep.hp - f);
                player.mana = Math.min(player.maxMana, player.mana + (config.hero === 'госсен' ? 2 : 1)); audioPack.hit();
                if (config.hero === 'алукард') { let v = Math.floor(f*0.25); player.hp = Math.min(player.maxHp, player.hp + v); triggerDamageText(`+${v}`, false); }
                triggerDamageText(cr ? `💥${f}!` : `-${f}`, true); addLog(`Обычный удар: -${f} ОЗ`);
            } 
            else if (sk === 'atk2') {
                player.mana -= 1; let f = Math.floor(dmg*1.2);
                let elem = (config.hero === 'алукард' || config.hero === 'госсен') ? 'fire' : (config.hero === 'мия' ? 'ice' : 'shock');
                currentCreep.status = elem; currentCreep.hp = Math.max(0, currentCreep.hp - f);
                audioPack.hit(); triggerDamageText(`-${f}🌀`, true); addLog(`Стихийный навык наложил [${elem.toUpperCase()}]: -${f} ОЗ!`, '#ffaa00');
            } 
            else if (sk === 'def') {
                player.mana -= 1; let multi = (config.hero === 'тигрил') ? 1.7 : 1.1;
                let s = Math.floor((20 + (player.armor ? player.armor.stat : 0)) * multi); player.shield += s;
                audioPack.block(); triggerDamageText(`+🛡️${s}`, false); addLog(`Активирован энерго-барьер: +${s}`, '#66b2ff');
            } 
            else if (sk === 'ult') {
                player.mana -= 3; let f = Math.floor(dmg*2.6);
                if (config.hero === 'госсен' && currentCreep.hp < (currentCreep.maxHp / 2)) f = Math.floor(f * 1.5);
                currentCreep.hp = Math.max(0, currentCreep.hp - f); audioPack.hit();
                if (config.hero === 'алукард') { let l = Math.floor(f*0.35); player.hp = Math.min(player.maxHp, player.hp + l); triggerDamageText(`+${l}`, false); }
                document.getElementById('battle-field').classList.add('flash-red'); setTimeout(() => document.getElementById('battle-field').classList.remove('flash-red'), 200);
                triggerDamageText(`💥💥${f}`, true); addLog(`🔮 УЛЬТИМЕЙТ КЛАССА сокрушил врага: нанес ${f}!`, '#ffff33');
            }

            updateBattleUI(); if (currentCreep.hp <= 0) { endBattle(true); return; }
            gameState.currentTurn = 'enemy'; setTimeout(enemyTurn, 650);
        }

        // ИИ СТИХИЙНОГО ПРОТИВНИКА
        function enemyTurn() {
            if (gameState.isGameOver) return;
            
            // Если монстр заморожен
            if (currentCreep.status === 'ice') { currentCreep.status = null; addLog(`🧊 ${currentCreep.name} заморожен и пропускает ход!`, "#55aaff"); gameState.currentTurn = 'player'; updateBattleUI(); return; }
            
            // Дорение монстра
            if (currentCreep.status === 'fire') { currentCreep.hp = Math.max(0, currentCreep.hp - 12); triggerDamageText("-12🔥", true); addLog(`🔥 Горение подрывает монстра: -12 ОЗ`, "#ff3333"); if(currentCreep.hp<=0){endBattle(true);return;} }

            let spr = document.getElementById('enemy-sprite'); spr.classList.add('strike-right'); setTimeout(() => spr.classList.remove('strike-right'), 250);
            
            let ed = Math.floor(Math.random()*(currentCreep.maxDmg - currentCreep.minDmg + 1)) + currentCreep.minDmg;
            let r = Math.random();

            if (r > 0.65) { // Наложение дебаффа на игрока в зависимости от элемента крипа
                player.status = currentCreep.element;
                addLog(`⚡ ${currentCreep.name} применил СТИХИЙНЫЙ ВСПЛЕСК [${currentCreep.element.toUpperCase()}]!`, '#ff3333');
            }

            if (player.shield > 0) { if (player.shield >= ed) { player.shield -= ed; ed = 0; } else { ed -= player.shield; player.shield = 0; } }
            if (ed > 0) { player.hp = Math.max(0, player.hp - ed); triggerDamageText(`-${ed}`, false); audioPack.hit(); addLog(`Враг нанес урон: -${ed} ОЗ`, '#ff5555'); }
            else { triggerDamageText("Блок", false); audioPack.block(); }

            updateBattleUI(); 
            if (player.hp <= 0) { endBattle(false); } else { gameState.currentTurn = 'player'; updateBattleUI(); }
        }

        function endBattle(win) {
            gameState.isGameOver = true; combatActive = false;
            if (win) {
                audioPack.lvlUp(); player.gold += currentCreep.gold; player.exp += currentCreep.exp;
                alert(`👑 Чистая победа! Получено: +${currentCreep.gold}💰 | +${currentCreep.exp} опыта`); 
                megaMap[playerY][playerX] = 0; // Очищаем ячейку мега-карты
                
                if (player.exp >= player.nextExp) { 
                    player.lvl++; player.exp -= player.nextExp; player.nextExp = Math.floor(player.nextExp * 1.5); 
                    player.baseDmg += 6; player.hp = player.maxHp = getDynamicMaxHp(); alert("🌟 ВЫ СТАЛИ ЕЩЕ СИЛЬНЕЕ! УРОВЕНЬ ПОВЫШЕН!"); 
                }
                renderViewport(); switchScreen('screen-adventure');
            } else { alert("💀 Мир пал перед мощью Бездны. Попробуйте сменить тактику или прокачать оружие."); switchScreen('screen-menu'); }
        }
        
        updateSettingsUI();
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(GAME_HTML)

if __name__ == '__main__':
    app.run(debug=True)
