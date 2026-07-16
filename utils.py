import shlex
import unicodedata
import difflib

def normalizar(texto):
    """Remove acentos e deixa tudo em minúsculo."""
    texto_sem_acento = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    return texto_sem_acento.strip().lower()

def extrair_argumentos(comando_bruto):
    """Usa shlex para entender argumentos com múltiplas palavras entre aspas."""
    try:
        args = shlex.split(comando_bruto)
        return [normalizar(a) for a in args]
    except ValueError:
        # Fallback caso o jogador esqueça de fechar a aspa
        return [normalizar(a) for a in comando_bruto.split()]

def encontrar_melhor_match(termo, lista_opcoes, cutoff=0.70):
    """O funil de pesquisa perfeito: Exato -> Começa Com -> Contém -> Fuzzy."""
    if not termo or not lista_opcoes: return None
    
    # 1. Match Exato
    for op in lista_opcoes:
        if termo == op: return op
        
    # 2. Startswith
    for op in lista_opcoes:
        if op.startswith(termo) or termo.startswith(op): return op
        
    # 3. Substring
    for op in lista_opcoes:
        if termo in op or op in termo: return op
        
    # 4. Fuzzy Match (Rigidez de 0.70)
    sugestoes = difflib.get_close_matches(termo, lista_opcoes, n=1, cutoff=cutoff)
    return sugestoes[0] if sugestoes else None

