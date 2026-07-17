import os
import json
import sys
import io
import re
import random
import uuid
import traceback
from pathlib import Path
from datetime import timedelta

from flask import Flask, request, jsonify, session
from flask_cors import CORS

from state import GameState, GameStateEnum, salvar_autosave, carregar_autosave, AUTOSAVE_FILE
from commands import processar_comando, normalizar
from minigames import MinigameMinotauro, MinigameSeguranca
from data import ARTE_PORCO, ARTE_ROBO, ARTE_PIANO, CAVEIRA_MORTE, MAX_INVENTARIO
from ui import DOS_VERDE, DOS_BRANCO, DOS_AMARELO, DOS_VERMELHO, RESET, UIHandler
from utils import extrair_argumentos, atualizar_eventos_de_tempo

from views import (imprimir_tela_boot, imprimir_menu_dificuldade, imprimir_tutorial,
                   dar_dica_jon, falar_pianista, imprimir_contexto_sala, dar_tela_de_morte, rodar_final)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

ARTE_COFRE = r'''
  __________________________
 /  ______________________  \
|  |  __   __   __   __   |  |
|  | |  | |  | |  | |  |  |  |
|  | |__| |__| |__| |__|  |  |
|  |                      |  |
|  |       .------.       |  |
|  |      /        \      |  |
|  |     |   [**]   |     |  |
|  |      \        /      |  |
|  |       `------'       |  |
|  |                      |  |
|  |______________________|  |
 \__________________________/
'''

class WebUIHandler(UIHandler):
    def limpar(self):
        print("@@CLEAR@@")
    
    def pausar(self, segs):
        pass
        
    def exibir(self, texto):
        # AQUI É O SEGREDO DO MINIGAME!
        # Agora o texto "instantâneo" vai ser desenhado a 2 milissegundos por letra!
        self.animar(texto, 0.002)
        
    def animar(self, texto, tempo=0.03, cor="", jogo=None):
        cor_nome = "verde"
        if cor == DOS_BRANCO: cor_nome = "branco"
        elif cor == DOS_AMARELO: cor_nome = "amarelo"
        elif cor == DOS_VERMELHO: cor_nome = "vermelho"
        
        if jogo and getattr(jogo, 'fast_mode', False): tempo = 0
        ms = int(tempo * 1000)
        print(f"@@TYPE@@{cor_nome}@@{ms}@@{texto}")
        
    def obter_input(self, prompt_text):
        return "" 

def ansi_para_html(texto_ansi):
    mapa_cores = { DOS_VERDE: "verde", DOS_BRANCO: "branco", DOS_AMARELO: "amarelo", DOS_VERMELHO: "vermelho" }
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

app = Flask(__name__, static_folder=BASE_DIR, static_url_path="/")
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "villas-boas-1982-seguranca")
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30) # <--- ADICIONE ESTA LINHA AQUI
CORS(app, supports_credentials=True)

SESSION_DIR = Path(BASE_DIR) / "sessions"
SESSION_DIR.mkdir(exist_ok=True)


# --- NOVO DIRETÓRIO ISOLADO PARA SAVES ---
SAVES_DIR = Path(BASE_DIR) / "saves"
SAVES_DIR.mkdir(exist_ok=True)

def obter_caminho_autosave(sid):
    return SAVES_DIR / f"autosave_{sid}.json"

def salvar_autosave_com_sid(jogo, sid):
    if not sid: return
    caminho = obter_caminho_autosave(sid)
    caminho.write_text(json.dumps(jogo.to_dict(), ensure_ascii=False), encoding="utf-8")

def carregar_autosave_com_sid(jogo, sid):
    if not sid: return False
    caminho = obter_caminho_autosave(sid)
    if caminho.exists():
        try:
            dados = json.loads(caminho.read_text(encoding="utf-8"))
            novo_jogo = GameState.from_dict(dados)
            # Copia os dados recuperados para o estado ao vivo da sessão
            for k, v in novo_jogo.__dict__.items():
                if k != 'ui_handler':
                    setattr(jogo, k, v)
            return True
        except:
            return False
    return False

# AQUI VAI O CACHE DE MEMÓRIA PARA SALVAR O MINIGAME!
MEMORIA_SESSOES = {}

def obter_estado():
    session.permanent = True
    sid = session.get("sid")
    if not sid:
        sid = str(uuid.uuid4())
        session["sid"] = sid
        
    # Tenta puxar direto da memória RAM rápida
    if sid in MEMORIA_SESSOES:
        jogo = MEMORIA_SESSOES[sid]
        jogo.ui_handler = WebUIHandler()
        return jogo
        
    # Se falhar (ex: servidor reiniciou), puxa do disco
    session_file = SESSION_DIR / f"{sid}.json"
    if session_file.exists():
        try:
            dados = json.loads(session_file.read_text(encoding="utf-8"))
            jogo = GameState.from_dict(dados)
            jogo.ui_handler = WebUIHandler()
            MEMORIA_SESSOES[sid] = jogo
            return jogo
        except: pass
        
    jogo = GameState(ui_handler=WebUIHandler())
    salvar_sessao(sid, jogo)
    return jogo

def salvar_sessao(sid, jogo):
    if not sid: return
    # Salva na memória e no disco
    MEMORIA_SESSOES[sid] = jogo
    session_file = SESSION_DIR / f"{sid}.json"
    session_file.write_text(json.dumps(jogo.to_dict(), ensure_ascii=False), encoding="utf-8")

def gerar_resposta_json(captura, jogo):
    linhas = [linha for linha in ansi_para_html(captura.getvalue()).split('\n') if linha.strip() != ""]
    saidas, hp, luz, inv, sala = [], "...", "...", [], "BOOT"

    if jogo:
        if getattr(jogo, 'estado_atual', "") not in ["FIM", "MENU", "AGUARDANDO_DIR"] and jogo.sala_atual in jogo.mapa:
            chaves_ignoradas = ["descrição", "itens", "inspecionaveis", "cofre_important", "cadeira"]
            saidas = [k.title() for k in jogo.mapa[jogo.sala_atual].keys() if k not in chaves_ignoradas and isinstance(jogo.mapa[jogo.sala_atual][k], str)]

        hp = jogo.hp if not getattr(jogo, 'god_mode', False) else "∞"
        luz = jogo.turnos_luz if not getattr(jogo, 'god_mode', False) else "∞"
        inv = jogo.inventario
        sala = jogo.sala_atual.upper() if jogo.estado_atual not in ["MENU", "AGUARDANDO_DIR"] else "SISTEMA"

    return jsonify({
        "linhas": linhas,
        "estado": { "hp": hp, "luz": luz, "inventario": inv, "sala": sala, "saidas": saidas }
    })

# --- REDIRECIONADORES DE ERRO (Mata a Tela Preta do "Not Found") ---
@app.route("/")
def raiz():
    return app.send_static_file("index.html")

@app.errorhandler(404)
@app.errorhandler(405)
def page_not_found(e):
    # Se o jogador der F5 numa rota proibida, o Flask manda ele de volta pro jogo à força!
    return app.send_static_file("index.html")

@app.route('/iniciar', methods=['GET'])
def iniciar_jogo():
    sid = session.get("sid")
    if sid:
        session_file = SESSION_DIR / f"{sid}.json"
        if session_file.exists():
            try: session_file.unlink() 
            except: pass
            
    # Limpa a sessão atual do Flask para garantir que o F5 sempre recomece do zero!
    session.clear()
    
    jogo = obter_estado()
    jogo.estado_atual = "AGUARDANDO_DIR"
    
    captura = io.StringIO()
    sys.stdout = captura
    imprimir_tela_boot(jogo.ui_handler)
    sys.stdout = sys.__stdout__
    
    salvar_sessao(session.get("sid"), jogo)
    return gerar_resposta_json(captura, jogo)

# --- A ROTA AGORA ACEITA GET (F5) E POST ---
@app.route('/comando', methods=['GET', 'POST'])
def receber_comando():
    # SE DER F5 AQUI, DEVOLVE O JOGO NORMALMENTE!
    if request.method == 'GET':
        return send_from_directory(BASE_DIR, "index.html")

    jogo = None
    captura = io.StringIO()
    stdout_original = sys.stdout
    sys.stdout = captura

    try:
        jogo = obter_estado()
        dados = request.json
        comando = normalizar(dados.get('comando', ''))
        ui = jogo.ui_handler

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
                ui.animar(f"{DOS_VERDE}COMMAND  COM          47.845  02-11-1982  6:00a{RESET}", 0.01, jogo=jogo)
                ui.animar(f"{DOS_VERDE}SEGURA   SYS           2.048  02-11-1982  6:00a{RESET}", 0.01, jogo=jogo)
                ui.animar(f"{DOS_VERDE}NOTURNO  EXE          18.204  02-11-1982  6:00a{RESET}", 0.01, jogo=jogo)
                ui.animar(f"{DOS_VERDE}DESKTOP  <DIR>        197.78  24-07-2007  4:00a{RESET}", 0.01, jogo=jogo)
                ui.animar(f"{DOS_VERDE}SAVES    <DIR>        358.21  23-07-2008  4:00a{RESET}", 0.01, jogo=jogo)
                ui.animar(f"{DOS_VERDE}PICTURE  <DIR>        666.00  05-11-1994  4:00a{RESET}", 0.01, jogo=jogo)
                ui.animar(f"{DOS_VERDE}VALID    <DIR>        2.7801  24-07-2007  4:00a{RESET}", 0.01, jogo=jogo)
                ui.exibir(f"{DOS_AMARELO}       3 file(s)        68.097 bytes{RESET}")
                ui.exibir(f"{DOS_AMARELO}       4 dir(s)        655.360 bytes free{RESET}\n")
                jogo.estado_atual = "MENU"
                imprimir_menu_dificuldade(ui, tem_autosave=AUTOSAVE_FILE.exists())
            else:
                ui.exibir(f"{DOS_VERMELHO}Bad command or file name{RESET}")
                ui.exibir(f"{DOS_VERDE}Digite {DOS_BRANCO}dir{DOS_VERDE} para acessar os diretórios:{RESET}")

        elif jogo.estado_atual == "MENU":
            sid = session.get("sid")
            tem_save = sid and obter_caminho_autosave(sid).exists() if sid else False

            if comando in ["cls", "limpar", "clear", "clean"]:
                ui.limpar()
                imprimir_menu_dificuldade(ui, tem_autosave=tem_save, jogo=jogo)
            elif comando == "5" and tem_save:
                ui.limpar()
                if carregar_autosave_com_sid(jogo, sid):
                    ui.animar(f"{DOS_VERDE}JOGO RESTAURADO COM SUCESSO DO SEU AUTOSAVE DE SESSÃO.{RESET}\n", 0.04, jogo=jogo)
                    imprimir_contexto_sala(jogo)
                else:
                    ui.animar(f"{DOS_VERMELHO}Falha ao ler o seu Autosave.{RESET}", 0.04, jogo=jogo)
                    imprimir_menu_dificuldade(ui, tem_autosave=tem_save, jogo=jogo)
            elif comando in ["1", "2", "3", "4"]:
                ui.limpar()
                if comando == "1":
                    jogo.dificuldade_escolhida = "NORMAL"
                    jogo.fast_mode = False
                    jogo.hp = 3; jogo.furia_noite = 1; jogo.energia_min_noite = 100; jogo.energia_max_noite = 100
                    ui.animar(f"{DOS_VERDE}MODO NORMAL SELECIONADO. VELOCIDADE RETRÔ ATIVADA.{RESET}\n", 0.04, jogo=jogo)
                elif comando == "2":
                    jogo.dificuldade_escolhida = "NORMAL"
                    jogo.fast_mode = True
                    jogo.hp = 3; jogo.furia_noite = 1; jogo.energia_min_noite = 100; jogo.energia_max_noite = 100
                    ui.animar(f"{DOS_AMARELO}MODO NORMAL COM TEXTO RÁPIDO SELECIONADO.{RESET}\n", 0.04, jogo=jogo)
                elif comando == "3":
                    jogo.dificuldade_escolhida = "PESADELO"
                    jogo.fast_mode = False
                    jogo.hp = 2; jogo.furia_noite = 2; jogo.energia_min_noite = 70; jogo.energia_max_noite = 82
                    ui.animar(f"{DOS_VERMELHO}MODO PESADELO SELECIONADO. VELOCIDADE RETRÔ ATIVADA. BOA SORTE.{RESET}\n", 0.04, jogo=jogo)
                elif comando == "4":
                    jogo.dificuldade_escolhida = "PESADELO"
                    jogo.fast_mode = True
                    jogo.hp = 2; jogo.furia_noite = 2; jogo.energia_min_noite = 70; jogo.energia_max_noite = 82
                    ui.animar(f"{DOS_VERMELHO}MODO PESADELO COM TEXTO RÁPIDO SELECIONADO. BOA SORTE.{RESET}\n", 0.04, jogo=jogo)

                jogo.estado_atual = "JOGO"
                imprimir_tutorial(ui)
                ui.animar(f"{DOS_BRANCO}Você entra no restaurante. Sua lanterna velha dá três piscadas fracas...{RESET}", 0.08, jogo=jogo)
                ui.animar(f"{DOS_AMARELO}[AVISO DO SISTEMA]: BATERIA DA LANTERNA EM 5%. PROCURAR OUTRA FONTE DE LUZ EM ATÉ 3 TURNOS.{RESET}", 0.01, jogo=jogo)
                imprimir_contexto_sala(jogo)
                
            elif comando == "2007":
                ui.limpar()
                jogo.dificuldade_escolhida = "GOD MODE"
                jogo.god_mode = True
                jogo.hp = 9999; jogo.furia_noite = 0; jogo.energia_min_noite = 9999; jogo.energia_max_noite = 9999
                jogo.turnos_luz = 9999
                jogo.estado_atual = "JOGO"
                ui.animar(f"{DOS_AMARELO}MODO DEUS ATIVADO. ACESSO AOS BASTIDORES CONCEDIDO.{RESET}\n", 0.04, jogo=jogo)
                ui.animar(f"{DOS_BRANCO}Você entra no restaurante. Sua lanterna brilha com a força de uma estrela...{RESET}", 0.04, jogo=jogo)
                imprimir_contexto_sala(jogo)
            else:
                ui.animar(f"{DOS_VERMELHO}OPÇÃO INVÁLIDA. DIGITE UMA OPÇÃO DO MENU.{RESET}", 0.04, jogo=jogo)

        elif jogo.estado_atual in ["JOGO", "COMBATE_ANIMATRONICO"]:
            if comando in ["cls", "limpar", "clear", "clean"]:
                ui.limpar()
                imprimir_contexto_sala(jogo)
            elif jogo.sala_atual == "sala de energia" and not getattr(jogo, 'fios_cortados_inventario', False):
                jogo.minigame_atual = MinigameMinotauro(jogo)
                jogo.estado_atual = "MINIGAME_MINOTAURO"
                jogo.minigame_atual.imprimir_status()
            elif jogo.sala_atual == "cadeira" and not getattr(jogo, 'noite_vencida', False):
                jogo.minigame_atual = MinigameSeguranca(jogo)
                jogo.estado_atual = "MINIGAME_SEGURANCA"
                jogo.minigame_atual.imprimir_status()
                
            # === CORREÇÃO DA SALA DO COFRE AQUI: Voltou a ser "01" ===
            elif comando == "abrir cofre" and jogo.sala_atual == "01":
                jogo.estado_atual = "MINIGAME_COFRE"
                ui.animar(f"{DOS_BRANCO}{ARTE_COFRE}{RESET}", 0.015, jogo=jogo)
                ui.exibir(f"{DOS_BRANCO}O cofre de ferro possui um teclado numérico antigo.{RESET}")
                ui.exibir(f"{DOS_VERDE}Digite a senha de 4 dígitos: {RESET}")
                
            elif (comando == "jogar jon" or comando == "jogar fome de jon") and jogo.sala_atual == "sala de fliperamas":
                jogo.estado_atual = "MINIGAME_JON"
                jogo.jon_passos_dados = 0
                jogo.jon_caminho_certo = [random.choice(["f", "e", "d"]) for _ in range(4)]
                ui.limpar()
                ui.animar(f"{DOS_BRANCO}{ARTE_PORCO}{RESET}", 0.015, jogo=jogo)
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
                    ui.animar(f"{DOS_BRANCO}{ARTE_ROBO}{RESET}", 0.015, jogo=jogo)
                    ui.animar("--- CONSERTOS & SORRISOS ---", 0.03, DOS_VERDE, jogo)
                    ui.exibir("Bem-vindo, Mecânico! Vamos montar nosso novo Festeiro!")
                    ui.exibir(f"\n{DOS_AMARELO}[ FASE 1: SELEÇÃO DE PEÇAS ]{RESET}")
                    ui.exibir("Escolha a Cabeça (1- Urso | 2- Coelho): ")
            elif (comando == "jogar adivinha" or comando == "jogar julgamento") and jogo.sala_atual == "sala de fliperamas":
                jogo.estado_atual = "MINIGAME_JULGAMENTO_Q1"
                jogo.web_julgamento = {"pontos": 0, "vitimas": ["angela", "joao", "renato"]}
                ui.limpar()
                ui.animar(f"{DOS_BRANCO}{ARTE_PIANO}{RESET}", 0.015, jogo=jogo)
                ui.animar("--- O JULGAMENTO DO PIANISTA ---", 0.03, DOS_VERDE, jogo)
                ui.exibir(f"{DOS_BRANCO}O animatrônico desperta. Ele detém todas as respostas.{RESET}")
                ui.exibir(f"\n{DOS_AMARELO}PERGUNTA 1: Em que ano a nossa música parou para sempre?{RESET}")
            else:
                gastou_turno = processar_comando(comando, jogo, jogo.mapa)
                if gastou_turno: atualizar_eventos_de_tempo(jogo)
                
                if jogo.sala_atual == "morte":
                    dar_tela_de_morte(jogo)
                elif jogo.sala_atual == "saida":
                    rodar_final("saida", jogo)
                elif jogo.sala_atual == "cama":
                    rodar_final("cama", jogo)
                elif jogo.sala_atual == "hall de entrada" and getattr(jogo, 'noite_vencida', False):
                    if getattr(jogo, 'incendio', False): rodar_final("verdadeiro", jogo)
                    else: rodar_final("final_bom", jogo)
                elif jogo.estado_atual == "COMBATE_ANIMATRONICO":
                    pass 
                else:
                    imprimir_contexto_sala(jogo)

        elif jogo.estado_atual == "MINIGAME_COFRE":
            if comando in ["cls", "limpar", "clear", "clean"]:
                ui.limpar()
                ui.animar(f"{DOS_BRANCO}{ARTE_COFRE}{RESET}", 0.015, jogo=jogo)
                ui.exibir(f"{DOS_VERDE}Digite a senha de 4 dígitos: {RESET}")
            elif comando == "1994": 
                ui.exibir(f"{DOS_VERDE}CLICK! A pesada porta de metal se abre.{RESET}")
                sala = jogo.mapa[jogo.sala_atual]
                sala.setdefault("itens", [])
                
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
            if comando in ["f", "e", "d", "frente", "esquerda", "direita"]:
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
                    if jogo.hp <= 0: dar_tela_de_morte(jogo)
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
            item_secreto = "remedio" if (cabeca == "2" and pernas == "2") else None
            
            ui.exibir(f"\n{DOS_VERDE}CONSERTO CONCLUÍDO! O ANIMATRÔNICO SORRI PARA VOCÊ!{RESET}")
            sala = jogo.mapa[jogo.sala_atual]
            sala.setdefault("itens", [])
            
            if "chave da cozinha" not in jogo.inventario and "chave da cozinha" not in sala["itens"]:
                if len(jogo.inventario) < MAX_INVENTARIO or getattr(jogo, 'god_mode', False):
                    jogo.inventario.append("chave da cozinha")
                    ui.exibir(f"{DOS_VERDE}🎒 Você obteve: CHAVE DA COZINHA!{RESET}")
                else:
                    sala["itens"].append("chave da cozinha")

            if item_secreto:
                if len(jogo.inventario) < MAX_INVENTARIO or getattr(jogo, 'god_mode', False):
                    jogo.inventario.append(item_secreto)
                    ui.exibir(f"{DOS_VERDE}🎒 Você obteve um item extra: {item_secreto.upper()}!{RESET}")
                else:
                    sala["itens"].append(item_secreto)
                
            jogo.turnos_luz = max(0, jogo.turnos_luz - 1)
            jogo.estado_atual = "JOGO"
            imprimir_contexto_sala(jogo)

        elif jogo.estado_atual == "MINIGAME_JULGAMENTO_Q1":
            if comando == "1994": jogo.web_julgamento["pontos"] += 1; falar_pianista(True, ui, jogo)
            else: falar_pianista(False, ui, jogo)
            jogo.estado_atual = "MINIGAME_JULGAMENTO_Q2"
            ui.exibir(f"\n{DOS_AMARELO}PERGUNTA 2: Qual animatrônico está atrás de você agora?{RESET}")

        elif jogo.estado_atual == "MINIGAME_JULGAMENTO_Q2":
            if "caroline" in comando or "ela" in comando: jogo.web_julgamento["pontos"] += 1; falar_pianista(True, ui, jogo)
            else: falar_pianista(False, ui, jogo)
            jogo.estado_atual = "MINIGAME_JULGAMENTO_Q3"
            ui.exibir(f"\n{DOS_AMARELO}PERGUNTA 3: Em que ano tudo isso começou?{RESET}")

        elif jogo.estado_atual == "MINIGAME_JULGAMENTO_Q3":
            if comando == "1982": jogo.web_julgamento["pontos"] += 1; falar_pianista(True, ui, jogo)
            else: falar_pianista(False, ui, jogo)
            jogo.estado_atual = "MINIGAME_JULGAMENTO_Q4"
            ui.exibir(f"\n{DOS_AMARELO}PERGUNTA 4: Quem é você?{RESET}")

        elif jogo.estado_atual == "MINIGAME_JULGAMENTO_Q4":
            if "rogerio" in comando: jogo.web_julgamento["pontos"] += 1; falar_pianista(True, ui, jogo)
            else: falar_pianista(False, ui, jogo)
            jogo.estado_atual = "MINIGAME_JULGAMENTO_V1"
            ui.exibir(f"\n{DOS_AMARELO}PERGUNTA 5: Quem são as três vítimas? Digite o 1º nome:{RESET}")

        elif jogo.estado_atual in ["MINIGAME_JULGAMENTO_V1", "MINIGAME_JULGAMENTO_V2", "MINIGAME_JULGAMENTO_V3"]:
            acertou = False
            for v in jogo.web_julgamento["vitimas"][:]:
                if v in comando:
                    jogo.web_julgamento["vitimas"].remove(v)
                    acertou = True
            
            if acertou: falar_pianista(True, ui, jogo)
            else: falar_pianista(False, ui, jogo)
            
            if jogo.estado_atual == "MINIGAME_JULGAMENTO_V1":
                jogo.estado_atual = "MINIGAME_JULGAMENTO_V2"
                ui.exibir("Digite o 2º nome: ")
            elif jogo.estado_atual == "MINIGAME_JULGAMENTO_V2":
                jogo.estado_atual = "MINIGAME_JULGAMENTO_V3"
                ui.exibir("Digite o 3º nome: ")
            else:
                if len(jogo.web_julgamento["vitimas"]) == 0: jogo.web_julgamento["pontos"] += 1
                if jogo.web_julgamento["pontos"] == 5:
                    ui.animar("Obrigado por voltar pela gente, Rogério...", 0.08, DOS_VERDE, jogo)
                    sala = jogo.mapa[jogo.sala_atual]
                    sala.setdefault("itens", [])
                    if "bateria nova" not in jogo.inventario and "bateria nova" not in sala["itens"]:
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
            if comando in ["pular noite", "pular", "set time 06:00"] and getattr(jogo, 'god_mode', False) and jogo.estado_atual == "MINIGAME_SEGURANCA":
                ui.exibir(f"{DOS_AMARELO}[GOD MODE] Você altera os ponteiros do universo. O relógio salta para as 06:00 instantaneamente.{RESET}")
                jogo.minigame_atual.turno = 24 
                resultado = jogo.minigame_atual.processar_turno("esperar", jogo) 
                if resultado == "vitoria_seguranca":
                    jogo.minigame_atual = None
                    # === CORREÇÃO DO RETORNO DE VITÓRIA: Voltou a ser "01" ===
                    jogo.sala_atual = "01" 
                    jogo.estado_atual = "JOGO"
                    imprimir_contexto_sala(jogo)

            elif comando in ["atacar", "bater", "chutar", "lutar"] and getattr(jogo, 'god_mode', False) and jogo.estado_atual == "MINIGAME_MINOTAURO":
                ui.exibir(f"{DOS_AMARELO}[GOD MODE] Você corre e dá uma voadora no peito do Minotauro! Ele foge.{RESET}")
                jogo.minigame_atual = None
                jogo.sala_atual = "sala dos fundos"
                jogo.estado_atual = "JOGO"
                imprimir_contexto_sala(jogo)
            else:
                partes = extrair_argumentos(comando)
                verbo = partes[0] if partes else ""
                mapa_direcoes = {"f": "ir frente", "t": "ir atrás", "e": "ir esquerda", "d": "ir direita"}
                if verbo in mapa_direcoes: comando = mapa_direcoes[verbo]
                
                resultado = jogo.minigame_atual.processar_turno(comando, jogo)
                
                if resultado == "morte":
                    jogo.minigame_atual = None
                    jogo.sala_atual = "morte"
                    dar_tela_de_morte(jogo)
                elif resultado == "vitoria_minotauro":
                    jogo.minigame_atual = None
                    jogo.sala_atual = "sala dos fundos" 
                    jogo.estado_atual = "JOGO"
                    jogo.mapa["sala dos fundos"]["energia"] = "A pesada porta da sala de energia está totalmente destruída."
                    ui.exibir(f"{DOS_VERDE}A porta cedeu atrás de você e travou para sempre.{RESET}")
                    imprimir_contexto_sala(jogo)
                elif resultado == "vitoria_seguranca":
                    jogo.minigame_atual = None
                    # === CORREÇÃO DO RETORNO DE VITÓRIA: Voltou a ser "01" ===
                    jogo.sala_atual = "01" 
                    jogo.estado_atual = "JOGO"
                    imprimir_contexto_sala(jogo)
                else:
                    jogo.minigame_atual.imprimir_status()
        
        if getattr(jogo, 'god_mode', False):
            jogo.hp = 9999
            jogo.turnos_luz = 9999
            if getattr(jogo, 'minigame_atual', None):
                if isinstance(jogo.minigame_atual, MinigameMinotauro): jogo.minigame_atual.bateria = 9999
                elif isinstance(jogo.minigame_atual, MinigameSeguranca): jogo.minigame_atual.energia = 9999
                    
        if getattr(jogo, 'estado_atual', "") in ["JOGO", "COMBATE_ANIMATRONICO"]:
            salvar_autosave_com_sid(jogo, session.get("sid"))

    except Exception as e:
        print(f"\n{DOS_VERMELHO}[ERRO INTERNO DO SISTEMA]: O sistema falhou ao processar a ação.{RESET}")
        print(f"{DOS_AMARELO}Detalhes técnicos: {e}{RESET}")
        traceback.print_exc()
    finally:
        sys.stdout = stdout_original

    if jogo: salvar_sessao(session.get("sid"), jogo)
    return gerar_resposta_json(captura, jogo)

if __name__ == '__main__':
    app.run(debug=True, port=5000)