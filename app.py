from flask import Flask, render_template_string

app = Flask(__name__)

GAME_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>MLBB: Хроники Монии — Приключение</title>
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
    <style>
        *, *::before, *::after { box-sizing: border-box; }
        body {
            font-family: 'Press Start 2P', cursive;
            background-color: #030308;
            color: #d1d1e0;
            margin: 0; padding: 5px; font-size: 7px;
            text-align: center; overflow: hidden;
            user-select: none; -webkit-user-select: none;
            height: 100vh; display: flex; justify-content: center; align-items: center;
        }
        
        #game-container {
            width: 100%; max-width: 460px; height: 100%; max-height: 740px;
            display: flex; flex-direction: column; justify-content: space-between;
            background: linear-gradient(135deg, #111126 0%, #040409 100%);
            border: 4px solid #4a4a6b; box-shadow: 0 0 30px rgba(0,0,0,0.9);
            padding: 8px; position: relative;
        }
        #game-container.fullscreen { max-width: 100vw; max-height: 100vh; border: none; padding: 10px; }
        
        h1 { font-size: 10px; color: #ffff55; text-shadow: 2px 2px #000; margin: 3px 0; text-transform: uppercase; }
        .subtitle { font-size: 6px; color: #8a8ab0; margin-bottom: 4px; text-transform: uppercase; }
        .screen { display: none; height: 100%; flex-direction: column; justify-content: space-between; }
        .screen.active { display: flex; }
        .panel { background-color: #111122; border: 2px solid #3d3d5c; box-shadow: 3px 3px 0px #000; padding: 6px; margin-bottom: 5px; position: relative; }
        
        /* ДВИЖОК КАРТЫ (ПРИКЛЮЧЕНИЕ) */
        #map-grid {
            display: grid;
            grid-template-columns: repeat(9, 1fr);
            gap: 2px;
            background: #000;
            padding: 4px;
            border: 3px solid #3d3d5c;
            margin: 4px auto;
            width: 100%;
            max-width: 320px;
        }
        .map-tile {
            aspect-ratio: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            background: #152515;
            border-radius: 2px;
        }
        .tile-wall { background: #2b2b36; }
        .tile-floor { background: #1a2e1a; }
        .tile-mine { background: #2d231e; }
        .tile-waste { background: #3d2a1c; }
        .tile-abyss { background: #330d0d; }

        /* Панель управления D-Pad */
        .dpad-container { display: grid; grid-template-columns: repeat(3, 1fr); width: 105px; margin: 5px auto; gap: 3px; }
        .dpad-btn { font-family: 'Press Start 2P'; font-size: 10px; background: #252540; color: #fff; border: 2px outset #444477; padding: 8px 0; cursor: pointer; }
        .dpad-btn:active { border-style: inset; background: #151525; }

        /* Прогресс-бары */
        .bar-container { width: 100%; height: 12px; background-color: #1a1a1a; border: 2px solid #fff; margin-top: 2px; position: relative; }
        .hp-fill { height: 100%; background-color: #cc2222; width: 100%; transition: width 0.15s; }
        .mana-fill { height: 100%; background-color: #1f75fe; width: 100%; transition: width 0.15s; }
        .shield-fill { height: 100%; background-color: #777; width: 0%; transition: width 0.15s; }
        .exp-fill { height: 100%; background-color: #aa22cc; width: 0%; }

        #log { height: 50px; overflow-y: auto; background: #020205; color: #4aff4a; padding: 4px; text-align: left; border: 2px solid #3d3d5c; font-size: 6px; line-height: 1.3; }
        
        .grid-2 { display: flex; flex-wrap: wrap; gap: 4px; justify-content: center; }
        .menu-btn { font-family: 'Press Start 2P', cursive; background-color: #22223b; color: #d4af37; border: 3px outset #444466; padding: 8px; width: 95%; margin: 4px auto; display: block; font-size: 7px; cursor: pointer; }
        .card-btn { font-family: 'Press Start 2P', cursive; background-color: #17172b; color: #fff; border: 2px outset #3d3d5c; padding: 6px 2px; font-size: 6px; cursor: pointer; width: 48%; min-height: 30px; }
        .card-btn:disabled { opacity: 0.3; }
        .attack { color: #ff4444; } .defend { color: #44aaff; } .ultimate { color: #ffff44; border-color: #ffff44; }

        /* Боевой экран */
        .stage-container { position: relative; height: 80px; overflow: hidden; background: #03030a; border: 2px solid #222; }
        .sprite { font-size: 36px; position: absolute; bottom: 4px; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; }
        #hero-sprite { left: 15%; transform: scaleX(-1); }
        #enemy-sprite { right: 15%; }
        
        .float-anim { animation: floatEff 1.6s infinite ease-in-out; }
        .strike-left { animation: strikeL 0.3s ease-in-out; }
        .strike-right { animation: strikeR 0.3s ease-in-out; }
        .flash-red { animation: flashR 0.2s ease-in-out; }
        @keyframes floatEff { 0%, 100% { bottom: 4px; } 50% { bottom: 10px; } }
        @keyframes strikeL { 0% { left: 15%; } 50% { left: 45%; transform: scaleX(-1) scale(1.2); } 100% { left: 15%; } }
        @keyframes strikeR { 0% { right: 15%; } 50% { right: 45%; transform: scale(1.2); } 100% { right: 15%; } }
        @keyframes flashR { 0%, 100% { background: #03030a; } 50% { background: #400; } }

        .damage-pop { position: absolute; font-size: 8px; font-weight: bold; color: #ff3333; text-shadow: 1px 1px #000; animation: pUp 0.6s forwards ease-out; z-index: 10; }
        @keyframes pUp { 0% { opacity: 1; transform: translateY(0); } 100% { opacity: 0; transform: translateY(-20px) scale(1.1); } }

        .inv-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px; margin: 4px 0; }
        .inv-slot { background: #070710; border: 2px solid #333; height: 32px; display: flex; align-items: center; justify-content: center; font-size: 14px; cursor: pointer; }
        .rare { border-color: #4444ff; } .epic { border-color: #aa22cc; } .legend { border-color: #ffaa00; }
        .setting-row { display: flex; justify-content: space-between; align-items: center; padding: 6px; border-bottom: 1px solid #222; }
        .btn-small { padding: 3px 6px; font-family: 'Press Start 2P'; font-size: 5px; background: #3d3d5c; color: #fff; border: 2px outset #555; }
    </style>
</head>
<body>

    <div id="game-container">

        <!-- ЭКРАН 1: ГЛАВНОЕ МЕНЮ -->
        <div id="screen-menu" class="screen active">
            <h1 style="font-size: 11px; color: #ffff55; margin-top: 20px;">MLBB RPG:<br>ОДИССЕЯ МОНИИ</h1>
            <p class="subtitle">Открытый мир и Крипы v4.0</p>
            <div style="font-size: 36px; margin: 20px 0; animation: floatEff 2.2s infinite ease-in-out; height: 45px;">🏃‍♂️🐺⚔️</div>
            <button class="menu-btn" onclick="startAdventure()">НАЧАТЬ ПУТЕШЕСТВИЕ</button>
            <button class="menu-btn" onclick="switchScreen('screen-settings')">НАСТРОЙКИ</button>
        </div>

        <!-- ЭКРАН 2: НАСТРОЙКИ -->
        <div id="screen-settings" class="screen">
            <h1>НАСТРОЙКИ СИСТЕМЫ</h1>
            <div class="panel" style="text-align: left;">
                <div class="setting-row"><span>ЭКРАН:</span> <button id="cfg-screen" class="btn-small" onclick="toggleSetting('screen')">ОКНО</button></div>
                <div class="setting-row"><span>МУЗЫКА СИНТЕЗАТОРА:</span> <button id="cfg-music" class="btn-small" onclick="toggleSetting('music')">ВКЛ</button></div>
                <div class="setting-row"><span>ЗВУКИ УДАРОВ:</span> <button id="cfg-sound" class="btn-small" onclick="toggleSetting('sound')">ВКЛ</button></div>
                <div class="setting-row"><span>ВЫБОР КЛАССА ГЕРОЯ:</span> <button id="cfg-hero" class="btn-small" onclick="toggleSetting('hero')">АЛУКАРД</button></div>
            </div>
            <button class="menu-btn" onclick="switchScreen('screen-menu')">ВЕРНУТЬСЯ</button>
        </div>

        <!-- ЭКРАН 3: КАРТА ИССЛЕДОВАНИЯ МИРА -->
        <div id="screen-adventure" class="screen">
            <div>
                <h1 id="adv-location-title">ЛОКАЦИЯ 1</h1>
                <div style="display:flex; justify-content:space-between; font-size:6px; padding: 0 5px;">
                    <span>❤️ ОЗ: <span id="adv-hp">100/100</span></span>
                    <span>💰 ЗОЛОТО: <span id="adv-gold" style="color:#ffff55;">0</span></span>
                    <span>⭐ УРОВЕНЬ: <span id="adv-lvl">1</span></span>
                </div>
            </div>

            <!-- Сетка карты -->
            <div id="map-grid"></div>

            <div style="font-size:5px; color:#8a8ab0; margin-bottom:2px;">
                Управление: Кнопки ниже или клавиши <b>WASD / Стрелочки</b> на клавиатуре.
            </div>

            <!-- Элементы D-Pad перемещения -->
            <div>
                <div class="dpad-container">
                    <div></div>
                    <button class="dpad-btn" onclick="movePlayer(0, -1)">▲</button>
                    <div></div>
                    <button class="dpad-btn" onclick="movePlayer(-1, 0)">◄</button>
                    <button class="dpad-btn" style="background:#3d3d5c; font-size:6px;" onclick="openCampHub()">🎒</button>
                    <button class="dpad-btn" onclick="movePlayer(1, 0)">►</button>
                    <div></div>
                    <button class="dpad-btn" onclick="movePlayer(0, 1)">▼</button>
                    <div></div>
                </div>
            </div>

            <button class="menu-btn" style="background:#333; margin-top:2px;" onclick="switchScreen('screen-menu')">В ГЛАВНОЕ МЕНЮ</button>
        </div>

        <!-- ЭКРАН 4: БЕЗОПАСНЫЙ ЛАГЕРЬ И КУЗНИЦА -->
        <div id="screen-camp" class="screen">
            <h1 style="color:#55ff55;">РЮКЗАК И СНАРЯЖЕНИЕ</h1>
            <div class="panel" style="text-align: left; font-size: 6px; line-height: 1.4;">
                <div>ГЕРОЙ: <span id="camp-hero" style="color:#6da5ff;">АЛУКАРД</span> (УРОВЕНЬ <span id="camp-lvl">1</span>)</div>
                <div>УРОН АТАК: <span id="camp-dmg" style="color:#ff5555;">15</span> (+доп. от меча)</div>
                <div style="margin-top:3px;">ОПЫТ ДО СЛЕД. УРОВНЯ:</div>
                <div class="bar-container" style="height:6px;"><div id="camp-exp-fill" class="exp-fill"></div></div>
            </div>

            <div class="panel">
                <div style="font-size: 6px; text-align: left; margin-bottom: 2px;">ЭКИПИРОВАНО:</div>
                <div style="display:flex; justify-content: space-around;">
                    <div class="inv-slot" id="slot-weapon" style="width:45%;" onclick="unequipItem('weapon')">⚔️ Пусто</div>
                    <div class="inv-slot" id="slot-armor" style="width:45%;" onclick="unequipItem('armor')">🛡️ Пусто</div>
                </div>
            </div>

            <div class="panel">
                <div style="font-size: 6px; text-align: left; margin-bottom: 2px;">ИНВЕНТАРЬ (КЛИК ДЛЯ ИСПОЛЬЗОВАНИЯ):</div>
                <div class="inv-grid" id="inventory-container"></div>
            </div>

            <div class="grid-2">
                <button class="card-btn attack" onclick="craftItem()">🔨 КУЗНИЦА (30💰)</button>
                <button class="card-btn defend" onclick="buyHealPotion()">🧪 КУПИТЬ ЗЕЛЬЕ (15💰)</button>
            </div>
            <button class="menu-btn" style="background:#444;" onclick="switchScreen('screen-adventure')">ВЕРНУТЬСЯ НА КАРТУ</button>
        </div>

        <!-- ЭКРАН 5: БОЕВАЯ СИСТЕМА -->
        <div id="screen-battle" class="screen">
            <h1 style="color:#ff4444;">РЕЖИМ БИТВЫ</h1>
            <div class="panel" id="battle-field">
                <div style="display:flex; justify-content:space-between; font-size:6px; font-weight:bold; margin-bottom:2px;">
                    <span id="bt-player-name" style="color:#6da5ff;">ГЕРОЙ</span>
                    <span id="bt-enemy-name" style="color:#ff6d6d;">КРИП</span>
                </div>
                <div class="stage-container">
                    <div id="hero-sprite" class="sprite float-anim">⚔️</div>
                    <div id="enemy-sprite" class="sprite float-anim">👾</div>
                </div>
                <div style="text-align: left; margin-top:2px;">
                    <div class="bar-container"><div id="enemy-hp-fill" class="hp-fill"></div></div>
                </div>
            </div>

            <div class="panel" style="padding:2px;"><div id="log">Приготовьтесь к бою!</div></div>

            <div class="panel" id="player-panel">
                <div style="display:flex; justify-content:space-between; font-size:6px; font-weight:bold; margin-bottom:2px;">
                    <span>ТВОЕ ОЗ: <span id="player-hp-text" style="color:#55ff55;">100/100</span></span>
                    <span>ЭНЕРГИЯ: <span id="player-mana-text" style="color:#55aaff;">⚡ 3/3</span></span>
                </div>
                <div class="bar-container">
                    <div id="player-hp-fill" class="hp-fill" style="background-color:#22cc22;"></div>
                    <div id="player-shield-fill" class="shield-fill" style="position:absolute; top:0; left:0;"></div>
                </div>
                <div class="cards" style="margin-top:4px;">
                    <button class="card-btn attack" id="btn-atk1" onclick="useCombatSkill('atk1')">⚔️ Атака<br>(+1 ⚡)</button>
                    <button class="card-btn attack" id="btn-atk2" onclick="useCombatSkill('atk2')">💥 Навык<br>(-1 ⚡)</button>
                    <button class="card-btn defend" id="btn-def" onclick="useCombatSkill('def')">🛡️ Блок<br>(-1 ⚡)</button>
                    <button class="card-btn ultimate" id="btn-ult" onclick="useCombatSkill('ult')">🔮 УЛЬТ<br>(-3 ⚡)</button>
                </div>
            </div>
        </div>

    </div>

    <script>
        // ИГРОВОЙ ДВИЖОК И КОНФИГУРАЦИЯ
        let config = { sound: true, music: true, hero: 'алукард', fullscreen: false };
        let player = { lvl: 1, exp: 0, nextExp: 80, gold: 30, baseDmg: 16, hp: 100, maxHp: 100, mana: 3, maxMana: 4, shield: 0, weapon: null, armor: null };
        let inventory = [{ type: 'potion', name: 'Зелье ОЗ', icon: '🧪' }];
        let currentZone = 0;
        let playerX = 1;
        let playerY = 1;
        let combatActive = false;
        let currentCreep = null;

        // База лута кузницы
        const lootTable = [
            { type: 'weapon', name: 'Меч Легиона', icon: '🗡️', stat: 8, rare: 'common' },
            { type: 'weapon', name: 'Копьё Дракона', icon: '🔱', stat: 18, rare: 'epic' },
            { type: 'weapon', name: 'Клинок Отчаяния', icon: '⚔️', stat: 35, rare: 'legend' },
            { type: 'armor', name: 'Латный щиток', icon: '👕', stat: 6, rare: 'common' },
            { type: 'armor', name: 'Кираса Монии', icon: '🛡️', stat: 16, rare: 'epic' },
            { type: 'armor', name: 'Бессмертие Спасителя', icon: '💎', stat: 33, rare: 'legend' }
        ];

        // 5 ОГРОМНЫХ ЛОКАЦИЙ (9x9 Матрицы)
        // Спецификация легенды: 0 = Пусто, 1 = Стена/Преграда, 2 = Крип, 3 = Портал (🎯) в следующую главу
        const zones = [
            {
                title: "🌲 Сады Империи Мония",
                tileClass: "tile-floor",
                wallClass: "tile-wall",
                wallIcon: "🌲",
                map: [
                    [1,1,1,1,1,1,1,1,1],
                    [1,0,0,0,1,0,0,2,1],
                    [1,0,1,0,1,0,1,0,1],
                    [1,2,1,0,0,0,1,0,1],
                    [1,0,1,1,1,0,1,2,1],
                    [1,0,0,2,1,0,1,0,1],
                    [1,1,0,0,1,0,0,0,1],
                    [1,2,0,0,0,0,1,3,1],
                    [1,1,1,1,1,1,1,1,1]
                ],
                creeps: [
                    { name: "Слайм Монии", hp: 45, maxHp: 45, sprite: "🟢", minDmg: 4, maxDmg: 8, exp: 35, gold: 15 },
                    { name: "Маленький Гоблин", hp: 55, maxHp: 55, sprite: "👺", minDmg: 5, maxDmg: 10, exp: 45, gold: 20 }
                ]
            },
            {
                title: "🍁 Шепчущий Древний Лес",
                tileClass: "tile-floor",
                wallClass: "tile-wall",
                wallIcon: "🌿",
                map: [
                    [1,1,1,1,1,1,1,1,1],
                    [1,0,2,0,0,0,1,2,1],
                    [1,1,1,1,0,1,1,0,1],
                    [1,0,0,2,0,0,1,0,1],
                    [1,0,1,1,1,1,1,0,1],
                    [1,2,1,0,0,0,0,0,1],
                    [1,0,1,0,1,1,1,2,1],
                    [1,0,0,0,2,0,1,3,1],
                    [1,1,1,1,1,1,1,1,1]
                ],
                creeps: [
                    { name: "Лесной Волк", hp: 75, maxHp: 75, sprite: "🐺", minDmg: 8, maxDmg: 14, exp: 60, gold: 30 },
                    { name: "Ядовитый Паук", hp: 85, maxHp: 85, sprite: "🕷️", minDmg: 10, maxDmg: 17, exp: 75, gold: 35 }
                ]
            },
            {
                title: "⛰️ Заброшенные Каменные Шахты",
                tileClass: "tile-mine",
                wallClass: "tile-wall",
                wallIcon: "🧱",
                map: [
                    [1,1,1,1,1,1,1,1,1],
                    [1,0,0,0,1,0,0,2,1],
                    [1,0,1,0,0,0,1,0,1],
                    [1,2,1,1,1,1,1,0,1],
                    [1,0,0,2,1,0,0,0,1],
                    [1,1,1,0,1,0,1,1,1],
                    [1,2,0,0,1,2,1,2,1],
                    [1,0,1,0,0,0,0,3,1],
                    [1,1,1,1,1,1,1,1,1]
                ],
                creeps: [
                    { name: "Каменный Голем", hp: 120, maxHp: 120, sprite: "🗿", minDmg: 12, maxDmg: 22, exp: 110, gold: 45 },
                    { name: "Шахтный Призрак", hp: 105, maxHp: 105, sprite: "👻", minDmg: 15, maxDmg: 25, exp: 125, gold: 50 }
                ]
            },
            {
                title: "🏜️ Выжженные Пустоши Заката",
                tileClass: "tile-waste",
                wallClass: "tile-wall",
                wallIcon: "⛰️",
                map: [
                    [1,1,1,1,1,1,1,1,1],
                    [1,0,2,1,0,2,1,0,1],
                    [1,0,0,1,0,0,1,0,1],
                    [1,1,0,0,0,0,0,2,1],
                    [1,2,0,1,1,1,1,0,1],
                    [1,0,1,1,0,0,1,0,1],
                    [1,0,2,1,2,0,0,2,1],
                    [1,1,0,0,0,1,1,3,1],
                    [1,1,1,1,1,1,1,1,1]
                ],
                creeps: [
                    { name: "Проклятый Мечник", hp: 160, maxHp: 160, sprite: "💀", minDmg: 18, maxDmg: 30, exp: 180, gold: 65 },
                    { name: "Ищейка Рока", hp: 140, maxHp: 140, sprite: "🐕", minDmg: 22, maxDmg: 34, exp: 195, gold: 75 }
                ]
            },
            {
                title: "🌋 Сумрачная Цитадель Бездны",
                tileClass: "tile-abyss",
                wallClass: "tile-wall",
                wallIcon: "🔥",
                map: [
                    [1,1,1,1,1,1,1,1,1],
                    [1,0,0,0,1,0,0,2,1],
                    [1,0,1,0,1,0,1,0,1],
                    [1,2,1,0,0,0,1,0,1],
                    [1,0,1,1,1,1,1,2,1],
                    [1,0,0,2,1,0,0,0,1],
                    [1,1,1,0,1,0,1,1,1],
                    [1,2,0,0,0,2,1,3,1],
                    [1,1,1,1,1,1,1,1,1]
                ],
                creeps: [
                    { name: "Демон Пекла", hp: 220, maxHp: 220, sprite: "👹", minDmg: 25, maxDmg: 42, exp: 260, gold: 110 },
                    { name: "ТАМУЗ (ГЕНЕРАЛ ХАОСА)", hp: 450, maxHp: 450, sprite: "🔱", minDmg: 35, maxDmg: 58, exp: 999, gold: 500, isBoss: true }
                ]
            }
        ];

        // ПРОЦЕДУРНЫЙ АУДИОДВИЖОК (Web Audio API)
        let audioCtx = null;
        let synthInterval = null;
        let stepCount = 0;

        function checkAudioInit() {
            if (!audioCtx) {
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                startWorldMusic();
            }
        }

        function playBeep(freq, type, duration, volume = 0.015) {
            if (!config.sound || !audioCtx) return;
            if (audioCtx.state === 'suspended') audioCtx.resume();
            let osc = audioCtx.createOscillator();
            let gain = audioCtx.createGain();
            osc.type = type;
            osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
            gain.gain.setValueAtTime(volume, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + duration);
            osc.connect(gain); gain.connect(audioCtx.destination);
            osc.start(); osc.stop(audioCtx.currentTime + duration);
        }

        function startWorldMusic() {
            if (synthInterval) clearInterval(synthInterval);
            const notes = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00];
            synthInterval = setInterval(() => {
                if (!config.music || !audioCtx) return;
                let currentNote = notes[stepCount % notes.length];
                if (stepCount % 4 === 0) playBeep(currentNote / 2, 'sawtooth', 0.4, 0.008);
                if (stepCount % 2 === 0) playBeep(currentNote, 'triangle', 0.15, 0.008);
                stepCount++;
            }, 320);
        }

        const soundPack = {
            click: () => playBeep(520, 'sine', 0.05, 0.03),
            step: () => playBeep(140, 'triangle', 0.04, 0.02),
            combatHit: () => { playBeep(240, 'sawtooth', 0.12, 0.03); playBeep(110, 'square', 0.1, 0.02); },
            shield: () => playBeep(420, 'sine', 0.2, 0.04),
            lvlUp: () => { [392, 523, 659, 784].forEach((f, i) => setTimeout(() => playBeep(f, 'sine', 0.25, 0.03), i*90)); }
        };

        // НАСТРОЙКИ СИСТЕМЫ И ПЕРЕКЛЮЧЕНИЯ ЭКРАНОВ
        function switchScreen(id) {
            checkAudioInit();
            soundPack.click();
            document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
            document.getElementById(id).classList.add('active');
        }

        function toggleSetting(key) {
            checkAudioInit(); soundPack.click();
            if (key === 'sound' || key === 'music') {
                config[key] = !config[key];
                document.getElementById(`cfg-${key}`).innerText = config[key] ? "ВКЛ" : "ВЫКЛ";
            } else if (key === 'screen') {
                config.fullscreen = !config.fullscreen;
                let container = document.getElementById('game-container');
                if (config.fullscreen) {
                    container.classList.add('fullscreen'); document.getElementById('cfg-screen').innerText = "ВЕСЬ ЭКРАН";
                    if (document.documentElement.requestFullscreen) document.documentElement.requestFullscreen();
                } else {
                    container.classList.remove('fullscreen'); document.getElementById('cfg-screen').innerText = "ОКНО";
                    if (document.exitFullscreen && document.fullscreenElement) document.exitFullscreen();
                }
            } else if (key === 'hero') {
                config.hero = config.hero === 'алукард' ? 'мия' : 'алукард';
                document.getElementById('cfg-hero').innerText = config.hero.toUpperCase();
            }
        }

        // РЕЖИМ ПРИКЛЮЧЕНИЯ: ГЕНЕРАЦИЯ И ПЕРЕМЕЩЕНИЕ НА КАРТЕ
        function startAdventure() {
            currentZone = 0;
            player.gold = 30; player.lvl = 1; player.exp = 0; player.hp = 100; player.maxHp = 100;
            player.weapon = null; player.armor = null;
            inventory = [{ type: 'potion', name: 'Зелье ОЗ', icon: '🧪' }];
            spawnPlayerOnMap();
            loadZone(0);
        }

        function spawnPlayerOnMap() {
            playerX = 1; playerY = 1;
        }

        function loadZone(zoneIdx) {
            currentZone = zoneIdx;
            if (currentZone >= zones.length) {
                alert("🏆 ПОЗДРАВЛЯЕМ! Вы прошли все 5 локаций, уничтожили Генерала Бездны и спасли мир Монии!");
                switchScreen('screen-menu');
                return;
            }
            spawnPlayerOnMap();
            renderMap();
            switchScreen('screen-adventure');
        }

        function renderMap() {
            let zData = zones[currentZone];
            document.getElementById('adv-location-title').innerText = `${currentZone+1}/5: ${zData.title}`;
            document.getElementById('adv-hp').innerText = `${player.hp}/${player.maxHp}`;
            document.getElementById('adv-gold').innerText = player.gold;
            document.getElementById('adv-lvl').innerText = player.lvl;

            let grid = document.getElementById('map-grid');
            grid.innerHTML = "";

            for (let y = 0; y < 9; y++) {
                for (let x = 0; x < 9; x++) {
                    let tile = document.createElement('div');
                    let type = zData.map[y][x];

                    tile.className = "map-tile " + zData.tileClass;
                    
                    if (type === 1) {
                        tile.className = "map-tile " + zData.wallClass;
                        tile.innerText = zData.wallIcon;
                    } else if (type === 2) {
                        tile.innerText = "👾"; // Крип
                    } else if (type === 3) {
                        tile.innerText = "🎯"; // Врата перехода
                    }

                    // Если здесь стоит персонаж игрока
                    if (x === playerX && y === playerY) {
                        tile.innerText = config.hero === 'алукард' ? "🏃‍♂️" : "🏹";
                    }

                    grid.appendChild(tile);
                }
            }
        }

        function movePlayer(dx, dy) {
            if (combatActive) return;
            checkAudioInit();
            
            let nextX = playerX + dx;
            let nextY = playerY + dy;
            let zData = zones[currentZone];

            // Проверка границ и стен
            if (nextX >= 0 && nextX < 9 && nextY >= 0 && nextY < 9) {
                if (zData.map[nextY][nextX] !== 1) {
                    playerX = nextX;
                    playerY = nextY;
                    soundPack.step();

                    let tileEvent = zData.map[playerY][playerX];
                    if (tileEvent === 2) {
                        // Столкновение с крипом -> Бой!
                        triggerBattle();
                        return;
                    } else if (tileEvent === 3) {
                        // Переход в следующую большую локацию
                        alert("✨ Вы входите в Световой Портал и перемещаетесь в следующую локацию!");
                        loadZone(currentZone + 1);
                        return;
                    }
                    renderMap();
                }
            }
        }

        // Поддержка клавиатуры (WASD / Стрелочки)
        window.addEventListener('keydown', (e) => {
            if (document.getElementById('screen-adventure').classList.contains('active')) {
                if (e.key === 'w' || e.key === 'W' || e.key === 'ArrowUp') movePlayer(0, -1);
                if (e.key === 's' || e.key === 'S' || e.key === 'ArrowDown') movePlayer(0, 1);
                if (e.key === 'a' || e.key === 'A' || e.key === 'ArrowLeft') movePlayer(-1, 0);
                if (e.key === 'd' || e.key === 'D' || e.key === 'ArrowRight') movePlayer(1, 0);
            }
        });

        // ОКНО ЛАГЕРЯ / ИНВЕНТАРЬ
        function openCampHub() {
            switchScreen('screen-camp');
            document.getElementById('camp-hero').innerText = config.hero.toUpperCase();
            document.getElementById('camp-lvl').innerText = player.lvl;
            document.getElementById('camp-gold').innerText = player.gold;
            document.getElementById('camp-exp-fill').style.width = `${(player.exp / player.nextExp)*100}%`;
            
            let weaponStat = player.weapon ? player.weapon.stat : 0;
            document.getElementById('camp-dmg').innerText = player.baseDmg + weaponStat;

            document.getElementById('slot-weapon').innerText = player.weapon ? `${player.weapon.icon} +${player.weapon.stat}` : '⚔️ Оружие';
            document.getElementById('slot-armor').innerText = player.armor ? `${player.armor.icon} +${player.armor.stat}` : '🛡️ Броня';

            let container = document.getElementById('inventory-container');
            container.innerHTML = "";
            inventory.forEach((item, idx) => {
                let slot = document.createElement('div');
                slot.className = `inv-slot ${item.rare || ''}`;
                slot.innerText = item.icon;
                slot.onclick = () => useItem(idx);
                container.appendChild(slot);
            });
        }

        function useItem(idx) {
            let item = inventory[idx];
            soundPack.click();
            if (item.type === 'potion') {
                player.hp = player.maxHp;
                alert("🧪 Вы выпили зелье. Здоровье полностью восстановлено!");
                inventory.splice(idx, 1);
            } else if (item.type === 'weapon') {
                if (player.weapon) inventory.push(player.weapon);
                player.weapon = item; inventory.splice(idx, 1);
                alert(`⚔️ Экипирован меч: ${item.name}`);
            } else if (item.type === 'armor') {
                if (player.armor) inventory.push(player.armor);
                player.armor = item; inventory.splice(idx, 1);
                alert(`🛡️ Надет доспех: ${item.name}`);
            }
            openCampHub();
        }

        function unequipItem(slot) {
            if (slot === 'weapon' && player.weapon) { inventory.push(player.weapon); player.weapon = null; }
            if (slot === 'armor' && player.armor) { inventory.push(player.armor); player.armor = null; }
            openCampHub();
        }

        function buyHealPotion() {
            if (player.gold >= 15) {
                player.gold -= 15;
                inventory.push({ type: 'potion', name: 'Зелье ОЗ', icon: '🧪' });
                openCampHub();
            } else alert("Не хватает золота!");
        }

        function craftItem() {
            if (player.gold >= 30) {
                player.gold -= 30;
                let randomGear = { ...lootTable[Math.floor(Math.random() * lootTable.length)] };
                inventory.push(randomGear);
                alert(`🔨 Вы выковали предмет: ${randomGear.name} [${randomGear.rare.toUpperCase()}]!`);
                openCampHub();
            } else alert("Кузнецу нужно минимум 30 золотых!");
        }

        // БОЕВОЙ ТАКТИЧЕСКИЙ ДВИЖОК
        function triggerBattle() {
            combatActive = true;
            let zoneCreeps = zones[currentZone].creeps;
            // Выбираем случайного крипа из пула текущей локации
            let baseCreep = zoneCreeps[Math.floor(Math.random() * zoneCreeps.length)];
            currentCreep = { ...baseCreep };

            document.getElementById('bt-player-name').innerText = config.hero.toUpperCase();
            document.getElementById('bt-enemy-name').innerText = currentCreep.name;
            document.getElementById('enemy-sprite').innerText = currentCreep.sprite;
            document.getElementById('hero-sprite').innerText = config.hero === 'алукард' ? '⚔️' : '🏹';

            player.mana = 3;
            player.shield = 0;
            gameState.isGameOver = false;
            gameState.currentTurn = 'player';

            document.getElementById('log').innerHTML = `Враг ${currentCreep.name} нападает! Твой ход.`;
            updateBattleUI();
            switchScreen('screen-battle');
        }

        function updateBattleUI() {
            document.getElementById('player-hp-text').innerText = `${player.hp}/${player.maxHp}`;
            document.getElementById('player-hp-fill').style.width = `${(player.hp / player.maxHp)*100}%`;
            document.getElementById('player-shield-fill').style.width = `${(player.shield / player.maxHp)*100}%`;
            document.getElementById('player-mana-text').innerText = `⚡ ${player.mana}/${player.maxMana}`;

            document.getElementById('enemy-hp-text').innerText = `${currentCreep.hp}/${currentCreep.maxHp}`;
            document.getElementById('enemy-hp-fill').style.width = `${(currentCreep.hp / currentCreep.maxHp)*100}%`;

            let isTurn = (gameState.currentTurn === 'player' && !gameState.isGameOver);
            document.getElementById('btn-atk1').disabled = !isTurn;
            document.getElementById('btn-atk2').disabled = !isTurn || player.mana < 1;
            document.getElementById('btn-def').disabled = !isTurn || player.mana < 1;
            document.getElementById('btn-ult').disabled = !isTurn || player.mana < 3;
        }

        function addLog(t, c='#fff') {
            let l = document.getElementById('log'); l.innerHTML += `<br><span style="color:${c}">${t}</span>`;
            l.scrollTop = l.scrollHeight;
        }

        function spawnPopup(txt, isEnemy) {
            let p = document.createElement('div'); p.className = 'damage-pop'; p.innerText = txt;
            p.style.left = isEnemy ? '70%' : '20%'; p.style.bottom = '35px';
            if (txt.includes('+')) p.style.color = '#55ff55';
            document.getElementById('battle-field').appendChild(p); setTimeout(() => p.remove(), 600);
        }

        function useCombatSkill(type) {
            let heroSprite = document.getElementById('hero-sprite');
            let wBonus = player.weapon ? player.weapon.stat : 0;
            let currentAtk = player.baseDmg + wBonus;

            if (type === 'atk1') {
                let dmg = Math.floor(Math.random() * 5) + Math.floor(currentAtk * 0.8);
                currentCreep.hp = Math.max(0, currentCreep.hp - dmg);
                player.mana = Math.min(player.maxMana, player.mana + 1);
                soundPack.combatHit(); heroSprite.classList.add('strike-left');
                setTimeout(() => heroSprite.classList.remove('strike-left'), 300);
                spawnPopup(`-${dmg}`, true); addLog(`Обычный выпад нанес ${dmg} урона. Восстановлена 1 Энергия.`);
            }
            else if (type === 'atk2' && player.mana >= 1) {
                player.mana -= 1;
                let dmg = Math.floor(Math.random() * 10) + Math.floor(currentAtk * 1.4);
                currentCreep.hp = Math.max(0, currentCreep.hp - dmg);
                soundPack.combatHit(); heroSprite.classList.add('strike-left');
                setTimeout(() => heroSprite.classList.remove('strike-left'), 300);
                spawnPopup(`-${dmg}!`, true); addLog(`Боевой Навык ранил крипа на ${dmg} урона.`, '#ff9999');
            }
            else if (type === 'def' && player.mana >= 1) {
                player.mana -= 1;
                let armBonus = player.armor ? player.armor.stat : 0;
                let sVal = Math.floor(Math.random() * 10) + 15 + armBonus;
                player.shield += sVal; soundPack.shield();
                spawnPopup(`+🛡️${sVal}`, false); addLog(`Вы заблокировались щитом на +${sVal} защиты.`, '#55aaff');
            }
            else if (type === 'ult' && player.mana >= 3) {
                player.mana -= 3;
                let dmg = Math.floor(Math.random() * 15) + Math.floor(currentAtk * 2.3);
                currentCreep.hp = Math.max(0, currentCreep.hp - dmg);
                let heal = Math.floor(dmg * 0.4);
                player.hp = Math.min(player.maxHp, player.hp + heal);
                
                soundPack.combatHit();
                document.getElementById('battle-field').classList.add('flash-red');
                setTimeout(() => document.getElementById('battle-field').classList.remove('flash-red'), 250);
                
                spawnPopup(`-${dmg}💥`, true); spawnPopup(`+${heal}`, false);
                addLog(`🔮 ВСПЫШКА УЛЬТИМЕЙТА! Нанесено ${dmg} урона. Восстановлено +${heal} ОЗ.`, '#ffff44');
            }

            updateBattleUI();

            if (currentCreep.hp <= 0) {
                battleVictoryEnd();
                return;
            }

            gameState.currentTurn = 'enemy';
            setTimeout(enemyAIAction, 800);
        }

        function enemyAIAction() {
            if (gameState.isGameOver) return;
            let enemySprite = document.getElementById('enemy-sprite');
            enemySprite.classList.add('strike-right'); setTimeout(() => enemySprite.classList.remove('strike-right'), 300);

            let rawDmg = Math.floor(Math.random() * (currentCreep.maxDmg - currentCreep.minDmg + 1)) + currentCreep.minDmg;
            
            if (player.shield > 0) {
                if (player.shield >= rawDmg) { player.shield -= rawDmg; rawDmg = 0; addLog(`🛡️ Броня полностью отразила атаку.`); }
                else { rawDmg -= player.shield; player.shield = 0; addLog(`🛡️ Щит сломан. Пропущено ${rawDmg} урона.`); }
            } else {
                addLog(`${currentCreep.name} бьет в ответ: получено ${rawDmg} урона.`, '#ff4444');
            }

            if (rawDmg > 0) {
                player.hp = Math.max(0, player.hp - rawDmg);
                spawnPopup(`-${rawDmg}`, false); soundPack.combatHit();
            } else {
                spawnPopup("Блок", false); soundPack.shield();
            }

            updateBattleUI();

            if (player.hp <= 0) {
                gameState.isGameOver = true;
                alert(`💀 Вы погибли в бою с ${currentCreep.name}! Прогресс локации обнулен.`);
                combatActive = false;
                switchScreen('screen-menu');
                return;
            }

            gameState.currentTurn = 'player';
            updateBattleUI();
        }

        function battleVictoryEnd() {
            gameState.isGameOver = true;
            soundPack.lvlUp();
            player.gold += currentCreep.gold;
            player.exp += currentCreep.exp;
            
            alert(`🎉 Крип уничтожен! Вы получили +${currentCreep.gold}💰 и +${currentCreep.exp} EXP!`);
            
            // Удаляем крипа с карты, превращая клетку в чистый пол (0)
            zones[currentZone].map[playerY][playerX] = 0;
            combatActive = false;

            // Проверка повышения уровня
            if (player.exp >= player.nextExp) {
                player.lvl++;
                player.exp -= player.nextExp;
                player.nextExp = Math.floor(player.nextExp * 1.3);
                player.baseDmg += 4;
                player.maxHp += 12;
                player.hp = player.maxHp;
                alert(`✨ УРОВЕНЬ ПОВЫШЕН! Теперь вы ${player.lvl} уровня! Параметры увеличены.`);
            }

            renderMap();
            switchScreen('screen-adventure');
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(GAME_HTML)

if __name__ == '__main__':
    app.run(debug=True)
