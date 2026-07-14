import time
import random
import unicodedata
import difflib

# Importa as ferramentas de interface
from ui import DOS_VERDE, DOS_BRANCO, DOS_AMARELO, DOS_VERMELHO, RESET, limpar_tela, pausar, digitar

# Importa os dados estáticos (que criaremos no data.py)
from data import MAX_INVENTARIO, COFRE_SENHA, descricoes_itens, ARTE_PORCO, ARTE_ROBO, ARTE_PIANO

# Importa a lógica de estado e saves (que criaremos no state.py)
from state import salvar_jogo, carregar_jogo, QuitGameException

# ==========================================
# FUNÇÃO DE NORMALIZAÇÃO DE TEXTO
# ==========================================
def normalizar(texto):
    texto_sem_acento = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    return texto_sem_acento.strip().lower()

# ==========================================
# FUNÇÕES DE COMANDOS ESPECÍFICOS
# ==========================================
def cmd_ir(comando, jogo, mapa):
    direcao_bruta = comando.replace("ir ", "").strip()
    
    palavras_ignoradas = ["para", "pro", "pra", "em", "a", "o", "as", "os", "na", "no"]
    palavras_da_frase = direcao_bruta.split()
    
    palavras_limpas = [p for p in palavras_da_frase if p not in palavras_ignoradas]
    direcao = " ".join(palavras_limpas)
    
    if direcao in ["tras", "atras", "fundo"]:
        direcao = "atrás"
    
    sala = mapa[jogo.sala_atual]
    
    if direcao in sala:
        destino = sala[direcao]
        lugares_validos = list(mapa.keys()) + ["morte", "saida", "01", "cadeira"]

        if destino in lugares_validos:
            limpar_tela()
            jogo.turnos_mesma_sala = 0

            if jogo.turnos_luz <= 0 and random.randint(1, 100) <= 10:
                print("\n No escuro, você perde a noção da direção, e acaba tropeçando no proprio pé, e cai no chão")
                jogo.hp -= 1
                print(f" Você se machucou na queda. (HP: {jogo.hp})")
                pausar(2)
                if jogo.hp <= 0:
                    print("\n Você cai no chão e quebra sua perna, você não consegue mais andar, e escuta barulhos vindo na sua direção")
                    pausar(2)
                    jogo.sala_atual = "morte"
                return 

            jogo.sala_atual = destino

            if jogo.dificuldade_escolhida == "PESADELO" and jogo.sala_atual == jogo.posicao_perseguidor:
                limpar_tela()
                print("\n" + "="*50)
                print(f"{DOS_VERMELHO}quando voce entra na sala, passos pesados e cheiro de fuligem fazem seu nariz doer, mas antes de qualquer ação sua, uma mão robotica segura seu pescoço{RESET}")
                print(f"{DOS_VERMELHO}Ele te levanta antes que você possa gritar.{RESET}")
                pausar(4)
                jogo.sala_atual = "morte"
                return 
            
            if jogo.sala_atual == "saida":
                if jogo.noite_vencida and jogo.fios_cortados_inventario and not jogo.incendio:
                    print(f"\n{DOS_VERDE}[DISPOSITIVO]: NÍVEL 2 - PRESENÇA PRÓXIMA.{RESET}")
                    print(f"{DOS_AMARELO}'Eu preciso terminar isso antes...', você murmura para si mesmo.{RESET}")
                    print(f"{DOS_AMARELO}Você vira as costas para a saída. A Sala de Energia espera.{RESET}")
                    jogo.sala_atual = "entrada"
                    pausar(3)
    else:
        print(f"Você não pode ir para '{direcao}'.")
        pausar(1.5)

def cmd_pegar(comando, jogo, mapa):
    item_desejado = comando.replace("pegar ", "").strip()
    sala = mapa[jogo.sala_atual]
    
    item_real_na_sala = next((item for item in sala.get("itens", []) if item_desejado in item), None)
    
    if item_real_na_sala:
        if len(jogo.inventario) >= MAX_INVENTARIO:
            print(f"{DOS_AMARELO}🎒 Sua mochila está cheia! (Máx: {MAX_INVENTARIO}). Use 'largar [item]' primeiro.{RESET}")
            pausar(1.5)
            return
        
        if jogo.turnos_luz <= 0:
            chance = random.randint(1, 100)
            if chance <= 30:
                print(f"{DOS_BRANCO}Você tateia o chão freneticamente, mas não encontra nada no escuro.{RESET}")
                pausar(1.5)
                return 
            elif chance <= 40:
                print(f"{DOS_VERMELHO}Você se machuca com um pedaço de vidro afiado no escuro, está sangrando muito.{RESET}")
                jogo.hp -= 1
                pausar(1.5)
                if jogo.hp <= 0:
                    print(f"{DOS_VERMELHO}Você sangrou até desmaiar, caindo no chão e perdendo a consciencia.{RESET}")
                    jogo.sala_atual = "morte"
                return 
                    
        sala["itens"].remove(item_real_na_sala) 
        jogo.inventario.append(item_real_na_sala)    
        print(f"{DOS_VERDE}🎒 Você pegou: {item_real_na_sala.upper()}{RESET}")
        pausar(1)
    else:
        print(f"{DOS_BRANCO}Não há nenhum '{item_desejado}' aqui para pegar.{RESET}")
        pausar(1)

def cmd_largar(comando, jogo, mapa):
    item_desejado = comando.replace("largar ", "")
    
    if item_desejado == "lanterna":
        print(f"{DOS_VERMELHO}Você enlouqueceu? Se largar a lanterna, não vai sobrar nada para iluminar.{RESET}")
        pausar(2)
        return
        
    if item_desejado in jogo.inventario:
        jogo.inventario.remove(item_desejado)
        sala = mapa[jogo.sala_atual]
        if "itens" not in sala:
            sala["itens"] = []
        sala["itens"].append(item_desejado)
        print(f"Você largou '{item_desejado}' no chão desta sala.")
    else:
        print(f"Você não tem '{item_desejado}' para largar.")
    pausar(1)

def cmd_examinar(comando, jogo, mapa):
    alvo_bruto = comando.replace("examinar ", "").replace("ex ", "").strip()
    
    palavras_ignoradas = [" o ", " a ", " um ", " uma ", " os ", " as "]
    alvo_limpo = f" {alvo_bruto} "
    for palavra in palavras_ignoradas:
        alvo_limpo = alvo_limpo.replace(palavra, " ")
    alvo = alvo_limpo.strip()

    if jogo.turnos_luz <= 0:
        print(f"{DOS_BRANCO}Está escuro demais para examinar '{alvo_bruto}'.{RESET}")
        pausar(1.5)
        return

    sala = mapa[jogo.sala_atual]
    coisas_para_olhar = sala.get("inspecionaveis", {})
    
    item_cenario = next((k for k in coisas_para_olhar.keys() if alvo in k or k in alvo), None)
    item_inventario = next((i for i in jogo.inventario if alvo in i or i in alvo), None)
    
    if item_cenario:
        print(f"\n{DOS_VERDE}C:\\> ACESSANDO ARQUIVO DE DADOS...{RESET}")
        pausar(1)
        digitar(coisas_para_olhar[item_cenario], 0.03, DOS_AMARELO)
        pausar(2)
    elif item_inventario:
        print(f"\n🔎 {descricoes_itens.get(item_inventario, 'Não há nada de especial nisso.')}")
        if item_inventario == "tabua pequena de madeira":
            jogo.hp -= 1
            print(f"Você se machucou nas farpas. (HP: {jogo.hp})")
            if jogo.hp <= 0:
                print("Você sangrou até desmaiar, caindo no chão e perdendo a consciencia.")
                jogo.sala_atual = "morte"
        pausar(2)
    else:
        print(f"Você olha para '{alvo_bruto}', mas não há nada de interessante ou você não possui o objeto.")
        pausar(1.5)

def cmd_abrir_cofre(jogo):
    if jogo.sala_atual == "01":
        print(f"{DOS_BRANCO}O cofre de ferro possui um teclado numérico antigo.{RESET}")
        senha = input(f"{DOS_VERDE}Digite a senha de 4 dígitos: {RESET}").strip()
        
        if senha == COFRE_SENHA: 
            print(f"{DOS_VERDE}CLICK! A pesada porta de metal se abre.{RESET}")
            if "chave dos fundos" not in jogo.inventario:
                print(f"{DOS_AMARELO}Você encontrou a 'chave dos fundos' suja de graxa lá dentro!{RESET}")
                jogo.inventario.append("chave dos fundos")
            else:
                print("O cofre está vazio. Apenas poeira.")
        else:
            print(f"{DOS_VERMELHO}BEEP! Senha incorreta. O painel pisca em vermelho.{RESET}")
        pausar(2)
    else:
        print("Não há nenhum cofre aqui para abrir.")
        pausar(1.5)

def cmd_combinar(comando, jogo):
    comando_limpo = comando.replace("combinar ", "").replace("juntar ", "").replace(" + ", " com ")
    
    if "recortes" in comando_limpo or "jornal" in comando_limpo:
        if all(r in jogo.inventario for r in ["recorte 1", "recorte 2", "recorte 3"]):
            for r in ["recorte 1", "recorte 2", "recorte 3"]: jogo.inventario.remove(r)
            jogo.inventario.append("jornal completo")
            print(f"{DOS_VERDE} Você juntou os recortes, formando o 'jornal completo'.{RESET}")
        else:
            print(f"{DOS_AMARELO}Você não tem os recortes necessários na mochila.{RESET}")
        pausar(2)
        return

    partes = comando_limpo.split(" com ")
    if len(partes) == 2:
        item1, item2 = partes[0].strip(), partes[1].strip()
        if item1 in jogo.inventario and item2 in jogo.inventario:
            if ("tabua pequena de madeira" in partes) and ("papel" in partes):
                jogo.inventario.remove("tabua pequena de madeira"); jogo.inventario.remove("papel")
                jogo.inventario.append("tocha")
                print("Você enrolou o papel na tábua. Criou uma 'tocha' (apagada).")
            elif ("tocha" in partes) and ("isqueiro" in partes):
                if jogo.isqueiro_usos > 0:
                    jogo.isqueiro_usos -= 1
                    jogo.inventario.remove("tocha"); jogo.inventario.append("tocha acesa")
                    jogo.turnos_luz = 2
                    print(f"🔥 Você acendeu a tocha! A luz vai durar 2 turnos. (Usos: {jogo.isqueiro_usos})")
                else: print("O isqueiro não faz faísca... acabou o gás!")
            elif ("papel" in partes) and ("isqueiro" in partes):
                if jogo.isqueiro_usos > 0:
                    jogo.isqueiro_usos -= 1
                    jogo.inventario.remove("papel"); jogo.inventario.append("papel aceso")
                    jogo.turnos_luz = 1
                    print(f" Você acendeu o papel. A chama vai queimar seus dedos rapidamente (Usos: {jogo.isqueiro_usos})")
                else: print("O isqueiro não tem gás")
            elif ("tesoura quebrada" in partes) and ("fita isolante" in partes):
                jogo.inventario.remove("tesoura quebrada"); jogo.inventario.remove("fita isolante")
                jogo.inventario.append("tesoura")
                print("Você passou fita na tesoura e estabilizou as lâminas!")
            else: print("Esses itens não parecem combinar.")
        else: print("Você não tem esses itens no inventário para tentar combinar.")
    else: print("Formato inválido. Use: 'combinar [item1] com [item2]'")
    pausar(2)

def cmd_usar(comando, jogo, mapa):
    item = comando.replace("usar ", "")
    if item not in jogo.inventario:
        print(f"Você não tem '{item}' no inventário.")
        pausar(1.5)
        return

    if item == "tabua pequena de madeira" and jogo.sala_atual == "entrada":
        print("Você usa a tábua para trancar a porta de entrada. Ninguém mais entra... e você não sai.")
        mapa["entrada"]["atrás"] = "parede"
        jogo.inventario.remove(item)
        pausar(2)
    elif item == "doce":
        jogo.hp += 1; jogo.turnos_enjoado = 2; jogo.inventario.remove("doce")
        print(f"🍬 Você engoliu o doce velho. Ganhou 1 HP! (HP: {jogo.hp})")
        print("Mas o gosto de açúcar mofado embrulha seu estômago...")
        pausar(2)
    elif item == "remedio":
        if jogo.hp < 3:
            jogo.hp = min(3, jogo.hp + 2)
            jogo.inventario.remove("remedio")
            print(f" Você engole as pílulas secas. A dor diminui (HP restaurado para {jogo.hp})")
        else: print("Você já está com a saúde máxima.")
        pausar(2)
    elif item == "pizza mofada":
        jogo.hp -= 1; jogo.turnos_enjoado = 4; jogo.inventario.remove("pizza mofada")
        print(f" Você comeu isso? Você vomita e seu estomago está doendo muito. (HP: {jogo.hp})")
        pausar(2)
    elif item == "bateria nova":
        jogo.turnos_luz = 10; jogo.inventario.remove("bateria nova")
        print(f"{DOS_VERDE} Você conectou a bateria na sua lanterna, ela brilha com força total.{RESET}")
        pausar(2)
    elif item == "tesoura" and jogo.sala_atual == "corredor":
        print("Você usa a tesoura na fechadura emperrada da porta 03. O metal estala e a porta abre!")
        mapa["corredor"]["03"] = "sala do gerador"
        jogo.inventario.remove("tesoura"); jogo.inventario.append("tesoura quebrada")
        print("A tesoura quebrou com o esforço.")
        pausar(2)
    elif item == "fios cortados" and jogo.sala_atual == "sala do gerador":
        print("\n Você joga os fios na fiação principal desencapada")
        print(" O painel explode e as chamas começam a lamber as paredes")
        jogo.incendio = True
        jogo.inventario.remove("fios cortados")
        mapa["entrada"]["descrição"] = "A porta! Está logo ali!"
        mapa["corredor"]["descrição"] = "O corredor está em chamas! Fumaça preenche seus pulmões!"
        mapa["sala de jantar"]["descrição"] = "As mesas estão queimando, o teto está caindo!"
        pausar(3)
    elif item in ["isqueiro", "fosforo"] and jogo.sala_atual == "sala dos fundos":
        if jogo.noite_vencida:
            print(f"\nVocê saca o {item}. A carcaça do coelho rosa avança na sua direção nas sombras.")
            pausar(2)
            if jogo.incendio and item == "fosforo":
                print("Com o restaurante caindo aos pedaços, você acende o fósforo e joga na fantasia!")
                print("A passagem está livre. CORRA!")
                mapa["sala dos fundos"]["frente"] = "parede" 
            elif not jogo.incendio and item == "isqueiro":
                jogo.sala_atual = "final_bom" 
            else:
                print("Você tenta usar isso, mas no pânico não funciona direito! Ela te agarra!")
                jogo.sala_atual = "morte"
        else: print("Você balança a luz, mas não há nada aqui... ainda.")
    elif item == "moeda velha" and jogo.sala_atual == "sala 1":
        print("A moeda não faz nada aqui sozinha. Tente ir na Sala de Fliperamas")
        pausar(2)
    elif item == "chave da cozinha" and jogo.sala_atual == "corredor":
        print("Você coloca a chave na fechadura da Sala 02. Ela gira com um 'clique' pesado.")
        mapa["corredor"]["02"] = "cozinha privada"; jogo.inventario.remove("chave da cozinha")
        print(f"{DOS_VERDE}A porta da Cozinha Privada está destrancada.{RESET}")
        pausar(2)
    elif item == "chave dos fundos" and jogo.sala_atual in ["sala de jantar", "porta dos fundos"]:
        print("Você insere a chave suja na porta de metal. A tranca estala!")
        mapa["sala de jantar"]["esquerda"] = "sala dos fundos"
        jogo.sala_atual = "sala dos fundos" 
        jogo.inventario.remove("chave dos fundos")
        print(f"{DOS_VERDE}O caminho para a Sala dos Fundos foi destrancado. Um ar gelado sai de lá...{RESET}")
        pausar(2)
    else:
        print(f"Você tenta usar '{item}' aqui, mas nada de útil acontece.")
        pausar(1.5)

def cmd_jogar(comando, jogo):
    if jogo.sala_atual != "sala de fliperamas":
        print("Não há fliperamas aqui para jogar.")
        pausar(1.5)
        return

    jogo_nome = comando.replace("jogar ", "").strip()
    
    if jogo_nome == "fome de jon" or jogo_nome == "jon":
        limpar_tela()
        print(f"{DOS_BRANCO}{ARTE_PORCO}{RESET}")
        digitar("--- A FOME DE JON ---", 0.03, DOS_VERDE)
        print(f"{DOS_BRANCO}Guie o Porco Jon pelos dutos baseando-se nos seus sentidos.{RESET}")
        print("Comandos: [F] Frente | [E] Esquerda | [D] Direita\n")
        
        opcoes = ["f", "e", "d"]
        caminho_certo = [random.choice(opcoes) for _ in range(4)]
        
        dicas = {
            "f": "Uma corrente de ar gelado bate direto no seu rosto.",
            "e": "Um som agudo de metal arranhando reverbera pela parede canhota do duto.",
            "d": "O cheiro podre de carne estragada fica mais forte no caminho destro."
        }
        
        passo = 0
        while passo < 4:
            if random.random() <= 0.25:
                erradas = [v for k, v in dicas.items() if k != caminho_certo[passo]]
                dica_exibida = random.choice(erradas)
                print(f"\n{DOS_VERMELHO}[SENSÓRIO CONFUSO]: {dica_exibida}{RESET}")
            else:
                print(f"\n{DOS_AMARELO}[SENSÓRIO]: {dicas[caminho_certo[passo]]}{RESET}")

            direcao = input(f"Passo {passo+1}/4 - Direção (F/E/D): ").strip().lower()

            if direcao == caminho_certo[passo]:
                print(f"{DOS_BRANCO}Jon rasteja em silêncio pelos dutos...{RESET}")
                passo += 1
            else:
                print(f"\n{DOS_VERMELHO}CRUNCH! Jon caiu num triturador de lixo ativo!{RESET}")
                jogo.hp -= 1
                print(f"{DOS_VERMELHO}A máquina entra em curto e você leva um choque brutal! Perdeu 1 HP. (HP: {jogo.hp}){RESET}")
                if jogo.hp <= 0:
                    print(f"{DOS_VERMELHO}Seu coração não suportou o choque...{RESET}")
                    jogo.sala_atual = "morte"
                break
        
        if passo == 4:
            digitar("\nJon encontrou a 'comida'. A tela pinga um pixel vermelho.", 0.03, DOS_VERDE)
            digitar("MENSAGEM: 'Eles não saíram pela porta da frente em 94.'", 0.03, DOS_VERMELHO)
        
        jogo.turnos_luz -= 1
        pausar(3)

    elif jogo_nome == "consertos":
        if "moeda velha" not in jogo.inventario:
            print("A máquina 'Consertos & Sorrisos' exige uma ficha (moeda velha) para iniciar.")
            pausar(2)
            return
            
        jogo.inventario.remove("moeda velha")
        limpar_tela()
        print(f"{DOS_BRANCO}{ARTE_ROBO}{RESET}")
        digitar("--- CONSERTOS & Sorrisos ---", 0.03, DOS_VERDE)
        print("Bem-vindo, Mecânico! Vamos montar nosso novo Festeiro!")
        pausar(1)
        
        print(f"\n{DOS_AMARELO}[ FASE 1: SELEÇÃO DE PEÇAS ]{RESET}")
        cabeca = input("Escolha a Cabeça (1- Urso | 2- Coelho): ").strip()
        tronco = input("Escolha o Tronco (1- Fino | 2- Robusto): ").strip()
        pernas = input("Escolha as Pernas (1- Aço | 2- Pelúcia): ").strip()
        
        digitar("\n[ FASE 2: CONECTANDO AS PARTES... ]", 0.03, DOS_AMARELO)
        pausar(1.5)
        
        item_secreto = None
        
        if cabeca == "2" and pernas == "2":
            digitar("> AVISO: Peças incompatíveis. Anomalia detectada.", 0.04, DOS_BRANCO)
            digitar("> O animatrônico tenta gritar, mas não tem cordas vocais.", 0.05, DOS_VERMELHO)
            digitar("> Liberando kit de primeiros socorros por protocolo de segurança.", 0.05, DOS_AMARELO)
            item_secreto = "remedio"
        elif cabeca == "1" and tronco == "2":
            digitar("> Encaixando peças do modelo padrão 'Urso Robusto'...", 0.04, DOS_BRANCO)
            digitar("> Sensor detecta carne em decomposição nos parafusos. Ignorando.", 0.05, DOS_VERMELHO)
        else:
            digitar("> Erro de harmonia visual. Soldando peças à força...", 0.04, DOS_AMARELO)
            digitar("> Ossos quebrando no interior do chassi. Encaixe concluído.", 0.05, DOS_VERMELHO)
            
        pausar(2)
        print(f"\n{DOS_VERDE}CONSERTO CONCLUÍDO! O ANIMATRÔNICO SORRI PARA VOCÊ!{RESET}")
        pausar(1)
        
        if "chave da cozinha" not in jogo.inventario:
            print(f"{DOS_BRANCO}A gaveta principal de prêmios se abre com um barulho metálico.{RESET}")
            jogo.inventario.append("chave da cozinha")
            print(f"{DOS_VERDE}🎒 Você obteve: CHAVE DA COZINHA!{RESET}")
            
        if item_secreto and len(jogo.inventario) < MAX_INVENTARIO:
            print(f"{DOS_BRANCO}Um compartimento de emergência se abriu na base da máquina!{RESET}")
            jogo.inventario.append(item_secreto)
            print(f"{DOS_VERDE}🎒 Você obteve um item extra: {item_secreto.upper()}!{RESET}")
        elif item_secreto:
            print(f"{DOS_BRANCO}Um compartimento se abriu com um '{item_secreto}', mas seu inventário está cheio.{RESET}")
        
        jogo.turnos_luz -= 1
        pausar(3)

    elif jogo_nome == "adivinha" or jogo_nome == "julgamento":
        limpar_tela()
        print(f"{DOS_BRANCO}{ARTE_PIANO}{RESET}")
        digitar("--- O JULGAMENTO DO PIANISTA ---", 0.03, DOS_VERDE)
        print(f"{DOS_BRANCO}O animatrônico desperta. Ele detém todas as respostas.{RESET}")
        pausar(1)
        
        pontos = 0
        tempo_limite = 20
        
        def fazer_pergunta_com_tempo(pergunta):
            print(f"\n{DOS_AMARELO}{pergunta}{RESET}")
            print(f"{DOS_BRANCO}[ Responda em até {tempo_limite} segundos ]{RESET}")
            
            inicio = time.time()
            resposta = normalizar(input(f"{DOS_VERDE}Sua resposta: {RESET}"))
            tempo_decorrido = time.time() - inicio
            
            if tempo_decorrido > tempo_limite:
                print(f"{DOS_VERMELHO}⏳ O pêndulo parou! Você demorou {int(tempo_decorrido)} segundos... O silêncio é a sua falha.{RESET}")
                return "TIMEOUT_ESGOTADO"
            return resposta

        resp1 = fazer_pergunta_com_tempo("PERGUNTA 1: Em que ano a nossa música parou para sempre?")
        if resp1 == "1994":
            print(f"{DOS_BRANCO}A máquina toca uma nota suave e agradável.{RESET}"); pontos += 1
        elif resp1 != "TIMEOUT_ESGOTADO": 
            print(f"{DOS_VERMELHO}Acorde dissonante. Resposta incorreta.{RESET}")
            
        resp2 = fazer_pergunta_com_tempo("PERGUNTA 2: Qual animatrônico está atrás de você agora?")
        if "caroline" in resp2 or "ela" in resp2:
            print(f"{DOS_BRANCO}A máquina toca uma nota suave e agradável.{RESET}"); pontos += 1
        elif resp2 != "TIMEOUT_ESGOTADO": 
            print(f"{DOS_VERMELHO}Acorde dissonante. Você não sente a presença dela?{RESET}")
            
        resp3 = fazer_pergunta_com_tempo("PERGUNTA 3: Em que ano tudo isso começou?")
        if resp3 == "1982":
            print(f"{DOS_BRANCO}A máquina toca uma nota suave e agradável.{RESET}"); pontos += 1
        elif resp3 != "TIMEOUT_ESGOTADO": 
            print(f"{DOS_VERMELHO}Acorde dissonante. Não leu as boas vindas?{RESET}")
            
        resp4 = fazer_pergunta_com_tempo("PERGUNTA 4: Quem é você?")
        if "rogerio" in resp4:
            print(f"{DOS_BRANCO}A máquina toca uma nota suave e agradável.{RESET}"); pontos += 1
        elif resp4 != "TIMEOUT_ESGOTADO": 
            print(f"{DOS_VERMELHO}Acorde dissonante. Você esqueceu seu próprio nome.{RESET}")

        print(f"\n{DOS_AMARELO}PERGUNTA 5: Quem são as três vítimas deste local? (Digite os três nomes juntos ou um por vez){RESET}")
        print(f"{DOS_BRANCO}[ Responda em até 30 segundos ]{RESET}")
        
        vitimas_restantes = ["angela", "joao", "renato"]
        acertos_vitimas = 0
        
        inicio = time.time()
        for i in range(3):
            if not vitimas_restantes: break
            resp5 = normalizar(input(f"{DOS_VERDE}Vítima(s): {RESET}"))
            
            if time.time() - inicio > 30:
                print(f"{DOS_VERMELHO}⏳ O pêndulo parou! Tempo limite esgotado.{RESET}")
                break
                
            acertou_nesta = False
            for v in vitimas_restantes[:]:
                if v in resp5: 
                    acertos_vitimas += 1
                    vitimas_restantes.remove(v)
                    acertou_nesta = True
                    
            if acertou_nesta: print(f"{DOS_BRANCO}A máquina processa... Correto.{RESET}")
            else: print(f"{DOS_VERMELHO}Acorde dissonante. Nome incorreto ou já citado.{RESET}")
            
        if acertos_vitimas == 3: pontos += 1
            
        print(f"\n{DOS_BRANCO}Calculando o seu julgamento...{RESET}")
        pausar(2)
        
        if pontos == 5:
            digitar("Obrigado por voltar pela gente, Rogério...", 0.08, DOS_VERDE)
            if "bateria nova" not in jogo.inventario:
                print(f"{DOS_BRANCO}A gaveta inferior abre. Você encontrou uma 'bateria nova'!{RESET}")
                jogo.inventario.append("bateria nova")
        else:
            digitar("Quem é você?", 0.08, DOS_VERMELHO)
            print(f"{DOS_BRANCO}A tela desliga. Você perdeu sua chance de absolvição.{RESET}")
            
        jogo.turnos_luz -= 1
        pausar(3)
        
    else:
        print(f"Não existe um fliperama chamado '{jogo_nome}'. Máquinas ligadas: 'jon', 'consertos' e 'julgamento'.")
        pausar(2)

# ==========================================
# PROCESSADOR CENTRAL
# ==========================================
def processar_comando(comando, jogo, mapa):
    comando = comando.strip()
    if not comando: return False

    mapa_direcoes = {
        "f": "ir frente", "frente": "ir frente",
        "t": "ir atrás", "tras": "ir atrás", "atras": "ir atrás", "atrás": "ir atrás",
        "e": "ir esquerda", "esquerda": "ir esquerda",
        "d": "ir direita", "direita": "ir direita"
    }
    if comando in mapa_direcoes:
        comando = mapa_direcoes[comando]

    partes = comando.split(" ", 1)
    verbo_bruto = partes[0]
    resto = partes[1] if len(partes) > 1 else ""

    verbos_validos = ["ir", "pegar", "largar", "usar", "combinar", "juntar", "examinar", "ex", "jogar", "abrir", "salvar", "carregar", "ajuda", "comandos", "inventario", "i", "olhar", "o", "cls", "limpar", "whoami", "sair"]
    
    if verbo_bruto not in verbos_validos:
        sugestoes = difflib.get_close_matches(verbo_bruto, verbos_validos, n=1, cutoff=0.6)
        
        if sugestoes:
            verbo_corrigido = sugestoes[0]
            comando = f"{verbo_corrigido} {resto}".strip()
            print(f"{DOS_AMARELO}(Entendido como: '{comando}'){RESET}")
            pausar(1)
        else:
            if verbo_bruto in ["correr", "fugir", "escapar"]:
                print(f"{DOS_BRANCO}Você está com muito medo, mas correr às cegas no escuro seria suicídio.{RESET}")
            elif verbo_bruto in ["atacar", "bater", "chutar", "lutar"]:
                print(f"{DOS_BRANCO}Você não tem armas. Suas mãos estão tremendo demais para lutar.{RESET}")
            elif verbo_bruto in ["chorar", "gritar", "socorro", "ajudem"]:
                print(f"{DOS_BRANCO}Ninguém vai vir te ajudar. Você está sozinho aqui.{RESET}")
            elif verbo_bruto in ["ir luz", "luz", "iluminar", "lanterna", "usar lanterna"]:
                print(f"{DOS_BRANCO} Digitar isso não vai fazer nada, tente procurar uma fonte de luz")
            else:
                print("Comando não reconhecido ou mal digitado. Digite 'ajuda' para ver a lista de ações.")
            pausar(1.5)
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
    elif comando.startswith("examinar ") or comando.startswith("ex "):
        cmd_examinar(comando, jogo, mapa); return False 
    elif comando.startswith("jogar "):
        cmd_jogar(comando, jogo); return True
    elif comando == "abrir cofre":
        cmd_abrir_cofre(jogo); return True
    elif comando == "salvar":
        salvar_jogo(jogo); return False
    elif comando == "carregar":
        carregar_jogo(jogo); return False
    elif comando == "ajuda" or comando == "comandos":
        print(f"\n{DOS_AMARELO}--- COMANDOS DO SISTEMA ---{RESET}")
        print("Mover: 'ir [frente/atrás/esquerda/direita/sala/etc]' (ou apenas 'f', 'atras', etc)")
        print("Itens: 'pegar [item]', 'largar [item]', 'usar [item]'")
        print("Ações: 'examinar [item/cenario]', 'combinar [item] com [item]'")
        print("Jogos: 'jogar [nome]', 'abrir cofre'")
        print("Outros: 'inventario' (ou 'i'), 'olhar' (ou 'o'), 'salvar', 'carregar'")
        pausar(2); return False
    elif comando == "inventario" or comando == "i":
        if len(jogo.inventario) > 0: 
            itens_inv = [f"{DOS_VERDE}{i}{RESET}" for i in jogo.inventario]
            print(f"🎒 Seu inventário: {', '.join(itens_inv)}")
        else: 
            print("🎒 Seu inventário está vazio.")
        pausar(2); return False
    elif comando == "olhar" or comando == "o":
        return False 
    elif comando == "cls" or comando == "limpar":
        limpar_tela(); return False
    elif comando == "whoami":
        digitar("Sou eu, Rogério.", 0.08, DOS_VERMELHO)
        pausar(2); return False
    elif comando == "format c:":
        digitar("FORMATAÇÃO INICIADA...", 0.05, DOS_VERMELHO)
        print(f"{DOS_VERMELHO}ERRO CRÍTICO 0x0000: PRESENÇA ULTERIOR PRESA NO DISCO.{RESET}")
        pausar(2); return False
    elif comando == "sair":
        raise QuitGameException()
    else:
        print("Faltam informações no comando. (Ex: se digitou 'pegar', o que deseja pegar?) para ver os comandos, digite 'ajuda' ou 'comandos' ")
        pausar(1.5); return False