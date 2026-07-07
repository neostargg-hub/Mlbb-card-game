from flask import Flask, render_template_string

app = Flask(__name__)

# Весь интерфейс, стили и логика игры (HTML + CSS + JS)
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
            background-color: #1a1a1a;
            color: #e0e0e0;
            margin: 0;
            padding: 10px;
            font-size: 10px;
            text-align: center;
        }
        h1 { font-size: 14px; color: #d4af37; text-shadow: 2px 2px #000; }
        
        /* Пиксельные панели */
        .panel {
            background-color: #2b2b2b;
            border: 4px solid #555;
            box-shadow: 4px 4px 0px #000;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 0;
        }
        
        /* Статусы здоровья */
        .hp-bar {
            width: 100%;
            height: 20px;
            background-color: #440000;
            border: 2px solid #fff;
            margin-top: 5px;
            position: relative;
        }
        .hp-fill {
            height: 100%;
            background-color: #cc0000;
            width: 100%;
            transition: width 0.3s;
        }
        .hp-text {
            position: absolute;
            top: 2px;
            width: 100%;
            text-align: center;
            color: white;
            text-shadow: 1px 1px #000;
        }

        /* Игровой лог */
        #log {
            height: 80px;
            overflow-y: auto;
            background: #000;
            color: #00ff00;
            padding: 10px;
            text-align: left;
            border: 2px solid #555;
            line-height: 1.5;
        }

        /* Кнопки-карты */
        .cards {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .card-btn {
            font-family: 'Press Start 2P', cursive;
            background-color: #4a4a4a;
            color: #fff;
            border: 4px outset #888;
            padding: 15px;
            font-size: 10px;
            cursor: pointer;
            text-transform: uppercase;
        }
        .card-btn:active {
            border-style: inset;
            background-color: #333;
        }
        .card-btn.attack { color: #ff5555; }
        .card-btn.defend { color: #55aaff; }
        .card-btn.heal { color: #55ff55; }
        
        .sprite { font-size: 40px; margin: 10px 0; }
    </style>
</head>
<body>

    <h1>MLBB: Закат Бездны</h1>

    <!-- Враг -->
    <div class="panel">
        <div>ЛОРД БЕЗДНЫ</div>
        <div class="sprite">👾</div>
        <div class="hp-bar">
            <div id="enemy-hp-fill" class="hp-fill"></div>
            <div id="enemy-hp-text" class="hp-text">100/100</div>
        </div>
    </div>

    <!-- Лог битвы -->
    <div class="panel" style="padding: 5px;">
        <div id="log">Битва началась! Алукард против Лорда Бездны. Твой ход...</div>
    </div>

    <!-- Игрок -->
    <div class="panel">
        <div>АЛУКАРД (Ты)</div>
        <div class="hp-bar">
            <div id="player-hp-fill" class="hp-fill" style="background-color: #00aa00;"></div>
            <div id="player-hp-text" class="hp-text">100/100</div>
        </div>
        
        <p>Выбери карту:</p>
        <div class="cards">
            <button class="card-btn attack" onclick="playCard('attack')">⚔️ Расщепитель (Урон)</button>
            <button class="card-btn defend" onclick="playCard('defend')">🛡️ Крылья (Блок)</button>
            <button class="card-btn heal" onclick="playCard('heal')">🩸 Вампиризм (Лечение)</button>
        </div>
    </div>

    <script>
        // Состояние игры
        let playerHP = 100;
        let enemyHP = 100;
        let isDefending = false;
        let gameOver = false;

        function updateUI() {
            document.getElementById('player-hp-text').innerText = playerHP + '/100';
            document.getElementById('player-hp-fill').style.width = playerHP + '%';
            
            document.getElementById('enemy-hp-text').innerText = enemyHP + '/100';
            document.getElementById('enemy-hp-fill').style.width = enemyHP + '%';
        }

        function addLog(text) {
            const logDiv = document.getElementById('log');
            logDiv.innerHTML += '<br>' + text;
            logDiv.scrollTop = logDiv.scrollHeight;
        }

        function playCard(type) {
            if (gameOver) return;
            
            isDefending = false;

            if (type === 'attack') {
                let dmg = Math.floor(Math.random() * 15) + 10; // Урон 10-25
                enemyHP -= dmg;
                addLog(`Ты ударил мечом на ${dmg} урона!`);
            } else if (type === 'defend') {
                isDefending = true;
                addLog(`Ты ушел в защиту. Урон врага снижен!`);
            } else if (type === 'heal') {
                let heal = Math.floor(Math.random() * 10) + 15; // Лечение 15-25
                playerHP = Math.min(100, playerHP + heal);
                addLog(`Вампиризм восстановил ${heal} ОЗ.`);
            }

            if (enemyHP <= 0) {
                enemyHP = 0;
                updateUI();
                addLog("🏆 Лорд Бездны повержен! Мония спасена.");
                gameOver = true;
                return;
            }

            updateUI();
            setTimeout(enemyTurn, 1000); // Ход врага через 1 секунду
        }

        function enemyTurn() {
            if (gameOver) return;

            let dmg = Math.floor(Math.random() * 20) + 5; // Урон врага 5-25
            
            if (isDefending) {
                dmg = Math.floor(dmg / 3); // Защита режет урон
                addLog(`👾 Лорд бьет! Твоя защита поглотила урон. Получено ${dmg} ед.`);
            } else {
                addLog(`👾 Лорд атакует тьмой! Получено ${dmg} урона.`);
            }

            playerHP -= dmg;
            
            if (playerHP <= 0) {
                playerHP = 0;
                updateUI();
                addLog("💀 Ты пал. Бездна поглотила эти земли...");
                gameOver = true;
                return;
            }

            updateUI();
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    # Отдаем пользователю наш HTML
    return render_template_string(GAME_HTML)

if __name__ == '__main__':
    app.run(debug=True)