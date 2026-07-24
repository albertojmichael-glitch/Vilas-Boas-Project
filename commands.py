import random
from utils import normalizar, extrair_argumentos, encontrar_melhor_match
from ui import DOS_VERDE, DOS_BRANCO, DOS_AMARELO, DOS_VERMELHO, RESET, default_ui
from data import MAX_INVENTARIO, COFRE_SENHA, descricoes_itens

import logging
logger = logging.getLogger(__name__)

def cmd_ir(comando, jogo, mapa):
    ui = jogo.ui_handler or default_ui
    direcao_bruta = comando.replace("ir ", "").strip()
    
    palavras_ignoradas = ["para", "pro", "pra", "em", "a", "o", "as", "os", "na", "no"]
    palavras_da_frase = extrair_argumentos(direcao_bruta)
    palavras_limpas = [p for p in palavras_da_frase if p not in palavras_ignoradas]
    direcao = " ".join(palavras_limpas)
    
    if direcao in ["tras", "atras", "fundo"]: direcao = "atrás"

    if jogo.sala_atual not in mapa:
        return False
    
    sala = mapa[jogo.sala_atual]

    if jogo.sala_atual == "03" and direcao == "frente":
        ui.exibir(f"{DOS_AMARELO}Você toma distância e dá um chute violento na porta emperrada!{RESET}")
        ui.exibir(f"{DOS_VERDE}CRASH! A madeira velha cede e a porta escancara.{RESET}")
        mapa["corredor"]["03"] = "sala do gerador"
        jogo.sala_atual = "sala do gerador"
        ui.pausar(2)
        return True

    saidas_validas = [k for k in sala.keys() if k not in ["descrição", "itens", "inspecionaveis", "cofre_important"] and isinstance(sala[k], str)]
    
    match_direcao = encontrar_melhor_match(direcao, saidas_validas)
    if match_direcao:
        direcao = match_direcao
    else:
        if direcao == "cadeira" and "cadeira" in sala:
            pass 
        else:
            ui.exibir(f"Você não pode ir para '{direcao_bruta}'.")
            if saidas_validas: ui.exibir(f"{DOS_BRANCO}Saídas disponíveis: {', '.join(saidas_validas).title()}{RESET}")
            ui.pausar(1.5)
            return False

    destino = sala.get(direcao, direcao) 
    
    if direcao == "cadeira" and "cadeira" in sala:
        destino = sala["cadeira"]

    lugares_validos = list(mapa.keys()) + ["morte", "saida", "01", "cadeira"]

    if destino in lugares_validos:
        ui.limpar()
        jogo.turnos_mesma_sala = 0

        if jogo.turnos_luz <= 0 and not getattr(jogo, 'god_mode', False) and random.randint(1, 100) <= 10:
            ui.exibir("\n No escuro, você perde a noção da direção, e acaba tropeçando no proprio pé, e cai no chão")
            jogo.hp -= 1
            ui.exibir(f" Você se machucou na queda. (HP: {jogo.hp})")
            ui.pausar(2)
            if jogo.hp <= 0:
                ui.exibir("\n Você cai no chão e quebra sua perna, você não consegue mais andar, e escuta barulhos vindo na sua direção")
                ui.pausar(2)
                jogo.sala_atual = "morte"
            return True

        jogo.sala_atual = destino

        if getattr(jogo, 'dificuldade_escolhida', 'NORMAL') == "PESADELO" and jogo.sala_atual == getattr(jogo, 'posicao_perseguidor', ''):
            ui.limpar()
            ui.exibir("\n" + "="*50)
            ui.exibir(f"{DOS_VERMELHO}Quando voce entra na sala, passos pesados e cheiro de fuligem invadem o ar.{RESET}")
            ui.exibir(f"{DOS_VERMELHO}Uma mão robótica gigante segura o seu pescoço e te levanta do chão!{RESET}")
            ui.exibir(f"{DOS_AMARELO}Você tem UMA AÇÃO para reagir antes que ele quebre o seu pescoço!{RESET}")
            jogo.estado_atual = "COMBATE_ANIMATRONICO" 
            ui.pausar(2)
            return True
        
        if jogo.sala_atual == "saida":
            if getattr(jogo, 'noite_vencida', False) and getattr(jogo, 'fios_cortados_inventario', False) and not getattr(jogo, 'incendio', False):
                ui.exibir(f"\n{DOS_VERDE}[DISPOSITIVO]: NÍVEL 2 - PRESENÇA PRÓXIMA.{RESET}")
                ui.exibir(f"{DOS_AMARELO}'Eu preciso terminar isso antes...', você murmura para si mesmo.{RESET}")
                ui.exibir(f"{DOS_AMARELO}Você vira as costas para a saída. A Sala de Energia espera.{RESET}")
                jogo.sala_atual = "entrada"
                ui.pausar(3)
    else:
        ui.exibir(f"{DOS_BRANCO}{destino}{RESET}")
        ui.pausar(1.5)
    return True

def cmd_pegar(comando, jogo, mapa):
    ui = jogo.ui_handler
    item = comando.replace("pegar ", "").strip()
    sala = mapa.get(jogo.sala_atual, {})
    itens_chao = sala.get("itens", [])
    
    match_item = encontrar_melhor_match(item, itens_chao)
    if not match_item:
        ui.exibir(f"Não há nenhum '{item}' aqui para pegar.")
        return False
        
    item = match_item

    
    qtd_bolsas = jogo.inventario.count("bolsa")
    limite_atual = MAX_INVENTARIO + (qtd_bolsas * 3)
    
    if len(jogo.inventario) >= limite_atual and not getattr(jogo, 'god_mode', False):
        ui.exibir(f"{DOS_VERMELHO}Sua mochila está cheia! Você precisa largar algo antes.{RESET}")
        return False
        
    jogo.inventario.append(item)
    itens_chao.remove(item)
    ui.exibir(f"{DOS_VERDE}Você pegou: {item}{RESET}")
    return True

def cmd_largar(comando, jogo, mapa):
    ui = jogo.ui_handler
    item = comando.replace("largar ", "").strip()
    
    match_item = encontrar_melhor_match(item, jogo.inventario)
    if not match_item:
        ui.exibir(f"Você não tem '{item}' no inventário.")
        return False
        
    item = match_item
    jogo.inventario.remove(item)
    sala = mapa.get(jogo.sala_atual, {})
    if "itens" not in sala:
        sala["itens"] = []
    sala["itens"].append(item)
    ui.exibir(f"{DOS_AMARELO}Você largou: {item} no chão.{RESET}")
    return True

def cmd_examinar(comando, jogo, mapa):
    ui = jogo.ui_handler
    item = comando.replace("examinar ", "").strip()
    
    sala = mapa.get(jogo.sala_atual, {})
    coisas_para_olhar = sala.get("inspecionaveis", {})
    
    match_cenario = encontrar_melhor_match(item, list(coisas_para_olhar.keys()))
    match_inv = encontrar_melhor_match(item, jogo.inventario)
    match_chao = encontrar_melhor_match(item, sala.get("itens", []))
    
    if match_cenario:
        ui.exibir(f"\n{DOS_VERDE}C:\\> ACESSANDO ARQUIVO DE DADOS...{RESET}")
        ui.pausar(1)
        
        if match_cenario == "papeis" and jogo.sala_atual == "01":
            try:
                from data import ARTE_PASTA
                ui.animar(f"{DOS_BRANCO}{ARTE_PASTA}{RESET}", 0.015, jogo=jogo)
            except:
                pass
            
        ui.animar(coisas_para_olhar[match_cenario], 0.03, DOS_AMARELO, jogo=jogo)
        ui.pausar(2)
        return True
        
    elif match_inv or match_chao:
        item_real = match_inv if match_inv else match_chao
        desc = descricoes_itens.get(item_real, "Não há nada de especial nisso.")
        ui.exibir(f"\n{DOS_AMARELO} ☞ {desc}{RESET}")
        return True
    else:
        ui.exibir(f"Você não vê nenhum '{item}' aqui para examinar.")
        return False

def cmd_usar(comando, jogo, mapa):
    ui = jogo.ui_handler
    item = comando.replace("usar ", "").strip()
    
    match_item = encontrar_melhor_match(item, jogo.inventario)
    if not match_item:
        ui.exibir(f"Você não tem '{item}' no inventário.")
        return False
        
    item = match_item
    
    if item == "lanterna":
        ui.exibir("Você já está usando a lanterna automaticamente (quando tem bateria).")
        
    elif item == "bateria nova":
        ui.exibir(f"{DOS_VERDE}Você abre a parte inferior da lanterna e insere a bateria nova.{RESET}")
        ui.exibir(f"{DOS_AMARELO}A luz da lanterna fica forte e ofuscante!{RESET}")
        jogo.turnos_luz = 12 
        jogo.inventario.remove("bateria nova")
        return True
        
    elif item == "disquete":
        if jogo.sala_atual == "01":
            ui.exibir(f"{DOS_VERDE}Você insere o disquete sujo no drive do terminal de segurança...{RESET}")
            ui.pausar(1.5)
            ui.exibir(f"{DOS_BRANCO}LENDO A:\\ ...{RESET}")
            ui.pausar(1)

            try:
                from data import ARTE_DISQUETE
                ui.animar(f"{DOS_BRANCO}{ARTE_DISQUETE}{RESET}", 0.015, jogo=jogo)
                ui.pausar(1)
            except:
                pass

            ui.animar(f"{DOS_AMARELO}ARQUIVO RECUPERADO: ANGELA.TXT{RESET}", 0.05, DOS_AMARELO, jogo)
            ui.animar(f"{DOS_BRANCO}'Hoje vim mostrar para meu esposo João, meu local de trabalho, o Vilas Boas. Talvez não tenha sido uma boa ideia.'{RESET}", 0.06, DOS_BRANCO, jogo)
            ui.animar(f"{DOS_BRANCO}'A gente brigou feio no meio do salão, pois aparentemente ele achava que tinha alguém me observando atrás das cortinas, sendo que não... Não tinha nada lá além de poeira e peças enferrujadas. Ele está perdendo a cabeça.'{RESET}", 0.05, DOS_BRANCO, jogo=jogo)
            ui.animar(f"{DOS_BRANCO}'Ele foi falar com meu chefe, o Sr. Renato, lá na salas dos fundos, enquanto eu escrevo isso.'{RESET}", 0.08, DOS_BRANCO, jogo)
            ui.animar(f"{DOS_VERMELHO}'Talvez... Seja loucura minha, mas eu vi alguem me chamando para a cozinha privada pela janela do escritório, vou ir lá ver.'{RESET}", 0.05, DOS_VERMELHO, jogo)
            ui.animar(f"{DOS_VERMELHO}'Ela foi libertada.'{RESET}", 0.10, DOS_VERMELHO, jogo)
            ui.pausar(2)

            ui.exibir(f"{DOS_VERMELHO}O drive faz um ruído horrível e ejeta o disquete arranhado. Ele está arruinado.{RESET}")
            jogo.inventario.remove("disquete")
            ui.pausar(2)
        else:
            ui.exibir(f"{DOS_BRANCO}Você segura o velho disquete, mas não há nenhum computador neste cômodo para lê-lo. Talvez na sala de segurança?{RESET}")
    elif item == "tábua pequena de madeira" or item == "tabua pequena de madeira":
        if jogo.sala_atual == "03":
            ui.exibir(f"{DOS_AMARELO}Você usa a tábua como alavanca e força a porta emperrada...{RESET}")
            ui.exibir(f"{DOS_VERDE}CRASH! A porta cede e abre! A tábua quebra no processo.{RESET}")
            jogo.inventario.remove(item)
            mapa["corredor"]["03"] = "sala do gerador"
            jogo.sala_atual = "sala do gerador"
            ui.pausar(2)
            return True
        else:
            ui.exibir("Não há onde usar a tábua aqui.")
    else:
        ui.exibir(f"Você não sabe como usar '{item}' aqui.")
    return True

def cmd_combinar(comando, jogo, mapa):
    ui = jogo.ui_handler
    partes = comando.replace("combinar ", "").replace("juntar ", "").split(" com ")
    if len(partes) != 2:
        ui.exibir("Use o formato: combinar [item1] com [item2]")
        return False
        
    item1 = encontrar_melhor_match(partes[0].strip(), jogo.inventario)
    item2 = encontrar_melhor_match(partes[1].strip(), jogo.inventario)
    
    if not item1 or not item2:
        ui.exibir("Você precisa ter os dois itens no inventário.")
        return False
        
    if (item1 == "tesoura quebrada" and item2 == "fita isolante") or (item2 == "tesoura quebrada" and item1 == "fita isolante"):
        ui.exibir(f"{DOS_VERDE}Você enrola a fita isolante na tesoura quebrada. Ela está consertada!{RESET}")
        jogo.inventario.remove("tesoura quebrada")
        jogo.inventario.append("tesoura")
        return True
        
    ui.exibir("Esses itens não parecem combinar.")
    return False

def cmd_inventario(jogo):
    ui = jogo.ui_handler
    if not jogo.inventario:
        ui.exibir("Sua mochila está vazia.")
    else:
        ui.exibir(f"{DOS_BRANCO}INVENTÁRIO:{RESET}")
        for item in jogo.inventario:
            ui.exibir(f" - {item}")
    return True


# ==========================================
# CÉREBRO PRINCIPAL DO PARSER
# ==========================================

def processar_comando(comando, jogo, mapa):
    ui = jogo.ui_handler
    comando = comando.strip()
    if not comando: return False

    if getattr(jogo, 'estado_atual', "") == "COMBATE_ANIMATRONICO":
        if comando.lower() in ["atacar", "bater", "chutar", "lutar"] and getattr(jogo, 'god_mode', False):
            ui.exibir(f"{DOS_AMARELO}[GOD MODE] Você solta um soco devastador direto na mandíbula de metal do animatrônico!{RESET}")
            ui.exibir(f"{DOS_AMARELO}Ele solta o seu pescoço, emite um bipe de erro e foge correndo de volta pras sombras.{RESET}")
            ui.pausar(2)
            jogo.estado_atual = "JOGO"
            jogo.posicao_perseguidor = "longe"
            return True
        else:
            ui.exibir(f"{DOS_VERMELHO}Sua reação foi inútil... Ele esmaga o seu pescoço em um estalo seco.{RESET}")
            ui.pausar(2)
            jogo.sala_atual = "morte"
            ui.exibir("@@JUMPSCARE@@")
    
            jogo.estado_atual = "FIM"
            return True

    if comando.lower() == "dir" and getattr(jogo, 'estado_atual', "") == "AGUARDANDO_DIR":
        jogo.estado_atual = "JOGO"
        return "olhar"

    mapa_direcoes = {
        "f": "ir frente", "frente": "ir frente", "n": "ir frente", "norte": "ir frente",
        "t": "ir atrás", "tras": "ir atrás", "atras": "ir atrás", "atrás": "ir atrás", "s": "ir atrás", "sul": "ir atrás",
        "e": "ir esquerda", "esquerda": "ir esquerda", "w": "ir esquerda", "oeste": "ir esquerda",
        "d": "ir direita", "direita": "ir direita", "leste": "ir direita"
    }
    if comando.lower() in mapa_direcoes:
        comando = mapa_direcoes[comando.lower()]

    if comando in ["cadeira", "sentar", "sentar na cadeira", "usar cadeira"]:
    
        if jogo.sala_atual == "01":  
            if not getattr(jogo, 'noite_vencida', False):
                
                jogo.estado_atual = "MINIGAME_SEGURANCA"
                jogo.minigame_atual = MinigameSeguranca(jogo)
                jogo.minigame_atual.imprimir_status()
            else:
                jogo.ui_handler.exibir(f"{DOS_AMARELO}A mesa de controle está desligada. A noite já terminou.{RESET}")
        else:
            jogo.ui_handler.exibir(f"{DOS_BRANCO}Não há nenhuma cadeira de segurança aqui.{RESET}")

    if jogo.sala_atual in mapa:
        sala = mapa[jogo.sala_atual]
        
        saidas_validas = [str(k).lower() for k in sala.keys() if k not in ["descrição", "itens", "inspecionaveis", "cofre_important"]]
        if normalizar(comando) in saidas_validas:
            comando = f"ir {normalizar(comando)}"

        inspecionaveis_sala = [normalizar(k) for k in sala.get("inspecionaveis", {}).keys()]
        if normalizar(comando) in inspecionaveis_sala:
            comando = f"examinar {normalizar(comando)}"

    if comando.startswith("tp ") and getattr(jogo, 'god_mode', False):
        destino = comando.replace("tp ", "").strip()
        jogo.sala_atual = destino
        ui.exibir(f"{DOS_AMARELO}[GOD MODE] Teleportado para: {destino}{RESET}")
        return True
        
    elif comando.startswith("gerar ") and getattr(jogo, 'god_mode', False):
        item_desejado = comando.replace("gerar ", "").strip()
        match_item = encontrar_melhor_match(item_desejado, list(descricoes_itens.keys()))
        
        if match_item:
            jogo.inventario.append(match_item)
            ui.exibir(f"{DOS_AMARELO}[GOD MODE] O item '{match_item}' materializou-se na sua mochila.{RESET}")
        else:
            ui.exibir(f"{DOS_VERMELHO}[GOD MODE ERRO] Matéria não catalogada. O sistema não sabe como fabricar '{item_desejado}'.{RESET}")
        return True

    partes = comando.split(maxsplit=1)
    verbo = partes[0].lower()
    argumento = partes[1].lower() if len(partes) > 1 else ""

    aliases_verbos = {
        "p": "pegar", "l": "largar", "u": "usar", "c": "combinar", 
        "j": "jogar", "x": "examinar", "ex": "examinar", "o": "examinar", 
        "olhar": "examinar", "ver": "examinar", "investigar": "examinar",
        "i": "inventario", "inv": "inventario"
    }
    if verbo in aliases_verbos:
        verbo = aliases_verbos[verbo]

    if verbo == "ir":
        if not argumento: ui.exibir("Ir para onde?"); return False
        return cmd_ir(argumento, jogo, mapa)
        
    elif verbo == "pegar":
        if not argumento: ui.exibir("Pegar o quê?"); return False
        return cmd_pegar(argumento, jogo, mapa)
        
    elif verbo == "largar":
        if not argumento: ui.exibir("Largar o quê?"); return False
        return cmd_largar(argumento, jogo, mapa)
        
    elif verbo == "usar":
        if not argumento: ui.exibir("Usar o quê?"); return False
        return cmd_usar(argumento, jogo, mapa)
        
    elif verbo in ["combinar", "juntar"]:
        if not argumento: ui.exibir("Combinar o quê?"); return False
        return cmd_combinar(argumento, jogo, mapa)
        
    elif verbo == "examinar":
        if not argumento: return "olhar" 
        return cmd_examinar(argumento, jogo, mapa)
        
    elif verbo == "inventario":
        return cmd_inventario(jogo)
            
    elif verbo in ["limpar", "cls", "clear", "clean"]:
        ui.limpar()
        return True
        
    else:
        ui.exibir("Comando não reconhecido.")
        return False
