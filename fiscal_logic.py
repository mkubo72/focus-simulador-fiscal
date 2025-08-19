import config
import gui_utils

UFS_COM_CALCULO_ESPECIFICO_CONSUMO = {'AP', 'MG', 'PR', 'RJ'}

def calcular_revenda(params):
    """
    Cálculo de ICMS-ST para operação de Revenda.
    Agora inclui FECP-ST (quando aplicável) SOMENTE na Revenda,
    condicionado a:
      - ST ativo para a UF/CF, e
      - FCP > 0 parametrizado para a UF/CF.
    O retorno traz:
      result (str), icms_st_principal (float), fcp_st (float)
    """
    mva = params['mva']
    icms_inter = params['icms_inter']
    icms_int = params['icms_int']
    base_icms = params['base_icms']
    icms_origem = params['icms_origem']
    uf_destino = params['uf_destino']
    st_ativo = params['st_ativo']
    fcp = params.get('fcp', 0.0)

    result = ""
    icms_st_principal = 0.0
    fcp_st = 0.0
    base_st = 0.0

    st_bloqueado = (uf_destino in config.ufs_sem_st_difal or not st_ativo)
    if st_bloqueado:
        result += f"\n! A UF {uf_destino} não exige ICMS-ST (ST Ativo: {'Sim' if st_ativo else 'Não'})."
    else:
        # MVA ajustada e base ST
        mva_ajustada = ((1 + mva / 100) * ((1 - icms_inter / 100) / (1 - icms_int / 100))) - 1
        base_st = base_icms * (1 + mva_ajustada)

        # ICMS-ST principal (sem FECP)
        icms_st_principal = round(base_st * icms_int / 100 - icms_origem, 2)
        if icms_st_principal < 0:
            icms_st_principal = 0.0

        # NOVO: FECP-ST somente na Revenda quando FCP>0
        if fcp and fcp > 0:
            fcp_st = round(base_st * fcp / 100, 2)
        else:
            fcp_st = 0.0

        icms_st_total = icms_st_principal + fcp_st

        # Mensagem detalhada
        if fcp_st > 0:
            result += (
                f"\n+ MVA Ajustada: {round(mva_ajustada * 100, 2):.2f}% | "
                f"Base ST: {gui_utils.moeda(base_st)} | "
                f"ICMS ST: {gui_utils.moeda(icms_st_principal)} | "
                f"FECP-ST: {gui_utils.moeda(fcp_st)} | "
                f"ST Total: {gui_utils.moeda(icms_st_total)}"
            )
        else:
            result += (
                f"\n+ MVA Ajustada: {round(mva_ajustada * 100, 2):.2f}% | "
                f"Base ST: {gui_utils.moeda(base_st)} | "
                f"ICMS ST: {gui_utils.moeda(icms_st_principal)}"
            )

    # Retorna o principal e o FECP-ST separados
    return result, icms_st_principal, fcp_st


def calcular_consumo(params):
    icms_inter = params['icms_inter']
    icms_int = params['icms_int']
    fcp = params.get('fcp', 0.0)

    icms_int_efetiva = icms_int + fcp
    base_icms_com_ipi = params['base_icms']
    icms_origem = params['icms_origem']
    uf_destino = params['uf_destino']
    st_ativo = params['st_ativo']

    ufs_com_difal = {'AP', 'DF', 'MG', 'PE', 'PR', 'RJ'}
    if uf_destino not in ufs_com_difal or not st_ativo:
        return f"\n! A UF {uf_destino} não exige DIFAL para esta operação.", 0, 0

    difal_total = 0
    fcp_valor = 0

    if uf_destino in UFS_COM_CALCULO_ESPECIFICO_CONSUMO:
        base_intermediaria = base_icms_com_ipi * (1 - (icms_inter / 100))
        base_final_difal = base_intermediaria / (1 - (icms_int_efetiva / 100))
        icms_destino_total = round(base_final_difal * (icms_int_efetiva / 100), 2)
        difal_total = round(icms_destino_total - icms_origem, 2)
        if difal_total < 0:
            difal_total = 0
        fcp_valor = round(base_final_difal * (fcp / 100), 2)
        difal_principal = difal_total - fcp_valor

        result = (
            f"\n+ Base DIFAL: {gui_utils.moeda(base_final_difal)} | "
            f"DIFAL (principal): {gui_utils.moeda(difal_principal)} | "
            f"FCP: {gui_utils.moeda(fcp_valor)} | "
            f"GNRE A RECOLHER: {gui_utils.moeda(difal_total)}"
        )
        return result, difal_total, fcp_valor

    elif uf_destino == 'PE':
        bscdf = (base_icms_com_ipi - icms_origem) / (1 - (icms_int / 100))
        difal_principal = round(bscdf * ((icms_int - icms_inter) / 100), 2)
        fcp_valor = round(bscdf * (fcp / 100), 2)
        difal_total = difal_principal + fcp_valor
        if difal_total < 0:
            difal_total = 0

        result = (
            f"\n+ Base DIFAL: {gui_utils.moeda(bscdf)} | "
            f"DIFAL (principal): {gui_utils.moeda(difal_principal)} | "
            f"FCP: {gui_utils.moeda(fcp_valor)} | "
            f"GNRE A RECOLHER: {gui_utils.moeda(difal_total)}"
        )
        return result, difal_total, fcp_valor

    else:
        icms_destino_valor = base_icms_com_ipi * (icms_int_efetiva / 100)
        icms_origem_valor = base_icms_com_ipi * (icms_inter / 100)
        difal_total = round(icms_destino_valor - icms_origem_valor, 2)
        if difal_total < 0:
            difal_total = 0
        fcp_valor = round(base_icms_com_ipi * (fcp / 100), 2)
        difal_principal = difal_total - fcp_valor

        result = (
            f"\n+ Base DIFAL: {gui_utils.moeda(base_icms_com_ipi)} | "
            f"DIFAL (principal): {gui_utils.moeda(difal_principal)} | "
            f"FCP: {gui_utils.moeda(fcp_valor)} | "
            f"GNRE A RECOLHER: {gui_utils.moeda(difal_total)}"
        )
        return result, difal_total, fcp_valor


def calcular_consumo_sem_ie(params):
    icms_int = params['icms_int']
    icms_inter = params['icms_inter']
    fcp = params.get('fcp', 0.0)

    icms_int_efetiva = icms_int + fcp
    base_icms = params['base_icms']
    uf_destino = params['uf_destino']
    st_ativo = params['st_ativo']

    difal_total = 0
    fcp_valor = 0

    if uf_destino in config.ufs_sem_st_difal or not st_ativo:
        return f"\n! A UF {uf_destino} não exige DIFAL (DIFAL Ativo: {'Sim' if st_ativo else 'Não'}).", 0, 0
    else:
        icms_destino_valor = base_icms * (icms_int_efetiva / 100)
        icms_origem_valor = base_icms * (icms_inter / 100)
        difal_total = round(icms_destino_valor - icms_origem_valor, 2)
        if difal_total < 0:
            difal_total = 0
        fcp_valor = round(base_icms * (fcp / 100), 2)
        difal_principal = difal_total - fcp_valor

        result = (
            f"\n+ Base DIFAL: {gui_utils.moeda(base_icms)} | "
            f"DIFAL (principal): {gui_utils.moeda(difal_principal)} | "
            f"FCP: {gui_utils.moeda(fcp_valor)} | "
            f"GNRE A RECOLHER: {gui_utils.moeda(difal_total)}"
        )
        return result, difal_total, fcp_valor


def calcular_industrializacao(params):
    return "\n+ Operação de industrialização não gera ST ou DIFAL.", 0, 0


def simular_sacola():
    total_geral = 0
    total_produtos = 0
    tot_ipi = 0
    tot_pis = 0
    tot_cofins = 0
    tot_icms_st = 0
    tot_difal = 0
    tot_fcp = 0
    tot_ibpt_fed = 0
    tot_ibpt_est = 0

    contem_consumo_sem_ie = False

    if not config.itens_sacola:
        return None, None, None, None, None, None, None

    primeiro_item = config.itens_sacola[0]
    uf_destino_cabecalho = primeiro_item['uf_destino']
    cf_cabecalho = primeiro_item['cf']

    icms_inter_cabecalho = config.icms_inter_dict.get((uf_destino_cabecalho, cf_cabecalho), 0)
    icms_int_cabecalho = config.icms_interno_dict.get((uf_destino_cabecalho, cf_cabecalho), 0)
    fcp_cabecalho = config.fcp_dict.get((uf_destino_cabecalho, cf_cabecalho), 0)

    resumo = (
        f"\n--- RESUMO DO ORÇAMENTO ---\n\n"
        f"ICMS Interestadual ({icms_inter_cabecalho:.2f}%) / "
        f"ICMS Interno ({icms_int_cabecalho:.2f}%) / "
        f"FCP ({fcp_cabecalho:.2f}%)\n"
        f"Faturado para: {uf_destino_cabecalho}\n"
    )

    for idx, it in enumerate(config.itens_sacola, 1):
        op = it['operacao']
        valor = it['valor']
        uf_destino = it['uf_destino']
        cf = it['cf']

        descricao = it.get('descricao_usuario') or config.descricoes.get(cf, 'Descrição N/A')
        ncm = config.cf_to_ncm.get(cf, 'NCM_N/A')

        ipi_pct = config.cf_dict.get(cf, 0.0)
        ipi_val = round(valor * ipi_pct / 100, 2)
        base_icms_com_ipi = valor + ipi_val

        icms_inter = config.icms_inter_dict.get((uf_destino, cf), 12.0)
        icms_int = config.icms_interno_dict.get((uf_destino, cf), 18.0)
        fcp = config.fcp_dict.get((uf_destino, cf), 0.0)

        if op == "Revenda":
            icms_origem = round(valor * icms_inter / 100, 2)
        else:
            icms_origem = round(base_icms_com_ipi * icms_inter / 100, 2)

        aliquotas_pc = config.pis_cofins_dict.get(op, {'pis': 0.0, 'cofins': 0.0})
        pis_pct = aliquotas_pc.get('pis', 0.0)
        cofins_pct = aliquotas_pc.get('cofins', 0.0)

        if op == "Consumo":
            base_piscofins = valor - (valor * (icms_inter / 100))
        else:
            base_piscofins = valor - icms_origem

        pis = round(base_piscofins * (pis_pct / 100), 2)
        cofins = round(base_piscofins * (cofins_pct / 100), 2)

        if op == "Consumo sem IE":
            contem_consumo_sem_ie = True

        if op in ["Consumo", "Consumo sem IE"]:
            trib_fed_pct = config.ibpt_fed.get(cf, 0.0)
            trib_est_pct = config.ibpt_est.get(cf, 0.0)
            trib_fed = round(trib_fed_pct * valor / 100, 2)
            trib_est = round(trib_est_pct * valor / 100, 2)
        else:
            trib_fed_pct, trib_est_pct, trib_fed, trib_est = 0.0, 0.0, 0, 0

        params = {
            'base_icms': base_icms_com_ipi,
            'icms_origem': icms_origem,
            'icms_inter': icms_inter,
            'icms_int': icms_int,
            'fcp': fcp,
            'uf_destino': uf_destino,
            'mva': config.mva_dict.get((uf_destino, cf), 0.0),
            'st_ativo': config.st_ativo_dict.get((uf_destino, cf), True),
        }

        icms_st_total_item = 0.0
        difal = 0.0
        fcp_item = 0.0
        bloco_calculo = ""

        if op == "Revenda":
            # calcular_revenda agora retorna (texto, icms_st_principal, fcp_st)
            bloco_calculo, icms_st_principal, fcp_item = calcular_revenda(params)
            icms_st_total_item = icms_st_principal + fcp_item
        elif op == "Consumo":
            bloco_calculo, difal, fcp_item = calcular_consumo(params)
        elif op == "Consumo sem IE":
            bloco_calculo, difal, fcp_item = calcular_consumo_sem_ie(params)
        elif op == "Industrialização":
            bloco_calculo, difal, fcp_item = calcular_industrializacao(params)

        # Total cliente por item: soma IPI + ST (com FECP quando Revenda) + DIFAL
        total_cliente_item = round(valor + ipi_val + icms_st_total_item + difal, 2)

        # Acumulações
        total_geral += total_cliente_item
        total_produtos += valor
        tot_ipi += ipi_val
        tot_pis += pis
        tot_cofins += cofins

        # NOVO: tot_icms_st deve refletir ICMS-ST + FECP-ST na Revenda
        if op == "Revenda":
            tot_icms_st += icms_st_total_item
        else:
            tot_icms_st += 0.0

        tot_difal += difal
        tot_fcp += fcp_item  # util para auditoria/consulta

        tot_ibpt_fed += trib_fed
        tot_ibpt_est += trib_est

        # Texto
        resumo += f"\nItem {idx}: {descricao} | NCM: {ncm} | Total: {gui_utils.moeda(valor)} | Op: {op}\n"
        resumo += bloco_calculo

        bloco_ibpt_str = ""
        if trib_fed > 0 or trib_est > 0:
            bloco_ibpt_str = (
                f" | IBPT Fed ({trib_fed_pct:.2f}%): {gui_utils.moeda(trib_fed)} | "
                f"IBPT Est ({trib_est_pct:.2f}%): {gui_utils.moeda(trib_est)}"
            )

        resumo += (
            f"\n IPI: {gui_utils.moeda(ipi_val)} | "
            f"Base PIS/COFINS: {gui_utils.moeda(base_piscofins)} | "
            f"PIS: {gui_utils.moeda(pis)} ({pis_pct:.2f}%) | "
            f"COFINS: {gui_utils.moeda(cofins)} ({cofins_pct:.2f}%)"
        )
        resumo += bloco_ibpt_str

        if difal > 0:
            resumo += f"\n GNRE A RECOLHER: {gui_utils.moeda(difal)}"
        if op == "Revenda" and icms_st_total_item > 0:
            resumo += f"\n ICMS ST: {gui_utils.moeda(icms_st_total_item)}"

        resumo += f"\n Cliente paga: {gui_utils.moeda(total_cliente_item)}\n"

        # Atualiza o item para uso no PDF e no texto de e-mail
        it.update({
            'ipi': ipi_val,
            'icms_origem': icms_origem,
            # Guardar o total de ST (incluindo FECP-ST quando Revenda)
            'icms_st': icms_st_total_item if op == "Revenda" else 0.0,
            'fcp_st': fcp_item if op == "Revenda" else 0.0,
            'difal': difal,
            'total_cliente': total_cliente_item,
            'ipi_pct': ipi_pct,
            'icms_int_pct': icms_int,
            # Para Consumo, este campo já era usado como FCP; aqui fica útil para auditoria
            'fcp': fcp_item
        })

    # Totalização final da nota
    if contem_consumo_sem_ie:
        total_final_nota = total_produtos + tot_ipi
    else:
        total_final_nota = total_geral

    resumo += f"\n===== TOTALIZAÇÃO FINAL ====="
    resumo += f"\nTotal Produtos: {gui_utils.moeda(total_produtos)}"
    resumo += f"\nTotal IPI: {gui_utils.moeda(tot_ipi)}"
    if tot_icms_st > 0:
        resumo += f"\nTotal ICMS ST: {gui_utils.moeda(tot_icms_st)}"
    if tot_difal > 0:
        resumo += f"\nTotal GNRE A RECOLHER: {gui_utils.moeda(tot_difal)}"
    resumo += f"\nTotal PIS: {gui_utils.moeda(tot_pis)}"
    resumo += f"\nTotal COFINS: {gui_utils.moeda(tot_cofins)}"

    total_ibpt = tot_ibpt_fed + tot_ibpt_est
    if total_ibpt > 0 and total_produtos > 0:
        percentual_ibpt = (total_ibpt / total_produtos) * 100
        resumo += f"\nTotal Aprox. Tributos (IBPT): {gui_utils.moeda(total_ibpt)} ({percentual_ibpt:.2f}%)"

    resumo += f"\n*** Total Final da Nota Fiscal: {gui_utils.moeda(total_final_nota)} ***"

    if contem_consumo_sem_ie:
        resumo += f"\n\nOBSERVAÇÃO DIFAL EMBUTIDO de {gui_utils.moeda(tot_difal)}"
        resumo += '\n"MERCADORIA SEGUE PARA USO E CONSUMO. RECOLHIMENTO DO DIFAL PARA NÃO CONTRIBUINTE CONFORME EC 87/2015 E CONVÊNIO ICMS 93/2015."'

    resumo += f"\nMaterial tem como destino: {primeiro_item['operacao'].upper()}\n"

    return total_produtos, tot_ipi, tot_icms_st, tot_difal, total_final_nota, tot_fcp, resumo
