import locale
import os
import sys

if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    except locale.Error:
        print(
            "AVISO: Não foi possível configurar o locale 'pt_BR'. A formatação de moeda pode usar o padrão do sistema.")

cfs = ['A', 'B', 'C', 'D']
ufs = sorted([
    'AC', 'AL', 'AM', 'AP', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MG', 'MS', 'MT', 'PA', 'PB', 'PE', 'PI',
    'PR', 'RJ', 'RN', 'RO', 'RR', 'RS', 'SC', 'SE', 'SP', 'TO'
])

ufs_sem_st_difal = {
    'AC', 'AL', 'AM', 'BA', 'CE', 'ES', 'MA', 'MT', 'PA', 'PB', 'PI', 'RR', 'GO', 'SC', 'SE', 'RO'
}

operacoes = ['Revenda', 'Consumo', 'Consumo sem IE', 'Industrialização', 'Regime Especial']
ibpt_validade = "2025-06-30"

cf_dict = {'A': 0.00, 'B': 9.75, 'C': 9.75, 'D': 3.25}
ibpt_fed = {'A': 13.45, 'B': 15.92, 'C': 10.00, 'D': 14.33}
ibpt_est = {'A': 18.00, 'B': 18.00, 'C': 18.00, 'D': 18.00}
cf_to_ncm = {'A': '8535.1000', 'B': '8536.1000', 'C': '8546.9000', 'D': '8535.3019'}
descricoes = {
    'A': 'Fusível alta tensão (>1000V)',
    'B': 'Fusível até 1000V',
    'C': 'Isolador de resina',
    'D': 'Chave seccionadora'
}

mva_dict = {}
fcp_dict = {}
icms_interno_dict = {}
icms_inter_dict = {}
protocolo_dict = {}
mensagem_dict = {}
st_ativo_dict = {}
pis_cofins_dict = {}

CAMINHO_DADOS = os.path.join(base_path, "dados")
ARQ_CONFIG = os.path.join(CAMINHO_DADOS, "parametros_fiscais.json")
ARQ_SACOLA = os.path.join(CAMINHO_DADOS, "sacola.json")
ARQ_EMPRESA = os.path.join(CAMINHO_DADOS, "empresa.json")
ARQ_VENDEDORES = os.path.join(CAMINHO_DADOS, "vendedores.json")
ARQ_LAST_VENDEDOR = os.path.join(CAMINHO_DADOS, "last_vendedor.json")
ARQ_PIS_COFINS = os.path.join(CAMINHO_DADOS, "pis_cofins.json")
DIR_COTACOES = os.path.join(CAMINHO_DADOS, "cotacoes")
DIR_ARQUIVADAS = os.path.join(CAMINHO_DADOS, "cotacoes_arquivadas")

itens_sacola = []
empresa_orcamento = {
    "nome": "ELETRO BRASIL LTDA", "cnpj": "12.345.678/0001-90",
    "endereco": "Rua das Indústrias, 123", "contato": "comercial@eletrobrasil.com.br",
    "fone": "(11) 4002-8922"
}
vendedores_cadastrados = []
last_selected_vendedor_code = ""

def reset_fiscal_params():
    global mva_dict, fcp_dict, icms_interno_dict, icms_inter_dict, protocolo_dict, mensagem_dict, st_ativo_dict
    mva_dict.clear(); fcp_dict.clear(); icms_interno_dict.clear(); icms_inter_dict.clear(); protocolo_dict.clear(); mensagem_dict.clear(); st_ativo_dict.clear()
    dados_aliquotas_por_uf = {
        'AC': [7.00, 19.00, 0.00, 'Não se aplica', 'Não'], 'AL': [7.00, 19.00, 1.00, 'Não se aplica', 'Não'],
        'AM': [7.00, 20.00, 0.00, 'Não se aplica', 'Não'], 'AP': [7.00, 18.00, 0.00, 'ICMS113 - 16/12/11', 'Sim'],
        'BA': [7.00, 21.00, 0.00, 'Não se aplica', 'Não'], 'CE': [7.00, 20.00, 0.00, 'Não se aplica', 'Não'],
        'DF': [7.00, 20.00, 0.00, 'ICMS 22 - 01/04/2011', 'Sim'], 'ES': [7.00, 17.00, 0.00, 'Não se aplica', 'Não'],
        'GO': [7.00, 19.00, 0.00, '83/2011', 'Não'], 'MA': [7.00, 23.00, 0.00, 'Não se aplica', 'Não'],
        'MG': [12.00, 18.00, 0.00, '39/2009', 'Sim'], 'MS': [7.00, 17.00, 0.00, 'Não se aplica', 'Não'],
        'MT': [7.00, 17.00, 0.00, 'ICMS 11 - 05/03/2008', 'Não'], 'PA': [7.00, 19.00, 0.00, 'Não se aplica', 'Não'],
        'PB': [7.00, 20.00, 0.00, 'Não se aplica', 'Não'], 'PE': [7.00, 21.00, 0.00, '132/2010', 'Sim'],
        'PI': [7.00, 23.00, 0.00, 'Não se aplica', 'Não'], 'PR': [12.00, 20.00, 0.00, '26-13/03/2013', 'Sim'],
        'RJ': [12.00, 20.00, 2.00, '33 - 17/07/2014', 'Sim'], 'RN': [7.00, 20.00, 0.00, 'Não se aplica', 'Não'],
        'RO': [7.00, 20.00, 0.00, 'Não se aplica', 'Não'], 'RR': [7.00, 20.00, 0.00, 'Não se aplica', 'Não'],
        'RS': [12.00, 17.00, 0.00, '91/2009', 'Não'], 'SC': [12.00, 17.00, 0.00, '117 - 03/09/2012', 'Não'],
        'SE': [7.00, 22.00, 0.00, 'Não se aplica', 'Não'], 'SP': [18.00, 18.00, 0.00, 'Não se aplica', 'Sim'],
        'TO': [7.00, 20.00, 0.00, 'Não se aplica', 'Não'],
    }
    for uf in ufs:
        for cf in cfs:
            dados_uf = dados_aliquotas_por_uf.get(uf, [7.00, 18.00, 0.00, '', False])
            icms_inter_dict[(uf, cf)] = dados_uf[0]; icms_interno_dict[(uf, cf)] = dados_uf[1]; fcp_dict[(uf, cf)] = dados_uf[2]
            protocolo_dict[(uf, cf)] = dados_uf[3]; st_ativo_dict[(uf, cf)] = (dados_uf[4] == 'Sim'); mva_dict[(uf, cf)] = 0.0; mensagem_dict[(uf, cf)] = ''

def reset_pis_cofins():
    global pis_cofins_dict
    pis_cofins_dict.clear()
    pis_cofins_dict.update({
        'Revenda': {'pis': 0.65, 'cofins': 3.00},
        'Consumo': {'pis': 0.65, 'cofins': 3.00},
        'Consumo sem IE': {'pis': 0.65, 'cofins': 3.00},
        'Industrialização': {'pis': 0.65, 'cofins': 3.00},
        'Regime Especial': {'pis': 0.65, 'cofins': 3.00},
    })

def reset_vendedores():
    global vendedores_cadastrados
    vendedores_cadastrados = [
        {'nome': 'José', 'codigo': '1', 'email': 'jose@empresa.com', 'celular': '(11) 98765-4321'},
        {'nome': 'Marcelo', 'codigo': '2', 'email': 'marcelo@empresa.com', 'celular': '(11) 91234-5678'}
    ]