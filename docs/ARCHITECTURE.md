# Architecture

## Design goals

- Keep the map responsive while large operational panels are open.
- Isolate provider credentials from browser code.
- Preserve operational behavior during gradual modularization.
- Keep business workflows out of HTTP route handlers.
- Apply tenant scope and authorization consistently.
- Support bulk imports and exports without coupling UI code to database details.

## Frontend

The frontend is split into focused JavaScript modules for authentication, map bootstrap, orders, clustering, routing, drivers, users, visits, reporting, and API access.

Key responsibilities include:

- Leaflet layer lifecycle and viewport management
- Large table rendering, filters, pagination, and selection state
- Excel/CSV parsing and validation feedback
- Cluster, route, order, driver, and visitor visualization
- Editable visit-calendar state and dependent-date recalculation
- Same-origin API calls with CSRF and session handling

## Backend

The Flask backend follows an incremental layered structure:

```text
routes/        HTTP request validation and response shaping
services/      business workflows and external-provider adapters
repositories/ parameterized database operations
core/          configuration, security, tenant context, shared helpers
```

The migration was staged so existing production behavior could continue while responsibilities were extracted from the legacy implementation.

## Data flows

### Order planning

```mermaid
sequenceDiagram
    participant U as User
    participant UI as Browser UI
    participant API as Flask API
    participant S as Planning Service
    participant DB as SQL Server
    participant P as Routing Provider

    U->>UI: Import/filter/select orders
    UI->>API: Submit normalized planning payload
    API->>S: Validate tenant and business rules
    S->>P: Request trip/logistics optimization
    P-->>S: Ordered stops / assignments
    S->>DB: Save routes, stops and assignments
    DB-->>S: Transaction result
    S-->>UI: Operational route model
```

### Field-visit planning

```mermaid
sequenceDiagram
    participant U as User
    participant UI as Visit UI
    participant API as Flask API
    participant DB as SQL Server
    participant W as Wialon

    U->>UI: Upload customers and create clusters
    UI->>UI: Build multi-week visit calendar
    U->>UI: Move a cluster to another workday
    UI->>UI: Recalculate visit and delivery dates
    UI->>API: Save tours/customers
    API->>DB: Tenant-scoped transactional update
    UI->>API: Send approved route
    API->>W: Server-side authenticated proxy call
```

## Security boundaries

- Third-party tokens remain in server environment variables.
- Browser integrations use restricted same-origin proxy endpoints.
- Mutating requests use authenticated sessions and CSRF validation.
- Database access is parameterized and tenant-scoped.
- Sensitive infrastructure identifiers are excluded from this portfolio repository.

## Selenium automation boundary

An ERP workflow without a suitable integration API was automated behind a backend endpoint using Selenium WebDriver. The worker consumes a validated temporary tour file, opens an authenticated browser session, waits explicitly for required controls, fills date and tour fields, submits the form, records item-level results, and closes the browser in a guaranteed cleanup path. Credentials and the private ERP address remain server-side and are not included in this repository.

```mermaid
sequenceDiagram
    participant UI as Authorized user
    participant API as Flask endpoint
    participant W as Selenium worker
    participant ERP as Private ERP form

    UI->>API: Submit approved tour file
    API->>API: Validate and create temporary file
    API->>W: Start controlled automation job
    W->>ERP: Authenticate with server-held credentials
    W->>ERP: Wait for controls and submit tour forms
    ERP-->>W: Form result
    W-->>API: Item-level execution logs
    API->>API: Delete temporary file
    API-->>UI: Structured operation result
```
