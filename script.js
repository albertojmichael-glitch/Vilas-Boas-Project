const outputDiv = document.getElementById('output');
const inputField = document.getElementById('comando');
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

inputField.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') enviarComando();
});

document.addEventListener('click', () => {
    inputField.focus();
});

function atualizarSidebar(estado) {
    if (!estado) return;
    salaEl.textContent = estado.sala;
    
    if (estado.hp === "∞") {
        hpEl.textContent = "∞";
    } else {
        // Usando a barra de vida estilo ASCII que configuramos!
        const coracoes = "[█] ".repeat(Math.max(0, estado.hp)) + "[ ] ".repeat(Math.max(0, 3 - estado.hp));
        hpEl.textContent = coracoes;
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
            let p = document.createElement('p');
            p.innerHTML = linha;
            outputDiv.appendChild(p);
            terminal.scrollTop = terminal.scrollHeight;
            resolve();
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
    
    try {
        const res = await fetch(url, options);
        if (!res.ok) throw new Error("Servidor offline");
        const data = await res.json();
        
        loadingSpinner.style.display = 'none';
        await processarLinhas(data.linhas, data.estado);
    } catch (erro) {
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