"""Synthetic SQL Server repository; table names are deliberately fictional."""

from contextlib import contextmanager
from datetime import date
from typing import Iterator, Protocol


class StopLike(Protocol):
    order_id: str
    latitude: float
    longitude: float
    sequence: int


class SqlServerRouteRepository:
    def __init__(self, connection_factory):
        self._connection_factory = connection_factory

    @contextmanager
    def _transaction(self) -> Iterator[object]:
        connection = self._connection_factory()
        connection.autocommit = False
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def save_plan(
        self, *, tenant_id: int, service_date: date, stops: list[StopLike]
    ) -> int:
        with self._transaction() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "EXEC sys.sp_set_session_context @key=N'tenant_id', @value=?",
                tenant_id,
            )
            cursor.execute(
                """
                INSERT INTO dbo.DemoRoute (tenant_id, service_date, status)
                OUTPUT INSERTED.route_id
                VALUES (?, ?, ?)
                """,
                tenant_id,
                service_date,
                "draft",
            )
            route_id = int(cursor.fetchone()[0])

            cursor.execute(
                """
                CREATE TABLE #RouteStopInput (
                    order_id nvarchar(64) NOT NULL,
                    latitude decimal(9, 6) NOT NULL,
                    longitude decimal(9, 6) NOT NULL,
                    stop_sequence int NOT NULL
                )
                """
            )
            cursor.fast_executemany = True
            cursor.executemany(
                "INSERT INTO #RouteStopInput VALUES (?, ?, ?, ?)",
                [
                    (stop.order_id, stop.latitude, stop.longitude, stop.sequence)
                    for stop in stops
                ],
            )

            # Idempotent key: tenant + route + order. Replaying updates the same rows.
            cursor.execute(
                """
                MERGE dbo.DemoRouteStop WITH (HOLDLOCK) AS target
                USING #RouteStopInput AS source
                   ON target.tenant_id = ?
                  AND target.route_id = ?
                  AND target.order_id = source.order_id
                WHEN MATCHED THEN UPDATE SET
                    latitude = source.latitude,
                    longitude = source.longitude,
                    stop_sequence = source.stop_sequence
                WHEN NOT MATCHED THEN INSERT
                    (tenant_id, route_id, order_id, latitude, longitude, stop_sequence)
                VALUES
                    (?, ?, source.order_id, source.latitude,
                     source.longitude, source.stop_sequence);
                """,
                tenant_id,
                route_id,
                tenant_id,
                route_id,
            )
            return route_id

