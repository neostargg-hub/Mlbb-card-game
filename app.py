from flask import Flask, render_template_string

app = Flask(__name__)

GAME_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>MLBB: Закат Бездны</title>
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Press Start 2P', cursive;
            background-color: #121212;
            color: #e0e0e0;
            margin: 0;
            padding: 10px;
            font-size: 9px;
            text-align: center;
        }
        h1 { font-size: 12px; color: #d4af37; text-shadow: 2px 2px #000; margin-bottom: 5px;}
        .subtitle { font-size: 8px; color: #888; margin-bottom: 15px; }
        
        .panel {
            background-color: #222;
            border: 4px solid #444;
            box-shadow: 4px 4px 0px #000;
            padding: 10px;
            margin-bottom: 10px;
        }
        .boss-panel { border-color: #600; }
        
        .bar-container {
            width: 100%; height: 16px; background-color: #333;
            border: 2px solid #fff; margin-top: 5px; position: relative;
        }
        .hp-fill { height: 100%; background-color: #cc0000; width: 100%; transition: width 0.3s; }
        .mana-fill { height: 100%; background-color: #0077ff; width: 100%; transition: width 0.3s; }
        .bar-text { position: absolute; top: 3px; width: 100%; text-align: center; color: white; text-shadow: 1px 1px #000; font-size: 8px;}

        #log {
            height: 70px; overflow-y: auto; background: #000; color: #00ff00;
            padding: 8px; text-align: left; border: 2px solid #555; line-height: 1.6; font-size: 8px;
        }

        .cards { display: flex; flex-wrap: wrap; gap: 5px; justify-content: center; }
        .card-btn {
            font-family: 'Press Start 2P', cursive; background-color: #333; color: #fff;
            border: 3px outset #666; padding: 10px; font-size: 8px; cursor: pointer;
            width: 48%; text-align: center; box-sizing: border-box;
        }
        .card-btn:active { border-style: inset; background-color: #111; }
        .card-btn:disabled { opacity: 0.5; border: 3px solid #333; cursor: not-allowed; }
        
        .attack { color: #ff5555; } .defend { color: #55aaff; } 
        .heal { color: #55ff55; } .rest { color: #ffcc00; }
        
        .sprite { font-size: 45px; margin: 5px 0; animation: float 2s infinite ease-in-out; }
        @keyframes float { 0% {transform: translateY(0);} 50% {transform: translateY(-5px);} 100% {transform: translateY(0);} }
    </style>
</head>
<body>

    <h1>MLBB: Закат Бездны</h1>
    <div class="subtitle" id="stage-title">Глава 1: Вторжение</div>

    <!-- Враг -->
    <div id="enemy-panel" class="panel">
        <div id="enemy-name">Миньон Бездны</div>
        <div id="enemy-sprite" class="sprite">👾</div>
        <div class="bar-container">
            <div id="enemy-hp-fill" class="hp-fill"></div>
            <div id="enemy-hp-text" class="bar-text">50/50</div>
        </div>
    </div>

    <!-- Лог -->
    <div class="panel" style="padding: 5px;">
        <div id="log">Ты — Алукард. Демоны наступают. Выбери действие!</div>
    </div>

    <!-- Игрок -->
    <div class="panel">
        <div style="color: #d4af37;">АЛУКАРД</div>
        <div class="bar-container">
            <div id="player-hp-fill" class="hp-fill" style="background-color: #00aa00;"></div>
            <div id="player-hp-text" class="bar-text">100/100</div>
        </div>
        <div class="bar-container">
            <div id="player-mana-fill" class="mana-fill"></div>
            <div id="player-mana-text" class="bar-text">⚡ 3/3</div>
        </div>
        
        <p style="margin: 10px 0 5px 0;">Действия:</p>
        <div class="cards">
            <button class="card-btn attack" id="btn-attack" onclick="playCard('attack')">⚔️ Удар<br>(1 ⚡)</button>
            <button class="card-btn defend" id="btn-defend" onclick="playCard('defend')">🛡️ Блок<br>(1 ⚡)</button>
            <button class="card-btn heal" id="btn-heal" onclick="playCard('heal')">🩸 Ульт<br>(3 ⚡)</button>
            <button class="card-btn rest" id="btn-rest" onclick="playCard('rest')">🧘 Отдых<br>(+2 ⚡)</button>
        </div>
    </div>

    <script>
        // 8-БИТНЫЕ ЗВУКИ (Синтезатор)
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        function play8BitSound(freqStart, freqEnd, type, duration) {
            if (audioCtx.state === 'suspended') audioCtx.resume();
            let osc = audioCtx.createOscillator();
            let gain = audioCtx.createGain();
            osc.type = type;
            osc.frequency.setValueAtTime(freqStart, audioCtx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(freqEnd, audioCtx.currentTime + duration);
            gain.gain.setValueAtTime(0.05, audioCtx.currentTime); // Громкость
            gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + duration);
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start();
            osc.stop(audioCtx.currentTime + duration);
        }

        const sounds = {
            attack: () => play8BitSound(600, 100, 'square', 0.2), // Взмах мечом
            defend: () => play8BitSound(300, 250, 'triangle', 0.2), // Щит
            heal: () => play8BitSound(300, 900, 'sine', 0.5), // Магия лечения
            rest: () => play8BitSound(400, 600, 'sine', 0.3), // Восстановление
            enemyHit: () => play8BitSound(150, 50, 'sawtooth', 0.3), // Удар врага
            win: () => play8BitSound(400, 1200, 'square', 0.6), // Победа
            lose: () => play8BitSound(200, 50, 'sawtooth', 1.0) // Поражение
        };

        // СЮЖЕТ И ВРАГИ
        const enemies = [
            { name: 'Миньон Бездны', hp: 50, maxHp: 50, minDmg: 5, maxDmg: 12, sprite: '👾', desc: 'Слабый, но опасный.' },
            { name: 'Алиса', hp: 120, maxHp: 120, minDmg: 10, maxDmg: 20, sprite: '🧛‍♀️', desc: 'Королева Крови жаждет битвы!' },
            { name: 'Тамуз, Лорд Лавы', hp: 250, maxHp: 250, minDmg: 15, maxDmg: 35, sprite: '🔥', desc: 'Истинное зло. Уничтожь его!' }
        ];

        let currentStage = 0;
        let player = { hp: 100, maxHp: 100, mana: 3, maxMana: 3 };
        let enemy = { ...enemies[0] };
        let isDefending = false;
        let isPlayerTurn = true;

        function updateUI() {
            document.getElementById('player-hp-text').innerText = player.hp + '/' + player.maxHp;
            document.getElementById('player-hp-fill').style.width = (player.hp / player.maxHp * 100) + '%';
            document.getElementById('player-mana-text').innerText = '⚡ ' + player.mana + '/' + player.maxMana;
            document.getElementById('player-mana-fill').style.width = (player.mana / player.maxMana * 100) + '%';
            
            document.getElementById('enemy-hp-text').innerText = enemy.hp + '/' + enemy.maxHp;
            document.getElementById('enemy-hp-fill').style.width = (enemy.hp / enemy.maxHp * 100) + '%';

            // Блокировка кнопок, если нет маны или не твой ход
            document.getElementById('btn-attack').disabled = !isPlayerTurn || player.mana < 1;
            document.getElementById('btn-defend').disabled = !isPlayerTurn || player.mana < 1;
            document.getElementById('btn-heal').disabled = !isPlayerTurn || player.mana < 3;
            document.getElementById('btn-rest').disabled = !isPlayerTurn;
        }

        function addLog(text, color = '#fff') {
            const logDiv = document.getElementById('log');
            logDiv.innerHTML += `<br><span style="color:${color}">${text}</span>`;
            logDiv.scrollTop = logDiv.scrollHeight;
        }

        function loadStage(stageIndex) {
            if (stageIndex >= enemies.length) {
                sounds.win();
                addLog("🏆 БЕЗДНА ПОВЕРЖЕНА! Империя Мония спасена! Ты прошел игру.", '#ffcc00');
                isPlayerTurn = false;
                return;
            }
            enemy = { ...enemies[stageIndex] };
            document.getElementById('enemy-name').innerText = enemy.name;
            document.getElementById('enemy-sprite').innerText = enemy.sprite;
            document.getElementById('stage-title').innerText = `Глава ${stageIndex + 1}: ${enemy.name}`;
            if (stageIndex === 2) document.getElementById('enemy-panel').classList.add('boss-panel');
            
            addLog(`Появляется ${enemy.name}! ${enemy.desc}`, '#ff5555');
            player.hp = Math.min(player.maxHp, player.hp + 30); // Хил между раундами
            player.mana = player.maxMana;
            updateUI();
        }

        function playCard(type) {
            if (!isPlayerTurn) return;
            isDefending = false;
            isPlayerTurn = false;

            if (type === 'attack' && player.mana >= 1) {
                player.mana -= 1;
                let dmg = Math.floor(Math.random() * 15) + 15; // 15-30
                enemy.hp -= dmg;
                sounds.attack();
                addLog(`Ты ударил мечом на ${dmg} урона.`, '#ffaaaa');
            } else if (type === 'defend' && player.mana >= 1) {
                player.mana -= 1;
                isDefending = true;
                sounds.defend();
                addLog(`Ты встал в блок! Урон будет снижен.`, '#aaffaa');
            } else if (type === 'heal' && player.mana >= 3) {
                player.mana -= 3;
                let heal = 40;
                let dmg = 20; // Ульт лечит и бьет
                player.hp = Math.min(player.maxHp, player.hp + heal);
                enemy.hp -= dmg;
                sounds.heal();
                addLog(`🔥 УЛЬТИМЕЙТ! Лечение на ${heal}, урон врагу ${dmg}!`, '#ffff55');
            } else if (type === 'rest') {
                player.mana = Math.min(player.maxMana, player.mana + 2);
                sounds.rest();
                addLog(`Ты отдыхаешь и копишь силы (+2 ⚡).`, '#aaddff');
            }

            if (enemy.hp <= 0) {
                enemy.hp = 0;
                updateUI();
                sounds.win();
                addLog(`💀 ${enemy.name} повержен!`, '#55ff55');
                currentStage++;
                setTimeout(() => { loadStage(currentStage); isPlayerTurn = true; }, 2000);
                return;
            }

            updateUI();
            setTimeout(enemyTurn, 1200);
        }

        function enemyTurn() {
            let dmg = Math.floor(Math.random() * (enemy.maxDmg - enemy.minDmg + 1)) + enemy.minDmg;
            
            if (isDefending) {
                dmg = Math.floor(dmg * 0.3); // Блок режет 70% урона
                addLog(`${enemy.sprite} атакует! Блок поглотил часть урона. Получено ${dmg}.`);
            } else {
                addLog(`${enemy.sprite} яростно бьет! Получено ${dmg} урона.`, '#ff5555');
            }

            sounds.enemyHit();
            player.hp -= dmg;
            
            if (player.hp <= 0) {
                player.hp = 0;
                updateUI();
                sounds.lose();
                addLog("💀 ТЫ ПОГИБ. Тьма поглотила этот мир...", '#ff0000');
                return;
            }

            isPlayerTurn = true;
            updateUI();
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
