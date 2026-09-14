# Zero-Exposure Contact Gateway & SMTP Relay

## 1. Overview

The **Contact Gateway** provides a secure, private communication channel for visitors on [codexrelic.com](https://codexrelic.com) to reach Mohd Azam directly without exposing personal email addresses or phone numbers anywhere in the frontend HTML, JavaScript, or public code repositories.

---

## 2. Architecture & Security Model

```text
┌────────────────────────────────────────────────────────┐
│                   Visitor Browser                      │
│   (contact.html - Vanilla JS + DOM Sanitization)       │
└───────────────────────────┬────────────────────────────┘
                            │
                            │ POST /api/contact (JSON payload)
                            ▼
┌────────────────────────────────────────────────────────┐
│                   FastAPI Backend                      │
│   • Request Validation (Pydantic regex sanitization)   │
│   • Anti-Injection / Anti-XSS filter                   │
└───────────────┬────────────────────────┬───────────────┘
                │                        │
                │ Persists               │ Relays (SMTP TLS)
                ▼                        ▼
┌───────────────────────────┐  ┌─────────────────────────┐
│     MongoDB Atlas M0      │  │     Gmail SMTP Relay     │
│   Collection: `inquiries` │  │ (smtp.gmail.com:587 TLS) │
└───────────────────────────┘  └────────────┬────────────┘
                                            │
                                            ▼
                               ┌─────────────────────────┐
                               │  Private Inbox Delivery │
                               │(Reply-To: Visitor Email)│
                               └─────────────────────────┘
```

### Key Security & Privacy Guarantees:
1. **Zero Client-Side Exposure**: Neither personal email addresses nor phone numbers exist in the static HTML or client JavaScript bundles.
2. **Server-Side Credential Isolation**: SMTP server credentials and destination mailboxes are strictly read from server environment variables at runtime (`.env` locally, Azure Key Vault in CI/CD).
3. **Automated Threat Sanitization**:
   - Client-side validation blocks null bytes, CRLF header injection, XSS vectors, and script tags.
   - Pydantic backend models validate string lengths and email formatting before processing.
4. **Resilient Dual Storage**:
   - All inbound inquiries are permanently recorded to MongoDB (`inquiries` collection).
   - Inquiries are forwarded in real time to the administrator's mailbox with `Reply-To` set to the visitor's email.

---

## 3. API Specification

### Endpoint: `POST /api/contact`

**Request Headers**:
```http
Content-Type: application/json
```

**Request Body (JSON)**:
```json
{
  "name": "Sarah Connor",
  "email": "sarah@example.com",
  "subject": "[SRE Role / Opportunity]",
  "message": "Hello Azam, I came across your portfolio and would like to discuss an opportunity."
}
```

**Field Validation Rules**:
| Field | Type | Required | Constraints |
|---|---|---|---|
| `name` | `string` | Yes | Min: 2 chars, Max: 80 chars |
| `email` | `string` | Yes | Valid RFC-compliant email, Max: 120 chars |
| `subject` | `string` | Yes | Min: 3 chars, Max: 150 chars |
| `message` | `string` | Yes | Min: 10 chars, Max: 3,000 chars |

**Successful Response (`200 OK`)**:
```json
{
  "success": true,
  "message": "Thank you! Your message has been received and routed securely."
}
```

---

## 4. Environment Variables Configuration

| Variable | Default Value | Description |
|---|---|---|
| `SMTP_HOST` | `smtp.gmail.com` | SMTP relay server hostname |
| `SMTP_PORT` | `587` | SMTP port (STARTTLS) |
| `SMTP_USER` | `""` | Authenticated sending email username |
| `SMTP_PASS` | `""` | 16-character Google App Password or SMTP token |
| `CONTACT_RECIPIENT_EMAIL` | `aazam.mohammad193@gmail.com` | Destination inbox for incoming inquiries |

---

## 5. Deployment & Secret Management

### Local Development:
Set the variables in `src/.env` (which is included in `.gitignore`):
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=aazam.mohammad193@gmail.com
SMTP_PASS=your_app_password
CONTACT_RECIPIENT_EMAIL=aazam.mohammad193@gmail.com
```

### UAT & Production Environments (Kubernetes via Azure Pipelines):
1. **Azure Key Vault**:
   Store the credentials in `kv-codexrelic-uat` and `kv-codexrelic-prod`:
   - `SMTP-USER` &rarr; `aazam.mohammad193@gmail.com`
   - `SMTP-PASS` &rarr; `<16-char-app-password>`
2. **Azure Pipeline (`deploy-stage.yml`)**:
   The deployment stage automatically fetches `SMTP-USER` and `SMTP-PASS` via the `AzureKeyVault@2` task and injects them into the runtime Kubernetes pod environment.
