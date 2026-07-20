# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.
O formato é baseado no [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

## [1.3.0] - 2026-07-20
### Adicionado
- **Histórico de Comandos:** Implementação de navegação de terminal via setas direcionais (`ArrowUp` e `ArrowDown`) com armazenamento em memória na sessão do navegador.
- **Sintetizador de Áudio (MS-DOS):** Injeção de feedback sonoro de hardware via `AudioContext` nativo do JavaScript (sem dependência de arquivos de áudio externos), simulando os *beeps* e *boops* da placa-mãe.
- **Atalhos Globais de Teclado:** Suporte a atalhos clássicos de terminal (`Ctrl+L` para limpar a tela, `Ctrl+S` para verificação visual de save e `?` para ajuda).
- **Acessibilidade (a11y):** Inclusão de atributos ARIA, *Live Regions* (`aria-live="polite"`) e classes `.sr-only` para suporte a leitores de tela.
- **Menu de Ajuda Contextual:** Adição de modal responsivo com lista de comandos básicos e atalhos, ativado via UI ou teclado.
- **Cache de Estáticos:** Interceptador nativo no Flask (`@app.after_request`) para forçar o cache de CSS e JS no navegador do cliente (1 hora).

### Modificado
- **Direção Artística (Fim dos Emojis):** Expurgados todos os emojis modernos da interface gráfica, substituídos por padronização ASCII (ex: `⨹`, `☠`, `✕`) para maximizar a imersão de 1982.
- **HUD Retrô:** Barra de progresso de HP reimaginada utilizando caracteres de bloco (`[██░]`) e reatividade de cor (verde para seguro, vermelho para perigo).
- **Estética de Monitor CRT:** Adição de `text-shadow` sutil no CSS para emular o vazamento de luz (glow) do fósforo verde/âmbar e ajuste no `line-height` para otimização de leitura.
- **UX de Carregamento (Anti-Flicker):** Inserção de uma barreira de atraso mínimo de 300ms na animação de carregamento (`spinner`) para evitar flashes visuais bruscos quando a latência de rede é próxima de zero.

### Corrigido
- **O Bug do "Fantasma do Cache" (F5):** Aplicação de cabeçalhos estritos de *No-Cache* na rota `/iniciar` e reestruturação da geração de *Session IDs* (SIDs). Agora, forçar a atualização da página pelo navegador reseta corretamente a máquina de estados do servidor para a tela de Boot, prevenindo bloqueios irreversíveis.
- **Minotauro Silencioso (Timeout Exploit):** Refatoração no bloco de tratamento de comandos da classe `MinigameMinotauro`. Comandos inválidos ou não reconhecidos deixaram de ser ignorados silenciosamente e passaram a consumir o turno do jogador, deduzindo bateria e movendo o monstro, com o devido feedback narrativo de penalidade.

## [1.2.0] - 2026-07-17
### Adicionado
- **Persistência em Nuvem (MongoDB):** Integração nativa com banco de dados NoSQL MongoDB (`pymongo`) via MongoDB Atlas, garantindo retenção perpétua dos dados de progresso e contornando a limpeza de arquivos efêmeros do Render.
- **Mecanismo de Salvamento Híbrido:** Arquitetura inteligente que detecta a presença de `MONGO_URI` em variáveis de ambiente, alternando dinamicamente entre persistência na nuvem (produção) ou fallback em disco local (desenvolvimento).
- **Cofre de Sessões em RAM:** Barreira de isolamento via dicionário de execução interna em `app.py`, evitando problemas de vazamento de contexto e falhas de serialização (*pickling/decoding*) entre jogadores simultâneos.
- **Ambiente de Testes Isolado (`MockUI`):** Implementação de uma interface simulada em `tests/test_game.py` para prevenir erros de execução nula (`AttributeError: 'NoneType' object has no attribute 'limpar'`) durante execuções automáticas.
- **Pipeline Automatizada (`make push`):** Inclusão de um fluxo operacional unificado no `Makefile` que auto-formata o código, executa linters e roda testes locais antes de enviar as atualizações ao repositório.

### Modificado
- **Suíte de Testes Determinísticos:** Atualização das asserções da Seed 42 no teste do Minotauro para validar com precisão a lógica de ataque imediato (bateria decrementada para 14 e estado de morte) mapeada na engine.
- **Documentação Exaustiva da API:** Expansão das referências no `README.md` detalhando as assinaturas completas de payload, contratos JSON de entrada/saída e códigos de status HTTP (200, 400 e 500) para os endpoints `/iniciar` e `/comando`.

### Segurança
- **Failsafe de Produção:** Injeção de cláusula de validação estrita no boot do `app.py` que derruba intencionalmente a aplicação em ambientes de produção (`RENDER`) se a chave `FLASK_SECRET_KEY` estiver utilizando os valores padrão de desenvolvimento.

### Corrigido
- **Duplicação de Código em `state.py`:** Expurgados os métodos repetidos de serialização/desserialização herdados da transição para a sintaxe do Pydantic V2 (`model_dump` e `model_validate`).
- **Sintaxe do Makefile:** Eliminação de comandos Git órfãos que causavam quebra de interpretação estrutural por estarem fora de escopos de *targets*.
- **Mapeamento de Importações no GitHub Actions:** Ajuste fino na declaração de dependências do fluxo com a injeção da flag `PYTHONPATH=.`, extinguindo falhas do tipo `ModuleNotFound` induzidas pela árvore de caminhos do Linux.
- **Quebra de Renderização da Arte ASCII:** Substituição do desenho complexo do cofre (`ARTE_COFRE`) por um layout compacto simétrico, prevenindo o colapso horizontal de linhas ocasionado pelas margens automáticas de navegadores.

## [1.1.0] - 2026-07-17
### Adicionado
- Flask-Session para gerenciamento assíncrono e isolado de saves por cookie.
- Motor Unificado (`engine.py`) para tratar lógica independente de UI (Web/CLI).
- Suíte completa de testes automatizados com `pytest` cobrindo cenários determinísticos (Seed 42).
- CI/CD via GitHub Actions.

### Modificado
- Remoção do hack `sys.stdout` em favor de Buffer JSON estruturado na WebUI.
- Modificador de Dificuldade de Velocidade (`fast_mode`) desvinculado de Game Modes absolutos.
- Mapa de rotas e dependência do item 'tesoura' atrelado rigorosamente à geolocalização da `sala_atual`.
