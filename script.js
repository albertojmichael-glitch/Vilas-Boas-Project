const inputField = document.getElementById('cmdInput');
const outputDiv = document.getElementById('output');
const terminal = document.getElementById('terminal');
const inputLine = document.querySelector('.input-line');
let digitando = false;

function ajustarLarguraInput() {
    const tamanho = Math.max(inputField.value.length, 1);
    inputField.style.width = tamanho + 'ch';
}
inputField.addEventListener('input', ajustarLarguraInput);

document.addEventListener('click', () => {
    if (!digitando) inputField.focus();
});

window.onload = () => {
    travarInput();
    fetch('/iniciar', { credentials: 'include' })
        .then(response => response.json())
        .then(data => {
            outputDiv.innerHTML = ''; 
            digitarFilaDeLinhas(data.linhas, 0);
        })
        .catch(error => {
            outputDiv.innerHTML = ''; 
            adicionarLinhaInstantaneaHTML('<span class="vermelho">FALHA DE CONEXÃO COM O SERVIDOR. LIGUE O APP.PY.</span>');
            destravarInput();
        });
};

inputField.addEventListener('keypress', function (e) {
    if (e.key === 'Enter' && !digitando) {
        const comando = inputField.value.trim();
        if (comando) {
            adicionarLinhaInstantaneaHTML(`<span class="verde">C:\\> ${comando}</span>`);
            inputField.value = '';
            ajustarLarguraInput();
            travarInput(); 
            
            fetch('/comando', {
                method: 'POST',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ comando: comando })
            })
            .then(response => response.json())
            .then(data => {
                digitarFilaDeLinhas(data.linhas, 0);
            })
            .catch(error => {
                adicionarLinhaInstantaneaHTML('<span class="vermelho">FALHA DE CONEXÃO COM O MAINFRAME.</span>');
                destravarInput();
            });
        }
    }
});

function travarInput() {
    digitando = true;
    inputLine.style.display = 'none'; 
}

function destravarInput() {
    digitando = false;
    inputLine.style.display = 'flex'; 
    inputField.focus(); 
    terminal.scrollTop = terminal.scrollHeight; 
}

function adicionarLinhaInstantaneaHTML(htmlString) {
    const p = document.createElement('p');
    p.className = 'verde'; 
    p.innerHTML = htmlString;
    outputDiv.appendChild(p);
    terminal.scrollTop = terminal.scrollHeight;
}

function digitarFilaDeLinhas(linhas, index) {
    if (index >= linhas.length) {
        destravarInput();
        return;
    }

    let linha = linhas[index];
    
    // 1. O Python mandou digitar numa velocidade específica (ex: Boot ou Frases de Tensão)
    if (linha.startsWith("@@TYPE@@")) {
        let parts = linha.split("@@");
        let cor = parts[2];
        let ms = parseInt(parts[3], 10);
        let texto = parts.slice(4).join("@@"); 
        
        digitarTextoAnimadoHTML(texto, cor, ms, () => {
            setTimeout(() => { digitarFilaDeLinhas(linhas, index + 1); }, 150);
        });
    } else {
        // 2. É um Print Normal do Python (HUD, Ações, Mapa, Artes)
        
        // Limpa as tags HTML mentalmente para avaliar o texto
        let textoPuro = linha.replace(/<[^>]*>?/gm, '');
        
        // Identifica se é Arte ASCII ou barras de separação do HUD
        let heArte = textoPuro.startsWith("  ") || textoPuro.startsWith("==") || textoPuro.startsWith("--") || textoPuro.startsWith("__") || textoPuro.startsWith("\\");
        
        if (heArte || textoPuro === "") {
            // Imprime artes instantaneamente para não distorcer!
            adicionarLinhaInstantaneaHTML(linha);
            setTimeout(() => {
                digitarFilaDeLinhas(linhas, index + 1);
            }, 10); 
        } else {
            // ANIMA TODO O RESTO! Textos normais e o HUD agora são digitados a 15ms por letra!
            digitarTextoAnimadoHTML(linha, 'verde', 15, () => {
                // Dá um respiro de 80ms antes de ir para a próxima linha
                setTimeout(() => {
                    digitarFilaDeLinhas(linhas, index + 1);
                }, 80); 
            });
        }
    }
}

// A Máquina de Escrever capaz de ler HTML sem quebrar as cores!
function digitarTextoAnimadoHTML(htmlString, classeCor, velocidade, aoTerminar) {
    const p = document.createElement('p');
    p.className = classeCor;
    outputDiv.appendChild(p);
    
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
            
            // Pula a lentidão instantaneamente se for um código HTML de cor (<span class="verde">)
            if (isTag || htmlString.charAt(i) === '<') {
                digitar(); 
            } else {
                setTimeout(digitar, velocidade); // Pausa apenas nas letras lidas pelo jogador
            }
        } else {
            aoTerminar(); 
        }
    }
    digitar();
}