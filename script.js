const outputDiv = document.getElementById('output');
const inputField = document.getElementById('comando');
const terminal = document.getElementById('terminal');

// Elementos da HUD
const hpEl = document.getElementById('hud-hp');
const luzEl = document.getElementById('hud-luz');
const invEl = document.getElementById('hud-inv');
const salaEl = document.getElementById('hud-sala');
const saidasEl = document.getElementById('hud-saidas');

// Auto-submit pelo ENTER
inputField.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        enviarComando();
    }
});

// Força foco no input sempre que clicar na tela
document.addEventListener('click', () => {
    inputField.focus();
});

function atualizarSidebar(estado) {
    if (!estado) return;
    
    salaEl.textContent = estado.sala;
    
    // Desenha corações para a vida
    if (estado.hp === "∞") {
        hpEl.textContent = "∞";
    } else {
        const coracoes = "❤️".repeat(Math.max(0, estado.hp)) + "🖤".repeat(Math.max(0, 3 - estado.hp));
        hpEl.textContent = coracoes;
    }
    
    luzEl.textContent = estado.luz === "∞" ? "∞" : estado.luz + " turnos";
    
    // Lista de Inventário
    invEl.innerHTML = "";
    if (estado.inventario.length === 0) {
        invEl.innerHTML = "<li>Vazio</li>";
    } else {
        estado.inventario.forEach(item => {
            let li = document.createElement('li');
            li.textContent = "- " + item;
            invEl.appendChild(li);
        });
    }

    // Lista de Saídas do Mapa
    saidasEl.innerHTML = "";
    if (estado.saidas.length === 0) {
        saidasEl.innerHTML = "<li>Nenhuma visível</li>";
    } else {
        estado.saidas.forEach(saida => {
            let li = document.createElement('li');
            li.textContent = "> " + saida;
            saidasEl.appendChild(li);
        });
    }
}

async function processarLinhas(linhas, estado) {
    inputField.disabled = true; // Bloqueia spam de comandos
    
    for (let linha of linhas) {
        await novaLinha(linha);
    }
    
    atualizarSidebar(estado);
    
    inputField.disabled = false;
    inputField.focus();
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
            let texto = parts.slice(4).join("@@"); // Junta caso o texto tenha "@@" dentro
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
    if (classeCor) p.className = classeCor;
    outputDiv.appendChild(p);
    
    if (velocidade === 0) {
        p.innerHTML = htmlString;
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
            p.innerHTML = currentHTML;
            i++;
            
            terminal.scrollTop = terminal.scrollHeight;
            
            if (char === '<') isTag = true;
            if (char === '>') isTag = false;
            
            // Pula a lentidão instantaneamente se for um código HTML invisível
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

async function iniciarJogo() {
    const res = await fetch('/iniciar');
    const data = await res.json();
    processarLinhas(data.linhas, data.estado);
}

async function enviarComando() {
    const comando = inputField.value;
    if (!comando.trim()) return;
    
    let p = document.createElement('p');
    p.innerHTML = `<span class="branco">> C:\\> ${comando}</span>`;
    outputDiv.appendChild(p);
    
    inputField.value = '';
    terminal.scrollTop = terminal.scrollHeight;

    const res = await fetch('/comando', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ comando: comando })
    });
    
    const data = await res.json();
    processarLinhas(data.linhas, data.estado);
}

window.onload = iniciarJogo;