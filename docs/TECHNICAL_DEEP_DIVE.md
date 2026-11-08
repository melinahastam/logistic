# Technical Deep Dive

This document focuses on engineering depth rather than end-user feature lists.

## 1. SQL Server and data engineering

The backend uses SQL Server through `pyodbc` and separates database access into repository-oriented modules.

### Implemented patterns

- Parameterized `cursor.execute` and `executemany` operations instead of string-concatenating user input
- Explicit transaction boundaries for workflows that update routes, stops, assignments, tours, and customers together
- `MERGE`-based upserts for repeatable synchronization without uncontrolled duplicate insertion
- Temporary staging tables for validating and joining bulk operational payloads
- `fast_executemany` for efficient batch insertion
- Tenant-aware predicates and SQL session context to prevent cross-tenant reads and writes
- Repository functions for orders, routes, users, visitors, sessions, and activity logs
- Pagination and database-side filtering for large operational tables
- Normalization of nullable values, dates, Persian text, numeric fields, and identifiers before persistence
- Transaction rollback and user-safe error translation on failure

### Why this matters

Route planning is not a single-row CRUD operation. Saving a plan can affect the route header, ordered stops, order assignments, driver relationships, dates, and synchronization state. Treating these updates as one consistency boundary prevents partial operational plans.

## 2. REST API design with Flask

The backend exposes domain-oriented JSON APIs using Flask blueprints.

```text
HTTP route
  → authentication and tenant resolution
  → payload validation and normalization
  → domain service
  → repository or provider adapter
  → consistent JSON response
```

### API engineering concerns addressed

- Clear separation between HTTP handling and business workflows
- GET endpoints for queries and POST/DELETE endpoints for controlled mutations
- Consistent handling of JSON bodies, query parameters, pagination, and status codes
- Centralized authorization and tenant context
- CSRF requirements on same-origin mutations
- Provider-specific adapters behind stable internal endpoints
- Timeouts and error mapping for third-party calls
- Restricted Wialon proxying rather than accepting arbitrary external requests
- Cron/shared-secret protection for scheduled operational endpoints
- Activity logging with exclusions for highly sensitive/authentication traffic

See [API & Integrations](API_INTEGRATIONS.md) for the route-to-destination matrix.

## 3. Modern asynchronous JavaScript

The frontend is implemented as focused JavaScript modules rather than one UI framework bundle.

### Async patterns used

- `async/await` for readable request and workflow sequencing
- `fetch` wrappers with credentials and JSON normalization
- Automatic CSRF token acquisition and one-time retry after token expiration
- `AbortController` for bounded network operations
- `Promise.all` for independent requests that can run concurrently
- Busy-state and in-flight guards to prevent duplicate submission
- Progressive UI feedback during clustering, imports, and synchronization
- Request timeouts for long-running operational jobs
- Deterministic state updates after asynchronous mutations
- Error handling that separates transport, provider, validation, and business failures

### UI state

The application maintains state for selected orders, visible layers, drivers, clusters, visitors, calendar edits, filters, pagination, and provider sessions. State-changing actions update both the model and map/table representation to avoid stale UI.

## 4. Geospatial algorithms

The platform includes domain-specific planning logic rather than only calling external APIs.

### Geographic clustering

- K-means-style allocation using latitude/longitude points
- Capacity enforcement and oversized-cluster refinement
- Cluster renumbering and deterministic ordering
- Manual corrections and customer transfers after automatic allocation
- Haversine distance for geographic comparison
- Geographic centers for cluster and region calculations

### Stop ordering

- Nearest-neighbor sequencing for fast operational ordering
- Recalculation after manual edits
- Optional external optimization through Neshan Trip and Logistics APIs
- Separate route identity and stop sequence to preserve order identity during reordering

## 5. Editable workday scheduling

The field-visit calendar combines business cycles with calendar rules:

- Jalali/Gregorian conversion
- Official Iranian holiday retrieval and normalization
- Friday and holiday exclusion from generated workdays
- Different visit cycles based on operational line
- Geographic ordering of visitor clusters
- Multi-week schedule generation
- Drag-and-drop rescheduling within a visitor's calendar
- Click-based accessible date selection
- Undo and cancel snapshots
- Recalculation of visit and dependent delivery dates
- Propagation to reports, persistence payloads, and fleet synchronization

## 6. Security and multi-tenancy

- Session-based authentication
- PBKDF2 password hashing with random salt
- Upgrade path for legacy password hashes
- CSRF token creation, validation, and rotation
- Role and permission checks
- Active-account validation
- Login failure tracking and temporary throttling
- Tenant resolution for every protected request
- Tenant predicates in repository queries
- Sensitive configuration sourced from environment variables
- Third-party credentials kept behind backend adapters
- Activity audit events for operational mutations

## 7. External integrations

### Neshan

The browser calls internal `/tsp` and `/neshan_logistics` endpoints. The backend builds provider-specific vehicle/job payloads, adds the server-side API key, applies a timeout, validates the response, and returns a normalized result.

### Wialon

The backend owns token login and session renewal. The frontend requests only approved Wialon services through a same-origin proxy. Orders and routes are constructed from approved clusters, visitor-to-unit mappings, and calendar dates.

### Iranian holiday data

The backend retrieves `https://www.time.ir/event-year`, decodes and normalizes holiday titles, and exposes a stable year-based endpoint to the calendar module.

### ERP and data warehouse

ERP tour submission and data-warehouse imports are isolated behind server workflows. Provider hosts, accounts, database names, and customer-specific payloads are deliberately absent from this public repository.

### Selenium ERP clicker

One operational ERP did not provide a suitable API for the required tour-entry workflow. A controlled Selenium WebDriver automation service was implemented instead of placing browser automation in the user's frontend.

The workflow includes:

- receiving only an approved temporary tour file through an authenticated backend route;
- parsing and grouping records by visitor and tour date;
- starting the configured browser driver on the server;
- authenticating with environment-provided credentials;
- using `WebDriverWait` and expected conditions for reliable DOM interaction;
- selecting dates and entering tour information into ERP forms;
- capturing an execution log for each processed group;
- handling browser or validation failures without leaking credentials;
- quitting the WebDriver and deleting temporary files through guaranteed cleanup paths.

This is intentionally described as browser automation—not a REST integration—because it automates an existing user workflow when a stable external API is unavailable.

## 8. Performance and scalability work

- Batch SQL operations and temporary staging tables
- Database-side pagination and filtering
- Reuse of map layer groups instead of rebuilding the entire map
- Cached holiday and lookup data
- Concurrent independent requests where safe
- Incremental progress reporting for CPU-heavy browser operations
- Selection maps/sets for constant-time UI membership checks
- Controlled rendering of large driver, order, and cluster collections
- Server and provider timeouts to avoid indefinitely blocked workflows

## 9. Reliability and maintainability

- Route/service/repository boundaries
- Modular frontend organized by domain
- Legacy-compatible staged migration
- Security and core-helper tests
- Parity checklists for migration work
- Defensive normalization at system boundaries
- Recoverable soft-delete flows for operational records
- Detailed operational error logging without returning credentials to the browser

## 10. Secondary capabilities

File import/export, report generation, and print workflows are present, but they are supporting capabilities rather than the core engineering focus of this portfolio.
