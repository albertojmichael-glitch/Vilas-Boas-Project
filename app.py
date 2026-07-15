from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
import sys
import io
import re
import random
import uuid

from state import GameState
from commands import processar_comando, normalizar
from main import atualizar_eventos_de_tempo
from minigames import MinigameMinotauro, MinigameSeguranca
from data import ARTE_PORCO, ARTE_ROBO, ARTE_PIANO, CAVEIRA_MORTE, MAX_INVENTARIO

import ui
import commands
import minigames
import main

ui.DEBUG_MODE = True 

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

def web_digitar(texto, tempo_base=0.03, cor="", jogo=None):
    cor_nome = "verde"
    if cor == ui.DOS_BRANCO: cor_nome = "branco"
    elif cor == ui.DOS_AMARELO: cor_nome = "amarelo"
    elif cor == ui.DOS_VERMELHO: cor_nome = "vermelho"
    
    ms = int(tempo_base * 1000)
    print(f"@@TYPE@@{cor_nome}@@{ms}@@{texto}")

ui.digitar = web_digitar
commands.digitar = web_digitar
minigames.digitar = web_digitar
main.digitar = web_digitar

def ansi_para_html(texto_ansi):
    mapa_cores = {
        ui.DOS_VERDE: "verde",
        ui.DOS_BRANCO: "branco",
        ui.DOS_AMARELO: "amarelo",
        ui.DOS_VERMELHO: "vermelho",
    }
    padrao = re.compile("(" + "|".join(re.escape(c) for c in list(mapa_cores.keys()) + [ui.RESET]) + ")")
    partes = padrao.split(texto_ansi)

    html = []
    aberto = False
    for parte in partes:
        if parte in mapa_cores:
            if aberto: html.append("</span>")
            html.append(f'<span class="{mapa_cores[parte]}">')
            aberto = True
        elif parte == ui.RESET:
            if aberto:
                html.append("</span>")
                aberto = False
        else:
            html.append(parte)
    if aberto: html.append("</span>")
    return "".join(html)

app = Flask(__name__, static_folder=".", static_url_path="")
app.secret_key = "villas-boas-1982-troque-essa-chave-em-producao"
CORS(app, supports_credentials=True)

partidas = {}

def obter_estado():
    global jogo
    sid = session.get("sid")
    if not sid or sid not in partidas:
        sid = str(uuid.uuid4())
        session["sid"] = sid
        partidas[sid] = GameState()
    jogo = partidas[sid]
    return jogo

jogo = GameState()

@app.route("/")
def raiz():
    return send_from_directory(".", "index.html")

def imprimir_tela_boot():
    ui.digitar("VILLAS-BOAS INDUSTRIES (C) 1982", 0.01, ui.DOS_BRANCO)
    ui.digitar("BIOS VERSION 1.04 - RELEASE 02/11/1982", 0.01, ui.DOS_BRANCO)
    ui.digitar("RAM CHECK: 640KB OK", 0.01, ui.DOS_VERDE)
    ui.digitar("DRIVE A: READY", 0.01, ui.DOS_VERDE)
    ui.digitar("CARREGANDO 'COMMAND.COM'....... OK\n", 0.05, ui.DOS_VERDE)
    print(f"{ui.DOS_VERDE}Digite {ui.DOS_BRANCO}dir{ui.DOS_VERDE} para acessar os diretórios:{ui.RESET}")

def imprimir_menu_dificuldade():
    ui.digitar("==================================================", 0.005, ui.DOS_VERDE)
    ui.digitar("__     _____ _     _        _ ____   ___   ____ ", 0.005, ui.DOS_VERDE)
    ui.digitar("\\ \\   / /_ _| |   | |      / / ___| / _ \\ / ___|", 0.005, ui.DOS_VERDE)
    ui.digitar(" \\ \\ / / | || |   | |     / /\\___ \\| | | |\\___ \\", 0.005, ui.DOS_VERDE)
    ui.digitar("  \\ V /  | || |___| |___ / /  ___) | |_| | ___) |", 0.005, ui.DOS_VERDE)
    ui.digitar("   \\_/  |___|_____|_____/_/  |____/ \\___/ |____/", 0.005, ui.DOS_VERDE)
    ui.digitar("==================================================", 0.005, ui.DOS_VERDE)
    ui.digitar("        SISTEMA DE SEGURANÇA INTEGRADO v1.0       \n", 0.02, ui.DOS_BRANCO)
    
    print(f"{ui.DOS_BRANCO}[1] INICIAR MODO: NORMAL (Para iniciantes){ui.RESET}")
    print(f"{ui.DOS_VERMELHO}[2] INICIAR MODO: PESADELO (RNG Agressivo / HP Baixo){ui.RESET}\n")
    print(f"{ui.DOS_VERDE}SELECIONE UMA OPÇÃO (1-2): {ui.RESET}")

def dar_dica_jon(passo_certo):
    dicas = {
        "f": "Uma corrente de ar gelado bate direto no seu rosto.",
        "e": "Um som agudo de metal arranhando reverbera pela parede canhota do duto.",
        "d": "O cheiro podre de carne estragada fica mais forte no caminho destro."
    }
    if random.random() <= 0.25:
        erradas = [v for k, v in dicas.items() if k != passo_certo]
        print(f"\n{ui.DOS_VERMELHO}[SENSÓRIO CONFUSO]: {random.choice(erradas)}{ui.RESET}")
    else:
        print(f"\n{ui.DOS_AMARELO}[SENSÓRIO]: {dicas[passo_certo]}{ui.RESET}")

FALAS_PIANISTA_CERTO = [
    "Você lembra bem, Rogério. Isso é bom.",
    "O ritmo continua. Você ainda tem ouvido para isso.",
    "Correto. Ele sempre soube que você voltaria.",
    "Sim... exatamente como aconteceu."
]
FALAS_PIANISTA_ERRADO = [
    "Errado. As teclas pretas não perdoam mentiras.",
    "Você deveria lembrar melhor do que isso, Rogério.",
    "Uma nota fora do lugar... como você, aquela noite.",
    "Isso não é o que consta no registro do restaurante."
]

def falar_pianista(acertou):
    if acertou:
        print(f"{ui.DOS_BRANCO}A máquina toca uma nota suave e agradável.{ui.RESET}")
        ui.digitar(f'"{random.choice(FALAS_PIANISTA_CERTO)}"', 0.04, ui.DOS_AMARELO)
    else:
        print(f"{ui.DOS_VERMELHO}Acorde dissonante.{ui.RESET}")
        ui.digitar(f'"{random.choice(FALAS_PIANISTA_ERRADO)}"', 0.04, ui.DOS_AMARELO)

def imprimir_contexto_sala():
    if not jogo.minigame_atual and jogo.sala_atual not in ["morte", "saida", "cama", "final_bom"]:
        sala = jogo.mapa[jogo.sala_atual]
        print("\n" + "="*50)
        print(f"📍 VOCÊ ESTÁ EM: {jogo.sala_atual.upper()}")
        
        descricao_colorida = sala['descrição']
        for inspecionavel in sala.get("inspecionaveis", {}):
            descricao_colorida = descricao_colorida.replace(inspecionavel, f"{ui.DOS_AMARELO}{inspecionavel}{ui.RESET}")
        for item in sala.get("itens", []):
            descricao_colorida = descricao_colorida.replace(item, f"{ui.DOS_VERDE}{item}{ui.RESET}")
            
        print(f"👁️  Visão: {descricao_colorida}")

        if len(sala.get("itens", [])) > 0:
            if jogo.turnos_luz > 0:
                itens_formatados = [f"{ui.DOS_VERDE}{item}{ui.RESET}" for item in sala['itens']]
                print(f"📦 Itens no chão: {', '.join(itens_formatados)}")
            else:
                print(f"📦 {ui.DOS_BRANCO}Deve ter algo no chão, mas escuro demais para ver o quê.{ui.RESET}")

        chaves_ignoradas = ["descrição", "itens", "inspecionaveis", "cofre_important", "cadeira"]
        saidas = [k for k in sala.keys() if k not in chaves_ignoradas and isinstance(sala[k], str)]
        if saidas:
            print(f"🧭 Saídas: {ui.DOS_AMARELO}{', '.join(saidas).title()}{ui.RESET}")
        else:
            print(f"🧭 Saídas: {ui.DOS_VERMELHO}Nenhuma saída aparente...{ui.RESET}")

        print(f"\n{ui.DOS_BRANCO}[ SISTEMA OPERACIONAL VILLAS BOAS v20.08 ]{ui.RESET}")
        print(f"{ui.DOS_BRANCO}[ HP: {ui.DOS_VERMELHO}{jogo.hp}/3{ui.DOS_BRANCO} | LUZ: {ui.DOS_AMARELO}{jogo.turnos_luz}{ui.DOS_BRANCO} | INV: {len(jogo.inventario)}/{MAX_INVENTARIO} ]{ui.RESET}")

def dar_tela_de_morte():
    jogo.estado_atual = "FIM"
    print(f"{ui.DOS_VERMELHO}{CAVEIRA_MORTE}{ui.RESET}")
    ui.digitar("💀 GAME OVER. A NOITE ENGOLIU VOCÊ.", 0.05, ui.DOS_VERMELHO)
    ui.digitar("=== SISTEMA CORROMPIDO. APERTE F5 PARA REINICIAR ===", 0.05, ui.DOS_AMARELO)

@app.route('/iniciar', methods=['GET'])
def iniciar_jogo():
    global jogo
    sid = session.get("sid")
    if sid and sid in partidas:
        del partidas[sid]  
    jogo = obter_estado()
    jogo.estado_atual = "AGUARDANDO_DIR"
    
    captura = io.StringIO()
    sys.stdout = captura
    imprimir_tela_boot()
    sys.stdout = sys.__stdout__
    
    texto_html = ansi_para_html(captura.getvalue())
    return jsonify({"linhas": [l for l in texto_html.split('\n') if l.strip() != ""]})

@app.route('/comando', methods=['POST'])
def receber_comando():
    global jogo
    jogo = obter_estado()
    dados = request.json
    comando = normalizar(dados.get('comando', ''))

    captura = io.StringIO()
    stdout_original = sys.stdout
    sys.stdout = captura

    try:
        if jogo.estado_atual == "FIM":
            print(f"{ui.DOS_VERMELHO}[SISTEMA BLOQUEADO] - Aperte a tecla F5 no teclado para jogar novamente.{ui.RESET}")

        elif jogo.estado_atual == "AGUARDANDO_DIR":
            if comando in ["cls", "limpar", "clear", "clean"]:
                print("@@CLEAR@@")
                imprimir_tela_boot()
            elif comando == "dir":
                print("@@CLEAR@@")
                print(f"{ui.DOS_BRANCO} Volume in drive A is VILLASBOAS{ui.RESET}")
                print(f"{ui.DOS_BRANCO} Directory of A:\\{ui.RESET}\n")
                print(f"{ui.DOS_VERDE}COMMAND  COM     47.845   02-11-82   6:00a{ui.RESET}")
                print(f"{ui.DOS_VERDE}SEGURA   SYS      2.048   02-11-82   6:00a{ui.RESET}")
                print(f"{ui.DOS_VERDE}NOTURNO  EXE     18.204   02-11-82   6:00a{ui.RESET}")
                print(f"{ui.DOS_AMARELO}       3 file(s)     68.097 bytes{ui.RESET}")
                print(f"{ui.DOS_AMARELO}       0 dir(s)    655.360 bytes free{ui.RESET}\n")
                jogo.estado_atual = "MENU"
                imprimir_menu_dificuldade()
            else:
                print(f"{ui.DOS_VERMELHO}Bad command or file name{ui.RESET}")
                print(f"{ui.DOS_VERDE}Digite {ui.DOS_BRANCO}dir{ui.DOS_VERDE} para acessar os diretórios:{ui.RESET}")

        elif jogo.estado_atual == "MENU":
            if comando in ["cls", "limpar", "clear", "clean"]:
                print("@@CLEAR@@")
                imprimir_menu_dificuldade()
            elif comando == "1":
                print("@@CLEAR@@")
                jogo.dificuldade_escolhida = "NORMAL"
                jogo.hp = 3; jogo.furia_noite = 1; jogo.energia_min_noite = 100; jogo.energia_max_noite = 100
                jogo.estado_atual = "JOGO"
                print(f"{ui.DOS_VERDE}MODO NORMAL SELECIONADO. INICIANDO JOGO.EXE...{ui.RESET}\n")
                print(f"{ui.DOS_BRANCO}Você entra no restaurante. Sua lanterna velha dá três piscadas fracas...{ui.RESET}")
                print(f"{ui.DOS_AMARELO}[AVISO DO SISTEMA]: BATERIA DA LANTERNA EM 5%. PROCURAR OUTRA FONTE DE LUZ EM ATÉ 3 TURNOS.{ui.RESET}")
                imprimir_contexto_sala()
            elif comando == "2":
                print("@@CLEAR@@")
                jogo.dificuldade_escolhida = "PESADELO"
                jogo.hp = 2; jogo.furia_noite = 2; jogo.energia_min_noite = 70; jogo.energia_max_noite = 82
                jogo.estado_atual = "JOGO"
                print(f"{ui.DOS_VERMELHO}MODO PESADELO SELECIONADO. BOA SORTE.{ui.RESET}\n")
                print(f"{ui.DOS_BRANCO}Você entra no restaurante. Sua lanterna velha dá três piscadas fracas...{ui.RESET}")
                print(f"{ui.DOS_AMARELO}[AVISO DO SISTEMA]: BATERIA DA LANTERNA EM 5%. PROCURAR OUTRA FONTE DE LUZ EM ATÉ 3 TURNOS.{ui.RESET}")
                imprimir_contexto_sala()
            else:
                print(f"{ui.DOS_VERMELHO}OPÇÃO INVÁLIDA. DIGITE 1 OU 2.{ui.RESET}")

        elif jogo.estado_atual == "JOGO":
            if comando in ["cls", "limpar", "clear", "clean"]:
                print("@@CLEAR@@")
                imprimir_contexto_sala()
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
                print(f"{ui.DOS_BRANCO}{ARTE_COFRE}{ui.RESET}")
                print(f"{ui.DOS_BRANCO}O cofre de ferro possui um teclado numérico antigo.{ui.RESET}")
                print(f"{ui.DOS_VERDE}Digite a senha de 4 dígitos: {ui.RESET}")
            elif (comando == "jogar jon" or comando == "jogar fome de jon") and jogo.sala_atual == "sala de fliperamas":
                jogo.estado_atual = "MINIGAME_JON"
                jogo.jon_passos_dados = 0
                jogo.jon_caminho_certo = [random.choice(["f", "e", "d"]) for _ in range(4)]
                print("@@CLEAR@@")
                print(f"{ui.DOS_BRANCO}{ARTE_PORCO}{ui.RESET}")
                ui.digitar("--- A FOME DE JON ---", 0.03, ui.DOS_VERDE)
                print(f"{ui.DOS_BRANCO}Guie o Porco Jon pelos dutos baseando-se nos seus sentidos.{ui.RESET}")
                print("Comandos: [F] Frente | [E] Esquerda | [D] Direita")
                dar_dica_jon(jogo.jon_caminho_certo[0])
                print(f"Passo 1/4 - Direção (F/E/D): ")
            elif comando == "jogar consertos" and jogo.sala_atual == "sala de fliperamas":
                if "moeda velha" not in jogo.inventario:
                    print("A máquina 'Consertos & Sorrisos' exige uma ficha (moeda velha) para iniciar.")
                else:
                    jogo.inventario.remove("moeda velha")
                    jogo.estado_atual = "MINIGAME_CONSERTOS_CABECA"
                    jogo.web_consertos = {}
                    print("@@CLEAR@@")
                    print(f"{ui.DOS_BRANCO}{ARTE_ROBO}{ui.RESET}")
                    ui.digitar("--- CONSERTOS & SORRISOS ---", 0.03, ui.DOS_VERDE)
                    print("Bem-vindo, Mecânico! Vamos montar nosso novo Festeiro!")
                    print(f"\n{ui.DOS_AMARELO}[ FASE 1: SELEÇÃO DE PEÇAS ]{ui.RESET}")
                    print("Escolha a Cabeça (1- Urso | 2- Coelho): ")
            elif (comando == "jogar adivinha" or comando == "jogar julgamento") and jogo.sala_atual == "sala de fliperamas":
                jogo.estado_atual = "MINIGAME_JULGAMENTO_Q1"
                jogo.web_julgamento = {"pontos": 0, "vitimas": ["angela", "joao", "renato"]}
                print("@@CLEAR@@")
                print(f"{ui.DOS_BRANCO}{ARTE_PIANO}{ui.RESET}")
                ui.digitar("--- O JULGAMENTO DO PIANISTA ---", 0.03, ui.DOS_VERDE)
                print(f"{ui.DOS_BRANCO}O animatrônico desperta. Ele detém todas as respostas.{ui.RESET}")
                print(f"\n{ui.DOS_AMARELO}PERGUNTA 1: Em que ano a nossa música parou para sempre?{ui.RESET}")
            else:
                gastou_turno = processar_comando(comando, jogo, jogo.mapa)
                if gastou_turno: atualizar_eventos_de_tempo(jogo)
                
                if jogo.sala_atual == "morte":
                    dar_tela_de_morte()
                elif jogo.sala_atual in ["saida", "cama", "final_bom"] or (jogo.sala_atual == "hall de entrada" and jogo.incendio and jogo.noite_vencida):
                    jogo.estado_atual = "FIM"
                    ui.digitar("FIM DE JOGO.", 0.05, ui.DOS_VERDE)
                    ui.digitar("=== APERTE F5 PARA REINICIAR ===", 0.05, ui.DOS_AMARELO)
                else:
                    imprimir_contexto_sala()

        elif jogo.estado_atual == "MINIGAME_COFRE":
            if comando in ["cls", "limpar", "clear", "clean"]:
                print("@@CLEAR@@")
                print(f"{ui.DOS_BRANCO}{ARTE_COFRE}{ui.RESET}")
                print(f"{ui.DOS_VERDE}Digite a senha de 4 dígitos: {ui.RESET}")
            elif comando == "1994": 
                print(f"{ui.DOS_VERDE}CLICK! A pesada porta de metal se abre.{ui.RESET}")
                sala = jogo.mapa[jogo.sala_atual]
                if "itens" not in sala: sala["itens"] = []
                
                if "chave dos fundos" not in jogo.inventario and "chave dos fundos" not in sala["itens"]:
                    if len(jogo.inventario) < MAX_INVENTARIO:
                        print(f"{ui.DOS_AMARELO}Você encontrou a 'chave dos fundos' suja de graxa lá dentro!{ui.RESET}")
                        jogo.inventario.append("chave dos fundos")
                    else:
                        print(f"{ui.DOS_AMARELO}Sua mochila está cheia! A 'chave dos fundos' caiu no chão da sala.{ui.RESET}")
                        sala["itens"].append("chave dos fundos")
                else:
                    print("O cofre está vazio. Apenas poeira.")
                jogo.estado_atual = "JOGO"
                imprimir_contexto_sala()
            else:
                print(f"{ui.DOS_VERMELHO}BEEP! Senha incorreta. Painel pisca em vermelho.{ui.RESET}")
                jogo.estado_atual = "JOGO"
                imprimir_contexto_sala()

        elif jogo.estado_atual == "MINIGAME_JON":
            passo = jogo.jon_passos_dados
            if comando in ["cls", "limpar", "clear", "clean"]:
                print("@@CLEAR@@")
                print(f"{ui.DOS_BRANCO}{ARTE_PORCO}{ui.RESET}")
                print(f"Passo {passo + 1}/4 - Direção (F/E/D): ")
            elif comando in ["f", "e", "d", "frente", "esquerda", "direita"]:
                letra = comando[0]
                if letra == jogo.jon_caminho_certo[passo]:
                    print(f"{ui.DOS_BRANCO}Jon rasteja em silêncio pelos dutos...{ui.RESET}")
                    jogo.jon_passos_dados += 1
                    if jogo.jon_passos_dados == 4:
                        print(f"\n{ui.DOS_VERDE}Jon encontrou a 'comida'. A tela pinga um pixel vermelho.{ui.RESET}")
                        print(f"{ui.DOS_VERMELHO}MENSAGEM: 'Eles não saíram pela porta da frente em 94.'{ui.RESET}")
                        jogo.turnos_luz = max(0, jogo.turnos_luz - 1)
                        jogo.estado_atual = "JOGO"
                        imprimir_contexto_sala()
                    else:
                        dar_dica_jon(jogo.jon_caminho_certo[jogo.jon_passos_dados])
                        print(f"Passo {jogo.jon_passos_dados + 1}/4 - Direção (F/E/D): ")
                else:
                    print(f"\n{ui.DOS_VERMELHO}CRUNCH! Jon caiu num triturador ativo! leva um choque brutal!{ui.RESET}")
                    jogo.hp -= 1
                    jogo.turnos_luz = max(0, jogo.turnos_luz - 1)
                    if jogo.hp <= 0:
                        dar_tela_de_morte()
                    else:
                        jogo.estado_atual = "JOGO"
                        imprimir_contexto_sala()
            else:
                print("Direção inválida. Use F, E ou D.")

        elif jogo.estado_atual == "MINIGAME_CONSERTOS_CABECA":
            jogo.web_consertos["cabeca"] = comando
            jogo.estado_atual = "MINIGAME_CONSERTOS_TRONCO"
            print("Escolha o Tronco (1- Fino | 2- Robusto): ")

        elif jogo.estado_atual == "MINIGAME_CONSERTOS_TRONCO":
            jogo.web_consertos["tronco"] = comando
            jogo.estado_atual = "MINIGAME_CONSERTOS_PERNAS"
            print("Escolha as Pernas (1- Aço | 2- Pelúcia): ")

        elif jogo.estado_atual == "MINIGAME_CONSERTOS_PERNAS":
            cabeca = jogo.web_consertos.get("cabeca", "1")
            tronco = jogo.web_consertos.get("tronco", "1")
            pernas = comando
            item_secreto = None
            
            if cabeca == "2" and pernas == "2":
                print("> AVISO: Peças incompatíveis. Anomalia detectada.")
                item_secreto = "remedio"
            elif cabeca == "1" and tronco == "2":
                print("> Encaixando peças do modelo padrão 'Urso Robusto'...")
            else:
                print("> Erro de harmonia visual. Soldando peças à força...")
                
            print(f"\n{ui.DOS_VERDE}CONSERTO CONCLUÍDO! O ANIMATRÔNICO SORRI PARA VOCÊ!{ui.RESET}")
            sala = jogo.mapa[jogo.sala_atual]
            if "itens" not in sala: sala["itens"] = []
            
            if "chave da cozinha" not in jogo.inventario and "chave da cozinha" not in sala["itens"]:
                print(f"{ui.DOS_BRANCO}A gaveta principal de prêmios se abre com um barulho metálico.{ui.RESET}")
                if len(jogo.inventario) < MAX_INVENTARIO:
                    jogo.inventario.append("chave da cozinha")
                    print(f"{ui.DOS_VERDE}🎒 Você obteve: CHAVE DA COZINHA!{ui.RESET}")
                else:
                    print(f"{ui.DOS_AMARELO}🎒 Sua mochila está cheia! A CHAVE DA COZINHA caiu no chão.{ui.RESET}")
                    sala["itens"].append("chave da cozinha")

            if item_secreto:
                print(f"{ui.DOS_BRANCO}Um compartimento de emergência se abriu na base da máquina!{ui.RESET}")
                if len(jogo.inventario) < MAX_INVENTARIO:
                    jogo.inventario.append(item_secreto)
                    print(f"{ui.DOS_VERDE}🎒 Você obteve um item extra: {item_secreto.upper()}!{ui.RESET}")
                else:
                    print(f"{ui.DOS_AMARELO}🎒 Sua mochila está cheia! O item {item_secreto.upper()} caiu no chão.{ui.RESET}")
                    sala["itens"].append(item_secreto)
                
            jogo.turnos_luz = max(0, jogo.turnos_luz - 1)
            jogo.estado_atual = "JOGO"
            imprimir_contexto_sala()

        elif jogo.estado_atual == "MINIGAME_JULGAMENTO_Q1":
            if comando == "1994": jogo.web_julgamento["pontos"] += 1; falar_pianista(True)
            else: falar_pianista(False)
            jogo.estado_atual = "MINIGAME_JULGAMENTO_Q2"
            print(f"\n{ui.DOS_AMARELO}PERGUNTA 2: Qual animatrônico está atrás de você agora?{ui.RESET}")

        elif jogo.estado_atual == "MINIGAME_JULGAMENTO_Q2":
            if "caroline" in comando or "ela" in comando: jogo.web_julgamento["pontos"] += 1; falar_pianista(True)
            else: falar_pianista(False)
            jogo.estado_atual = "MINIGAME_JULGAMENTO_Q3"
            print(f"\n{ui.DOS_AMARELO}PERGUNTA 3: Em que ano tudo isso começou?{ui.RESET}")

        elif jogo.estado_atual == "MINIGAME_JULGAMENTO_Q3":
            if comando == "1982": jogo.web_julgamento["pontos"] += 1; falar_pianista(True)
            else: falar_pianista(False)
            jogo.estado_atual = "MINIGAME_JULGAMENTO_Q4"
            print(f"\n{ui.DOS_AMARELO}PERGUNTA 4: Quem é você?{ui.RESET}")

        elif jogo.estado_atual == "MINIGAME_JULGAMENTO_Q4":
            if "rogerio" in comando: jogo.web_julgamento["pontos"] += 1; falar_pianista(True)
            else: falar_pianista(False)
            jogo.estado_atual = "MINIGAME_JULGAMENTO_V1"
            print(f"\n{ui.DOS_AMARELO}PERGUNTA 5: Quem são as três vítimas? Digite o 1º nome:{ui.RESET}")

        elif jogo.estado_atual in ["MINIGAME_JULGAMENTO_V1", "MINIGAME_JULGAMENTO_V2", "MINIGAME_JULGAMENTO_V3"]:
            acertou = False
            for v in jogo.web_julgamento["vitimas"][:]:
                if v in comando:
                    jogo.web_julgamento["vitimas"].remove(v)
                    acertou = True
            
            if acertou: falar_pianista(True)
            else: falar_pianista(False)
            
            if jogo.estado_atual == "MINIGAME_JULGAMENTO_V1":
                jogo.estado_atual = "MINIGAME_JULGAMENTO_V2"
                print("Digite o 2º nome: ")
            elif jogo.estado_atual == "MINIGAME_JULGAMENTO_V2":
                jogo.estado_atual = "MINIGAME_JULGAMENTO_V3"
                print("Digite o 3º nome: ")
            else:
                if len(jogo.web_julgamento["vitimas"]) == 0:
                    jogo.web_julgamento["pontos"] += 1
                if jogo.web_julgamento["pontos"] == 5:
                    ui.digitar("Obrigado por voltar pela gente, Rogério...", 0.08, ui.DOS_VERDE)
                    sala = jogo.mapa[jogo.sala_atual]
                    if "itens" not in sala: sala["itens"] = []
                    
                    if "bateria nova" not in jogo.inventario and "bateria nova" not in sala["itens"]:
                        print(f"{ui.DOS_BRANCO}A gaveta inferior abre com uma 'bateria nova'!{ui.RESET}")
                        if len(jogo.inventario) < MAX_INVENTARIO:
                            jogo.inventario.append("bateria nova")
                            print(f"{ui.DOS_VERDE}🎒 Você a guardou na mochila.{ui.RESET}")
                        else:
                            print(f"{ui.DOS_AMARELO}🎒 Mochila cheia! A bateria nova caiu no chão.{ui.RESET}")
                            sala["itens"].append("bateria nova")
                else:
                    ui.digitar("Quem é você? A tela desliga. Você perdeu a absolvição.", 0.05, ui.DOS_VERMELHO)
                    
                jogo.turnos_luz = max(0, jogo.turnos_luz - 1)
                jogo.estado_atual = "JOGO"
                imprimir_contexto_sala()

        elif jogo.estado_atual in ["MINIGAME_MINOTAURO", "MINIGAME_SEGURANCA"]:
            if comando in ["cls", "limpar", "clear", "clean"]:
                print("@@CLEAR@@")
                jogo.minigame_atual.imprimir_status()
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
                    dar_tela_de_morte()
                elif resultado in ["vitoria_minotauro", "vitoria_seguranca"]:
                    jogo.minigame_atual = None
                    jogo.sala_atual = "01"
                    jogo.estado_atual = "JOGO"
                    print(f"{ui.DOS_VERDE}Você sobreviveu ao evento! Voltando ao sistema principal...{ui.RESET}")
                    imprimir_contexto_sala()
                else:
                    jogo.minigame_atual.imprimir_status()

    except Exception as e:
        print(f"\n[ERRO DE SISTEMA]: {e}")
    finally:
        sys.stdout = stdout_original

    texto_html = ansi_para_html(captura.getvalue())
    return jsonify({"linhas": [linha for linha in texto_html.split('\n') if linha.strip() != ""]})

if __name__ == '__main__':
    app.run(debug=True, port=5000)