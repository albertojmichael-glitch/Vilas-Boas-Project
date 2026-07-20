const outputDiv = document.getElementById('output');

const inputField = document.getElementById('comando');

let historicoComandos = [];
let posicaoHistorico = -1;
let comandoDigitadoAtual = "";


const terminal = document.getElementById('terminal');
const loadingSpinner = document.getElementById('loading');

// NOVA VARIÁVEL QUE CONTROLA A LINHA DO C:\>
const inputLineDiv = document.querySelector('.input-line'); 

// Elementos da HUD
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
            // Salva o comando no histórico (sem repetir o último)
            if (historicoComandos[historicoComandos.length - 1] !== comando) {
                historicoComandos.push(comando);
            }
            posicaoHistorico = historicoComandos.length; // Reseta a posição
            
            // Joga o comando na tela (eco)
            const p = document.createElement("p");
            p.className = "branco";
            p.innerHTML = `<span class="prompt">C:\\></span> ${comandoBruto}`;
            outputDiv.appendChild(p);
            
            inputField.value = "";
            terminal.scrollTop = terminal.scrollHeight;
            
            await enviarComando(comando);
        }
    } 
    // --- LÓGICA DA SETA PRA CIMA ---
    else if (event.key === "ArrowUp") {
        event.preventDefault(); // Impede o cursor de ir pro começo
        if (posicaoHistorico === historicoComandos.length) {
            comandoDigitadoAtual = inputField.value; // Salva o que estava digitando
        }
        if (posicaoHistorico > 0) {
            posicaoHistorico--;
            inputField.value = historicoComandos[posicaoHistorico];
        }
    } 
    // --- LÓGICA DA SETA PRA BAIXO ---
    else if (event.key === "ArrowDown") {
        event.preventDefault();
        if (posicaoHistorico < historicoComandos.length - 1) {
            posicaoHistorico++;
            inputField.value = historicoComandos[posicaoHistorico];
        } else if (posicaoHistorico === historicoComandos.length - 1) {
            posicaoHistorico++;
            inputField.value = comandoDigitadoAtual; // Devolve o texto em rascunho
        }
    }
});

document.addEventListener('click', () => {
    inputField.focus();
});

function atualizarSidebar(estado) {
    if (!estado) return;
    salaEl.textContent = estado.sala;
    
    const hpVal = document.getElementById("hp-val");
    if (estado.hp === "∞") {
        hpVal.innerText = "[ GOD MODE ]";
        hpVal.className = "amarelo";
    } else {
        // Supondo que o HP máximo normal seja 3
        const hpAtual = parseInt(estado.hp) || 0;
        const maxHp = 3;
        
        // Cria os blocos cheios (█) e vazios (░)
        const blocosCheios = "█".repeat(hpAtual);
        const blocosVazios = "░".repeat(Math.max(0, maxHp - hpAtual));
        
        hpVal.innerText = `[${blocosCheios}${blocosVazios}]`;
        
        // Muda a cor para vermelho se o HP estiver em 1 (Perigo)
        if (hpAtual <= 1) {
            hpVal.className = "vermelho";
        } else {
            hpVal.className = "verde";
        }
    }
    
    luzEl.textContent = estado.luz === "∞" ? "∞" : estado.luz + " turnos";
    
    invEl.innerHTML = "";
    if (estado.inventario.length === 0) invEl.innerHTML = "<li>Vazio</li>";
    else estado.inventario.forEach(item => { invEl.innerHTML += `<li>- ${item}</li>`; });

    saidasEl.innerHTML = "";
    if (estado.saidas.length === 0) saidasEl.innerHTML = "<li>Nenhuma visível</li>";
    else estado.saidas.forEach(saida => { saidasEl.innerHTML += `<li>> ${saida}</li>`; });
}

async function processarLinhas(linhas, estado) {
    for (let linha of linhas) {
        await novaLinha(linha);
    }
    atualizarSidebar(estado);
}

function novaLinha(linha) {
    return new Promise((resolve) => {
        if (linha.startsWith("@@CLEAR@@")) {
            outputDiv.innerHTML = "";
            resolve();
        } else if (linha.startsWith("@@TYPE@@")) {
            let parts = linha.split("@@");
            let cor = parts[2];
            let ms = parseInt(parts[3]);
            let texto = parts.slice(4).join("@@"); 
            digitarTextoAnimadoHTML(texto, cor, ms, resolve);
        } else {
            // O SEGREDO AQUI: Qualquer 'print' normal que o Python enviar 
            // será automaticamente digitado a 15ms por letra!
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
    inputLineDiv.style.display = 'none'; // ESCONDE O C:\> DURANTE A DIGITAÇÃO
    loadingSpinner.style.display = 'flex';
    
    // 1. Inicia o cronômetro AQUI
    const startTime = Date.now(); 
    
    try {
        const res = await fetch(url, options);
        if (!res.ok) throw new Error("Servidor offline");
        const data = await res.json();
        
        // 2. Calcula quanto tempo passou
        const tempoDecorrido = Date.now() - startTime;
        
        // 3. Se foi rápido demais (menos de 300ms), força uma esperazinha
        if (tempoDecorrido < 300) {
            await new Promise(resolve => setTimeout(resolve, 300 - tempoDecorrido));
        }
        
        loadingSpinner.style.display = 'none';
        await processarLinhas(data.linhas, data.estado);
    } catch (erro) {

        console.error("O ERRO REAL É ESTE AQUI:", erro);
        
        loadingSpinner.style.display = 'none';
        let p = document.createElement('p');
        p.className = 'vermelho';
        p.innerHTML = "[ERRO DE CONEXÃO] O sinal com o servidor falhou. Verifique sua internet.";
        outputDiv.appendChild(p);
        terminal.scrollTop = terminal.scrollHeight;
    } finally {
        inputLineDiv.style.display = 'flex'; // MOSTRA O C:\> DE NOVO QUANDO ACABA
        inputField.disabled = false;
        inputField.focus();
    }
}

function iniciarJogo() {
    fetchSeguro('/iniciar', { method: 'GET' });
}

// --- SINTETIZADOR DE SOM MS-DOS ---
function reproduzirBeep(tipo = 'sucesso') {
    // Usa o sintetizador nativo do navegador (não precisa de arquivos MP3!)
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(audioCtx.destination);

    if (tipo === 'erro') {
        oscillator.type = 'sawtooth'; // Som mais "rasgado" e grave
        oscillator.frequency.setValueAtTime(150, audioCtx.currentTime); 
        gainNode.gain.setValueAtTime(0.1, audioCtx.currentTime);
        oscillator.start();
        oscillator.stop(audioCtx.currentTime + 0.3);
    } else {
        oscillator.type = 'square'; // Beep clássico e agudo
        oscillator.frequency.setValueAtTime(800, audioCtx.currentTime); 
        gainNode.gain.setValueAtTime(0.03, audioCtx.currentTime);
        oscillator.start();
        oscillator.stop(audioCtx.currentTime + 0.1);
    }
}

function enviarComando() {
    const comando = inputField.value;
    if (!comando.trim()) return;
    
    let p = document.createElement('p');
    p.innerHTML = `<span class="branco">> C:\\> ${comando}</span>`;
    outputDiv.appendChild(p);
    
    inputField.value = '';
    terminal.scrollTop = terminal.scrollHeight;

    fetchSeguro('/comando', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ comando: comando })
    });
}

window.onload = iniciarJogo;

// Funções do Modal de Ajuda
function openHelp() {
    document.getElementById('help-modal').classList.remove('hidden');
}

function closeHelp() {
    document.getElementById('help-modal').classList.add('hidden');
    // Foca de volta no input para o jogador não ter que clicar na tela
    document.getElementById('comando').focus(); 
}

// Fechar o modal com a tecla ESC
document.addEventListener('keydown', function(event) {
    if (event.key === "Escape") {
        closeHelp();
    }
});

// --- ATALHOS GLOBAIS DE TECLADO ---
document.addEventListener('keydown', function (e) {
    // Ctrl + L (Limpar Terminal)
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'l') {
        e.preventDefault();
        outputDiv.innerHTML = '';
        reproduzirBeep('sucesso');
    }
    
    // Ctrl + S (Feedback visual de Save)
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 's') {
        e.preventDefault();
        let p = document.createElement('p');
        p.className = 'verde';
        p.innerHTML = "[SISTEMA] O progresso do jogo é salvo automaticamente a cada turno.";
        outputDiv.appendChild(p);
        terminal.scrollTop = terminal.scrollHeight;
        reproduzirBeep('sucesso');
    }

    // Tecla ? (Ajuda) - Só abre se ele não estiver digitando texto
    if (e.key === '?' && document.activeElement !== inputField) {
        e.preventDefault();
        openHelp(); // Função que criamos na etapa anterior
    }
});