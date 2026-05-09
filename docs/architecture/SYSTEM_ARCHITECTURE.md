# MAMA-LENS AI — System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                 │
├──────────────┬──────────────┬──────────────┬──────────────┬─────────┤
│  Mobile App  │   Web App    │  WhatsApp    │  SMS/USSD    │ Wearable│
│ (React Native│  (React +    │  (Meta API)  │(Africa's     │  Devices│
│  Expo)       │  TypeScript) │              │ Talking)     │  (IoT)  │
└──────┬───────┴──────┬───────┴──────┬───────┴──────┬───────┴────┬────┘
       │              │              │              │            │
       └──────────────┴──────────────┴──────────────┴────────────┘
                                     │
                              ┌──────▼──────┐
                              │   NGINX     │
                              │  Reverse    │
                              │   Proxy     │
                              └──────┬──────┘
                                     │
       ┌─────────────────────────────┼─────────────────────────────┐
       │                             │                             │
┌──────▼──────┐              ┌───────▼──────┐             ┌───────▼──────┐
│  FastAPI    │              │  Node.js     │             │  SMS/USSD    │
│  Core API   │              │  Telemedicine│             │  Gateway     │
│  (Python)   │              │  Service     │             │  Service     │
└──────┬──────┘              └───────┬──────┘             └──────────────┘
       │                             │
       │                    ┌────────▼────────┐
       │                    │   LiveKit       │
       │                    │   WebRTC Server │
       │                    └─────────────────┘
       │
┌──────▼──────────────────────────────────────────────────────────────┐
│                         AI/ML LAYER                                  │
├─────────────────┬─────────────────┬─────────────────┬───────────────┤
│  Risk Engine    │  Emotion AI     │  Conversation   │ Recommendation│
│  (TF/PyTorch)   │  (NLP Models)   │  AI (GPT-4o)    │ Engine        │
└─────────────────┴─────────────────┴─────────────────┴───────────────┘
       │
┌──────▼──────────────────────────────────────────────────────────────┐
│                         DATA LAYER                                   │
├─────────────────┬─────────────────┬─────────────────────────────────┤
│   PostgreSQL    │     Redis       │         AWS S3                  │
│   (Primary DB)  │  (Cache/Queue)  │    (Media/Documents)            │
└─────────────────┴─────────────────┴─────────────────────────────────┘
       │
┌──────▼──────────────────────────────────────────────────────────────┐
│                      INFRASTRUCTURE LAYER                            │
├─────────────────┬─────────────────┬─────────────────────────────────┤
│   Kubernetes    │   Prometheus    │         Sentry                  │
│   (Orchestration│   + Grafana     │    (Error Tracking)             │
│   & Scaling)    │  (Monitoring)   │                                 │
└─────────────────┴─────────────────┴─────────────────────────────────┘
```

## Data Flow Diagrams

### Risk Assessment Flow
```
User Input → API Validation → Risk Engine
    → Rule-Based Scoring (always)
    → ML Model Overlay (if available)
    → Emergency Detection
    → Recommendations Generation
    → Database Storage
    → Cache Update
    → Emergency Alert (if needed)
    → Response to User
```

### WhatsApp Message Flow
```
User Message → Meta Webhook → Signature Verification
    → Language Detection
    → Session Retrieval (Redis)
    → Intent Classification
    → Emergency Check
    → GPT-4o Response Generation
    → Response Simplification (if needed)
    → WhatsApp API Send
    → Message Logging (DB)
    → Session Update (Redis)
```

### Telemedicine Flow
```
Patient Request → Appointment Check → LiveKit Room Creation
    → Token Generation (patient + clinician)
    → WebRTC Connection
    → Video/Audio Stream
    → Real-time Transcription (optional)
    → Clinical Notes Entry
    → Prescription Generation
    → Consultation Record Storage
    → Follow-up Scheduling
    → Patient Feedback Collection
```

## Security Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      SECURITY LAYERS                                 │
├─────────────────────────────────────────────────────────────────────┤
│  Layer 1: Transport Security                                         │
│  - TLS 1.3 for all connections                                       │
│  - HSTS headers                                                      │
│  - Certificate pinning (mobile)                                      │
├─────────────────────────────────────────────────────────────────────┤
│  Layer 2: Authentication & Authorization                             │
│  - JWT tokens (access + refresh)                                     │
│  - OTP verification (SMS/email)                                      │
│  - Optional 2FA (TOTP)                                               │
│  - Role-based access control (RBAC)                                  │
├─────────────────────────────────────────────────────────────────────┤
│  Layer 3: Data Protection                                            │
│  - AES-256 encryption at rest                                        │
│  - Field-level encryption for PHI/PII                                │
│  - PostgreSQL row-level security                                     │
│  - S3 server-side encryption                                         │
├─────────────────────────────────────────────────────────────────────┤
│  Layer 4: Application Security                                       │
│  - Input validation (Pydantic)                                       │
│  - SQL injection prevention (SQLAlchemy ORM)                         │
│  - Rate limiting (Redis)                                             │
│  - CORS configuration                                                │
│  - Security headers (HSTS, CSP, etc.)                                │
├─────────────────────────────────────────────────────────────────────┤
│  Layer 5: Compliance                                                 │
│  - HIPAA principles                                                  │
│  - GDPR principles                                                   │
│  - Kenya Data Protection Act 2019                                    │
│  - AU Data Policy Framework                                          │
│  - Consent management                                                │
│  - Audit logging                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Database Schema Overview

```
users
  ├── pregnancy_profiles (1:many)
  │   ├── risk_assessments (1:many)
  │   └── health_records (1:many)
  │       └── vital_signs (1:many)
  ├── appointments (1:many)
  │   └── consultations (1:1)
  │       └── messages (1:many)
  ├── wearable_devices (1:many)
  │   └── wearable_readings (1:many)
  ├── notifications (1:many)
  └── consent_records (1:many)

health_facilities
  └── appointments (1:many)
```

## Scalability Strategy

### Horizontal Scaling
- Kubernetes auto-scaling based on CPU/memory
- Database read replicas for query distribution
- Redis cluster for cache distribution
- CDN for static assets

### Offline-First Architecture
- Service workers for web app caching
- SQLite local database for mobile app
- Background sync when connectivity restored
- Conflict resolution for offline edits

### Low-Bandwidth Optimization
- Compressed API responses (gzip)
- Image optimization and lazy loading
- Progressive Web App (PWA) capabilities
- SMS/USSD fallback for no-internet scenarios
- Minimal data transfer for mobile networks

### Multi-Region Deployment
- Primary: AWS af-south-1 (Cape Town)
- Secondary: AWS eu-west-1 (Ireland) for diaspora
- CDN: CloudFront with African edge locations
- Database: Multi-AZ PostgreSQL with read replicas
