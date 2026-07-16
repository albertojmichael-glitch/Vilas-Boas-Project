import os
from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
import sys
import io
import re
import random
import uuid

from state import GameState, registrar_final, carregar_conquistas, salvar_autosave, carregar_autosave, AUTOSAVE_FILE
from commands import processar_comando, normalizar
from minigames import MinigameMinotauro, MinigameSeguranca
from main import atualizar_eventos_de_tempo
from data import ARTE_PORCO, ARTE_ROBO, ARTE_PIANO, CAVEIRA_MORTE, MAX_INVENTARIO
from ui import DOS_VERDE, DOS_BRANCO, DOS_AMARELO, DOS_VERMELHO, RESET, UIHandler

ARTE_COFRE = r'''                                                                              
       .-----:-:--:-:-:::--:::::::::::-:::-::::::-::-------:::-:------::        
      :--:::::::::::-::::::::::::::::::::::::::::::::::::::::::::::::::--.      
    .------------------------:-::--::--:::::::::::::::::::::::::::::::::::.     
    ***********************************************************************.    
    *********************************************************************** ******%%#%#%%%%%%%%%%%%%%%%%%%%%#%###############################****** *****%***********************************************************%***** *****#***********************************************************%***** *****#***********************************************************%***** *****#*********:=*************##########*#####*******************%***** +****#*********+***=+*********##+--**=+*#**###*******************%***** +****#*******%%###%##*+***++**##::-++-:-+:=+##*******************%***** +****#****#%###%%%%#%#*=*+:.**##===++==**==*##*******************%***** +****#****%#######%##%#=++:--*##:=-++-=+-=-+##*******************%***** +****#****#######%###%#***-:+*##===**+*#***###*******************%****+     
    +****#****####%#%%####********##:::+=++*:::+##*******************%****+     
    +****#******#####%##**********##===*+==*+==*##*******************#****+     
    +****#************************##::=+-+=#:==+##*******************#****+     
    *****#************************###############********************#****+     
    +****#****+==****************************************************#****+     
    +****##**:--=++*======+******************************************#****+     
    +****##*********************************************************##****+     
    +******#########################################%%%%%%%%%%%%%%%%%=****+     
    +*********************************************************************+     
    +*********************************************************************+'''

class WebUIHandler(UIHandler):
    """Adaptador que transforma os prints do Python em Comandos JSON para o Frontend."""
    def limpar(self):
        print("@@CLEAR@@")
    
    def pausar(self, segs):
        pass # A web gerencia o timing pelo JSON
        
    def exibir(self, texto):
        print(texto)
        
    def animar(self, texto, tempo=0.03, cor="", jogo=None):
        cor_nome = "verde"
        if cor == DOS_BRANCO: cor_nome = "branco"
        elif cor == DOS_AMARELO: cor_nome = "amarelo"
        elif cor == DOS_VERMELHO: cor_nome = "vermelho"
        
        # Modo rápido da UI
        if jogo and getattr(jogo, 'fast_mode', False): tempo = 0
            
        ms = int(tempo * 1000)
        print(f"@@TYPE@@{cor_nome}@@{ms}@@{texto}")
        
    def obter_input(self, prompt_text):
        return "" # A Web gerencia o input via botões na tela do Cofre

def ansi_para_html(texto_ansi):
    mapa_cores = {
        DOS_VERDE: "verde",
        DOS_BRANCO: "branco",
        DOS_AMARELO: "amarelo",
        DOS_VERMELHO: "vermelho",
    }
    padrao = re.compile("(" + "|".join(re.escape(c) for c in list(mapa_cores.keys()) + [RESET]) + ")")
    partes = padrao.split(texto_ansi)

    html = []
    aberto = False
    for parte in partes:
        if parte in mapa_cores:
            if aberto: html.append("</span>")
            html.append(f'<span class="{mapa_cores[parte]}">')
            aberto = True
        elif parte == RESET:
            if aberto:
                html.append("</span>")
                aberto = False
        else:
            html.append(parte)
    if aberto: html.append("</span>")
    return "".join(html)

app = Flask(__name__, static_folder=".", static_url_path="")

# Chave protegida para produção
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "villas-boas-1982-seguranca")
CORS(app, supports_credentials=True)

partidas = {}

def obter_estado():
    sid = session.get("sid")
    if not sid or sid not in partidas:
        sid = str(uuid.uuid4())
        session["sid"] = sid
        partidas[sid] = GameState(ui_handler=WebUIHandler())
    
    jogo = partidas[sid]
    # Garante que o WebUI esteja ativo para essa sessão!
    if not isinstance(jogo.ui_handler, WebUIHandler):
        jogo.ui_handler = WebUIHandler()
    return jogo

@app.route("/")
def raiz():
    return send_from_directory(".", "index.html")

def imprimir_tela_boot(ui_handler):
    ui_handler.animar("VILLAS-BOAS INDUSTRIES (C) 1982", 0.01, DOS_BRANCO)
    ui_handler.animar("BIOS VERSION 1.04 - RELEASE 02/11/1982", 0.01, DOS_BRANCO)
    ui_handler.animar("RAM CHECK: 640KB OK", 0.01, DOS_VERDE)
    ui_handler.animar("DRIVE A: READY", 0.01, DOS_VERDE)
    ui_handler.animar("CARREGANDO 'COMMAND.COM'....... OK\n", 0.05, DOS_VERDE)
    ui_handler.exibir(f"{DOS_VERDE}Digite {DOS_BRANCO}dir{DOS_VERDE} para acessar os diretórios:{RESET}")

def imprimir_menu_dificuldade(ui_handler):
    ui_handler.animar("==================================================", 0.005, DOS_VERDE)
    ui_handler.animar("__     _____ _     _        _ ____   ___   ____ ", 0.005, DOS_VERDE)
    ui_handler.animar("\\ \\   / /_ _| |   | |      / / ___| / _ \\ / ___|", 0.005, DOS_VERDE)
    ui_handler.animar(" \\ \\ / / | || |   | |     / /\\___ \\| | | |\\___ \\", 0.005, DOS_VERDE)
    ui_handler.animar("  \\ V /  | || |___| |___ / /  ___) | |_| | ___) |", 0.005, DOS_VERDE)
    ui_handler.animar("   \\_/  |___|_____|_____/_/  |____/ \\___/ |____/", 0.005, DOS_VERDE)
    ui_handler.animar("==================================================", 0.005, DOS_VERDE)
    ui_handler.animar("        SISTEMA DE SEGURANÇA INTEGRADO v1.0       \n", 0.02, DOS_BRANCO)
    
    conquistas = carregar_conquistas()
    c_med = "[X]" if "mediocre" in conquistas else "[ ]"
    c_son = "[X]" if "bons_sonhos" in conquistas else "[ ]"
    c_bom = "[X]" if "bom" in conquistas else "[ ]"
    c_ver = "[X]" if "verdadeiro" in conquistas else "[ ]"
    qtd = len(set(conquistas) & {"mediocre", "bons_sonhos", "bom", "verdadeiro"})

    ui_handler.exibir(f"{DOS_AMARELO}🏆 FINAIS ALCANÇADOS: {qtd}/4{RESET}")
    ui_handler.exibir(f"{DOS_BRANCO}{c_med} Medíocre  {c_son} Bons Sonhos  {c_bom} Bom  {c_ver} Verdadeiro{RESET}\n")
    
    ui_handler.exibir(f"{DOS_BRANCO}[1] INICIAR MODO: NORMAL (Para iniciantes){RESET}")
    ui_handler.exibir(f"{DOS_VERMELHO}[2] INICIAR MODO: PESADELO (RNG Agressivo / HP Baixo){RESET}")
    ui_handler.exibir(f"{DOS_AMARELO}[3] INICIAR MODO: RÁPIDO (Skip Delays de Digitação){RESET}")
    
    if AUTOSAVE_FILE.exists():
        ui_handler.exibir(f"{DOS_VERDE}[4] CONTINUAR JOGO (Autosave Encontrado){RESET}\n")
        ui_handler.exibir(f"{DOS_VERDE}SELECIONE UMA OPÇÃO (1-4): {RESET}")
    else:
        ui_handler.exibir(f"\n{DOS_VERDE}SELECIONE UMA OPÇÃO (1-3): {RESET}")

def imprimir_tutorial(ui_handler):
    ui_handler.exibir(f"\n{DOS_AMARELO}--- DICAS DE SOBREVIVÊNCIA (TUTORIAL) ---{RESET}")
    ui_handler.exibir(f"{DOS_BRANCO}1. Mova-se digitando {DOS_VERDE}ir frente{DOS_BRANCO}, ou apenas o nome da sala (Ex: {DOS_VERDE}sala de jantar{DOS_BRANCO}).{RESET}")
    ui_handler.exibir(f"{DOS_BRANCO}2. Interaja com objetos digitando {DOS_VERDE}pegar [item]{DOS_BRANCO} ou {DOS_VERDE}examinar [item]{DOS_BRANCO}.{RESET}")
    ui_handler.exibir(f"{DOS_BRANCO}3. Você pode encurtar comandos usando {DOS_VERDE}p chave{DOS_BRANCO} em vez de {DOS_VERDE}pegar chave{DOS_BRANCO}.{RESET}")
    ui_handler.exibir(f"{DOS_BRANCO}4. Digite {DOS_VERDE}ajuda{DOS_BRANCO} a qualquer momento para ver o manual do sistema.{RESET}")
    ui_handler.exibir(f"{DOS_AMARELO}-----------------------------------------{RESET}\n")

def dar_dica_jon(passo_certo, ui_handler):
    dicas = {
        "f": "Uma corrente de ar gelado bate direto no seu rosto.",
        "e": "Um som agudo de metal arranhando reverbera pela parede canhota do duto.",
        "d": "O cheiro podre de carne estragada fica mais forte no caminho destro."
    }
    if random.random() <= 0.25:
        ui_handler.exibir(f"\n{DOS_VERMELHO}[SENSÓRIO CONFUSO]: {random.choice([v for k, v in dicas.items() if k != passo_certo])}{RESET}")
    else:
        ui_handler.exibir(f"\n{DOS_AMARELO}[SENSÓRIO]: {dicas[passo_certo]}{RESET}")

def falar_pianista(acertou, ui_handler):
    if acertou:
        ui_handler.exibir(f"{DOS_BRANCO}A máquina toca uma nota suave e agradável.{RESET}")
        ui_handler.animar(f'"{random.choice(["Você lembra bem, Rogério. Isso é bom.", "O ritmo continua. Você ainda tem ouvido para isso.", "Correto. Ele sempre soube que você voltaria.", "Sim... exatamente como aconteceu."])}"', 0.04, DOS_AMARELO)
    else:
        ui_handler.exibir(f"{DOS_VERMELHO}Acorde dissonante.{RESET}")
        ui_handler.animar(f'"{random.choice(["Errado. As teclas pretas não perdoam mentiras.", "Você deveria lembrar melhor do que isso, Rogério.", "Uma nota fora do lugar... como você, aquela noite.", "Isso não é o que consta no registro do restaurante."])}"', 0.04, DOS_AMARELO)

def imprimir_contexto_sala(jogo):
    if jogo.estado_atual == "COMBATE_ANIMATRONICO": return
    ui_handler = jogo.ui_handler
    
    if not jogo.minigame_atual and jogo.sala_atual not in ["morte", "saida", "cama", "final_bom"]:
        sala = jogo.mapa[jogo.sala_atual]
        ui_handler.exibir("\n" + "="*50)
        ui_handler.exibir(f"📍 VOCÊ ESTÁ EM: {jogo.sala_atual.upper()}")
        
        descricao_colorida = sala['descrição']
        for inspecionavel in sala.get("inspecionaveis", {}):
            descricao_colorida = descricao_colorida.replace(inspecionavel, f"{DOS_AMARELO}{inspecionavel}{RESET}")
        for item in sala.get("itens", []):
            descricao_colorida = descricao_colorida.replace(item, f"{DOS_VERDE}{item}{RESET}")
            
        ui_handler.exibir(f"👁️  Visão: {descricao_colorida}")

        if len(sala.get("itens", [])) > 0:
            if jogo.turnos_luz > 0:
                itens_formatados = [f"{DOS_VERDE}{item}{RESET}" for item in sala['itens']]
                ui_handler.exibir(f"📦 Itens no chão: {', '.join(itens_formatados)}")
            else:
                ui_handler.exibir(f"📦 {DOS_BRANCO}Deve ter algo no chão, mas escuro demais para ver o quê.{RESET}")

        chaves_ignoradas = ["descrição", "itens", "inspecionaveis", "cofre_important", "cadeira"]
        saidas = [k for k in sala.keys() if k not in chaves_ignoradas and isinstance(sala[k], str)]
        if saidas:
            ui_handler.exibir(f"🧭 Saídas: {DOS_AMARELO}{', '.join(saidas).title()}{RESET}")
        else:
            ui_handler.exibir(f"🧭 Saídas: {DOS_VERMELHO}Nenhuma saída aparente...{RESET}")

        ui_handler.exibir(f"\n{DOS_BRANCO}[ SISTEMA OPERACIONAL VILLAS BOAS v20.08 ]{RESET}")
        
        vida_visual = "9999" if jogo.god_mode else f"{jogo.hp}/3"
        luz_visual = "9999" if jogo.god_mode else str(jogo.turnos_luz)
        inv_visual = "∞" if jogo.god_mode else f"{len(jogo.inventario)}/{MAX_INVENTARIO}"
        ui_handler.exibir(f"{DOS_BRANCO}[ HP: {DOS_VERMELHO}{vida_visual}{DOS_BRANCO} | LUZ: {DOS_AMARELO}{luz_visual}{DOS_BRANCO} | INV: {inv_visual} ]{RESET}")

def dar_tela_de_morte(jogo):
    jogo.estado_atual = "FIM"
    ui = jogo.ui_handler
    ui.exibir(f"{DOS_VERMELHO}{CAVEIRA_MORTE}{RESET}")
    ui.animar("💀 GAME OVER. A NOITE ENGOLIU VOCÊ.", 0.05, DOS_VERMELHO, jogo)
    ui.animar("=== SISTEMA CORROMPIDO. APERTE F5 PARA REINICIAR ===", 0.05, DOS_AMARELO, jogo)

def rodar_final_web(tipo_final, jogo):
    jogo.estado_atual = "FIM"
    ui = jogo.ui_handler
    ui.limpar()
    
    liberou_deus = False
    
    if tipo_final == "saida":
        ui.animar("[ FINAL MEDÍOCRE ]", 0.05, DOS_VERDE, jogo)
        liberou_deus = registrar_final("mediocre")
        
    elif tipo_final == "cama":
        ui.animar("[ FINAL BONS SONHOS ]", 0.05, DOS_BRANCO, jogo)
        liberou_deus = registrar_final("bons_sonhos")
        
    elif tipo_final == "final_bom":
        ui.animar("Voce acende o isqueiro e ilumina o local. A luz do fogo traz calma...", 0.04, DOS_VERDE, jogo)
        ui.animar("- Por que não deu certo? O que eu fiz de errado?", 0.05, DOS_AMARELO, jogo)
        ui.animar("- 'Ainda estou aqui...'", 0.09, DOS_VERMELHO, jogo)
        ui.animar("- Amor? É voce? Mesmo???", 0.05, DOS_AMARELO, jogo)
        ui.animar("- 'Eu espero que ainda seja eu...'", 0.09, DOS_VERMELHO, jogo)
        ui.animar("- Caroline... desista desse corpo que não lhe pertence. Siga o rumo das estrelas.", 0.05, DOS_AMARELO, jogo)
        ui.animar("- ... *Caroline abraça Rogério*", 0.09, DOS_VERMELHO, jogo)
        ui.animar("- 'Vamos nos encontrar no céu, meu bem.'", 0.09, DOS_VERMELHO, jogo)
        ui.exibir(f"\n{DOS_BRANCO}[ FINAL BOM ]{RESET}")
        liberou_deus = registrar_final("bom")
        
    elif tipo_final == "verdadeiro":
        ui.animar("Voce se aproxima do animatronico... dela. E encaixa os fios na sua fiação...", 0.05, DOS_BRANCO, jogo)
        ui.animar("Voce acende o isqueiro. Os olhos de plastico parecem te encarar.", 0.05, DOS_BRANCO, jogo)
        ui.animar("Os olhos piscam em vermelho, ela tenta fazer algo... mas não consegue.\n", 0.05, DOS_BRANCO, jogo)
        ui.animar("- Por que não deu certo? O que eu fiz de errado?", 0.05, DOS_AMARELO, jogo)
        ui.animar("- '... voce fez dar certo'", 0.08, DOS_VERMELHO, jogo)
        ui.animar("- Caro... Caroline? É você?", 0.05, DOS_AMARELO, jogo)
        ui.animar("*(Você abraça a carcaça de pelugem rosa)*", 0.04, DOS_BRANCO, jogo)
        ui.animar("- Meu corpo ficou em silencio, não sinto mais raiva.", 0.07, DOS_VERDE, jogo)
        ui.animar("*(O fogo se alastra pelo restaurante, a fumaça chega no hall)*", 0.04, DOS_BRANCO, jogo)
        ui.animar("- Me sinta pela ultima vez.", 0.07, DOS_VERDE, jogo)
        ui.animar("*(Voce sente mãos invisíveis em seus ombros, um alivio inunda sua mente)*", 0.04, DOS_BRANCO, jogo)
        ui.animar("- Obrigada por me deixar assim pela ultima vez.", 0.07, DOS_VERDE, jogo)
        ui.animar("- Eu te amo.", 0.06, DOS_AMARELO, jogo)
        ui.animar("*(O animatronico cai no chão, o fogo cobre o metal e o plástico)*", 0.05, DOS_BRANCO, jogo)
        ui.animar("\n[DISPOSITIVO]: NENHUMA PRESENÇA DETECTADA.", 0.05, DOS_VERDE, jogo)
        ui.animar("Você se levanta e caminha para a saída antes que o teto desabe.", 0.05, DOS_BRANCO, jogo)
        ui.exibir(f"\n{DOS_BRANCO}[ FINAL VERDADEIRO ]{RESET}")
        liberou_deus = registrar_final("verdadeiro")

    if liberou_deus:
        ui.exibir(f"\n{DOS_AMARELO}=================================================={RESET}")
        ui.animar(">>> MENSAGEM DO SISTEMA <<<", 0.05, DOS_VERMELHO, jogo)
        ui.animar("VOCÊ DESVENDOU TODAS AS VERDADES DESTA NOITE.", 0.05, DOS_VERMELHO, jogo)
        ui.animar("O CÓDIGO DE MANUTENÇÃO FOI LIBERADO.", 0.05, DOS_VERMELHO, jogo)
        ui.exibir(f"{DOS_AMARELO}DIGITE O ANO EM QUE TUDO ACABOU NA TELA DE MENU: {DOS_BRANCO}2007{RESET}")
        ui.exibir(f"{DOS_AMARELO}=================================================={RESET}")
        
    ui.animar("\n=== APERTE F5 PARA REINICIAR ===", 0.05, DOS_AMARELO, jogo)

@app.route('/iniciar', methods=['GET'])
def iniciar_jogo():
    sid = session.get("sid")
    if sid and sid in partidas:
        del partidas[sid]  
    jogo = obter_estado()
    jogo.estado_atual = "AGUARDANDO_DIR"
    
    captura = io.StringIO()
    sys.stdout = captura
    imprimir_tela_boot(jogo.ui_handler)
    sys.stdout = sys.__stdout__
    
    texto_html = ansi_para_html(captura.getvalue())
    return jsonify({"linhas": [l for l in texto_html.split('\n') if l.strip() != ""]})

@app.route('/comando', methods=['POST'])
def receber_comando():
    jogo = obter_estado()
    dados = request.json
    comando = normalizar(dados.get('comando', ''))
    ui = jogo.ui_handler

    captura = io.StringIO()
    stdout_original = sys.stdout
    sys.stdout = captura

    try:
        if jogo.estado_atual == "FIM":
            ui.exibir(f"{DOS_VERMELHO}[SISTEMA BLOQUEADO] - Aperte a tecla F5 no teclado para jogar novamente.{RESET}")

        elif jogo.estado_atual == "AGUARDANDO_DIR":
            if comando in ["cls", "limpar", "clear", "clean"]:
                ui.limpar()
                imprimir_tela_boot(ui)
            elif comando == "dir":
                ui.limpar()
                ui.exibir(f"{DOS_BRANCO} Volume in drive A is VILLASBOAS{RESET}")
                ui.exibir(f"{DOS_BRANCO} Directory of A:\\{RESET}\n")
                ui.exibir(f"{DOS_VERDE}COMMAND  COM          47.845  02-11-1982  6:00a{RESET}")
                ui.exibir(f"{DOS_VERDE}SEGURA   SYS           2.048  02-11-1982  6:00a{RESET}")
                ui.exibir(f"{DOS_VERDE}NOTURNO  EXE          18.204  02-11-1982  6:00a{RESET}")
                ui.exibir(f"{DOS_VERDE}DESKTOP  &lt;DIR&gt;        197.78  24-07-2007  4:00a{RESET}")
                ui.exibir(f"{DOS_VERDE}SAVES    &lt;DIR&gt;        358.21  23-07-2008  4:00a{RESET}")
                ui.exibir(f"{DOS_VERDE}PICTURE  &lt;DIR&gt;        666.00  05-11-1994  4:00a{RESET}")
                ui.exibir(f"{DOS_VERDE}VALID    &lt;DIR&gt;        2.7801  24-07-2007  4:00a{RESET}")
                ui.exibir(f"{DOS_AMARELO}       3 file(s)        68.097 bytes{RESET}")
                ui.exibir(f"{DOS_AMARELO}       4 dir(s)        655.360 bytes free{RESET}\n")
                jogo.estado_atual = "MENU"
                imprimir_menu_dificuldade(ui)
            else:
                ui.exibir(f"{DOS_VERMELHO}Bad command or file name{RESET}")
                ui.exibir(f"{DOS_VERDE}Digite {DOS_BRANCO}dir{DOS_VERDE} para acessar os diretórios:{RESET}")

        elif jogo.estado_atual == "MENU":
            if comando in ["cls", "limpar", "clear", "clean"]:
                ui.limpar()
                imprimir_menu_dificuldade(ui)
            elif comando == "4" and AUTOSAVE_FILE.exists():
                ui.limpar()
                if carregar_autosave(jogo):
                    ui.exibir(f"{DOS_VERDE}JOGO RESTAURADO COM SUCESSO DO ÚLTIMO AUTOSAVE.{RESET}\n")
                    imprimir_contexto_sala(jogo)
                else:
                    ui.exibir(f"{DOS_VERMELHO}Falha ao ler o Autosave.{RESET}")
                    imprimir_menu_dificuldade(ui)
            elif comando in ["1", "2", "3"]:
                ui.limpar()
                if comando == "1":
                    jogo.dificuldade_escolhida = "NORMAL"
                    jogo.hp = 3; jogo.furia_noite = 1; jogo.energia_min_noite = 100; jogo.energia_max_noite = 100
                    ui.exibir(f"{DOS_VERDE}MODO NORMAL SELECIONADO. INICIANDO JOGO.EXE...{RESET}\n")
                elif comando == "2":
                    jogo.dificuldade_escolhida = "PESADELO"
                    jogo.hp = 2; jogo.furia_noite = 2; jogo.energia_min_noite = 70; jogo.energia_max_noite = 82
                    ui.exibir(f"{DOS_VERMELHO}MODO PESADELO SELECIONADO. BOA SORTE.{RESET}\n")
                elif comando == "3":
                    jogo.dificuldade_escolhida = "NORMAL"
                    jogo.fast_mode = True
                    jogo.hp = 3; jogo.furia_noite = 1; jogo.energia_min_noite = 100; jogo.energia_max_noite = 100
                    ui.exibir(f"{DOS_AMARELO}MODO RÁPIDO SELECIONADO. DELAYS DE DIGITAÇÃO DESATIVADOS.{RESET}\n")

                jogo.estado_atual = "JOGO"
                imprimir_tutorial(ui)
                ui.exibir(f"{DOS_BRANCO}Você entra no restaurante. Sua lanterna velha dá três piscadas fracas...{RESET}")
                ui.exibir(f"{DOS_AMARELO}[AVISO DO SISTEMA]: BATERIA DA LANTERNA EM 5%. PROCURAR OUTRA FONTE DE LUZ EM ATÉ 3 TURNOS.{RESET}")
                imprimir_contexto_sala(jogo)

            elif comando == "2007":
                ui.limpar()
                jogo.dificuldade_escolhida = "GOD MODE"
                jogo.god_mode = True
                jogo.fast_mode = True
                jogo.hp = 9999
                jogo.furia_noite = 0
                jogo.energia_min_noite = 9999
                jogo.energia_max_noite = 9999
                jogo.turnos_luz = 9999
                jogo.estado_atual = "JOGO"
                ui.exibir(f"{DOS_AMARELO}MODO DEUS ATIVADO. ACESSO AOS BASTIDORES CONCEDIDO.{RESET}\n")
                ui.exibir(f"{DOS_BRANCO}Você entra no restaurante. Sua lanterna brilha com a força de uma estrela...{RESET}")
                imprimir_contexto_sala(jogo)
            else:
                ui.exibir(f"{DOS_VERMELHO}OPÇÃO INVÁLIDA. DIGITE UMA OPÇÃO DO MENU.{RESET}")

        elif jogo.estado_atual in ["JOGO", "COMBATE_ANIMATRONICO"]:
            if comando in ["cls", "limpar", "clear", "clean"]:
                ui.limpar()
                imprimir_contexto_sala(jogo)
            elif jogo.sala_atual == "sala de energia" and not jogo.fios_cortados_inventario:
                jogo.minigame_atual = MinigameMinotauro(jogo)
                jogo.estado_atual = "MINIGAME_MINOTAURO"
                jogo.minigame_atual.imprimir_status()
            elif jogo.sala_atual == "cadeira" and not jogo.noite_vencida:
                jogo.minigame_atual = MinigameSeguranca(jogo)
                jogo.estado_atual = "MINIGAME_SEGURANCA"
                jogo.minigame_atual.imprimir_status()
            elif comando == "abrir cofre" and jogo.sala_atual == "01":
                jogo.estado_atual = "MINIGAME_COFRE"
                ui.exibir(f"{DOS_BRANCO}{ARTE_COFRE}{RESET}")
                ui.exibir(f"{DOS_BRANCO}O cofre de ferro possui um teclado numérico antigo.{RESET}")
                ui.exibir(f"{DOS_VERDE}Digite a senha de 4 dígitos: {RESET}")
            elif (comando == "jogar jon" or comando == "jogar fome de jon") and jogo.sala_atual == "sala de fliperamas":
                jogo.estado_atual = "MINIGAME_JON"
                jogo.jon_passos_dados = 0
                jogo.jon_caminho_certo = [random.choice(["f", "e", "d"]) for _ in range(4)]
                ui.limpar()
                ui.exibir(f"{DOS_BRANCO}{ARTE_PORCO}{RESET}")
                ui.animar("--- A FOME DE JON ---", 0.03, DOS_VERDE, jogo)
                ui.exibir(f"{DOS_BRANCO}Guie o Porco Jon pelos dutos baseando-se nos seus sentidos.{RESET}")
                ui.exibir("Comandos: [F] Frente | [E] Esquerda | [D] Direita")
                dar_dica_jon(jogo.jon_caminho_certo[0], ui)
                ui.exibir(f"Passo 1/4 - Direção (F/E/D): ")
            elif comando == "jogar consertos" and jogo.sala_atual == "sala de fliperamas":
                if "moeda velha" not in jogo.inventario:
                    ui.exibir("A máquina 'Consertos & Sorrisos' exige uma ficha (moeda velha) para iniciar.")
                else:
                    jogo.inventario.remove("moeda velha")
                    jogo.estado_atual = "MINIGAME_CONSERTOS_CABECA"
                    jogo.web_consertos = {}
                    ui.limpar()
                    ui.exibir(f"{DOS_BRANCO}{ARTE_ROBO}{RESET}")
                    ui.animar("--- CONSERTOS & SORRISOS ---", 0.03, DOS_VERDE, jogo)
                    ui.exibir("Bem-vindo, Mecânico! Vamos montar nosso novo Festeiro!")
                    ui.exibir(f"\n{DOS_AMARELO}[ FASE 1: SELEÇÃO DE PEÇAS ]{RESET}")
                    ui.exibir("Escolha a Cabeça (1- Urso | 2- Coelho): ")
            elif (comando == "jogar adivinha" or comando == "jogar julgamento") and jogo.sala_atual == "sala de fliperamas":
                jogo.estado_atual = "MINIGAME_JULGAMENTO_Q1"
                jogo.web_julgamento = {"pontos": 0, "vitimas": ["angela", "joao", "renato"]}
                ui.limpar()
                ui.exibir(f"{DOS_BRANCO}{ARTE_PIANO}{RESET}")
                ui.animar("--- O JULGAMENTO DO PIANISTA ---", 0.03, DOS_VERDE, jogo)
                ui.exibir(f"{DOS_BRANCO}O animatrônico desperta. Ele detém todas as respostas.{RESET}")
                ui.exibir(f"\n{DOS_AMARELO}PERGUNTA 1: Em que ano a nossa música parou para sempre?{RESET}")
            elif comando in ["salvar", "carregar"]:
                ui.limpar()
                ui.exibir(f"{DOS_AMARELO}>>> MENSAGEM DO SISTEMA: O drive de disquete virtual está offline.{RESET}")
                ui.exibir(f"{DOS_AMARELO}Na versão Web, o progresso salva a cada turno automaticamente.{RESET}")
                imprimir_contexto_sala(jogo)
            else:
                gastou_turno = processar_comando(comando, jogo, jogo.mapa)
                if gastou_turno: atualizar_eventos_de_tempo(jogo)
                
                if jogo.sala_atual == "morte":
                    dar_tela_de_morte(jogo)
                elif jogo.sala_atual == "saida":
                    rodar_final_web("saida", jogo)
                elif jogo.sala_atual == "cama":
                    rodar_final_web("cama", jogo)
                elif jogo.sala_atual == "hall de entrada" and getattr(jogo, 'noite_vencida', False):
                    if getattr(jogo, 'incendio', False):
                        rodar_final_web("verdadeiro", jogo)
                    else:
                        rodar_final_web("final_bom", jogo)
                elif jogo.estado_atual == "COMBATE_ANIMATRONICO":
                    pass 
                else:
                    imprimir_contexto_sala(jogo)

        elif jogo.estado_atual == "MINIGAME_COFRE":
            if comando in ["cls", "limpar", "clear", "clean"]:
                ui.limpar()
                ui.exibir(f"{DOS_BRANCO}{ARTE_COFRE}{RESET}")
                ui.exibir(f"{DOS_VERDE}Digite a senha de 4 dígitos: {RESET}")
            elif comando == "1994": 
                ui.exibir(f"{DOS_VERDE}CLICK! A pesada porta de metal se abre.{RESET}")
                sala = jogo.mapa[jogo.sala_atual]
                if "itens" not in sala: sala["itens"] = []
                
                if "chave dos fundos" not in jogo.inventario and "chave dos fundos" not in sala["itens"]:
                    if len(jogo.inventario) < MAX_INVENTARIO or getattr(jogo, 'god_mode', False):
                        ui.exibir(f"{DOS_AMARELO}Você encontrou a 'chave dos fundos' suja de graxa lá dentro!{RESET}")
                        jogo.inventario.append("chave dos fundos")
                    else:
                        ui.exibir(f"{DOS_AMARELO}Sua mochila está cheia! A 'chave dos fundos' caiu no chão da sala.{RESET}")
                        sala["itens"].append("chave dos fundos")
                else:
                    ui.exibir("O cofre está vazio. Apenas poeira.")
                jogo.estado_atual = "JOGO"
                imprimir_contexto_sala(jogo)
            else:
                ui.exibir(f"{DOS_VERMELHO}BEEP! Senha incorreta. Painel pisca em vermelho.{RESET}")
                jogo.estado_atual = "JOGO"
                imprimir_contexto_sala(jogo)

        elif jogo.estado_atual == "MINIGAME_JON":
            passo = jogo.jon_passos_dados
            if comando in ["cls", "limpar", "clear", "clean"]:
                ui.limpar()
                ui.exibir(f"{DOS_BRANCO}{ARTE_PORCO}{RESET}")
                ui.exibir(f"Passo {passo + 1}/4 - Direção (F/E/D): ")
            elif comando in ["f", "e", "d", "frente", "esquerda", "direita"]:
                letra = comando[0]
                if letra == jogo.jon_caminho_certo[passo]:
                    ui.exibir(f"{DOS_BRANCO}Jon rasteja em silêncio pelos dutos...{RESET}")
                    jogo.jon_passos_dados += 1
                    if jogo.jon_passos_dados == 4:
                        ui.exibir(f"\n{DOS_VERDE}Jon encontrou a 'comida'. A tela pinga um pixel vermelho.{RESET}")
                        ui.exibir(f"{DOS_VERMELHO}MENSAGEM: 'Eles não saíram pela porta da frente em 94.'{RESET}")
                        jogo.turnos_luz = max(0, jogo.turnos_luz - 1)
                        jogo.estado_atual = "JOGO"
                        imprimir_contexto_sala(jogo)
                    else:
                        dar_dica_jon(jogo.jon_caminho_certo[jogo.jon_passos_dados], ui)
                        ui.exibir(f"Passo {jogo.jon_passos_dados + 1}/4 - Direção (F/E/D): ")
                else:
                    ui.exibir(f"\n{DOS_VERMELHO}CRUNCH! Jon caiu num triturador ativo! leva um choque brutal!{RESET}")
                    jogo.hp -= 1
                    jogo.turnos_luz = max(0, jogo.turnos_luz - 1)
                    if jogo.hp <= 0:
                        dar_tela_de_morte(jogo)
                    else:
                        jogo.estado_atual = "JOGO"
                        imprimir_contexto_sala(jogo)
            else:
                ui.exibir("Direção inválida. Use F, E ou D.")

        elif jogo.estado_atual == "MINIGAME_CONSERTOS_CABECA":
            jogo.web_consertos["cabeca"] = comando
            jogo.estado_atual = "MINIGAME_CONSERTOS_TRONCO"
            ui.exibir("Escolha o Tronco (1- Fino | 2- Robusto): ")

        elif jogo.estado_atual == "MINIGAME_CONSERTOS_TRONCO":
            jogo.web_consertos["tronco"] = comando
            jogo.estado_atual = "MINIGAME_CONSERTOS_PERNAS"
            ui.exibir("Escolha as Pernas (1- Aço | 2- Pelúcia): ")

        elif jogo.estado_atual == "MINIGAME_CONSERTOS_PERNAS":
            cabeca = jogo.web_consertos.get("cabeca", "1")
            tronco = jogo.web_consertos.get("tronco", "1")
            pernas = comando
            item_secreto = None
            
            if cabeca == "2" and pernas == "2":
                ui.exibir("> AVISO: Peças incompatíveis. Anomalia detectada.")
                item_secreto = "remedio"
            elif cabeca == "1" and tronco == "2":
                ui.exibir("> Encaixando peças do modelo padrão 'Urso Robusto'...")
            else:
                ui.exibir("> Erro de harmonia visual. Soldando peças à força...")
                
            ui.exibir(f"\n{DOS_VERDE}CONSERTO CONCLUÍDO! O ANIMATRÔNICO SORRI PARA VOCÊ!{RESET}")
            sala = jogo.mapa[jogo.sala_atual]
            if "itens" not in sala: sala["itens"] = []
            
            if "chave da cozinha" not in jogo.inventario and "chave da cozinha" not in sala["itens"]:
                ui.exibir(f"{DOS_BRANCO}A gaveta principal de prêmios se abre com um barulho metálico.{RESET}")
                if len(jogo.inventario) < MAX_INVENTARIO or getattr(jogo, 'god_mode', False):
                    jogo.inventario.append("chave da cozinha")
                    ui.exibir(f"{DOS_VERDE}🎒 Você obteve: CHAVE DA COZINHA!{RESET}")
                else:
                    ui.exibir(f"{DOS_AMARELO}🎒 Sua mochila está cheia! A CHAVE DA COZINHA caiu no chão.{RESET}")
                    sala["itens"].append("chave da cozinha")

            if item_secreto:
                ui.exibir(f"{DOS_BRANCO}Um compartimento de emergência se abriu na base da máquina!{RESET}")
                if len(jogo.inventario) < MAX_INVENTARIO or getattr(jogo, 'god_mode', False):
                    jogo.inventario.append(item_secreto)
                    ui.exibir(f"{DOS_VERDE}🎒 Você obteve um item extra: {item_secreto.upper()}!{RESET}")
                else:
                    ui.exibir(f"{DOS_AMARELO}🎒 Sua mochila está cheia! O item {item_secreto.upper()} caiu no chão.{RESET}")
                    sala["itens"].append(item_secreto)
                
            jogo.turnos_luz = max(0, jogo.turnos_luz - 1)
            jogo.estado_atual = "JOGO"
            imprimir_contexto_sala(jogo)

        elif jogo.estado_atual == "MINIGAME_JULGAMENTO_Q1":
            if comando == "1994": jogo.web_julgamento["pontos"] += 1; falar_pianista(True, ui)
            else: falar_pianista(False, ui)
            jogo.estado_atual = "MINIGAME_JULGAMENTO_Q2"
            ui.exibir(f"\n{DOS_AMARELO}PERGUNTA 2: Qual animatrônico está atrás de você agora?{RESET}")

        elif jogo.estado_atual == "MINIGAME_JULGAMENTO_Q2":
            if "caroline" in comando or "ela" in comando: jogo.web_julgamento["pontos"] += 1; falar_pianista(True, ui)
            else: falar_pianista(False, ui)
            jogo.estado_atual = "MINIGAME_JULGAMENTO_Q3"
            ui.exibir(f"\n{DOS_AMARELO}PERGUNTA 3: Em que ano tudo isso começou?{RESET}")

        elif jogo.estado_atual == "MINIGAME_JULGAMENTO_Q3":
            if comando == "1982": jogo.web_julgamento["pontos"] += 1; falar_pianista(True, ui)
            else: falar_pianista(False, ui)
            jogo.estado_atual = "MINIGAME_JULGAMENTO_Q4"
            ui.exibir(f"\n{DOS_AMARELO}PERGUNTA 4: Quem é você?{RESET}")

        elif jogo.estado_atual == "MINIGAME_JULGAMENTO_Q4":
            if "rogerio" in comando: jogo.web_julgamento["pontos"] += 1; falar_pianista(True, ui)
            else: falar_pianista(False, ui)
            jogo.estado_atual = "MINIGAME_JULGAMENTO_V1"
            ui.exibir(f"\n{DOS_AMARELO}PERGUNTA 5: Quem são as três vítimas? Digite o 1º nome:{RESET}")

        elif jogo.estado_atual in ["MINIGAME_JULGAMENTO_V1", "MINIGAME_JULGAMENTO_V2", "MINIGAME_JULGAMENTO_V3"]:
            acertou = False
            for v in jogo.web_julgamento["vitimas"][:]:
                if v in comando:
                    jogo.web_julgamento["vitimas"].remove(v)
                    acertou = True
            
            if acertou: falar_pianista(True, ui)
            else: falar_pianista(False, ui)
            
            if jogo.estado_atual == "MINIGAME_JULGAMENTO_V1":
                jogo.estado_atual = "MINIGAME_JULGAMENTO_V2"
                ui.exibir("Digite o 2º nome: ")
            elif jogo.estado_atual == "MINIGAME_JULGAMENTO_V2":
                jogo.estado_atual = "MINIGAME_JULGAMENTO_V3"
                ui.exibir("Digite o 3º nome: ")
            else:
                if len(jogo.web_julgamento["vitimas"]) == 0:
                    jogo.web_julgamento["pontos"] += 1
                if jogo.web_julgamento["pontos"] == 5:
                    ui.animar("Obrigado por voltar pela gente, Rogério...", 0.08, DOS_VERDE, jogo)
                    sala = jogo.mapa[jogo.sala_atual]
                    if "itens" not in sala: sala["itens"] = []
                    
                    if "bateria nova" not in jogo.inventario and "bateria nova" not in sala["itens"]:
                        ui.exibir(f"{DOS_BRANCO}A gaveta inferior abre com uma 'bateria nova'!{RESET}")
                        if len(jogo.inventario) < MAX_INVENTARIO or getattr(jogo, 'god_mode', False):
                            jogo.inventario.append("bateria nova")
                            ui.exibir(f"{DOS_VERDE}🎒 Você a guardou na mochila.{RESET}")
                        else:
                            ui.exibir(f"{DOS_AMARELO}🎒 Mochila cheia! A bateria nova caiu no chão.{RESET}")
                            sala["itens"].append("bateria nova")
                else:
                    ui.animar("Quem é você? A tela desliga. Você perdeu a absolvição.", 0.05, DOS_VERMELHO, jogo)
                    
                jogo.turnos_luz = max(0, jogo.turnos_luz - 1)
                jogo.estado_atual = "JOGO"
                imprimir_contexto_sala(jogo)

        elif jogo.estado_atual in ["MINIGAME_MINOTAURO", "MINIGAME_SEGURANCA"]:
            if comando in ["cls", "limpar", "clear", "clean"]:
                ui.limpar()
                jogo.minigame_atual.imprimir_status()
                
            elif comando in ["pular noite", "pular", "set time 06:00"] and getattr(jogo, 'god_mode', False) and jogo.estado_atual == "MINIGAME_SEGURANCA":
                ui.exibir(f"{DOS_AMARELO}[GOD MODE] Você altera os ponteiros do universo. O relógio salta para as 06:00 instantaneamente.{RESET}")
                jogo.minigame_atual.turno = 24 
                resultado = jogo.minigame_atual.processar_turno("esperar", jogo) 
                
                if resultado == "vitoria_seguranca":
                    jogo.minigame_atual = None
                    jogo.sala_atual = "01"
                    jogo.estado_atual = "JOGO"
                    ui.exibir(f"{DOS_VERDE}Você sobreviveu ao evento! Voltando ao sistema principal...{RESET}")
                    imprimir_contexto_sala(jogo)

            elif comando in ["atacar", "bater", "chutar", "lutar"] and getattr(jogo, 'god_mode', False) and jogo.estado_atual == "MINIGAME_MINOTAURO":
                ui.exibir(f"{DOS_AMARELO}[GOD MODE] Você corre na direção do Minotauro e dá uma voadora com os dois pés no peito dele!{RESET}")
                ui.exibir(f"{DOS_AMARELO}A fera despenca para trás, choraminga em som de estática e foge rompendo as paredes.{RESET}")
                jogo.minigame_atual = None
                jogo.sala_atual = "sala dos fundos"
                jogo.estado_atual = "JOGO"
                ui.exibir(f"{DOS_VERDE}Você sobreviveu ao evento! Voltando ao sistema principal...{RESET}")
                imprimir_contexto_sala(jogo)
                
            else:
                mapa_direcoes = {
                    "f": "ir frente", "frente": "ir frente",
                    "t": "ir atrás", "tras": "ir atrás", "atras": "ir atrás", "atrás": "ir atrás",
                    "e": "ir esquerda", "esquerda": "ir esquerda",
                    "d": "ir direita", "direita": "ir direita"
                }
                if comando in mapa_direcoes:
                    comando = mapa_direcoes[comando]
                
                resultado = jogo.minigame_atual.processar_turno(comando, jogo)
                
                if resultado == "morte":
                    jogo.minigame_atual = None
                    jogo.sala_atual = "morte"
                    dar_tela_de_morte(jogo)

                elif resultado == "vitoria_minotauro":
                    jogo.minigame_atual = None
                    jogo.sala_atual = "sala dos fundos" 
                    jogo.estado_atual = "JOGO"
                    jogo.mapa["sala dos fundos"]["energia"] = "A pesada porta da sala de energia está totalmente destruída e bloqueada pelos destroços."
                    ui.exibir(f"{DOS_VERDE}Você escapou da Sala de Energia com os fios! A porta cedeu atrás de você e travou para sempre.{RESET}")
                    imprimir_contexto_sala(jogo)

                elif resultado == "vitoria_seguranca":
                    jogo.minigame_atual = None
                    jogo.sala_atual = "01" 
                    jogo.estado_atual = "JOGO"
                    ui.exibir(f"{DOS_VERDE}Você sobreviveu à noite! Se levantando da cadeira...{RESET}")
                    imprimir_contexto_sala(jogo)
                else:
                    jogo.minigame_atual.imprimir_status()
        
        if getattr(jogo, 'god_mode', False):
            jogo.hp = 9999
            jogo.turnos_luz = 9999
            if jogo.minigame_atual:
                if isinstance(jogo.minigame_atual, MinigameMinotauro):
                    jogo.minigame_atual.bateria = 9999
                elif isinstance(jogo.minigame_atual, MinigameSeguranca):
                    jogo.minigame_atual.energia = 9999
                    
        # --- SALVAMENTO INVISÍVEL A CADA AÇÃO ---
        if jogo.estado_atual in ["JOGO", "COMBATE_ANIMATRONICO"]:
            salvar_autosave(jogo)

    except Exception as e:
        ui.exibir(f"\n[ERRO DE SISTEMA]: {e}")
    finally:
        sys.stdout = stdout_original

    texto_html = ansi_para_html(captura.getvalue())
    return jsonify({"linhas": [linha for linha in texto_html.split('\n') if linha.strip() != ""]})

if __name__ == '__main__':
    app.run(debug=True, port=5000)