/** Synthetic same-origin API client; contains no production endpoints. */

let csrfToken = null;

export class ApiError extends Error {
  constructor(message, { status = 0, details = null } = {}) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

async function loadCsrfToken(signal) {
  const response = await fetch("/api/demo/csrf", {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
    signal,
  });
  if (!response.ok) throw new ApiError("Unable to initialize request security");
  const body = await response.json();
  csrfToken = body.csrf_token;
  return csrfToken;
}

export async function fetchJson(path, options = {}) {
  const {
    method = "GET",
    body,
    timeoutMs = 15_000,
    signal: callerSignal,
    retryCsrf = true,
  } = options;

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort("timeout"), timeoutMs);
  const abortFromCaller = () => controller.abort(callerSignal.reason);
  callerSignal?.addEventListener("abort", abortFromCaller, { once: true });

  try {
    const mutating = !["GET", "HEAD", "OPTIONS"].includes(method.toUpperCase());
    if (mutating && !csrfToken) await loadCsrfToken(controller.signal);

    const response = await fetch(path, {
      method,
      credentials: "same-origin",
      signal: controller.signal,
      headers: {
        Accept: "application/json",
        ...(body ? { "Content-Type": "application/json" } : {}),
        ...(mutating ? { "X-CSRF-Token": csrfToken } : {}),
      },
      body: body ? JSON.stringify(body) : undefined,
    });

    if (response.status === 403 && retryCsrf && mutating) {
      csrfToken = null;
      await loadCsrfToken(controller.signal);
      return fetchJson(path, { ...options, retryCsrf: false });
    }

    const payload = await response.json().catch(() => null);
    if (!response.ok) {
      throw new ApiError(payload?.error ?? "Request failed", {
        status: response.status,
        details: payload,
      });
    }
    return payload;
  } catch (error) {
    if (error.name === "AbortError") {
      throw new ApiError("Request cancelled or timed out");
    }
    throw error;
  } finally {
    clearTimeout(timeout);
    callerSignal?.removeEventListener("abort", abortFromCaller);
  }
}

export function saveDemoRoute(route) {
  return fetchJson("/api/demo/routes", { method: "POST", body: route });
}

