import sys
import random
from state import GameState, QuitGameException, salvar_autosave, carregar_autosave, AUTOSAVE_FILE
from commands import processar_comando, normalizar
from ui import default_ui, DOS_VERDE, DOS_BRANCO, DOS_AMARELO, DOS_VERMELHO, RESET
from views import (imprimir_tela_boot, imprimir_menu_dificuldade, imprimir_tutorial, 
                   imprimir_contexto_sala, dar_tela_de_morte, rodar_final)
from minigames import MinigameMinotauro, MinigameSeguranca
from utils import extrair_argumentos

# ==========================================
# EVENTOS DE TEMPO E MOVIMENTAÇÃO DO MAPA
# ==========================================
def atualizar_eventos_de_tempo(jogo):
    ui = jogo.ui_handler or default_ui
    
    # Modo Deus ignora as restrições de tempo
    if getattr(jogo, 'god_mode', False):
        jogo.hp = 9999
        jogo.turnos_luz = 9999
        return

    if jogo.turnos_luz > 0:
        jogo.turnos_luz -= 1
        jogo.turnos_no_escuro = 0
        if jogo.turnos_luz == 0:
            ui.exibir("\n A escuridão volta a dominar... Sua fonte de luz se apagou")
            ui.pausar(1.5)
    else:
        jogo.turnos_no_escuro += 1
        if jogo.turnos_no_escuro == 3: 
            ui.exibir("\n As sombras parecem se mexer nos cantos da sua visão...")
        elif jogo.turnos_no_escuro == 5: 
            ui.exibir("\n Você escuta alguém sussurrando seu nome bem baixinho na escuridão...")
            
        chance_sombra = min(1 + (jogo.turnos_no_escuro * 2), 20) 
        if random.randint(1, 100) <= chance_sombra:
            ui.exibir("\n" + "="*50)
            ui.exibir("Na escuridão total, dois olhos brancos se abrem a centímetros do seu rosto.")
            ui.exibir("'Você não devia ter voltado, Rogério.'")
            ui.pausar(4)
            ui.exibir("\n[ FINAL ???: MENTE FRATURADA ]")
            jogo.sala_atual = "morte"

    if getattr(jogo, 'incendio', False):
        jogo.turnos_fuga -= 1
        ui.exibir(f"\n O RESTAURANTE ESTÁ DESMORONANDO ({jogo.turnos_fuga} turnos para fugir)")
        if jogo.turnos_fuga <= 0:
            ui.exibir("\n O teto desaba sobre você. O fogo consome o que restou.")
            jogo.sala_atual = "morte"

    if jogo.turnos_enjoado > 0:
        ui.exibir("\n Você está enjoado e com tontura... Seus olhos embaçam.")
        if jogo.turnos_luz > 0: jogo.turnos_luz -= 1
        jogo.turnos_enjoado -= 1

    if jogo.dificuldade_escolhida == "NORMAL":
        jogo.turnos_mesma_sala += 1
        if jogo.turnos_mesma_sala == jogo.turnos_perseguidor_aviso:
            ui.exibir("\n Você escuta ruídos metálicos pesados ecoando no corredor próximo...")
        elif jogo.turnos_mesma_sala == jogo.turnos_perseguidor_morte:
            ui.exibir("\n" + "="*50 + "\nVocê ficou muito tempo parado. A porta é arrombada\n" + "="*50)
            ui.pausar(4)
            jogo.sala_atual = "morte"
            
    elif jogo.dificuldade_escolhida == "PESADELO":
        if jogo.posicao_perseguidor != "morte" and jogo.sala_atual not in ["saida", "cama", "final_bom", "morte", "tubo de ventilação"]: 
            sala_monstro = jogo.mapa.get(jogo.posicao_perseguidor, {})
            conexoes = [v for k, v in sala_monstro.items() if k not in ["descrição", "itens", "inspecionaveis"] and v in jogo.mapa and v not in ["morte", "saida", "cama"]]
            
            if conexoes and random.random() < 0.40: 
                jogo.posicao_perseguidor = random.choice(conexoes)
            
            if jogo.posicao_perseguidor == jogo.sala_atual:
                ui.exibir("\n" + "="*50)
                ui.exibir(f"{DOS_VERMELHO}A porta quebra. Ela te encontrou{RESET}")
                ui.pausar(3)
                jogo.sala_atual = "morte"
            else:
                conexoes_jogador = [v for k, v in jogo.mapa[jogo.sala_atual].items() if k not in ["descrição", "itens", "inspecionaveis"] and isinstance(v, str)]
                if jogo.posicao_perseguidor in conexoes_jogador:
                    ui.exibir(f"\n{DOS_AMARELO} O chão vibra. Você ouve passos de metal maciço na sala ao lado...{RESET}")


# ==========================================
# MOTOR PRINCIPAL (GAME LOOP)
# ==========================================
if __name__ == "__main__":
    # Inicializa o estado do jogo injetando o UI Padrão do Terminal (desacoplado)
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
            
            # --- TELA DE BOOT ---
            if jogo.estado_atual == "AGUARDANDO_DIR":
                if comando in ["cls", "limpar", "clear", "clean"]:
                    ui.limpar()
                    imprimir_tela_boot(ui)
                elif comando == "dir":
                    ui.limpar()
                    ui.exibir(f"{DOS_BRANCO} Volume in drive A is VILLASBOAS{RESET}")
                    ui.exibir(f"{DOS_BRANCO} Directory of A:\\{RESET}\n")
                    ui.exibir(f"{DOS_VERDE}COMMAND  COM          47.845  02-11-1982  6:00a{RESET}")
                    ui.exibir(f"{DOS_VERDE}SEGURA   SYS           2.048  02-11-1982  6:00a{RESET}")
                    ui.exibir(f"{DOS_VERDE}NOTURNO  EXE          18.204  02-11-1982  6:00a{RESET}")
                    ui.exibir(f"{DOS_VERDE}DESKTOP  <DIR>        197.78  24-07-2007  4:00a{RESET}")
                    ui.exibir(f"{DOS_VERDE}SAVES    <DIR>        358.21  23-07-2008  4:00a{RESET}")
                    ui.exibir(f"{DOS_VERDE}PICTURE  <DIR>        666.00  05-11-1994  4:00a{RESET}")
                    ui.exibir(f"{DOS_VERDE}VALID    <DIR>        2.7801  24-07-2007  4:00a{RESET}")
                    ui.exibir(f"{DOS_AMARELO}       3 file(s)        68.097 bytes{RESET}")
                    ui.exibir(f"{DOS_AMARELO}       4 dir(s)        655.360 bytes free{RESET}\n")
                    jogo.estado_atual = "MENU"
                    imprimir_menu_dificuldade(ui, tem_autosave=AUTOSAVE_FILE.exists())
                else:
                    ui.exibir(f"{DOS_VERMELHO}Bad command or file name{RESET}")
                    ui.exibir(f"{DOS_VERDE}Digite {DOS_BRANCO}dir{DOS_VERDE} para acessar os diretórios:{RESET}")

            # --- TELA DE MENU ---
            elif jogo.estado_atual == "MENU":
                if comando in ["cls", "limpar", "clear", "clean"]:
                    ui.limpar()
                    imprimir_menu_dificuldade(ui, tem_autosave=AUTOSAVE_FILE.exists())
                elif comando == "4" and AUTOSAVE_FILE.exists():
                    ui.limpar()
                    if carregar_autosave(jogo):
                        ui.exibir(f"{DOS_VERDE}JOGO RESTAURADO COM SUCESSO DO ÚLTIMO AUTOSAVE.{RESET}\n")
                        imprimir_contexto_sala(jogo)
                    else:
                        ui.exibir(f"{DOS_VERMELHO}Falha ao ler o Autosave.{RESET}")
                        imprimir_menu_dificuldade(ui, tem_autosave=AUTOSAVE_FILE.exists())
                elif comando in ["1", "2", "3"]:
                    ui.limpar()
                    if comando == "1":
                        jogo.dificuldade_escolhida = "NORMAL"
                        jogo.hp = 3; jogo.furia_noite = 1; jogo.energia_min_noite = 100; jogo.energia_max_noite = 100
                        ui.exibir(f"{DOS_VERDE}MODO NORMAL SELECIONADO. INICIANDO JOGO.EXE...{RESET}\n")
                    elif comando == "2":
                        jogo.dificuldade_escolhida = "PESADELO"
                        jogo.hp = 2; jogo.furia_noite = 2; jogo.energia_min_noite = 70; jogo.energia_max_noite = 82
                        ui.exibir(f"{DOS_VERMELHO}MODO PESADELO SELECIONADO. BOA SORTE.{RESET}\n")
                    elif comando == "3":
                        jogo.dificuldade_escolhida = "NORMAL"
                        jogo.fast_mode = True
                        jogo.hp = 3; jogo.furia_noite = 1; jogo.energia_min_noite = 100; jogo.energia_max_noite = 100
                        ui.exibir(f"{DOS_AMARELO}MODO RÁPIDO SELECIONADO. DELAYS DE DIGITAÇÃO DESATIVADOS.{RESET}\n")

                    jogo.estado_atual = "JOGO"
                    imprimir_tutorial(ui)
                    ui.exibir(f"{DOS_BRANCO}Você entra no restaurante. Sua lanterna velha dá três piscadas fracas...{RESET}")
                    ui.exibir(f"{DOS_AMARELO}[AVISO DO SISTEMA]: BATERIA DA LANTERNA EM 5%. PROCURAR OUTRA FONTE DE LUZ EM ATÉ 3 TURNOS.{RESET}")
                    imprimir_contexto_sala(jogo)
                elif comando == "2007":
                    ui.limpar()
                    jogo.dificuldade_escolhida = "GOD MODE"
                    jogo.god_mode = True
                    jogo.fast_mode = True
                    jogo.hp = 9999; jogo.furia_noite = 0; jogo.energia_min_noite = 9999; jogo.energia_max_noite = 9999
                    jogo.turnos_luz = 9999
                    jogo.estado_atual = "JOGO"
                    ui.exibir(f"{DOS_AMARELO}MODO DEUS ATIVADO. ACESSO AOS BASTIDORES CONCEDIDO.{RESET}\n")
                    ui.exibir(f"{DOS_BRANCO}Você entra no restaurante. Sua lanterna brilha com a força de uma estrela...{RESET}")
                    imprimir_contexto_sala(jogo)
                else:
                    ui.exibir(f"{DOS_VERMELHO}OPÇÃO INVÁLIDA. DIGITE UMA OPÇÃO DO MENU.{RESET}")

            # --- CORPO PRINCIPAL DO JOGO ---
            elif jogo.estado_atual in ["JOGO", "COMBATE_ANIMATRONICO"]:
                if comando in ["cls", "limpar", "clear", "clean"]:
                    ui.limpar()
                    imprimir_contexto_sala(jogo)
                
                # Checagem de ativação de Minigames pelo mapa
                elif jogo.sala_atual == "sala de energia" and not getattr(jogo, 'fios_cortados_inventario', False):
                    jogo.minigame_atual = MinigameMinotauro(jogo)
                    jogo.estado_atual = "MINIGAME_MINOTAURO"
                    jogo.minigame_atual.imprimir_status()
                elif jogo.sala_atual == "cadeira" and not getattr(jogo, 'noite_vencida', False):
                    jogo.minigame_atual = MinigameSeguranca(jogo)
                    jogo.estado_atual = "MINIGAME_SEGURANCA"
                    jogo.minigame_atual.imprimir_status()
                else:
                    # Passa o comando para o Parser Inteligente e abstraído no CLI
                    gastou_turno = processar_comando(comando_bruto, jogo, jogo.mapa)
                    if gastou_turno: 
                        atualizar_eventos_de_tempo(jogo)
                    
                    if jogo.sala_atual == "morte":
                        dar_tela_de_morte(jogo)
                    elif jogo.sala_atual == "saida":
                        rodar_final("saida", jogo)
                    elif jogo.sala_atual == "cama":
                        rodar_final("cama", jogo)
                    elif jogo.sala_atual == "hall de entrada" and getattr(jogo, 'noite_vencida', False):
                        if getattr(jogo, 'incendio', False):
                            rodar_final("verdadeiro", jogo)
                        else:
                            rodar_final("final_bom", jogo)
                    elif jogo.estado_atual == "COMBATE_ANIMATRONICO":
                        pass 
                    else:
                        imprimir_contexto_sala(jogo)
                        
            # --- LÓGICA DE MINIGAMES DE SOBREVIVÊNCIA ---
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

            # Godmode contínuo
            if getattr(jogo, 'god_mode', False):
                jogo.hp = 9999
                jogo.turnos_luz = 9999
                if jogo.minigame_atual:
                    if isinstance(jogo.minigame_atual, MinigameMinotauro): jogo.minigame_atual.bateria = 9999
                    elif isinstance(jogo.minigame_atual, MinigameSeguranca): jogo.minigame_atual.energia = 9999
                        
            # Salva no disco invisivelmente a cada turno!
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