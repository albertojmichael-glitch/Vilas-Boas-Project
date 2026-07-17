import sys
import random
import logging
from pathlib import Path
from state import GameState, QuitGameException, salvar_autosave, carregar_autosave, AUTOSAVE_FILE
from commands import processar_comando, normalizar
from ui import default_ui, DOS_VERDE, DOS_BRANCO, DOS_AMARELO, DOS_VERMELHO, RESET
from views import (imprimir_tela_boot, imprimir_menu_dificuldade, imprimir_tutorial, 
                   imprimir_contexto_sala, dar_tela_de_morte, rodar_final)
from minigames import MinigameMinotauro, MinigameSeguranca
from utils import extrair_argumentos, atualizar_eventos_de_tempo

# Configuração profissional de logging para o Terminal
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
            comando = normalizar(comando_bruto)
            
            if jogo.estado_atual == "AGUARDANDO_DIR":
                if comando in ["cls", "limpar", "clear", "clean"]:
                    ui.limpar()
                    imprimir_tela_boot(ui)
                elif comando == "dir":
                    ui.limpar()
                    ui.exibir(f"{DOS_BRANCO} Volume in drive A is VILLASBOAS{RESET}")
                    ui.exibir(f"{DOS_BRANCO} Directory of A:\\{RESET}\n")
                    ui.animar(f"{DOS_VERDE}COMMAND  COM          47.845  02-11-1982  6:00a{RESET}", 0.01, jogo=jogo)
                    ui.animar(f"{DOS_VERDE}SEGURA   SYS           2.048  02-11-1982  6:00a{RESET}", 0.01, jogo=jogo)
                    ui.animar(f"{DOS_VERDE}NOTURNO  EXE          18.204  02-11-1982  6:00a{RESET}", 0.01, jogo=jogo)
                    ui.animar(f"{DOS_VERDE}DESKTOP  &lt;DIR&gt;        197.78  24-07-2007  4:00a{RESET}", 0.01, jogo=jogo)
                    ui.animar(f"{DOS_VERDE}SAVES    &lt;DIR&gt;        358.21  23-07-2008  4:00a{RESET}", 0.01, jogo=jogo)
                    ui.animar(f"{DOS_VERDE}PICTURE  &lt;DIR&gt;        666.00  05-11-1994  4:00a{RESET}", 0.01, jogo=jogo)
                    ui.animar(f"{DOS_VERDE}VALID    &lt;DIR&gt;        2.7801  24-07-2007  4:00a{RESET}", 0.01, jogo=jogo)
                    ui.exibir(f"{DOS_AMARELO}       3 file(s)        68.097 bytes{RESET}")
                    ui.exibir(f"{DOS_AMARELO}       4 dir(s)        655.360 bytes free{RESET}\n")
                    jogo.estado_atual = "MENU"
                    imprimir_menu_dificuldade(ui, tem_autosave=AUTOSAVE_FILE.exists(), jogo=jogo)
                else:
                    ui.exibir(f"{DOS_VERMELHO}Bad command or file name{RESET}")
                    ui.exibir(f"{DOS_VERDE}Digite {DOS_BRANCO}dir{DOS_VERDE} para acessar os diretórios:{RESET}")

            elif jogo.estado_atual == "MENU":
                tem_save_local = AUTOSAVE_FILE.exists()
                
                if comando in ["cls", "limpar", "clear", "clean"]:
                    ui.limpar()
                    imprimir_menu_dificuldade(ui, tem_autosave=tem_save_local, jogo=jogo)
                elif comando == "5" and tem_save_local:
                    ui.limpar()
                    if carregar_autosave(jogo):
                        ui.animar(f"{DOS_VERDE}JOGO RESTAURADO COM SUCESSO DO AUTOSAVE LOCAL.{RESET}\n", 0.04, jogo=jogo)
                        imprimir_contexto_sala(jogo)
                    else:
                        ui.animar(f"{DOS_VERMELHO}Falha ao ler o Autosave local.{RESET}", 0.04, jogo=jogo)
                        imprimir_menu_dificuldade(ui, tem_autosave=tem_save_local, jogo=jogo)
                elif comando in ["1", "2", "3", "4"]:
                    ui.limpar()
                    if comando == "1":
                        jogo.dificuldade_escolhida = "NORMAL"
                        jogo.fast_mode = False
                        jogo.hp = 3; jogo.furia_noite = 1; jogo.energia_min_noite = 100; jogo.energia_max_noite = 100
                        ui.animar(f"{DOS_VERDE}MODO NORMAL SELECIONADO. VELOCIDADE RETRÔ ATIVADA.{RESET}\n", 0.04, jogo=jogo)
                    elif comando == "2":
                        jogo.dificuldade_escolhida = "NORMAL"
                        jogo.fast_mode = True
                        jogo.hp = 3; jogo.furia_noite = 1; jogo.energia_min_noite = 100; jogo.energia_max_noite = 100
                        ui.animar(f"{DOS_AMARELO}MODO NORMAL COM TEXTO RÁPIDO SELECIONADO.{RESET}\n", 0.04, jogo=jogo)
                    elif comando == "3":
                        jogo.dificuldade_escolhida = "PESADELO"
                        jogo.fast_mode = False
                        jogo.hp = 2; jogo.furia_noite = 2; jogo.energia_min_noite = 70; jogo.energia_max_noite = 82
                        ui.animar(f"{DOS_VERMELHO}MODO PESADELO SELECIONADO. VELOCIDADE RETRÔ ATIVADA. BOA SORTE.{RESET}\n", 0.04, jogo=jogo)
                    elif comando == "4":
                        jogo.dificuldade_escolhida = "PESADELO"
                        jogo.fast_mode = True
                        jogo.hp = 2; jogo.furia_noite = 2; jogo.energia_min_noite = 70; jogo.energia_max_noite = 82
                        ui.animar(f"{DOS_VERMELHO}MODO PESADELO COM TEXTO RÁPIDO SELECIONADO. BOA SORTE.{RESET}\n", 0.04, jogo=jogo)

                    jogo.estado_atual = "JOGO"
                    imprimir_tutorial(ui, jogo=jogo)
                    ui.animar(f"{DOS_BRANCO}Você entra no restaurante. Sua lanterna velha dá três piscadas fracas...{RESET}", 0.04, jogo=jogo)
                    ui.animar(f"{DOS_AMARELO}[AVISO DO SISTEMA]: BATERIA DA LANTERNA EM 5%. PROCURAR OUTRA FONTE DE LUZ EM ATÉ 3 TURNOS.{RESET}", 0.04, jogo=jogo)
                    imprimir_contexto_sala(jogo)
                elif comando == "2007":
                    ui.limpar()
                    jogo.dificuldade_escolhida = "GOD MODE"
                    jogo.god_mode = True
                    jogo.hp = 9999; jogo.furia_noite = 0; jogo.energia_min_noite = 9999; jogo.energia_max_noite = 9999
                    jogo.turnos_luz = 9999
                    jogo.estado_atual = "JOGO"
                    ui.animar(f"{DOS_AMARELO}MODO DEUS ATIVADO. ACESSO AOS BASTIDORES CONCEDIDO.{RESET}\n", 0.04, jogo=jogo)
                    ui.animar(f"{DOS_BRANCO}Você entra no restaurante. Sua lanterna brilha com a força de uma estrela...{RESET}", 0.04, jogo=jogo)
                    imprimir_contexto_sala(jogo)
                else:
                    ui.exibir(f"{DOS_VERMELHO}OPÇÃO INVÁLIDA. DIGITE UMA OPÇÃO DO MENU.{RESET}")

            elif jogo.estado_atual in ["JOGO", "COMBATE_ANIMATRONICO"]:
                if comando in ["cls", "limpar", "clear", "clean"]:
                    ui.limpar()
                    imprimir_contexto_sala(jogo)
                elif jogo.sala_atual == "sala de energia" and not getattr(jogo, 'fios_cortados_inventario', False):
                    jogo.minigame_atual = MinigameMinotauro(jogo)
                    jogo.estado_atual = "MINIGAME_MINOTAURO"
                    jogo.minigame_atual.imprimir_status()
                elif jogo.sala_atual == "cadeira" and not getattr(jogo, 'noite_vencida', False):
                    jogo.minigame_atual = MinigameSeguranca(jogo)
                    jogo.estado_atual = "MINIGAME_SEGURANCA"
                    jogo.minigame_atual.imprimir_status()
                else:
                    gastou_turno = processar_comando(comando_bruto, jogo, jogo.mapa)
                    if gastou_turno: atualizar_eventos_de_tempo(jogo)
                    
                    if jogo.sala_atual == "morte":
                        dar_tela_de_morte(jogo)
                    elif jogo.sala_atual == "saida":
                        rodar_final("saida", jogo)
                    elif jogo.sala_atual == "cama":
                        rodar_final("cama", jogo)
                    elif jogo.sala_atual == "hall de entrada" and getattr(jogo, 'noite_vencida', False):
                        if getattr(jogo, 'incendio', False): rodar_final("verdadeiro", jogo)
                        else: rodar_final("final_bom", jogo)
                    elif jogo.estado_atual == "COMBATE_ANIMATRONICO":
                        pass 
                    else:
                        imprimir_contexto_sala(jogo)
                        
            elif jogo.estado_atual in ["MINIGAME_MINOTAURO", "MINIGAME_SEGURANCA"]:
                if comando in ["cls", "limpar", "clear", "clean"]:
                    ui.limpar()
                    jogo.minigame_atual.imprimir_status()
                else:
                    partes = extrair_argumentos(comando)
                    verbo = partes[0] if partes else ""
                    mapa_direcoes = {"f": "ir frente", "t": "ir atrás", "e": "ir esquerda", "d": "ir direita"}
                    if verbo in mapa_direcoes: comando = mapa_direcoes[verbo]
                    
                    resultado = jogo.minigame_atual.processar_turno(comando, jogo)
                    
                    if resultado == "morte":
                        jogo.minigame_atual = None
                        jogo.sala_atual = "morte"
                        dar_tela_de_morte(jogo)
                    elif resultado == "vitoria_minotauro":
                        jogo.minigame_atual = None
                        jogo.sala_atual = "sala dos fundos" 
                        jogo.estado_atual = "JOGO"
                        imprimir_contexto_sala(jogo)
                    elif resultado == "vitoria_seguranca":
                        jogo.minigame_atual = None
                        jogo.sala_atual = "01" 
                        jogo.estado_atual = "JOGO"
                        imprimir_contexto_sala(jogo)
                    else:
                        jogo.minigame_atual.imprimir_status()

            if getattr(jogo, 'god_mode', False):
                jogo.hp = 9999
                jogo.turnos_luz = 9999
                        
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