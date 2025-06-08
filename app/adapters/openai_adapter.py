import json
import os
import re
from typing import Dict, Any, Optional
from app.adapters.llm_adapter import LLMAdapter
from app.models.denuncia import SeveridadeDenuncia


class OpenAIAdapter(LLMAdapter):
    """
    Adapter para integração com OpenAI GPT models.
    Implementa a interface LLMAdapter para análise de severidade.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4-turbo"):
        """
        Inicializa o adapter OpenAI.

        Args:
            api_key: Chave da API OpenAI (se não fornecida, busca em variável de ambiente)
            model: Modelo a ser usado (default: gpt-4-turbo)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        self.client = None

        if self.api_key:
            try:
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "Biblioteca 'openai' não encontrada. Instale com: pip install openai")

    def analyze_severity(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisa severidade usando OpenAI GPT.

        Args:
            prompt: Prompt formatado para análise
            context: Contexto adicional da denúncia

        Returns:
            Dictionary com resultado da análise
        """
        if not self.is_available():
            raise Exception(
                "OpenAI adapter não disponível - verifique API key")

        try:
            messages = [
                {
                    "role": "system",
                    "content": "Você é um especialista em análise de severidade de denúncias. SEMPRE responda APENAS em formato JSON válido, sem texto adicional antes ou depois do JSON. Sua resposta deve ser um objeto JSON completo."
                },
                {
                    "role": "user",
                    "content": prompt + "\n\nResposta deve ser SOMENTE JSON válido, sem explicações adicionais."
                }
            ]

            params = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.3,
                "max_tokens": 1000
            }

            if self.model in ["gpt-4-turbo", "gpt-3.5-turbo"]:
                params["response_format"] = {"type": "json_object"}

            response = self.client.chat.completions.create(**params)
            content = response.choices[0].message.content.strip()

            if not content.startswith('{'):
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    content = json_match.group()

            result = json.loads(content)
            validated_result = self._validate_and_normalize_response(
                result, context)

            print(f"🔍 VALIDAÇÃO: Iniciando validação da resposta")
            print(f"📋 Resposta recebida: {validated_result}")

            validated_result.update({
                "provider": "openai",
                "model": self.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "method": "llm"
            })

            return validated_result

        except json.JSONDecodeError as e:
            return self._create_fallback_response(f"Erro ao parsear JSON da resposta: {str(e)}", context)
        except Exception as e:
            return self._create_fallback_response(f"Erro na análise OpenAI: {str(e)}", context)

    def is_available(self) -> bool:
        """
        Verifica se o serviço OpenAI está disponível.
        """
        if not self.api_key or not self.client:
            return False

        try:
            self.client.models.list()
            return True
        except:
            return False

    def get_provider_name(self) -> str:
        """
        Retorna o nome do provedor.
        """
        return f"OpenAI ({self.model})"

    def estimate_cost(self, prompt: str) -> Optional[float]:
        """
        Estima o custo da análise baseado no modelo e tamanho do prompt.

        Args:
            prompt: Prompt para estimar custo

        Returns:
            Custo estimado em USD
        """
        pricing = {
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002}
        }

        if self.model not in pricing:
            return None

        prompt_tokens = len(prompt) / 4
        estimated_completion_tokens = 200

        input_cost = (prompt_tokens / 1000) * pricing[self.model]["input"]
        output_cost = (estimated_completion_tokens / 1000) * \
            pricing[self.model]["output"]

        return round(input_cost + output_cost, 6)

    def _validate_and_normalize_response(self, response: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida e normaliza a resposta do LLM.

        Args:
            response: Resposta bruta do LLM
            context: Contexto da denúncia

        Returns:
            Resposta validada e normalizada
        """
        required_fields = ["severidade", "justificativa"]

        for field in required_fields:
            if field not in response:
                raise ValueError(
                    f"Campo obrigatório '{field}' não encontrado na resposta")

        severidade_str = str(response["severidade"]).upper()
        valid_severities = ["CRITICA", "ALTA", "MEDIA", "BAIXA"]

        if severidade_str not in valid_severities:
            severity_mapping = {
                "CRÍTICA": "CRITICA",
                "CRITICAL": "CRITICA",
                "HIGH": "ALTA",
                "MEDIUM": "MEDIA",
                "LOW": "BAIXA",
                "MODERADA": "MEDIA"
            }
            severidade_str = severity_mapping.get(severidade_str, "MEDIA")

        try:
            severidade_enum = SeveridadeDenuncia(severidade_str)
        except ValueError:
            severidade_enum = SeveridadeDenuncia.MEDIA

        pontuacao = float(response.get("pontuacao", 5.0))
        pontuacao = max(0.0, min(10.0, pontuacao))

        confianca = float(response.get("confianca", 0.7))
        confianca = max(0.0, min(1.0, confianca))

        return {
            "severidade": severidade_enum,
            "pontuacao": pontuacao,
            "fatores_identificados": response.get("fatores_identificados", []),
            "palavras_chave": response.get("palavras_chave", []),
            "justificativa": response["justificativa"],
            "urgencia": response.get("urgencia", "MEDIA"),
            "recomendacoes": response.get("recomendacoes", []),
            "confianca": confianca,
            "llm_analysis": True
        }

    def _create_fallback_response(self, error_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria uma resposta de fallback em caso de erro.

        Args:
            error_message: Mensagem de erro
            context: Contexto da denúncia

        Returns:
            Resposta de fallback
        """
        return {
            "severidade": SeveridadeDenuncia.MEDIA,
            "pontuacao": 5.0,
            "fatores_identificados": ["Análise de fallback devido a erro no LLM"],
            "palavras_chave": [],
            "justificativa": f"Análise automática falhou: {error_message}. Classificação padrão aplicada.",
            "urgencia": "MEDIA",
            "recomendacoes": ["Revisar manualmente devido a falha na análise automática"],
            "confianca": 0.3,
            "llm_analysis": False,
            "error": error_message,
            "provider": "openai",
            "method": "fallback"
        }
