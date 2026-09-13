import asyncio
from datetime import datetime, timezone

from app.workers.celery_app import celery_app
from app.workers.ingestion_jobs import NER_SAMPLE_POINTS


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def update_risk(self):
    from app.schemas.common import Location
    from app.services.risk.engine import RiskEngine

    started = datetime.now(timezone.utc)
    try:
        engine = RiskEngine()

        async def _run():
            out = []
            for lat, lon, name in NER_SAMPLE_POINTS:
                out.append(await engine.assess(Location(latitude=lat, longitude=lon, name=name)))
            return out

        results = asyncio.run(_run())
        return {
            "job_name": "update_risk", "started_at": started, "completed_at": datetime.now(timezone.utc),
            "status": "success", "records_processed": len(results),
        }
    except Exception as exc:  # noqa: BLE001
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def update_impact(self):
    # Depends on update_risk + infrastructure being fresh; recomputes impact
    # for the sample points as a placeholder for the full PostGIS join.
    from app.schemas.common import Location
    from app.services.impact.service import ImpactService
    from app.services.infrastructure.service import InfrastructureService
    from app.services.risk.engine import RiskEngine

    started = datetime.now(timezone.utc)
    try:
        risk_engine = RiskEngine()
        infra_service = InfrastructureService()
        impact_service = ImpactService()

        async def _run():
            out = []
            for lat, lon, name in NER_SAMPLE_POINTS:
                loc = Location(latitude=lat, longitude=lon, name=name)
                assessment = await risk_engine.assess(loc)
                infra = await infra_service.get_infrastructure(loc)
                out.append(impact_service.assess_impact(loc, assessment.category, infra.assets))
            return out

        results = asyncio.run(_run())
        return {"job_name": "update_impact", "started_at": started, "completed_at": datetime.now(timezone.utc),
                "status": "success", "records_processed": len(results)}
    except Exception as exc:  # noqa: BLE001
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def generate_alerts(self):
    from app.schemas.common import Location
    from app.services.alerts.service import AlertService
    from app.services.decision.service import DecisionService
    from app.services.impact.service import ImpactService
    from app.services.infrastructure.service import InfrastructureService
    from app.services.risk.engine import RiskEngine

    started = datetime.now(timezone.utc)
    try:
        risk_engine = RiskEngine()
        infra_service = InfrastructureService()
        impact_service = ImpactService()
        decision_service = DecisionService()
        alert_service = AlertService()

        async def _run():
            alerts = []
            for lat, lon, name in NER_SAMPLE_POINTS:
                loc = Location(latitude=lat, longitude=lon, name=name)
                assessment = await risk_engine.assess(loc)
                infra = await infra_service.get_infrastructure(loc)
                impact = impact_service.assess_impact(loc, assessment.category, infra.assets)
                decision = decision_service.recommend(assessment.category, assessment.uncertainty, impact.estimated_population_exposure)
                alert = alert_service.evaluate(
                    loc, assessment.category, assessment.drivers,
                    [a.name or a.id for a in impact.ranked_assets], decision.actions,
                )
                if alert:
                    alerts.append(alert)
            return alerts

        alerts = asyncio.run(_run())
        return {"job_name": "generate_alerts", "started_at": started, "completed_at": datetime.now(timezone.utc),
                "status": "success", "records_processed": len(alerts)}
    except Exception as exc:  # noqa: BLE001
        raise self.retry(exc=exc)

