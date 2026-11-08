# API & Integration Inventory

This document describes the integration design without publishing credentials, private hosts, database names, or customer-specific payloads.

## Request path

```text
Browser module
  → same-origin Flask endpoint
    → authentication / CSRF / validation
      → service adapter or repository
        → SQL Server or approved external provider
```

## External providers

| Internal endpoint | Method | Destination | Data sent | Result used for |
|---|---:|---|---|---|
| `/tsp` | POST | `Neshan Trip API v3` | Coordinates and trip options | Stop sequencing and route geometry workflow |
| `/neshan_logistics` | POST | `Neshan Logistics API v5` | Vehicle constraints and geographic jobs | Multi-vehicle job assignment and optimization |
| `/api/wialon_proxy` | POST | `Wialon Remote API` | Allow-listed service name and sanitized parameters | Fleet units, orders, routes, and route updates |
| `/api/wialon_client_config` | GET | Server-side Wialon configuration adapter | No provider token returned | Non-secret client integration settings |
| `/api/iran_holidays` | GET | `https://www.time.ir/event-year` | Requested Jalali year | Official holiday normalization for workday calendars |
| `/rahkaran/send_tours` | POST | Selenium WebDriver → private ERP workflow | Approved temporary tour file | Controlled form entry and item-level operation logs |
| `/sale_request/send` | POST | Sales integration adapter | Validated sales-request payload | Submit operational sales requests |

Provider keys and credentials are read from server environment variables. The browser never calls provider APIs with secret tokens.

### Selenium ERP adapter

`POST /rahkaran/send_tours` accepts an approved tour file, validates its extension, writes it to a uniquely named temporary path, and invokes a server-side Selenium worker. The worker:

1. launches the configured WebDriver;
2. authenticates against the ERP form with server-held credentials;
3. uses explicit waits for page controls rather than fixed sleeps;
4. groups input rows into tour/date operations;
5. fills and submits the required form controls;
6. returns structured execution logs to the caller;
7. quits the driver and removes the temporary file on success or failure.

This automation was used where a stable provider API was not available. The private URL, deployment-specific selectors, and credentials are intentionally omitted.

## Authentication and user administration

| Endpoint | Method | Responsibility |
|---|---:|---|
| `/auth/login` | POST | Validate credentials, establish session, rotate CSRF state |
| `/auth/logout` | POST | End authenticated session |
| `/auth/csrf` | GET | Provide CSRF token for same-origin mutations |
| `/auth/me` | GET | Return current authorized user profile |
| `/auth/signup` | POST | Create a tenant-scoped account |
| `/admin-change-password` | POST | Apply controlled password update |
| `/getallusers` | GET | Load permitted user records |
| `/updateusersaccess` | POST | Update access configuration |
| `/update-users-status` | POST | Activate or deactivate accounts |
| `/update-user-roles` | POST | Apply role assignments |

## Orders and operational data

| Endpoint group | Representative endpoints | Destination |
|---|---|---|
| Order CRUD | `/api/orders/create`, `/api/orders/update`, `/api/orders/delete` | Order service → SQL repository |
| Order queries | `/api/get_orders`, `/api/get_all_orders`, `/api/get_routed_orders_by_date` | Tenant-scoped SQL queries |
| Reference filters | `/api/get_order_regions`, `/api/get_order_types`, `/api/get_order_statuses` | Distinct operational reference data |
| Route cleanup | `/api/orders/delete_route` | Transactional route/order unlink workflow |
| Excel output | `/api/orders/print_excel` | Server-side report generation |
| Data warehouse import | `/api/import_pending_requests_from_dw`, `/api/import_danayan_orders_from_dw` | Internal DW adapter → normalized operational orders |
| Order groups | `/api/dw_order_groups`, `/api/order_groups` | DW and local group catalogs |

## Clustering and routing

| Endpoint | Method | Responsibility |
|---|---:|---|
| `/kmeans` | POST | Base geographic clustering |
| `/manual_kmeans` | POST | User-directed clustering workflow |
| `/kmeans_vba_exact` | POST | Compatibility mode for an established allocation model |
| `/auto_kmeans` | POST | Select cluster count and run automated allocation |
| `/cost_effective` | POST | Cost-aware planning alternative |
| `/recalculate_order` | POST | Recalculate stop ordering after edits |
| `/save_route` | POST | Persist route metadata |
| `/save_route_stops` | POST | Persist ordered route stops |

Clustering combines capacity rules, geographic distance, cluster refinement, and deterministic stop ordering. Provider optimization is accessed separately through `/tsp` or `/neshan_logistics`.

## Field visits

| Endpoint | Method | Responsibility |
|---|---:|---|
| `/api/visit/customer_groups` | GET | Load visit customer group catalog |
| `/api/visit/customers_by_group` | POST | Load eligible customers for selected groups |
| `/api/visit/tours/by-date` | GET | Load tours scheduled for a date |
| `/api/visit/manage_routes` | GET | Paginated route/tour management view |
| `/api/visit/tours/customers` | GET | Load customers belonging to selected tours |
| `/api/visit/customers/update` | POST | Edit visit customer information |
| `/api/visit/customers/import` | POST | Import and normalize visit customers |
| `/api/visit/manage_routes/delete_customers` | POST | Remove selected tour customers safely |
| `/api/visit/manage_routes/delete_tours` | POST | Remove selected tours safely |
| `/visitor/groups` | GET | Load visitor line/group configuration |
| `/get_visitors_list` | GET | Load visitors and mapped fleet-unit identifiers |

The visit calendar is initially generated in the browser from workdays, line cycles, holidays, cluster geography, and visitor assignments. Approved dates are then sent to backend persistence and fleet workflows.

## Fleet, attendance, and scheduling

| Domain | Representative endpoints | Purpose |
|---|---|---|
| Drivers | `/get_drivers`, `/driver/add`, `/driver/edit`, `/driver/soft_delete` | Driver lifecycle and fleet metadata |
| Visitors | `/visitor/add`, `/visitor/edit`, `/visitor/update_status` | Visitor lifecycle and Wialon unit mapping |
| Attendance | `/get_driver_attendance`, `/driver/update_daily_shift`, `/assistant/update_shift` | Daily driver/assistant operations |
| Scheduler | `/api/auto_assign_and_save_planning_orders`, `/api/trigger_scheduled_sync` | Controlled background workflows |
| Cafe import/merge | `/api/cron/cafe_import`, `/api/cron/cafe_merge` | Protected scheduled ingestion and merge jobs |

## Deliberately omitted

- Provider tokens and account identifiers
- Internal IP addresses, hosts, ports, and database names
- Customer-specific schemas and example payload values
- Production retry limits and operational thresholds that reveal internal policy
- Any credential-bearing environment file
