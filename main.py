import sys
import random
from state import GameState, QuitGameException, salvar_autosave, carregar_autosave, AUTOSAVE_FILE
from commands import processar_comando, normalizar
from ui import default_ui, DOS_VERDE, DOS_BRANCO, DOS_AMARELO, DOS_VERMELHO, RESET
from views import (imprimir_tela_boot, imprimir_menu_dificuldade, imprimir_tutorial, 
                   imprimir_contexto_sala, dar_tela_de_morte, rodar_final)
from minigames import MinigameMinotauro, MinigameSeguranca
from utils import extrair_argumentos, atualizar_eventos_de_tempo 

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
                    ui.animar(f"{DOS_VERDE}DESKTOP  <DIR>        197.78  24-07-2007  4:00a{RESET}", 0.01, jogo=jogo)
                    ui.animar(f"{DOS_VERDE}SAVES    <DIR>        358.21  23-07-2008  4:00a{RESET}", 0.01, jogo=jogo)
                    ui.animar(f"{DOS_VERDE}PICTURE  <DIR>        666.00  05-11-1994  4:00a{RESET}", 0.01, jogo=jogo)
                    ui.animar(f"{DOS_VERDE}VALID    <DIR>        2.7801  24-07-2007  4:00a{RESET}", 0.01, jogo=jogo)
                    ui.exibir(f"{DOS_AMARELO}       3 file(s)        68.097 bytes{RESET}")
                    ui.exibir(f"{DOS_AMARELO}       4 dir(s)        655.360 bytes free{RESET}\n")
                    jogo.estado_atual = "MENU"
                    imprimir_menu_dificuldade(ui, tem_autosave=AUTOSAVE_FILE.exists())
                else:
                    ui.exibir(f"{DOS_VERMELHO}Bad command or file name{RESET}")
                    ui.exibir(f"{DOS_VERDE}Digite {DOS_BRANCO}dir{DOS_VERDE} para acessar os diretórios:{RESET}")

            elif jogo.estado_atual == "MENU":
                if comando in ["cls", "limpar", "clear", "clean"]:
                    ui.limpar()
                    imprimir_menu_dificuldade(ui, tem_autosave=AUTOSAVE_FILE.exists(), jogo=jogo)
                elif comando == "4" and AUTOSAVE_FILE.exists():
                    ui.limpar()
                    if carregar_autosave(jogo):
                        ui.animar(f"{DOS_VERDE}JOGO RESTAURADO COM SUCESSO DO ÚLTIMO AUTOSAVE.{RESET}\n", 0.04, jogo=jogo)
                        imprimir_contexto_sala(jogo)
                    else:
                        ui.animar(f"{DOS_VERMELHO}Falha ao ler o Autosave.{RESET}", 0.04, jogo=jogo)
                        imprimir_menu_dificuldade(ui, tem_autosave=AUTOSAVE_FILE.exists(), jogo=jogo)
                elif comando in ["1", "2", "3"]:
                    ui.limpar()
                    if comando == "1":
                        jogo.dificuldade_escolhida = "NORMAL"
                        jogo.hp = 3; jogo.furia_noite = 1; jogo.energia_min_noite = 100; jogo.energia_max_noite = 100
                        ui.animar(f"{DOS_VERDE}MODO NORMAL SELECIONADO. INICIANDO JOGO.EXE...{RESET}\n", 0.04, jogo=jogo)
                    elif comando == "2":
                        jogo.dificuldade_escolhida = "PESADELO"
                        jogo.hp = 2; jogo.furia_noite = 2; jogo.energia_min_noite = 70; jogo.energia_max_noite = 82
                        ui.animar(f"{DOS_VERMELHO}MODO PESADELO SELECIONADO. BOA SORTE.{RESET}\n", 0.04, jogo=jogo)
                    elif comando == "3":
                        jogo.dificuldade_escolhida = "NORMAL"
                        jogo.fast_mode = True # AQUI O FAST MODE DEVE FICAR!
                        jogo.hp = 3; jogo.furia_noite = 1; jogo.energia_min_noite = 100; jogo.energia_max_noite = 100
                        ui.animar(f"{DOS_AMARELO}MODO RÁPIDO SELECIONADO. DELAYS DE DIGITAÇÃO DESATIVADOS.{RESET}\n", 0.04, jogo=jogo)

                    jogo.estado_atual = "JOGO"
                    imprimir_tutorial(ui, jogo=jogo)
                    ui.animar(f"{DOS_BRANCO}Você entra no restaurante. Sua lanterna velha dá três piscadas fracas...{RESET}", 0.04, jogo=jogo)
                    ui.animar(f"{DOS_AMARELO}[AVISO DO SISTEMA]: BATERIA DA LANTERNA EM 5%. PROCURAR OUTRA FONTE DE LUZ EM ATÉ 3 TURNOS.{RESET}", 0.04, jogo=jogo)
                    imprimir_contexto_sala(jogo)
                    
                elif comando == "2007":
                    ui.limpar()
                    jogo.dificuldade_escolhida = "GOD MODE"
                    jogo.god_mode = True
                    # A LINHA QUE QUEBRAVA A SUA IMERSÃO FOI REMOVIDA DAQUI! 
                    jogo.hp = 9999; jogo.furia_noite = 0; jogo.energia_min_noite = 9999; jogo.energia_max_noite = 9999
                    jogo.turnos_luz = 9999
                    jogo.estado_atual = "JOGO"
                    ui.animar(f"{DOS_AMARELO}MODO DEUS ATIVADO. ACESSO AOS BASTIDORES CONCEDIDO.{RESET}\n", 0.04, jogo=jogo)
                    ui.animar(f"{DOS_BRANCO}Você entra no restaurante. Sua lanterna brilha com a força de uma estrela...{RESET}", 0.04, jogo=jogo)
                    imprimir_contexto_sala(jogo)
                else:
                    ui.animar(f"{DOS_VERMELHO}OPÇÃO INVÁLIDA. DIGITE UMA OPÇÃO DO MENU.{RESET}", 0.04, jogo=jogo)

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
                elif comando in ["pular noite", "pular", "set time 06:00"] and getattr(jogo, 'god_mode', False) and jogo.estado_atual == "MINIGAME_SEGURANCA":
                    ui.exibir(f"{DOS_AMARELO}[GOD MODE] Você altera os ponteiros do universo. O relógio salta para as 06:00 instantaneamente.{RESET}")
                    jogo.minigame_atual.turno = 24 
                    resultado = jogo.minigame_atual.processar_turno("esperar", jogo) 
                    if resultado == "vitoria_seguranca":
                        jogo.minigame_atual = None
                        jogo.sala_atual = "01"
                        jogo.estado_atual = "JOGO"
                        imprimir_contexto_sala(jogo)
                elif comando in ["atacar", "bater", "chutar", "lutar"] and getattr(jogo, 'god_mode', False) and jogo.estado_atual == "MINIGAME_MINOTAURO":
                    ui.exibir(f"{DOS_AMARELO}[GOD MODE] Você corre e dá uma voadora no peito do Minotauro! Ele foge.{RESET}")
                    jogo.minigame_atual = None
                    jogo.sala_atual = "sala dos fundos"
                    jogo.estado_atual = "JOGO"
                    imprimir_contexto_sala(jogo)
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
                        jogo.mapa["sala dos fundos"]["energia"] = "A pesada porta da sala de energia está totalmente destruída."
                        ui.exibir(f"{DOS_VERDE}A porta cedeu atrás de você e travou para sempre.{RESET}")
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
                if jogo.minigame_atual:
                    if isinstance(jogo.minigame_atual, MinigameMinotauro): jogo.minigame_atual.bateria = 9999
                    elif isinstance(jogo.minigame_atual, MinigameSeguranca): jogo.minigame_atual.energia = 9999
                        
            if jogo.estado_atual in ["JOGO", "COMBATE_ANIMATRONICO"]:
                salvar_autosave(jogo)

        except QuitGameException:
            ui.exibir(f"\n{DOS_AMARELO}Encerrando o Sistema Villas Boas. Até logo.{RESET}")
            break
            
        except Exception as e:
            ui.exibir(f"\n{DOS_VERMELHO}[ FALHA GERAL DE SISTEMA - TELA AZUL ]{RESET}")
            ui.exibir(f"{DOS_BRANCO}O sistema encontrou um erro: {e}{RESET}")
            ui.pausar(3)
            continue