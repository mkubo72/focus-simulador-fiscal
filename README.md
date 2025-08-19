Focus Simulador Fiscal (Projeto FOCUS)

Simulador fiscal para ICMS-ST, DIFAL, PIS/COFINS e geração de saída (GUI e PDF).

⚙️ Requisitos

Python 3.11 (recomendado)

Pip atualizado

🧰 Instalação
pip install -r requirements.txt


Se você estiver no Windows e aparecer aviso de “Pillow / tk”, instale o Python com opção de “tcl/tk” habilitada (padrão do instalador oficial).

▶️ Executar a aplicação (GUI)
python main_app.py


A interface abre (Tkinter). Use os controles para simular operações e gerar relatórios.

✅ Rodar testes (local)
python -m unittest -v


Os testes usam test_focus_current.py e validam os principais caminhos do módulo fiscal.

🤖 GitHub Actions (CI)

O repositório possui workflow em .github/workflows/tests.yml.

Sempre que você enviar arquivos ao GitHub, os testes rodam automaticamente.

O selo no topo deste README mostra o status atual (verde = ok).

🗂️ Estrutura do projeto
.
├── config.py
├── data_manager.py
├── empresa.json
├── fiscal_logic.py
├── gui_utils.py
├── last_vendedor.json
├── main_app.py
├── parametros_fiscais.json
├── pdf_generator.py
├── pis_cofins.json
├── README.md
├── requirements.txt
├── sacola.json
├── test_focus_current.py
├── vendedores.json
└── .github/
    └── workflows/
        └── tests.yml

Principais arquivos

fiscal_logic.py — regras de ICMS-ST, DIFAL, PIS/COFINS (cálculos).

config.py — constantes, UFs com exceção, configurações gerais.

main_app.py — GUI (Tkinter).

pdf_generator.py — geração de PDF do resultado.

data_manager.py — leitura e persistência de dados.

gui_utils.py — helpers de interface e formatação.

*.json — bases de parâmetros e exemplos.

🔢 Parâmetros principais (JSON)

parametros_fiscais.json

MVA por UF/CF, ICMS interno/interestadual, FCP, protocolos, ativação de ST.

pis_cofins.json

Alíquotas por tipo de operação (Revenda, Consumo, etc.).

empresa.json, vendedores.json, last_vendedor.json

Identificação e contato.

sacola.json

Exemplos de itens para simulação.

Dica: mantenha esses arquivos sob versionamento (commits) para rastrear mudanças fiscais.

🛠️ Dúvidas comuns

1) A aba “Actions” não mostra o workflow.
Verifique se existe o arquivo .github/workflows/tests.yml.
No GitHub, você pode criar manualmente: Add file → Create new file e nomear como
.github/workflows/tests.yml (cole o conteúdo do workflow).

2) O badge não aparece.
Confirme se o repositório é mkubo72/focus-simulador-fiscal e se o arquivo do workflow chama tests.yml.

3) Erro ao abrir GUI (Tkinter).
Instale o Python oficial (Windows/Mac) ou, no Linux, instale python3-tk.

📦 Empacotamento (opcional)

Você pode criar um executável (ex.: PyInstaller). Um exemplo de spec já existe no projeto (quando aplicável).
No geral:

pip install pyinstaller
pyinstaller --name AssistenteFiscal --onefile main_app.py


Ajustes de assets (JSONs) podem ser necessários via --add-data.

🔒 Política de mudanças

Este projeto segue a regra: não modificar código existente sem autorização explícita.

Novas funções devem vir marcadas com comentários # NOVO.

Alterações em funções existentes: # ALTERADO.

Sempre incluir changelog no final de cada entrega.

📄 Licença

Defina aqui sua licença (ex.: MIT).
