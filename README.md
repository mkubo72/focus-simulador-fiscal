# Focus Simulador Fiscal (Projeto FOCUS)

Simulador fiscal para operações de ICMS-ST, DIFAL, PIS/COFINS e geração de relatórios.

## Como usar

1. Instale dependências:
   ```bash
   pip install -r requirements.txt
   ```

2. Execute a aplicação principal:
   ```bash
   python main_app.py
   ```

3. Rode os testes automatizados:
   ```bash
   python -m unittest -v
   ```

## GitHub Actions (CI)

Este repositório já inclui configuração para rodar testes automáticos com GitHub Actions.

Toda vez que você enviar arquivos para o GitHub, os testes serão executados automaticamente.
