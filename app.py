import os
import sys
import logging
import json
import uuid
import certifi
from datetime import timedelta
from pathlib import Path

from pymongo import MongoClient
from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS

from state import GameState
from ui import UIHandler, DOS_VERDE, DOS_BRANCO, DOS_AMARELO, DOS_VERMELHO, RESET
from engine import processar_fluxo_jogo
from views import imprimir_tela_boot

# Configuração de Logs para auditoria no Render
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# --- SEGURANÇA E CONFIGURAÇÃO ---
SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "DEV_SECRET_DO_NOT_USE_IN_PROD_1982")

if os.environ.get("RENDER"):
    assert SECRET_KEY != "DEV_SECRET_DO_NOT_USE_IN_PROD_1982", "CRÍTICO: FLASK_SECRET_KEY não configurada em produção! Abortando boot."

SAVES_DIR_ENV = os.environ.get("SAVES_DIR", os.path.join(BASE_DIR, "saves"))
os.makedirs(SAVES_DIR_ENV, exist_ok=True)

# --- CONEXÃO COM O BANCO DE DADOS (MONGODB) ---
MONGO_URI = os.environ.get("MONGO_URI")
if MONGO_URI:
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client["villasboas_db"]
    saves_collection = db["saves"]
    logging.info("🚀 Conectado ao MongoDB com sucesso!")
else:
    mongo_client = None
    logging.warning("⚠️ Rodando sem Banco de Dados. Usando arquivos locais.")

app = Flask(__name__, static_folder=BASE_DIR, static_url_path="/")
app.secret_key = SECRET_KEY
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)
CORS(app, supports_credentials=True)

# COFRE DE MEMÓRIA RAM (Blindado contra falhas de Pickling)
MEMORIA_SESSOES = {}

class WebUIHandler(UIHandler):
    def __init__(self):
        self.buffer = [] 
        
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

    if mongo_client:
        # Busca o save no Banco de Dados MongoDB
        try:
            doc = saves_collection.find_one({"sid": sid})
            if doc and "dados" in doc:
                novo_jogo = GameState.from_dict(doc["dados"])
                for k, v in novo_jogo.__dict__.items():
                    if k != 'ui_handler':
                        setattr(jogo, k, v)
                return True
        except Exception as e:
            logging.exception(f"Erro ao buscar save no MongoDB: {e}")
    else:
        # Busca o save no Disco Local (Fallback)
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
                logging.exception(f"Erro ao carregar save local: {e}")
                
    return False

def salvar_save_web(jogo):
    sid = session.get("sid")
    if not sid: return
    
    if mongo_client:
        # Salva / Atualiza o progresso no Banco de Dados MongoDB
        try:
            saves_collection.update_one(
                {"sid": sid},
                {"$set": {"sid": sid, "dados": jogo.to_dict()}},
                upsert=True
            )
        except Exception as e:
            logging.exception(f"Erro ao salvar progresso no MongoDB: {e}")
    else:
        # Salva o progresso no Disco Local (Fallback)
        try:
            caminho = obter_caminho_autosave(sid)
            caminho.write_text(json.dumps(jogo.to_dict(), ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            logging.exception(f"Erro ao gerar autosave local: {e}")

def gerar_resposta_json(jogo):
    linhas = []
    saidas, hp, luz, inv, sala = [], "...", "...", [], "BOOT"
    
    if jogo:
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
@app.route("/ping")
def ping():
    # Rota super leve apenas para o Uptime Robot bater e manter o servidor acordado
    return "Estou vivo!", 200
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
    # Cria uma sessão 100% nova e limpa da memória
    session.clear()
    sid = str(uuid.uuid4())
    session["sid"] = sid
    session.permanent = True
    
    jogo = GameState()
    jogo.ui_handler = WebUIHandler()
    jogo.estado_atual = "AGUARDANDO_DIR"
    
    # Guarda o jogo na memória RAM segura
    MEMORIA_SESSOES[sid] = jogo
    
    imprimir_tela_boot(jogo.ui_handler)
    return gerar_resposta_json(jogo)

@app.route('/comando', methods=['GET', 'POST'])
def receber_comando():
    if request.method == 'GET':
        return send_from_directory(BASE_DIR, "index.html")

    sid = session.get("sid")
    
    # Se a sessão foi perdida ou o servidor reiniciou, cria uma nova
    if not sid or sid not in MEMORIA_SESSOES:
        sid = str(uuid.uuid4())
        session["sid"] = sid
        session.permanent = True
        MEMORIA_SESSOES[sid] = GameState()
        
    jogo = MEMORIA_SESSOES[sid]
    
    # Injeta um handler novo e limpo para capturar o texto desta requisição
    jogo.ui_handler = WebUIHandler()

    dados = request.json
    comando = dados.get('comando', '')
    tem_save = obter_caminho_autosave(sid).exists()

    try:
        processar_fluxo_jogo(comando, jogo, tem_save=tem_save, callback_load_save=carregar_save_web)

        if getattr(jogo, 'estado_atual', "") in ["JOGO", "COMBATE_ANIMATRONICO"]:
            salvar_save_web(jogo)

    except Exception as e:
        logging.exception(f"Erro critico na Engine: {e}")
        jogo.ui_handler.buffer.append(f"@@TYPE@@vermelho@@0@@[ERRO INTERNO]: O servidor falhou ao processar a ação.")
        if app.debug:
            jogo.ui_handler.buffer.append(f"@@TYPE@@amarelo@@0@@Detalhes (Apenas em Debug): {str(e)}")

    return gerar_resposta_json(jogo)

if __name__ == '__main__':
    app.run(debug=True, port=5000)