const outputDiv = document.getElementById('output');

const inputField = document.getElementById('comando');

let historicoComandos = [];
let posicaoHistorico = -1;
let comandoDigitadoAtual = "";


const terminal = document.getElementById('terminal');
const loadingSpinner = document.getElementById('loading');


const inputLineDiv = document.querySelector('.input-line'); 

const hpEl = document.getElementById('hud-hp');
const luzEl = document.getElementById('hud-luz');
const invEl = document.getElementById('hud-inv');
const salaEl = document.getElementById('hud-sala');
const saidasEl = document.getElementById('hud-saidas');

inputField.addEventListener("keydown", async function(event) {
    if (event.key === "Enter") {
        const comandoBruto = inputField.value;
        const comando = comandoBruto.trim();
        
        if (comando !== "") {
            
            if (historicoComandos[historicoComandos.length - 1] !== comando) {
                historicoComandos.push(comando);
            }
            posicaoHistorico = historicoComandos.length; 
            
            
            const p = document.createElement("p");
            p.className = "branco";
            p.innerHTML = `<span class="prompt">C:\\></span> ${comandoBruto}`;
            outputDiv.appendChild(p);
            
            inputField.value = "";
            terminal.scrollTop = terminal.scrollHeight;
            
            await enviarComando(comando);
        }
    } 
    
    else if (event.key === "ArrowUp") {
        event.preventDefault(); 
        if (posicaoHistorico === historicoComandos.length) {
            comandoDigitadoAtual = inputField.value; 
        }
        if (posicaoHistorico > 0) {
            posicaoHistorico--;
            inputField.value = historicoComandos[posicaoHistorico];
        }
    } 
    
    else if (event.key === "ArrowDown") {
        event.preventDefault();
        if (posicaoHistorico < historicoComandos.length - 1) {
            posicaoHistorico++;
            inputField.value = historicoComandos[posicaoHistorico];
        } else if (posicaoHistorico === historicoComandos.length - 1) {
            posicaoHistorico++;
            inputField.value = comandoDigitadoAtual; 
        }
    }
});

document.addEventListener('click', () => {
    inputField.focus();
});

function atualizarSidebar(estado) {
    if (!estado) return;

    // --- HUD DE HP ---
    const hpVal = document.getElementById("hp-val");
    if (hpVal) {
        if (estado.hp === "∞") {
            hpVal.textContent = "[ GOD MODE ]";
            hpVal.className = "amarelo";
        } else {
            const hpAtual = parseInt(estado.hp) || 0;
            const maxHp = 3;
            const blocosCheios = "█".repeat(hpAtual);
            const blocosVazios = "░".repeat(Math.max(0, maxHp - hpAtual));
            
            hpVal.textContent = `[${blocosCheios}${blocosVazios}]`;
            hpVal.className = (hpAtual <= 1) ? "vermelho" : "verde";
        }
    }

    // --- HUD DE LUZ (Consertado) ---
    const luzVal = document.getElementById("luz-val");
    if (luzVal) {
        luzVal.textContent = estado.turnos_luz !== undefined ? estado.turnos_luz : "??";
        luzVal.className = (estado.turnos_luz <= 3) ? "vermelho" : "verde";
    }

    
    const invList = document.getElementById("inv-list");
    const invTitulo = document.querySelector("#hud-inv"); 
    
    if (invList) {
        invList.innerHTML = "";
        
        
        
        let qtdBolsas = 0;
        if (estado.inventario) {
            qtdBolsas = estado.inventario.filter(item => item === "bolsa").length;
        }
        
        const limiteMaximo = 3 + (qtdBolsas * 3);
        const qtdAtual = estado.inventario ? estado.inventario.length : 0;
        
        
        if (invTitulo) {
            invTitulo.textContent = `INV (${qtdAtual}/${limiteMaximo}):`;
        }

        if (qtdAtual > 0) {
            estado.inventario.forEach(item => {
                let li = document.createElement("li");
                li.textContent = `- ${item}`;
                li.className = "branco";
                invList.appendChild(li);
            });
        } else {
            let li = document.createElement("li");
            li.textContent = "Vazio";
            li.className = "amarelo";
            invList.appendChild(li);
        }
    }
}

async function processarLinhas(linhas, estado) {
    const terminal = document.querySelector('.terminal-section'); 

    for (let linha of linhas) {
        await novaLinha(linha, terminal); 
        
        
        if (terminal) terminal.scrollTop = terminal.scrollHeight;
    }
    atualizarSidebar(estado);
}

function novaLinha(linha, terminal) {
    return new Promise((resolve) => {

        if (typeof linha === 'string' && linha.includes("@@JUMPSCARE@@")) {
            linha = linha.replace("@@JUMPSCARE@@", ""); 
            triggerJumpscare(); 
        }


        if (linha.startsWith("@@CLEAR@@")) {
            outputDiv.innerHTML = "";
            
            if (terminal) terminal.scrollTop = terminal.scrollHeight;
            resolve();
        } else if (linha.startsWith("@@TYPE@@")) {
            let parts = linha.split("@@");
            let cor = parts[2];
            let ms = parseInt(parts[3]);
            let texto = parts.slice(4).join("@@"); 
            digitarTextoAnimadoHTML(texto, cor, ms, resolve);
        } else {
            digitarTextoAnimadoHTML(linha, "", 15, resolve);
        }
    });
}


function digitarTextoAnimadoHTML(htmlString, classeCor, velocidade, aoTerminar) {
    const p = document.createElement('p');
    
    let a11yPrefix = "";
    if (classeCor === 'vermelho') a11yPrefix = "<span style='opacity:0; position:absolute'>[PERIGO] </span>";
    if (classeCor === 'amarelo') a11yPrefix = "<span style='opacity:0; position:absolute'>[ATENÇÃO] </span>";
    
    if (classeCor) p.className = classeCor;
    outputDiv.appendChild(p);
    
    if (velocidade === 0) {
        p.innerHTML = a11yPrefix + htmlString;
        terminal.scrollTop = terminal.scrollHeight;
        aoTerminar();
        return;
    }
    
    let i = 0;
    let isTag = false;
    let currentHTML = "";
    
    function digitar() {
        if (i < htmlString.length) {
            let char = htmlString.charAt(i);
            currentHTML += char;
            p.innerHTML = a11yPrefix + currentHTML;
            i++;
            
            terminal.scrollTop = terminal.scrollHeight;
            
            if (char === '<') isTag = true;
            if (char === '>') isTag = false;
            
            if (isTag || (i < htmlString.length && htmlString.charAt(i) === '<')) {
                digitar(); 
            } else {
                setTimeout(digitar, velocidade);
            }
        } else {
            aoTerminar(); 
        }
    }
    digitar();
}

async function fetchSeguro(url, options) {
    inputField.disabled = true;
    inputLineDiv.style.display = 'none'; 
    loadingSpinner.style.display = 'flex';
    
    
    const startTime = Date.now(); 
    
    try {
        const res = await fetch(url, options);
        if (!res.ok) throw new Error("Servidor offline");
        const data = await res.json();

        console.log("PYTHON:", data);
        
        
        const tempoDecorrido = Date.now() - startTime;
        
        
        if (tempoDecorrido < 300) {
            await new Promise(resolve => setTimeout(resolve, 300 - tempoDecorrido));
        }
        
        loadingSpinner.style.display = 'none';
        await processarLinhas(data.linhas, data.estado);

        if (url === '/comando') { 
            mostrarSalvando(); 
        }

    } catch (erro) {

        console.error("O ERRO REAL É ESTE AQUI:", erro);

        loadingSpinner.style.display = 'none';
        let p = document.createElement('p');
        p.className = 'vermelho';
        p.innerHTML = "[ERRO DE CONEXÃO] O sinal com o servidor falhou. Verifique sua internet.";
        outputDiv.appendChild(p);
        terminal.scrollTop = terminal.scrollHeight;
    } finally {
        inputLineDiv.style.display = 'flex'; 
        inputField.disabled = false;
        inputField.focus();
    }
}

function iniciarJogo() {
    fetchSeguro('/iniciar', { method: 'GET' });
}


function reproduzirBeep(tipo = 'sucesso') {
    
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(audioCtx.destination);

    if (tipo === 'erro') {
        oscillator.type = 'sawtooth'; 
        oscillator.frequency.setValueAtTime(150, audioCtx.currentTime); 
        gainNode.gain.setValueAtTime(0.1, audioCtx.currentTime);
        oscillator.start();
        oscillator.stop(audioCtx.currentTime + 0.3);
    } else {
        oscillator.type = 'square'; 
        oscillator.frequency.setValueAtTime(800, audioCtx.currentTime); 
        gainNode.gain.setValueAtTime(0.03, audioCtx.currentTime);
        oscillator.start();
        oscillator.stop(audioCtx.currentTime + 0.1);
    }
}

async function enviarComando(comando) {
    
    fetchSeguro('/comando', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ comando: comando })
    });
}

window.onload = iniciarJogo;


function openHelp() {
    document.getElementById('help-modal').classList.remove('hidden');
}

function closeHelp() {
    document.getElementById('help-modal').classList.add('hidden');
    
    document.getElementById('comando').focus(); 
}


document.addEventListener('keydown', function(event) {
    if (event.key === "Escape") {
        closeHelp();
    }
});


document.addEventListener('keydown', function (e) {
    
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'l') {
        e.preventDefault();
        outputDiv.innerHTML = '';
        reproduzirBeep('sucesso');
    }
    
    
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 's') {
        e.preventDefault();
        let p = document.createElement('p');
        p.className = 'verde';
        p.innerHTML = "[SISTEMA] O progresso do jogo é salvo automaticamente a cada turno.";
        outputDiv.appendChild(p);
        terminal.scrollTop = terminal.scrollHeight;
        reproduzirBeep('sucesso');
    }

    
    if (e.key === '?' && document.activeElement !== inputField) {
        e.preventDefault();
        openHelp(); 
    }
});


document.addEventListener('click', () => {
    const inputTerminal = document.querySelector('input');
    const textoSelecionado = window.getSelection().toString();
    
    
    if (!textoSelecionado && inputTerminal) {
        inputTerminal.focus();
    }
});


const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

function playBip(tipo) {
    if (audioCtx.state === 'suspended') audioCtx.resume();
    
    const oscillator = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioCtx.destination);

    if (tipo === 'erro') {
        
        oscillator.type = 'sawtooth';
        oscillator.frequency.setValueAtTime(150, audioCtx.currentTime);
        gainNode.gain.setValueAtTime(0.1, audioCtx.currentTime);
        oscillator.start();
        oscillator.stop(audioCtx.currentTime + 0.3);
    } else {
        
        oscillator.type = 'square';
        oscillator.frequency.setValueAtTime(800, audioCtx.currentTime);
        gainNode.gain.setValueAtTime(0.05, audioCtx.currentTime);
        oscillator.start();
        oscillator.stop(audioCtx.currentTime + 0.08);
    }
}

// ==========================================
// NOVOS SISTEMAS DE IMERSÃO (V1.0 FINAL)
// ==========================================


function executarAtalho(cmd) {
    const input = document.getElementById('comando');
    input.value = cmd;
    input.focus();
    
    if (typeof enviarComando === "function") enviarComando();
}


let ambientCtx, ambientOsc, ambientGain;
function iniciarSomAmbiente() {
    if (ambientCtx) return;
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!AudioContext) return;
    
    ambientCtx = new AudioContext();
    ambientOsc = ambientCtx.createOscillator();
    ambientGain = ambientCtx.createGain();
    
    ambientOsc.type = 'triangle';
    ambientOsc.frequency.value = 55; 
    ambientGain.gain.value = 0.03; 
    
    ambientOsc.connect(ambientGain);
    ambientGain.connect(ambientCtx.destination);
    ambientOsc.start();
}

document.body.addEventListener('click', iniciarSomAmbiente, {once: true});
document.body.addEventListener('keydown', iniciarSomAmbiente, {once: true});


function triggerJumpscare() {
    const overlay = document.getElementById('jumpscare-overlay');
    overlay.classList.remove('hidden');
    
    
    if(ambientCtx) {
        const scareOsc = ambientCtx.createOscillator();
        const scareGain = ambientCtx.createGain();
        scareOsc.type = 'sawtooth';
        scareOsc.frequency.value = 130;
        scareGain.gain.value = 0.6; 
        scareOsc.connect(scareGain);
        scareGain.connect(ambientCtx.destination);
        scareOsc.start();
        scareOsc.stop(ambientCtx.currentTime + 0.15); 
    }
    
    
    setTimeout(() => overlay.classList.add('hidden'), 150); 
}


function mostrarSalvando() {
    const ind = document.getElementById('save-indicator');
    ind.classList.remove('hidden');
    setTimeout(() => ind.classList.add('hidden'), 1500);
}