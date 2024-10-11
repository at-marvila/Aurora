def generate_supermarket_id(supermarket_name, state_code, city_code, district_code, store_number):
    """
    Gera uma chave composta para o ID do supermercado.
    :param supermarket_name: Nome da rede de supermercado.
    :param state_code: Código do estado.
    :param city_code: Código da cidade.
    :param district_code: Código do bairro.
    :param store_number: Número da loja dentro da cidade/bairro.
    :return: ID composto do supermercado.
    """
    return f"{supermarket_name}-{state_code}-{city_code}-{district_code}-{store_number}"