from dataclasses import asdict, dataclass
from datetime import date
from typing import Protocol

from flask import Blueprint, jsonify, request


@dataclass(frozen=True)
class StopInput:
    order_id: str
    latitude: float
    longitude: float
    sequence: int


class RouteWriter(Protocol):
    def save_plan(
        self, *, tenant_id: int, service_date: date, stops: list[StopInput]
    ) -> int: ...


class ValidationError(ValueError):
    pass


def _parse_plan(payload: object) -> tuple[date, list[StopInput]]:
    if not isinstance(payload, dict):
        raise ValidationError("JSON object required")

    try:
        service_date = date.fromisoformat(str(payload["service_date"]))
        raw_stops = payload["stops"]
    except (KeyError, TypeError, ValueError) as exc:
        raise ValidationError("service_date and stops are required") from exc

    if not isinstance(raw_stops, list) or not raw_stops:
        raise ValidationError("stops must be a non-empty list")

    stops: list[StopInput] = []
    for sequence, item in enumerate(raw_stops, start=1):
        try:
            stop = StopInput(
                order_id=str(item["order_id"]).strip(),
                latitude=float(item["latitude"]),
                longitude=float(item["longitude"]),
                sequence=sequence,
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ValidationError(f"invalid stop at position {sequence}") from exc

        if not stop.order_id or not (-90 <= stop.latitude <= 90):
            raise ValidationError(f"invalid stop at position {sequence}")
        if not (-180 <= stop.longitude <= 180):
            raise ValidationError(f"invalid stop at position {sequence}")
        stops.append(stop)

    return service_date, stops


def create_demo_blueprint(repository: RouteWriter) -> Blueprint:
    bp = Blueprint("demo_routes", __name__, url_prefix="/api/demo/routes")

    @bp.post("")
    def save_route():
        # Authentication middleware resolves the tenant context.
        tenant_id = request.environ.get("demo.tenant_id")
        if not isinstance(tenant_id, int):
            return jsonify(error="authentication required"), 401

        try:
            service_date, stops = _parse_plan(request.get_json(silent=True))
            route_id = repository.save_plan(
                tenant_id=tenant_id,
                service_date=service_date,
                stops=stops,
            )
        except ValidationError as exc:
            return jsonify(error=str(exc)), 400

        return jsonify(
            route_id=route_id,
            service_date=service_date.isoformat(),
            stops=[asdict(stop) for stop in stops],
        ), 201

    return bp

