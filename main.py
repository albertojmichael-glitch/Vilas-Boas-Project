import logging
from pathlib import Path
from state import GameState, QuitGameException, AUTOSAVE_FILE, carregar_autosave, salvar_autosave
from ui import default_ui, DOS_VERDE, DOS_AMARELO, DOS_VERMELHO, DOS_BRANCO, RESET
from views import imprimir_tela_boot
from engine import processar_fluxo_jogo

# Configuração de Logs para o Terminal
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_local_save(jogo):
    return carregar_autosave(jogo)

if __name__ == "__main__":
    jogo = GameState(ui_handler=default_ui)
    ui = default_ui
    
    jogo.estado_atual = "AGUARDANDO_DIR"
    imprimir_tela_boot(ui)
    
    while True:
        try:
            if jogo.estado_atual == "FIM":
                ui.obter_input(f"\n{DOS_AMARELO}Aperte ENTER para sair do sistema...{RESET}")
                break
                
            comando_bruto = ui.obter_input(f"\n{DOS_VERDE}C:\\> {RESET}")
            tem_save = AUTOSAVE_FILE.exists()
            
            # Delega 100% da lógica para o Motor Unificado
            processar_fluxo_jogo(comando_bruto, jogo, tem_save=tem_save, callback_load_save=load_local_save)
            
            if jogo.estado_atual in ["JOGO", "COMBATE_ANIMATRONICO"]:
                salvar_autosave(jogo)

        except QuitGameException:
            ui.exibir(f"\n{DOS_AMARELO}Encerrando o Sistema Villas Boas. Até logo.{RESET}")
            break
        except Exception as e:
            logging.exception("Erro inesperado no loop principal da CLI")
            ui.exibir(f"\n{DOS_VERMELHO}[ FALHA GERAL DE SISTEMA - TELA AZUL ]{RESET}")
            ui.exibir(f"{DOS_BRANCO}Ocorreu um problema inesperado. O sistema tentará prosseguir.{RESET}")
            ui.pausar(3)
            continue