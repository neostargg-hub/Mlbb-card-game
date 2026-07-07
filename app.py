from flask import Flask, render_template_string

app = Flask(__name__)

GAME_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>MLBB: Хроники Монии — Полная Версия</title>
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
    <style>
        *, *::before, *::after { box-sizing: border-box; }
        body {
            font-family: 'Press Start 2P', cursive;
            background-color: #05050b;
            color: #e0e0f0;
            margin: 0;
            padding: 8px;
            font-size: 8px;
            text-align: center;
            overflow: hidden;
            user-select: none;
            -webkit-user-select: none;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        /* Основной контейнер игры */
        #game-container {
            width: 100%;
            max-width: 480px;
            height: 100%;
            max-height: 720px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            background: radial-gradient(circle, #121224 0%, #05050b 100%);
            border: 4px solid #3d3d5c;
            box-shadow: 0px 0px 20px rgba(0,0,0,0.8);
            padding: 10px;
            position: relative;
            transition: all 0.3s ease;
        }

        /* Полноэкранный режим */
        #game-container.fullscreen {
            max-width: 100vw;
            max-height: 100vh;
            border: none;
            padding: 15px;
        }
        
        h1 { font-size: 11px; color: #d4af37; text-shadow: 2px 2px #000; margin: 5px 0; letter-spacing: 1px; }
        .subtitle { font-size: 7px; color: #8a8ab0; margin-bottom: 8px; text-transform: uppercase; }

        /* Экраны игры */
        .screen { display: none; height: 100%; flex-direction: column; justify-content: center; }
        .screen.active { display: flex; }

        /* Панели */
        .panel {
            background-color: #141423;
            border: 3px solid #3d3d5c;
            box-shadow: 4px 4px 0px #000;
            padding: 8px;
            margin-bottom: 8px;
            position: relative;
        }
        .boss-panel { border-color: #991f1f; background-color: #221212; }
        
        /* Прогресс-бары */
        .bar-container {
            width: 100%; height: 14px; background-color: #222;
            border: 2px solid #fff; margin-top: 4px; position: relative;
        }
        .hp-fill { height: 100%; background-color: #cc2222; width: 100%; transition: width 0.2s ease-out; }
        .mana-fill { height: 100%; background-color: #1f75fe; width: 100%; transition: width 0.2s ease-out; }
        .shield-fill { height: 100%; background-color: #9c9c9c; width: 0%; transition: width 0.2s ease-out; }
        .bar-text { position: absolute; top: 2px; width: 100%; text-align: center; color: white; text-shadow: 1px 1px #000; font-size: 7px; font-weight: bold; }

        #log {
            height: 60px; overflow-y: auto; background: #05050d; color: #4af24a;
            padding: 6px; text-align: left; border: 2px solid #3d3d5c; line-height: 1.4; font-size: 7px;
        }
        
        /* Окно диалогов и Пролога */
        .story-box {
            min-height: 120px; background: #000; border: 3px double #d4af37;
            padding: 12px; text-align: left; margin: 10px 0; position: relative;
        }
        .speaker-name {
            position: absolute; top: -10px; left: 10px; background: #d4af37;
            color: #000; padding: 2px 6px; font-size: 7px; font-weight: bold;
        }
        .story-text { line-height: 1.6; color: #fff; font-size: 8px; }
        
        /* Кнопки и Сетка действий */
        .cards { display: flex; flex-wrap: wrap; gap: 4px; justify-content: center; margin-top: 5px; }
        .card-btn {
            font-family: 'Press Start 2P', cursive; background-color: #2a2a40; color: #fff;
            border: 3px outset #4f4f7a; padding: 8px 4px; font-size: 7px; cursor: pointer;
            width: 48%; text-align: center; min-height: 36px;
        }
        .card-btn:active { border-style: inset; background-color: #151525; }
        .card-btn:disabled { opacity: 0.4; cursor: not-allowed; border: 3px solid #222; }
        
        .attack { color: #ff5555; } .defend { color: #55aaff; } 
        .heal { color: #55ff55; } .ultimate { color: #ffff55; border-color: #ffff55; }
        
        /* Анимации и Спрайты */
        .stage-container { position: relative; height: 95px; margin: 5px 0; overflow: hidden; }
        .sprite { 
            font-size: 42px; position: absolute; bottom: 5px; width: 50px; height: 50px;
            display: flex; align-items: center; justify-content: center;
        }
        #hero-sprite { left: 15%; transform: scaleX(-1); }
        #enemy-sprite { right: 15%; }
        
        .float-anim { animation: floatEffect 2s infinite ease-in-out; }
        .strike-left { animation: strikeLeftEffect 0.4s ease-in-out; }
        .strike-right { animation: strikeRightEffect 0.4s ease-in-out; }
        .flash-red { animation: flashRedEffect 0.3s ease-in-out; }
        .heal-flash { animation: healFlashEffect 0.4s ease-in-out; }
        
        @keyframes floatEffect { 0%, 100% { bottom: 5px; } 50% { bottom: 14px; } }
        @keyframes strikeLeftEffect {
            0% { left: 15%; } 50% { left: 50%; transform: scaleX(-1) scale(1.3); } 100% { left: 15%; }
        }
        @keyframes strikeRightEffect {
            0% { right: 15%; } 50% { right: 50%; transform: scale(1.3); } 100% { right: 15%; }
        }
        @keyframes flashRedEffect {
            0%, 100% { background-color: #141423; } 50% { background-color: #551111; }
        }
        @keyframes healFlashEffect {
            0%, 100% { box-shadow: 4px 4px 0px #000; } 50% { box-shadow: 0px 0px 15px #55ff55; border-color: #55ff55; }
        }

        /* Главное Меню */
        .menu-btn {
            font-family: 'Press Start 2P', cursive; background-color: #2b2b45; color: #d4af37;
            border: 3px outset #444477; padding: 10px; width: 90%; margin: 6px auto; display: block; font-size: 8px; cursor: pointer;
        }
        .menu-btn:active { border-style: inset; }
        .setting-row { display: flex; justify-content: space-between; align-items: center; padding: 8px; border-bottom: 1px solid #2d2d44; }
        .btn-small { padding: 4px 8px; font-family: 'Press Start 2P'; font-size: 6px; background: #3d3d5c; color: #fff; border: 2px outset #555; cursor: pointer; }

        /* Всплывающий урон */
        .damage-pop {
            position: absolute; font-size: 9px; font-weight: bold; color: #ff3333;
            text-shadow: 1px 1px #000; animation: popUp 0.8s forwards ease-out; z-index: 10;
        }
        @keyframes popUp { 0% { opacity: 1; transform: translateY(0) scale(1); } 100% { opacity: 0; transform: translateY(-35px) scale(1.4); } }
    </style>
</head>
<body>

    <div id="game-container">

        <div id="screen-menu" class="screen active">
            <h1 style="font-size: 13px; margin-top: 20px; color: #ffff55; line-height: 1.5;">MLBB RPG:<br>ЛЕГЕНДЫ МОНИИ</h1>
            <p class="subtitle" style="color: #7a7a9a;">Глобальное расширение v2.0</p>
            <div style="font-size: 45px; margin: 20px 0; animation: floatEffect 3s infinite ease-in-out; position:relative; height:60px; bottom:0;">⚔️🔮👑</div>
            <button class="menu-btn" onclick="startNewGame()">НАЧАТЬ ПРИКЛЮЧЕНИЕ</button>
            <button class="menu-btn" onclick="switchScreen('screen-settings')">НАСТРОЙКИ СИСТЕМЫ</button>
            <button class="menu-btn" onclick="switchScreen('screen-credits')">ОБ ИГРЕ</button>
        </div>

        <div id="screen-settings" class="screen">
            <h1>НАСТРОЙКИ</h1>
            <div class="panel" style="text-align: left; margin-top: 10px;">
                <div class="setting-row">
                    <span>ЭКРАН:</span>
                    <button id="cfg-screen" class="btn-small" onclick="toggleSetting('screen')">ОКНО</button>
                </div>
                <div class="setting-row">
                    <span>МУЗЫКА (BACKGROUND):</span>
                    <button id="cfg-music" class="btn-small" onclick="toggleSetting('music')">ВКЛ</button>
                </div>
                <div class="setting-row">
                    <span>ИМИТАЦИЯ ГОЛОСА:</span>
                    <button id="cfg-voice" class="btn-small" onclick="toggleSetting('voice')">ВКЛ</button>
                </div>
                <div class="setting-row">
                    <span>ЗВУКОВЫЕ ЭФФЕКТЫ:</span>
                    <button id="cfg-sound" class="btn-small" onclick="toggleSetting('sound')">ВКЛ</button>
                </div>
                <div class="setting-row">
                    <span>СЛОЖНОСТЬ СЮЖЕТА:</span>
                    <button id="cfg-diff" class="btn-small" onclick="toggleSetting('diff')">НОРМА</button>
                </div>
                <div class="setting-row">
                    <span>ВЫБОР ГЕРОЯ:</span>
                    <button id="cfg-hero" class="btn-small" onclick="toggleSetting('hero')">АЛУКАРД</button>
                </div>
            </div>
            <button class="menu-btn" onclick="switchScreen('screen-menu')">НАЗАД В МЕНЮ</button>
        </div>

        <div id="screen-credits" class="screen">
            <h1>ОБ ИГРЕ</h1>
            <div class="panel" style="line-height: 1.8; text-align: justify; font-size: 7px; max-height: 250px; overflow-y: auto;">
                ПОЛНОЦЕННАЯ ОДНОФАЙЛОВАЯ РЕТРО-RPG.<br><br>
                ВСЕ МЕЛОДИИ, ЭФФЕКТЫ И РЕЧЕВЫЕ СИГНАЛЫ ГЕНЕРИРУЮТСЯ ПРОЦЕДУРНО С ПОМОЩЬЮ WEB AUDIO API БЕЗ СКАЧИВАНИЯ СТАТИЧЕСКИХ ФАЙЛОВ.<br><br>
                РЕЖИМ ПОЛНОГО ЭКРАНА ДОСТУПЕН В НАСТРОЙКАХ. УДАЧИ, РЫЦАРЬ!
            </div>
            <button class="menu-btn" onclick="switchScreen('screen-menu')">НАЗАД В МЕНЮ</button>
        </div>

        <div id="screen-story" class="screen">
            <h1 id="story-chapter-title">ПРОЛОГ</h1>
            <div id="story-scene-container" class="stage-container panel" style="background: #03030a;">
                <div id="story-sprite-center" class="sprite float-anim" style="left: 42%; font-size: 45px;">📜</div>
            </div>
            <div class="story-box">
                <div id="story-speaker" class="speaker-name">Рассказчик</div>
                <div id="story-text" class="story-text">...</div>
            </div>
            <button id="story-next-btn" class="menu-btn" style="width: 100%;" onclick="nextStoryStep()">ДАЛЕЕ >></button>
        </div>

        <div id="screen-battle" class="screen">
            <h1>БИТВА</h1>
            <div class="subtitle" id="battle-stage-title">ГЛАВА 1</div>

            <div id="battle-field" class="panel">
                <div style="display: flex; justify-content: space-between; font-weight: bold; margin-bottom: 2px;">
                    <span id="txt-player-name" style="color: #6da5ff;">АЛУКАРД</span>
                    <span id="txt-enemy-name" style="color: #ff6d6d;">ВРАГ</span>
                </div>
                
                <div class="stage-container">
                    <div id="hero-sprite" class="sprite float-anim">⚔️</div>
                    <div id="enemy-sprite" class="sprite float-anim">👾</div>
                </div>

                <div style="text-align: left; margin-bottom: 4px;">
                    <div style="display:flex; justify-content: space-between; font-size: 6px;">
                        <span>ЗДОРОВЬЕ ВРАГА:</span><span id="enemy-hp-text">100/100</span>
                    </div>
                    <div class="bar-container">
                        <div id="enemy-hp-fill" class="hp-fill"></div>
                    </div>
                </div>
            </div>

            <div class="panel" style="padding: 4px; margin-bottom: 4px;">
                <div id="log">Приготовьтесь к бою!</div>
            </div>

            <div class="panel" id="player-panel">
                <div style="display: flex; justify-content: space-between; font-size: 6px; font-weight: bold;">
                    <span>ТВОЕ ОЗ: <span id="player-hp-text" style="color: #55ff55;">100/100</span></span>
                    <span>ЭНЕРГИЯ: <span id="player-mana-text" style="color: #55aaff;">⚡ 3/3</span></span>
                </div>
                
                <div class="bar-container" style="margin-top: 3px;">
                    <div id="player-hp-fill" class="hp-fill" style="background-color: #22cc22;"></div>
                    <div id="player-shield-fill" class="shield-fill" style="position: absolute; top:0; left:0;"></div>
                </div>
                <div class="bar-container" style="height: 5px; margin-top: 3px;">
                    <div id="player-mana-fill" class="mana-fill"></div>
                </div>
                
                <div class="cards">
                    <button class="card-btn attack" id="btn-atk1" onclick="useSkill('atk1')">⚔️ Удар<br>(0 ⚡)</button>
                    <button class="card-btn attack" id="btn-atk2" onclick="useSkill('atk2')">💥 Навык<br>(1 ⚡)</button>
                    <button class="card-btn defend" id="btn-def" onclick="useSkill('def')">🛡️ Щит<br>(1 ⚡)</button>
                    <button class="card-btn ultimate" id="btn-ult" onclick="useSkill('ult')">🔮 УЛЬТ<br>(3 ⚡)</button>
                </div>
            </div>
            <button class="menu-btn" style="width: 100%; margin-top: 4px; background: #222; color: #aaa;" onclick="forfeitBattle()">СДАСТЬСЯ</button>
        </div>

    </div>

    <script>
        // КОНФИГУРАЦИЯ И ПЕРЕМЕННЫЕ СОСТОЯНИЯ
        let config = { sound: true, voice: true, music: true, diff: 'норма', hero: 'алукард', fullscreen: false };
        let gameState = { currentChapter: 0, storyIndex: 0, currentTurn: 'player', isGameOver: false };
        
        let player = { hp: 100, maxHp: 100, mana: 3, maxMana: 4, shield: 0 };
        let enemy = { name: '', hp: 100, maxHp: 100, sprite: '', minDmg: 5, maxDmg: 15, boss: false };

        // ЗВУКОВОЙ ПРОЦЕДУРНЫЙ ДВИЖОК (Web Audio API)
        let audioCtx = null;
        let musicInterval = null;
        let musicStep = 0;

        function initAudioContext() {
            if (!audioCtx) {
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                startProceduralMusic();
            }
        }

        function playTone(freq, type, duration, volume = 0.03) {
            if (!config.sound || !audioCtx) return;
            if (audioCtx.state === 'suspended') audioCtx.resume();
            let osc = audioCtx.createOscillator();
            let gain = audioCtx.createGain();
            osc.type = type;
            osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
            gain.gain.setValueAtTime(volume, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + duration);
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start();
            osc.stop(audioCtx.currentTime + duration);
        }

        function playVoiceSound(speaker) {
            if (!config.voice || !audioCtx) return;
            let baseFreq = speaker === 'Рассказчик' ? 130 : (speaker === 'Алукард' || speaker === 'Мия' ? 210 : 85);
            let rndFreq = baseFreq + Math.floor(Math.random() * 40);
            let waveType = (speaker === 'Тамуз' || speaker === 'Алиса' || speaker === 'Лорд Бездны') ? 'sawtooth' : 'triangle';
            playTone(rndFreq, waveType, 0.04, 0.02);
        }

        // САУНДТРЕК (Генерируется кодом на лету)
        function startProceduralMusic() {
            if (musicInterval) clearInterval(musicInterval);
            
            // Сюжетный минорный лад
            const notes = [220.00, 261.63, 293.66, 329.63, 392.00, 440.00]; 
            
            musicInterval = setInterval(() => {
                if (!config.music || !audioCtx) return;
                
                let currentNote = notes[musicStep % notes.length];
                
                // Басы на каждом 4-м шаге
                if (musicStep % 4 === 0) {
                    playTone(currentNote / 2, 'sawtooth', 0.5, 0.015);
                }
                // Основная мелодия арпеджио
                if (musicStep % 2 === 0) {
                    playTone(currentNote, 'triangle', 0.3, 0.015);
                }
                
                musicStep++;
            }, 350);
        }

        const soundEffects = {
            click: () => playTone(480, 'sine', 0.08, 0.04),
            hitHero: () => { playTone(170, 'sawtooth', 0.2, 0.04); playTone(90, 'square', 0.15, 0.03); },
            hitEnemy: () => { playTone(420, 'square', 0.12, 0.04); playTone(220, 'triangle', 0.1, 0.03); },
            shield: () => playTone(380, 'sine', 0.3, 0.05),
            ult: () => { playTone(180, 'sawtooth', 0.1, 0.05); playTone(380, 'square', 0.15, 0.05); playTone(680, 'sine', 0.4, 0.04); },
            win: () => { [330, 440, 550, 660].forEach((f, i) => setTimeout(() => playTone(f, 'sine', 0.25, 0.04), i * 130)); },
            lose: () => { [220, 160, 110].forEach((f, i) => setTimeout(() => playTone(f, 'sawtooth', 0.35, 0.05), i * 180)); }
        };

        // ДАННЫЕ О СЮЖЕТЕ (УВЕЛИЧЕННЫЙ ПРОЛОГ И РАССКАЗЫ)
        const storyLines = [
            {
                chapter: "Пролог: Падение Печатей",
                scenes: [
                    { speaker: "Рассказчик", text: "Сказания гласят, что тысячи лет назад великие маги заперли Бездну глубоко под землями Империи Мония.", bgSprite: "🌋" },
                    { speaker: "Рассказчик", text: "Но ничто не вечно. Тьма копила силы, пуская корни сквозь трещины в людских сердцах. Врата Заката начали разрушаться...", bgSprite: "🌌" },
                    { speaker: "Рассказчик", text: "Вспышки багрового пламени озарили южные рубежи. Передовые патрули Монии перестали выходить на связь.", bgSprite: "🔥" },
                    { speaker: "Алукард", text: "Я чувствую запах серы и скверны даже на огромном расстоянии. Мой клинок жаждет правосудия.", bgSprite: "⚔️" },
                    { speaker: "Рассказчик", text: "Навстречу нашему герою из тумана Бездны выползает уродливое существо — Разведчик Демонов!", bgSprite: "👾" }
                ],
                battleEnemy: { name: 'Разведчик Бездны', hp: 55, maxHp: 55, minDmg: 5, maxDmg: 12, sprite: '👾', boss: false }
            },
            {
                chapter: "Глава 2: Замки Алого Тумана",
                scenes: [
                    { speaker: "Рассказчик", text: "Первая тварь повержена, но это лишь капля в океане. Алукард пересекает границу Проклятых Земель, где небо затянуто кровавой дымкой.", bgSprite: "🏰" },
                    { speaker: "Рассказчик", text: "Из глубин полуразрушенного замка доносится гипнотический, леденящий душу женский смех.", bgSprite: "🦇" },
                    { speaker: "Алиса", text: "Ах, какой благородный рыцарь пожаловал в мои владения... Твоя чистая кровь станет прекрасным завершением моего ужина!", bgSprite: "🧛‍♀️" },
                    { speaker: "Алукард", text: "Королева Крови Алиса! Твоим бесчинствам пришел конец. Защищайся!", bgSprite: "⚔️" }
                ],
                battleEnemy: { name: 'Королева Алиса', hp: 120, maxHp: 120, minDmg: 10, maxDmg: 22, sprite: '🧛‍♀️', boss: false }
            },
            {
                chapter: "Глава 3: Лорд Пекла",
                scenes: [
                    { speaker: "Рассказчик", text: "Алиса исчезает в стае летучих мышей. Но радоваться рано — земля под ногами начинает плавиться, превращаясь в реки магмы.", bgSprite: "🔥" },
                    { speaker: "Лорд Бездны", text: "Глупец... Ты победил слуг, но перед тобой стоит истинный владыка огненных недр Земли!", bgSprite: "👹" },
                    { speaker: "Тамуз", text: "Я — Тамуз! Король Лавы сожжет Империю Мония дотла, а твои кости станут пеплом для моих наковален!", bgSprite: "🔥" },
                    { speaker: "Алукард", text: "Свет внутри меня ярче, чем всё твоё адское пламя! Этот бой решит судьбу мира!", bgSprite: "⚔️" }
                ],
                battleEnemy: { name: 'Тамуз (Босс)', hp: 250, maxHp: 250, minDmg: 16, maxDmg: 35, sprite: '👹', boss: true }
            }
        ];

        // УПРАВЛЕНИЕ ИНТЕРФЕЙСОМ И ЭКРАНАМИ
        function switchScreen(screenId) {
            initAudioContext();
            soundEffects.click();
            document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
            document.getElementById(screenId).classList.add('active');
        }

        function toggleSetting(key) {
            initAudioContext();
            soundEffects.click();
            if (key === 'sound' || key === 'voice' || key === 'music') {
                config[key] = !config[key];
                document.getElementById(`cfg-${key}`).innerText = config[key] ? "ВКЛ" : "ВЫКЛ";
            } else if (key === 'diff') {
                config.diff = config.diff === 'норма' ? 'хардкор' : 'норма';
                document.getElementById('cfg-diff').innerText = config.diff.toUpperCase();
            } else if (key === 'screen') {
                config.fullscreen = !config.fullscreen;
                let container = document.getElementById('game-container');
                if (config.fullscreen) {
                    container.classList.add('fullscreen');
                    document.getElementById('cfg-screen').innerText = "ВЕСЬ ЭКРАН";
                    if (document.documentElement.requestFullscreen) document.documentElement.requestFullscreen();
                } else {
                    container.classList.remove('fullscreen');
                    document.getElementById('cfg-screen').innerText = "ОКНО";
                    if (document.exitFullscreen && document.fullscreenElement) document.exitFullscreen();
                }
            } else if (key === 'hero') {
                config.hero = config.hero === 'алукард' ? 'мия' : 'алукард';
                document.getElementById('cfg-hero').innerText = config.hero.toUpperCase();
                document.getElementById('txt-player-name').innerText = config.hero.toUpperCase();
                document.getElementById('hero-sprite').innerText = config.hero === 'алукард' ? '⚔️' : '🏹';
            }
        }

        // ЭФФЕКТ ПЕЧАТНОЙ МАШИНКИ И ИМИТАЦИИ РЕЧИ
        let typingTimeout;
        function typeWriterEffect(element, text, index, speaker, callback) {
            if (index < text.length) {
                element.innerHTML += text.charAt(index);
                if (index % 2 === 0) playVoiceSound(speaker);
                typingTimeout = setTimeout(() => {
                    typeWriterEffect(element, text, index + 1, speaker, callback);
                }, 35);
            } else {
                if (callback) callback();
            }
        }

        // СЮЖЕТНЫЙ ПРЕД-ИГРОВОЙ ПРОЦЕСС
        function startNewGame() {
            initAudioContext();
            gameState.currentChapter = 0;
            gameState.storyIndex = 0;
            player.hp = config.diff === 'хардкор' ? 80 : 100;
            player.mana = 3;
            player.shield = 0;
            launchStoryChapter();
        }

        function launchStoryChapter() {
            if (gameState.currentChapter >= storyLines.length) {
                switchScreen('screen-menu');
                alert("🏆 ПОБЕДА! Сюжетная кампания завершена. Мония спасена от Бездны!");
                return;
            }
            gameState.storyIndex = 0;
            switchScreen('screen-story');
            showStoryScene();
        }

        function showStoryScene() {
            let chData = storyLines[gameState.currentChapter];
            document.getElementById('story-chapter-title').innerText = chData.chapter;
            let scene = chData.scenes[gameState.storyIndex];
            
            document.getElementById('story-speaker').innerText = scene.speaker;
            document.getElementById('story-sprite-center').innerText = scene.bgSprite;
            
            let textEl = document.getElementById('story-text');
            textEl.innerHTML = "";
            clearTimeout(typingTimeout);
            
            document.getElementById('story-next-btn').disabled = true;
            typeWriterEffect(textEl, scene.text, 0, scene.speaker, () => {
                document.getElementById('story-next-btn').disabled = false;
            });
        }

        function nextStoryStep() {
            soundEffects.click();
            let chData = storyLines[gameState.currentChapter];
            gameState.storyIndex++;
            if (gameState.storyIndex < chData.scenes.length) {
                showStoryScene();
            } else {
                initBattle(chData.battleEnemy);
            }
        }

        // БОЕВАЯ СИСТЕМА И АНИМАЦИИ
        function initBattle(enemyData) {
            enemy = { ...enemyData };
            if (config.diff === 'хардкор') { enemy.hp = Math.floor(enemy.hp * 1.35); enemy.maxHp = enemy.hp; }
            
            document.getElementById('battle-stage-title').innerText = storyLines[gameState.currentChapter].chapter;
            document.getElementById('txt-enemy-name').innerText = enemy.name.toUpperCase();
            document.getElementById('enemy-sprite').innerText = enemy.sprite;
            
            let battleField = document.getElementById('battle-field');
            if (enemy.boss) battleField.classList.add('boss-panel');
            else battleField.classList.remove('boss-panel');

            gameState.isGameOver = false;
            gameState.currentTurn = 'player';
            player.mana = 3;
            player.shield = 0;
            
            document.getElementById('log').innerHTML = `Враг ${enemy.name} преграждает путь! Ваш ход.`;
            updateBattleUI();
            switchScreen('screen-battle');
        }

        function updateBattleUI() {
            document.getElementById('player-hp-text').innerText = `${player.hp}/${player.maxHp}`;
            document.getElementById('player-hp-fill').style.width = `${(player.hp / player.maxHp) * 100}%`;
            document.getElementById('player-shield-fill').style.width = `${(player.shield / player.maxHp) * 100}%`;
            
            document.getElementById('player-mana-text').innerText = `⚡ ${player.mana}/${player.maxMana}`;
            document.getElementById('player-mana-fill').style.width = `${(player.mana / player.maxMana) * 100}%`;

            document.getElementById('enemy-hp-text').innerText = `${enemy.hp}/${enemy.maxHp}`;
            document.getElementById('enemy-hp-fill').style.width = `${(enemy.hp / enemy.maxHp) * 100}%`;

            let isMyTurn = (gameState.currentTurn === 'player' && !gameState.isGameOver);
            document.getElementById('btn-atk1').disabled = !isMyTurn;
            document.getElementById('btn-atk2').disabled = !isMyTurn || player.mana < 1;
            document.getElementById('btn-def').disabled = !isMyTurn || player.mana < 1;
            document.getElementById('btn-ult').disabled = !isMyTurn || player.mana < 3;
        }

        function spawnDamagePopup(text, isEnemySide) {
            let pop = document.createElement('div');
            pop.className = 'damage-pop';
            pop.innerText = text;
            pop.style.left = isEnemySide ? '70%' : '20%';
            pop.style.bottom = '40px';
            if (text.includes('+')) pop.style.color = '#55ff55';
            else if (text.includes('🛡️')) pop.style.color = '#55aaff';
            document.getElementById('battle-field').appendChild(pop);
            setTimeout(() => pop.remove(), 750);
        }

        function addBattleLog(text, color = '#fff') {
            let log = document.getElementById('log');
            log.innerHTML += `<br><span style="color:${color}">${text}</span>`;
            log.scrollTop = log.scrollHeight;
        }

        function useSkill(type) {
            if (gameState.currentTurn !== 'player' || gameState.isGameOver) return;
            
            let hSprite = document.getElementById('hero-sprite');
            let bField = document.getElementById('battle-field');
            
            if (type === 'atk1') {
                let dmg = Math.floor(Math.random() * 7) + 8;
                enemy.hp = Math.max(0, enemy.hp - dmg);
                player.mana = Math.min(player.maxMana, player.mana + 1);
                
                soundEffects.hitEnemy();
                hSprite.classList.add('strike-left');
                setTimeout(() => hSprite.classList.remove('strike-left'), 400);
                spawnDamagePopup(`-${dmg}`, true);
                addBattleLog(`Базовая атака нанесла ${dmg} урона. Получена 1 ⚡.`, '#fff');
            } 
            else if (type === 'atk2' && player.mana >= 1) {
                player.mana -= 1;
                let dmg = Math.floor(Math.random() * 14) + 18;
                enemy.hp = Math.max(0, enemy.hp - dmg);
                
                soundEffects.hitEnemy();
                hSprite.classList.add('strike-left');
                setTimeout(() => hSprite.classList.remove('strike-left'), 400);
                spawnDamagePopup(`-${dmg}!`, true);
                addBattleLog(`Навык 1 поразил врага на ${dmg} урона.`, '#ffaaaa');
            } 
            else if (type === 'def' && player.mana >= 1) {
                player.mana -= 1;
                let shieldVal = Math.floor(Math.random() * 10) + 20;
                player.shield += shieldVal;
                
                soundEffects.shield();
                document.getElementById('player-panel').classList.add('heal-flash');
                setTimeout(() => document.getElementById('player-panel').classList.remove('heal-flash'), 400);
                spawnDamagePopup(`+🛡️${shieldVal}`, false);
                addBattleLog(`Активирован барьер прочностью ${shieldVal} единиц.`, '#55aaff');
            } 
            else if (type === 'ult' && player.mana >= 3) {
                player.mana -= 3;
                let dmg = Math.floor(Math.random() * 20) + 35;
                let vamp = Math.floor(dmg * 0.5);
                
                enemy.hp = Math.max(0, enemy.hp - dmg);
                player.hp = Math.min(player.maxHp, player.hp + vamp);
                
                soundEffects.ult();
                hSprite.classList.add('strike-left');
                bField.classList.add('flash-red');
                setTimeout(() => { hSprite.classList.remove('strike-left'); bField.classList.remove('flash-red'); }, 400);
                
                spawnDamagePopup(`-${dmg}!!`, true);
                spawnDamagePopup(`+${vamp}`, false);
                addBattleLog(`💥💥 УЛЬТИМЕЙТ! Нанесено ${dmg} урона. Восстановлено ${vamp} ОЗ!`, '#ffff55');
            }

            updateBattleUI();

            if (enemy.hp <= 0) {
                gameState.isGameOver = true;
                soundEffects.win();
                addBattleLog(`🎉 Победа над ${enemy.name}!`, '#55ff55');
                setTimeout(() => { gameState.currentChapter++; launchStoryChapter(); }, 2200);
                return;
            }

            gameState.currentTurn = 'enemy';
            setTimeout(enemyTurn, 1000);
        }

        function enemyTurn() {
            if (gameState.isGameOver) return;
            
            let eSprite = document.getElementById('enemy-sprite');
            let pPanel = document.getElementById('player-panel');
            
            eSprite.classList.add('strike-right');
            setTimeout(() => eSprite.classList.remove('strike-right'), 400);
            
            let rawDmg = Math.floor(Math.random() * (enemy.maxDmg - enemy.minDmg + 1)) + enemy.minDmg;
            let currentDmg = rawDmg;
            
            if (player.shield > 0) {
                if (player.shield >= currentDmg) {
                    player.shield -= currentDmg;
                    currentDmg = 0;
                    addBattleLog(`🛡️ Энергощит полностью поглотил удар.`, '#55aaff');
                } else {
                    currentDmg -= player.shield;
                    player.shield = 0;
                    addBattleLog(`🛡️ Барьер разрушен! Пропущено ${currentDmg} урона.`, '#ff6d6d');
                }
            } else {
                addBattleLog(`${enemy.name} наносит встречный удар: получено ${currentDmg} урона.`, '#ff5555');
            }

            if (currentDmg > 0) {
                soundEffects.hitHero();
                pPanel.classList.add('flash-red');
                setTimeout(() => pPanel.classList.remove('flash-red'), 300);
                player.hp = Math.max(0, player.hp - currentDmg);
                spawnDamagePopup(`-${currentDmg}`, false);
            } else {
                soundEffects.shield();
                spawnDamagePopup(`Блок!`, false);
            }

            updateBattleUI();

            if (player.hp <= 0) {
                gameState.isGameOver = true;
                soundEffects.lose();
                addBattleLog(`💀 Вы пали в бою. Демоны Бездны празднуют триумф...`, '#ff3333');
                setTimeout(() => { switchScreen('screen-menu'); }, 3000);
                return;
            }

            gameState.currentTurn = 'player';
            updateBattleUI();
        }

        function forfeitBattle() {
            if (confirm("Отступить в главное меню? Текущий прогресс главы будет сброшен.")) {
                switchScreen('screen-menu');
            }
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
