from flask import Flask, render_template_string

app = Flask(__name__)

GAME_HTML = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>MLBB: Легенды Империи Мония</title>
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
    <style>
        *, *::before, *::after { box-sizing: border-box; }
        body {
            font-family: 'Press Start 2P', cursive;
            background-color: #0b0b13;
            color: #e0e0f0;
            margin: 0;
            padding: 8px;
            font-size: 8px;
            text-align: center;
            overflow-x: hidden;
            user-select: none;
            -webkit-user-select: none;
        }
        
        h1 { font-size: 11px; color: #d4af37; text-shadow: 2px 2px #000; margin: 5px 0; letter-spacing: 1px; }
        .subtitle { font-size: 7px; color: #8a8ab0; margin-bottom: 8px; text-transform: uppercase; }

        /* Экраны игры */
        .screen { display: none; }
        .screen.active { display: block; }

        /* Пиксельные панели */
        .panel {
            background-color: #161625;
            border: 3px solid #3d3d5c;
            box-shadow: 4px 4px 0px #000;
            padding: 10px;
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

        /* Текстовые логи и диалоги */
        #log {
            height: 65px; overflow-y: auto; background: #05050d; color: #4af24a;
            padding: 6px; text-align: left; border: 2px solid #3d3d5c; line-height: 1.4; font-size: 7px;
        }
        
        /* Сцена диалогов / Катсцены */
        .story-box {
            min-height: 110px; background: #000; border: 3px double #d4af37;
            padding: 12px; text-align: left; margin: 15px 0; position: relative;
        }
        .speaker-name {
            position: absolute; top: -10px; left: 10px; background: #d4af37;
            color: #000; padding: 2px 6px; font-size: 7px; font-weight: bold;
        }
        .story-text { line-height: 1.6; color: #fff; min-height: 45px; }
        
        /* Сетка карт и действий */
        .cards { display: flex; flex-wrap: wrap; gap: 4px; justify-content: center; margin-top: 5px; }
        .card-btn {
            font-family: 'Press Start 2P', cursive; background-color: #2a2a40; color: #fff;
            border: 3px outset #4f4f7a; padding: 8px 4px; font-size: 7px; cursor: pointer;
            width: 48%; text-align: center; min-height: 38px;
        }
        .card-btn:active { border-style: inset; background-color: #151525; }
        .card-btn:disabled { opacity: 0.4; cursor: not-allowed; border: 3px solid #222; }
        
        .attack { color: #ff5555; } .defend { color: #55aaff; } 
        .heal { color: #55ff55; } .ultimate { color: #ffff55; border-color: #ffff55; }
        
        /* Спрайты и Анимации */
        .stage-container { position: relative; height: 90px; margin: 5px 0; overflow: hidden; }
        .sprite { 
            font-size: 42px; position: absolute; bottom: 5px; width: 50px; height: 50px;
            display: flex; align-items: center; justify-content: center;
        }
        #hero-sprite { left: 20%; transform: scaleX(-1); }
        #enemy-sprite { right: 20%; }
        
        /* Классы анимаций */
        .float-anim { animation: floatEffect 2s infinite ease-in-out; }
        .shake-anim { animation: shakeEffect 0.4s ease-in-out; }
        .strike-left { animation: strikeLeftEffect 0.4s ease-in-out; }
        .strike-right { animation: strikeRightEffect 0.4s ease-in-out; }
        .flash-red { animation: flashRedEffect 0.3s ease-in-out; }
        .heal-flash { animation: healFlashEffect 0.4s ease-in-out; }
        
        @keyframes floatEffect { 0%, 100% { bottom: 5px; } 50% { bottom: 12px; } }
        @keyframes shakeEffect {
            0%, 100% { transform: translateX(0); }
            20%, 60% { transform: translateX(-6px); }
            40%, 80% { transform: translateX(6px); }
        }
        @keyframes strikeLeftEffect {
            0% { left: 20%; } 50% { left: 55%; transform: scaleX(-1) scale(1.3); } 100% { left: 20%; }
        }
        @keyframes strikeRightEffect {
            0% { right: 20%; } 50% { right: 55%; transform: scale(1.3); } 100% { right: 20%; }
        }
        @keyframes flashRedEffect {
            0%, 100% { background-color: #161625; } 50% { background-color: #551111; }
        }
        @keyframes healFlashEffect {
            0%, 100% { box-shadow: 4px 4px 0px #000; } 50% { box-shadow: 0px 0px 15px #55ff55; border-color: #55ff55; }
        }

        /* Главное Меню и Настройки */
        .menu-btn {
            font-family: 'Press Start 2P', cursive; background-color: #2b2b45; color: #d4af37;
            border: 3px outset #444477; padding: 12px; width: 85%; margin: 6px auto; display: block; font-size: 8px;
        }
        .setting-row { display: flex; justify-content: space-between; align-items: center; padding: 8px; border-bottom: 1px solid #333; }
        .btn-small { padding: 4px 8px; font-family: 'Press Start 2P'; font-size: 7px; background: #3d3d5c; color: #fff; border: 2px outset #555; }

        /* Всплывающие цифры урона */
        .damage-pop {
            position: absolute; font-size: 10px; font-weight: bold; color: #ff3333;
            text-shadow: 1px 1px #000; animation: popUp 0.8s forwards ease-out; z-index: 10;
        }
        @keyframes popUp { 0% { opacity: 1; transform: translateY(0) scale(1); } 100% { opacity: 0; transform: translateY(-30px) scale(1.4); } }
    </style>
</head>
<body>

    <!-- ЭКРАН 1: ГЛАВНОЕ МЕНЮ -->
    <div id="screen-menu" class="screen active">
        <h1 style="font-size: 14px; margin-top: 30px; color: #ffff55;">MLBB RPG:<br>ЛЕГЕНДЫ МОНИИ</h1>
        <p class="subtitle" style="color: #888;">Карманное Текстово-Пиксельное Приключение</p>
        <div style="font-size: 45px; margin: 25px 0;">⚔️🛡️🔮</div>
        <button class="menu-btn" onclick="startGame()">НАЧАТЬ ИГРУ</button>
        <button class="menu-btn" onclick="switchScreen('screen-settings')">НАСТРОЙКИ</button>
        <button class="menu-btn" onclick="switchScreen('screen-credits')">ОБ ИГРЕ</button>
    </div>

    <!-- ЭКРАН 2: НАСТРОЙКИ -->
    <div id="screen-settings" class="screen">
        <h1>НАСТРОЙКИ</h1>
        <div class="panel" style="text-align: left; margin-top: 20px;">
            <div class="setting-row">
                <span>8-БИТНЫЙ ЗВУК:</span>
                <button id="cfg-sound" class="btn-small" onclick="toggleSetting('sound')">ВКЛ</button>
            </div>
            <div class="setting-row">
                <span>ИМИТАЦИЯ ГОЛОСА:</span>
                <button id="cfg-voice" class="btn-small" onclick="toggleSetting('voice')">ВКЛ</button>
            </div>
            <div class="setting-row">
                <span>СЛОЖНОСТЬ БИТВЫ:</span>
                <button id="cfg-diff" class="btn-small" onclick="toggleSetting('diff')">НОРМА</button>
            </div>
            <div class="setting-row">
                <span>ВЫБОР ГЕРОЯ:</span>
                <button id="cfg-hero" class="btn-small" onclick="toggleSetting('hero')">АЛУКАРД</button>
            </div>
        </div>
        <button class="menu-btn" onclick="switchScreen('screen-menu')">НАЗАД В МЕНЮ</button>
    </div>

    <!-- ЭКРАН 3: ТИТРЫ -->
    <div id="screen-credits" class="screen">
        <h1>ОБ ИГРЕ</h1>
        <div class="panel" style="line-height: 1.8; text-align: justify; font-size: 7px;">
            ЭТО ПОЛНОФУНКЦИОНАЛЬНАЯ СЮЖЕТНАЯ КАРТОЧНАЯ RPG НА ОСНОВЕ ВСЕЛЕННОЙ MOBILE LEGENDS.<br><br>
            РАЗРАБОТАНО СПЕЦИАЛЬНО ДЛЯ МОБИЛЬНЫХ УСТРОЙСТВ И РАЗВЕРТЫВАНИЯ НА ПЛАТФОРМЕ RENDER. ВСЕ ЭФФЕКТЫ СИНТЕЗИРУЮТСЯ НАЛЕТУ В БРАУЗЕРЕ.<br><br>
            УДАЧИ В БОЮ ЗА ЧЕСТЬ МОНИИ!
        </div>
        <button class="menu-btn" onclick="switchScreen('screen-menu')">НАЗАД В МЕНЮ</button>
    </div>

    <!-- ЭКРАН 4: СЮЖЕТ / КАТСЦЕНЫ -->
    <div id="screen-story" class="screen">
        <h1 id="story-chapter-title">ГЛАВА 1</h1>
        <div id="story-scene-container" class="stage-container panel" style="background: #050510;">
            <div id="story-sprite-center" class="sprite float-anim" style="left: 42%; font-size: 50px;">📜</div>
        </div>
        <div class="story-box">
            <div id="story-speaker" class="speaker-name">Рассказчик</div>
            <div id="story-text" class="story-text">...</div>
        </div>
        <button id="story-next-btn" class="menu-btn" style="width: 100%;" onclick="nextStoryStep()">ДАЛЕЕ >></button>
    </div>

    <!-- ЭКРАН 5: БОЕВОЙ ИНТЕРФЕЙС -->
    <div id="screen-battle" class="screen">
        <h1>БИТВА</h1>
        <div class="subtitle" id="battle-stage-title">ГЛАВА 1: ПРОТИВНИК</div>

        <!-- Поле боя -->
        <div id="battle-field" class="panel">
            <div style="display: flex; justify-content: space-between; font-weight: bold; margin-bottom: 2px;">
                <span id="txt-player-name" style="color: #6da5ff;">АЛУКАРД</span>
                <span id="txt-enemy-name" style="color: #ff6d6d;">ВРАГ</span>
            </div>
            
            <div class="stage-container">
                <div id="hero-sprite" class="sprite float-anim">⚔️</div>
                <div id="enemy-sprite" class="sprite float-anim">👾</div>
            </div>

            <!-- Здоровье Врага -->
            <div style="text-align: left; margin-bottom: 4px;">
                <div style="display:flex; justify-content: space-between; font-size: 7px;">
                    <span>ОЗ ВРАГА:</span><span id="enemy-hp-text">100/100</span>
                </div>
                <div class="bar-container">
                    <div id="enemy-hp-fill" class="hp-fill"></div>
                </div>
            </div>
        </div>

        <!-- Лог сражения -->
        <div class="panel" style="padding: 4px; margin-bottom: 6px;">
            <div id="log">Битва началась! Ваш ход.</div>
        </div>

        <!-- Состояние Игрока и Карты -->
        <div class="panel" id="player-panel">
            <div style="display: flex; justify-content: space-between; font-size: 7px; font-weight: bold;">
                <span>ТВОЕ ЗДОРОВЬЕ: <span id="player-hp-text" style="color: #55ff55;">100/100</span></span>
                <span>ЭНЕРГИЯ: <span id="player-mana-text" style="color: #55aaff;">⚡ 3/3</span></span>
            </div>
            
            <div class="bar-container" style="margin-top: 3px;">
                <div id="player-hp-fill" class="hp-fill" style="background-color: #22cc22;"></div>
                <div id="player-shield-fill" class="shield-fill" style="position: absolute; top:0; left:0;"></div>
            </div>
            <div class="bar-container" style="height: 6px; margin-top: 3px;">
                <div id="player-mana-fill" class="mana-fill"></div>
            </div>
            
            <div class="cards">
                <button class="card-btn attack" id="btn-atk1" onclick="useSkill('atk1')">⚔️ Базовый<br>(0 ⚡)</button>
                <button class="card-btn attack" id="btn-atk2" onclick="useSkill('atk2')">💥 Навык 1<br>(1 ⚡)</button>
                <button class="card-btn defend" id="btn-def" onclick="useSkill('def')">🛡️ Блок<br>(1 ⚡)</button>
                <button class="card-btn ultimate" id="btn-ult" onclick="useSkill('ult')">🔮 УЛЬТИМЕЙТ<br>(3 ⚡)</button>
            </div>
        </div>
        <button class="menu-btn" style="width: 100%; margin-top: 5px; background: #222; color: #aaa;" onclick="forfeitBattle()">СДАСТЬСЯ</button>
    </div>

    <script>
        // ГЛОБАЛЬНЫЕ НАСТРОЙКИ И СОСТОЯНИЕ ИГРЫ
        let config = { sound: true, voice: true, diff: 'норма', hero: 'алукард' };
        let gameState = { currentChapter: 0, storyIndex: 0, currentTurn: 'player', isGameOver: false };
        
        let player = { hp: 100, maxHp: 100, mana: 3, maxMana: 4, shield: 0 };
        let enemy = { name: '', hp: 100, maxHp: 100, sprite: '', minDmg: 5, maxDmg: 15, boss: false };

        // ЗВУКОВОЙ ДВИЖОК Web Audio API (8-битный синтезатор)
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        
        function playTone(freq, type, duration, volume = 0.04) {
            if (!config.sound) return;
            if (audioCtx.state === 'suspended') audioCtx.resume();
            let osc = audioCtx.createOscillator();
            let gain = audioCtx.createGain();
            osc.type = type;
            osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
            gain.gain.setValueAtTime(volume, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + duration);
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start();
            osc.stop(audioCtx.currentTime + duration);
        }

        // Имитация голоса (Речевые пиксельные звуки)
        function playVoiceSound(speaker) {
            if (!config.voice) return;
            let baseFreq = speaker === 'Рассказчик' ? 140 : (speaker === 'Алукард' || speaker === 'Мия' ? 220 : 90);
            let rndFreq = baseFreq + Math.floor(Math.random() * 50);
            let waveType = (speaker === 'Тамуз' || speaker === 'Алиса') ? 'sawtooth' : 'triangle';
            playTone(rndFreq, waveType, 0.05, 0.03);
        }

        const soundEffects = {
            click: () => playTone(500, 'sine', 0.08),
            hitHero: () => { playTone(180, 'sawtooth', 0.2); playTone(100, 'square', 0.15); },
            hitEnemy: () => { playTone(450, 'square', 0.15); playTone(250, 'triangle', 0.1); },
            shield: () => playTone(350, 'sine', 0.35),
            ult: () => { playTone(200, 'sawtooth', 0.1); playTone(400, 'square', 0.2); playTone(700, 'sine', 0.4); },
            win: () => { let t = audioCtx.currentTime; [300, 400, 500, 600].forEach((f, i) => setTimeout(() => playTone(f, 'sine', 0.2), i*150)); },
            lose: () => { let t = audioCtx.currentTime; [250, 180, 120].forEach((f, i) => setTimeout(() => playTone(f, 'sawtooth', 0.3), i*200)); }
        };

        // ДАННЫЕ О СЮЖЕТЕ И СЦЕНАРИИ
        const storyLines = [
            {
                chapter: "Глава 1: Пробуждение Бездны",
                scenes: [
                    { speaker: "Рассказчик", text: "Мрачные тучи сгустились над Империей Мония. Древние печати Южного Светила ослабли, освободив орды демонов.", bgSprite: "🌋" },
                    { speaker: "Алукард", text: "Мой меч чувствует их приближение. Тьма не пройдет, пока я жив!", bgSprite: "⚔️" },
                    { speaker: "Рассказчик", text: "Навстречу герою вырывается Передовой Разведчик Бездны! Битва неизбежна...", bgSprite: "👾" }
                ],
                battleEnemy: { name: 'Разведчик Бездны', hp: 60, maxHp: 60, minDmg: 6, maxDmg: 14, sprite: '👾', boss: false }
            },
            {
                chapter: "Глава 2: Замки Тьмы",
                scenes: [
                    { speaker: "Рассказчик", text: "Первая победа далась нелегко. Алукард продвигается вглубь Проклятых Земель. Из тени замка доносится зловещий смех.", bgSprite: "🏰" },
                    { speaker: "Алиса", text: "Какая глупая и аппетитная добыча сама забрела в мои покои. Королева Крови жаждет свежих сил!", bgSprite: "🧛‍♀️" },
                    { speaker: "Алукард", text: "Твои чары бессильны против веры света, Алиса! Защищайся!", bgSprite: "⚔️" }
                ],
                battleEnemy: { name: 'Королева Алиса', hp: 130, maxHp: 130, minDmg: 12, maxDmg: 24, sprite: '🧛‍♀️', boss: false }
            },
            {
                chapter: "Финал: Король Лавы",
                scenes: [
                    { speaker: "Рассказчик", text: "Алиса бежала, но земля начинает трескаться под ногами. Воздух наполняется чистым пламенем и серой.", bgSprite: "🔥" },
                    { speaker: "Тамуз", text: "Жалкий червь! Ты посмел бросить вызов Бездне? Я сожгу твои кости дотла!", bgSprite: "👹" },
                    { speaker: "Алукард", text: "Это решающий бой за будущее Монии. Во имя света — погибни!", bgSprite: "⚔️" }
                ],
                battleEnemy: { name: 'Тамуз (Босс)', hp: 260, maxHp: 260, minDmg: 18, maxDmg: 38, sprite: '👹', boss: true }
            }
        ];

        // ФУНКЦИИ ИНТЕРФЕЙСА СМЕНЫ ЭКРАНОВ
        function switchScreen(screenId) {
            soundEffects.click();
            document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
            document.getElementById(screenId).classList.add('active');
        }

        function toggleSetting(key) {
            soundEffects.click();
            if (key === 'sound' || key === 'voice') {
                config[key] = !config[key];
                document.getElementById(`cfg-${key}`).innerText = config[key] ? "ВКЛ" : "ВЫКЛ";
            } else if (key === 'diff') {
                config.diff = config.diff === 'норма' ? 'хардکور' : 'норма';
                document.getElementById('cfg-diff').innerText = config.diff.toUpperCase();
            } else if (key === 'hero') {
                config.hero = config.hero === 'алукард' ? 'мия' : 'алукард';
                document.getElementById('cfg-hero').innerText = config.hero.toUpperCase();
                document.getElementById('txt-player-name').innerText = config.hero.toUpperCase();
                document.getElementById('hero-sprite').innerText = config.hero === 'алукард' ? '⚔️' : '🏹';
            }
        }

        // РАБОТА С ТЕКСТОМ И ЭФФЕКТОМ ГОЛОСА И БЕГУЩЕЙ СТРОКИ
        let typingTimeout;
        function typeWriterEffect(element, text, index, speaker, callback) {
            if (index < text.length) {
                element.innerHTML += text.charAt(index);
                if (index % 2 === 0) playVoiceSound(speaker);
                typingTimeout = setTimeout(() => {
                    typeWriterEffect(element, text, index + 1, speaker, callback);
                }, 40);
            } else {
                if (callback) callback();
            }
        }

        // УПРАВЛЕНИЕ СЮЖЕТОМ
        function startGame() {
            gameState.currentChapter = 0;
            gameState.storyIndex = 0;
            player.hp = 100;
            if (config.diff === 'хардکور') player.hp = 80;
            player.mana = 3;
            player.shield = 0;
            launchStoryChapter();
        }

        function launchStoryChapter() {
            if (gameState.currentChapter >= storyLines.length) {
                switchScreen('screen-menu');
                alert("Поздравляем! Вы прошли всю кампанию и спасли Империю Мония!");
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
                // Переходим к битве главы
                initBattle(chData.battleEnemy);
            }
        }

        // БОЕВАЯ СИСТЕМА
        function initBattle(enemyData) {
            enemy = { ...enemyData };
            if (config.diff === 'хардکور') { enemy.hp = Math.floor(enemy.hp * 1.3); enemy.maxHp = enemy.hp; }
            
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
            
            document.getElementById('log').innerHTML = `Поле боя: Враг ${enemy.name} готов к схватке! Ваш ход.`;
            updateBattleUI();
            switchScreen('screen-battle');
        }

        function updateBattleUI() {
            document.getElementById('player-hp-text').innerText = `${player.hp}/${player.maxHp}`;
            document.getElementById('player-hp-fill').style.width = `${(player.hp / player.maxHp) * 100}%`;
            
            // Расчет полоски щита поверх ХП
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

        function createDamagePop(text, isEnemy) {
            let pop = document.createElement('div');
            pop.className = 'damage-pop';
            pop.innerText = text;
            pop.style.left = isEnemy ? '70%' : '25%';
            pop.style.bottom = '40px';
            if (text.includes('+')) pop.style.color = '#55ff55';
            else if (text.includes('🛡️')) pop.style.color = '#55aaff';
            document.getElementById('battle-field').appendChild(pop);
            setTimeout(() => pop.remove(), 800);
        }

        function addBattleLog(text, color = '#fff') {
            let log = document.getElementById('log');
            log.innerHTML += `<br><span style="color:${color}">${text}</span>`;
            log.scrollTop = log.scrollHeight;
        }

        function useSkill(skillType) {
            if (gameState.currentTurn !== 'player' || gameState.isGameOver) return;
            
            let hSprite = document.getElementById('hero-sprite');
            let eField = document.getElementById('battle-field');
            
            if (skillType === 'atk1') {
                // Базовая атака
                let dmg = Math.floor(Math.random() * 8) + 8; // 8-15
                enemy.hp = Math.max(0, enemy.hp - dmg);
                player.mana = Math.min(player.maxMana, player.mana + 1); // Копит 1 ману
                
                soundEffects.hitEnemy();
                hSprite.classList.add('strike-left');
                setTimeout(() => hSprite.classList.remove('strike-left'), 400);
                createDamagePop(`-${dmg}`, true);
                addBattleLog(`Вы провели базовую атаку: урон ${dmg}. Восстановлена 1 ⚡.`, '#fff');
            } 
            else if (skillType === 'atk2' && player.mana >= 1) {
                // Навык 1
                player.mana -= 1;
                let dmg = Math.floor(Math.random() * 15) + 18; // 18-32
                enemy.hp = Math.max(0, enemy.hp - dmg);
                
                soundEffects.hitEnemy();
                hSprite.classList.add('strike-left');
                setTimeout(() => hSprite.classList.remove('strike-left'), 400);
                createDamagePop(`-${dmg}!`, true);
                addBattleLog(`Использован Навык 1: Сокрушительный удар нанес ${dmg} урона.`, '#ffaaaa');
            } 
            else if (skillType === 'def' && player.mana >= 1) {
                // Защитный барьер
                player.mana -= 1;
                let shieldVal = Math.floor(Math.random() * 10) + 20; // 20-30 щита
                player.shield += shieldVal;
                
                soundEffects.shield();
                document.getElementById('player-panel').classList.add('heal-flash');
                setTimeout(() => document.getElementById('player-panel').classList.remove('heal-flash'), 400);
                createDamagePop(`+🛡️${shieldVal}`, false);
                addBattleLog(`Активирован энергетический щит объемом ${shieldVal} единиц.`, '#55aaff');
            } 
            else if (skillType === 'ult' && player.mana >= 3) {
                // Ультимейт
                player.mana -= 3;
                let dmg = Math.floor(Math.random() * 20) + 35; // 35-55 урона
                let vamp = Math.floor(dmg * 0.5); // 50% вампиризм
                
                enemy.hp = Math.max(0, enemy.hp - dmg);
                player.hp = Math.min(player.maxHp, player.hp + vamp);
                
                soundEffects.ult();
                hSprite.classList.add('strike-left');
                eField.classList.add('flash-red');
                setTimeout(() => { hSprite.classList.remove('strike-left'); eField.classList.remove('flash-red'); }, 400);
                
                createDamagePop(`-${dmg}!!`, true);
                createDamagePop(`+${vamp}`, false);
                addBattleLog(`💥 УЛЬТИМЕЙТ ОХОТНИКА! Нанесено ${dmg} урона. Вы восстановили ${vamp} ОЗ.`, '#ffff55');
            }

            updateBattleUI();

            // Проверка победы
            if (enemy.hp <= 0) {
                handleBattleVictory();
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
            
            // Расчет поглощения щитом
            if (player.shield > 0) {
                if (player.shield >= currentDmg) {
                    player.shield -= currentDmg;
                    currentDmg = 0;
                    addBattleLog(`🛡️ Щит полностью заблокировал атаку врага.`, '#55aaff');
                } else {
                    currentDmg -= player.shield;
                    player.shield = 0;
                    addBattleLog(`🛡️ Щит разрушен атакой! Пропущено ${currentDmg} урона.`, '#ff6d6d');
                }
            } else {
                addBattleLog(`${enemy.name} наносит яростный удар! Получено ${currentDmg} урона.`, '#ff5555');
            }

            if (currentDmg > 0) {
                soundEffects.hitHero();
                pPanel.classList.add('flash-red');
                setTimeout(() => pPanel.classList.remove('flash-red'), 300);
                player.hp = Math.max(0, player.hp - currentDmg);
                createDamagePop(`-${currentDmg}`, false);
            } else {
                soundEffects.shield();
                createDamagePop(`Блок!`, false);
            }

            updateBattleUI();

            if (player.hp <= 0) {
                handleBattleDefeat();
                return;
            }

            gameState.currentTurn = 'player';
            updateBattleUI();
        }

        function handleBattleVictory() {
            gameState.isGameOver = true;
            soundEffects.win();
            addBattleLog(`🎉 ПОБЕДА! ${enemy.name} повержен!`, '#55ff55');
            
            setTimeout(() => {
                gameState.currentChapter++;
                launchStoryChapter();
            }, 2500);
        }

        function handleBattleDefeat() {
            gameState.isGameOver = true;
            soundEffects.lose();
            addBattleLog(`💀 ВЫ ПОГИБЛИ. Тьма поглотила Монию...`, '#ff3333');
            setTimeout(() => {
                switchScreen('screen-menu');
            }, 3000);
        }

        function forfeitBattle() {
            if (confirm("Вы уверены, что хотите отступить? Прогресс главы сотрется.")) {
                switchScreen('screen-menu');
            }
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(GAME_HTML)

if __name__ == '__main__':
    app.run(debug=True)
