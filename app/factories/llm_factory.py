"""
Factory para criação de adapters de Large Language Models.
Implementa o padrão Factory para facilitar extensão e configuração.
"""

from typing import Dict, Type, Optional
from app.adapters.llm_adapter import LLMAdapter
from app.adapters.openai_adapter import OpenAIAdapter
from app.adapters.mock_adapter import MockLLMAdapter


class LLMFactory:
    """
    Factory para criação de adapters de LLM.
    Facilita a adição de novos provedores e configuração centralizada.
    """

    _providers: Dict[str, Type[LLMAdapter]] = {
        "openai": OpenAIAdapter,
        "mock": MockLLMAdapter,
        # Futuros provedores podem ser adicionados aqui:
        # "anthropic": AnthropicAdapter,
        # "google": GoogleAdapter,
        # "azure": AzureOpenAIAdapter,
    }

    _default_configs: Dict[str, Dict] = {
        "openai": {
            "model": "gpt-4",
            "api_key": None
        },
        "mock": {}
    }

    @classmethod
    def create_llm_adapter(cls, provider: str, **kwargs) -> LLMAdapter:
        """
        Cria uma instância do adapter LLM especificado.

        Args:
            provider: Nome do provedor (openai, etc.)
            **kwargs: Argumentos específicos do provedor

        Returns:
            Instância do adapter LLM

        Raises:
            ValueError: Se o provedor não for encontrado
        """
        provider_lower = provider.lower()

        if provider_lower not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ValueError(
                f"Provedor '{provider}' não encontrado. Disponíveis: {available}")

        config = cls._default_configs.get(provider_lower, {}).copy()
        config.update(kwargs)

        adapter_class = cls._providers[provider_lower]
        return adapter_class(**config)

    @classmethod
    def get_available_providers(cls) -> list:
        """
        Retorna lista de provedores disponíveis.

        Returns:
            Lista de nomes de provedores
        """
        return list(cls._providers.keys())

    @classmethod
    def register_provider(cls, name: str, adapter_class: Type[LLMAdapter], default_config: Dict = None):
        """
        Registra um novo provedor LLM.

        Args:
            name: Nome do provedor
            adapter_class: Classe do adapter
            default_config: Configuração padrão (opcional)
        """
        cls._providers[name.lower()] = adapter_class
        if default_config:
            cls._default_configs[name.lower()] = default_config

    @classmethod
    def create_best_available(cls, preferred_order: Optional[list] = None) -> LLMAdapter:
        """
        Cria o melhor adapter disponível baseado na ordem de preferência.

        Args:
            preferred_order: Lista ordenada de provedores preferidos

        Returns:
            Primeiro adapter disponível da lista de preferência

        Raises:
            RuntimeError: Se nenhum adapter estiver disponível
        """
        if not preferred_order:
            preferred_order = ["openai", "mock"]

        for provider in preferred_order:
            try:
                adapter = cls.create_llm_adapter(provider)
                if adapter.is_available():
                    return adapter
            except Exception as e:
                print(f"Provedor '{provider}' não disponível: {str(e)}")
                continue

        raise RuntimeError("Nenhum provedor LLM disponível")

    @classmethod
    def get_provider_info(cls, provider: str) -> Dict:
        """
        Obtém informações sobre um provedor específico.

        Args:
            provider: Nome do provedor

        Returns:
            Dictionary com informações do provedor
        """
        provider_lower = provider.lower()

        if provider_lower not in cls._providers:
            return {"error": f"Provedor '{provider}' não encontrado"}

        try:
            adapter = cls.create_llm_adapter(provider)

            return {
                "name": provider,
                "class": cls._providers[provider_lower].__name__,
                "available": adapter.is_available(),
                "provider_name": adapter.get_provider_name(),
                "default_config": cls._default_configs.get(provider_lower, {})
            }
        except Exception as e:
            return {
                "name": provider,
                "class": cls._providers[provider_lower].__name__,
                "available": False,
                "error": str(e)
            }


def create_openai_adapter(model: str = "gpt-4", api_key: Optional[str] = None) -> LLMAdapter:
    """
    Função de conveniência para criar adapter OpenAI.

    Args:
        model: Modelo OpenAI a usar
        api_key: Chave da API (opcional)

    Returns:
        Adapter OpenAI configurado
    """
    return LLMFactory.create_llm_adapter("openai", model=model, api_key=api_key)


def create_best_llm() -> LLMAdapter:
    """
    Função de conveniência para criar o melhor LLM disponível.

    Returns:
        Melhor adapter LLM disponível
    """
    return LLMFactory.create_best_available()


def create_mock_adapter() -> LLMAdapter:
    """
    Função de conveniência para criar adapter mock.

    Returns:
        Adapter mock configurado
    """
    return LLMFactory.create_llm_adapter("mock")


class EnvironmentLLMFactory:
    """
    Factory específica para diferentes ambientes (dev, prod, test).
    """

    @staticmethod
    def create_for_environment(env: str = "development") -> LLMAdapter:
        """
        Cria adapter apropriado para o ambiente especificado.

        Args:
            env: Ambiente (development, production, testing)

        Returns:
            Adapter LLM apropriado para o ambiente
        """

        if env.lower() in ["prod", "production"]:
            try:
                adapter = create_openai_adapter()
                if not adapter.is_available():
                    raise RuntimeError("OpenAI não disponível em produção")
                return adapter
            except Exception as e:
                raise RuntimeError(
                    f"Falha ao configurar LLM para produção: {str(e)}")

        elif env.lower() in ["dev", "development", "local", "test", "testing"]:
            try:
                adapter = create_openai_adapter()
                if adapter.is_available():
                    return adapter
                else:
                    return LLMFactory.create_llm_adapter("mock")
            except Exception:
                return LLMFactory.create_llm_adapter("mock")

        else:
            raise ValueError(f"Ambiente '{env}' não reconhecido")


class UseCaseLLMFactory:
    """
    Factory para casos de uso específicos com configurações otimizadas.
    """

    @staticmethod
    def create_for_severity_analysis(high_precision: bool = False) -> LLMAdapter:
        """
        Cria LLM otimizado para análise de severidade.

        Args:
            high_precision: Se True, usa modelo mais preciso (e caro)

        Returns:
            Adapter LLM otimizado para análise de severidade
        """
        if high_precision:
            return create_openai_adapter(model="gpt-4")
        else:
            return LLMFactory.create_best_available(["openai"])
