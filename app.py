import os
import sys
import logging
import io
import json
import uuid
from datetime import timedelta
from pathlib import Path

from flask import Flask, request, jsonify, session, send_from_directory
from flask_session import Session
from flask_cors import CORS

from state import GameState
from ui import UIHandler, DOS_VERDE, DOS_BRANCO, DOS_AMARELO, DOS_VERMELHO, RESET
from engine import processar_fluxo_jogo
from views import imprimir_tela_boot

# Configuração de Logs para auditoria no Render
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# --- SEGURANÇA E CONFIGURAÇÃO VIA ENVIRONMENT VARIABLES ---
SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
if not SECRET_KEY:
    logging.critical("CRITICO: FLASK_SECRET_KEY nao configurada no ambiente. Aplicacao vulneravel!")
    # Apenas para impedir o app de quebrar nos testes locais. No Render, preencha as ENV Vars!
    SECRET_KEY = "DEV_SECRET_DO_NOT_USE_IN_PROD_1982"

SESSION_DIR_ENV = os.environ.get("SESSION_DIR", os.path.join(BASE_DIR, "sessions"))
SAVES_DIR_ENV = os.environ.get("SAVES_DIR", os.path.join(BASE_DIR, "saves"))

os.makedirs(SESSION_DIR_ENV, exist_ok=True)
os.makedirs(SAVES_DIR_ENV, exist_ok=True)

# Inicialização Blindada do App
app = Flask(__name__, static_folder=BASE_DIR, static_url_path="/")
app.secret_key = SECRET_KEY

# Configuração Oficial do Flask-Session (Pronto para escalar para Redis se necessário)
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = SESSION_DIR_ENV
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)

Session(app)
CORS(app, supports_credentials=True)

class WebUIHandler(UIHandler):
    def __init__(self):
        self.buffer = [] # Buffer de memória estruturado (Fim do sys.stdout!)
        
    def limpar(self): 
        self.buffer.append("@@CLEAR@@")
        
    def pausar(self, segs): 
        pass
        
    def exibir(self, texto): 
        self.animar(texto, 0.015)
        
    def animar(self, texto, tempo=0.03, cor="", jogo=None):
        cor_nome = "verde"
        if cor == DOS_BRANCO: cor_nome = "branco"
        elif cor == DOS_AMARELO: cor_nome = "amarelo"
        elif cor == DOS_VERMELHO: cor_nome = "vermelho"
        
        if jogo and getattr(jogo, 'fast_mode', False): tempo = 0
        ms = int(tempo * 1000)
        self.buffer.append(f"@@TYPE@@{cor_nome}@@{ms}@@{texto}")
        
    def obter_input(self, prompt_text): 
        return ""

def ansi_para_html(texto_ansi):
    import re
    mapa_cores = { DOS_VERDE: "verde", DOS_BRANCO: "branco", DOS_AMARELO: "amarelo", DOS_VERMELHO: "vermelho" }
    padrao = re.compile("(" + "|".join(re.escape(c) for c in list(mapa_cores.keys()) + [RESET]) + ")")
    partes = padrao.split(texto_ansi)
    html, aberto = [], False
    for parte in partes:
        if parte in mapa_cores:
            if aberto: html.append("</span>")
            html.append(f'<span class="{mapa_cores[parte]}">')
            aberto = True
        elif parte == RESET:
            if aberto: html.append("</span>"); aberto = False
        else: html.append(parte)
    if aberto: html.append("</span>")
    return "".join(html)

def obter_caminho_autosave(sid):
    return Path(SAVES_DIR_ENV) / f"autosave_{sid}.json"

def carregar_save_web(jogo):
    sid = session.get("sid")
    if not sid: return False
    caminho = obter_caminho_autosave(sid)
    if caminho.exists():
        try:
            dados = json.loads(caminho.read_text(encoding="utf-8"))
            novo_jogo = GameState.from_dict(dados)
            for k, v in novo_jogo.__dict__.items():
                if k != 'ui_handler':
                    setattr(jogo, k, v)
            return True
        except Exception as e:
            logger.error(f"Erro ao carregar save da web: {e}")
    return False

def salvar_save_web(jogo):
    sid = session.get("sid")
    if not sid: return
    try:
        caminho = obter_caminho_autosave(sid)
        caminho.write_text(json.dumps(jogo.to_dict(), ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        logger.error(f"Erro ao Gerar Save: {e}")

def gerar_resposta_json(jogo):
    linhas = []
    saidas, hp, luz, inv, sala = [], "...", "...", [], "BOOT"
    
    if jogo:
        # Pega as linhas direto do buffer do UIHandler e depois limpa o buffer
        if hasattr(jogo.ui_handler, 'buffer'):
            linhas = [ansi_para_html(linha) for linha in jogo.ui_handler.buffer if linha.strip() != ""]
            jogo.ui_handler.buffer.clear()
            
        if getattr(jogo, 'estado_atual', "") not in ["FIM", "MENU", "AGUARDANDO_DIR"] and jogo.sala_atual in jogo.mapa:
            chaves_ignoradas = ["descrição", "itens", "inspecionaveis", "cofre_important", "cadeira"]
            saidas = [k.title() for k in jogo.mapa[jogo.sala_atual].keys() if k not in chaves_ignoradas and isinstance(jogo.mapa[jogo.sala_atual][k], str)]
            
        hp = jogo.hp if not getattr(jogo, 'god_mode', False) else "∞"
        luz = jogo.turnos_luz if not getattr(jogo, 'god_mode', False) else "∞"
        inv = jogo.inventario
        sala = jogo.sala_atual.upper() if jogo.estado_atual not in ["MENU", "AGUARDANDO_DIR"] else "SISTEMA"
        
    return jsonify({"linhas": linhas, "estado": {"hp": hp, "luz": luz, "inventario": inv, "sala": sala, "saidas": saidas}})



@app.route("/")
def raiz(): return send_from_directory(BASE_DIR, "index.html")
@app.route("/style.css")
def serve_css(): return send_from_directory(BASE_DIR, "style.css")
@app.route("/script.js")
def serve_js(): return send_from_directory(BASE_DIR, "script.js")

@app.errorhandler(404)
@app.errorhandler(405)
def page_not_found(e):
    return send_from_directory(BASE_DIR, "index.html")

@app.route('/iniciar', methods=['GET'])
def iniciar_jogo():
    session.clear()
    session.permanent = True
    session["sid"] = str(uuid.uuid4())
    session["jogo"] = GameState()
    
    jogo = session["jogo"]
    jogo.ui_handler = WebUIHandler()
    jogo.estado_atual = "AGUARDANDO_DIR"
    
    captura = io.StringIO()
    sys.stdout = captura
    imprimir_tela_boot(jogo.ui_handler)
    sys.stdout = sys.__stdout__
    
    session.modified = True
    return gerar_resposta_json(captura, jogo)

@app.route('/comando', methods=['GET', 'POST'])
def receber_comando():
    if request.method == 'GET':
        return send_from_directory(BASE_DIR, "index.html")

    jogo = None

    try:
        if "jogo" not in session:
            session["sid"] = str(uuid.uuid4())
            session["jogo"] = GameState()
            session.permanent = True
            
        jogo = session["jogo"]
        
        # Injeta um handler novo e limpo para cada requisição HTTP
        jogo.ui_handler = WebUIHandler()

        dados = request.json
        comando = dados.get('comando', '')
        sid = session.get("sid")
        tem_save = sid and obter_caminho_autosave(sid).exists() if sid else False

        processar_fluxo_jogo(comando, jogo, tem_save=tem_save, callback_load_save=carregar_save_web)

        if getattr(jogo, 'estado_atual', "") in ["JOGO", "COMBATE_ANIMATRONICO"]:
            salvar_save_web(jogo)

        session.modified = True

    except Exception as e:
        logging.exception(f"Erro critico de rota: {e}")
        if jogo and hasattr(jogo, 'ui_handler'):
            jogo.ui_handler.buffer.append(f"@@TYPE@@vermelho@@0@@[ERRO INTERNO]: O servidor falhou ao processar a ação.")
            # Esconde o trace do usuário em produção!
            if app.debug:
                jogo.ui_handler.buffer.append(f"@@TYPE@@amarelo@@0@@Detalhes (Apenas em Debug): {str(e)}")

    # Chama o gerador sem precisar passar o StringIO!
    return gerar_resposta_json(jogo)

if __name__ == '__main__':
    app.run(debug=True, port=5000)