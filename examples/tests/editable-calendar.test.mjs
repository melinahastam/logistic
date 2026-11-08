import assert from "node:assert/strict";
import test from "node:test";

import { EditableVisitCalendar } from "../frontend/editable-calendar.js";

const rows = [
  {
    visitorId: "visitor-1",
    allowedDates: ["2026-11-08", "2026-11-09"],
    visits: [
      {
        clusterId: "cluster-1",
        visitDate: "2026-11-08",
        deliveryDate: "2026-11-09",
        deliveryLagDays: 1,
      },
    ],
  },
];

test("moving a visit recalculates its dependent delivery date", () => {
  const calendar = new EditableVisitCalendar(rows);
  const moved = calendar.moveVisit({
    visitorId: "visitor-1",
    clusterId: "cluster-1",
    targetDate: "2026-11-09",
  });

  assert.equal(moved.visitDate, "2026-11-09");
  assert.equal(moved.deliveryDate, "2026-11-10");
});

test("undo restores the previous snapshot", () => {
  const calendar = new EditableVisitCalendar(rows);
  calendar.moveVisit({
    visitorId: "visitor-1",
    clusterId: "cluster-1",
    targetDate: "2026-11-09",
  });

  assert.equal(calendar.undo(), true);
  assert.equal(calendar.value[0].visits[0].visitDate, "2026-11-08");
});

