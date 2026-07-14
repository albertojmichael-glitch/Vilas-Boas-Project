import sys
import os
import time
import colorama
import re  

# INICIALIZA SEM O AUTORESET!
colorama.init() 
if sys.platform == "win32":
    os.system("color") 

# ==========================================
# CONFIGURAÇÕES GERAIS E CORES
# ==========================================
DEBUG_MODE = False # Mude para True para pular delays de texto durante testes

DOS_VERDE = '\033[92m'    
DOS_BRANCO = '\033[97m'   
DOS_AMARELO = '\033[93m'  
DOS_VERMELHO = '\033[91m' 
RESET = '\033[0m'         

# ==========================================
# FUNÇÕES DE INTERFACE (UI)
# ==========================================
def limpar_tela():
    """Limpa a tela imprimindo linhas em branco."""
    print("\n" * 50)

def pausar(segundos):
    """Substitui o time.sleep para respeitar o DEBUG_MODE."""
    if not DEBUG_MODE:
        time.sleep(segundos)

def digitar(texto, tempo_base=0.03, cor="", jogo=None):
    """Imprime texto com delay, lidando corretamente com códigos ANSI de cor."""
    texto_final = f"{cor}{texto}{RESET}" if cor else texto
    
    if DEBUG_MODE:
        print(texto_final)
        return
        
    tempo_real = tempo_base
    
    # Acelera o texto com base no estado de tensão do jogo
    if jogo is not None:
        if getattr(jogo, 'hp', 3) <= 1:
            tempo_real = 0.005  
        elif getattr(jogo, 'turnos_no_escuro', 0) >= 3:
            tempo_real = 0.01   
        
    # Fatia a string separando os códigos ANSI (que começam com \033[ e terminam com m) do texto normal
    partes = re.split(r'(\033\[[0-9;]*m)', texto_final)
    
    for parte in partes:
        if parte.startswith('\033['):
            # Se a parte for um código de cor, imprime inteiro instantaneamente para o terminal entender
            sys.stdout.write(parte)
        else:
            # Se for o texto, imprime letra por letra com o efeito de digitação
            for letra in parte:
                sys.stdout.write(letra)
                sys.stdout.flush()
                time.sleep(tempo_real)
    print()