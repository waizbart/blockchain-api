# Sistema de Registro de Denúncias na Blockchain

## 📋 Visão Geral

O sistema utiliza blockchain (Polygon) para garantir **imutabilidade** e **transparência** dos registros de denúncias. Cada denúncia é hasheada e registrada na blockchain, criando uma prova criptográfica de sua existência e integridade.

### Benefícios da Blockchain

- **🔒 Imutabilidade**: Registros não podem ser alterados após confirmação
- **🌐 Transparência**: Dados públicos e verificáveis
- **🛡️ Integridade**: Hash criptográfico previne adulteração
- **📝 Auditabilidade**: Histórico completo de transações
- **🔗 Descentralização**: Não dependente de servidor central

## 🏗️ Arquitetura do Sistema

### Componentes Principais

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Blockchain    │
│   (React/Vue)   │────│   (FastAPI)     │────│   (Polygon)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                       ┌─────────────────┐
                       │   Database      │
                       │   (SQLite)      │
                       └─────────────────┘
```

### Fluxo de Dados

1. **Criação da Denúncia** → Frontend coleta dados
2. **Validação** → Backend valida dados
3. **Hash Generation** → Gera hash SHA-256 dos dados
4. **Blockchain Registration** → Registra hash na blockchain
5. **Database Storage** → Armazena dados completos localmente
6. **Severity Analysis** → Analisa severidade com LLM
7. **Response** → Retorna confirmação com TX hash

## 🔧 Implementação Técnica

### Estrutura de Dados

#### Denúncia (Input)

```json
{
    "descricao": "Descrição da denúncia",
    "categoria": "CORRUPCAO|VIOLENCIA|TRAFICO|AMBIENTAL|OUTROS",
    "latitude": -23.5505,
    "longitude": -46.6333,
    "datetime": "2024-01-15T10:30:00Z",
    "user_uuid": "opcional-uuid-anonimo"
}
```

#### Hash Generation

```python
def generate_hash(denuncia_data: dict) -> str:
    """Gera hash determinístico dos dados da denúncia"""
    # Remove campos variáveis que não afetam o conteúdo
    hashable_data = {
        "descricao": denuncia_data["descricao"],
        "categoria": denuncia_data["categoria"],
        "latitude": denuncia_data.get("latitude"),
        "longitude": denuncia_data.get("longitude")
    }
    
    # Serializa de forma determinística
    json_string = json.dumps(hashable_data, sort_keys=True, separators=(',', ':'))
    
    # Gera hash SHA-256
    return hashlib.sha256(json_string.encode('utf-8')).hexdigest()
```

### Contrato Inteligente

#### Estrutura no Contrato

```solidity
struct Denuncia {
    string hashDados;      // Hash SHA-256 dos dados
    uint256 timestamp;     // Timestamp do registro
    string categoria;      // Categoria da denúncia
    address submitter;     // Endereço que submeteu
}

mapping(uint256 => Denuncia) public denuncias;
uint256 public totalDenuncias;
```

#### Funções Principais

```solidity
function registrarDenuncia(
    string memory _hashDados,
    string memory _categoria
) public returns (uint256) {
    require(bytes(_hashDados).length == 64, "Hash inválido");
    require(bytes(_categoria).length > 0, "Categoria obrigatória");
    
    uint256 denunciaId = totalDenuncias;
    
    denuncias[denunciaId] = Denuncia({
        hashDados: _hashDados,
        timestamp: block.timestamp,
        categoria: _categoria,
        submitter: msg.sender
    });
    
    totalDenuncias++;
    
    emit DenunciaRegistrada(denunciaId, _hashDados, _categoria);
    
    return denunciaId;
}
```

## 🔄 Fluxo Detalhado de Registro

### 1. Preparação dos Dados

```python
# app/services/denuncia_service.py
def create_denuncia(self, denuncia: DenunciaSchema) -> Dict[str, Any]:
    # Converte modelo para dict
    denuncia_dict = denuncia.dict()
    
    # Gera hash determinístico
    hash_dados = self.blockchain_service.generate_hash(denuncia_dict)
```

### 2. Registro na Blockchain

```python
# app/services/blockchain_service.py
def register_denuncia(self, hash_dados: str, categoria: str) -> str:
    try:
        # Constrói transação
        transaction = self.contract.functions.registrarDenuncia(
            hash_dados,
            categoria
        ).build_transaction({
            'from': self.public_address,
            'gas': 200000,
            'gasPrice': Web3.to_wei('20', 'gwei'),
            'nonce': self.w3.eth.get_transaction_count(self.public_address)
        })
        
        # Assina transação
        signed_txn = self.w3.eth.account.sign_transaction(
            transaction, private_key=self.private_key
        )
        
        # Envia para blockchain
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        # Aguarda confirmação
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return receipt.transactionHash.hex()
        
    except Exception as e:
        raise BlockchainError(f"Falha no registro: {str(e)}")
```

### 3. Armazenamento Local

```python
# Salva dados completos localmente
db_denuncia = self.repository.create_from_schema(denuncia, hash_dados)

# Análise de severidade
severity_service = SeverityAnalysisService(self.repository.db)
analysis = severity_service.analyze_severity(db_denuncia)
db_denuncia.severidade = analysis['severidade']

# Commit no banco
self.repository.db.commit()
```

## 🔐 Segurança e Integridade

### Verificação de Integridade

```python
def verify_integrity(self, denuncia_id: int) -> bool:
    """Verifica se dados locais correspondem ao hash na blockchain"""
    
    # Busca dados locais
    local_denuncia = self.repository.get_by_id(denuncia_id)
    if not local_denuncia:
        return False
    
    # Busca hash na blockchain
    blockchain_hash, _, _ = self.blockchain_service.get_denuncia(denuncia_id)
    
    # Recalcula hash dos dados locais
    calculated_hash = self.blockchain_service.generate_hash({
        "descricao": local_denuncia.descricao,
        "categoria": local_denuncia.categoria,
        "latitude": local_denuncia.latitude,
        "longitude": local_denuncia.longitude
    })
    
    # Compara hashes
    return calculated_hash == blockchain_hash
```

### Detecção de Adulteração

- **Hash mismatch**: Dados foram alterados localmente
- **Missing blockchain entry**: Denúncia não existe na blockchain
- **Invalid transaction**: Transação foi revertida

## 📡 APIs e Endpoints

### Registro de Denúncia

```http
POST /api/denuncia
Content-Type: application/json

{
    "descricao": "Descrição da ocorrência",
    "categoria": "CORRUPCAO",
    "latitude": -23.5505,
    "longitude": -46.6333,
    "datetime": "2024-01-15T10:30:00Z",
    "user_uuid": "optional-anonymous-uuid"
}
```

**Resposta de Sucesso:**

```json
{
    "status": "sucesso",
    "tx_hash": "0x1234567890abcdef...",
    "hash_dados": "a1b2c3d4e5f6...",
    "ipfs_cid": "QmXxXxXx..." // se IPFS habilitado
}
```

### Listagem de Denúncias

```http
GET /api/denuncias?status=PENDING&categoria=CORRUPCAO&severidade=ALTA
```

### Verificação de Integridade

```http
GET /api/denuncias/{id}/verify
```

## ⚙️ Configuração

### Variáveis de Ambiente

```bash
# Blockchain
POLYGON_RPC=https://polygon-rpc.com
PRIVATE_KEY=0x1234567890abcdef...
PUBLIC_ADDRESS=0xYourPublicAddress
CONTRACT_ADDRESS=0xYourContractAddress

# Segurança
SECRET_KEY=your-secret-key

# Optional: IPFS para dados adicionais
IPFS_ENABLED=false
IPFS_URL=/ip4/127.0.0.1/tcp/5001
```

### Deploy do Contrato

```bash
# Usando Hardhat
npx hardhat run scripts/deploy.js --network polygon

# Ou usando Remix IDE
# 1. Compile o contrato
# 2. Deploy na rede Polygon
# 3. Copie o endereço do contrato para .env
```

## 🚀 Monitoramento e Logs

### Métricas Importantes

- **Taxa de sucesso de transações**
- **Tempo médio de confirmação**
- **Gas utilizado por transação**
- **Denúncias registradas por dia/hora**
- **Falhas de conexão com RPC**

### Logs Estruturados

```python
# Logs de transação
logger.info(f"Denuncia registered - TX: {tx_hash}, Hash: {hash_dados}")

# Logs de erro
logger.error(f"Blockchain registration failed: {error_message}")

# Logs de performance
logger.info(f"Transaction confirmed in {confirmation_time}s")
```

## 🔍 Troubleshooting

### Problemas Comuns

#### 1. Falha na Conexão RPC

```
Erro: HTTPConnectionPool(...): Max retries exceeded
```

**Solução:**

- Verificar URL do RPC no `.env`
- Testar conectividade com o endpoint
- Usar RPC alternativo se necessário

#### 2. Gas Insuficiente

```
Erro: intrinsic gas too low
```

**Solução:**

- Aumentar gas limit na transação
- Verificar gas price atual da rede
- Ajustar parâmetros no `blockchain_service.py`

#### 3. Nonce Incorreto

```
Erro: nonce too low/high
```

**Solução:**

- Verificar nonce atual da conta
- Aguardar confirmação de transações pendentes
- Reset do nonce se necessário

#### 4. Chave Privada Inválida

```
Erro: could not decode private key
```

**Solução:**

- Verificar formato da chave (deve começar com 0x)
- Confirmar que a chave corresponde ao endereço público
- Regenerar keypair se necessário

### Comandos de Debug

#### Verificar Status da Blockchain

```python
from app.services.blockchain_service import BlockchainService

service = BlockchainService()
print(f"Connected: {service.w3.is_connected()}")
print(f"Latest block: {service.w3.eth.block_number}")
print(f"Account balance: {service.w3.eth.get_balance(service.public_address)}")
```

#### Testar Contrato

```python
# Verificar se contrato está acessível
total = service.get_total_denuncias()
print(f"Total denúncias no contrato: {total}")

# Buscar denúncia específica
hash_dados, timestamp, categoria = service.get_denuncia(0)
print(f"Primeira denúncia: {hash_dados}")
```

## 📈 Performance e Escalabilidade

### Otimizações Implementadas

1. **Connection Pooling**: Reutilização de conexões RPC
2. **Batch Transactions**: Agrupamento de múltiplas operações
3. **Gas Optimization**: Contratos otimizados para menor custo
4. **Async Processing**: Operações não-bloqueantes

### Métricas de Performance

- **Throughput**: ~10-50 denúncias/minuto (limitado pelo gas)
- **Latência**: 2-15 segundos (dependente da rede)
- **Custo por transação**: ~0.001-0.01 MATIC

### Considerações de Escala

- **Para alto volume**: Considerar Layer 2 solutions
- **Para dados grandes**: Usar IPFS + hash na blockchain
- **Para private data**: Implementar zero-knowledge proofs

## 📚 Referências

- [Polygon Documentation](https://docs.polygon.technology/)
- [Web3.py Documentation](https://web3py.readthedocs.io/)
- [Solidity Documentation](https://docs.soliditylang.org/)
- [IPFS Documentation](https://docs.ipfs.io/)

## 🔗 Links Relacionados

- [docs/SEVERITY_ANALYSIS.md](SEVERITY_ANALYSIS.md) - Sistema de análise de severidade
- [contracts/](../contracts/) - Contratos inteligentes
- [app/services/blockchain_service.py](../app/services/blockchain_service.py) - Implementação do serviço
