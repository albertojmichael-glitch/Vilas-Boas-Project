import pytest
import random
from state import GameState
from commands import processar_comando
from minigames import MinigameMinotauro
from engine import processar_fluxo_jogo

# --- MOCK UI ---
# Uma "Tela de Mentira" para que a Engine possa tentar "limpar" ou "exibir"
# coisas durante os testes sem causar crash de 'NoneType'.
class MockUI:
    def limpar(self): pass
    def pausar(self, segs): pass
    def exibir(self, texto): pass
    def animar(self, texto, tempo=0.03, cor="", jogo=None): pass
    def obter_input(self, prompt_text): return ""


def test_inventario_pegar_item():
    """Unit Test: Lógica de inventário e manipulação do mapa."""
    jogo = GameState(sala_atual="01", inventario=[])
    jogo.ui_handler = MockUI() # Injeta a tela de mentira
    
    mapa_mock = {"01": {"itens": ["lanterna"]}}
    
    processar_comando("pegar lanterna", jogo, mapa_mock)
    
    assert "lanterna" in jogo.inventario
    assert "lanterna" not in mapa_mock["01"].get("itens", [])

def test_engine_transicao_menu_para_jogo():
    """Integration Test: Transição de estado da máquina (MENU -> JOGO)."""
    jogo = GameState(estado_atual="MENU")
    jogo.ui_handler = MockUI() # Injeta a tela de mentira
    
    # Simula o jogador escolhendo a opção 1 (Modo Normal)
    processar_fluxo_jogo("1", jogo)
    
    assert jogo.estado_atual == "JOGO"
    assert jogo.dificuldade_escolhida == "NORMAL"
    assert jogo.hp == 3
    assert not jogo.fast_mode

def test_minigame_minotauro_deterministico_seed_42():
    """Minigame Test: Controlando a aleatoriedade (Seed 42)."""
    random.seed(42) 
    jogo = GameState()
    jogo.ui_handler = MockUI()
    minigame = MinigameMinotauro(jogo)
    
    # O Pytest revelou que na Seed 42 o Minotauro é implacável:
    # Se você esperar no turno 1, ele ataca, te mata e a bateria cai para 14.
    resultado = minigame.processar_turno("esperar", jogo)
    
    assert resultado == "morte"
    assert minigame.bateria == 14