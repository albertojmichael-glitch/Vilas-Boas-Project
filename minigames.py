import random
from ui import DOS_VERDE, DOS_BRANCO, DOS_AMARELO, DOS_VERMELHO, RESET, limpar_tela, pausar, digitar
from data import ARTE_INDIO

CAVEIRA_ASCII = r'''
                     .ed"""" """$$$$be.
                   -"           ^""**$$$e.
                 ."                   '$$$c
                /                      "4$$b
               d  3                     $$$$
               $  * .$$$$$$
              .$  ^c           $$$$$e$$$$$$$$.
              d$L  4.         4$$$$$$$$$$$$$$b
              $$$$b ^ceeeee.  4$$ECL.F*$$$$$$$
  e$""=.      $$$$P d$$$$F $ $$$$$$$$$- $$$$$$
 z$$b. ^c     3$$$F "$$$$b   $"$$$$$$$  $$$$*"      .=""$c
4$$$$L   \     $$P"  "$$b   .$ $$$$$...e$$        .=  e$$$.
^*$$$$$c  %..   *c    ..    $$ 3$$$$$$$$$$eF     zP  d$$$$$
  "**$$$ec   "\   %ce""    $$$  $$$$$$$$$$* .r" =$$$$P""
        "*$b.  "c  *$e.    *** d$$$$$"L$$    .d"  e$$***"
          ^*$$c ^$c $$$      4J$$$$$% $$$ .e*".eeP"
             "$$$$$$"'$=e....$*$$**$cz$$" "..d$*"
               "*$$$  *=%4.$ L L$ P3$$$F $$$P"
                  "$   "%*ebJLzb$e$$$$$b $P"
                    %..      4$$$$$$$$$$ "
                     $$$e   z$$$$$$$$$$%
                      "*$c  "$$$$$$$P"
                       ."""*$$$$$$$$bc
                    .-"    .$***$$$"""*e.
                 .-"    .e$"     "*$c  ^*b.
          .=*""""    .e$*"          "*bc  "*$e..
        .$"        .z*"               ^*$e.   "*****e.
        $$ee$c   .d"                     "*$.        3.
        ^*$E")$..$"                         * .ee==d%
           $.d$$$* * J$$$e*
            """""                             "$$$"    
'''



#minigame minotauro



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
        print(f" Bateria da Lanterna: {texto_bat} turnos restantes")
        
        distancia = abs(self.px - self.mx) + abs(self.py - self.my)
        
        if distancia > 1: 
            print("[v] Você sente uma presença distante, talvez não haja perigo por enquanto.")
        elif distancia == 1:
            if random.random() < 0.2:
                print("[!] Os ecos do labirinto te confundem... não dá pra saber de onde o som vem!")
            else:
                if self.mx < self.px: print("⚠ Você sente um ar pesado em sua esquerda.")
                elif self.mx > self.px: print("⚠ Você enxerga um vulto a sua direita.")
                elif self.my > self.py: print("⚠ Você não enxerga nada a sua frente, uma mancha negra cobre o fundo.")
                elif self.my < self.py: print("⚠ Passos pesados são ouvidos atrás de você.")

        opcoes = "ir frente | ir trás | ir esquerda | ir direita | esperar"
        
        if self.px == 0 and self.py == 3 and not self.fios_cortados:
            print(" ↯ Você encontrou a caixa de fusíveis na parede central!")
            if self.tesoura_chao:
                print("	✂ Há uma tesoura caída no chão.")
                opcoes += " | pegar tesoura"
            opcoes += " | cortar fios"
            
        if self.fios_cortados:
            print(f"{DOS_VERMELHO} ↯ OS FIOS ESTÃO CORTADOS! A SALA ESTÁ DESMORONANDO! FUJA PARA A SAÍDA!{RESET}")
            if self.px == 0 and self.py == 0:
                print(f"{DOS_VERDE}⍍ A porta de entrada está logo aqui! Você pode sair!{RESET}")
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
        ui = jogo.ui_handler 

        if acao in ["celular quebrado", "ver celular quebrado", "olhar celular quebrado", "examinar celular quebrado", "investigar celular quebrado", "celular"]:
            if self.px == 0 and self.py == 3: 
                desc = jogo.mapa.get("sala de energia", {}).get("inspecionaveis", {}).get("celular quebrado", "Parece ser dela...")
                ui.exibir(f"\n{DOS_AMARELO}🔎 {desc}{RESET}")
                return "continuar"
            else:
                ui.exibir("O celular quebrado está no fundo da sala (na parede central).")
                return "continuar"
        
        if acao in ["atacar", "bater", "chutar", "lutar"] and getattr(jogo, 'god_mode', False):
            ui.exibir(f"{DOS_AMARELO}[GOD MODE] Você corre na direção do Minotauro e dá uma voadora com os dois pés no peito dele!{RESET}")
            ui.exibir(f"{DOS_AMARELO}A fera despenca para trás, choraminga em som de estática e foge rompendo as paredes.{RESET}")
            ui.pausar(2)
            return "vitoria_minotauro"

        turno_gasto = False
        
        if acao == "ir esquerda":
            if self.px > -1: self.px -= 1
            else: ui.exibir("Você bate a cara na parede...")
            turno_gasto = True 

        elif acao == "ir direita":
            if self.px < 1: self.px += 1
            else: ui.exibir("Você bate a cara na parede...")
            turno_gasto = True

        elif acao == "ir frente":
            if self.py < 3: self.py += 1
            else: ui.exibir("Você bateu na parede do fundo...")
            turno_gasto = True
            
        elif acao in ["ir trás", "ir tras", "ir atrás", "ir atras"]:
            if self.py > 0: self.py -= 1
            else: ui.exibir("Você bate as costas na porta de metal. Ela não abre...")
            turno_gasto = True

        elif acao == "esperar": 
            ui.exibir("Você fica imóvel aguardando...")
            turno_gasto = True

        elif acao == "pegar tesoura":
            if self.px == 0 and self.py == 3 and self.tesoura_chao:
                jogo.inventario.append("tesoura")
                self.tesoura_chao = False
                ui.exibir(" ✂ Você derruba a tesoura sem querer, fazendo um barulho, mas guarda na sua bolsa")
                if random.random() < 0.50:
                    self.mover_minotauro() 
                turno_gasto = True
            else: 
                ui.exibir("Não tem tesoura aqui.")

        elif acao == "cortar fios":
            if self.px == 0 and self.py == 3 and not self.fios_cortados:
                if "tesoura" in jogo.inventario:
                    ui.exibir(f"\\n{DOS_VERMELHO}Você corta os fios principais. Faíscas voam no seu rosto, mas não causam queimaduras.{RESET}")
                    ui.exibir(f"{DOS_VERMELHO} ✂ Sua tesoura quebra com a força do choque elétrico{RESET}")
                    ui.exibir(f"{DOS_VERMELHO}Ele sabe onde você está.{RESET}")
                    ui.exibir(f"{DOS_VERMELHO}CORRA DE VOLTA PARA A PORTA{RESET}")
                    
                    jogo.inventario.remove("tesoura")
                    jogo.inventario.append("tesoura quebrada")
                    
                    
                    jogo.inventario.append("fios cortados")
                    ui.exibir(f"{DOS_AMARELO}Você guarda os 'fios cortados' na mochila.{RESET}")
                    
                    self.fios_cortados = True
                    jogo.fios_cortados_inventario = True
                    turno_gasto = True
                else: 
                    ui.exibir("Você precisa de uma tesoura inteira para cortar os fios.")
                    turno_gasto = True
            else: 
                ui.exibir("Não há mais fios aqui.")
                turno_gasto = True
                
        elif acao == "sair":
            if self.px == 0 and self.py == 0:
                
                if self.fios_cortados and "fios cortados" in jogo.inventario:
                    ui.exibir(f"\\n{DOS_VERDE}Você se joga contra a maçaneta, abre a porta e a tranca com toda a força! Você sobreviveu!{RESET}")
                    ui.pausar(2)
                    return "vitoria_minotauro"
                else:
                    ui.exibir("Você está na porta de saída, Você precisa cortar e pegar os fios eletricos.")
                    turno_gasto = True
            else:
                ui.exibir("A porta de saída não fica aqui. Tente voltar para trás.")
        
        
        else: 
            ui.exibir(f"{DOS_AMARELO}Comando não reconhecido no escuro. Você gasta segundos preciosos tropeçando...{RESET}")
            turno_gasto = True 

        
        if self.px == self.mx and self.py == self.my:
            if getattr(jogo, 'god_mode', False):
                ui.exibir(f"\n{DOS_AMARELO}[GOD MODE] Você esbarra no Minotauro. Ele tenta te arranhar, mas suas garras quebram na sua pele divina! Ele foge chorando.{RESET}")
                ui.pausar(2)
                return "vitoria_minotauro"
            else:
                ui.exibir("\n Você andou direto para as mãos do monstro no escuro...")
                ui.exibir("@@JUMPSCARE@@")
                ui.pausar(2)
                ui.exibir("\n No vazio, você morre sozinho, sem poder salvar ninguém. ")
                ui.animar(CAVEIRA_ASCII, 0.005, cor="vermelho", jogo=jogo)
                return "morte"

        if turno_gasto:
            if not getattr(jogo, 'god_mode', False):
                self.bateria -= 1
                if self.bateria <= 0:
                    ui.exibir("\n A sua lanterna apaga, você entra em desespero e bate na bateria fazendo barulho.")
                    ui.pausar(2)
                    ui.exibir("\n Você sente uma mão atravessando seu estômago por trás, não há nada a se fazer.")
                    ui.animar(CAVEIRA_ASCII, 0.005, cor="vermelho", jogo=jogo)
                    return "morte"
                
            passos = 2 if random.randint(1, 100) <= self.chance_sprint else 1 
            
            if passos == 2:
                ui.exibir(f"\n{DOS_VERMELHO}⚠VOCÊ ESCUTA PASSOS PESADOS CORRENDO NA SUA DIREÇÃO!⚠{RESET}")
                ui.pausar(1.5)

            dist_antes = abs(self.px - self.mx) + abs(self.py - self.my)
            mx_old, my_old = self.mx, self.my

            for _ in range(passos):
                self.mover_minotauro()
                
            if self.px == self.mx and self.py == self.my:
                if dist_antes > 1 and passos == 1:
                    self.mx, self.my = mx_old, my_old
                    ui.exibir(f"\n{DOS_VERMELHO}⚠VOCÊ TROMBA COM ALGO GIGANTE E METÁLICO NO ESCURO! ELE ESTÁ BEM NA SUA FRENTE!⚠{RESET}")
                    ui.pausar(2)
                    return "continuar"
                else:
                    if getattr(jogo, 'god_mode', False):
                        ui.exibir(f"\n{DOS_AMARELO}[GOD MODE] O Minotauro pula em cima de você, mas é repelido por um escudo de energia! Ele desiste e foge.{RESET}")
                        ui.pausar(2)
                        return "vitoria_minotauro"
                    else:
                        ui.exibir("\n ☠ O Minotauro te encontrou no escuro. Mãos frias de metal te rasgam por inteiro ☠")
                        ui.exibir("@@JUMPSCARE@@")
                        ui.animar(CAVEIRA_ASCII, 0.005, cor="vermelho", jogo=jogo)
                        return "morte"
                
        return "continuar"



# minigame sala de segurança

import random
from ui import DOS_VERDE, DOS_BRANCO, DOS_AMARELO, DOS_VERMELHO, RESET



class MinigameSeguranca:
    def __init__(self, jogo):
        self.ui = jogo.ui_handler 
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
        
        try:
            from data import ARTE_MESA_SEGURANCA
            self.ui.exibir(f"{DOS_BRANCO}{ARTE_MESA_SEGURANCA}{RESET}")
        except:
            pass
        
        self.ui.exibir("\n" + "="*50)
        self.ui.exibir("Você senta na cadeira da sala de segurança.")
        self.ui.pausar(1)

    def imprimir_status(self):
        self.ui.limpar()
        self.ui.exibir("\n" + "=" * 50)
        chance_bug = self.caroline_pos * 15 

        def bug(texto, chance):
            return "".join([c.upper() if random.randint(1, 100) <= chance and c.isalpha() else c for c in texto])

        if self.apagao > 0: hora_disp = "[SISTEMA DESLIGADO]"
        elif self.erro_relogio: hora_disp = f"0{(self.turno * 15) // 60}:??"
        else: hora_disp = f"0{(self.turno * 15) // 60}:{(self.turno * 15) % 60:02d}"

        texto_energia = "∞" if self.energia > 100 else f"{self.energia}%"
        self.ui.exibir(bug(f"RELOGIO: {hora_disp}", chance_bug))
        self.ui.exibir(bug(f"ENERGIA: {texto_energia}", chance_bug))
        self.ui.exibir(bug(f"PORTA CENTRAL: {'Fechada' if self.porta_fechada else 'Aberta'}", chance_bug))

        erros = []
        if self.erro_camera: erros.append("CÂMERAS")
        if self.erro_relogio: erros.append("RELÓGIO")
        if self.erro_deteccao: erros.append("DETECÇÃO")
        self.ui.exibir(f"ERROS ATIVOS: {', '.join(erros)}" if erros else bug("ERROS: Nenhum", chance_bug))

        if self.turnos_gerador_ativo > 0:
            self.ui.exibir(f"{DOS_VERDE}Gerador reserva: Ativo({self.turnos_gerador_ativo} turnos restantes){RESET}")
        elif not self.gerador_reserva_usado:
            self.ui.exibir(f"{DOS_AMARELO}Gerador Reserva: Disponível{RESET}")

        if self.alberto_troll: self.ui.exibir("\n[MENSAGEM]: ERRO CRÍTICO! FECHAR PORTA AGORA!")
        if self.indio_janela and not self.erro_deteccao: self.ui.exibir("\n" + bug("Você sente como se algo estivesse te olhando pelo vidro...", chance_bug))

        self.ui.exibir("\nAção (ouvir | cameras | ver tubulacao | iluminar tubulacao | fechar porta | abrir porta | olhar vidro | ligar gerador | consertar [sistema] | esperar)")

    def processar_turno(self, acao, jogo):
        ui = self.ui
        if acao in ["pular noite", "pular", "set time 06:00"] and getattr(jogo, 'god_mode', False):
            ui.exibir(f"{DOS_AMARELO}[GOD MODE] O tempo se contorce. O relógio salta para as 06:00.{RESET}")
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
            if self.apagao > 0 or self.energia <= CUSTO_MOTOR: ui.exibir("Sem energia! O botão faz um clique morto.")
            elif self.porta_fechada: ui.exibir("A porta já está fechada.")
            else:
                self.porta_fechada = True
                self.energia -= CUSTO_MOTOR
                ui.exibir(f"A pesada porta de metal desce com um estrondo. (-{CUSTO_MOTOR}% Energia)")
                if self.alberto_troll:
                    ui.exibir("\n Como você é tão tolo? Hahahaha")
                    self.erro_camera = True; self.erro_deteccao = True; self.alberto_troll = False

        elif acao == "abrir porta":
            if self.apagao > 0 or self.energia <= CUSTO_MOTOR: ui.exibir("Sem energia! A porta não responde.")
            elif not self.porta_fechada: ui.exibir("A porta já está aberta.")
            else: 
                self.porta_fechada = False
                self.energia -= CUSTO_MOTOR
                ui.exibir(f"A porta de metal se ergue lentamente. (-{CUSTO_MOTOR}% Energia)")

        elif acao == "iluminar tubulacao":
            if self.apagao > 0 or self.energia <= CUSTO_INFO_PESADO: ui.exibir("Sem força nas luzes.")
            elif self.usos_sistema_turno >= 2:
                ui.exibir(f"{DOS_VERMELHO} [SISTEMA SOBRECARREGADO]: Muitas requisições simultâneas. Hardware travado{RESET}")
                self.energia -= CUSTO_INFO_PESADO
            else:
                self.usos_sistema_turno += 1
                self.energia -= CUSTO_INFO_PESADO
                ui.exibir(f"Você liga o projetor nos dutos (-{CUSTO_INFO_PESADO}% Energia)")
                if self.jon_pos >= 4: self.jon_pos = 0; ui.exibir("Jon recua apressado pela tubulação")
                if self.caroline_caminho == "tubulacao" and self.caroline_pos >= 5:
                    self.caroline_pos = 0; self.caroline_caminho = random.choice(["porta", "tubulacao"]) 
                    ui.exibir("A Caroline fugiu do duto")

        elif acao == "olhar vidro":
            if self.indio_janela:
                ui.limpar()
                try:
                    from data import ARTE_INDIO
                    ui.exibir(f"{DOS_BRANCO}{ARTE_INDIO}{RESET}")
                except:
                    pass
                ui.pausar(2)
                ui.exibir("Você não enxerga nada, até que 2 olhos te encaram pela janela, a figura do indio jones faz você perder a cabeça")
                falha = random.choice(["camera", "relogio", "deteccao"])
                if falha == "camera": self.erro_camera = True
                elif falha == "relogio": self.erro_relogio = True
                elif falha == "deteccao": self.erro_deteccao = True
                if self.turno < 20: self.indio_janela = False
            else:
                rick_na_porta = self.rick_pos >= 3
                carol_na_porta = (self.caroline_caminho == "porta" and self.caroline_pos >= 5)
                
                if rick_na_porta and carol_na_porta:
                    ui.exibir(" Seu corpo treme. Você vê a carcaça maciça de Rick, o mosqueteiro e a carcaça de coelho rosa retorcido de Caroline parados lado a lado no corredor, olhando diretamente para você através do vidro")
                elif rick_na_porta:
                    ui.exibir(" Você olha pelo vidro e vê a silhueta gigantesca do Rick, o mosqueteiro, parado nas sombras. Os olhos de plástico sem vida dele estão focados em você.")
                elif carol_na_porta:
                    ui.exibir(" Através da sujeira do vidro, você enxerga a carcaça do coelho rosa tentando se esconder nas sombras. Ela está encostada na parede do corredor")
                else:
                    ui.exibir("Você limpa o embaçado do vidro e força a vista para o corredor escuro. Consegue distinguir as portas fechadas das outras salas, os cartazes rasgados nas paredes e o chão de linóleo imundo refletindo a pouca luz que resta. Nenhum movimento... Além das sombras, há apenas o seu reflexo devolvendo o olhar.")

        elif acao.lower() == "ligar gerador":
            if self.apagao >0:
                ui.exibir("Tarde demais, o sistema principal já foi totalmente desligado")
            elif self.gerador_reserva_usado:
                ui.exibir("O combustivel do gerador reserva já foi queimado, ele só pode ser usado uma vez")
            else:
                ui.exibir(f"\n{DOS_VERDE} Você aperta o botão do gerador reserva, ele cospe uma fumaça preta, sistemas basicos operando sem custo de energia.{RESET}")
                self.gerador_reserva_usado = True
                self.turnos_gerador_ativo = 2
                turno_passou = True
                self.turno += 1
                self.alberto_troll = False
        
        elif acao.startswith("consertar "):
            sistema = acao.replace("consertar ", "")
            if self.apagao > 0: ui.exibir("Não há energia.")
            elif sistema == "camera": self.erro_camera = False; ui.exibir("Câmeras online.")
            elif sistema == "relogio": self.erro_relogio = False; ui.exibir("Relógio sincronizado.")
            elif sistema == "deteccao": self.erro_deteccao = False; ui.exibir("Sensores calibrados.")
            else: ui.exibir("Sistema não reconhecido.")

        elif acao == "ouvir":
            if self.apagao > 0: 
                ui.exibir("No apagão, você ouve sua própria respiração...")
            elif self.erro_deteccao: 
                ui.exibir(f"{DOS_VERMELHO}⚠ ⚠ ⚠ O alarme estridente de falha nos sensores ecoa na sala. Você não consegue ouvir nada além disso ⚠ ⚠ ⚠{RESET}")
            elif self.energia <= CUSTO_INFO_LEVE: 
                ui.exibir("Sistema de áudio offline (Bateria fraca).")
            elif self.usos_sistema_turno >= 2:
                ui.exibir(f"{DOS_VERMELHO}⚠ [SISTEMA SOBRECARREGADO]: Placa de áudio em curto. Passe o turno para resfriar!{RESET}")
                self.energia -= CUSTO_INFO_LEVE
            else:
                self.usos_sistema_turno += 1
                self.energia -= CUSTO_INFO_LEVE
                ui.exibir(f"(-{CUSTO_INFO_LEVE}% Energia)")
                ouviu = False
                if self.rick_pos >= 3 or (self.caroline_caminho == "porta" and self.caroline_pos >= 5):
                    ui.exibir(" Passos metálicos pesados são ouvidos do corredor"); ouviu = True
                if self.jon_pos >= 4 or (self.caroline_caminho == "tubulacao" and self.caroline_pos >= 5):
                    ui.exibir(" Você escuta arranhões e batidas vindo da tubulação"); ouviu = True
                if not ouviu: 
                    ui.exibir("Apenas o zumbido dos fios elétricos e da lâmpada quase apagada.")

        elif acao == "cameras":
            if self.apagao > 0 or self.erro_camera: ui.exibir("⊠ [SINAL PERDIDO]")
            elif self.energia <= CUSTO_INFO_LEVE: ui.exibir("Câmeras offline (Bateria fraca).")
            elif self.usos_sistema_turno >= 2:
                ui.exibir(f"{DOS_VERMELHO}⚠ [SISTEMA SOBRECARREGADO]: Monitor superaquecido. A tela exibe apenas estática!{RESET}")
                self.energia -= CUSTO_INFO_LEVE
            else:
                self.usos_sistema_turno += 1
                self.energia -= CUSTO_INFO_LEVE
                ui.exibir(f"(-{CUSTO_INFO_LEVE}% Energia)")
                
                chance_bug_visual = self.caroline_pos * 10
                if random.randint(1, 100) <= chance_bug_visual:
                    ui.exibir("⊠ [SINAL COM INTERFERÊNCIA] Imagens distorcidas...")
                    ui.exibir(f"Rick: Setor {random.randint(0,4)}/4 (???)")
                    ui.exibir(f"Jon: Setor {random.randint(0,5)}/5 (???)")
                else:
                    ui.exibir(f"\n--- FEED DAS CÂMERAS ---\nRick: Setor {self.rick_pos}/4")
                    ui.exibir(f"Jon: Setor {self.jon_pos}/5" if self.jon_pos < 3 else "Jon: [não é visivel nas cameras]")
                ui.exibir("------------------------")
                
                if random.randint(1, 100) == 1:
                    ui.exibir(f"\n{DOS_VERMELHO}⊠ [ANOMALIA DETECTADA]: O feed pisca. Em uma das câmeras escuras, o rosto quebrado de Caroline encara diretamente a lente... e ela está sorrindo para você.{RESET}")

        elif acao == "ver tubulacao":
            if self.apagao > 0 or self.erro_deteccao: ui.exibir("◯ [SENSORES OFFLINE]")
            elif self.energia <= CUSTO_INFO_LEVE: ui.exibir("Sensores offline (Bateria fraca).")
            elif self.usos_sistema_turno >= 2:
                ui.exibir(f"{DOS_VERMELHO}⚠ [SISTEMA SOBRECARREGADO]: Painel de detecção travado!{RESET}")
                self.energia -= CUSTO_INFO_LEVE
            else:
                self.usos_sistema_turno += 1
                self.energia -= CUSTO_INFO_LEVE
                ui.exibir(f"(-{CUSTO_INFO_LEVE}% Energia)")
                if self.jon_pos >= 3 or (self.caroline_caminho == "tubulacao" and self.caroline_pos >= 4): ui.exibir("⭙ Sensor fica vermelho, há algo nos dutos ⭙")
                else: ui.exibir("◉ Sensor não detecta nada")

        elif acao in ["esperar", "pular noite", "pular", "set time 06:00"]:
            ui.exibir("Você deixa o tempo passar...")
            turno_passou = True
            self.turno += 1
            self.alberto_troll = False
        else:
            ui.exibir("Comando inválido.")
            acao_valida = False

        if acao_valida and acao not in ["esperar", "pular noite", "pular", "set time 06:00"]:
            if random.random() <= 0.10:
                quem = random.choice(["rick", "jon", "caroline"])
                if quem == "rick": self.rick_pos += 1
                elif quem == "jon": self.jon_pos += 1
                elif quem == "caroline": self.caroline_pos += 1
                ui.exibir(f"\n{DOS_VERMELHO}Você ouve um ruído metálico se aproximando enquanto mexe no sistema.{RESET}")

            if self.porta_fechada:
                if self.rick_pos >= 4:
                    self.rick_pos = 0
                    ui.exibir(f"\n{DOS_AMARELO} ALGO SOCA A PORTA COM VIOLÊNCIA E RECUA{RESET}")
                if (self.caroline_caminho == "porta" and self.caroline_pos >= 6):
                    self.caroline_pos = 0
                    self.caroline_caminho = random.choice(["porta", "tubulacao"])
                    ui.exibir(f"\n{DOS_AMARELO} Um estrondo na porta. Ela recuou...{RESET}")
        
        ui.pausar(4)

        if acao_valida:
            chance_evento = random.randint(1,100)
            if chance_evento <= 3:
                ui.exibir(f"\n{DOS_AMARELO} Toc.. Toc.. Você escuta batidas fracas na janela, você não sabe se há algo ali, o vidro está muito sujo.{RESET}")
            elif chance_evento <= 7:
                ui.exibir(f"\n{DOS_AMARELO} Você escuta ruidos vindo da ventilação... Parece que algo está arranhando o aluminio. {RESET}")
            elif chance_evento <= 9:
                ui.exibir(f"\n{DOS_VERMELHO} 'Rogerio'... Você escuta algo chamar seu nome vindo do fundo do corredor.{RESET}")
            elif chance_evento <= 10:
                ui.exibir(f"\n{DOS_VERMELHO} Pelo canto do seu olho, você jura ter visto algo acenando da janela, você não sabe se é algo real ou não.{RESET}")
            elif chance_evento <= 12:
                ui.exibir(f"\n{DOS_VERMELHO} Você jura ter visto algo na ventilação... Será que é coisa da sua cabeça?{RESET}")
        
        ui.pausar(4)

        if turno_passou:
            self.usos_sistema_turno = 0
            if self.turnos_gerador_ativo > 0 and acao.lower() != "ligar gerador":
                self.turnos_gerador_ativo -= 1
                if self.turnos_gerador_ativo == 0:
                    ui.exibir(f"\n{DOS_AMARELO} O gerador reserva para de soltar fumaça, e começa a dar gargalos, e depois deliga. A energia volta a ser drenada normalmente{RESET}")

            if self.turno == 12:
                ui.exibir(f"\n{DOS_AMARELO} [SISTEMA] O antigo gerador está superaquecendo, cada acão custará mais energia a partir de agora.{RESET}")
            elif self.turno == 22:
                ui.exibir(f"\n {DOS_AMARELO} [SISTEMA] [AVISO CRITICO!!!] O gerador superaqueceu! Geradores reservas ligados, dreno de energia aumentou!{RESET}")
            
            if self.porta_fechada and self.energia > 0:
                self.energia -= 2
                ui.exibir(" A pesada porta de metal consome energia contínua... (-2% Energia)")

            if self.energia <= 0 and self.apagao == 0 and not getattr(jogo, 'god_mode', False):
                ui.exibir("\n [ ENERGIA ESGOTADA ] Tudo fica escuro. A porta abre sozinha...")
                self.porta_fechada = False; self.apagao = 1; ui.pausar(2)

            if self.porta_fechada:
                if self.rick_pos == 4: 
                    self.rick_pos = 0 
                    ui.exibir("\n Você escuta batidas na porta, e passos para fora do corredor logo depois.")
                if self.caroline_caminho == "porta" and self.caroline_pos >= 5:
                    self.caroline_pos = 0
                    self.caroline_caminho = random.choice(["porta", "tubulacao"])
                    ui.exibir("\n Você escuta um estrondo na porta, e depois passos apressados para a sala de jantar.")

            rick_ataque = (self.rick_pos >= 4) or (self.rick_pos == 3 and random.random() < 0.3)
            carol_porta_ataque = (self.caroline_caminho == "porta") and ((self.caroline_pos >= 6) or (self.caroline_pos == 5 and random.random() < 0.3))
            carol_duto_ataque = (self.caroline_caminho == "tubulacao" and self.caroline_pos >= 6)
            jon_ataque = (self.jon_pos >= 5)
            
            if (rick_ataque and not self.porta_fechada) or (carol_porta_ataque and not self.porta_fechada) or jon_ataque or carol_duto_ataque:
                if getattr(jogo, 'god_mode', False):
                    ui.exibir(f"\n{DOS_AMARELO}[GOD MODE] Um animatrônico entra na sala... mas você o encara. Ele pede desculpas e sai de fininho.{RESET}")
                    self.rick_pos = 0; self.caroline_pos = 0; self.jon_pos = 0
                else:
                    ui.exibir("\n Um animatronico conseguiu entrar.")
                    ui.exibir("@@JUMPSCARE@@")
                    ui.pausar(2)
                    return "morte"
            
            if self.rick_pos == 3 and not self.porta_fechada and random.random() < 0.25:
                self.rick_pos = 1 
                ui.exibir(" Ouve passos pesados a se afastar da porta")
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
            if random.randint(1, 100) > 80 and not getattr(jogo, 'alberto_desativado', False): 
                self.alberto_troll = True

            ui.exibir("\n[A atualizar sistema...]")
            ui.pausar(3.5)

        if self.turno >= 24:
            ui.limpar()
            try:
                from views import digitar
                digitar("Você se sente aliviado quando a luz do sol começa a invadir a janela do restaurante, e o relogio marca pontualmente '06:00' ", 0.03, DOS_BRANCO)
                ui.pausar(2)
                digitar("O sol começa a nascer. A energia retorna aos poucos.", 0.03, DOS_BRANCO)
                digitar("A porta da sala destranca.", 0.03, DOS_BRANCO)
            except:
                ui.exibir("Você se sente aliviado quando a luz do sol começa a invadir a janela do restaurante, e o relogio marca pontualmente '06:00' ")
                ui.pausar(2)
                ui.exibir("O sol começa a nascer. A energia retorna aos poucos.")
                ui.exibir("A porta da sala destranca.")
            
            jogo.mapa["sala de jantar"]["descrição"] = "A luz da manhã invade as janelas sujas."
            jogo.mapa["hall de entrada"]["descrição"] = "O hall está iluminado."
            jogo.mapa["balcão"]["descrição"] = "A claridade revela o mofo nos doces."
            jogo.mapa["entrada"]["descrição"] = "As luzes não piscam mais."
            jogo.noite_vencida = True

            if getattr(jogo, 'fios_cortados_inventario', False):
                ui.pausar(2)
                try:
                    from data import ARTE_RADAR
                    radar = ARTE_RADAR
                except:
                    radar = "   .---.\n /   |   \\\n|----O----|\n \\   |   /\n   '---'"
                
                try:
                    digitar("\nVocê saca o dispositivo.", 0.03, DOS_AMARELO)
                    ui.exibir(f"{DOS_VERDE}{radar}{RESET}")
                    ui.pausar(1)
                    digitar("[DISPOSITIVO]: PRESENÇA ULTERIOR DETECTADA.", 0.03, DOS_VERDE)
                    digitar("Ela ainda está aqui...\n", 0.04, DOS_AMARELO)
                except:
                    ui.exibir("\nVocê saca o dispositivo.")
                    ui.exibir(f"{DOS_VERDE}{radar}{RESET}")
                    ui.pausar(1)
                    ui.exibir("[DISPOSITIVO]: PRESENÇA ULTERIOR DETECTADA.")
                    ui.exibir("Ela ainda está aqui...\n")
                ui.pausar(3)
            return "vitoria_seguranca"
            
        return "continuar"