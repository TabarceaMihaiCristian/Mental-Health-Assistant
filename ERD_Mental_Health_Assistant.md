# Mental Health Assistant ERD

Diagrama de mai jos descrie structura actuala a principalelor entitati din backend si relatiile dintre ele.

```mermaid
erDiagram
    USERS {
        uuid id PK
        string email
        string full_name
        enum role
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    AUTH_IDENTITIES {
        uuid id PK
        uuid user_id FK
        enum provider
        string provider_user_id
        string email
        text password_hash
        boolean is_primary
        datetime created_at
        datetime updated_at
    }

    USER_PROFILES {
        uuid user_id PK
        string age_range
        string occupation
        text goals
        jsonb preferred_activities
        string timezone
        datetime created_at
        datetime updated_at
    }

    CHAT_SESSIONS {
        uuid id PK
        uuid user_id FK
        enum status
        datetime started_at
        datetime last_message_at
        datetime ended_at
        text summary
        datetime created_at
        datetime updated_at
    }

    CHAT_MESSAGES {
        uuid id PK
        uuid session_id FK
        enum sender
        text content
        datetime created_at
    }

    MOOD_ANALYSES {
        uuid id PK
        uuid session_id FK
        uuid message_id FK
        uuid user_id FK
        enum primary_mood
        enum secondary_mood
        smallint intensity
        numeric confidence
        enum risk
        text trigger_notes
        datetime created_at
    }

    RISK_EVENTS {
        uuid id PK
        uuid user_id FK
        uuid message_id FK
        uuid session_id FK
        enum risk
        text action_taken
        datetime created_at
    }

    DAILY_MOOD_SUMMARIES {
        uuid id PK
        uuid user_id FK
        date summary_date
        enum dominant_mood
        numeric average_intensity
        enum risk
        text summary_text
        datetime created_at
    }

    REPORTS {
        uuid id PK
        uuid user_id FK
        enum period
        date period_start
        date period_end
        jsonb report_data
        datetime created_at
    }

    SPECIALISTS {
        uuid id PK
        uuid user_id FK
        string full_name
        string specialty
        text bio
        jsonb consultation_modes
        string city
        enum status
        datetime created_at
        datetime updated_at
    }

    SPECIALIST_REVIEWS {
        uuid id PK
        uuid specialist_id FK
        uuid user_id FK
        smallint rating
        text comment
        datetime created_at
        datetime updated_at
    }

    SPECIALIST_AVAILABILITY_RULES {
        uuid id PK
        uuid specialist_id FK
        smallint weekday
        time start_time
        time end_time
        boolean is_enabled
        datetime created_at
        datetime updated_at
    }

    SPECIALIST_BREAKS {
        uuid id PK
        uuid specialist_id FK
        smallint weekday
        time start_time
        time end_time
        string label
        datetime created_at
        datetime updated_at
    }

    SPECIALIST_TIME_OFF {
        uuid id PK
        uuid specialist_id FK
        datetime start_datetime
        datetime end_datetime
        string reason
        datetime created_at
        datetime updated_at
    }

    APPOINTMENTS {
        uuid id PK
        uuid user_id FK
        uuid specialist_id FK
        enum mode
        enum status
        datetime preferred_datetime
        datetime end_datetime
        text notes
        text cancellation_reason
        text rejection_reason
        text reschedule_note
        datetime confirmed_at
        datetime rejected_at
        datetime cancelled_at
        datetime completed_at
        datetime last_rescheduled_at
        datetime reminder_sent_at
        enum last_rescheduled_by_role
        uuid status_updated_by_user_id FK
        datetime created_at
        datetime updated_at
    }

    NOTIFICATIONS {
        uuid id PK
        uuid user_id FK
        uuid appointment_id FK
        enum type
        string title
        text message
        boolean is_read
        datetime read_at
        datetime created_at
    }

    USERS ||--o{ AUTH_IDENTITIES : has
    USERS ||--|| USER_PROFILES : has
    USERS ||--o{ CHAT_SESSIONS : starts
    CHAT_SESSIONS ||--o{ CHAT_MESSAGES : contains
    USERS ||--o{ MOOD_ANALYSES : receives
    CHAT_SESSIONS ||--o{ MOOD_ANALYSES : aggregates
    CHAT_MESSAGES ||--o{ MOOD_ANALYSES : analyzes
    USERS ||--o{ RISK_EVENTS : triggers
    CHAT_SESSIONS ||--o{ RISK_EVENTS : contains
    CHAT_MESSAGES ||--o{ RISK_EVENTS : raises
    USERS ||--o{ DAILY_MOOD_SUMMARIES : owns
    USERS ||--o{ REPORTS : owns

    USERS ||--o{ APPOINTMENTS : books
    SPECIALISTS ||--o{ APPOINTMENTS : receives
    USERS ||--o| SPECIALISTS : may_map_to

    USERS ||--o{ SPECIALIST_REVIEWS : writes
    SPECIALISTS ||--o{ SPECIALIST_REVIEWS : receives
    SPECIALISTS ||--o{ SPECIALIST_AVAILABILITY_RULES : has
    SPECIALISTS ||--o{ SPECIALIST_BREAKS : has
    SPECIALISTS ||--o{ SPECIALIST_TIME_OFF : has

    USERS ||--o{ NOTIFICATIONS : receives
    APPOINTMENTS ||--o{ NOTIFICATIONS : generates
    USERS ||--o{ APPOINTMENTS : updates_status
```

## Observatii

- `users` este entitatea centrala pentru autentificare, chat, rapoarte, programari si notificari.
- `specialists.user_id` este optional, dar unic; permite maparea unui cont de utilizator la un profil de specialist.
- `user_profiles.user_id` este simultan cheie primara si cheie externa catre `users.id`, deci relatia este 1 la 1.
- `appointments.status_updated_by_user_id` leaga o modificare de status de un utilizator, separat de utilizatorul care a facut programarea.
- `risk_events.session_id` este optional, deoarece un eveniment de risc poate fi legat direct de mesaj, chiar daca sesiunea nu mai este activa.

## Cum il poti vizualiza

- In GitHub sau in editoare cu suport Mermaid, fisierul se randareaza direct.
- In VS Code poti folosi o extensie Mermaid Preview.
- Daca vrei, il pot converti si intr-un SVG sau PNG pentru documentatie/prezentare.
