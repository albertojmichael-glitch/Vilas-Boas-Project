import pytest
import random
from state import GameState
from commands import processar_comando
from minigames import MinigameMinotauro
from engine import processar_fluxo_jogo

def test_inventario_pegar_item():
    """Unit Test: Lógica de inventário e manipulação do mapa."""
    jogo = GameState(sala_atual="01", inventario=[])
    mapa_mock = {"01": {"itens": ["lanterna"]}}
    
    processar_comando("pegar lanterna", jogo, mapa_mock)
    
    assert "lanterna" in jogo.inventario
    assert "lanterna" not in mapa_mock["01"].get("itens", [])

def test_engine_transicao_menu_para_jogo():
    """Integration Test: Transição de estado da máquina (MENU -> JOGO)."""
    jogo = GameState(estado_atual="MENU")
    
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
    minigame = MinigameMinotauro(jogo)
    
    # Com a Seed 42, sabemos exatamente como o gerador vai se comportar
    # Turno 1: O jogador espera. O monstro deve agir e a bateria deve cair.
    resultado = minigame.processar_turno("esperar", jogo)
    
    assert minigame.bateria == 95  # Bateria gasta por esperar
    assert minigame.turno == 1
    assert resultado != "morte" # Na seed 42, ele não ataca no turno 1