import pytest
import random
from state import GameState
from commands import processar_comando
from minigames import MinigameMinotauro
from engine import processar_fluxo_jogo


class MockUI:
    def __init__(self):
        self.buffer = [] 
        
    def limpar(self): pass
    def pausar(self, segs): pass
    def exibir(self, texto): pass
    def animar(self, texto, tempo=0.03, cor="", jogo=None): pass
    def obter_input(self, prompt_text): return ""


def test_inventario_pegar_item():
    """Unit Test: Lógica de inventário e manipulação do mapa."""
    jogo = GameState(sala_atual="01", inventario=[])
    jogo.ui_handler = MockUI()
    
    mapa_mock = {"01": {"itens": ["lanterna"]}}
    
    processar_comando("pegar lanterna", jogo, mapa_mock)
    
    assert "lanterna" in jogo.inventario
    assert "lanterna" not in mapa_mock["01"].get("itens", [])


def test_engine_transicao_menu_para_jogo():
    """Integration Test: Transição de estado da máquina (MENU -> JOGO)."""
    
    jogo = GameState(estado_atual="MENU", sala_atual="entrada")
    jogo.ui_handler = MockUI() 
    
    
    jogo.mapa = {
        "entrada": {
            "descrição": "Você está na entrada escura.",
            "itens": [],
            "inspecionaveis": {}
        }
    }
    
    
    processar_fluxo_jogo("1", jogo)
    
    assert jogo.estado_atual == "JOGO"
    assert getattr(jogo, 'dificuldade_escolhida', 'NORMAL') == "NORMAL"
    assert jogo.hp == 3
    assert getattr(jogo, 'fast_mode', False) is False


def test_minigame_minotauro_deterministico_seed_42():
    """Minigame Test: Controlando a aleatoriedade (Seed 42)."""
    random.seed(42) 
    jogo = GameState()
    jogo.ui_handler = MockUI()
    minigame = MinigameMinotauro(jogo)
    
    
    resultado = minigame.processar_turno("esperar", jogo)
    
    assert resultado == "morte"
    assert minigame.bateria == 14