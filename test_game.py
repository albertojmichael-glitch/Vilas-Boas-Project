import pytest
from state import GameState
from commands import processar_comando
from views import imprimir_contexto_sala

# Criamos um "Robô" que joga o jogo muito rápido e sem tela para testes!
class TestUIHandler:
    def limpar(self): pass
    def pausar(self, segs): pass
    def exibir(self, texto): pass
    def animar(self, texto, tempo=0.03, cor="", jogo=None): pass
    def obter_input(self, prompt_text): 
        if "senha" in prompt_text.lower():
            return "1994"
        return ""

def test_pegar_item_simples():
    jogo = GameState(ui_handler=TestUIHandler())
    jogo.sala_atual = "balcão"
    
    assert "doce" not in jogo.inventario
    
    processar_comando("pegar doce", jogo, jogo.mapa)
    
    assert "doce" in jogo.inventario
    assert "doce" not in jogo.mapa["balcão"]["itens"]

def test_arrombar_porta_com_tesoura():
    jogo = GameState(ui_handler=TestUIHandler())
    jogo.sala_atual = "corredor"
    jogo.inventario.append("tesoura")
    
    assert jogo.mapa["corredor"]["03"] == "03"
    
    processar_comando("usar tesoura", jogo, jogo.mapa)
    
    assert jogo.mapa["corredor"]["03"] == "sala do gerador"
    assert "tesoura quebrada" in jogo.inventario

def test_abrir_cofre_com_mock_input():
    jogo = GameState(ui_handler=TestUIHandler())
    jogo.sala_atual = "01"
    
    processar_comando("abrir cofre", jogo, jogo.mapa)
    
    assert "chave dos fundos" in jogo.inventario