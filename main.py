import time
import random
import sys

# 1. Importa a Interface e Cores
from ui import (DOS_VERDE, DOS_BRANCO, DOS_AMARELO, DOS_VERMELHO, 
                RESET, limpar_tela, pausar, digitar, DEBUG_MODE)

# 2. Importa os Dados Estáticos
from data import CAVEIRA_MORTE, MAX_INVENTARIO

# 3. Importa o Estado e o Sistema de Saves
from state import GameState, QuitGameException

# 4. Importa as Inteligências Artificiais
from minigames import MinigameMinotauro, MinigameSeguranca

# 5. Importa o Motor de Comandos
from commands import processar_comando, normalizar


# ==========================================
# EVENTOS DE TEMPO E MOVIMENTAÇÃO DO MAPA
# ==========================================
def atualizar_eventos_de_tempo(jogo):
    if jogo.turnos_luz > 0:
        jogo.turnos_luz -= 1
        jogo.turnos_no_escuro = 0
        if jogo.turnos_luz == 0:
            print("\n A escuridão volta a dominar... Sua fonte de luz se apagou")
            pausar(1.5)
    else:
        jogo.turnos_no_escuro += 1
        if jogo.turnos_no_escuro == 3: print("\n As sombras parecem se mexer nos cantos da sua visão...")
        elif jogo.turnos_no_escuro == 5: print("\n Você escuta alguém sussurrando seu nome bem baixinho na escuridão...")
            
        chance_sombra = min(1 + (jogo.turnos_no_escuro * 2), 20) 
        if random.randint(1, 100) <= chance_sombra:
            print("\n" + "="*50)
            print("Na escuridão total, dois olhos brancos se abrem a centímetros do seu rosto.")
            print("'Você não devia ter voltado, Rogério.'")
            pausar(4)
            print("\n[ FINAL ???: MENTE FRATURADA ]")
            jogo.sala_atual = "morte"

    if jogo.incendio:
        jogo.turnos_fuga -= 1
        print(f"\n O RESTAURANTE ESTÁ DESMORONANDO ({jogo.turnos_fuga} turnos para fugir)")
        if jogo.turnos_fuga <= 0:
            print("\n O teto desaba sobre você. O fogo consome o que restou.")
            jogo.sala_atual = "morte"

    if jogo.turnos_enjoado > 0:
        print("\n Você está enjoado e com tontura... Seus olhos embaçam.")
        if jogo.turnos_luz > 0: jogo.turnos_luz -= 1
        jogo.turnos_enjoado -= 1

    if jogo.dificuldade_escolhida == "NORMAL":
        jogo.turnos_mesma_sala += 1
        if jogo.turnos_mesma_sala == jogo.turnos_perseguidor_aviso:
            print("\n Você escuta ruídos metálicos pesados ecoando no corredor próximo...")
        elif jogo.turnos_mesma_sala == jogo.turnos_perseguidor_morte:
            print("\n" + "="*50 + "\nVocê ficou muito tempo parado. A porta é arrombada\n" + "="*50)
            pausar(4)
            jogo.sala_atual = "morte"
            
    elif jogo.dificuldade_escolhida == "PESADELO":
        if jogo.posicao_perseguidor != "morte" and jogo.sala_atual not in ["saida", "cama", "final_bom", "morte", "tubo de ventilação"]: 
            sala_monstro = jogo.mapa.get(jogo.posicao_perseguidor, {})
            conexoes = [v for k, v in sala_monstro.items() if k not in ["descrição", "itens", "inspecionaveis"] and v in jogo.mapa and v not in ["morte", "saida", "cama"]]
            
            if conexoes and random.random() < 0.40: 
                jogo.posicao_perseguidor = random.choice(conexoes)
            
            if jogo.posicao_perseguidor == jogo.sala_atual:
                print("\n" + "="*50)
                print(f"{DOS_VERMELHO}A porta quebra. Ela te encontrou{RESET}")
                pausar(3)
                jogo.sala_atual = "morte"
            else:
                conexoes_jogador = [v for k, v in jogo.mapa[jogo.sala_atual].items() if k not in ["descrição", "itens", "inspecionaveis"] and isinstance(v, str)]
                if jogo.posicao_perseguidor in conexoes_jogador:
                    print(f"\n{DOS_AMARELO} O chão vibra. Você ouve passos de metal maciço na sala ao lado...{RESET}")

# ==========================================
# BOOT DO SISTEMA
# ==========================================
def menu_inicial(jogo):
    limpar_tela()
    digitar("VILLAS-BOAS INDUSTRIES (C) 1982", 0.01, DOS_BRANCO, jogo)
    digitar("BIOS VERSION 1.04 - RELEASE 02/11/1982", 0.01, DOS_BRANCO, jogo)
    digitar("RAM CHECK: 640KB OK", 0.01, DOS_VERDE, jogo)
    digitar("DRIVE A: READY", 0.01, DOS_VERDE, jogo)
    digitar("CARREGANDO 'COMMAND.COM'....... OK\n", 0.05, DOS_VERDE, jogo)
    pausar(1)
    
    digitar("==================================================", 0.005, DOS_VERDE, jogo)
    digitar("__     _____ _     _        _ ____   ___   ____ ", 0.005, DOS_VERDE, jogo)
    digitar("\\ \\   / /_ _| |   | |      / / ___| / _ \\ / ___|", 0.005, DOS_VERDE, jogo)
    digitar(" \\ \\ / / | || |   | |     / /\\___ \\| | | |\\___ \\", 0.005, DOS_VERDE, jogo)
    digitar("  \\ V /  | || |___| |___ / /  ___) | |_| | ___) |", 0.005, DOS_VERDE, jogo)
    digitar("   \\_/  |___|_____|_____/_/  |____/ \\___/ |____/", 0.005, DOS_VERDE, jogo)
    digitar("==================================================", 0.005, DOS_VERDE, jogo)
    digitar("        SISTEMA DE SEGURANÇA INTEGRADO v1.0       ", 0.02, DOS_BRANCO, jogo)
    
    print(f"\n{DOS_BRANCO}[1] INICIAR MODO: NORMAL (Para iniciantes){RESET}")
    print(f"{DOS_VERMELHO}[2] INICIAR MODO: PESADELO (RNG Agressivo / HP Baixo){RESET}\n")
    
    while True:
        opcao = input(f"{DOS_VERDE}SELECIONE UMA OPÇÃO (1-2): {RESET}").strip()
        if opcao == "1":
            jogo.hp = 3
            jogo.chance_sprint_minotauro = 15
            jogo.turnos_perseguidor_aviso = 3
            jogo.turnos_perseguidor_morte = 5
            jogo.energia_min_noite = 100
            jogo.energia_max_noite = 100
            jogo.furia_noite = 1
            jogo.dificuldade_escolhida = "NORMAL"
            break
        elif opcao == "2":
            jogo.hp = 2
            jogo.chance_sprint_minotauro = 45          
            jogo.turnos_perseguidor_aviso = 2          
            jogo.turnos_perseguidor_morte = 4          
            jogo.energia_min_noite = 70                
            jogo.energia_max_noite = 82
            jogo.furia_noite = 2                       
            jogo.dificuldade_escolhida = "PESADELO"
            break
        elif opcao == "1982":
            limpar_tela()
            digitar("[ ACESSO RESTRITO: NOITE CUSTOMIZADA ]", 0.03, DOS_VERMELHO, jogo)
            print("Defina a agressividade das máquinas.")
            try:
                jogo.furia_noite = int(input(f"{DOS_VERDE}Fúria (1 a 10): {RESET}"))
                jogo.energia_min_noite = int(input(f"{DOS_VERDE}Bateria Inicial (0 a 100): {RESET}"))
                jogo.energia_max_noite = jogo.energia_min_noite
            except:
                jogo.furia_noite = 10; jogo.energia_min_noite = 10; jogo.energia_max_noite = 10
            jogo.hp = 3
            jogo.chance_sprint_minotauro = 50
            jogo.turnos_perseguidor_aviso = 2
            jogo.turnos_perseguidor_morte = 3
            jogo.dificuldade_escolhida = "CUSTOM"
            break
        else:
            print(f"{DOS_VERMELHO}OPÇÃO INVÁLIDA.{RESET}")
            
    limpar_tela()
    digitar(f"C:\\> CONFIGURANDO AMBIENTE MODO_{jogo.dificuldade_escolhida}...", 0.02, DOS_VERDE, jogo)
    digitar("C:\\> INICIANDO ARQUIVO 'JOGO.EXE'...\n", 0.05, DOS_VERDE, jogo)
    pausar(2)
    limpar_tela()

# ==========================================
# MOTOR PRINCIPAL (GAME LOOP)
# ==========================================
if __name__ == "__main__":
    jogo = GameState()
    
    menu_inicial(jogo) 
    
    pausar(1)
    print(f"\n{DOS_BRANCO}[ OS VILLAS BOAS v1.0 | MODO: {jogo.dificuldade_escolhida} ]{RESET}")
    print(f"{DOS_BRANCO}Você entra no restaurante. Sua lanterna velha dá três piscadas fracas...{RESET}")
    pausar(2)
    print(f"{DOS_AMARELO}[AVISO DO SISTEMA]: BATERIA DA LANTERNA EM 5%. PROCURAR OUTRA FONTE DE LUZ EM ATÉ 3 TURNOS.{RESET}\n")
    pausar(2)

    while True:
        try:
            print("\n" + "="*50)

            # --- CHECAGEM DE MINIGAMES ---
            if jogo.sala_atual == "sala de energia" and not jogo.fios_cortados_inventario:
                if not isinstance(jogo.minigame_atual, MinigameMinotauro):
                    jogo.minigame_atual = MinigameMinotauro(jogo)
                    
            elif jogo.sala_atual == "cadeira" and not jogo.noite_vencida:
                if not isinstance(jogo.minigame_atual, MinigameSeguranca):
                    jogo.minigame_atual = MinigameSeguranca(jogo)

            if jogo.minigame_atual:
                jogo.minigame_atual.imprimir_status()
                
                try:
                    comando = normalizar(input(f"\n{DOS_VERDE}Ação: {RESET}"))
                except (EOFError, KeyboardInterrupt):
                    raise QuitGameException()
                    
                resultado = jogo.minigame_atual.processar_turno(comando, jogo)
                
                if resultado == "morte":
                    jogo.minigame_atual = None; jogo.sala_atual = "morte"
                elif resultado == "vitoria_minotauro":
                    jogo.minigame_atual = None
                elif resultado == "vitoria_seguranca":
                    jogo.minigame_atual = None; jogo.sala_atual = "01"
                continue 

            # --- CHECAGEM DE FINAIS ---
            if jogo.sala_atual == "morte":
                limpar_tela()
                print(f"{DOS_VERMELHO}{CAVEIRA_MORTE}{RESET}")
                print(f"\n{DOS_VERMELHO}💀 GAME OVER. Um animatrônico te pegou e você não sobreviveu à noite.{RESET}")
                break

            elif jogo.sala_atual == "saida":
                print(f"\n{DOS_VERDE}[ FINAL MEDÍOCRE ]{RESET}")
                break
                
            elif jogo.sala_atual == "cama":
                print(f"\n{DOS_BRANCO}[ FINAL BONS SONHOS ]{RESET}")
                break

            elif jogo.sala_atual == "final_bom":
                limpar_tela()
                digitar("Voce acende o isqueiro e ilumina o local. A luz do fogo traz calma...", 0.04, DOS_VERDE, jogo)
                pausar(1)
                digitar("- Por que não deu certo? O que eu fiz de errado?", 0.05, DOS_AMARELO, jogo)
                pausar(1)
                digitar("- 'Ainda estou aqui...'", 0.09, DOS_VERMELHO, jogo)
                pausar(1)
                digitar("- Amor? É voce? Mesmo???", 0.05, DOS_AMARELO, jogo)
                pausar(1)
                digitar("- 'Eu espero que ainda seja eu...'", 0.09, DOS_VERMELHO, jogo)
                pausar(1)
                digitar("- Caroline... desista desse corpo que não lhe pertence. Siga o rumo das estrelas.", 0.05, DOS_AMARELO, jogo)
                pausar(2)
                digitar("- ... *Caroline abraça Rogério*", 0.09, DOS_VERMELHO, jogo)
                pausar(2)
                digitar("- 'Vamos nos encontrar no céu, meu bem.'", 0.09, DOS_VERMELHO, jogo)
                pausar(3)
                limpar_tela()
                print(f"\n{DOS_BRANCO}[ FINAL BOM ]{RESET}")
                break

            elif jogo.sala_atual == "hall de entrada" and jogo.incendio and jogo.noite_vencida and jogo.fios_cortados_inventario:
                limpar_tela()
                digitar("Voce se aproxima do animatronico... dela. E encaixa os fios na sua fiação...", 0.05, DOS_BRANCO, jogo)
                digitar("Voce acende o isqueiro. Os olhos de plastico parecem te encarar.", 0.05, DOS_BRANCO, jogo)
                digitar("Os olhos piscam em vermelho, ela tenta fazer algo... mas não consegue.\n", 0.05, DOS_BRANCO, jogo)
                pausar(1)
                digitar("- Por que não deu certo? O que eu fiz de errado?", 0.05, DOS_AMARELO, jogo)
                pausar(1)
                digitar("- '... voce fez dar certo'", 0.08, DOS_VERMELHO, jogo)
                pausar(1)
                digitar("- Caro... Caroline? É você?", 0.05, DOS_AMARELO, jogo)
                pausar(1)
                digitar("*(Você abraça a carcaça de pelugem rosa)*", 0.04, DOS_BRANCO, jogo)
                pausar(1)
                digitar("- Meu corpo ficou em silencio, não sinto mais raiva.", 0.07, DOS_VERDE, jogo)
                pausar(2)
                digitar("*(O fogo se alastra pelo restaurante, a fumaça chega no hall)*", 0.04, DOS_BRANCO, jogo)
                pausar(1)
                digitar("- Me sinta pela ultima vez.", 0.07, DOS_VERDE, jogo)
                pausar(2)
                digitar("*(Voce sente mãos invisíveis em seus ombros, um alivio inunda sua mente)*", 0.04, DOS_BRANCO, jogo)
                pausar(1)
                digitar("- Obrigada por me deixar assim pela ultima vez.", 0.07, DOS_VERDE, jogo)
                pausar(3)
                digitar("- Eu te amo.", 0.06, DOS_AMARELO, jogo)
                pausar(2)
                digitar("*(O animatronico cai no chão, o fogo cobre o metal e o plástico)*", 0.05, DOS_BRANCO, jogo)
                pausar(2)
                digitar("\n[DISPOSITIVO]: NENHUMA PRESENÇA DETECTADA.", 0.05, DOS_VERDE, jogo)
                pausar(2)
                digitar("Você se levanta e caminha para a saída antes que o teto desabe.", 0.05, DOS_BRANCO, jogo)
                print(f"\n{DOS_BRANCO}[ FINAL VERDADEIRO ]{RESET}")
                break

            # --- HUD E NAVEGAÇÃO ---
            sala = jogo.mapa[jogo.sala_atual]
            print(f"📍 VOCÊ ESTÁ EM: {jogo.sala_atual.upper()}")
            
            descricao_colorida = sala['descrição']
            for inspecionavel in sala.get("inspecionaveis", {}):
                descricao_colorida = descricao_colorida.replace(inspecionavel, f"{DOS_AMARELO}{inspecionavel}{RESET}")
            for item in sala.get("itens", []):
                descricao_colorida = descricao_colorida.replace(item, f"{DOS_VERDE}{item}{RESET}")
                
            print(f"👁️  Visão: {descricao_colorida}")

            if len(sala.get("itens", [])) > 0:
                if jogo.turnos_luz > 0:
                    itens_formatados = [f"{DOS_VERDE}{item}{RESET}" for item in sala['itens']]
                    print(f"📦 Itens no chão: {', '.join(itens_formatados)}")
                else:
                    print(f"📦 {DOS_BRANCO}Deve ter algo no chão, mas está escuro demais para ver o quê.{RESET}")

            chaves_ignoradas = ["descrição", "itens", "inspecionaveis", "cofre_important", "cadeira"]
            saidas = [k for k in sala.keys() if k not in chaves_ignoradas and isinstance(sala[k], str)]
            if saidas:
                print(f"🧭 Saídas: {DOS_AMARELO}{', '.join(saidas).title()}{RESET}")
            else:
                print(f"🧭 Saídas: {DOS_VERMELHO}Nenhuma saída aparente...{RESET}")

            print(f"\n{DOS_BRANCO}[ SISTEMA OPERACIONAL VILLAS BOAS v20.08 ]{RESET}")
            print(f"{DOS_BRANCO}[ HP: {DOS_VERMELHO}{jogo.hp}/3{DOS_BRANCO} | LUZ: {DOS_AMARELO}{jogo.turnos_luz}{DOS_BRANCO} | INV: {len(jogo.inventario)}/{MAX_INVENTARIO} ]{RESET}")
            
            try:
                comando = normalizar(input(f"{DOS_VERDE}C:\\> {RESET}"))
            except (EOFError, KeyboardInterrupt):
                raise QuitGameException()

            gastou_turno = processar_comando(comando, jogo, jogo.mapa)

            if gastou_turno:
                atualizar_eventos_de_tempo(jogo)

        except QuitGameException:
            print(f"\n{DOS_AMARELO}Encerrando o Sistema Villas Boas. Até logo.{RESET}")
            break
            
        except Exception as e:
            if DEBUG_MODE:
                raise e
            else:
                print(f"\n{DOS_VERMELHO}[ FALHA GERAL DE SISTEMA - TELA AZUL ]{RESET}")
                print(f"{DOS_BRANCO}O sistema encontrou um erro: {e}{RESET}")
                time.sleep(3)
                continue