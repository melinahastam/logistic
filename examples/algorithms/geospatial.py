from dataclasses import dataclass
from math import asin, cos, radians, sin, sqrt
from typing import Iterable

EARTH_RADIUS_KM = 6371.0088


@dataclass(frozen=True)
class Stop:
    stop_id: str
    latitude: float
    longitude: float
    demand: float = 1.0


def haversine_km(a: Stop, b: Stop) -> float:
    lat1, lat2 = radians(a.latitude), radians(b.latitude)
    delta_lat = lat2 - lat1
    delta_lon = radians(b.longitude - a.longitude)
    value = sin(delta_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(delta_lon / 2) ** 2
    return 2 * EARTH_RADIUS_KM * asin(sqrt(value))


def _center(stops: list[Stop]) -> Stop:
    total = sum(stop.demand for stop in stops) or len(stops)
    return Stop(
        stop_id="center",
        latitude=sum(stop.latitude * stop.demand for stop in stops) / total,
        longitude=sum(stop.longitude * stop.demand for stop in stops) / total,
    )


def allocate_by_capacity(stops: Iterable[Stop], capacity: float) -> list[list[Stop]]:
    """Allocate nearby stops without exceeding vehicle capacity."""
    if capacity <= 0:
        raise ValueError("capacity must be positive")

    pending = sorted(stops, key=lambda item: item.stop_id)
    if any(stop.demand <= 0 or stop.demand > capacity for stop in pending):
        raise ValueError("each demand must be positive and no larger than capacity")

    clusters: list[list[Stop]] = []
    while pending:
        cluster = [pending.pop(0)]
        load = cluster[0].demand
        while pending:
            center = _center(cluster)
            candidates = [stop for stop in pending if load + stop.demand <= capacity]
            if not candidates:
                break
            nearest = min(candidates, key=lambda stop: (haversine_km(center, stop), stop.stop_id))
            pending.remove(nearest)
            cluster.append(nearest)
            load += nearest.demand
        clusters.append(cluster)
    return clusters


def nearest_neighbor(stops: Iterable[Stop], origin: Stop) -> list[Stop]:
    pending = list(stops)
    ordered: list[Stop] = []
    current = origin
    while pending:
        next_stop = min(pending, key=lambda stop: (haversine_km(current, stop), stop.stop_id))
        pending.remove(next_stop)
        ordered.append(next_stop)
        current = next_stop
    return ordered

