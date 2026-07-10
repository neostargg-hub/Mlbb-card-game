"use strict";

// ===============================
// SOCKET
// ===============================

const socket = io();

// ===============================
// GAME
// ===============================

const Game = {

    player: null,

    heroes: {},

    players: {},

    keys: {},

    fps: 0,

    lastFrame: 0,

    canvas: null,

    ctx: null,

    camera: {

        x: 0,

        y: 0

    },

    tileSize: 48,

    worldWidth: 200,

    worldHeight: 200

};

// ===============================
// UI
// ===============================

const UI = {

    loading:

        document.getElementById("loading"),

    login:

        document.getElementById("loginScreen"),

    game:

        document.getElementById("game"),

    canvas:

        document.getElementById("gameCanvas"),

    nickname:

        document.getElementById("nickname"),

    hero:

        document.getElementById("hero"),

    createBtn:

        document.getElementById("createBtn"),

    loginBtn:

        document.getElementById("loginBtn")

};

// ===============================
// INIT
// ===============================

window.onload = async () => {

    Game.canvas = UI.canvas;

    Game.ctx = UI.canvas.getContext("2d");

    await loadHeroes();

    UI.loading.classList.add("hidden");

    UI.login.classList.remove("hidden");

    bindEvents();

};

// ===============================
// LOAD HEROES
// ===============================

async function loadHeroes(){

    const response = await fetch("/api/heroes");

    Game.heroes = await response.json();

}

// ===============================
// REGISTER
// ===============================

async function registerPlayer(){

    const nickname =

        UI.nickname.value.trim();

    const hero =

        UI.hero.value;

    if(nickname.length < 2){

        alert("Введите ник");

        return;

    }

    const response = await fetch(

        "/api/register",

        {

            method:"POST",

            headers:{

                "Content-Type":"application/json"

            },

            body:JSON.stringify({

                nickname,

                hero

            })

        }

    );

    const result =

        await response.json();

    if(result.status==="exists"){

        alert("Такой игрок уже существует");

        return;

    }

    if(result.status==="error"){

        alert(result.message);

        return;

    }

    Game.player = result.player;

    startGame();

}

// ===============================
// LOGIN
// ===============================

async function loginPlayer(){

    const nickname =

        UI.nickname.value.trim();

    const response = await fetch(

        "/api/login",

        {

            method:"POST",

            headers:{

                "Content-Type":"application/json"

            },

            body:JSON.stringify({

                nickname

            })

        }

    );

    const result =

        await response.json();

    if(result.status!=="ok"){

        alert("Игрок не найден");

        return;

    }

    Game.player = result.player;

    startGame();

}
// ===============================
// START GAME
// ===============================

function startGame() {

    UI.login.classList.add("hidden");
    UI.game.classList.remove("hidden");

    document.getElementById("playerName").textContent =
        Game.player.nickname;

    document.getElementById("playerLevel").textContent =
        "Lv." + Game.player.level;

    updateStats();

    socket.emit("join", {

        nickname: Game.player.nickname

    });

    requestAnimationFrame(gameLoop);

}

// ===============================
// UPDATE UI
// ===============================

function updateStats(){

    document.getElementById("hp").textContent =
        Game.player.hp;

    document.getElementById("maxHp").textContent =
        Game.player.max_hp;

    document.getElementById("mana").textContent =
        Game.player.mana;

    document.getElementById("maxMana").textContent =
        Game.player.max_mana;

    document.getElementById("attack").textContent =
        Game.player.attack;

    document.getElementById("defense").textContent =
        Game.player.defense;

    document.getElementById("xp").textContent =
        Game.player.xp;

    document.getElementById("gold").textContent =
        Game.player.gold + " золота";

}

// ===============================
// INPUT
// ===============================

function bindEvents(){

    UI.createBtn.onclick =
        registerPlayer;

    UI.loginBtn.onclick =
        loginPlayer;

    window.addEventListener(

        "keydown",

        e=>{

            Game.keys[e.key.toLowerCase()] = true;

        }

    );

    window.addEventListener(

        "keyup",

        e=>{

            delete Game.keys[e.key.toLowerCase()];

        }

    );

}

// ===============================
// MOVEMENT
// ===============================

function updateMovement(){

    if(!Game.player)
        return;

    let moved = false;

    const speed = 4;

    if(Game.keys["w"] || Game.keys["arrowup"]){

        Game.player.y -= speed;

        moved = true;

    }

    if(Game.keys["s"] || Game.keys["arrowdown"]){

        Game.player.y += speed;

        moved = true;

    }

    if(Game.keys["a"] || Game.keys["arrowleft"]){

        Game.player.x -= speed;

        moved = true;

    }

    if(Game.keys["d"] || Game.keys["arrowright"]){

        Game.player.x += speed;

        moved = true;

    }

    if(!moved)
        return;

    socket.emit(

        "move",

        {

            nickname:Game.player.nickname,

            x:Game.player.x,

            y:Game.player.y

        }

    );

}

// ===============================
// GAME LOOP
// ===============================

function gameLoop(time){

    const delta =

        time - Game.lastFrame;

    Game.lastFrame = time;

    Game.fps =

        Math.round(1000 / Math.max(delta,1));

    document.getElementById("fps").textContent =
        Game.fps + " FPS";

    updateMovement();

    draw();

    requestAnimationFrame(gameLoop);

}
