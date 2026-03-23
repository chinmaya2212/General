# Platform Security Architecture

## 1. Authentication & Identity
- **JWT-Based Session Management**: All client-server communication is secured via HS256-signed JSON Web Tokens.
- **Backend Role-Based Access Control (RBAC)**: Critical endpoints (Ingest, Admin, Management) are guarded by a `require_role` dependency, enforcing least privilege for `analyst`, `executive`, and `admin` roles.
- **Frontend Protection**: Next.js Middleware and `ProtectedRoute` components ensure that unauthenticated users are redirected and unauthorized UI elements are omitted.

## 2. Ingestion & Data Safety
- **Input Validation**: The ingestion pipeline enforces entity-type registries and strictly validates file extensions (`.json`, `.csv`) and payload sizes (10MB limit).
- **Schema Enforcement**: Normalization services use Pydantic models to ensure data integrity before persistence.
- **Sanitized Persistence**: All database interactions use parameterized queries via the `motor` (app-level) driver to prevent injection.

## 3. AI Safety & Grounding
- **Prompt Injection Defense**: All agentic workflows use a "System Instruction" pattern that explicitly separates system constraints from user-provided context.
- **Constitutional Guardrails**: Agents are instructed to politely decline queries outside their security domain (e.g., non-governance queries to the Policy Advisor).
- **Verifiable RAG**: Responses are grounded in a private Knowledge Graph and Vector Store, with mandatory citations for every claim.

## 4. Operational Hardening
- **Secret Management**: API keys and database URIs are never exposed to the frontend.
- **Audit Logging**: Successful and failed admin actions are logged at the service level.
- **Local Storage Caveat**: For this MVP, tokens are stored in `localStorage`. For production, migration to `HttpOnly` cookies is recommended to mitigate XSS risks.

---
*Last Security Audit: March 2026*
