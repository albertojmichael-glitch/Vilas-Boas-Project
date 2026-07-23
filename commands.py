import random
import difflib
from utils import normalizar, extrair_argumentos, encontrar_melhor_match
from ui import DOS_VERDE, DOS_BRANCO, DOS_AMARELO, DOS_VERMELHO, RESET, default_ui
from data import MAX_INVENTARIO, COFRE_SENHA, descricoes_itens
from state import salvar_autosave, carregar_autosave, QuitGameException
from views import imprimir_contexto_sala

def cmd_ir(comando, jogo, mapa):
    ui = jogo.ui_handler or default_ui
    direcao_bruta = comando.replace("ir ", "").strip()
    
    palavras_ignoradas = ["para", "pro", "pra", "em", "a", "o", "as", "os", "na", "no"]
    palavras_da_frase = extrair_argumentos(direcao_bruta)
    palavras_limpas = [p for p in palavras_da_frase if p not in palavras_ignoradas]
    direcao = " ".join(palavras_limpas)
    
    if direcao in ["tras", "atras", "fundo"]: direcao = "atrás"
    
    sala = mapa[jogo.sala_atual]

    if jogo.sala_atual == "03" and direcao == "frente":
        ui.exibir(f"{DOS_AMARELO}Você toma distância e dá um chute violento na porta emperrada!{RESET}")
        ui.exibir(f"{DOS_VERDE}CRASH! A madeira velha cede e a porta escancara.{RESET}")
        mapa["corredor"]["03"] = "sala do gerador"
        jogo.sala_atual = "sala do gerador"
        ui.pausar(2)
        return True

    saidas_validas = [str(k).lower() for k in sala.keys() if k not in ["descrição", "itens", "inspecionaveis", "cofre_important"]]
    
    match_direcao = encontrar_melhor_match(direcao, saidas_validas)
    if match_direcao:
        direcao = match_direcao
    else:
        ui.exibir(f"Você não pode ir para '{direcao_bruta}'.")
        if saidas_validas: ui.exibir(f"{DOS_BRANCO}Saídas disponíveis: {', '.join(saidas_validas).title()}{RESET}")
        ui.pausar(1.5)
        return False

    destino = sala[direcao]
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

        if jogo.dificuldade_escolhida == "PESADELO" and jogo.sala_atual == jogo.posicao_perseguidor:
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
    ui = jogo.ui_handler or default_ui
    item_desejado = comando.replace("pegar ", "").strip()
    sala = mapa[jogo.sala_atual]
    itens_sala = sala.get("itens", [])
    
    item_real_na_sala = encontrar_melhor_match(item_desejado, itens_sala)
    
    if item_real_na_sala:
        
        if len(jogo.inventario) >= MAX_INVENTARIO and not getattr(jogo, 'god_mode', False):

            if item_desejado == "bolsa":
                jogo.limite_inventario += 3
                jogo.mapa[jogo.sala_atual]["itens"].remove("bolsa")
                ui.exibir(f"{DOS_VERDE}Você colocou a pequena bolsa escolar nas costas. ainda está resistente.{RESET}")
                ui.exibir(f"{DOS_BRANCO}Seu limite de inventário aumentou para {jogo.limite_inventario} espaços!{RESET}")
                return

            if len(jogo.inventario) >= jogo.limite_inventario:
                ui.exibir(f"Suas mãos estão cheias! Você só consegue carregar {jogo.limite_inventario} itens.")
                return

            ui.exibir(f"{DOS_AMARELO}[INV] Sua mochila está cheia! (Máx: {MAX_INVENTARIO}). Use 'largar [item]' primeiro.{RESET}")
            ui.pausar(1.5)
            return
        
        if jogo.turnos_luz <= 0 and not getattr(jogo, 'god_mode', False):
            chance = random.randint(1, 100)
            if chance <= 30:
                ui.exibir(f"{DOS_BRANCO}Você tateia o chão freneticamente, mas não encontra nada no escuro.{RESET}")
                ui.pausar(1.5)
                return 
            elif chance <= 40:
                ui.exibir(f"{DOS_VERMELHO}Você se machuca com um pedaço de vidro afiado no escuro, está sangrando muito.{RESET}")
                jogo.hp -= 1
                ui.pausar(1.5)
                if jogo.hp <= 0:
                    ui.exibir(f"{DOS_VERMELHO}Você sangrou até desmaiar, caindo no chão e perdendo a consciencia.{RESET}")
                    jogo.sala_atual = "morte"
                return 
                    
        sala["itens"].remove(item_real_na_sala) 
        jogo.inventario.append(item_real_na_sala)    
        ui.exibir(f"{DOS_VERDE}[INV] Você pegou: {item_real_na_sala.upper()}{RESET}")
        ui.pausar(1)
    else:
        ui.exibir(f"{DOS_BRANCO}Não há nenhum '{item_desejado}' aqui para pegar.{RESET}")
        if itens_sala and jogo.turnos_luz > 0:
            ui.exibir(f"{DOS_BRANCO}Itens visíveis: {', '.join(itens_sala)}{RESET}")
        ui.pausar(1.5)

def cmd_largar(comando, jogo, mapa):
    ui = jogo.ui_handler or default_ui
    item_desejado = comando.replace("largar ", "").strip()
    
    match_inv = encontrar_melhor_match(item_desejado, jogo.inventario)
    if match_inv:
        item_desejado = match_inv

    if item_desejado == "lanterna":
        ui.exibir(f"{DOS_VERMELHO}Se largar a lanterna, não vai sobrar nada para iluminar.{RESET}")
        ui.pausar(2)
        return
        
    if item_desejado in jogo.inventario:
        jogo.inventario.remove(item_desejado)
        sala = mapa[jogo.sala_atual]
        sala.setdefault("itens", []).append(item_desejado)
        ui.exibir(f"Você largou '{item_desejado}' no chão desta sala.")
    else:
        ui.exibir(f"Você não tem '{item_desejado}' para largar.")
    ui.pausar(1)

def cmd_examinar(comando, jogo, mapa):
    ui = jogo.ui_handler or default_ui
    alvo_bruto = comando.replace("examinar ", "").replace("ex ", "").strip()
    
    if jogo.turnos_luz <= 0 and not getattr(jogo, 'god_mode', False):
        ui.exibir(f"{DOS_BRANCO}Está escuro demais para examinar '{alvo_bruto}'.{RESET}")
        ui.pausar(1.5)
        return

    sala = mapa[jogo.sala_atual]
    coisas_para_olhar = sala.get("inspecionaveis", {})
    todas_chaves = list(coisas_para_olhar.keys()) + jogo.inventario
    
    match_alvo = encontrar_melhor_match(alvo_bruto, todas_chaves)
    item_cenario = next((k for k in coisas_para_olhar.keys() if match_alvo == k), None)
    item_inventario = next((i for i in jogo.inventario if match_alvo == i), None)

    if item_cenario:
        ui.exibir(fr"\n{DOS_VERDE}C:\> ACESSANDO ARQUIVO DE DADOS...{RESET}")
        ui.pausar(1)
        ui.animar(coisas_para_olhar[item_cenario], 0.03, DOS_AMARELO)
        ui.pausar(2)
    elif item_inventario:
        ui.exibir(f"\n ☞ {descricoes_itens.get(item_inventario, 'Não há nada de especial nisso.')}")
        if item_inventario == "tabua pequena de madeira" and not getattr(jogo, 'god_mode', False):
            jogo.hp -= 1
            ui.exibir(f"{DOS_VERMELHO}Você se machucou nas farpas. (HP: {jogo.hp}){RESET}")
            if jogo.hp <= 0:
                ui.exibir(f"{DOS_VERMELHO}Você sangrou até desmaiar, caindo no chão e perdendo a consciencia.{RESET}")
                jogo.sala_atual = "morte"
        ui.pausar(2)
    else:
        ui.exibir(f"Você olha para '{alvo_bruto}', mas não há nada de interessante ou você não possui o objeto.")
        ui.pausar(1.5)

def cmd_abrir_cofre(jogo):
    ui = jogo.ui_handler or default_ui
    if jogo.sala_atual == "01":
        ui.exibir(f"{DOS_BRANCO}O cofre de ferro possui um teclado numérico antigo.{RESET}")
        
        senha = ui.obter_input(f"{DOS_VERDE}Digite a senha de 4 dígitos: {RESET}").strip()
        
        if senha == COFRE_SENHA: 
            ui.exibir(f"{DOS_VERDE}CLICK! A pesada porta de metal se abre.{RESET}")
            sala = jogo.mapa[jogo.sala_atual]
            sala.setdefault("itens", [])
            
            if "chave dos fundos" not in jogo.inventario and "chave dos fundos" not in sala["itens"]:
                if len(jogo.inventario) < MAX_INVENTARIO or getattr(jogo, 'god_mode', False):
                    ui.exibir(f"{DOS_AMARELO}Você encontrou a 'chave dos fundos' suja de graxa lá dentro!{RESET}")
                    jogo.inventario.append("chave dos fundos")
                else:
                    ui.exibir(f"{DOS_AMARELO}Você encontrou a 'chave dos fundos', mas sua mochila está cheia. Ela caiu no chão.{RESET}")
                    sala["itens"].append("chave dos fundos")
            else:
                ui.exibir("O cofre está vazio. Apenas poeira.")
        else:
            ui.exibir(f"{DOS_VERMELHO}☓ Senha incorreta. O painel pisca em vermelho. ☓{RESET}")
        ui.pausar(2)
    else:
        ui.exibir("Não há nenhum cofre aqui para abrir.")
        ui.pausar(1.5)

def cmd_combinar(comando, jogo):
    ui = jogo.ui_handler or default_ui
    comando_limpo = comando.replace("combinar ", "").replace("juntar ", "").replace(" + ", " com ")
    if "recortes" in comando_limpo or "jornal" in comando_limpo:
        if all(r in jogo.inventario for r in ["recorte 1", "recorte 2", "recorte 3"]):
            for r in ["recorte 1", "recorte 2", "recorte 3"]: jogo.inventario.remove(r)
            jogo.inventario.append("jornal completo")
            ui.exibir(f"{DOS_VERDE} Você juntou os recortes, formando o 'jornal completo'.{RESET}")
        else:
            ui.exibir(f"{DOS_AMARELO}Você não tem os recortes necessários na mochila.{RESET}")
        ui.pausar(2)
        return

    partes = comando_limpo.split(" com ")
    if len(partes) == 2:
        item1, item2 = partes[0].strip(), partes[1].strip()
        match_1 = encontrar_melhor_match(item1, jogo.inventario)
        match_2 = encontrar_melhor_match(item2, jogo.inventario)
        
        if match_1: item1 = match_1
        if match_2: item2 = match_2
            
        if item1 in jogo.inventario and item2 in jogo.inventario:
            if ("tabua pequena de madeira" in [item1, item2]) and ("papel" in [item1, item2]):
                jogo.inventario.remove("tabua pequena de madeira"); jogo.inventario.remove("papel")
                jogo.inventario.append("tocha")
                ui.exibir("Você enrolou o papel na tábua. Criou uma 'tocha' (apagada).")
            elif ("tocha" in [item1, item2]) and ("isqueiro" in [item1, item2]):
                if getattr(jogo, 'isqueiro_usos', 0) > 0 or getattr(jogo, 'god_mode', False):
                    if not getattr(jogo, 'god_mode', False): jogo.isqueiro_usos -= 1
                    jogo.inventario.remove("tocha"); jogo.inventario.append("tocha acesa")
                    jogo.turnos_luz = 2 if not getattr(jogo, 'god_mode', False) else 9999
                    ui.exibir(f"🜂 Você acendeu a tocha! A luz vai durar 2 turnos. (Usos: {getattr(jogo, 'isqueiro_usos', 0)})")
                else: ui.exibir("O isqueiro não faz faísca... acabou o gás!")
            elif ("papel" in [item1, item2]) and ("isqueiro" in [item1, item2]):
                if getattr(jogo, 'isqueiro_usos', 0) > 0 or getattr(jogo, 'god_mode', False):
                    if not getattr(jogo, 'god_mode', False): jogo.isqueiro_usos -= 1
                    jogo.inventario.remove("papel"); jogo.inventario.append("papel aceso")
                    jogo.turnos_luz = 1 if not getattr(jogo, 'god_mode', False) else 9999
                    ui.exibir(f" Você acendeu o papel. A chama vai queimar seus dedos rapidamente (Usos: {getattr(jogo, 'isqueiro_usos', 0)})")
                else: ui.exibir("O isqueiro não tem gás")
            elif ("tesoura quebrada" in [item1, item2]) and ("fita isolante" in [item1, item2]):
                jogo.inventario.remove("tesoura quebrada"); jogo.inventario.remove("fita isolante")
                jogo.inventario.append("tesoura")
                ui.exibir("Você passou fita na tesoura e estabilizou as lâminas!")
            else: ui.exibir(f"Não há como combinar '{item1}' com '{item2}'.")
        else: ui.exibir("Você não tem esses itens no inventário para tentar combinar.")
    else: ui.exibir("Formato inválido. Use: 'combinar [item1] com [item2]'")
    ui.pausar(2)

def cmd_usar(comando, jogo, mapa):
    ui = jogo.ui_handler or default_ui
    item_desejado = comando.replace("usar ", "").strip()
    match_item = encontrar_melhor_match(item_desejado, jogo.inventario)
    
    if match_item:
        item = match_item
    else:
        ui.exibir(f"Você não tem '{item_desejado}' no inventário.")
        ui.pausar(1.5)
        return

    if item == "tabua pequena de madeira" and jogo.sala_atual == "entrada":
        ui.exibir("Você usa a tábua para trancar a porta de entrada. Ninguém mais entra... e você não sai.")
        mapa["entrada"]["atrás"] = "parede"
        jogo.inventario.remove(item)
        ui.pausar(2)
    elif item == "doce":
        jogo.hp += 1; jogo.inventario.remove("doce")
        ui.exibir(f"Você engoliu o doce velho. Ganhou 1 HP! (HP: {jogo.hp})")
        ui.exibir("Mas o gosto de açúcar mofado embrulha seu estômago...")
        ui.pausar(2)
    elif item == "sanduiche estragado":
        jogo.hp -= 1; jogo.turnos_enjoado = 4; jogo.inventario.remove("sanduiche estragado")
        ui.exibir(f" Você deu uma mordida na gosma cinza. Seu estômago revira violentamente! (HP: {jogo.hp})")
        ui.pausar(2)
    elif item == "remedio":
        if jogo.hp < 3:
            jogo.hp = min(3, jogo.hp + 2)
            jogo.inventario.remove("remedio")
            ui.exibir(f" Você engole as pílulas secas. A dor diminui (HP restaurado para {jogo.hp})")
        else: ui.exibir("Você já está com a saúde máxima.")
        ui.pausar(2)
    elif item == "bateria nova":
        jogo.turnos_luz = 10 if not getattr(jogo, 'god_mode', False) else 9999
        jogo.inventario.remove("bateria nova")
        ui.exibir(f"{DOS_VERDE} Você conectou a bateria na sua lanterna, ela brilha com força total.{RESET}")
        ui.pausar(2)
    elif item == "tesoura":
        if jogo.sala_atual == "02":
            if mapa["corredor"]["02"] != "cozinha privada":
                mapa["corredor"]["02"] = "cozinha privada"
                jogo.sala_atual = "cozinha privada"
                jogo.inventario.remove("tesoura")
                jogo.inventario.append("tesoura quebrada")
                ui.exibir(f"{DOS_VERDE}Você usa a tesoura na fechadura da Sala 02. O metal estala e a porta abre.{RESET}")
                ui.exibir(f"{DOS_AMARELO}A tesoura quebrou com o esforço e as lâminas se soltaram.{RESET}")
                ui.pausar(2)
            else:
                ui.exibir("A cozinha privada (Sala 02) já está aberta.")
                ui.pausar(1.5)
        elif jogo.sala_atual == "03":
            if mapa["corredor"]["03"] != "sala do gerador":
                mapa["corredor"]["03"] = "sala do gerador"
                jogo.sala_atual = "sala do gerador"
                jogo.inventario.remove("tesoura")
                jogo.inventario.append("tesoura quebrada")
                ui.exibir(f"{DOS_VERDE}Você usa a tesoura na porta emperrada 03. Você força a alavanca e a porta escancara.{RESET}")
                ui.exibir(f"{DOS_AMARELO}A tesoura quebrou com o esforço e as lâminas se soltaram.{RESET}")
                ui.pausar(2)
            else:
                ui.exibir("A sala do gerador (Sala 03) já está aberta.")
                ui.pausar(1.5)
        elif jogo.sala_atual == "corredor":
            ui.exibir("Vá até a porta trancada (02) ou emperrada (03) para tentar usar a tesoura diretamente nela.")
            ui.pausar(2)
        else:
            ui.exibir("Não há nenhuma porta ou tranca aqui que precise ser arrombada com a tesoura.")
            ui.pausar(1.5)
    elif item in ["usar tabua", "arrombar porta", "usar tabua pequena de madeira", "forçar porta", "tabua pequena de madeira"] and jogo.sala_atual == "03":
        if "tabua pequena de madeira" in jogo.inventario:
            ui.exibir(f"{DOS_VERDE}Você encaixa a tábua de madeira na fresta da porta emperrada e faz alavanca.{RESET}")
            ui.exibir(f"{DOS_AMARELO}CRACK! A tábua quebra ao meio, mas a porta de metal cede e se abre!{RESET}")
            jogo.inventario.remove("tabua pequena de madeira")
            jogo.mapa["03"]["frente"] = "sala do gerador"
            jogo.mapa["03"]["descrição"] = "A porta emperrada foi arrombada com a tábua. A passagem para frente está livre."
        else:
            ui.exibir("Você tenta forçar com as mãos, mas precisa de algo firme para fazer alavanca.")

    elif item in ["usar fios cortados", "montar armadilha", "fazer armadilha", "usar garrafa vazia", "fios cortados", "garrafa vazia", "pano", "fita isolante"] and jogo.sala_atual == "hall de entrada":
        if not getattr(jogo, 'amanheceu', False):
            ui.exibir(f"{DOS_AMARELO}Ainda é noite. Sobreviva até as 6:00 da manhã antes de tentar uma fuga barulhenta.{RESET}")
            return
        
        itens_necessarios = ["fios cortados", "garrafa vazia", "pano", "fita isolante"]
        tem_tudo = all(it in jogo.inventario for it in itens_necessarios)
        tem_fogo = "isqueiro" in jogo.inventario or "fosforo" in jogo.inventario
        
        if tem_tudo and tem_fogo:
            ui.limpar()
            
            ui.exibir(f"{DOS_VERMELHO}Você vê ela ao fundo da sala, apenas esperando o momento certo.{RESET}")
            ui.pausar(2)
            
            ui.exibir(f"{DOS_VERMELHO}Você junta a garrafa de vidro, o pano e a fita isolante.{RESET}")
            ui.exibir(f"{DOS_VERMELHO}Usando os fios cortados do Minotauro, você improvisa um pavio perfeito para a mistura inflamável!{RESET}")
            ui.exibir(f"{DOS_AMARELO}Você joga a armadilha no centro do hall de entrada e risca o fogo...{RESET}")
            ui.pausar(2.5)
            
            jogo.estado_atual = "FIM" 
            jogo.sala_atual = "hall de entrada"
            jogo.incendio = True
        else:
            
            ui.exibir(f"{DOS_VERMELHO}Você vê ela ao fundo da sala, bloqueando a porta de saída. Apenas esperando...{RESET}")
            ui.exibir(f"{DOS_AMARELO}Você tenta montar a armadilha para acabar com tudo isso, mas faltam peças. Você precisa de: fios cortados, garrafa vazia, pano, fita isolante e fogo.{RESET}")
            ui.exibir(f"{DOS_BRANCO}Volte e vasculhe o restaurante.{RESET}")

    elif item == "fios cortados" and jogo.sala_atual == "sala do gerador":
        ui.exibir("\n Você joga os fios na fiação principal desencapada")
        ui.exibir(" O painel explode e as chamas começam a lamber as paredes")
        jogo.incendio = True
        jogo.inventario.remove("fios cortados")
        mapa["entrada"]["descrição"] = "A porta! Está logo ali!"
        ui.pausar(3)
    elif item in ["isqueiro", "fosforo"] and jogo.sala_atual == "sala dos fundos":
        if getattr(jogo, 'noite_vencida', False):
            ui.exibir(f"\nVocê saca o {item}. A carcaça do coelho rosa avança na sua direção nas sombras.")
            ui.pausar(2)
            if getattr(jogo, 'incendio', False) and item == "fosforo":
                ui.exibir("Com o restaurante caindo aos pedaços, você acende o fósforo e joga na fantasia!")
                mapa["sala dos fundos"]["frente"] = "parede" 
            elif not getattr(jogo, 'incendio', False) and item == "isqueiro":
                ui.exibir(f"{DOS_VERDE}Você acende o isqueiro. O fogo assusta a criatura, que recua para as sombras. O caminho de volta está livre!{RESET}")
            else:
                ui.exibir("Você tenta usar isso, mas no pânico não funciona direito! Ela te agarra!")
                jogo.sala_atual = "morte"
        else: ui.exibir("Você balança a luz, mas não há nada aqui... ainda.")
    elif item == "chave da cozinha" and jogo.sala_atual in ["corredor", "02"]:
        ui.exibir("Você coloca a chave na fechadura. Ela gira com um 'clique' pesado.")
        mapa["corredor"]["02"] = "cozinha privada"
        jogo.sala_atual = "cozinha privada"
        jogo.inventario.remove("chave da cozinha")
        ui.exibir(f"{DOS_VERDE}A porta da Cozinha Privada está destrancada e você entra no local.{RESET}")
        ui.pausar(2)
    elif item == "chave dos fundos" and jogo.sala_atual in ["sala de jantar", "porta dos fundos"]:
        ui.exibir("Você insere a chave suja na porta de metal. A tranca estala!")
        mapa["sala de jantar"]["esquerda"] = "sala dos fundos"
        jogo.sala_atual = "sala dos fundos"; jogo.inventario.remove("chave dos fundos")
        ui.exibir(f"{DOS_VERDE}O caminho para a Sala dos Fundos foi destrancado. Um ar gelado sai de lá...{RESET}")
        ui.pausar(2)
    else:
        ui.exibir(f"Você tenta usar '{item}' aqui, mas nada de útil acontece.")
        ui.pausar(1.5)

def cmd_jogar(comando, jogo):
    ui = jogo.ui_handler or default_ui
    if jogo.sala_atual != "sala de fliperamas":
        ui.exibir("Não há fliperamas aqui para jogar.")
        ui.pausar(1.5); return
    ui.exibir("Iniciando fliperama na Web, favor usar a interface web para os jogos completos.")
    ui.pausar(2)

def processar_comando(comando, jogo, mapa):
    if comando.strip().lower() == "dir" and jogo.estado_atual == "AGUARDANDO_DIR":
        jogo.estado_atual = "JOGANDO"
        return "olhar"
    ui = jogo.ui_handler or default_ui
    comando = comando.strip()
    if not comando: return False

    if getattr(jogo, 'estado_atual', "") == "COMBATE_ANIMATRONICO":
        if comando in ["atacar", "bater", "chutar", "lutar"] and getattr(jogo, 'god_mode', False):
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
            jogo.estado_atual = "FIM"
            return True

    mapa_direcoes = {
        "f": "ir frente", "frente": "ir frente", "n": "ir frente", "norte": "ir frente",
        "t": "ir atrás", "tras": "ir atrás", "atras": "ir atrás", "atrás": "ir atrás", "s": "ir atrás", "sul": "ir atrás",
        "e": "ir esquerda", "esquerda": "ir esquerda", "w": "ir esquerda", "oeste": "ir esquerda",
        "d": "ir direita", "direita": "ir direita", "leste": "ir direita"
    }
    if comando in mapa_direcoes:
        comando = mapa_direcoes[comando]

    if jogo.sala_atual in mapa:
        sala = mapa[jogo.sala_atual] 
        
        saidas_validas = [str(k).lower() for k in sala.keys() if k not in ["descrição", "itens", "inspecionaveis", "cofre_important", "cadeira"]]
        if normalizar(comando) in saidas_validas:
            comando = f"ir {normalizar(comando)}"

        inspecionaveis_sala = [normalizar(k) for k in sala.get("inspecionaveis", {}).keys()]
        if normalizar(comando) in inspecionaveis_sala:
            comando = f"examinar {normalizar(comando)}"

    partes = extrair_argumentos(comando)
    verbo_bruto = partes[0] if partes else ""
    resto = " ".join(partes[1:]) if len(partes) > 1 else ""

    aliases_verbos = {
        "p": "pegar", "l": "largar", "u": "usar", "c": "combinar", 
        "j": "jogar", "x": "examinar", "ex": "examinar", "o": "examinar", 
        "olhar": "examinar", "ver": "examinar", "investigar": "examinar",
        "i": "inventario", "inv": "inventario"
    }
    if verbo_bruto in aliases_verbos:
        verbo_bruto = aliases_verbos[verbo_bruto]
        comando = f"{verbo_bruto} {resto}".strip()

    verbos_validos = ["ir", "ver", "investigar", "pegar", "largar", "usar", "combinar", "juntar", "examinar", "jogar", "abrir", "salvar", "carregar", "ajuda", "comandos", "inventario", "olhar", "cls", "limpar", "clear", "clean", "whoami", "sair", "tp", "gerar", "atacar", "bater", "chutar", "lutar", "pular", "desligar", "desativar"]
    
    if verbo_bruto not in verbos_validos:
        sugestoes = difflib.get_close_matches(verbo_bruto, verbos_validos, n=1, cutoff=0.75)
        if sugestoes:
            verbo_corrigido = sugestoes[0]
            comando = f"{verbo_corrigido} {resto}".strip()
            
        else:
            if verbo_bruto in ["correr", "fugir", "escapar"]:
                ui.exibir(f"{DOS_BRANCO}Você está com muito medo, mas correr às cegas no escuro seria suicídio.{RESET}")
            elif verbo_bruto in ["chorar", "gritar", "socorro", "ajudem"]:
                ui.exibir(f"{DOS_BRANCO}Ninguém vai vir te ajudar. Você está sozinho aqui.{RESET}")
            else:
                ui.exibir("Comando não reconhecido ou mal digitado. Digite 'ajuda' para ver a lista de ações.")
            ui.pausar(1.5)
            return False

    if comando.startswith("ir "):
        cmd_ir(comando, jogo, mapa); return True
    elif comando.startswith("pegar "):
        cmd_pegar(comando, jogo, mapa); return True
    elif comando.startswith("largar "):
        cmd_largar(comando, jogo, mapa); return True
    elif comando.startswith("usar "):
        cmd_usar(comando, jogo, mapa); return True
    elif comando.startswith("combinar ") or comando.startswith("juntar "):
        cmd_combinar(comando, jogo); return True
    elif comando.startswith("examinar "):
        cmd_examinar(comando, jogo, mapa); return False 
    elif comando.startswith("jogar "):
        cmd_jogar(comando, jogo); return True
    elif comando == "abrir cofre":
        cmd_abrir_cofre(jogo); return True
    elif verbo_bruto in ["desligar", "desativar"]:
        if "alberto" in comando or "troll" in comando or "animatronico" in comando or "robô" in comando or "robo" in comando:
            if jogo.sala_atual == "cozinha privada":
                if not getattr(jogo, 'alberto_desativado', False):
                    ui.exibir(f"{DOS_VERDE}Você gira a chave de manutenção nas costas do Alberto Troll.{RESET}")
                    ui.exibir(f"{DOS_AMARELO}Os olhos dele apagam com um clique metálico. O sistema dele foi desativado.{RESET}")
                    jogo.alberto_desativado = True
                else:
                    ui.exibir("Ele já está desativado. Não mexa mais do que o necessário.")
            else:
                ui.exibir("Não há nenhum animatrônico chamado Alberto para desativar aqui.")
        else:
            ui.exibir("Desativar o quê?")
        ui.pausar(2)
        return True
    elif comando.startswith("tp ") and getattr(jogo, 'god_mode', False):
        destino = comando.replace("tp ", "").strip()
        jogo.sala_atual = destino
        ui.exibir(f"{DOS_AMARELO}[GOD MODE] Teleportado instantaneamente para '{destino}'.{RESET}")
        return True 
    elif comando.startswith("gerar ") and getattr(jogo, 'god_mode', False):
        item = comando.replace("gerar ", "").strip()
        jogo.inventario.append(item)
        ui.exibir(f"{DOS_AMARELO}[GOD MODE] O item '{item}' materializou-se na sua mochila.{RESET}")
        return True
    elif verbo_bruto in ["atacar", "bater", "chutar", "lutar"]:
        if getattr(jogo, 'god_mode', False):
            ui.exibir(f"{DOS_AMARELO}[GOD MODE] Você dá um soco no ar! A pressão rompe as partículas de poeira ao seu redor. Você se sente incrivelmente forte.{RESET}")
        else:
            ui.exibir(f"{DOS_BRANCO}Você não tem armas. Suas mãos estão tremendo demais para lutar.{RESET}")
        ui.pausar(1.5)
        return False
    elif comando == "salvar":
        salvar_autosave(jogo)
        ui.exibir(f"{DOS_VERDE}Progresso salvo no sistema unificado de Autosave.{RESET}")
        ui.pausar(1.5)
        return False
    elif comando == "carregar":
        if carregar_autosave(jogo):
            ui.exibir(f"{DOS_VERDE} Jogo carregado com sucesso do Autosave.{RESET}")
            ui.pausar(1.5)
            imprimir_contexto_sala(jogo)
        else:
            ui.exibir(f"{DOS_AMARELO}Nenhum Autosave encontrado no disco.{RESET}")
            ui.pausar(1.5)
        return False
    elif comando == "ajuda" or comando == "comandos":
        ui.exibir(f"\n{DOS_AMARELO}--- COMANDOS DO SISTEMA ---{RESET}")
        ui.exibir("Mover: 'ir [direcao]' ou apenas o nome da sala! | Itens: 'pegar', 'largar', 'usar', 'combinar'")
        ui.exibir("Ações: 'examinar', 'jogar', 'desativar [objeto]' | Outros: 'i', 'cls'")
        ui.exibir(f"{DOS_AMARELO}Atalhos:{RESET} 'p' (pegar), 'l' (largar), 'u' (usar), 'x' (examinar), 'c' (combinar), 'i' (inventario)")
        if getattr(jogo, 'god_mode', False):
            ui.exibir(f"{DOS_VERMELHO}--- CÓDIGOS DE DEUS ---{RESET}")
            ui.exibir(f"{DOS_VERMELHO}'tp [sala]' -> Teleporta | 'gerar [item]' -> Cria item | 'atacar' -> Insta-Kill{RESET}")
            ui.exibir(f"{DOS_VERMELHO}'pular noite' -> Vence a noite 06:00 (Apenas no minigame de Segurança){RESET}")
        ui.pausar(2); return False
    elif comando == "inventario" or comando == "i":
        if len(jogo.inventario) > 0: 
            itens_inv = [f"{DOS_VERDE}{i}{RESET}" for i in jogo.inventario]
            texto_inv = "∞" if getattr(jogo, 'god_mode', False) else f"{len(jogo.inventario)}/{MAX_INVENTARIO}"
            ui.exibir(f"[INV] Seu inventário ({texto_inv}): {', '.join(itens_inv)}")
        else: 
            ui.exibir("[INV] Seu inventário está vazio.")
        ui.pausar(2); return False
    elif comando == "olhar" or comando == "o":
        return False 
    elif comando in ["cls", "limpar", "clear", "clean"]:
        ui.limpar(); return False
    elif comando == "whoami":
        ui.animar("Sou eu, Rogério.", 0.08, DOS_VERMELHO, jogo)
        ui.pausar(2); return False
    elif comando == "format c:":
        ui.animar("FORMATAÇÃO INICIADA...", 0.05, DOS_VERMELHO, jogo)
        ui.exibir(f"{DOS_VERMELHO} ☣ ERRO CRÍTICO 0x0000: PRESENÇA ULTERIOR PRESA NO DISCO. ☣{RESET}")
        ui.pausar(2); return False
    elif comando == "sair":
        raise QuitGameException()
    else:
        ui.exibir("Faltam informações no comando. (Ex: se digitou 'pegar', o que deseja pegar?)")
        ui.pausar(1.5); return False