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

// ==========================================
// GERENCIADOR DE ÁUDIO E ZUMBIDO CRT
// ==========================================
let audioCtx = null;
let ambientOsc = null;
let crtOsc = null;

function obterAudioContext() {
    if (!audioCtx) {
        const AudioContextClass = window.AudioContext || window.webkitAudioContext;
        if (AudioContextClass) {
            audioCtx = new AudioContextClass();
        }
    }
    if (audioCtx && audioCtx.state === 'suspended') {
        audioCtx.resume();
    }
    return audioCtx;
}

function iniciarSomAmbiente() {
    const ctx = obterAudioContext();
    if (!ctx || ambientOsc) return;

    // 1. Drone Grave de Fundo (Ambiente abafado de $55\text{ Hz}$)
    ambientOsc = ctx.createOscillator();
    const ambientGain = ctx.createGain();
    ambientOsc.type = 'triangle';
    ambientOsc.frequency.value = 55; 
    ambientGain.gain.value = 0.025; 

    ambientOsc.connect(ambientGain);
    ambientGain.connect(ctx.destination);
    ambientOsc.start();

    // 2. Zumbido de Monitor CRT (Chiado elétrico de $60\text{ Hz}$)
    crtOsc = ctx.createOscillator();
    const crtGain = ctx.createGain();
    crtOsc.type = 'sawtooth';
    crtOsc.frequency.value = 60; 
    crtGain.gain.value = 0.005; 

    crtOsc.connect(crtGain);
    crtGain.connect(ctx.destination);
    crtOsc.start();
}

document.body.addEventListener('click', iniciarSomAmbiente, { once: true });
document.body.addEventListener('keydown', iniciarSomAmbiente, { once: true });

// ==========================================
// SINTETIZADORES DE EFEITOS SONOROS
// ==========================================

// 1. Som de caractere sendo impresso na tela
function tocarSomDigito() {
    const ctx = obterAudioContext();
    if (!ctx) return;

    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.type = 'triangle';
    osc.frequency.setValueAtTime(320 + Math.random() * 90, ctx.currentTime);

    gain.gain.setValueAtTime(0.015, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.02);

    osc.connect(gain);
    gain.connect(ctx.destination);

    osc.start();
    osc.stop(ctx.currentTime + 0.02);
}

// 2. Bip de Confirmação de Comando (Enter)
function tocarBipEntrada() {
    const ctx = obterAudioContext();
    if (!ctx) return;

    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.type = 'square'; 
    osc.frequency.setValueAtTime(550, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(1100, ctx.currentTime + 0.05);

    gain.gain.setValueAtTime(0.035, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.06);

    osc.connect(gain);
    gain.connect(ctx.destination);

    osc.start();
    osc.stop(ctx.currentTime + 0.06);
}

// 3. Passos Metálicos Pesados
function tocarPassoMetalico() {
    const ctx = obterAudioContext();
    if (!ctx) return;

    const t = ctx.currentTime;

    // Impacto Sub-grave do peso
    const subOsc = ctx.createOscillator();
    const subGain = ctx.createGain();
    subOsc.type = 'sine';
    subOsc.frequency.setValueAtTime(110, t);
    subOsc.frequency.exponentialRampToValueAtTime(30, t + 0.25);

    subGain.gain.setValueAtTime(0.12, t);
    subGain.gain.exponentialRampToValueAtTime(0.001, t + 0.25);

    subOsc.connect(subGain);
    subGain.connect(ctx.destination);
    subOsc.start(t);
    subOsc.stop(t + 0.25);

    // Rangido e fricção do metal
    const metalOsc = ctx.createOscillator();
    const metalGain = ctx.createGain();
    metalOsc.type = 'sawtooth';
    metalOsc.frequency.setValueAtTime(420 + Math.random() * 80, t);
    metalOsc.frequency.exponentialRampToValueAtTime(160, t + 0.18);

    metalGain.gain.setValueAtTime(0.045, t);
    metalGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.18);

    metalOsc.connect(metalGain);
    metalGain.connect(ctx.destination);
    metalOsc.start(t);
    metalOsc.stop(t + 0.18);
}

// Beep genérico de erro/sucesso
function reproduzirBeep(tipo = 'sucesso') {
    const ctx = obterAudioContext();
    if (!ctx) return;

    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.connect(gain);
    gain.connect(ctx.destination);

    if (tipo === 'erro') {
        osc.type = 'sawtooth'; 
        osc.frequency.setValueAtTime(150, ctx.currentTime); 
        gain.gain.setValueAtTime(0.08, ctx.currentTime);
        osc.start();
        osc.stop(ctx.currentTime + 0.3);
    } else {
        osc.type = 'square'; 
        osc.frequency.setValueAtTime(800, ctx.currentTime); 
        gain.gain.setValueAtTime(0.03, ctx.currentTime);
        osc.start();
        osc.stop(ctx.currentTime + 0.1);
    }
}

function playBip(tipo) {
    reproduzirBeep(tipo);
}

// ==========================================
// FOCO INTELIGENTE E CONTROLES
// ==========================================
document.addEventListener('click', (event) => {
    const inputTerminal = document.getElementById('comando');
    const textoSelecionado = window.getSelection().toString();
    const clicouNoBotao = event.target.closest('button');
    
    if (!textoSelecionado && inputTerminal && !clicouNoBotao) {
        inputTerminal.focus();
    }
});

// ==========================================
// EVENTOS DE TECLADO (INPUT)
// ==========================================
inputField.addEventListener("keydown", async function(event) {
    if (event.key === "Enter") {
        const comandoBruto = inputField.value;
        const comando = comandoBruto.trim();
        
        if (comando !== "") {
            tocarBipEntrada(); // Toca o Bip ao apertar Enter

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

// ==========================================
// ATUALIZAÇÃO DO HUD VISUAL
// ==========================================
function atualizarSidebar(estado) {
    if (!estado) return;

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

    const luzVal = document.getElementById("luz-val");
    if (luzVal) {
        luzVal.textContent = estado.luz !== undefined ? estado.luz : "??";
        luzVal.className = (estado.luz === "∞" || estado.luz > 3) ? "verde" : "vermelho";
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

// ==========================================
// PROCESSAMENTO E ANIMAÇÃO DE TEXTO
// ==========================================
async function processarLinhas(linhas, estado) {
    const terminalEl = document.querySelector('.terminal-section'); 

    for (let linha of linhas) {
        await novaLinha(linha, terminalEl); 
        if (terminalEl) terminalEl.scrollTop = terminalEl.scrollHeight;
    }
    atualizarSidebar(estado);
}

function novaLinha(linha, terminalEl) {
    return new Promise((resolve) => {
        if (typeof linha === 'string') {
            if (linha.includes("@@JUMPSCARE@@")) {
                linha = linha.replace("@@JUMPSCARE@@", ""); 
                triggerJumpscare(); 
            }
            if (linha.includes("@@PASSO@@")) {
                linha = linha.replace("@@PASSO@@", "");
                tocarPassoMetalico();
            }
        }

        if (linha.startsWith("@@CLEAR@@")) {
            outputDiv.innerHTML = "";
            if (terminalEl) terminalEl.scrollTop = terminalEl.scrollHeight;
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
                if (char !== ' ' && char !== '\n') {
                    tocarSomDigito(); // Som de digitação a cada letra exibida
                }
                setTimeout(digitar, velocidade);
            }
        } else {
            aoTerminar(); 
        }
    }
    digitar();
}

// ==========================================
// COMUNICAÇÃO COM O SERVIDOR (API)
// ==========================================
async function fetchSeguro(url, options) {
    inputField.disabled = true;
    inputLineDiv.style.display = 'none'; 
    loadingSpinner.style.display = 'flex';
    
    const startTime = Date.now(); 
    
    try {
        const res = await fetch(url, options);
        if (!res.ok) throw new Error("Servidor offline");
        const data = await res.json();

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
        console.error("Erro na comunicação:", erro);
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

async function enviarComando(comando) {
    fetchSeguro('/comando', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ comando: comando })
    });
}

window.onload = iniciarJogo;

// ==========================================
// UTILITÁRIOS E ATALHOS
// ==========================================
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

function executarAtalho(cmd) {
    const input = document.getElementById('comando');
    input.value = cmd;
    input.focus();
    if (typeof enviarComando === "function") enviarComando(cmd);
}

function triggerJumpscare() {
    const overlay = document.getElementById('jumpscare-overlay');
    if (overlay) overlay.classList.remove('hidden');
    
    const ctx = obterAudioContext();
    if (ctx) {
        const scareOsc = ctx.createOscillator();
        const scareGain = ctx.createGain();
        scareOsc.type = 'sawtooth';
        scareOsc.frequency.value = 130;
        scareGain.gain.value = 0.6; 
        scareOsc.connect(scareGain);
        scareGain.connect(ctx.destination);
        scareOsc.start();
        scareOsc.stop(ctx.currentTime + 0.15); 
    }
    
    if (overlay) setTimeout(() => overlay.classList.add('hidden'), 150); 
}

function mostrarSalvando() {
    const ind = document.getElementById('save-indicator');
    if (ind) {
        ind.classList.remove('hidden');
        setTimeout(() => ind.classList.add('hidden'), 1500);
    }
}

function fazerNada() {
    
}

