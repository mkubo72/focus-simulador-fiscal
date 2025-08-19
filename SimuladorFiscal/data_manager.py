import json
import os
from datetime import datetime
from tkinter import messagebox
import config

def salvar_tudo():
    """Salva todos os dados da aplicação em arquivos JSON."""
    os.makedirs(config.CAMINHO_DADOS, exist_ok=True)
    os.makedirs(config.DIR_COTACOES, exist_ok=True)
    os.makedirs(config.DIR_ARQUIVADAS, exist_ok=True)

    parametros = {
        "ibpt_validade": config.ibpt_validade, "cf_dict": config.cf_dict, "ibpt_fed": config.ibpt_fed,
        "ibpt_est": config.ibpt_est, "cf_to_ncm": config.cf_to_ncm, "descricoes": config.descricoes,
        "mva_dict": {f"{uf}-{cf}": v for (uf, cf), v in config.mva_dict.items()},
        "fcp_dict": {f"{uf}-{cf}": v for (uf, cf), v in config.fcp_dict.items()},
        "icms_interno_dict": {f"{uf}-{cf}": v for (uf, cf), v in config.icms_interno_dict.items()},
        "icms_inter_dict": {f"{uf}-{cf}": v for (uf, cf), v in config.icms_inter_dict.items()},
        "protocolo_dict": {f"{uf}-{cf}": v for (uf, cf), v in config.protocolo_dict.items()},
        "mensagem_dict": {f"{uf}-{cf}": v for (uf, cf), v in config.mensagem_dict.items()},
        "st_ativo_dict": {f"{uf}-{cf}": v for (uf, cf), v in config.st_ativo_dict.items()},
    }
    try:
        with open(config.ARQ_CONFIG, "w", encoding="utf-8") as f:
            json.dump(parametros, f, ensure_ascii=False, indent=2)
        with open(config.ARQ_SACOLA, "w", encoding="utf-8") as f:
            json.dump(config.itens_sacola, f, ensure_ascii=False, indent=2)
        with open(config.ARQ_EMPRESA, "w", encoding="utf-8") as f:
            json.dump(config.empresa_orcamento, f, ensure_ascii=False, indent=2)
        with open(config.ARQ_VENDEDORES, "w", encoding="utf-8") as f:
            json.dump(config.vendedores_cadastrados, f, ensure_ascii=False, indent=2)
        with open(config.ARQ_LAST_VENDEDOR, "w", encoding="utf-8") as f:
            json.dump({"last_vendedor_code": config.last_selected_vendedor_code}, f, ensure_ascii=False, indent=2)
        with open(config.ARQ_PIS_COFINS, "w", encoding="utf-8") as f:
            json.dump(config.pis_cofins_dict, f, ensure_ascii=False, indent=2)

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao salvar dados: {e}")

def carregar_tudo():
    """Carrega todos os dados da aplicação a partir de arquivos JSON."""
    try:
        if os.path.exists(config.ARQ_CONFIG):
            with open(config.ARQ_CONFIG, "r", encoding="utf-8") as f:
                parametros = json.load(f)
                config.ibpt_validade = parametros.get("ibpt_validade", "2000-01-01")
                config.cf_dict.update(parametros.get("cf_dict", {}))
                config.ibpt_fed.update(parametros.get("ibpt_fed", {}))
                config.ibpt_est.update(parametros.get("ibpt_est", {}))
                config.cf_to_ncm.update(parametros.get("cf_to_ncm", {}))
                config.descricoes.update(parametros.get("descricoes", {}))

                def load_dict_with_tuple_keys(data_dict_str):
                    new_dict = {}
                    for k_str, v in data_dict_str.items():
                        parts = k_str.split('-')
                        if len(parts) == 2:
                           uf, cf = parts
                           new_dict[(uf, cf)] = v
                    return new_dict

                config.mva_dict.clear(); config.mva_dict.update(load_dict_with_tuple_keys(parametros.get("mva_dict", {})))
                config.fcp_dict.clear(); config.fcp_dict.update(load_dict_with_tuple_keys(parametros.get("fcp_dict", {})))
                config.icms_interno_dict.clear(); config.icms_interno_dict.update(load_dict_with_tuple_keys(parametros.get("icms_interno_dict", {})))
                config.icms_inter_dict.clear(); config.icms_inter_dict.update(load_dict_with_tuple_keys(parametros.get("icms_inter_dict", {})))
                config.protocolo_dict.clear(); config.protocolo_dict.update(load_dict_with_tuple_keys(parametros.get("protocolo_dict", {})))
                config.mensagem_dict.clear(); config.mensagem_dict.update(load_dict_with_tuple_keys(parametros.get("mensagem_dict", {})))
                config.st_ativo_dict.clear(); config.st_ativo_dict.update(load_dict_with_tuple_keys(parametros.get("st_ativo_dict", {})))
        else:
            config.reset_fiscal_params()
            salvar_tudo()
    except (json.JSONDecodeError, Exception) as e:
        messagebox.showerror("Erro de Carregamento", f"Erro ao carregar parâmetros fiscais: {e}. Redefinindo para os padrões.")
        config.reset_fiscal_params()
        salvar_tudo()

    try:
        if os.path.exists(config.ARQ_SACOLA):
            with open(config.ARQ_SACOLA, "r", encoding="utf-8") as f:
                config.itens_sacola.clear()
                config.itens_sacola.extend(json.load(f))
    except (json.JSONDecodeError, Exception):
        config.itens_sacola.clear()

    try:
        if os.path.exists(config.ARQ_EMPRESA):
            with open(config.ARQ_EMPRESA, "r", encoding="utf-8") as f:
                dados_empresa_salvos = json.load(f)
                config.empresa_orcamento.clear()
                config.empresa_orcamento.update(dados_empresa_salvos)
    except (json.JSONDecodeError, Exception):
        pass

    try:
        if os.path.exists(config.ARQ_VENDEDORES):
            with open(config.ARQ_VENDEDORES, "r", encoding="utf-8") as f:
                config.vendedores_cadastrados.clear()
                config.vendedores_cadastrados.extend(json.load(f))
        else:
            config.reset_vendedores()
    except (json.JSONDecodeError, Exception):
        config.reset_vendedores()

    try:
        if os.path.exists(config.ARQ_LAST_VENDEDOR):
            with open(config.ARQ_LAST_VENDEDOR, "r", encoding="utf-8") as f:
                data = json.load(f)
                config.last_selected_vendedor_code = data.get("last_vendedor_code", "")
    except (json.JSONDecodeError, FileNotFoundError):
        config.last_selected_vendedor_code = ""

    config.reset_pis_cofins()
    try:
        if os.path.exists(config.ARQ_PIS_COFINS):
            with open(config.ARQ_PIS_COFINS, "r", encoding="utf-8") as f:
                loaded_pc = json.load(f)
                config.pis_cofins_dict.update(loaded_pc)
    except (json.JSONDecodeError, Exception):
        pass

def gerar_numero_cotacao(vendedor_codigo):
    agora = datetime.now()
    mes_dia = agora.strftime("%m%d")
    ano_curto = agora.strftime("%y")
    max_seq = 0
    try:
        os.makedirs(config.DIR_COTACOES, exist_ok=True)
        for arq in os.listdir(config.DIR_COTACOES):
            if arq.endswith(".json") and not arq.endswith("_cotacao.json"):
                nome_base = arq.split('.')[0]
                parts = nome_base.split('-')
                if len(parts) == 2:
                    data_vend_seq = parts[0]
                    ano_arq = parts[1]
                    if ano_arq == ano_curto and data_vend_seq.startswith(mes_dia):
                        try:
                            file_vendedor_code_part = data_vend_seq[4:-2]
                            if file_vendedor_code_part == vendedor_codigo:
                                seq_str = data_vend_seq[-2:]
                                current_seq = int(seq_str)
                                if current_seq > max_seq:
                                    max_seq = current_seq
                        except (ValueError, IndexError):
                            pass
    except Exception as e:
        print(f"Erro ao buscar sequencial de cotação: {e}")
    next_seq = max_seq + 1
    return f"{mes_dia}{vendedor_codigo}{next_seq:02d}-{ano_curto}"