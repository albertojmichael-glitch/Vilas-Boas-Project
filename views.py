import random
from ui import DOS_VERDE, DOS_BRANCO, DOS_AMARELO, DOS_VERMELHO, RESET
from data import CAVEIRA_MORTE, MAX_INVENTARIO
from state import registrar_final, carregar_conquistas, AUTOSAVE_FILE

def imprimir_tela_boot(ui):
    ui.animar("VILLAS-BOAS INDUSTRIES (C) 1982", 0.04, DOS_BRANCO)
    ui.animar("BIOS VERSION 1.04 - RELEASE 02/11/1982", 0.04, DOS_BRANCO)
    ui.animar("RAM CHECK: 640KB OK", 0.03, DOS_VERDE)
    ui.animar("DRIVE A: READY", 0.03, DOS_VERDE)
    ui.animar("CARREGANDO 'COMMAND.COM'....... OK\n", 0.06, DOS_VERDE)
    ui.exibir(f"{DOS_VERDE}Digite {DOS_BRANCO}dir{DOS_VERDE} para acessar os diretórios:{RESET}")

def imprimir_menu_dificuldade(ui):
    ui.animar("==================================================", 0.01, DOS_VERDE)
    ui.animar("__     _____ _     _        _ ____   ___   ____ ", 0.01, DOS_VERDE)
    ui.animar("\\ \\   / /_ _| |   | |      / / ___| / _ \\ / ___|", 0.01, DOS_VERDE)
    ui.animar(" \\ \\ / / | || |   | |     / /\\___ \\| | | |\\___ \\", 0.01, DOS_VERDE)
    ui.animar("  \\ V /  | || |___| |___ / /  ___) | |_| | ___) |", 0.01, DOS_VERDE)
    ui.animar("   \\_/  |___|_____|_____/_/  |____/ \\___/ |____/", 0.01, DOS_VERDE)
    ui.animar("==================================================", 0.01, DOS_VERDE)
    ui.animar("        SISTEMA DE SEGURANÇA INTEGRADO v1.0       \n", 0.03, DOS_BRANCO)

    conquistas = carregar_conquistas()
    c_med = "[X]" if "mediocre" in conquistas else "[ ]"
    c_son = "[X]" if "bons_sonhos" in conquistas else "[ ]"
    c_bom = "[X]" if "bom" in conquistas else "[ ]"
    c_ver = "[X]" if "verdadeiro" in conquistas else "[ ]"
    qtd = len(set(conquistas) & {"mediocre", "bons_sonhos", "bom", "verdadeiro"})

    ui.exibir(f"{DOS_AMARELO}🏆 FINAIS ALCANÇADOS: {qtd}/4{RESET}")
    ui.exibir(f"{DOS_BRANCO}{c_med} Medíocre  {c_son} Bons Sonhos  {c_bom} Bom  {c_ver} Verdadeiro{RESET}\n")

    ui.exibir(f"{DOS_BRANCO}[1] INICIAR MODO: NORMAL (Para iniciantes){RESET}")
    ui.exibir(f"{DOS_VERMELHO}[2] INICIAR MODO: PESADELO (RNG Agressivo / HP Baixo){RESET}")
    ui.exibir(f"{DOS_AMARELO}[3] INICIAR MODO: RÁPIDO (Skip Delays de Digitação){RESET}")

    if AUTOSAVE_FILE.exists():
        ui.exibir(f"{DOS_VERDE}[4] CONTINUAR JOGO (Autosave Encontrado){RESET}\n")
        ui.exibir(f"{DOS_VERDE}SELECIONE UMA OPÇÃO (1-4): {RESET}")
    else:
        ui.exibir(f"\n{DOS_VERDE}SELECIONE UMA OPÇÃO (1-3): {RESET}")

def imprimir_tutorial(ui):
    ui.exibir(f"\n{DOS_AMARELO}--- DICAS DE SOBREVIVÊNCIA (TUTORIAL) ---{RESET}")
    ui.exibir(f"{DOS_BRANCO}1. Mova-se digitando {DOS_VERDE}ir frente{DOS_BRANCO}, ou apenas o nome da sala.{RESET}")
    ui.exibir(f"{DOS_BRANCO}2. Use aspas para nomes compostos: {DOS_VERDE}pegar \"tabua pequena de madeira\"{DOS_BRANCO}.{RESET}")
    ui.exibir(f"{DOS_BRANCO}3. Você pode usar atalhos como {DOS_VERDE}p chave{DOS_BRANCO} em vez de {DOS_VERDE}pegar chave{DOS_BRANCO}.{RESET}")
    ui.exibir(f"{DOS_BRANCO}4. Digite {DOS_VERDE}ajuda{DOS_BRANCO} a qualquer momento para ver o manual do sistema.{RESET}")
    ui.exibir(f"{DOS_AMARELO}-----------------------------------------{RESET}\n")

def dar_dica_jon(passo_certo, ui):
    dicas = {
        "f": "Uma corrente de ar gelado bate direto no seu rosto.",
        "e": "Um som agudo de metal arranhando reverbera pela parede canhota do duto.",
        "d": "O cheiro podre de carne estragada fica mais forte no caminho destro."
    }
    if random.random() <= 0.25: ui.exibir(f"\n{DOS_VERMELHO}[SENSÓRIO CONFUSO]: {random.choice([v for k, v in dicas.items() if k != passo_certo])}{RESET}")
    else: ui.exibir(f"\n{DOS_AMARELO}[SENSÓRIO]: {dicas[passo_certo]}{RESET}")

def falar_pianista(acertou, ui, jogo):
    if acertou:
        ui.exibir(f"{DOS_BRANCO}A máquina toca uma nota suave e agradável.{RESET}")
        ui.animar(f'"{random.choice(["Você lembra bem, Rogério. Isso é bom.", "O ritmo continua. Você ainda tem ouvido para isso.", "Correto. Ele sempre soube que você voltaria.", "Sim... exatamente como aconteceu."])}"', 0.04, DOS_AMARELO, jogo)
    else:
        ui.exibir(f"{DOS_VERMELHO}Acorde dissonante.{RESET}")
        ui.animar(f'"{random.choice(["Errado. As teclas pretas não perdoam mentiras.", "Você deveria lembrar melhor do que isso, Rogério.", "Uma nota fora do lugar... como você, aquela noite.", "Isso não é o que consta no registro do restaurante."])}"', 0.04, DOS_AMARELO, jogo)

def imprimir_contexto_sala(jogo):
    if jogo.estado_atual == "COMBATE_ANIMATRONICO": return
    ui = jogo.ui_handler
    
    if not jogo.minigame_atual and jogo.sala_atual not in ["morte", "saida", "cama", "final_bom"]:
        sala = jogo.mapa[jogo.sala_atual]
        ui.exibir("\n" + "="*50)
        ui.exibir(f"📍 VOCÊ ESTÁ EM: {jogo.sala_atual.upper()}")
        
        descricao_colorida = sala.get('descrição', '')
        for inspecionavel in sala.get("inspecionaveis", {}):
            descricao_colorida = descricao_colorida.replace(inspecionavel, f"{DOS_AMARELO}{inspecionavel}{RESET}")
        for item in sala.get("itens", []):
            descricao_colorida = descricao_colorida.replace(item, f"{DOS_VERDE}{item}{RESET}")
            
        ui.exibir(f"👁️  Visão: {descricao_colorida}")

        if len(sala.get("itens", [])) > 0:
            if jogo.turnos_luz > 0:
                itens_formatados = [f"{DOS_VERDE}{item}{RESET}" for item in sala['itens']]
                ui.exibir(f"📦 Itens no chão: {', '.join(itens_formatados)}")
            else:
                ui.exibir(f"📦 {DOS_BRANCO}Deve ter algo no chão, mas escuro demais para ver o quê.{RESET}")

        chaves_ignoradas = ["descrição", "itens", "inspecionaveis", "cofre_important", "cadeira"]
        saidas = [k for k in sala.keys() if k not in chaves_ignoradas and isinstance(sala[k], str)]
        if saidas: ui.exibir(f"🧭 Saídas: {DOS_AMARELO}{', '.join(saidas).title()}{RESET}")
        else: ui.exibir(f"🧭 Saídas: {DOS_VERMELHO}Nenhuma saída aparente...{RESET}")

        ui.exibir(f"\n{DOS_BRANCO}[ SISTEMA OPERACIONAL VILLAS BOAS v20.08 ]{RESET}")
        vida_visual = "9999" if jogo.god_mode else f"{jogo.hp}/3"
        luz_visual = "9999" if jogo.god_mode else str(jogo.turnos_luz)
        inv_visual = "∞" if jogo.god_mode else f"{len(jogo.inventario)}/{MAX_INVENTARIO}"
        ui.exibir(f"{DOS_BRANCO}[ HP: {DOS_VERMELHO}{vida_visual}{DOS_BRANCO} | LUZ: {DOS_AMARELO}{luz_visual}{DOS_BRANCO} | INV: {inv_visual} ]{RESET}")

def dar_tela_de_morte(jogo):
    jogo.estado_atual = "FIM"
    ui = jogo.ui_handler
    ui.animar(f"{DOS_VERMELHO}{CAVEIRA_MORTE}{RESET}", 0.002, jogo=jogo)
    ui.animar("💀 GAME OVER. A NOITE ENGOLIU VOCÊ.", 0.05, DOS_VERMELHO, jogo)
    ui.animar("=== SISTEMA CORROMPIDO. APERTE F5 PARA REINICIAR ===", 0.05, DOS_AMARELO, jogo)

def rodar_final(tipo_final, jogo):
    jogo.estado_atual = "FIM"
    ui = jogo.ui_handler
    ui.limpar()
    liberou_deus = False
    
    if tipo_final == "saida":
        ui.animar("[ FINAL MEDÍOCRE ]", 0.05, DOS_VERDE, jogo)
        liberou_deus = registrar_final("mediocre")
    elif tipo_final == "cama":
        ui.animar("[ FINAL BONS SONHOS ]", 0.05, DOS_BRANCO, jogo)
        liberou_deus = registrar_final("bons_sonhos")
    elif tipo_final == "final_bom":
        ui.animar("Você acende o isqueiro e ilumina o local. A luz do fogo traz calma...", 0.04, DOS_VERDE, jogo)
        ui.exibir(f"\n{DOS_BRANCO}[ FINAL BOM ]{RESET}")
        liberou_deus = registrar_final("bom")
    elif tipo_final == "verdadeiro":
        ui.animar("Voce se aproxima do animatronico... dela. E encaixa os fios na sua fiação...", 0.05, DOS_BRANCO, jogo)
        ui.exibir(f"\n{DOS_BRANCO}[ FINAL VERDADEIRO ]{RESET}")
        liberou_deus = registrar_final("verdadeiro")

    if liberou_deus:
        ui.exibir(f"\n{DOS_AMARELO}=================================================={RESET}")
        ui.animar("VOCÊ DESVENDOU TODAS AS VERDADES DESTA NOITE.", 0.05, DOS_VERMELHO, jogo)
        ui.exibir(f"{DOS_AMARELO}DIGITE O ANO EM QUE TUDO ACABOU NA TELA DE MENU: {DOS_BRANCO}2007{RESET}")
        ui.exibir(f"{DOS_AMARELO}=================================================={RESET}")
        
    ui.animar("\n=== APERTE F5 PARA REINICIAR ===", 0.05, DOS_AMARELO, jogo)