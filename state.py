import copy
import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any

# Importa os dados originais para poder resetar o mapa
from data import MAPA_ORIGINAL

# Importa a interface para as mensagens do sistema
from ui import DOS_VERDE, DOS_AMARELO, DOS_VERMELHO, RESET, pausar

# ==========================================
# EXCEÇÕES DE SISTEMA
# ==========================================
class QuitGameException(Exception):
    """Exceção customizada para fechar o jogo de forma segura e elegante."""
    pass

# ==========================================
# ESTADO GERAL DO JOGO (DATACLASS)
# ==========================================
@dataclass
class GameState:
    hp: int = 3
    inventario: List[str] = field(default_factory=lambda: ["lanterna"])
    turnos_luz: int = 3
    turnos_no_escuro: int = 0
    turnos_enjoado: int = 0
    sala_atual: str = "entrada"
    turnos_mesma_sala: int = 0
    dificuldade_escolhida: str = "NORMAL"
    chance_sprint_minotauro: int = 15
    turnos_perseguidor_aviso: int = 3
    turnos_perseguidor_morte: int = 5
    energia_min_noite: int = 90
    energia_max_noite: int = 100
    furia_noite: int = 1
    fios_cortados_inventario: bool = False
    noite_vencida: bool = False
    incendio: bool = False
    turnos_fuga: int = 5
    isqueiro_usos: int = 3
    posicao_perseguidor: str = "palco"
    estado_atual: str = "MENU"
    minigame_atual: Any = None
    god_mode: bool = False
    alberto_desativado: bool = False
    fast_mode: bool = False
    mapa: Dict[str, Any] = field(default_factory=lambda: copy.deepcopy(MAPA_ORIGINAL))

    def to_dict(self) -> dict:
        d = asdict(self)
        d['minigame_atual'] = None # Nunca salva o meio do minigame para evitar bugs
        return d

    @classmethod
    def from_dict(cls, dados: dict):
        return cls(**dados)

# ==========================================
# SISTEMA DE SAVE / LOAD
# ==========================================
SAVE_FILE = Path("save_villasboas.json")

def salvar_jogo(estado: GameState) -> bool:
    if estado.minigame_atual is not None:
        print(f"{DOS_AMARELO}Você não pode salvar o jogo durante um evento!{RESET}")
        pausar(2)
        return False
        
    if "disquete" not in estado.inventario:
        print(f"{DOS_VERMELHO}ACESSO NEGADO: Você precisa de um 'disquete' na mochila para salvar.{RESET}")
        pausar(2)
        return False
    
    try:
        dados = estado.to_dict()
        SAVE_FILE.write_text(json.dumps(dados, ensure_ascii=False, indent=4), encoding="utf-8")
        
        estado.inventario.remove("disquete") # Consome o item!
        print(f"{DOS_VERDE}💾 Jogo salvo. O disquete foi consumido na leitura.{RESET}")
        pausar(1.5)
        return True
    except Exception as e:
        print(f"{DOS_VERMELHO}Erro crítico de I/O ao salvar o jogo: {e}{RESET}")
        return False

def carregar_jogo(estado: GameState) -> bool:
    if not SAVE_FILE.exists():
        print(f"{DOS_AMARELO}Nenhum arquivo de save encontrado.{RESET}")
        pausar(1.5)
        return False
        
    try:
        dados = json.loads(SAVE_FILE.read_text(encoding="utf-8"))
        novo_estado = GameState.from_dict(dados)
        
        for key, value in asdict(novo_estado).items():
            setattr(estado, key, value)
            
        print(f"{DOS_VERDE}💾 Jogo carregado com sucesso.{RESET}")
        pausar(2)
        return True
    except (json.JSONDecodeError, TypeError):
        print(f"{DOS_VERMELHO}Arquivo de save corrompido ou incompatível.{RESET}")
        return False
    except Exception as e:
        print(f"{DOS_VERMELHO}Erro desconhecido ao carregar: {e}{RESET}")
        return False


# ==========================================
# NOVO SISTEMA DE CONQUISTAS GLOBAIS
# ==========================================
ARQUIVO_CONQUISTAS = Path("conquistas.json")

def registrar_final(nome_final: str) -> bool:
    """Registra um final no disco. Retorna True se todos os 4 finais foram alcançados."""
    conquistas = []
    if ARQUIVO_CONQUISTAS.exists():
        try:
            conquistas = json.loads(ARQUIVO_CONQUISTAS.read_text(encoding="utf-8"))
        except:
            pass
    
    if nome_final not in conquistas:
        conquistas.append(nome_final)
        try:
            ARQUIVO_CONQUISTAS.write_text(json.dumps(conquistas, ensure_ascii=False), encoding="utf-8")
        except:
            pass
    
    finais_necessarios = ["mediocre", "bons_sonhos", "bom", "verdadeiro"]
    # Checa se o jogador tem os 4 finais na conta dele
    return all(f in conquistas for f in finais_necessarios)