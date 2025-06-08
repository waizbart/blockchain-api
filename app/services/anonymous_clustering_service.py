import hashlib
import hmac
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.denuncia import Denuncia, StatusDenuncia
from app.schemas.denuncia import PseudonymAnalysis, SystemMetrics
from app.core.config import settings
from collections import Counter
from datetime import datetime, timezone


class AnonymousClusteringService:
    """
    Serviço para clusterização anônima de denúncias usando pseudônimos irreversíveis.

    Características:
    - Gera pseudônimos determinísticos baseados no user_id
    - Usa salt secreto para garantir irreversibilidade
    - Permite análise de padrões sem comprometer anonimato
    - NUNCA armazena ou expõe dados pessoais
    """

    def __init__(self, db: Session):
        self.db = db
        self.secret_salt = getattr(
            settings, 'ANONYMOUS_CLUSTERING_SALT', 'default_clustering_salt_2024')

    def generate_anonymous_pseudonym(self, user_id: int) -> str:
        """
        Gera um pseudônimo anônimo e irreversível baseado no user_id.

        Args:
            user_id: ID do usuário autenticado

        Returns:
            Pseudônimo SHA256 que não pode ser usado para identificar o usuário
        """
        message = f"user_{user_id}_anonymous_cluster"
        pseudonimo = hmac.new(
            self.secret_salt.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        return pseudonimo[:16]

    def calculate_pseudonym_credibility_score(self, pseudonimo: str) -> float:
        """
        Calcula score de credibilidade de um pseudônimo (0.0 a 1.0).

        Fatores considerados:
        - Taxa de denúncias verificadas vs rejeitadas (50%)
        - Consistência temporal (tem atividade ao longo do tempo) (20%)
        - Consistência geográfica (denuncia em regiões consistentes) (15%)
        - Volume adequado de denúncias (não muito pouco nem excessivo) (15%)
        """
        analysis = self.get_pseudonym_analysis(pseudonimo)
        if not analysis:
            return 0.5

        factors = {
            'taxa_veracidade': analysis.taxa_veracidade * 0.5,
            'consistencia_temporal': self._calculate_temporal_consistency(analysis) * 0.2,
            'consistencia_geografica': self._calculate_geographic_consistency(analysis) * 0.15,
            'volume_adequado': self._calculate_volume_factor(analysis) * 0.15
        }

        credibility_score = sum(factors.values())
        return min(max(credibility_score, 0.0), 1.0)

    def get_pseudonym_analysis(self, pseudonimo: str) -> Optional[PseudonymAnalysis]:
        """
        Analisa as denúncias de um pseudônimo específico.
        """
        denuncias = self.db.query(Denuncia).filter(
            Denuncia.pseudonimo_cluster == pseudonimo
        ).all()

        if not denuncias:
            return None

        total_denuncias = len(denuncias)
        denuncias_verificadas = sum(
            1 for d in denuncias if d.status == StatusDenuncia.VERIFIED)
        denuncias_rejeitadas = sum(
            1 for d in denuncias if d.status == StatusDenuncia.REJECTED)
        denuncias_pendentes = sum(
            1 for d in denuncias if d.status == StatusDenuncia.PENDING)

        denuncias_finalizadas = denuncias_verificadas + denuncias_rejeitadas
        taxa_veracidade = (denuncias_verificadas /
                           denuncias_finalizadas) if denuncias_finalizadas > 0 else 0.0

        categorias = [d.categoria for d in denuncias]
        categorias_frequentes = [cat for cat,
                                 _ in Counter(categorias).most_common(5)]

        regioes_frequentes = self._get_frequent_regions(denuncias)

        datas = [d.datetime for d in denuncias if d.datetime]
        primeiro_relato = min(datas) if datas else None
        ultimo_relato = max(datas) if datas else None

        dias_atividade = 0
        if primeiro_relato and ultimo_relato and primeiro_relato != ultimo_relato:
            try:
                primeiro_dt = datetime.fromisoformat(
                    primeiro_relato.replace('Z', '+00:00'))
                ultimo_dt = datetime.fromisoformat(
                    ultimo_relato.replace('Z', '+00:00'))
                dias_atividade = (ultimo_dt - primeiro_dt).days
            except:
                dias_atividade = 0

        credibilidade_score = self.calculate_pseudonym_credibility_score(
            pseudonimo)

        return PseudonymAnalysis(
            pseudonimo=pseudonimo,
            total_denuncias=total_denuncias,
            denuncias_verificadas=denuncias_verificadas,
            denuncias_rejeitadas=denuncias_rejeitadas,
            denuncias_pendentes=denuncias_pendentes,
            taxa_veracidade=taxa_veracidade,
            credibilidade_score=credibilidade_score,
            categorias_frequentes=categorias_frequentes,
            regioes_frequentes=regioes_frequentes,
            primeiro_relato=primeiro_relato,
            ultimo_relato=ultimo_relato,
            dias_atividade=dias_atividade
        )

    def get_low_credibility_pseudonyms(self, threshold: float = 0.3, min_reports: int = 3) -> List[PseudonymAnalysis]:
        """
        Retorna pseudônimos com baixa credibilidade.
        Útil para identificar padrões suspeitos sem comprometer anonimato.
        """
        pseudonyms_with_reports = self.db.query(Denuncia.pseudonimo_cluster).filter(
            Denuncia.pseudonimo_cluster.isnot(None),
            Denuncia.status.in_(
                [StatusDenuncia.VERIFIED, StatusDenuncia.REJECTED])
        ).group_by(Denuncia.pseudonimo_cluster).having(
            func.count(Denuncia.id) >= min_reports
        ).all()

        low_credibility = []
        for (pseudonimo,) in pseudonyms_with_reports:
            analysis = self.get_pseudonym_analysis(pseudonimo)
            if analysis and analysis.credibilidade_score <= threshold:
                low_credibility.append(analysis)

        return sorted(low_credibility, key=lambda x: x.credibilidade_score)

    def get_high_credibility_pseudonyms(self, threshold: float = 0.7, min_reports: int = 3) -> List[PseudonymAnalysis]:
        """
        Retorna pseudônimos com alta credibilidade.
        Identifica padrões de reportadores confiáveis.
        """
        pseudonyms_with_reports = self.db.query(Denuncia.pseudonimo_cluster).filter(
            Denuncia.pseudonimo_cluster.isnot(None),
            Denuncia.status.in_(
                [StatusDenuncia.VERIFIED, StatusDenuncia.REJECTED])
        ).group_by(Denuncia.pseudonimo_cluster).having(
            func.count(Denuncia.id) >= min_reports
        ).all()

        high_credibility = []
        for (pseudonimo,) in pseudonyms_with_reports:
            analysis = self.get_pseudonym_analysis(pseudonimo)
            if analysis and analysis.credibilidade_score >= threshold:
                high_credibility.append(analysis)

        return sorted(high_credibility, key=lambda x: x.credibilidade_score, reverse=True)

    def get_system_metrics(self) -> SystemMetrics:
        """
        Retorna métricas do sistema sem comprometer anonimato.
        """
        total_pseudonimos_ativos = self.db.query(Denuncia.pseudonimo_cluster).filter(
            Denuncia.pseudonimo_cluster.isnot(None)
        ).distinct().count()

        total_denuncias = self.db.query(Denuncia).count()

        denuncias_verificadas = self.db.query(Denuncia).filter(
            Denuncia.status == StatusDenuncia.VERIFIED
        ).count()
        denuncias_finalizadas = self.db.query(Denuncia).filter(
            Denuncia.status.in_(
                [StatusDenuncia.VERIFIED, StatusDenuncia.REJECTED])
        ).count()

        taxa_verificacao_geral = (
            denuncias_verificadas / denuncias_finalizadas) if denuncias_finalizadas > 0 else 0.0

        pseudonimos_alta_credibilidade = len(
            self.get_high_credibility_pseudonyms())
        pseudonimos_baixa_credibilidade = len(
            self.get_low_credibility_pseudonyms())

        categoria_counts = self.db.query(
            Denuncia.categoria, func.count(Denuncia.id).label('count')
        ).group_by(Denuncia.categoria).order_by(desc('count')).limit(10).all()

        categorias_mais_reportadas = [
            {"categoria": cat, "total": count} for cat, count in categoria_counts
        ]

        all_pseudonyms = self.db.query(Denuncia.pseudonimo_cluster).filter(
            Denuncia.pseudonimo_cluster.isnot(None)
        ).distinct().all()

        distribuicao = {"alta": 0, "media": 0, "baixa": 0}
        for (pseudonimo,) in all_pseudonyms:
            score = self.calculate_pseudonym_credibility_score(pseudonimo)
            if score >= 0.7:
                distribuicao["alta"] += 1
            elif score >= 0.4:
                distribuicao["media"] += 1
            else:
                distribuicao["baixa"] += 1

        return SystemMetrics(
            total_pseudonimos_ativos=total_pseudonimos_ativos,
            total_denuncias=total_denuncias,
            taxa_verificacao_geral=taxa_verificacao_geral,
            pseudonimos_alta_credibilidade=pseudonimos_alta_credibilidade,
            pseudonimos_baixa_credibilidade=pseudonimos_baixa_credibilidade,
            categorias_mais_reportadas=categorias_mais_reportadas,
            distribuicao_credibilidade=distribuicao
        )

    def get_denuncias_with_credibility(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retorna denúncias com scores de credibilidade dos pseudônimos.
        Mantém anonimato completo.
        """
        denuncias = self.db.query(Denuncia).limit(limit).all()

        result = []
        for denuncia in denuncias:
            credibility_score = None
            if denuncia.pseudonimo_cluster:
                credibility_score = self.calculate_pseudonym_credibility_score(
                    denuncia.pseudonimo_cluster
                )

            result.append({
                "id": denuncia.id,
                "descricao": denuncia.descricao,
                "categoria": denuncia.categoria,
                "status": denuncia.status.value,
                "datetime": denuncia.datetime,
                "latitude": denuncia.latitude,
                "longitude": denuncia.longitude,
                "hash_dados": denuncia.hash_dados,
                "pseudonimo_cluster": denuncia.pseudonimo_cluster,
                "credibilidade_score": credibility_score
            })

        return result

    def _get_frequent_regions(self, denuncias: List[Denuncia]) -> List[Dict[str, Any]]:
        """Agrupa denúncias por região aproximada"""
        regions = []
        for denuncia in denuncias:
            if denuncia.latitude is not None and denuncia.longitude is not None:
                lat_rounded = round(denuncia.latitude, 2)
                lng_rounded = round(denuncia.longitude, 2)
                regions.append({
                    'latitude_aproximada': lat_rounded,
                    'longitude_aproximada': lng_rounded
                })

        region_counts = Counter()
        for region in regions:
            key = f"{region['latitude_aproximada']},{region['longitude_aproximada']}"
            region_counts[key] += 1

        frequent_regions = []
        for region_key, count in region_counts.most_common(5):
            lat_str, lng_str = region_key.split(',')
            frequent_regions.append({
                'latitude_aproximada': float(lat_str),
                'longitude_aproximada': float(lng_str),
                'frequencia': count
            })

        return frequent_regions

    def _calculate_temporal_consistency(self, analysis: PseudonymAnalysis) -> float:
        """Calcula consistência temporal"""
        if analysis.dias_atividade == 0:
            return 0.5

        if analysis.dias_atividade > 90:
            return 1.0
        elif analysis.dias_atividade > 30:
            return 0.8
        elif analysis.dias_atividade > 7:
            return 0.6
        else:
            return 0.3

    def _calculate_geographic_consistency(self, analysis: PseudonymAnalysis) -> float:
        """Calcula consistência geográfica"""
        if not analysis.regioes_frequentes:
            return 0.5

        total_regioes = len(analysis.regioes_frequentes)
        if total_regioes <= 2:
            return 1.0
        elif total_regioes <= 4:
            return 0.7
        else:
            return 0.4

    def _calculate_volume_factor(self, analysis: PseudonymAnalysis) -> float:
        """Calcula fator baseado no volume de denúncias"""
        total = analysis.total_denuncias

        if 3 <= total <= 15:
            return 1.0
        elif 16 <= total <= 30:
            return 0.8
        elif total > 30:
            return 0.3
        else:
            return 0.6
