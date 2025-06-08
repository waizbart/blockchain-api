from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.denuncia import Denuncia
from app.repositories.denuncia import DenunciaRepository
from app.factories.llm_factory import LLMFactory, EnvironmentLLMFactory
from app.prompts.severity_analysis_prompts import format_severity_prompt


class SeverityAnalysisService:
    """
    Serviço para análise automática de severidade das denúncias usando LLM.
    """

    def __init__(self, db: Session, llm_provider: str = "auto"):
        self.db = db
        self.repository = DenunciaRepository(db)

        try:
            if llm_provider == "auto":
                self.llm_adapter = EnvironmentLLMFactory.create_for_environment(
                    "development")
            else:
                self.llm_adapter = LLMFactory.create_llm_adapter(llm_provider)

            if not self.llm_adapter.is_available():
                raise RuntimeError("LLM não está disponível")

        except Exception as e:
            raise RuntimeError(
                f"Erro ao configurar LLM '{llm_provider}': {str(e)}. Análise de severidade requer LLM.")

    def analyze_severity(self, denuncia: Denuncia) -> Dict[str, Any]:
        """
        Analisa a severidade de uma denúncia usando LLM.

        Args:
            denuncia: Objeto Denuncia para análise

        Returns:
            Dictionary com análise completa de severidade
        """
        if not self.llm_adapter.is_available():
            raise RuntimeError("LLM não disponível para análise de severidade")

        context = {
            "descricao": denuncia.descricao,
            "categoria": denuncia.categoria,
            "datetime": denuncia.datetime,
            "latitude": denuncia.latitude,
            "longitude": denuncia.longitude
        }

        historico_usuario = "Não disponível"
        if denuncia.user_uuid:
            user_denuncias = self.repository.get_by_user_uuid(
                denuncia.user_uuid)
            if user_denuncias:
                verified_count = sum(
                    1 for d in user_denuncias if d.status.value == 'VERIFIED')
                rejected_count = sum(
                    1 for d in user_denuncias if d.status.value == 'REJECTED')
                total_count = len(user_denuncias)

                historico_usuario = f"Usuário com {total_count} denúncias: {verified_count} verificadas, {rejected_count} rejeitadas"

        prompt = format_severity_prompt(
            descricao=denuncia.descricao,
            categoria=denuncia.categoria,
            datetime=denuncia.datetime or "Não informado",
            latitude=denuncia.latitude,
            longitude=denuncia.longitude,
            historico_usuario=historico_usuario
        )

        llm_result = self.llm_adapter.analyze_severity(prompt, context)
        return llm_result

    def update_denuncia_severity(self, denuncia_id: int) -> Optional[Dict[str, Any]]:
        """
        Atualiza a severidade de uma denúncia específica.
        """
        denuncia = self.repository.get_by_id(denuncia_id)
        if not denuncia:
            return None

        analysis = self.analyze_severity(denuncia)

        denuncia.severidade = analysis['severidade']
        self.db.commit()
        self.db.refresh(denuncia)

        return {
            'denuncia_id': denuncia_id,
            'severidade_anterior': None,
            'nova_severidade': analysis['severidade'].value,
            'analise': analysis
        }

    def bulk_analyze_denuncias(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Analisa severidade de todas as denúncias sem severidade definida.
        """
        query = self.db.query(Denuncia).filter(Denuncia.severidade.is_(None))
        if limit:
            query = query.limit(limit)

        denuncias_sem_severidade = query.all()

        if not denuncias_sem_severidade:
            return {
                'message': 'Nenhuma denúncia sem análise de severidade encontrada',
                'processadas': 0
            }

        resultados = []
        sucessos = 0
        erros = 0

        for denuncia in denuncias_sem_severidade:
            try:
                analysis = self.analyze_severity(denuncia)
                denuncia.severidade = analysis['severidade']

                resultados.append({
                    'id': denuncia.id,
                    'severidade': analysis['severidade'].value,
                    'pontuacao': analysis.get('pontuacao', 0),
                    'confianca': analysis.get('confianca', 0),
                    'status': 'sucesso'
                })
                sucessos += 1
            except Exception as e:
                resultados.append({
                    'id': denuncia.id,
                    'erro': str(e),
                    'status': 'erro'
                })
                erros += 1

        if sucessos > 0:
            self.db.commit()

        return {
            'message': f'Análise de severidade concluída: {sucessos} sucessos, {erros} erros',
            'total_processadas': len(denuncias_sem_severidade),
            'sucessos': sucessos,
            'erros': erros,
            'resultados': resultados
        }

    def get_severity_statistics(self) -> Dict[str, Any]:
        """
        Obtém estatísticas sobre a distribuição de severidade das denúncias.
        """
        all_denuncias = self.db.query(Denuncia).all()

        if not all_denuncias:
            return {
                "message": "Nenhuma denúncia encontrada",
                "total_denuncias": 0,
                "distribuicao_severidade": {}
            }

        severity_counts = {
            "CRITICA": 0,
            "ALTA": 0,
            "MEDIA": 0,
            "BAIXA": 0,
            "NAO_ANALISADA": 0
        }

        for denuncia in all_denuncias:
            if denuncia.severidade:
                severity_counts[denuncia.severidade.value] += 1
            else:
                severity_counts["NAO_ANALISADA"] += 1

        total_com_severidade = sum(
            v for k, v in severity_counts.items() if k != "NAO_ANALISADA")
        total_denuncias = len(all_denuncias)

        percentuais = {}
        for severidade, count in severity_counts.items():
            if total_denuncias > 0:
                percentuais[severidade] = round(
                    (count / total_denuncias) * 100, 2)
            else:
                percentuais[severidade] = 0.0

        return {
            "total_denuncias": total_denuncias,
            "total_com_severidade": total_com_severidade,
            "total_sem_severidade": severity_counts["NAO_ANALISADA"],
            "distribuicao_severidade": {
                "contagem": severity_counts,
                "percentuais": percentuais
            },
            "prioridade_critica": severity_counts["CRITICA"],
            "requer_atencao_urgente": severity_counts["CRITICA"] + severity_counts["ALTA"],
            "taxa_cobertura_analise": round((total_com_severidade / total_denuncias) * 100, 2) if total_denuncias > 0 else 0.0
        }

    def get_llm_info(self) -> Dict[str, Any]:
        """
        Retorna informações sobre o LLM configurado.
        """
        return {
            "provider": self.llm_adapter.get_provider_name(),
            "available": self.llm_adapter.is_available(),
            "estimated_cost_per_analysis": self.llm_adapter.estimate_cost("Sample prompt for estimation")
        }
