# Aurora - Smart AI Solutions for Supermarkets

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE) ![Build Status](https://img.shields.io/badge/build-passing-brightgreen)

## Descrição

**Aurora** é uma inteligência artificial avançada projetada para transformar a experiência de compras em supermercados. Ao integrar tecnologias de ponta como reconhecimento de fala e processamento de linguagem natural (NLP), Aurora personaliza a interação com os clientes e otimiza a gestão interna do supermercado. Com Aurora, os estabelecimentos podem oferecer um atendimento mais ágil, intuitivo e personalizado, adaptando-se às necessidades dinâmicas do mercado de varejo.

## Índice

- [Instalação](#instalação)
  - [Pré-requisitos](#pré-requisitos)
  - [Passos](#passos)
- [Configuração](#configuração)
  - [Configurações de Arquivos](#configurações-de-arquivos)
  - [Variáveis de Ambiente](#variáveis-de-ambiente)
- [Uso](#uso)
  - [Exemplos de Comandos](#exemplos-de-comandos)
  - [Fluxos de Trabalho](#fluxos-de-trabalho)
- [Contribuição](#contribuição)
  - [Relatório de Bugs](#relatório-de-bugs)
  - [Sugestões de Melhorias](#sugestões-de-melhorias)
- [Licença](#licença)
- [Contato](#contato)

## Instalação

### Pré-requisitos

- Python 3.x
- Dependências adicionais listadas em `requirements.txt`
- Acesso a um banco de dados Firebase (para integração de dados e armazenamento)
- Conexão com a internet para utilizar APIs externas

### Passos

1. Clone o repositório:

    ```bash
    git clone https://github.com/username/repo.git
    ```

2. Navegue para o diretório do projeto:

    ```bash
    cd repo
    ```

3. Crie um ambiente virtual:

    ```bash
    python -m venv env
    source env/bin/activate  # Para Linux/MacOS
    .\env\Scripts\activate   # Para Windows
    ```

4. Instale as dependências:

    ```bash
    pip install -r requirements.txt
    ```

5. Configure as variáveis de ambiente conforme necessário (veja a seção [Configuração](#configuração)).

6. Execute o script principal:

    ```bash
    python -m aurora.core.aurora
    ```

## Configuração

### Configurações de Arquivos

O projeto utiliza arquivos de configuração em formato YAML e JSON. Esses arquivos podem ser encontrados no diretório `data/` e são usados para definir as ações e intenções que a IA pode executar.

- **intent_actions.yaml**: Define as ações que Aurora pode realizar com base em frases específicas ou reconhecimento de voz.
- **employees.json**: Armazena informações dos colaboradores para personalizar interações.

### Variáveis de Ambiente

Certifique-se de configurar as seguintes variáveis de ambiente para que o projeto funcione corretamente:

- `FIREBASE_API_KEY`: Chave de API do Firebase para acessar o banco de dados e armazenamento.
- `FIREBASE_PROJECT_ID`: ID do projeto Firebase.
- `AURORA_ENV`: Define o ambiente de execução (`development`, `staging`, `production`).

## Uso

### Exemplos de Comandos

Aqui estão alguns exemplos de como interagir com a Aurora:

```bash
# Para verificar a voz registrada de um cliente
python -m aurora.core.aurora --action "verificar voz"

# Para registrar um novo cliente
python -m aurora.core.aurora --action "cadastro cliente"

# Para consultar a promoção do dia
python -m aurora.core.aurora --action "qual a promoção do dia"
