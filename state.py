import copy
import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any
from data import MAPA_ORIGINAL

class QuitGameException(Exception):
    pass

@dataclass
class GameState:
    ui_handler: Any = None 
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
    
    def to_dict(self):
        d = asdict(self)
        d.pop('ui_handler', None)
        d.pop('minigame_atual', None)
        return d
        
    @classmethod
    def from_dict(cls, dados):
        return cls(**dados)

ARQUIVO_CONQUISTAS = Path("conquistas.json")
AUTOSAVE_FILE = Path("autosave.json")

def carregar_conquistas() -> List[str]:
    if ARQUIVO_CONQUISTAS.exists():
        try:
            return json.loads(ARQUIVO_CONQUISTAS.read_text(encoding="utf-8"))
        except:
            pass
    return []

def registrar_final(nome_final: str) -> bool:
    conquistas = carregar_conquistas()
    if nome_final not in conquistas:
        conquistas.append(nome_final)
        try:
            ARQUIVO_CONQUISTAS.write_text(json.dumps(conquistas, ensure_ascii=False), encoding="utf-8")
        except:
            pass
    finais_necessarios = ["mediocre", "bons_sonhos", "bom", "verdadeiro"]
    return all(f in conquistas for f in finais_necessarios)

# --- UNIFICAÇÃO DA API DE SAVE/LOAD (Sem Disquete!) ---
def salvar_autosave(estado: GameState):
    if getattr(estado, 'estado_atual', '') != "JOGO": return
    try:
        dados = estado.to_dict()
        AUTOSAVE_FILE.write_text(json.dumps(dados, ensure_ascii=False, indent=4), encoding="utf-8")
        return True
    except:
        return False

def carregar_autosave(estado: GameState) -> bool:
    if AUTOSAVE_FILE.exists():
        try:
            dados = json.loads(AUTOSAVE_FILE.read_text(encoding="utf-8"))
            novo_estado = GameState.from_dict(dados)
            for key, value in asdict(novo_estado).items():
                if key not in ['ui_handler', 'minigame_atual']:
                    setattr(estado, key, value)
            return True
        except:
            pass
    return False