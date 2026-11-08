import sys
import unittest
from pathlib import Path

EXAMPLES_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXAMPLES_ROOT))

from algorithms.geospatial import Stop, allocate_by_capacity, haversine_km, nearest_neighbor


class GeospatialTests(unittest.TestCase):
    def test_haversine_is_zero_for_same_point(self):
        point = Stop("A", 35.7000, 51.4000)
        self.assertEqual(haversine_km(point, point), 0.0)

    def test_capacity_is_never_exceeded(self):
        stops = [
            Stop("A", 35.70, 51.40, 4),
            Stop("B", 35.71, 51.41, 3),
            Stop("C", 35.72, 51.42, 5),
            Stop("D", 35.73, 51.43, 2),
        ]
        clusters = allocate_by_capacity(stops, capacity=7)
        assigned = {stop.stop_id for group in clusters for stop in group}
        self.assertEqual(assigned, {"A", "B", "C", "D"})
        self.assertTrue(all(sum(stop.demand for stop in group) <= 7 for group in clusters))

    def test_nearest_neighbor_is_deterministic(self):
        origin = Stop("origin", 35.70, 51.40)
        ordered = nearest_neighbor(
            [Stop("far", 35.90, 51.60), Stop("near", 35.71, 51.41)],
            origin,
        )
        self.assertEqual([stop.stop_id for stop in ordered], ["near", "far"])


if __name__ == "__main__":
    unittest.main()

