# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.
O formato é baseado no [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

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