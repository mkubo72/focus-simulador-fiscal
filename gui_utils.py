import locale

def moeda(v):
    """Formata um valor numérico como moeda brasileira (R\$)."""
    return locale.currency(v, grouping=True)

def validate_float(P):
    """
    Função de validação para campos Entry do Tkinter.
    Permite apenas números de ponto flutuante (com vírgula ou ponto).
    Retorna True se a entrada é válida, False caso contrário.
    """
    if P == "":
        return True
    try:
        float(P.replace(",", "."))
        return True
    except ValueError:
        return False
