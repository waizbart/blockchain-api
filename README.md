# API Blockchain - Denúncias Anônimas

Uma API baseada em blockchain para denúncias anônimas, construída com FastAPI e a blockchain Polygon.

Tudo o que foi proposto pelo grupo no quadro gira foi implementado com sucesso.

-----

## Estrutura do Projeto

```
app/
├── adapters/         # Adaptadores para serviços externos
├── blockchain/       # Código de interação com a blockchain
├── controllers/      # Endpoints da API
├── core/             # Configuração principal
├── db/               # Configuração do banco de dados e dados iniciais (seed)
├── factories/        # Fábricas para criação de objetos
├── models/           # Modelos do banco de dados
├── repositories/     # Camada de acesso a dados
├── schemas/          # DTOs (Objetos de Transferência de Dados)
├── services/         # Camada de lógica de negócios
├── strategies/       # Implementações de estratégias
└── utils.py          # Funções utilitárias
```

-----

## Padrões de Projeto

### Padrão Repository (Repositório)

O padrão Repository cria uma camada de abstração entre o acesso a dados e as camadas de lógica de negócios de uma aplicação. Isso ajuda com:

  - Centralizar a lógica de acesso a dados
  - Tornar a aplicação mais fácil de manter e testar
  - Permitir a troca fácil entre diferentes fontes de dados

Exemplo: `app/repositories/denuncia.py`

### Padrão Service Layer (Camada de Serviço)

O padrão Service Layer fornece um conjunto de serviços da aplicação que definem o limite da aplicação e seu conjunto de operações disponíveis sob a perspectiva das camadas cliente. Isso ajuda com:

  - Garantir que a lógica de negócios não seja espalhada pelos controllers
  - Abstrair operações complexas
  - Facilitar testes e manutenção

Exemplo: `app/services/denuncia_service.py`

### Padrão Factory (Fábrica)

O padrão Factory fornece uma interface para criar objetos sem especificar suas classes concretas. Isso ajuda com:

  - Encapsular a lógica de criação de objetos
  - Facilitar a alteração de implementações
  - Suportar o Princípio Aberto/Fechado (Open/Closed Principle)

Exemplo: `app/factories/blockchain_factory.py`

### Padrão Strategy (Estratégia)

O padrão Strategy define uma família de algoritmos, encapsula cada um deles e os torna intercambiáveis. Isso ajuda com:

  - Suportar múltiplas implementações da mesma interface
  - Tornar os algoritmos independentes dos clientes que os utilizam
  - Adicionar novas estratégias sem modificar o código existente

Exemplo: `app/strategies/blockchain_provider.py` e implementações

### Padrão Adapter (Adaptador)

O padrão Adapter permite que objetos com interfaces incompatíveis colaborem. Isso helps com:

  - Integrar bibliotecas de terceiros com interfaces diferentes
  - Fazer código legado funcionar com sistemas modernos
  - Isolar o código cliente dos detalhes de implementação

Exemplo: `app/adapters/ipfs_adapter.py`

### Injeção de Dependência

Uso do sistema de injeção de dependência do FastAPI para injetar repositórios e serviços nos controllers. Isso ajuda com:

  - Baixo acoplamento entre componentes
  - Testes mais fáceis através de mocking
  - Código mais limpo

Exemplo: Controllers usando `Depends(get_auth_service)`

### DTOs (Objetos de Transferência de Dados)

Uso de modelos Pydantic para validar e transformar dados entre a API e a aplicação. Isso ajuda com:

  - Validação de entrada
  - Separação dos modelos da API dos modelos de domínio
  - Documentação da API mais clara

Exemplo: `app/schemas/denuncia.py`

-----

## Começando

1.  Clone o repositório
2.  Crie um ambiente virtual: `python -m venv .venv`
3.  Ative o ambiente virtual:
      * Windows: `.venv\Scripts\activate`
      * Linux/Mac: `source .venv/bin/activate`
4.  Instale as dependências: `pip install -r requirements.txt`
5.  Configure o arquivo `.env` com suas credenciais da Polygon
6.  Execute a aplicação: `uvicorn app.main:app --reload`

-----

## Documentação da API

Com a aplicação em execução, acesse a documentação Swagger UI em: [http://localhost:8000/docs](https://www.google.com/search?q=http://localhost:8000/docs)