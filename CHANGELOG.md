# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.
O formato é baseado no [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

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
