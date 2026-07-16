import random
from ui import DOS_VERDE, DOS_BRANCO, DOS_AMARELO, DOS_VERMELHO, RESET, limpar_tela, pausar, digitar
from data import ARTE_INDIO

# ==========================================
# MINIGAME: SALA DE ENERGIA (O MINOTAURO)
# ==========================================
class MinigameMinotauro:
    def __init__(self, jogo):
        self.px, self.py = 0, 0 
        self.mx, self.my = random.choice([-1, 0, 1]), random.choice([2, 3]) 
        self.tesoura_chao = True
        self.fios_cortados = False
        self.chance_sprint = getattr(jogo, 'chance_sprint_minotauro', 15)
        self.bateria = 9999 if getattr(jogo, 'god_mode', False) else 15
        
        print("\n" + "="*50)
        print("Você entra na Sala de Energia... e a pesada porta de metal bate atrás de você.")
        pausar(2)
        print("Você escuta uma respiração pesada.")
        print("Ele está aqui.")
        pausar(2)

    def imprimir_status(self):
        print("\n" + "-"*30)
        texto_bat = "∞" if self.bateria > 100 else str(self.bateria)
        print(f"🔋 Bateria da Lanterna: {texto_bat} turnos restantes")
        
        distancia = abs(self.px - self.mx) + abs(self.py - self.my)
        
        if distancia > 1: 
            print("👁️ Você sente uma presença distante, talvez não haja perigo por enquanto.")
        elif distancia == 1:
            if random.random() < 0.2:
                print("⚠️ Os ecos do labirinto te confundem... não dá pra saber de onde o som vem!")
            else:
                if self.mx < self.px: print("⚠️ Você sente um ar pesado em sua esquerda.")
                elif self.mx > self.px: print("⚠️ Você enxerga um vulto a sua direita.")
                elif self.my > self.py: print("⚠️ Você não enxerga nada a sua frente, uma mancha negra cobre o fundo.")
                elif self.my < self.py: print("⚠️ Passos pesados são ouvidos atrás de você.")

        opcoes = "ir frente | ir trás | ir esquerda | ir direita | esperar"
        
        if self.px == 0 and self.py == 3 and not self.fios_cortados:
            print("⚡ Você encontrou a caixa de fusíveis na parede central!")
            if self.tesoura_chao:
                print("Há uma tesoura caída no chão.")
                opcoes += " | pegar tesoura"
            opcoes += " | cortar fios"
            
        if self.fios_cortados:
            print(f"{DOS_VERMELHO}⚡ OS FIOS ESTÃO CORTADOS! A SALA ESTÁ DESMORONANDO! FUJA PARA A SAÍDA!{RESET}")
            if self.px == 0 and self.py == 0:
                print(f"{DOS_VERDE}🚪 A porta de entrada está logo aqui! Você pode sair!{RESET}")
                opcoes += " | sair"
                
        print(f"\n[{opcoes}]")

    def mover_minotauro(self):
        if random.random() < 0.60:
            if self.px > self.mx: self.mx += 1
            elif self.px < self.mx: self.mx -= 1
            elif self.py > self.my: self.my += 1
            elif self.py < self.my: self.my -= 1
        else:
            self.mx += random.choice([-1, 0, 1])
            self.my += random.choice([-1, 0, 1])
            
        self.mx = max(-1, min(1, self.mx)) 
        self.my = max(0, min(3, self.my))

    def processar_turno(self, acao, jogo):
        if acao in ["atacar", "bater", "chutar", "lutar"] and getattr(jogo, 'god_mode', False):
            print(f"{DOS_AMARELO}[GOD MODE] Você corre na direção do Minotauro e dá uma voadora com os dois pés no peito dele!{RESET}")
            print(f"{DOS_AMARELO}A fera despenca para trás, choraminga em som de estática e foge rompendo as paredes.{RESET}")
            pausar(2)
            return "vitoria_minotauro"

        turno_gasto = False
        
        if acao == "ir esquerda":
            if self.px > -1: self.px -= 1
            else: print("Você bate a cara na parede...")
            turno_gasto = True 

        elif acao == "ir direita":
            if self.px < 1: self.px += 1
            else: print("Você bate a cara na parede...")
            turno_gasto = True

        elif acao == "ir frente":
            if self.py < 3: self.py += 1
            else: print("Você bateu na parede do fundo...")
            turno_gasto = True
            
        elif acao in ["ir trás", "ir tras", "ir atrás", "ir atras"]:
            if self.py > 0: self.py -= 1
            else: print("Você bate as costas na porta de metal. Ela não abre apenas encostando...")
            turno_gasto = True

        elif acao == "esperar": 
            print("Você fica imóvel aguardando...")
            turno_gasto = True

        elif acao == "pegar tesoura":
            if self.px == 0 and self.py == 3 and self.tesoura_chao:
                jogo.inventario.append("tesoura"); self.tesoura_chao = False
                print("Você derruba a tesoura sem querer, fazendo um barulho, mas guarda na sua bolsa")
                if random.random() < 0.50:
                    self.mover_minotauro() 
                turno_gasto = True
            else: 
                print("Não tem tesoura aqui.")

        elif acao == "cortar fios":
            if self.px == 0 and self.py == 3 and not self.fios_cortados:
                if "tesoura" in jogo.inventario:
                    print(f"\n{DOS_VERMELHO}Você corta os fios principais! Faíscas voam e as poucas luzes estouram!{RESET}")
                    print(f"{DOS_VERMELHO}O Minotauro solta um RUGIDO DE FÚRIA ensurdecedor! Ele sabe onde você está!{RESET}")
                    print(f"{DOS_VERMELHO}CORRA DE VOLTA PARA A PORTA!{RESET}")
                    self.fios_cortados = True
                    jogo.fios_cortados_inventario = True
                    turno_gasto = True
                else: 
                    print("Você precisa de uma ferramenta para cortar os fios!"); turno_gasto = True
            else: 
                print("Não há mais fios aqui."); turno_gasto = True
                
        elif acao == "sair":
            if self.px == 0 and self.py == 0:
                if self.fios_cortados:
                    print(f"\n{DOS_VERDE}Você se joga contra a maçaneta, abre a porta e a tranca com toda a força! Você sobreviveu!{RESET}")
                    pausar(2)
                    return "vitoria_minotauro"
                else:
                    print("Você não pode fugir ainda! A missão não foi cumprida no fundo da sala.")
                    turno_gasto = True
            else:
                print("A porta de saída não fica aqui! Tente voltar para trás.")
        else: 
            print("Ação inválida no momento.")

        if self.px == self.mx and self.py == self.my:
            if getattr(jogo, 'god_mode', False):
                print(f"\n{DOS_AMARELO}[GOD MODE] Você esbarra no Minotauro. Ele tenta te arranhar, mas suas garras quebram na sua pele divina! Ele foge chorando.{RESET}")
                pausar(2)
                return "vitoria_minotauro"
            else:
                print("\n Você andou direto para as mãos do monstro no escuro...")
                pausar(2)
                print("\n No vazio, você morre sozinho, sem poder salvar ninguem. ")
                pausar(2)
                return "morte"

        if turno_gasto:
            if not getattr(jogo, 'god_mode', False):
                self.bateria -= 1
                if self.bateria <= 0:
                    print("\n A sua lanterna apaga, você entra em desespero e bate na bateria fazendo barulho.")
                    pausar(2)
                    print("\n Você sente uma mão atravessando seu estômago por trás, não há nada a se fazer.")
                    pausar(2)
                    return "morte"
                
            passos = 2 if random.randint(1, 100) <= self.chance_sprint else 1 
            
            if passos == 2:
                print(f"\n{DOS_VERMELHO}⚠️ O CHÃO TREME! VOCÊ ESCUTA PASSOS PESADOS CORRENDO NA SUA DIREÇÃO!{RESET}")
                pausar(1.5)

            dist_antes = abs(self.px - self.mx) + abs(self.py - self.my)
            mx_old, my_old = self.mx, self.my

            for _ in range(passos):
                self.mover_minotauro()
                
            if self.px == self.mx and self.py == self.my:
                if dist_antes > 1 and passos == 1:
                    self.mx, self.my = mx_old, my_old
                    print(f"\n{DOS_VERMELHO}⚠️ VOCÊ TROMBA COM ALGO GIGANTE E METÁLICO NO ESCURO! ELE ESTÁ BEM NA SUA FRENTE!{RESET}")
                    pausar(2)
                    return "continuar"
                else:
                    if getattr(jogo, 'god_mode', False):
                        print(f"\n{DOS_AMARELO}[GOD MODE] O Minotauro pula em cima de você, mas é repelido por um escudo de energia! Ele desiste e foge.{RESET}")
                        pausar(2)
                        return "vitoria_minotauro"
                    else:
                        print("\n o minotauro te encontrou no escuro. Mãos frias de metal te rasgam por inteiro")
                        pausar(2)
                        return "morte"
                
        return "continuar"


# ==========================================
# MINIGAME: SALA DE SEGURANÇA (SOBREVIVÊNCIA)
# ==========================================
class MinigameSeguranca:
    def __init__(self, jogo):
        self.turno = 0
        self.energia = 9999 if getattr(jogo, 'god_mode', False) else random.randint(getattr(jogo, 'energia_min_noite', 70), getattr(jogo, 'energia_max_noite', 100)) 
        self.porta_fechada = False
        self.erro_camera = False
        self.erro_relogio = False
        self.erro_deteccao = False
        self.apagao = 0 
        self.rick_pos = 0
        self.jon_pos = 0
        self.caroline_pos = 0
        self.caroline_caminho = random.choice(["porta", "tubulacao"])  
        self.indio_janela = False
        self.alberto_troll = False
        self.furia = getattr(jogo, 'furia_noite', 1)
        self.gerador_reserva_usado = False
        self.turnos_gerador_ativo = 0
        self.usos_sistema_turno = 0
        
        print("\n" + "="*50)
        print("Você senta na cadeira da sala de segurança.")
        pausar(1)

    def imprimir_status(self):
        limpar_tela()
        print("\n" + "=" * 50)
        chance_bug = self.caroline_pos * 15 

        def bug(texto, chance):
            return "".join([c.upper() if random.randint(1, 100) <= chance and c.isalpha() else c for c in texto])

        if self.apagao > 0: hora_disp = "[SISTEMA DESLIGADO]"
        elif self.erro_relogio: hora_disp = f"0{(self.turno * 15) // 60}:??"
        else: hora_disp = f"0{(self.turno * 15) // 60}:{(self.turno * 15) % 60:02d}"

        texto_energia = "∞" if self.energia > 100 else f"{self.energia}%"
        print(bug(f"RELOGIO: {hora_disp}", chance_bug))
        print(bug(f"ENERGIA: {texto_energia}", chance_bug))
        print(bug(f"PORTA CENTRAL: {'Fechada' if self.porta_fechada else 'Aberta'}", chance_bug))

        erros = []
        if self.erro_camera: erros.append("CÂMERAS")
        if self.erro_relogio: erros.append("RELÓGIO")
        if self.erro_deteccao: erros.append("DETECÇÃO")
        print(f"ERROS ATIVOS: {', '.join(erros)}" if erros else bug("ERROS: Nenhum", chance_bug))

        if self.turnos_gerador_ativo > 0:
            print(f"{DOS_VERDE}Gerador reserva: Ativo({self.turnos_gerador_ativo} turnos restantes){RESET}")
        elif not self.gerador_reserva_usado:
            print(f"{DOS_AMARELO}Gerador Reserva: Disponível{RESET}")

        if self.alberto_troll: print("\n[MENSAGEM]: ERRO CRÍTICO! FECHAR PORTA AGORA!")
        if self.indio_janela and not self.erro_deteccao: print("\n" + bug("Você sente como se algo estivesse te olhando pelo vidro...", chance_bug))

        print("\nAção (ouvir | cameras | ver tubulacao | iluminar tubulacao | fechar porta | abrir porta | olhar vidro | Ligar Gerador | consertar [sistema] | esperar)")

    def processar_turno(self, acao, jogo):
        if acao in ["pular noite", "pular", "set time 06:00"] and getattr(jogo, 'god_mode', False):
            print(f"{DOS_AMARELO}[GOD MODE] O tempo se contorce. O relógio salta para as 06:00.{RESET}")
            self.turno = 24
            
        turno_passou = False
        acao_valida = True

        custo_extra = 0 
        if self.turno >= 22:
            custo_extra = 3
        elif self.turno >= 12:
            custo_extra = 1
        
        CUSTO_INFO_LEVE = 0 if self.turnos_gerador_ativo > 0 else ( 1+ custo_extra)
        CUSTO_INFO_PESADO = 1 + custo_extra
        CUSTO_MOTOR = 2 + custo_extra

        if acao == "fechar porta":
            if self.apagao > 0 or self.energia <= CUSTO_MOTOR: print("Sem energia! O botão faz um clique morto.")
            elif self.porta_fechada: print("A porta já está fechada.")
            else:
                self.porta_fechada = True
                self.energia -= CUSTO_MOTOR
                print(f"A pesada porta de metal desce com um estrondo. (-{CUSTO_MOTOR}% Energia)")
                if self.alberto_troll:
                    print("\n Como você é tão tolo? Hahahaha")
                    self.erro_camera = True; self.erro_deteccao = True; self.alberto_troll = False

        elif acao == "abrir porta":
            if self.apagao > 0 or self.energia <= CUSTO_MOTOR: print("Sem energia! A porta não responde.")
            elif not self.porta_fechada: print("A porta já está aberta.")
            else: 
                self.porta_fechada = False
                self.energia -= CUSTO_MOTOR
                print(f"A porta de metal se ergue lentamente. (-{CUSTO_MOTOR}% Energia)")

        elif acao == "iluminar tubulacao":
            if self.apagao > 0 or self.energia <= CUSTO_INFO_PESADO: print("Sem força nas luzes.")
            elif self.usos_sistema_turno >= 2:
                print(f"{DOS_VERMELHO} [SISTEMA SOBRECARREGADO]: Muitas requisições simultâneas. Hardware travado{RESET}")
                self.energia -= CUSTO_INFO_PESADO
            else:
                self.usos_sistema_turno += 1
                self.energia -= CUSTO_INFO_PESADO
                print(f"Você liga o projetor nos dutos (-{CUSTO_INFO_PESADO}% Energia)")
                if self.jon_pos >= 4: self.jon_pos = 0; print("Jon recua apressado pela tubulação")
                if self.caroline_caminho == "tubulacao" and self.caroline_pos >= 5:
                    self.caroline_pos = 0; self.caroline_caminho = random.choice(["porta", "tubulacao"]) 
                    print("A Caroline fugiu do duto")

        elif acao == "olhar vidro":
            if self.indio_janela:
                limpar_tela()
                print(f"{DOS_BRANCO}{ARTE_INDIO}{RESET}")
                pausar(2)
                print("Você não enxerga nada, até que 2 olhos te encaram pela janela, a figura do indio jones faz você perder a cabeça")
                falha = random.choice(["camera", "relogio", "deteccao"])
                if falha == "camera": self.erro_camera = True
                elif falha == "relogio": self.erro_relogio = True
                elif falha == "deteccao": self.erro_deteccao = True
                if self.turno < 20: self.indio_janela = False
            else:
                rick_na_porta = self.rick_pos >= 3
                carol_na_porta = (self.caroline_caminho == "porta" and self.caroline_pos >= 5)
                
                if rick_na_porta and carol_na_porta:
                    print(" Seu corpo treme. Você vê a carcaça maciça de Rick, o mosqueteiro e a carcaça de coelho rosa retorcido de Caroline")
                    print("parados lado a lado no corredor, olhando diretamente para você através do vidro")
                elif rick_na_porta:
                    print(" Você olha pelo vidro e vê a silhueta gigantesca do Rick, o mosqueteiro, parado nas sombras.")
                    print("Os olhos de plástico sem vida dele estão focados em você.")
                elif carol_na_porta:
                    print(" Através da sujeira do vidro, você enxerga a carcaça do coelho rosa tentando se esconder nas sombras.")
                    print("Ela está encostada na parede do corredor")
                else:
                    print("Você limpa o embaçado do vidro e força a vista para o corredor escuro.")
                    print("Consegue distinguir as portas fechadas das outras salas, os cartazes rasgados nas paredes")
                    print("e o chão de linóleo imundo refletindo a pouca luz que resta.")
                    print("Nenhum movimento... Além das sombras, há apenas o seu reflexo devolvendo o olhar.")

        elif acao == "ligar gerador" or acao == "Ligar gerador":
            if self.apagao >0:
                print("Tarde demais, o sistema principal já foi totalmente desligado")
            elif self.gerador_reserva_usado:
                print("O combustivel do gerador reserva já foi queimado, ele só pode ser usado uma vez")
            else:
                print(f"\n{DOS_VERDE} Você aperta o botão do gerador reserva, ele cospe uma fumaça preta, sistemas basicos operando sem custo de energia.{RESET}")
                self.gerador_reserva_usado = True
                self.turnos_gerador_ativo = 2
                turno_passou = True
                self.turno += 1
                self.alberto_troll = False
        
        elif acao.startswith("consertar "):
            sistema = acao.replace("consertar ", "")
            if self.apagao > 0: print("Não há energia.")
            elif sistema == "camera": self.erro_camera = False; print("Câmeras online.")
            elif sistema == "relogio": self.erro_relogio = False; print("Relógio sincronizado.")
            elif sistema == "deteccao": self.erro_deteccao = False; print("Sensores calibrados.")
            else: print("Sistema não reconhecido.")

        elif acao == "ouvir":
            if self.apagao > 0: 
                print("No apagão, você ouve sua própria respiração...")
            elif self.erro_deteccao: 
                print(f"{DOS_VERMELHO}BEEP! BEEP! O alarme estridente de falha nos sensores ecoa na sala. Você não consegue ouvir nada além disso!{RESET}")
            elif self.energia <= CUSTO_INFO_LEVE: 
                print("Sistema de áudio offline (Bateria fraca).")
            elif self.usos_sistema_turno >= 2:
                print(f"{DOS_VERMELHO}🚨 [SISTEMA SOBRECARREGADO]: Placa de áudio em curto. Passe o turno para resfriar!{RESET}")
                self.energia -= CUSTO_INFO_LEVE
            else:
                self.usos_sistema_turno += 1
                self.energia -= CUSTO_INFO_LEVE
                print(f"(-{CUSTO_INFO_LEVE}% Energia)")
                ouviu = False
                if self.rick_pos >= 3 or (self.caroline_caminho == "porta" and self.caroline_pos >= 5):
                    print(" Passos metálicos pesados são ouvidos do corredor"); ouviu = True
                if self.jon_pos >= 4 or (self.caroline_caminho == "tubulacao" and self.caroline_pos >= 5):
                    print(" Você escuta arranhões e batidas vindo da tubulação"); ouviu = True
                if not ouviu: 
                    print("Apenas o zumbido dos fios elétricos e da lâmpada quase apagada.")

        elif acao == "cameras":
            if self.apagao > 0 or self.erro_camera: print("📺 [SINAL PERDIDO]")
            elif self.energia <= CUSTO_INFO_LEVE: print("Câmeras offline (Bateria fraca).")
            elif self.usos_sistema_turno >= 2:
                print(f"{DOS_VERMELHO}🚨 [SISTEMA SOBRECARREGADO]: Monitor superaquecido. A tela exibe apenas estática!{RESET}")
                self.energia -= CUSTO_INFO_LEVE
            else:
                self.usos_sistema_turno += 1
                self.energia -= CUSTO_INFO_LEVE
                print(f"(-{CUSTO_INFO_LEVE}% Energia)")
                
                chance_bug_visual = self.caroline_pos * 10
                if random.randint(1, 100) <= chance_bug_visual:
                    print("📺 [SINAL COM INTERFERÊNCIA] Imagens distorcidas...")
                    print(f"Rick: Setor {random.randint(0,4)}/4 (???)")
                    print(f"Jon: Setor {random.randint(0,5)}/5 (???)")
                else:
                    print(f"\n--- FEED DAS CÂMERAS ---\nRick: Setor {self.rick_pos}/4")
                    print(f"Jon: Setor {self.jon_pos}/5" if self.jon_pos < 3 else "Jon: [não é visivel nas cameras]")
                print("------------------------")
                
                if random.randint(1, 100) == 1:
                    print(f"\n{DOS_VERMELHO}📺 [ANOMALIA DETECTADA]: O feed pisca. Em uma das câmeras escuras, o rosto quebrado de Caroline encara diretamente a lente... e ela está sorrindo para você.{RESET}")

        elif acao == "ver tubulacao":
            if self.apagao > 0 or self.erro_deteccao: print("🔴 [SENSORES OFFLINE]")
            elif self.energia <= CUSTO_INFO_LEVE: print("Sensores offline (Bateria fraca).")
            elif self.usos_sistema_turno >= 2:
                print(f"{DOS_VERMELHO}🚨 [SISTEMA SOBRECARREGADO]: Painel de detecção travado!{RESET}")
                self.energia -= CUSTO_INFO_LEVE
            else:
                self.usos_sistema_turno += 1
                self.energia -= CUSTO_INFO_LEVE
                print(f"(-{CUSTO_INFO_LEVE}% Energia)")
                if self.jon_pos >= 3 or (self.caroline_caminho == "tubulacao" and self.caroline_pos >= 4): print("🔴 Sensor fica vermelho, há um movimento nos dutos.")
                else: print("🟢 Sensor não detecta nada")

        elif acao in ["esperar", "pular noite", "pular", "set time 06:00"]:
            print("Você deixa o tempo passar...")
            turno_passou = True
            self.turno += 1
            self.alberto_troll = False
        else:
            print("Comando inválido.")
            acao_valida = False

        if acao_valida and acao not in ["esperar", "pular noite", "pular", "set time 06:00"]:
            if random.random() <= 0.10:
                quem = random.choice(["rick", "jon", "caroline"])
                if quem == "rick": self.rick_pos += 1
                elif quem == "jon": self.jon_pos += 1
                elif quem == "caroline": self.caroline_pos += 1
                print(f"\n{DOS_VERMELHO}Você ouve um ruído metálico se aproximando enquanto mexe no sistema.{RESET}")

            if self.porta_fechada:
                if self.rick_pos >= 4:
                    self.rick_pos = 0
                    print(f"\n{DOS_AMARELO} ALGO SOCA A PORTA COM VIOLÊNCIA E RECUA{RESET}")
                if (self.caroline_caminho == "porta" and self.caroline_pos >= 6):
                    self.caroline_pos = 0
                    self.caroline_caminho = random.choice(["porta", "tubulacao"])
                    print(f"\n{DOS_AMARELO} Um estrondo na porta. Ela recuou frustrada.{RESET}")
        
        pausar(4)

        if acao_valida:
            chance_evento = random.randint(1,100)
            if chance_evento <= 3:
                print(f"\n{DOS_AMARELO} Toc.. Toc.. Você escuta batidas fracas na janela, você não sabe se há algo ali, o vidro está muito sujo.{RESET}")
            elif chance_evento <= 7:
                print(f"\n{DOS_AMARELO} Você escuta ruidos vindo da ventilação... Parece que algo está arranhando o aluminio. {RESET}")
            elif chance_evento <= 9:
                print(f"\n{DOS_VERMELHO} 'Rogerio'... Você escuta algo chamar seu nome vindo do fundo do corredor.{RESET}")
            elif chance_evento <= 10:
                print(f"\n{DOS_VERMELHO} Pelo canto do seu olho, você jura ter visto algo acenando da janela, você não sabe se é algo real ou não.{RESET}")
            elif chance_evento <= 12:
                print(f"\n{DOS_VERMELHO} Você jura ter visto algo na ventilação... Será que é coisa da sua cabeça?{RESET}")
        
        pausar(4)

        if turno_passou:

            self.usos_sistema_turno = 0

            if self.turnos_gerador_ativo > 0 and acao != "ligar gerador" and acao != "Ligar gerador":
                self.turnos_gerador_ativo -= 1
                if self.turnos_gerador_ativo == 0:
                    print(f"\n{DOS_AMARELO} O gerador reserva para de soltar fumaça, e começa a dar gargalos, e depois deliga. A energia volta a ser drenada normalmente{RESET}")

            if self.turno == 12:
                print(f"\n{DOS_AMARELO} [SISTEMA] O antigo gerador está superaquecendo, cada acão custará mais energia a partir de agora.{RESET}")
            elif self.turno == 22:
                print(f"\n {DOS_AMARELO} [SISTEMA] [AVISO CRITICO!!!] O gerador superaqueceu! Geradores reservas ligados, dreno de energia aumentou!{RESET}")
            
            if self.porta_fechada and self.energia > 0:
                self.energia -= 2
                print(" A pesada porta de metal consome energia contínua... (-2% Energia)")

            if self.energia <= 0 and self.apagao == 0 and not getattr(jogo, 'god_mode', False):
                print("\n [ ENERGIA ESGOTADA ] Tudo fica escuro. A porta abre sozinha...")
                self.porta_fechada = False; self.apagao = 1; pausar(2)

            if self.porta_fechada:
                if self.rick_pos == 4: 
                    self.rick_pos = 0 
                    print("\n Você escuta batidas na porta, e passos para fora do corredor logo depois.")
                if self.caroline_caminho == "porta" and self.caroline_pos >= 5:
                    self.caroline_pos = 0
                    self.caroline_caminho = random.choice(["porta", "tubulacao"])
                    print("\n Você escuta um estrondo na porta, e depois passos apressados para a sala de jantar.")

            rick_ataque = (self.rick_pos >= 4) or (self.rick_pos == 3 and random.random() < 0.3)
            carol_porta_ataque = (self.caroline_caminho == "porta") and ((self.caroline_pos >= 6) or (self.caroline_pos == 5 and random.random() < 0.3))
            carol_duto_ataque = (self.caroline_caminho == "tubulacao" and self.caroline_pos >= 6)
            jon_ataque = (self.jon_pos >= 5)
            
            if (rick_ataque and not self.porta_fechada) or (carol_porta_ataque and not self.porta_fechada) or jon_ataque or carol_duto_ataque:
                if getattr(jogo, 'god_mode', False):
                    print(f"\n{DOS_AMARELO}[GOD MODE] Um animatrônico entra na sala... mas você o encara com um olhar mortal. Ele pede desculpas e sai de fininho.{RESET}")
                    self.rick_pos = 0; self.caroline_pos = 0; self.jon_pos = 0
                else:
                    print("\n Um animatronico conseguiu entrar.")
                    pausar(2)
                    return "morte"
            
            if self.rick_pos == 3 and not self.porta_fechada and random.random() < 0.25:
                self.rick_pos = 1 
                print(" Ouve passos pesados a se afastar da porta")
            else:
                furia_atual = self.furia + (self.turno // 6) 
                if self.rick_pos < 3: 
                    self.rick_pos = min(3, self.rick_pos + random.choice([0, 1, 1, 2]) * furia_atual)
                elif self.rick_pos == 3: 
                    self.rick_pos += random.choice([0, 1])

            if self.erro_deteccao:
                passos_jon = random.choice([1, 2, 3])
                self.jon_pos = min(5, self.jon_pos + passos_jon)
            else:
                self.jon_pos = min(5, self.jon_pos + random.choice([0, 1, 2]))
                
            self.caroline_pos = min(6, self.caroline_pos + random.choice([0, 1, 2, 3]))
            
            if self.turno >= 12 and (self.turno >= 20 or random.randint(1, 100) > 70): self.indio_janela = True
            else: self.indio_janela = False
            if random.randint(1, 100) > 80: self.alberto_troll = True

            print("\n[A atualizar sistema...]")
            pausar(3.5)

        if self.turno >= 24:
            limpar_tela()
            digitar("Você se sente aliviado quando a luz do sol começa a invadir a janela do restaurante, e o relogio marca pontualmente '06:00' ", 0.03, DOS_BRANCO)
            pausar(2)
            digitar("O sol começa a nascer. A energia retorna aos poucos.", 0.03, DOS_BRANCO)
            digitar("A porta da sala destranca.", 0.03, DOS_BRANCO)
            
            jogo.mapa["sala de jantar"]["descrição"] = "A luz da manhã invade as janelas sujas."
            jogo.mapa["hall de entrada"]["descrição"] = "O hall está iluminado."
            jogo.mapa["balcão"]["descrição"] = "A claridade revela o mofo nos doces."
            jogo.mapa["entrada"]["descrição"] = "As luzes não piscam mais."
            jogo.noite_vencida = True

            if getattr(jogo, 'fios_cortados_inventario', False):
                pausar(2)
                radar = "   .---.\n /   |   \\\n|----O----|\n \\   |   /\n   '---'"
                digitar("\nVocê saca o dispositivo.", 0.03, DOS_AMARELO)
                print(f"{DOS_VERDE}{radar}{RESET}")
                pausar(1)
                digitar("[DISPOSITIVO]: PRESENÇA ULTERIOR DETECTADA.", 0.03, DOS_VERDE)
                digitar("Ela ainda está aqui...\n", 0.04, DOS_AMARELO)
                pausar(3)
            return "vitoria_seguranca"
            
        return "continuar"