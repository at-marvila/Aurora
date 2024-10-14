# Aurora Engine

### Overview
O **Aurora Engine** é uma assistente virtual personalizada, desenvolvida especificamente para o ambiente de supermercados. A solução é composta por dois principais componentes:

- **Aurora Assistente Virtual**: Interage diretamente com usuários e colaboradores em cada supermercado, automatizando processos e facilitando operações.
- **Aurora Hub**: Portal centralizado premium, que oferece visualizações, relatórios e insights para a gestão estratégica.

### Principais Tecnologias

- **Backend**:
  - **Python**: Implementação do motor de IA e processamento.
  - **Node.js**: Expansão para o frontend do Aurora Hub.
  
- **Reconhecimento de Voz e NLP**:
  - **speech_recognition**: Testes iniciais.
  - **Google Cloud Speech-to-Text**: Reconhecimento de voz de alta precisão.
  - **SpeechBrain + Transformers**: Para embeddings vetoriais e processamento de linguagem natural avançado.

- **Banco de Dados e Cache**:
  - **Firebase Firestore**: Armazenamento persistente e estruturado para dados de configuração e perfil de colaboradores.
  - **Redis Vetorial**: Cache para armazenamento rápido de embeddings vetoriais.

- **Infraestrutura**:
  - **Docker e Kubernetes**: Orquestração de contêineres para escalabilidade.
  - **Google Cloud Platform (GCP)**: Ambiente de hospedagem.

- **Autenticação e Segurança**:
  - **OAuth 2.0 e Firebase Authentication**: Controle de acesso seguro.
  - **Google Secret Manager**: Armazenamento seguro de chaves.

### Estrutura de Dados

#### Firebase Firestore
- **Estrutura Hierárquica**:
  - **Regions / States / Cities / Supermarkets**: Organização de dados por localidade.
  - **Documentos de Supermercado**:
    - **store_configuration**: Configurações específicas da loja.
    - **employees**: Perfis de colaboradores.
    - **workspace_access**: Permissões para o Aurora Hub.

#### Redis (Vetorial)
- **Chaves Estruturadas por Supermercado**:
  - **intention e response**: Embeddings vetoriais, organizados e reutilizáveis.
  - **Perfis de Colaboradores**: Chaves únicas para cada supermercado e colaborador.

### Organização de Arquivos

- **core/embedding_manager.py**: Centraliza o gerenciamento dos embeddings no Redis.
- **core/embedding_loader.py**: Carrega e verifica embeddings ao iniciar.
- **core/embedding_processor.py**: Processa e prepara dados de intents e responses.
- **data/intents/**: Configurações de intents e responses para o Aurora.

### Fluxo de Processamento

1. **Pré-Processamento de Embeddings**:
   - `embedding_processor.py` gera embeddings a partir de `actions.yaml` e `responses.yaml`, armazenando no Redis com chaves organizadas.

2. **Carregamento Inicial**:
   - `embedding_loader.py` verifica e carrega embeddings existentes do Redis para o Aurora.

3. **Operação do Aurora**:
   - **Interação**: Acessa intents e responses processados, oferecendo respostas rápidas e precisas.

### Fluxo de Interação e Ativação

- **Ativação e Segurança**:
  - Validação e ativação seguras com chaves armazenadas no Google Secret Manager.
  
- **Interação do Usuário**:
  - Comando “Oi Aurora” inicia a interação.
  - Embeddings do Redis garantem respostas rápidas e eficientes.

- **Aurora Hub**:
  - Permite acesso diferenciado a relatórios e insights estratégicos com controle de permissões.

### Configuração e Início do Projeto

1. **Instalação de Dependências**:
   Utilize o [Poetry](https://python-poetry.org/) para gerenciar as dependências:
   ```bash
   poetry install
