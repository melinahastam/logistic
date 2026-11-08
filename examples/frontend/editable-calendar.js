/** Pure state model for a synthetic editable visit calendar. */

const clone = (value) => structuredClone(value);

function addDays(isoDate, days) {
  const date = new Date(`${isoDate}T12:00:00Z`);
  date.setUTCDate(date.getUTCDate() + days);
  return date.toISOString().slice(0, 10);
}

function nextBusinessDate(isoDate, daysAfterVisit = 1) {
  let result = isoDate;
  let remaining = daysAfterVisit;
  while (remaining > 0) {
    result = addDays(result, 1);
    const weekday = new Date(`${result}T12:00:00Z`).getUTCDay();
    if (weekday !== 5) remaining -= 1; // Friday excluded in this public sample.
  }
  return result;
}

export class EditableVisitCalendar {
  #rows;
  #history = [];

  constructor(rows) {
    this.#rows = clone(rows);
  }

  get value() {
    return clone(this.#rows);
  }

  moveVisit({ visitorId, clusterId, targetDate }) {
    const row = this.#rows.find((item) => item.visitorId === visitorId);
    if (!row) throw new Error("Unknown visitor");
    if (!row.allowedDates.includes(targetDate)) throw new Error("Date is not selectable");

    const visit = row.visits.find((item) => item.clusterId === clusterId);
    if (!visit) throw new Error("Unknown cluster");

    this.#history.push(clone(this.#rows));
    visit.visitDate = targetDate;
    visit.deliveryDate = nextBusinessDate(targetDate, visit.deliveryLagDays ?? 1);
    row.visits.sort((a, b) => a.visitDate.localeCompare(b.visitDate));
    return clone(visit);
  }

  undo() {
    const previous = this.#history.pop();
    if (!previous) return false;
    this.#rows = previous;
    return true;
  }

  cancelAllEdits() {
    if (!this.#history.length) return false;
    this.#rows = this.#history[0];
    this.#history = [];
    return true;
  }
}

