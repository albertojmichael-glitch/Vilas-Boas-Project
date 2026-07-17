import pytest
import random
from state import GameState
from commands import processar_comando
from minigames import MinigameMinotauro

def test_serializacao_estado():
    # Testa se o Pydantic salva e recupera os dados corretamente
    jogo = GameState(hp=2, sala_atual="01", inventario=["lanterna"])
    dados = jogo.to_dict()
    
    assert dados["hp"] == 2
    assert dados["sala_atual"] == "01"
    assert "lanterna" in dados["inventario"]
    
    jogo_restaurado = GameState.from_dict(dados)
    assert jogo_restaurado.sala_atual == "01"
    assert len(jogo_restaurado.inventario) == 1

def test_comando_ir_frente():
    # Testa a mecânica de movimentação sem depender da UI
    jogo = GameState(sala_atual="entrada")
    mapa_mock = {
        "entrada": {"frente": "sala de jantar", "itens": []},
        "sala de jantar": {"descrição": "Uma sala vazia"}
    }
    
    processar_comando("ir frente", jogo, mapa_mock)
    
    assert jogo.sala_atual == "sala de jantar"

def test_minigame_minotauro_deterministico():
    # Fixamos a "semente" do gerador aleatório para que o RNG seja previsível.
    # Com seed(42), o Minotauro SEMPRE vai atacar do mesmo lado.
    random.seed(42) 
    jogo = GameState()
    minigame = MinigameMinotauro(jogo)
    
    # Comportamento forçado da Seed 42: O boss pode atacar pela 'esquerda' na primeira rodada
    # Ajuste as asserções de acordo com a lógica fixa do seu minigame:
    minigame.processar_turno("esperar", jogo)
    
    # Exemplo: bateria gasta ao esperar
    assert minigame.bateria < 100