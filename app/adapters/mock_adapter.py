import json
import random
from typing import Dict, Any, Optional
from app.adapters.llm_adapter import LLMAdapter
from app.models.denuncia import SeveridadeDenuncia


class MockLLMAdapter(LLMAdapter):
    """
    Adapter mock para desenvolvimento e testes.
    Simula respostas de análise de severidade sem usar APIs externas.
    """

    def __init__(self, **kwargs):
        """
        Inicializa o adapter mock.
        """
        self.available = True

    def analyze_severity(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simula análise de severidade baseada em palavras-chave e regras simples.

        Args:
            prompt: Prompt formatado (não usado no mock)
            context: Contexto da denúncia

        Returns:
            Dictionary com análise simulada de severidade
        """
        descricao = context.get("descricao", "").lower()
        categoria = context.get("categoria", "").lower()
        palavras_criticas = [
            "assassinato", "homicídio", "morte", "matar", "morrer", "sangue",
            "arma", "violência", "agressão", "espancamento", "tortura",
            "estupro", "abuso sexual", "pedofilia", "tráfico", "drogas",
            "sequestro", "roubo", "assalto", "furto qualificado"
        ]

        palavras_altas = [
            "corrupcão", "propina", "desvio", "peculato", "fraude",
            "violência doméstica", "ameaça", "intimidação", "discriminação",
            "assédio", "bullying", "vandalismo", "dano", "prejudicar"
        ]

        palavras_medias = [
            "irregularidade", "infração", "má administração", "negligência",
            "descaso", "problema", "reclamação", "falha", "erro"
        ]

        severidade = SeveridadeDenuncia.BAIXA
        fatores = []
        palavras_encontradas = []
        for palavra in palavras_criticas:
            if palavra in descricao:
                severidade = SeveridadeDenuncia.CRITICA
                fatores.append(f"Detectada palavra crítica: '{palavra}'")
                palavras_encontradas.append(palavra)

        if severidade != SeveridadeDenuncia.CRITICA:
            for palavra in palavras_altas:
                if palavra in descricao:
                    severidade = SeveridadeDenuncia.ALTA
                    fatores.append(
                        f"Detectada palavra de alta severidade: '{palavra}'")
                    palavras_encontradas.append(palavra)
                    break

        if severidade not in [SeveridadeDenuncia.CRITICA, SeveridadeDenuncia.ALTA]:
            for palavra in palavras_medias:
                if palavra in descricao:
                    severidade = SeveridadeDenuncia.MEDIA
                    fatores.append(
                        f"Detectada palavra de média severidade: '{palavra}'")
                    palavras_encontradas.append(palavra)
                    break

        if categoria in ["saúde", "educação", "segurança"] and severidade == SeveridadeDenuncia.BAIXA:
            severidade = SeveridadeDenuncia.MEDIA
            fatores.append(
                f"Categoria '{categoria}' aumentou severidade para MEDIA")

        if not fatores:
            fatores.append(
                "Análise automática por regras - classificação padrão")
        pontuacao_map = {
            SeveridadeDenuncia.BAIXA: random.uniform(1.0, 3.0),
            SeveridadeDenuncia.MEDIA: random.uniform(3.0, 6.0),
            SeveridadeDenuncia.ALTA: random.uniform(6.0, 8.5),
            SeveridadeDenuncia.CRITICA: random.uniform(8.5, 10.0)
        }

        pontuacao = round(pontuacao_map[severidade], 1)
        confianca = random.uniform(0.7, 0.9)

        justificativa_map = {
            SeveridadeDenuncia.BAIXA: "Classificada como BAIXA severidade baseada em análise de conteúdo e palavras-chave. Não foram identificados indicadores de risco significativo.",
            SeveridadeDenuncia.MEDIA: "Classificada como MEDIA severidade devido à presença de termos que indicam problemas administrativos ou infrações moderadas.",
            SeveridadeDenuncia.ALTA: "Classificada como ALTA severidade devido à identificação de termos relacionados a crimes ou violações sérias de direitos.",
            SeveridadeDenuncia.CRITICA: "Classificada como CRITICA devido à presença de termos que indicam risco iminente, crimes graves ou situações de emergência."
        }

        recomendacoes_map = {
            SeveridadeDenuncia.BAIXA: ["Encaminhar para análise administrativa", "Processar em prazo normal"],
            SeveridadeDenuncia.MEDIA: ["Priorizar análise", "Verificar documentação", "Encaminhar para setor responsável"],
            SeveridadeDenuncia.ALTA: ["Análise urgente necessária", "Notificar autoridades competentes", "Documentar evidências"],
            SeveridadeDenuncia.CRITICA: [
                "AÇÃO IMEDIATA NECESSÁRIA", "Contatar autoridades", "Protocolo de emergência", "Proteção de envolvidos"]
        }

        result = {
            "severidade": severidade,
            "pontuacao": pontuacao,
            "fatores_identificados": fatores,
            "palavras_chave": palavras_encontradas,
            "justificativa": justificativa_map[severidade],
            "urgencia": severidade.value,
            "recomendacoes": recomendacoes_map[severidade],
            "confianca": round(confianca, 2),
            "llm_analysis": False,
            "provider": "mock",
            "model": "rule-based-mock",
            "method": "rule-based"
        }

        return result

    def is_available(self) -> bool:
        """
        Mock sempre está disponível.
        """
        return True

    def get_provider_name(self) -> str:
        """
        Retorna o nome do provedor mock.
        """
        return "Mock LLM (Rule-based)"

    def estimate_cost(self, prompt: str) -> Optional[float]:
        """
        Mock não tem custo.
        """
        return 0.0
