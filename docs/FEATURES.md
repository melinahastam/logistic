# Feature & Engineering Inventory

## Map workspace

- Interactive Leaflet map with multiple independent layer groups
- Driver, visitor, customer, order, cluster, route, and stop rendering
- Layer visibility controls and state preservation across panel changes
- Route polylines, numbered markers, fit-to-bounds, and selection feedback
- Responsive split-screen operational panels

## Order lifecycle

- Excel/CSV ingestion and column normalization
- Manual order creation and editing
- Search, filters, date ranges, pagination, and bulk selection
- Driver assignment and route removal
- Database persistence and status tracking
- Excel and print-oriented reports

## Clustering and route planning

- Capacity-constrained geographic K-means workflow
- Cluster refinement and maximum-size enforcement
- Manual cluster correction and reassignment
- Nearest-neighbor stop sequencing
- Cost-aware and compatibility allocation modes
- Route and stop transactional persistence

## Field-visit workflows

- Visitor/customer file preparation
- Per-visitor cluster-count configuration
- Geographic customer clustering and map visibility controls
- Transfer of customers between compatible clusters
- Multi-week workday calendar generation
- Jalali/Gregorian date conversion and official holiday awareness
- Drag-and-drop calendar edits with undo and cancellation
- Automatic dependent delivery-date recalculation
- Excel calendar export and fleet-route synchronization

## People and fleet management

- User, role, permission, and status management
- Driver, assistant, visitor, and vehicle records
- Daily shift and attendance updates
- Wialon unit mapping for operational personnel
- Soft-delete flows for recoverable administration

## Security and reliability

- Session-based authentication
- PBKDF2 password hashing and legacy-hash upgrade path
- CSRF protection for state-changing requests
- Login throttling and account state checks
- Tenant context and tenant-scoped SQL access
- Parameterized repository operations
- Activity logging with sensitive-route exclusions
- Server-side provider proxy and allow-listed external calls

## Browser automation

- Selenium WebDriver worker for a private ERP workflow without a suitable integration API
- Explicit waits and deterministic element interaction
- Server-held credentials and private endpoint configuration
- Input grouping by tour/date before form submission
- Per-item execution logs and failure reporting
- Guaranteed WebDriver shutdown and temporary-file cleanup

## Modularization work

- Frontend features split into focused JavaScript modules
- Flask blueprints separated by domain
- Business logic extracted into services
- Database logic extracted into repositories
- Shared security, tenant, configuration, and response helpers centralized
- Legacy-compatible runtime retained during staged migration
- Parity checks used to reduce regression risk
