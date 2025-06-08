from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class LLMAdapter(ABC):
    """
    Interface abstrata para adapters de Large Language Models.
    Implementa o padrão Adapter para diferentes provedores de LLM.
    """

    @abstractmethod
    def analyze_severity(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisa a severidade de uma denúncia usando o LLM.

        Args:
            prompt: Prompt formatado para análise
            context: Contexto adicional da denúncia

        Returns:
            Dictionary com resultado da análise
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Verifica se o serviço LLM está disponível.

        Returns:
            True se disponível, False caso contrário
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Retorna o nome do provedor LLM.

        Returns:
            Nome do provedor
        """
        pass

    @abstractmethod
    def estimate_cost(self, prompt: str) -> Optional[float]:
        """
        Estima o custo da análise (se aplicável).

        Args:
            prompt: Prompt para estimar custo

        Returns:
            Custo estimado ou None se não aplicável
        """
        pass
