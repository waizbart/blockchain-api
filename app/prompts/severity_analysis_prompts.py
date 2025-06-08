"""
Prompts modulares para análise de severidade de denúncias usando LLM.
Este arquivo centraliza todos os prompts para facilitar manutenção e ajustes.
"""

SEVERITY_ANALYSIS_PROMPT = """
Você é um especialista em análise de denúncias e classificação de severidade para sistema de ouvidoria pública.

Sua tarefa é analisar a denúncia fornecida e classificar sua severidade em uma das categorias:
- CRITICA: Situações que envolvem risco iminente à vida, crimes graves, emergências
- ALTA: Crimes significativos, violações sérias de direitos, situações de risco
- MEDIA: Infrações moderadas, problemas administrativos sérios, irregularidades
- BAIXA: Questões administrativas menores, reclamações de serviços, problemas rotineiros

DADOS DA DENÚNCIA:
Descrição: {descricao}
Categoria: {categoria}
Data/Hora: {datetime}
Localização: {localizacao}
Histórico do Usuário: {historico_usuario}

CRITÉRIOS DE ANÁLISE:
1. GRAVIDADE DOS FATOS: Avalie a natureza e gravidade dos fatos relatados
2. URGÊNCIA: Considere se a situação requer ação imediata
3. IMPACTO SOCIAL: Analise o potencial impacto na sociedade ou comunidade
4. RISCO: Identifique riscos à segurança, saúde ou direitos
5. CATEGORIA: Considere o peso da categoria da denúncia
6. CREDIBILIDADE: Avalie a credibilidade baseada no histórico do usuário

FORMATO DE RESPOSTA (JSON):
{{
    "severidade": "CRITICA|ALTA|MEDIA|BAIXA",
    "pontuacao": float_entre_0_e_10,
    "fatores_identificados": [
        "lista de fatores que influenciaram a classificação"
    ],
    "palavras_chave": [
        "palavras-chave relevantes encontradas"
    ],
    "justificativa": "explicação detalhada da classificação",
    "urgencia": "EMERGENCIAL|ALTA|MEDIA|BAIXA",
    "recomendacoes": [
        "lista de recomendações de ação"
    ],
    "confianca": float_entre_0_e_1
}}

Analise cuidadosamente todos os aspectos e forneça uma classificação precisa.
"""

SEVERITY_ANALYSIS_LIMITED_INFO_PROMPT = """
Você é um especialista em análise de denúncias. Analise a denúncia com informações limitadas fornecida.

DENÚNCIA:
Descrição: {descricao}
Categoria: {categoria}

Classifique a severidade em: CRITICA, ALTA, MEDIA, BAIXA

Responda APENAS no formato JSON:
{{
    "severidade": "classificação",
    "pontuacao": pontuacao_numerica,
    "justificativa": "breve explicação",
    "confianca": confianca_0_a_1
}}
"""

SEVERITY_REANALYSIS_PROMPT = """
Você está re-analisando uma denúncia onde houve incerteza na classificação inicial.

DADOS ORIGINAIS:
{dados_originais}

CLASSIFICAÇÃO ANTERIOR: {classificacao_anterior}
MOTIVO DA RE-ANÁLISE: {motivo_reanalise}

Faça uma nova análise mais aprofundada, considerando:
1. Nuances do contexto que podem ter sido perdidas
2. Comparação com casos similares
3. Precedentes de classificação

Forneça sua nova análise no formato JSON padrão.
"""

COMPARATIVE_ANALYSIS_PROMPT = """
Compare esta denúncia com casos similares para calibrar a severidade:

DENÚNCIA ATUAL:
{denuncia_atual}

CASOS DE REFERÊNCIA:
{casos_referencia}

Baseado na comparação, confirme ou ajuste a classificação de severidade.
"""

CATEGORY_SPECIFIC_PROMPTS = {
    "VIOLENCIA": """
    Esta denúncia é da categoria VIOLÊNCIA. Considere especialmente:
    - Tipo e intensidade da violência relatada
    - Presença de armas ou ameaças
    - Número de pessoas envolvidas
    - Repetição dos atos violentos
    - Vulnerabilidade das vítimas
    
    {base_prompt}
    """,

    "CORRUPCAO": """
    Esta denúncia é da categoria CORRUPÇÃO. Considere especialmente:
    - Valor monetário envolvido
    - Nível hierárquico dos envolvidos
    - Impacto no serviço público
    - Evidências apresentadas
    - Sistemática da corrupção
    
    {base_prompt}
    """,

    "TRAFICO": """
    Esta denúncia é da categoria TRÁFICO. Considere especialmente:
    - Tipo de substância/material
    - Escala da operação
    - Proximidade de escolas/hospitais
    - Envolvimento de menores
    - Violência associada
    
    {base_prompt}
    """,

    "AMBIENTAL": """
    Esta denúncia é da categoria AMBIENTAL. Considere especialmente:
    - Extensão do dano ambiental
    - Reversibilidade dos danos
    - Impacto na saúde pública
    - Espécies ou habitats afetados
    - Recorrência da infração
    
    {base_prompt}
    """
}

CONTEXT_EXTRACTION_PROMPT = """
Extraia informações contextuais relevantes desta denúncia para análise de severidade:

TEXTO: {texto}

Identifique:
1. Indicadores de urgência temporal
2. Elementos de risco
3. Potencial impacto
4. Credibilidade aparente
5. Complexidade do caso

Responda em formato JSON estruturado.
"""

CLASSIFICATION_VALIDATION_PROMPT = """
Valide se esta classificação de severidade está correta:

DENÚNCIA: {denuncia}
CLASSIFICAÇÃO: {classificacao}
JUSTIFICATIVA: {justificativa}

Confirme se concorda ou sugira ajustes com fundamentação.
"""


def get_prompt_for_category(categoria: str, base_prompt: str) -> str:
    """
    Retorna prompt específico para uma categoria ou o prompt base.

    Args:
        categoria: Categoria da denúncia
        base_prompt: Prompt base formatado

    Returns:
        Prompt específico da categoria ou prompt base
    """
    categoria_upper = categoria.upper()
    if categoria_upper in CATEGORY_SPECIFIC_PROMPTS:
        return CATEGORY_SPECIFIC_PROMPTS[categoria_upper].format(base_prompt=base_prompt)
    return base_prompt


def format_severity_prompt(
    descricao: str,
    categoria: str,
    datetime: str = "Não informado",
    latitude: float = None,
    longitude: float = None,
    historico_usuario: str = "Não disponível"
) -> str:
    """
    Formata o prompt principal de análise de severidade.

    Args:
        descricao: Descrição da denúncia
        categoria: Categoria da denúncia
        datetime: Data e hora da denúncia
        latitude: Latitude (opcional)
        longitude: Longitude (opcional)
        historico_usuario: Resumo do histórico do usuário

    Returns:
        Prompt formatado
    """
    if latitude and longitude:
        localizacao = f"Latitude: {latitude}, Longitude: {longitude}"
    else:
        localizacao = "Não informada"

    base_prompt = SEVERITY_ANALYSIS_PROMPT.format(
        descricao=descricao,
        categoria=categoria,
        datetime=datetime,
        localizacao=localizacao,
        historico_usuario=historico_usuario
    )

    return get_prompt_for_category(categoria, base_prompt)


def get_limited_info_prompt(descricao: str, categoria: str) -> str:
    """
    Retorna prompt para casos com informações limitadas.
    """
    return SEVERITY_ANALYSIS_LIMITED_INFO_PROMPT.format(
        descricao=descricao,
        categoria=categoria
    )
