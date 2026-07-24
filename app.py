import os
import sys
import logging
import json
import uuid
import time


try:
    import redis
except ImportError:
    redis = None

from datetime import timedelta
from pathlib import Path
from logging.handlers import RotatingFileHandler

from pymongo import MongoClient
from flask import Flask, request, jsonify, session, send_from_directory, redirect
from pydantic import BaseModel, Field, ValidationError
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from cachetools import TTLCache

from state import GameState
from ui import UIHandler, DOS_VERDE, DOS_BRANCO, DOS_AMARELO, DOS_VERMELHO, RESET
from engine import processar_fluxo_jogo
from views import imprimir_tela_boot

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# --- LOGGING ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
log_file = os.path.join(BASE_DIR, "villas_boas.log")
file_handler = RotatingFileHandler(log_file, maxBytes=10_000_000, backupCount=5, encoding="utf-8")
file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
logging.getLogger().addHandler(file_handler)
logger = logging.getLogger(__name__)

# --- CONFIGURAÇÃO ---
SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "DEV_SECRET_DO_NOT_USE_IN_PROD_1982")
if os.environ.get("RENDER") or os.environ.get("RAILWAY_STATIC_URL"):
    assert SECRET_KEY != "DEV_SECRET_DO_NOT_USE_IN_PROD_1982", "CRÍTICO: FLASK_SECRET_KEY não configurada em produção! Abortando boot."

SAVES_DIR_ENV = os.environ.get("SAVES_DIR", os.path.join(BASE_DIR, "saves"))
os.makedirs(SAVES_DIR_ENV, exist_ok=True)

# --- MONGODB ---
MONGO_URI = os.environ.get("MONGO_URI")
if MONGO_URI:
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client["villasboas_db"]
    saves_collection = db["saves"]
    telemetry_collection = db["telemetry"]
    logger.info("Conectado ao MongoDB com sucesso...")
else:
    mongo_client = None
    logger.warning("⚠ Rodando sem Banco de Dados. Usando arquivos locais.")

# --- INICIALIZAÇÃO FLASK ---
app = Flask(__name__, static_folder=BASE_DIR, static_url_path="/")
app.secret_key = SECRET_KEY
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)
CORS(app, supports_credentials=True)

limiter = Limiter(key_func=get_remote_address, app=app, storage_uri="memory://")



REDIS_URL = os.environ.get("REDIS_URL")

if REDIS_URL and redis is not None:
    try:
        redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
        redis_client.ping()
        MEMORIA_SESSOES = redis_client
        logger.info("Conectado ao Redis com sucesso.")
    except Exception as e:
        logger.error(f"Falha ao conectar no Redis: {e}. Caindo para TTLCache.")
        MEMORIA_SESSOES = TTLCache(maxsize=1000, ttl=3600)
else:
    logger.info("Usando TTLCache na memória RAM local.")
    MEMORIA_SESSOES = TTLCache(maxsize=1000, ttl=3600)



# --- SEGURANÇA E SCHEMAS ---
class ComandoRequest(BaseModel):
    comando: str = Field(default="", max_length=256)

def obter_sid_seguro():
    """Garante que o SID lido do cookie é um UUID válido e não um script de injeção"""
    sid_bruto = session.get("sid")
    if not sid_bruto:
        return None
    try:
        return str(uuid.UUID(str(sid_bruto)))
    except (ValueError, TypeError, AttributeError):
        logger.warning(f"Alerta de Segurança: SID inválido/adulterado: {sid_bruto}")
        return None

# --- CLASSES AUXILIARES ---
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

def registrar_telemetria(evento, sala, dificuldade, detalhes=""):
    if not mongo_client: return
    try:
        telemetry_collection.insert_one({
            "evento": evento,              
            "sala": sala,                  
            "dificuldade": dificuldade,    
            "detalhes": detalhes,          
            "timestamp": time.time()
        })
    except Exception as e:
        logger.error(f"Erro na telemetria: {e}")

# --- BANCO DE DADOS: CARREGAR E SALVAR ---
def carregar_save_web(jogo):
    sid = obter_sid_seguro()
    if not sid: return False

    if mongo_client:
        try:
            doc = saves_collection.find_one({"sid": sid})
            if doc and "dados" in doc:
                novo_jogo = GameState.from_dict(doc["dados"])
                for k, v in novo_jogo.__dict__.items():
                    if k != 'ui_handler':
                        setattr(jogo, k, v)
                return True
        except Exception as e:
            logger.exception(f"Erro ao buscar save no MongoDB: {e}")
    else:
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
                logger.exception(f"Erro ao carregar save local: {e}")
                
    return False

def salvar_save_web(jogo):
    sid = obter_sid_seguro()
    if not sid: return
    
    if mongo_client:
        try:
            saves_collection.update_one(
                {"sid": sid},
                {"$set": {"sid": sid, "dados": jogo.to_dict()}},
                upsert=True
            )
        except Exception as e:
            logger.exception(f"Erro ao salvar progresso no MongoDB: {e}")
    else:
        try:
            caminho = obter_caminho_autosave(sid)
            caminho.write_text(json.dumps(jogo.to_dict(), ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            logger.exception(f"Erro ao gerar autosave local: {e}")

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
        
    return jsonify({
        "linhas": linhas,
        "estado": {
            "hp": hp,
            "luz": luz,
            "inventario": inv,
            "sala": sala,
            "saidas": saidas
        }
    })

# --- ROTAS PRINCIPAIS ---
@app.route("/")
def raiz(): return send_from_directory(BASE_DIR, "index.html")

@app.route("/ping")
def ping(): return "Estou vivo!", 200

@app.route("/style.css")
def serve_css():
    if os.path.exists(os.path.join(BASE_DIR, "style.min.css")):
        return send_from_directory(BASE_DIR, "style.min.css")
    return send_from_directory(BASE_DIR, "style.css")

@app.route("/script.js")
def serve_js():
    if os.path.exists(os.path.join(BASE_DIR, "script.min.js")):
        return send_from_directory(BASE_DIR, "script.min.js")
    return send_from_directory(BASE_DIR, "script.js")

@app.errorhandler(404)
@app.errorhandler(405)
def page_not_found(e):
    return send_from_directory(BASE_DIR, "index.html")

@app.route('/iniciar', methods=['GET'])
def iniciar_jogo():
    session.clear()
    sid = str(uuid.uuid4())
    session["sid"] = sid
    session.permanent = True
    session.modified = True 
    
    jogo = GameState()
    jogo.ui_handler = WebUIHandler()
    jogo.estado_atual = "AGUARDANDO_DIR"
    
    MEMORIA_SESSOES[sid] = jogo
    
    imprimir_tela_boot(jogo.ui_handler)
    
    resposta = gerar_resposta_json(jogo)
    resposta.headers["Cache-Control"] = "no-store"
    return resposta

@app.route('/comando', methods=['GET', 'POST'])
@limiter.limit("60 per minute")
@limiter.limit("500 per hour")
def receber_comando():
    if request.method == 'GET':
        return send_from_directory(BASE_DIR, "index.html")

    sid = obter_sid_seguro()
    
    if not sid or sid not in MEMORIA_SESSOES:
        sid = str(uuid.uuid4())
        session["sid"] = sid
        session.permanent = True
        session.modified = True
        
        MEMORIA_SESSOES[sid] = GameState()
        MEMORIA_SESSOES[sid].estado_atual = "AGUARDANDO_DIR" 
        
    jogo = MEMORIA_SESSOES[sid]
    jogo.ui_handler = WebUIHandler()

    dados = request.json or {}
    try:
        requisicao = ComandoRequest(**dados)
        comando = requisicao.comando
    except ValidationError:
        return jsonify({
            "linhas": ["@@TYPE@@vermelho@@15@@[ ERRO DE SEGURANÇA ] O formato do comando enviado é inválido ou excede 256 caracteres."],
            "estado": {}
        }), 400

    tem_save = obter_caminho_autosave(sid).exists()

    try:
        processar_fluxo_jogo(comando, jogo, tem_save=tem_save, callback_load_save=carregar_save_web)

        if getattr(jogo, 'estado_atual', "") in ["JOGO", "COMBATE_ANIMATRONICO"]:
            salvar_save_web(jogo)

    except Exception as e:
        logger.exception(f"Erro critico na Engine: {e}")
        jogo.ui_handler.buffer.append(f"@@TYPE@@vermelho@@0@@[ERRO INTERNO]: O servidor falhou ao processar a ação.")
        if app.debug:
            jogo.ui_handler.buffer.append(f"@@TYPE@@amarelo@@0@@Detalhes (Apenas em Debug): {str(e)}")

    return gerar_resposta_json(jogo)

# --- ROTAS EXTRAS (Achievements, Telemetry, Share) ---
@app.route('/achievements', methods=['GET'])
def listar_conquistas():
    sid = obter_sid_seguro()
    if not sid or sid not in MEMORIA_SESSOES:
        return jsonify({"erro": "Sessão não encontrada", "conquistas": []})
    
    jogo = MEMORIA_SESSOES[sid]
    conquistas = getattr(jogo, 'conquistas', [])
    return jsonify({"conquistas": conquistas, "total": len(conquistas)})

@app.route('/admin/analytics', methods=['GET'])
def ver_telemetria():
    if not mongo_client: return "Sem banco de dados."
    mortes = telemetry_collection.count_documents({"evento": "MORTE"})
    vitorias = telemetry_collection.count_documents({"evento": "VITORIA"})
    return jsonify({"mortes_totais": mortes, "vitorias_totais": vitorias})

@app.route('/share/generate', methods=['GET'])
def gerar_link_compartilhamento():
    sid = obter_sid_seguro()
    if not sid: return jsonify({"erro": "Sem save ativo"})
    url_share = f"{request.host_url}share/{sid}"
    return jsonify({"link": url_share})

@app.route('/share/<save_id>', methods=['GET'])
def carregar_save_compartilhado(save_id):
    if not mongo_client:
        return "Banco de dados desativado. Não é possível compartilhar.", 400
        
    doc = saves_collection.find_one({"sid": save_id})
    if not doc:
        return "Save corrompido ou não encontrado nas fitas magnéticas.", 404
        
    novo_sid = str(uuid.uuid4())
    session["sid"] = novo_sid
    session.permanent = True
    
    jogo_compartilhado = GameState.from_dict(doc["dados"])
    MEMORIA_SESSOES[novo_sid] = jogo_compartilhado
    
    saves_collection.insert_one({"sid": novo_sid, "dados": jogo_compartilhado.to_dict()})
    
    return redirect("/")


@app.route('/saves', methods=['GET'])
@limiter.limit("10 per minute")
def listar_saves_paginados():
    if not mongo_client:
        return jsonify({"erro": "Banco de dados desativado."}), 400

    try:
        
        page = request.args.get('page', 1, type=int)
        limit = 10
        skip = (page - 1) * limit

        
        cursor = saves_collection.find({}, {"_id": 0}).sort("dados.timestamp", -1).skip(skip).limit(limit)
        saves = list(cursor)
        
        
        total_saves = saves_collection.count_documents({})
        total_pages = (total_saves + limit - 1) // limit

        return jsonify({
            "page": page,
            "limit": limit,
            "total_saves": total_saves,
            "total_pages": total_pages,
            "saves": saves
        })

    except Exception as e:
        logger.error(f"Erro ao listar saves paginados: {e}")
        return jsonify({"erro": "Erro interno do servidor"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)