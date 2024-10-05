# utils.py

def generate_supermarket_id(supermarket_chain_code, city_code, district_code, store_number):
    """
    Gera uma chave composta para o ID do supermercado.
    :param supermarket_chain_code: Código da rede de supermercado.
    :param city_code: Código da cidade.
    :param district_code: Código do bairro.
    :param store_number: Número da loja dentro da cidade/bairro.
    :return: ID composto do supermercado.
    """
    return f"{supermarket_chain_code}-{city_code}-{district_code}-{store_number}"