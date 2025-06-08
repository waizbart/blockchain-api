from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.repositories.denuncia import DenunciaRepository
from app.models.denuncia import StatusDenuncia


class AnalysisService:
    """
    Service for analyzing user reliability based on their denuncias.
    """

    def __init__(self, db: Session):
        """
        Initialize the analysis service.

        Args:
            db: Database session.
        """
        self.repository = DenunciaRepository(db)

    def get_user_reliability(self, user_uuid: str) -> Dict[str, Any]:
        """
        Calculate user reliability based on their denuncias status history.

        Args:
            user_uuid: The UUID of the user to analyze.

        Returns:
            Dictionary containing reliability metrics and statistics.
        """
        user_denuncias = self.repository.get_by_user_uuid(user_uuid)

        if not user_denuncias:
            return {
                "user_uuid": user_uuid,
                "total_denuncias": 0,
                "reliability_score": 0.0,
                "reliability_percentage": "0.00%",
                "status_breakdown": {},
                "message": "Usuário não possui denúncias registradas"
            }

        status_counts = {
            "PENDING": 0,
            "VERIFIED": 0,
            "REJECTED": 0
        }

        for denuncia in user_denuncias:
            status_counts[denuncia.status.value] += 1

        total_denuncias = len(user_denuncias)

        # Calculate reliability score
        # Verified denuncias add positive points
        # Rejected denuncias subtract points
        # Pending denuncias are neutral but show activity
        verified_count = status_counts["VERIFIED"]
        rejected_count = status_counts["REJECTED"]
        pending_count = status_counts["PENDING"]

        # Reliability calculation:
        # - Each verified denuncia adds 1 point
        # - Each rejected denuncia subtracts 0.5 points
        # - Pending denuncias don't affect the score but are counted
        reliability_score = verified_count - (rejected_count * 0.5)

        # Calculate reliability percentage (max score = total verified)
        # If user has only rejected denuncias, reliability can be negative
        if total_denuncias > 0:
            max_possible_score = verified_count + rejected_count  # Only processed denuncias
            if max_possible_score > 0:
                reliability_percentage = max(
                    0, (reliability_score / max_possible_score) * 100)
            else:
                reliability_percentage = 0.0  # Only pending denuncias
        else:
            reliability_percentage = 0.0

        # Determine reliability level
        reliability_level = self._get_reliability_level(reliability_percentage)

        return {
            "user_uuid": user_uuid,
            "total_denuncias": total_denuncias,
            "reliability_score": round(reliability_score, 2),
            "reliability_percentage": f"{reliability_percentage:.2f}%",
            "reliability_level": reliability_level,
            "status_breakdown": {
                "verified": status_counts["VERIFIED"],
                "rejected": status_counts["REJECTED"],
                "pending": status_counts["PENDING"]
            },
            "processed_denuncias": verified_count + rejected_count,
            "analysis": {
                "verification_rate": f"{(verified_count / max(1, verified_count + rejected_count) * 100):.2f}%" if (verified_count + rejected_count) > 0 else "N/A",
                "rejection_rate": f"{(rejected_count / max(1, verified_count + rejected_count) * 100):.2f}%" if (verified_count + rejected_count) > 0 else "N/A"
            }
        }

    def _get_reliability_level(self, percentage: float) -> str:
        """
        Determine reliability level based on percentage.

        Args:
            percentage: Reliability percentage.

        Returns:
            String describing the reliability level.
        """
        if percentage >= 80:
            return "MUITO_CONFIAVEL"
        elif percentage >= 60:
            return "CONFIAVEL"
        elif percentage >= 40:
            return "MODERADA"
        elif percentage >= 20:
            return "BAIXA"
        else:
            return "MUITO_BAIXA"

    def get_users_reliability_ranking(self, limit: Optional[int] = 10) -> Dict[str, Any]:
        """
        Get a ranking of users by their reliability scores.

        Args:
            limit: Maximum number of users to return.

        Returns:
            Dictionary containing the ranking and statistics.
        """
        all_users = self.repository.get_all_users_with_denuncias()

        if not all_users:
            return {
                "message": "Nenhum usuário com denúncias encontrado",
                "ranking": [],
                "total_users": 0
            }

        user_reliabilities = []
        for user_uuid in all_users:
            reliability_data = self.get_user_reliability(user_uuid)
            if reliability_data["total_denuncias"] > 0:
                user_reliabilities.append({
                    "user_uuid": user_uuid,
                    "reliability_score": reliability_data["reliability_score"],
                    "reliability_percentage": reliability_data["reliability_percentage"],
                    "reliability_level": reliability_data["reliability_level"],
                    "total_denuncias": reliability_data["total_denuncias"],
                    "verified": reliability_data["status_breakdown"]["verified"],
                    "rejected": reliability_data["status_breakdown"]["rejected"]
                })

        user_reliabilities.sort(
            key=lambda x: x["reliability_score"], reverse=True)

        if limit:
            user_reliabilities = user_reliabilities[:limit]

        return {
            "ranking": user_reliabilities,
            "total_users": len(user_reliabilities),
            "generated_at": "now"
        }
