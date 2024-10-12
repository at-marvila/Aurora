# Aurora - Soluções de IA Inteligente para Supermercados

[![Licença](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE) ![Status do Build](https://img.shields.io/badge/build-passing-brightgreen)

## Descrição

**Aurora** é uma solução de inteligência artificial projetada para transformar a experiência de compras em supermercados. Integrando tecnologias de ponta como reconhecimento de fala e processamento de linguagem natural (NLP), Aurora oferece interações personalizadas com os clientes e otimiza a gestão interna dos supermercados. Com Aurora, estabelecimentos podem proporcionar atendimento ágil, intuitivo e adaptado às necessidades do mercado varejista.

## Índice

- [Instalação](#instalação)
  - [Pré-requisitos](#pré-requisitos)
  - [Passos](#passos)
- [Configuração](#configuração)
  - [Configurações de Arquivos](#configurações-de-arquivos)
  - [Variáveis de Ambiente](#variáveis-de-ambiente)
- [Uso](#uso)
  - [Exemplos de Comandos](#exemplos-de-comandos)
  - [Principais Fluxos de Trabalho](#principais-fluxos-de-trabalho)
- [Contribuição](#contribuição)
  - [Relatório de Bugs](#relatório-de-bugs)
  - [Sugestões de Melhorias](#sugestões-de-melhorias)
- [Licença](#licença)
- [Contato](#contato)

## Instalação

### Pré-requisitos

- **Python 3.x** (certifique-se de estar atualizado com a versão recomendada)
- **Firebase**: Acesso a um banco de dados Firebase para integração de dados e armazenamento.
- **Dependências**: Listadas no arquivo `requirements.txt`.
- **Conexão com a Internet**: Necessária para utilizar as APIs externas.

### Passos

1. **Clone o repositório**:

    ```bash
    git clone https://github.com/username/repo.git
    ```

2. **Navegue para o diretório do projeto**:

    ```bash
    cd Aurora
    ```

3. **Crie um ambiente virtual**:

    ```bash
    python -m venv env
    source env/bin/activate  # Para Linux/MacOS
    .\env\Scripts\activate   # Para Windows
    ```

4. **Instale as dependências**:

    ```bash
    pip install -r requirements.txt
    ```

5. **Configurações de ambiente**: Defina as variáveis de ambiente (veja a seção [Configuração](#configuração)).

6. **Execute o script principal**:

    ```bash
    python -m core.aurora
    ```

## Configuração

### Configurações de Arquivos

A Aurora utiliza arquivos de configuração em formatos YAML e JSON. Esses arquivos estão no diretório `config/` para facilitar a manutenção e o acesso.

- **intent_actions.yaml**: Define ações com base em frases ou reconhecimento de voz.
- **employees.json**: Armazena informações dos colaboradores para personalizar interações.

### Variáveis de Ambiente

Configure as seguintes variáveis de ambiente para assegurar o funcionamento correto da Aurora:

- `FIREBASE_API_KEY`: Chave de API do Firebase para acesso ao banco de dados e armazenamento.
- `FIREBASE_PROJECT_ID`: ID do projeto Firebase.
- `AURORA_ENV`: Ambiente de execução (`development`, `staging`, `production`).
- `REDIS_URL`: URL de conexão para o cache Redis (se aplicável).
- `GOOGLE_CLOUD_SPEECH_CREDENTIALS`: Credenciais para integração com o Google Cloud Speech-to-Text.

## Uso

### Exemplos de Comandos

Aqui estão alguns exemplos de comandos para interagir com a Aurora:

```bash
# Verificar voz registrada de um cliente
python -m core.aurora --action "verificar voz"

# Registrar um novo cliente
python -m core.aurora --action "cadastro cliente"

# Consultar a promoção do dia
python -m core.aurora --action "qual a promoção do dia"