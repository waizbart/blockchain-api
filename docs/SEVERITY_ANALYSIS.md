# Sistema de Análise de Severidade de Denúncias

## 📋 Visão Geral

O sistema de análise de severidade classifica automaticamente as denúncias em quatro níveis:

- **CRITICA**: Situações que envolvem risco iminente à vida, crimes graves, emergências
- **ALTA**: Crimes significativos, violações sérias de direitos, situações de risco  
- **MEDIA**: Infrações moderadas, problemas administrativos sérios, irregularidades
- **BAIXA**: Questões administrativas menores, reclamações de serviços, problemas rotineiros

## 🤖 Método de Análise

### Análise com LLM (Large Language Model)

- **Modelo Padrão**: GPT-4 da OpenAI
- **Mock para Desenvolvimento**: Adapter mock para testes
- **Vantagens**: Compreensão contextual avançada, análise semântica, flexibilidade
- **Requisitos**: API key OpenAI para produção

## 🏗️ Arquitetura

### Padrões de Design Implementados

1. **Adapter Pattern**: Interface unificada para diferentes provedores LLM
2. **Factory Pattern**: Criação centralizada de adapters LLM

### Estrutura de Arquivos

```
app/
├── adapters/
│   ├── llm_adapter.py          # Interface abstrata
│   └── openai_adapter.py       # Implementação OpenAI + Mock
├── factories/
│   └── llm_factory.py          # Factory para LLMs
├── prompts/
│   └── severity_analysis_prompts.py  # Prompts modulares
├── services/
│   └── severity_analysis_service.py  # Serviço principal
└── models/
    └── denuncia.py             # Enum SeveridadeDenuncia
```

## ⚙️ Configuração

### Variáveis de Ambiente

```bash
# Configurações LLM
OPENAI_API_KEY=sk-your-openai-key-here
LLM_PROVIDER=openai                    # ou 'mock' para desenvolvimento
LLM_MODEL=gpt-4                        # ou 'gpt-3.5-turbo'
```

### Configuração por Ambiente

- **Desenvolvimento**: Usa mock LLM por padrão
- **Produção**: Requer OpenAI configurado
- **Testes**: Sempre usa mock LLM

## 🚀 Uso da API

### Filtrar Denúncias por Severidade

```http
GET /api/denuncias?severidade=CRITICA
```

**Parâmetros:**

- `severidade`: BAIXA, MEDIA, ALTA, CRITICA

### Resposta das Denúncias

```json
{
  "id": 123,
  "descricao": "Descrição da denúncia...",
  "categoria": "VIOLENCIA",
  "severidade": "ALTA",
  "status": "PENDING",
  "datetime": "2024-01-15T10:30:00Z",
  // ... outros campos
}
```

## 🔧 Análise Automática

### Quando Ocorre

- **Criação de Nova Denúncia**: Análise automática na criação
- **Processamento em Lote**: Para denúncias sem severidade definida
- **Re-análise Manual**: Via endpoints administrativos

### Fatores Considerados

1. **Gravidade dos Fatos**: Natureza e gravidade dos fatos relatados
2. **Urgência**: Necessidade de ação imediata
3. **Impacto Social**: Potencial impacto na sociedade
4. **Risco**: Riscos à segurança, saúde ou direitos
5. **Categoria**: Peso da categoria da denúncia
6. **Credibilidade**: Histórico do usuário
7. **Contexto Temporal e Geográfico**: Análise contextual da situação

## 📊 Exemplos de Classificação

### CRITICA

- "Ameaça de bomba na escola municipal"
- "Tiroteio em andamento no centro da cidade"
- "Sequestro de criança relatado"

### ALTA

- "Agressão física contra idoso"
- "Corrupção envolvendo milhões em licitação"
- "Tráfico de drogas próximo à escola"

### MEDIA

- "Furto de celular no transporte público"
- "Fraude em benefício social"
- "Vandalismo em prédio público"

### BAIXA

- "Música alta do vizinho após 22h"
- "Buraco na calçada sem sinalização"
- "Lixo acumulado em terreno baldio"

## 🔒 Prompts e Segurança

### Modularização de Prompts

- **Arquivo Central**: `app/prompts/severity_analysis_prompts.py`
- **Prompts Específicos**: Por categoria de denúncia
- **Versionamento**: Facilita ajustes e melhorias

### Validação de Respostas

- **Sanitização**: Validação de campos obrigatórios
- **Normalização**: Mapeamento de valores similares
- **Fallback**: Valores padrão para respostas inválidas

## 🧪 Testes e Desenvolvimento

### Mock Adapter

```python
from app.factories.llm_factory import create_mock_adapter

# Usar para desenvolvimento/testes
llm = create_mock_adapter()
```

### Ambiente de Desenvolvimento

```python
from app.factories.llm_factory import EnvironmentLLMFactory

# Detecta automaticamente o melhor LLM disponível
llm = EnvironmentLLMFactory.create_for_environment("development")
```

## 💰 Custos e Performance

### Estimativa de Custos (OpenAI)

- **GPT-4**: ~$0.03-0.06 por análise
- **GPT-3.5-turbo**: ~$0.002-0.003 por análise
- **Mock**: $0.00

### Performance

- **LLM**: 2-5 segundos por análise
- **Mock**: <100ms por análise (desenvolvimento)

## 🔄 Extensibilidade

### Adicionar Novo Provedor LLM

```python
from app.adapters.llm_adapter import LLMAdapter
from app.factories.llm_factory import LLMFactory

class NovoProviderAdapter(LLMAdapter):
    # Implementar métodos abstratos
    pass

# Registrar novo provedor
LLMFactory.register_provider("novo_provider", NovoProviderAdapter)
```

### Customizar Prompts

- Editar `app/prompts/severity_analysis_prompts.py`
- Adicionar prompts específicos por categoria
- Implementar prompts multi-idioma

## 📈 Monitoramento

### Métricas Recomendadas

- Taxa de uso LLM vs Regras
- Distribuição de severidades
- Tempo de resposta por método
- Custo por análise (LLM)
- Taxa de erro/fallback

### Logs

- Decisões de classificação
- Erros de LLM e fallbacks
- Performance por método
- Uso de recursos

## 🛠️ Manutenção

### Ajuste de Prompts

- Monitorar qualidade das classificações
- Ajustar prompts baseado em feedback
- Versionar mudanças importantes

### Calibração de Regras

- Revisar palavras-chave periodicamente
- Ajustar pesos por categoria
- Sincronizar com classificações LLM

### Backup e Redundância

- Mock sempre disponível como fallback
- Regras independentes de APIs externas
- Cache de resultados (recomendado)
