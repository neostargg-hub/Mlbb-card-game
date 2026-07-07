from flask import Flask, render_template_string

app = Flask(__name__)

GAME_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>MLBB RPG: Одиссея Монии — v7.0</title>
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
    <style>
        *, *::before, *::after { box-sizing: border-box; }
        body {
            font-family: 'Press Start 2P', cursive;
            background-color: #020205;
            color: #d1d1e0;
            margin: 0; padding: 5px; font-size: 7px;
            text-align: center; overflow: hidden;
            user-select: none; -webkit-user-select: none;
            height: 100vh; display: flex; justify-content: center; align-items: center;
        }
        
        #game-container {
            width: 100%; max-width: 440px; height: 100%; max-height: 740px;
            display: flex; flex-direction: column; justify-content: space-between;
            background: linear-gradient(135deg, #0f0f20 0%, #030307 100%);
            border: 4px solid #555577; box-shadow: 0 0 35px rgba(0,0,0,0.9);
            padding: 8px; position: relative; transition: all 0.3s ease;
        }
        #game-container.fullscreen { max-width: 100vw; max-height: 100vh; border: none; padding: 10px; }
        
        .screen { display: none; height: 100%; flex-direction: column; justify-content: space-between; }
        .screen.active { display: flex; }
        .col-left, .col-right { width: 100%; display: flex; flex-direction: column; justify-content: space-between; }
        
        @media (orientation: landscape) and (min-width: 550px) {
            #game-container { max-width: 840px; max-height: 420px; flex-direction: row; padding: 10px; }
            .screen { flex-direction: row !important; width: 100%; gap: 12px; }
            .col-left { width: 49%; height: 100%; justify-content: space-between; }
            .col-right { width: 49%; height: 100%; justify-content: space-between; }
        }

        h1 { font-size: 9px; color: #ffff55; text-shadow: 2px 2px #000; margin: 3px 0; text-transform: uppercase; letter-spacing: 1px; }
        .subtitle { font-size: 6px; color: #8a8ab0; margin-bottom: 4px; text-transform: uppercase; }
        .panel { background-color: #0b0b14; border: 2px solid #3d3d5c; box-shadow: 3px 3px 0px #000; padding: 6px; margin-bottom: 4px; position: relative; }
        
        #map-grid {
            display: grid; grid-template-columns: repeat(9, 1fr); gap: 2px;
            background: #05050a; padding: 4px; border: 3px solid #444466; margin: 2px auto;
            width: 100%; max-width: 280px;
        }
        @media (orientation: landscape) { #map-grid { max-width: 230px; } }

        .map-tile {
            aspect-ratio: 1; display: flex; align-items: center; justify-content: center;
            font-size: 11px; background: #122212; border-radius: 2px; text-shadow: 1px 1px 0 #000;
        }
        .tile-wall { background: #22222b; }
        .tile-floor { background: #142414; }
        .tile-mine { background: #261c17; }
        .tile-waste { background: #332015; }
        .tile-abyss { background: #2b0a0a; }

        .dpad-container { display: grid; grid-template-columns: repeat(3, 1fr); width: 140px; margin: 4px auto; gap: 6px; }
        .dpad-btn { font-family: 'Press Start 2P'; font-size: 15px; background: #252542; color: #fff; border: 2px outset #555588; padding: 12px 0; cursor: pointer; border-radius: 6px; }
        .dpad-btn:active { border-style: inset; background: #15152b; color: #ffea00; }

        .bar-container { width: 100%; height: 11px; background-color: #111; border: 2px solid #fff; margin-top: 2px; position: relative; }
        .hp-fill { height: 100%; background-color: #cc2222; width: 100%; transition: width 0.15s; }
        .mana-fill { height: 100%; background-color: #1f75fe; width: 100%; transition: width 0.15s; }
        .shield-fill { height: 100%; background-color: #777788; width: 0%; transition: width 0.15s; }
        .exp-fill { height: 100%; background-color: #aa22cc; width: 0%; }

        #log { height: 50px; overflow-y: auto; background: #010103; color: #4aff4a; padding: 4px; text-align: left; border: 2px solid #3d3d5c; font-size: 5.5px; line-height: 1.4; }
        @media (orientation: landscape) { #log { height: 65px; } }
        
        .grid-2 { display: flex; flex-wrap: wrap; gap: 4px; justify-content: center; }
        .menu-btn { font-family: 'Press Start 2P', cursive; background-color: #1f1f3a; color: #d4af37; border: 3px outset #444477; padding: 10px; width: 95%; margin: 4px auto; display: block; font-size: 8px; cursor: pointer; border-radius: 4px; }
        
        .cards { display: flex; flex-wrap: wrap; gap: 4px; justify-content: space-between; }
        .card-btn { font-family: 'Press Start 2P', cursive; background-color: #131324; color: #fff; border: 2px outset #3d3d5c; padding: 8px 1px; font-size: 6px; cursor: pointer; width: 49%; min-height: 40px; border-radius: 4px; line-height: 1.3; }
        .card-btn:disabled { opacity: 0.20; cursor: not-allowed; border-color: #222; }
        .attack { color: #ff6666; border-color: #aa4444; } .defend { color: #66b2ff; border-color: #4477aa; } .ultimate { color: #ffff55; border-color: #ffff55; font-weight: bold; }

        .stage-container { position: relative; height: 80px; overflow: hidden; background: #020207; border: 2px solid #333; margin-top: 2px; }
        .sprite { font-size: 34px; position: absolute; bottom: 4px; width: 45px; height: 45px; display: flex; align-items: center; justify-content: center; }
        #hero-sprite { left: 15%; transform: scaleX(-1); }
        #enemy-sprite { right: 15%; }
        
        .float-anim { animation: floatEff 1.6s infinite ease-in-out; }
        .strike-left { animation: strikeL 0.3s ease-in-out; }
        .strike-right { animation: strikeR 0.3s ease-in-out; }
        .flash-red { animation: flashR 0.2s ease-in-out; }
        @keyframes floatEff { 0%, 100% { bottom: 4px; } 50% { bottom: 10px; } }
        @keyframes strikeL { 0% { left: 15%; } 50% { left: 45%; transform: scaleX(-1) scale(1.2); } 100% { left: 15%; } }
        @keyframes strikeR { 0% { right: 15%; } 50% { right: 45%; transform: scale(1.2); } 100% { right: 15%; } }
        @keyframes flashR { 0%, 100% { background: #020207; } 50% { background: #400; } }

        .damage-pop { position: absolute; font-size: 9px; font-weight: bold; color: #ff3333; text-shadow: 1.5px 1.5px #000; animation: pUp 0.6s forwards ease-out; z-index: 10; }
        @keyframes pUp { 0% { opacity: 1; transform: translateY(0); } 100% { opacity: 0; transform: translateY(-25px) scale(1.2); } }

        .inv-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px; margin: 4px 0; }
        .inv-slot { background: #04040a; border: 2px solid #333; height: 36px; display: flex; align-items: center; justify-content: center; font-size: 16px; cursor: pointer; border-radius: 4px; }
        .common { border-color: #888; } .epic { border-color: #22aaff; } .legend { border-color: #ffaa00; text-shadow: 0 0 4px #ffaa00; }
        .setting-row { display: flex; justify-content: space-between; align-items: center; padding: 6px; border-bottom: 1px solid #222; }
        .btn-small { padding: 5px 8px; font-family: 'Press Start 2P'; font-size: 6px; background: #3d3d5c; color: #fff; border: 2px outset #555; cursor: pointer; border-radius: 3px; }
    </style>
</head>
<body>

    <div id="game-container">

        <!-- ЭКРАН 1: ГЛАВНОЕ МЕНЮ -->
        <div id="screen-menu" class="screen active">
            <div class="col-left" style="justify-content: center;">
                <h1 style="font-size: 11px; color: #ffff55; line-height: 1.4;">MLBB RPG:<br>ОДИССЕЯ МОНИИ</h1>
                <p class="subtitle">Версия 7.0 (Эволюция Классов)</p>
            </div>
            <div class="col-right" style="justify-content: center;">
                <div style="font-size: 34px; margin: 15px 0; animation: floatEff 2s infinite ease-in-out;">🛡️🏹🗡️👹</div>
                <button class="menu-btn" onclick="startAdventure()">НАЧАТЬ ПУТЕШЕСТВИЕ</button>
                <button class="menu-btn" onclick="switchScreen('screen-settings')">ВЫБОР ГЕРОЯ И НАСТРОЙКИ</button>
            </div>
        </div>

        <!-- ЭКРАН 2: НАСТРОЙКИ И ПЕРСОНАЖИ -->
        <div id="screen-settings" class="screen">
            <div class="col-left">
                <h1>ВЫБОР ЧЕМПИОНА</h1>
                <div class="panel" style="text-align: left; margin: 0;">
                    <div class="setting-row"><span>ГЕРОЙ:</span> <button id="cfg-hero" class="btn-small" style="color:#ffaa00; font-size:7px;" onclick="toggleSetting('hero')">АЛУКАРД</button></div>
                    <div class="setting-row"><span>ЭКРАН:</span> <button id="cfg-screen" class="btn-small" onclick="toggleSetting('screen')">ОКНО</button></div>
                    <div class="setting-row"><span>ЗВУК:</span> <button id="cfg-sound" class="btn-small" onclick="toggleSetting('sound')">ВКЛ</button></div>
                    <div class="setting-row"><span>МУЗЫКА:</span> <button id="cfg-music" class="btn-small" onclick="toggleSetting('music')">ВКЛ</button></div>
                </div>
            </div>
            <div class="col-right">
                <div class="panel" id="hero-desc-panel" style="font-size:5.5px; text-align:left; color:#aaa; line-height:1.4; margin-top: 5px; min-height: 110px;">
                    <!-- Динамическое описание -->
                </div>
                <button class="menu-btn" onclick="switchScreen('screen-menu')">СОХРАНИТЬ И ВЕРНУТЬСЯ</button>
            </div>
        </div>

        <!-- ЭКРАН 3: КАРТА ИССЛЕДОВАНИЯ -->
        <div id="screen-adventure" class="screen">
            <div class="col-left">
                <div>
                    <h1 id="adv-location-title">ЛОКАЦИЯ 1</h1>
                    <div style="display:flex; justify-content:space-between; font-size:6px; padding: 2px 3px; background: #000; border: 1px solid #222;">
                        <span>❤️ ОЗ: <span id="adv-hp" style="color:#ff5555;">100/100</span></span>
                        <span>💰 ЗОЛОТО: <span id="adv-gold" style="color:#ffff55;">0</span></span>
                        <span>⭐ УР: <span id="adv-lvl">1</span></span>
                    </div>
                </div>
                <div id="map-grid"></div>
            </div>

            <div class="col-right">
                <div style="font-size:5px; color:#8a8ab0; margin: 2px 0;">
                    Легенда: 👾-Крип | 🎁-Сундук | ⛲-Фонтан | 🎯-Портал
                </div>
                <div>
                    <div class="dpad-container">
                        <div></div>
                        <button class="dpad-btn" onclick="movePlayer(0, -1)">▲</button>
                        <div></div>
                        <button class="dpad-btn" onclick="movePlayer(-1, 0)">◄</button>
                        <button class="dpad-btn" style="background:#444466; font-size:11px; color:#ffff55;" onclick="openCampHub()">🎒</button>
                        <button class="dpad-btn" onclick="movePlayer(1, 0)">►</button>
                        <div></div>
                        <button class="dpad-btn" onclick="movePlayer(0, 1)">▼</button>
                        <div></div>
                    </div>
                </div>
                <button class="menu-btn" style="background:#222; margin-top:2px; padding:6px;" onclick="switchScreen('screen-menu')">ПОКИНУТЬ МИР</button>
            </div>
        </div>

        <!-- ЭКРАН 4: ЛАГЕРЬ -->
        <div id="screen-camp" class="screen">
            <div class="col-left">
                <h1 style="color:#55ff55;">СНАРЯЖЕНИЕ И ЛАГЕРЬ</h1>
                <div class="panel" style="text-align: left; font-size: 6px; line-height: 1.4; margin: 0;">
                    <div>КЛАСС: <span id="camp-hero" style="color:#6da5ff;">АЛУКАРД</span> (<span id="camp-lvl">1</span> Ур.)</div>
                    <div>УРОН: <span id="camp-dmg" style="color:#ff5555;">16</span> | ЗОЛОТО: <span id="camp-gold" style="color:#ffff55;">0</span></div>
                    <div class="bar-container" style="height:6px; margin-top:4px;"><div id="camp-exp-fill" class="exp-fill"></div></div>
                </div>
                <div class="panel" style="margin-top: 4px;">
                    <div style="display:flex; justify-content: space-between;">
                        <div class="inv-slot" id="slot-weapon" style="width:48%; font-size:7px;" onclick="unequipItem('weapon')">⚔️ Оружие</div>
                        <div class="inv-slot" id="slot-armor" style="width:48%; font-size:7px;" onclick="unequipItem('armor')">🛡️ Доспех</div>
                    </div>
                </div>
            </div>

            <div class="col-right">
                <div class="panel" style="margin: 0;">
                    <div style="font-size: 5px; text-align: left; margin-bottom: 2px; color:#aaa;">РЮКЗАК:</div>
                    <div class="inv-grid" id="inventory-container"></div>
                </div>
                <div class="grid-2" style="margin-top:4px;">
                    <button class="card-btn attack" style="min-height:30px;" onclick="craftItem()">🔨 КУЗНИЦА (30💰)</button>
                    <button class="card-btn defend" style="min-height:30px;" onclick="buyHealPotion()">🧪 ЗЕЛЬЕ (15💰)</button>
                </div>
                <button class="menu-btn" style="background:#333; padding:6px; margin-top:4px;" onclick="switchScreen('screen-adventure')">НАЗАД К КАРТЕ</button>
            </div>
        </div>

        <!-- ЭКРАН 5: БОЕВАЯ СИСТЕМА -->
        <div id="screen-battle" class="screen">
            <div class="col-left">
                <h1 style="color:#ff4444; font-size:8px;">БИТВА С КРИПОМ!</h1>
                <div class="panel" id="battle-field" style="margin: 0; flex-grow: 1; display: flex; flex-direction: column; justify-content: space-between;">
                    <div style="display:flex; justify-content:space-between; font-size:6px; font-weight:bold;">
                        <span id="bt-player-name" style="color:#6da5ff;">ГЕРОЙ</span>
                        <span id="bt-enemy-name" style="color:#ff6d6d;">КРИП</span>
                    </div>
                    <div class="stage-container">
                        <div id="hero-sprite" class="sprite float-anim">⚔️</div>
                        <div id="enemy-sprite" class="sprite float-anim">👾</div>
                    </div>
                    <div>
                        <div style="font-size:5px; margin-bottom:1px; text-align:left;">ОЗ ВРАГА: <span id="enemy-hp-text">50/50</span></div>
                        <div class="bar-container" style="height:7px;"><div id="enemy-hp-fill" class="hp-fill"></div></div>
                    </div>
                </div>
            </div>

            <div class="col-right">
                <div class="panel" style="padding:2px; margin-bottom:4px;"><div id="log">Приготовьтесь...</div></div>

                <div class="panel" id="player-panel" style="margin: 0; padding: 4px;">
                    <div style="display:flex; justify-content:space-between; font-size:6px; font-weight:bold; margin-bottom:2px;">
                        <span>ТВОЕ ОЗ: <span id="player-hp-text" style="color:#55ff55;">100/100</span></span>
                        <span>ЭНЕРГИЯ: <span id="player-mana-text" style="color:#55aaff;">⚡ 3/3</span></span>
                    </div>
                    <div class="bar-container" style="height:8px;">
                        <div id="player-hp-fill" class="hp-fill" style="background-color:#22cc22;"></div>
                        <div id="player-shield-fill" class="shield-fill" style="position:absolute; top:0; left:0;"></div>
                    </div>
                    <div class="cards" style="margin-top:6px;">
                        <button class="card-btn attack" id="btn-atk1" onclick="useCombatSkill('atk1')">Атака</button>
                        <button class="card-btn attack" id="btn-atk2" onclick="useCombatSkill('atk2')">Навык</button>
                        <button class="card-btn defend" id="btn-def" onclick="useCombatSkill('def')">Блок</button>
                        <button class="card-btn ultimate" id="btn-ult" onclick="useCombatSkill('ult')">УЛЬТ</button>
                    </div>
                </div>
            </div>
        </div>

    </div>

    <script>
        const heroList = ['алукард', 'мия', 'тигрил', 'госсен'];
        const heroData = {
            'алукард': { name: "АЛУКАРД", maxHp: 120, dmg: 16, sprite: "⚔️", desc: "* АЛУКАРД: Боец. Вампиризм (Восстанавливает здоровье при базовой атаке и Ультимейте)." },
            'мия': { name: "МИЯ", maxHp: 95, dmg: 21, sprite: "🏹", desc: "* МИЯ: Стрелок. Критический урон (Шанс 25% нанести двойной урон базовой атакой)." },
            'тигрил': { name: "ТИГРИЛ", maxHp: 160, dmg: 13, sprite: "🛡️", desc: "* ТИГРИЛ: Танк. Крепость (Начинает бой с 30 единицами брони, а навык щита усилен на +50%)." },
            'госсен': { name: "ГОССЕН", maxHp: 100, dmg: 20, sprite: "🗡️", desc: "* ГОССЕН: Убийца. Комбо (Базовая атака дает +2 энергии. Ультимейт наносит +40% урона, если у врага <50% ОЗ)." }
        };

        let config = { sound: true, music: true, hero: 'алукард', fullscreen: false };
        let player = { lvl: 1, exp: 0, nextExp: 80, gold: 40, baseDmg: 16, hp: 100, maxHp: 100, mana: 3, maxMana: 4, shield: 0, weapon: null, armor: null };
        let inventory = [{ type: 'potion', name: 'Зелье ОЗ', icon: '🧪' }];
        let currentZone = 0; let playerX = 1; let playerY = 1;
        let combatActive = false; let currentCreep = null;
        let gameState = { isGameOver: false, currentTurn: 'player' };

        const lootTable = [
            { type: 'weapon', name: 'Меч Легиона', icon: '🗡️', stat: 8, rare: 'common' },
            { type: 'weapon', name: 'Копьё Дракона', icon: '🔱', stat: 18, rare: 'epic' },
            { type: 'weapon', name: 'Клинок Отчаяния', icon: '⚔️', stat: 38, rare: 'legend' },
            { type: 'armor', name: 'Латный доспех', icon: '👕', stat: 6, rare: 'common' },
            { type: 'armor', name: 'Кираса Монии', icon: '🛡️', stat: 16, rare: 'epic' },
            { type: 'armor', name: 'Щит Спасителя', icon: '💎', stat: 35, rare: 'legend' }
        ];

        const zones = [
            {
                title: "🌲 Сады Империи Мония", tileClass: "tile-floor", wallClass: "tile-wall", wallIcon: "🌲",
                map: [
                    [1,1,1,1,1,1,1,1,1], [1,0,0,4,1,0,0,2,1], [1,0,1,0,1,0,1,0,1], [1,2,1,0,5,0,1,0,1],
                    [1,0,1,1,1,0,1,2,1], [1,0,0,2,1,0,1,0,1], [1,1,0,0,1,0,4,0,1], [1,2,0,4,0,0,1,3,1], [1,1,1,1,1,1,1,1,1]
                ],
                creeps: [{ name: "Слайм Бездны", hp: 45, maxHp: 45, sprite: "🟢", minDmg: 4, maxDmg: 8, exp: 40, gold: 15 }]
            },
            {
                title: "🍁 Шепчущий Древний Лес", tileClass: "tile-floor", wallClass: "tile-wall", wallIcon: "🌿",
                map: [
                    [1,1,1,1,1,1,1,1,1], [1,0,2,0,4,0,1,2,1], [1,1,1,1,0,1,1,0,1], [1,0,5,2,0,0,1,0,1],
                    [1,0,1,1,1,1,1,4,1], [1,2,1,0,0,5,0,0,1], [1,0,1,0,1,1,1,2,1], [1,4,0,0,2,0,1,3,1], [1,1,1,1,1,1,1,1,1]
                ],
                creeps: [{ name: "Лесной Волк", hp: 75, maxHp: 75, sprite: "🐺", minDmg: 9, maxDmg: 15, exp: 65, gold: 30 }]
            },
            {
                title: "⛰️ Заброшенные Шахты Эрдитии", tileClass: "tile-mine", wallClass: "tile-wall", wallIcon: "🧱",
                map: [
                    [1,1,1,1,1,1,1,1,1], [1,0,4,0,1,0,5,2,1], [1,0,1,0,0,0,1,0,1], [1,2,1,1,1,1,1,4,1],
                    [1,0,0,2,1,0,0,0,1], [1,1,1,0,1,0,1,1,1], [1,2,5,0,1,2,1,2,1], [1,4,1,0,4,0,0,3,1], [1,1,1,1,1,1,1,1,1]
                ],
                creeps: [{ name: "Каменный Голем", hp: 130, maxHp: 130, sprite: "🗿", minDmg: 14, maxDmg: 24, exp: 120, gold: 45 }]
            },
            {
                title: "🏜️ Пустоши Заката", tileClass: "tile-waste", wallClass: "tile-wall", wallIcon: "⛰️",
                map: [
                    [1,1,1,1,1,1,1,1,1], [1,0,2,1,0,2,1,4,1], [1,5,0,1,0,0,1,0,1], [1,1,0,4,5,0,0,2,1],
                    [1,2,0,1,1,1,1,0,1], [1,0,1,1,0,4,1,0,1], [1,4,2,1,2,0,0,2,1], [1,1,0,0,0,1,1,3,1], [1,1,1,1,1,1,1,1,1]
                ],
                creeps: [{ name: "Орк-Налетчик", hp: 180, maxHp: 180, sprite: "👹", minDmg: 20, maxDmg: 32, exp: 190, gold: 65 }]
            },
            {
                title: "🌋 Цитадель Бездны", tileClass: "tile-abyss", wallClass: "tile-wall", wallIcon: "🔥",
                map: [
                    [1,1,1,1,1,1,1,1,1], [1,4,0,0,1,0,0,2,1], [1,0,1,0,1,0,1,0,1], [1,2,1,0,5,0,1,4,1],
                    [1,0,1,1,1,1,1,2,1], [1,0,4,2,1,0,5,0,1], [1,1,1,0,1,0,1,1,1], [1,2,0,0,4,2,1,3,1], [1,1,1,1,1,1,1,1,1]
                ],
                creeps: [{ name: "ТАМУЗ (ЛОРД ПЕКЛА)", hp: 480, maxHp: 480, sprite: "🔥", minDmg: 35, maxDmg: 55, exp: 999, gold: 500, isBoss: true }]
            }
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
                let notes = [293.66, 349.23, 440.00, 392.00];
                let note = notes[musicTicks % notes.length];
                makeTone(note, 'sine', 0.15, 0.006); musicTicks++;
            }, 400);
        }

        const audioPack = {
            click: () => makeTone(580, 'sine', 0.05, 0.02),
            step: () => makeTone(140, 'triangle', 0.05, 0.02),
            loot: () => { makeTone(440, 'sine', 0.08, 0.02); setTimeout(() => makeTone(660, 'sine', 0.12, 0.02), 60); },
            heal: () => { makeTone(300, 'sine', 0.1, 0.02); setTimeout(() => makeTone(600, 'sine', 0.15, 0.02), 60); },
            hit: () => { makeTone(200, 'sawtooth', 0.08, 0.02); },
            block: () => makeTone(350, 'sine', 0.1, 0.03),
            lvlUp: () => { [440, 554, 659].forEach((f, i) => setTimeout(() => makeTone(f, 'sine', 0.15, 0.02), i*70)); }
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
            document.getElementById('hero-desc-panel').innerHTML = `${h.desc}<br><br><span style='color:#ff5555'>Базовое ОЗ: ${h.maxHp}</span><br><span style='color:#ffaa00'>Базовый Урон: ${h.dmg}</span>`;
        }

        function toggleSetting(key) {
            initAudio(); audioPack.click();
            if (key === 'sound' || key === 'music') { config[key] = !config[key]; document.getElementById(`cfg-${key}`).innerText = config[key] ? "ВКЛ" : "ВЫКЛ"; }
            else if (key === 'screen') {
                config.fullscreen = !config.fullscreen; let c = document.getElementById('game-container');
                if (config.fullscreen) { c.classList.add('fullscreen'); document.getElementById('cfg-screen').innerText = "ВЕСЬ ЭКРАН"; if (document.documentElement.requestFullscreen) document.documentElement.requestFullscreen(); }
                else { c.classList.remove('fullscreen'); document.getElementById('cfg-screen').innerText = "ОКНО"; if (document.exitFullscreen && document.fullscreenElement) document.exitFullscreen(); }
            } else if (key === 'hero') {
                let idx = heroList.indexOf(config.hero);
                config.hero = heroList[(idx + 1) % heroList.length];
                updateSettingsUI();
            }
        }

        function startAdventure() {
            let data = heroData[config.hero];
            player.maxHp = data.maxHp; player.baseDmg = data.dmg;
            player.gold = 40; player.lvl = 1; player.exp = 0; player.hp = player.maxHp; player.weapon = null; player.armor = null;
            inventory = [{ type: 'potion', name: 'Зелье ОЗ', icon: '🧪' }]; loadZone(0);
        }

        function loadZone(idx) {
            currentZone = idx; if (currentZone >= zones.length) { alert("🏆 ПОБЕДА! Мония полностью спасена!"); switchScreen('screen-menu'); return; }
            playerX = 1; playerY = 1; renderMap(); switchScreen('screen-adventure');
        }

        function renderMap() {
            let z = zones[currentZone];
            document.getElementById('adv-location-title').innerText = `${currentZone+1}/5: ${z.title}`;
            document.getElementById('adv-hp').innerText = `${player.hp}/${player.maxHp}`;
            document.getElementById('adv-gold').innerText = player.gold; document.getElementById('adv-lvl').innerText = player.lvl;
            
            let grid = document.getElementById('map-grid'); grid.innerHTML = "";
            for (let y = 0; y < 9; y++) {
                for (let x = 0; x < 9; x++) {
                    let cell = document.createElement('div'); let code = z.map[y][x];
                    cell.className = "map-tile " + z.tileClass;
                    if (code === 1) { cell.className = "map-tile " + z.wallClass; cell.innerText = z.wallIcon; }
                    else if (code === 2) cell.innerText = "👾"; else if (code === 3) cell.innerText = "🎯";
                    else if (code === 4) cell.innerText = "🎁"; else if (code === 5) cell.innerText = "⛲";
                    if (x === playerX && y === playerY) cell.innerText = heroData[config.hero].sprite;
                    grid.appendChild(cell);
                }
            }
        }

        function movePlayer(dx, dy) {
            if (combatActive) return; initAudio();
            let tx = playerX + dx, ty = playerY + dy; let z = zones[currentZone];
            if (tx >= 0 && tx < 9 && ty >= 0 && ty < 9 && z.map[ty][tx] !== 1) {
                playerX = tx; playerY = ty; audioPack.step();
                let trg = z.map[playerY][playerX];
                if (trg === 2) { triggerBattle(); return; }
                if (trg === 3) { alert("✨ Телепортация вглубь Монии..."); loadZone(currentZone + 1); return; }
                if (trg === 4) { let g = Math.floor(Math.random()*15)+15; player.gold += g; audioPack.loot(); alert(`🎁 Золото: +${g}💰`); z.map[playerY][playerX] = 0; }
                if (trg === 5) { player.hp = player.maxHp; audioPack.heal(); alert("⛲ Светлый Фонтан полностью исцелил раны!"); z.map[playerY][playerX] = 0; }
                renderMap();
            }
        }

        window.addEventListener('keydown', (e) => {
            if (!document.getElementById('screen-adventure').classList.contains('active')) return;
            if (e.key === 'w' || e.key === 'ArrowUp') movePlayer(0, -1); if (e.key === 's' || e.key === 'ArrowDown') movePlayer(0, 1);
            if (e.key === 'a' || e.key === 'ArrowLeft') movePlayer(-1, 0); if (e.key === 'd' || e.key === 'ArrowRight') movePlayer(1, 0);
        });

        function openCampHub() {
            switchScreen('screen-camp'); document.getElementById('camp-hero').innerText = config.hero.toUpperCase();
            document.getElementById('camp-lvl').innerText = player.lvl; document.getElementById('camp-gold').innerText = player.gold;
            document.getElementById('camp-exp-fill').style.width = `${(player.exp / player.nextExp)*100}%`;
            let wStat = player.weapon ? player.weapon.stat : 0; document.getElementById('camp-dmg').innerText = player.baseDmg + wStat;
            document.getElementById('slot-weapon').innerText = player.weapon ? `${player.weapon.icon} +${player.weapon.stat}` : '⚔️ Руки';
            document.getElementById('slot-armor').innerText = player.armor ? `${player.armor.icon} +${player.armor.stat}` : '🛡️ Одежда';
            let box = document.getElementById('inventory-container'); box.innerHTML = "";
            inventory.forEach((item, i) => {
                let slot = document.createElement('div'); slot.className = `inv-slot ${item.rare || 'common'}`;
                slot.innerText = item.icon; slot.onclick = () => useItem(i); box.appendChild(slot);
            });
        }

        function useItem(idx) {
            let item = inventory[idx]; audioPack.click();
            if (item.type === 'potion') { player.hp = player.maxHp; alert("🧪 ХП восстановлено!"); inventory.splice(idx, 1); }
            else { if (player[item.type]) inventory.push(player[item.type]); player[item.type] = item; inventory.splice(idx, 1); alert(`Экипировано: ${item.name}`); }
            openCampHub();
        }
        function unequipItem(slot) { if (player[slot]) { inventory.push(player[slot]); player[slot] = null; openCampHub(); } }
        function buyHealPotion() { if (player.gold >= 15) { player.gold -= 15; inventory.push({ type: 'potion', name: 'Зелье', icon: '🧪' }); openCampHub(); } else alert("Недостаточно золота!"); }
        function craftItem() { if (player.gold >= 30) { player.gold -= 30; let r = { ...lootTable[Math.floor(Math.random() * lootTable.length)] }; inventory.push(r); alert(`🔨 Выковано: ${r.name}`); openCampHub(); } else alert("Нужно 30💰"); }

        function setupSkillButtons() {
            let b1 = document.getElementById('btn-atk1'); let b2 = document.getElementById('btn-atk2');
            let b3 = document.getElementById('btn-def'); let b4 = document.getElementById('btn-ult');
            if (config.hero === 'алукард') {
                b1.innerHTML = "⚔️ Рубка<br>(+1⚡ Вамп)"; b2.innerHTML = "💥 Прыжок<br>(-1⚡)"; b3.innerHTML = "🛡️ Контрудар<br>(-1⚡)"; b4.innerHTML = "🔮 Расщепл.<br>(-3⚡ Вамп)";
            } else if (config.hero === 'мия') {
                b1.innerHTML = "🏹 Выстрел<br>(+1⚡ Крит)"; b2.innerHTML = "💥 Обстрел<br>(-1⚡)"; b3.innerHTML = "💨 Шаг ветра<br>(-1⚡)"; b4.innerHTML = "🔮 Натиск<br>(-3⚡)";
            } else if (config.hero === 'тигрил') {
                b1.innerHTML = "🔨 Молот<br>(+1⚡)"; b2.innerHTML = "💥 Авангард<br>(-1⚡)"; b3.innerHTML = "🛡️ Стена<br>(-1⚡ Усил)"; b4.innerHTML = "🔮 Имплозия<br>(-3⚡)";
            } else if (config.hero === 'госсен') {
                b1.innerHTML = "🗡️ Кинжал<br>(+2⚡ Быстро)"; b2.innerHTML = "💥 Бросок<br>(-1⚡)"; b3.innerHTML = "🌀 Смещение<br>(-1⚡)"; b4.innerHTML = "🔮 Казнь<br>(-3⚡ Урон+)";
            }
        }

        function triggerBattle() {
            combatActive = true; gameState.isGameOver = false; gameState.currentTurn = 'player';
            let pool = zones[currentZone].creeps; currentCreep = { ...pool[Math.floor(Math.random() * pool.length)] };
            document.getElementById('bt-player-name').innerText = heroData[config.hero].name;
            document.getElementById('bt-enemy-name').innerText = currentCreep.name;
            document.getElementById('enemy-sprite').innerText = currentCreep.sprite;
            document.getElementById('hero-sprite').innerText = heroData[config.hero].sprite;
            player.mana = 3; 
            player.shield = (config.hero === 'тигрил') ? 30 : 0; 
            document.getElementById('log').innerHTML = "Да начнется бой в Монии!";
            setupSkillButtons(); updateBattleUI(); switchScreen('screen-battle');
        }

        function updateBattleUI() {
            document.getElementById('player-hp-text').innerText = `${player.hp}/${player.maxHp}`;
            document.getElementById('player-hp-fill').style.width = `${(player.hp / player.maxHp)*100}%`;
            document.getElementById('player-shield-fill').style.width = `${(player.shield / player.maxHp)*100}%`;
            document.getElementById('player-mana-text').innerText = `⚡ ${player.mana}/${player.maxMana}`;
            document.getElementById('enemy-hp-text').innerText = `${currentCreep.hp}/${currentCreep.maxHp}`;
            document.getElementById('enemy-hp-fill').style.width = `${(currentCreep.hp / currentCreep.maxHp)*100}%`;
            let myTurn = (gameState.currentTurn === 'player' && !gameState.isGameOver);
            document.getElementById('btn-atk1').disabled = !myTurn; document.getElementById('btn-atk2').disabled = !myTurn || player.mana < 1;
            document.getElementById('btn-def').disabled = !myTurn || player.mana < 1; document.getElementById('btn-ult').disabled = !myTurn || player.mana < 3;
        }

        function addLog(t, c='#fff') { let l = document.getElementById('log'); l.innerHTML += `<br><span style="color:${c}">${t}</span>`; l.scrollTop = l.scrollHeight; }
        function triggerDamageText(v, side) {
            let d = document.createElement('div'); d.className = 'damage-pop'; d.innerText = v; d.style.left = side ? '70%' : '20%'; d.style.bottom = '35px';
            if (v.includes('+') || v.includes('Блок')) d.style.color = '#55ff55'; if (v.includes('💥')) d.style.color = '#ffff55';
            document.getElementById('battle-field').appendChild(d); setTimeout(() => d.remove(), 600);
        }

        function useCombatSkill(sk) {
            if (gameState.isGameOver || gameState.currentTurn !== 'player') return;
            let spr = document.getElementById('hero-sprite'); let dmg = player.baseDmg + (player.weapon ? player.weapon.stat : 0);
            spr.classList.add('strike-left'); setTimeout(() => spr.classList.remove('strike-left'), 300);

            if (sk === 'atk1') {
                let f = Math.floor(dmg*0.8) + Math.floor(Math.random()*4); let cr = false;
                if (config.hero === 'мия' && Math.random() < 0.25) { f *= 2; cr = true; }
                currentCreep.hp = Math.max(0, currentCreep.hp - f); 
                player.mana = Math.min(player.maxMana, player.mana + (config.hero === 'госсен' ? 2 : 1)); audioPack.hit();
                if (config.hero === 'алукард') { let v = Math.floor(f*0.25); player.hp = Math.min(player.maxHp, player.hp + v); triggerDamageText(`+${v}`, false); }
                triggerDamageText(cr ? `💥${f}!` : `-${f}`, true); addLog(`Атака нанесла: ${f} ед.`);
            } else if (sk === 'atk2') {
                player.mana -= 1; let f = Math.floor(dmg*1.4) + Math.floor(Math.random()*6); currentCreep.hp = Math.max(0, currentCreep.hp - f);
                audioPack.hit(); triggerDamageText(`-${f}`, true); addLog(`Навык нанес: ${f} урона!`, '#ff9999');
            } else if (sk === 'def') {
                player.mana -= 1; 
                let multi = (config.hero === 'тигрил') ? 1.5 : 1.0;
                let s = Math.floor((16 + (player.armor ? player.armor.stat : 0)) * multi); player.shield += s;
                audioPack.block(); triggerDamageText(`+🛡️${s}`, false); addLog(`Броня укреплена: +${s}`, '#55aaff');
            } else if (sk === 'ult') {
                player.mana -= 3; let f = Math.floor(dmg*2.4) + Math.floor(Math.random()*10); 
                if (config.hero === 'госсен' && currentCreep.hp < (currentCreep.maxHp / 2)) { f = Math.floor(f * 1.4); }
                currentCreep.hp = Math.max(0, currentCreep.hp - f); 
                audioPack.hit();
                if (config.hero === 'алукард') { let l = Math.floor(f*0.3); player.hp = Math.min(player.maxHp, player.hp + l); triggerDamageText(`+${l}`, false); }
                document.getElementById('battle-field').classList.add('flash-red'); setTimeout(() => document.getElementById('battle-field').classList.remove('flash-red'), 200);
                triggerDamageText(`💥${f}`, true); addLog(`🔮 УЛЬТИМЕЙТ: ${f} сокрушительного урона!`, '#ffff44');
            }

            updateBattleUI(); if (currentCreep.hp <= 0) { endBattle(true); return; }
            gameState.currentTurn = 'enemy'; setTimeout(enemyTurn, 600);
        }

        function enemyTurn() {
            if (gameState.isGameOver) return;
            let spr = document.getElementById('enemy-sprite'); spr.classList.add('strike-right'); setTimeout(() => spr.classList.remove('strike-right'), 300);
            let ed = Math.floor(Math.random()*(currentCreep.maxDmg - currentCreep.minDmg + 1)) + currentCreep.minDmg;
            if (player.shield > 0) { if (player.shield >= ed) { player.shield -= ed; ed = 0; } else { ed -= player.shield; player.shield = 0; } }
            if (ed > 0) { player.hp = Math.max(0, player.hp - ed); triggerDamageText(`-${ed}`, false); audioPack.hit(); addLog(`Враг нанес: ${ed}`, '#ff4444'); }
            else { triggerDamageText("Блок", false); audioPack.block(); }
            updateBattleUI(); if (player.hp <= 0) { endBattle(false); } else { gameState.currentTurn = 'player'; updateBattleUI(); }
        }

        function endBattle(win) {
            gameState.isGameOver = true; combatActive = false;
            if (win) {
                audioPack.lvlUp(); player.gold += currentCreep.gold; player.exp += currentCreep.exp;
                alert(`✌️ Победили крипа! Награда: +${currentCreep.gold}💰 | +${currentCreep.exp} EXP`); zones[currentZone].map[playerY][playerX] = 0;
                if (player.exp >= player.nextExp) { player.lvl++; player.exp -= player.nextExp; player.nextExp = Math.floor(player.nextExp*1.35); player.baseDmg += 4; player.maxHp += 12; player.hp = player.maxHp; alert("✨ НОВЫЙ УРОВЕНЬ ДОСТИГНУТ!"); }
                renderMap(); switchScreen('screen-adventure');
            } else { alert("💀 Герой пал в бою... Одиссея начинается заново."); switchScreen('screen-menu'); }
        }
        
        // Первичная инициализация описания при запуске страницы
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
