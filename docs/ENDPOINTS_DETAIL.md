# Endpoint Specifications — Detailed

---

## About

This file contains the **full specification** for every AMS API endpoint.
For a concise route-list overview, see `ENDPOINTS.md`.

---

## Developer Instructions

> **How to update:** When an endpoint is added, modified, or removed:
> 1. Update the route list in **`ENDPOINTS.md`** immediately.
> 2. Update or add the full spec entry here in **this file**.
> 3. Log the change in **`DOC_HISTORY.md`**.
>
> **Keep in sync with:** `ENDPOINTS.md` — the route list there must always match the entries here.
> This file is the source of truth for request/response shapes, query params, body fields, and error codes.

---

## System & Health

<details>
<summary><strong>GET /healthz</strong> — Kubernetes liveness probe</summary>

**Auth:** None  
**Response:** `200 OK`
```json
{
  "status": "ok"
}
```
</details>

<details>
<summary><strong>GET /readyz</strong> — Kubernetes readiness probe</summary>

**Auth:** None  
**Response:** `200 OK` (when DB connection is healthy)
```json
{
  "status": "ready",
  "db": "connected",
  "redis": "connected"
}
```
</details>

<details>
<summary><strong>POST /auth/refresh</strong> — Refresh access token</summary>

**Auth:** None (Bearer token in body)
**Request Body:**
```json
{
  "refresh_token": "string"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```
</details>

---

## Auth

<details>
<summary><strong>POST /auth/register/lecturer</strong> — Register new lecturer</summary>

**Request Body:**
```json
{
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "password": "string",
  "staff_id": "string",
  "department_id": "string"
}
```

**Response:**
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer"
}
```
</details>

<details>
<summary><strong>POST /auth/register/student</strong> — Register new student</summary>

**Request Body:**
```json
{
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "password": "string",
  "matric_num": "string",
  "admission_session": "string (e.g. \"2021/2022\")",
  "department_id": "string"
}
```

**Response:**
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer"
}
```
</details>

<details>
<summary><strong>POST /auth/login</strong> — Login user</summary>

**Request Body:**
```json
{
  "email": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer"
}
```
</details>

<details>
<summary><strong>POST /auth/logout</strong> — Logout current user</summary>

**Auth:** Bearer Token
**Request Body:**
```json
{
  "refresh_token": "string"
}
```

**Response:** 
`204 No Content`
</details>

<details>
<summary><strong>POST /auth/forgot-password</strong> — Request password reset</summary>

**Request Body:**
```json
{
  "email": "string"
}
```

**Response:**
```json
{
  "message": "string"
}
```
</details>

<details>
<summary><strong>POST /auth/reset-password</strong> — Reset password</summary>

**Request Body:**
```json
{
  "token": "string",
  "new_password": "string"
}
```

**Response:**
```json
{
  "message": "string"
}
```
</details>

<details>
<summary><strong>GET /auth/me</strong> — Get current user profile</summary>

**Response:**
```json
{
  "id": "string",
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "role": "string",
  "department": { "id": "string", "name": "string" } | null,
  "matric_num": "string | null",
  "admission_session": "string | null",
  "level_offset": 0 | null,
  "staff_id": "string | null",
  "authorized": true | null
}
```
</details>

<details>
<summary><strong>PATCH /auth/me</strong> — Update current user profile</summary>

**Request Body (all optional):**
```json
{
  "first_name": "string",
  "last_name": "string",
  "phone": "string",
  "avatar": "file (multipart)"
}
```

**Response:**
```json
{
  "message": "string",
  "user": { "id": "string", "first_name": "string", "last_name": "string", "email": "string", ... }
}
```
</details>

<details>
<summary><strong>PATCH /auth/me/password</strong> — Change password</summary>

**Request Body:**
```json
{
  "current_password": "string",
  "new_password": "string",
  "confirm_password": "string"
}
```

**Response:**
```json
{
  "message": "string"
}
```
</details>

<details>
<summary><strong>PATCH /auth/me/student</strong> — Update student-specific fields</summary>

**Request Body (optional):**
```json
{
  "matric_num": "string",
  "admission_session": "string"
}
```

**Response:**
```json
{
  "message": "string",
  "user": { "id": "string", "matric_num": "string", "admission_session": "string" }
}
```
</details>

<details>
<summary><strong>PATCH /auth/me/lecturer</strong> — Update lecturer-specific fields</summary>

**Request Body (optional):**
```json
{
  "staff_id": "string"
}
```

**Response:**
```json
{
  "message": "string",
  "user": { "id": "string", "staff_id": "string" }
}
```
</details>

---

## Student
<details>
<summary><strong>GET /courses</strong> — View all available courses</summary>

**Query Parameters (optional):** `department`, `level`, `search`, `page`, `limit`

**Response:**
```json
{
  "courses": [
    {
      "id": "string",
      "title": "string",
      "code": "string",
      "level": 0,
      "department": "string",
      "lecturer": { "id": "string", "first_name": "string", "last_name": "string" },
      "total_students": 0
    }
  ],
  "pagination": { "page": 0, "limit": 0, "total": 0 }
}
```
</details>

<details>
<summary><strong>GET /courses/{offering_id}</strong> — View single course details</summary>

**Path Parameters:** `offering_id`

**Response:**
```json
{
  "id": "string",
  "title": "string",
  "code": "string",
  "description": "string",
  "level": 0,
  "department": "string",
  "lecturer": { "id": "string", "first_name": "string", "last_name": "string" },
  "is_registered": true,
  "total_students": 0
}
```
</details>

<details>
<summary><strong>POST /courses/{offering_id}/register</strong> — Register for a course</summary>

**Path Parameters:** `offering_id`

**Response:**
```json
{
  "message": "string",
  "status": "pending | approved"
}
```
</details>

<details>
<summary><strong>DELETE /courses/{offering_id}/register</strong> — Drop course registration</summary>

**Path Parameters:** `offering_id`

**Response:**
```json
{
  "message": "string"
}
```
</details>

<details>
<summary><strong>GET /student/courses</strong> — View registered courses</summary>

**Query Parameters (optional):** `status` (`pending` | `approved`), `semester_id`

**Response:**
```json
{
  "courses": [
    {
      "id": "string",
      "title": "string",
      "code": "string",
      "level": 0,
      "status": "pending | approved",
      "lecturer": { "id": "string", "first_name": "string", "last_name": "string" }
    }
  ]
}
```
</details>

<details>
<summary><strong>GET /student/courses/{offering_id}/materials</strong> — View course materials</summary>

**Path Parameters:** `offering_id`  
**Query (optional):** `type` (`note` | `slide` | `resource`)

**Response:**
```json
{
  "materials": [
    {
      "id": "string",
      "title": "string",
      "type": "string",
      "file_url": "string",
      "uploaded_at": "datetime",
      "visibility": "string"
    }
  ]
}
```
</details>

<details>
<summary><strong>GET /student/courses/{offering_id}/tasks</strong> — View tasks for a course</summary>

**Path Parameters:** `offering_id`  
**Query (optional):** `status` (`upcoming` | `ungraded` | `ai_draft` | `ai_approved` | `manually_graded` | `overdue`)

**Response:**
```json
{
  "tasks": [
    {
      "id": "string",
      "title": "string",
      "due_date": "datetime",
      "max_score": 0,
      "submission_status": "string",
      "score": 0
    }
  ]
}
```
</details>

<details>
<summary><strong>GET /student/courses/{offering_id}/tasks/{task_id}</strong> — View specific task</summary>

**Path Parameters:** `offering_id`, `task_id`

**Response:**
```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "due_date": "datetime",
  "total_score": 0,
  "questions": [
    {
      "id": "string",
      "text": "string",
      "type": "string",
      "score": 0,
      "options": ["string"]
    }
  ],
  "submission": { "submitted_at": "datetime", "answers": [] } | null
}
```
</details>

<details>
<summary><strong>POST /student/courses/{offering_id}/tasks/{task_id}/submit</strong> — Submit task</summary>

**Path Parameters:** `offering_id`, `task_id`  
**Body (multipart):** `answers[]` (with appropriate fields based on question type)

**Response:**
```json
{
  "message": "string",
  "submission": { "id": "string", "submitted_at": "datetime", "answers_count": 0 }
}
```
</details>

<details>
<summary><strong>GET /student/courses/{offering_id}/grades</strong> — View grades for a course</summary>

**Path Parameters:** `offering_id`

**Response:**
```json
{
  "grades": [
    {
      "task_id": "string",
      "task_title": "string",
      "score": 0,
      "max_score": 0,
      "graded_at": "datetime",
      "feedback": "string"
    }
  ],
  "summary": {
    "total_score": 0,
    "average": 0,
    "grade": "string"
  }
}
```
</details>

<details>
<summary><strong>GET /student/courses/{offering_id}/announcements</strong> — View course announcements</summary>

**Path Parameters:** `offering_id`  
**Query (optional):** `viewed`, `pinned`, `page`, `limit`

**Response:**
```json
{
  "announcements": [
    {
      "id": "string",
      "title": "string",
      "body": "string",
      "created_at": "datetime",
      "lecturer": { "id": "string", "first_name": "string", "last_name": "string" },
      "viewed": true
    }
  ],
  "pagination": { "page": 0, "limit": 0, "total": 0 }
}
```
</details>

<details>
<summary><strong>GET /student/courses/{offering_id}/announcements/{announcement_id}</strong> — View announcement details</summary>

**Path Parameters:** `offering_id`, `announcement_id`

**Response:**
```json
{
  "id": "string",
  "title": "string",
  "body": "string",
  "created_at": "datetime",
  "lecturer": {
    "id": "string",
    "first_name": "string",
    "last_name": "string",
    "name": "string"
  },
  "viewed": true
}
```
</details>

<details>
<summary><strong>PATCH /student/courses/{offering_id}/announcements/{announcement_id}/viewed</strong> — Mark announcement as viewed</summary>

**Path Parameters:** `offering_id`, `announcement_id`

**Response:** `204 No Content`
</details>

<details>
<summary><strong>GET /student/courses/{offering_id}/attendance</strong> — View personal attendance</summary>

**Path Parameters:** `offering_id`

**Response:**
```json
{
  "attendance": [
    {
      "session_id": "string",
      "session_date": "datetime",
      "status": "present | absent"
    }
  ],
  "summary": {
    "total": 0,
    "present": 0,
    "absent": 0,
    "percentage": 0
  }
}
```
</details>

<details>
<summary><strong>GET /student/courses/{offering_id}/sessions</strong> — View course sessions</summary>

**Path Parameters:** `offering_id`  
**Query (optional):** `status` (`upcoming` | `completed` | `cancelled`)

**Response:**
```json
{
  "sessions": [
    {
      "id": "string",
      "title": "string",
      "scheduled_at": "datetime",
      "venue": "string",
      "status": "string",
      "attended": true | null,
      "lecturer": { "id": "string", "first_name": "string", "last_name": "string" }
    }
  ]
}
```
</details>

<details>
<summary><strong>GET /student/courses/{offering_id}/sessions/{session_id}</strong> — View specific session</summary>

**Path Parameters:** `offering_id`, `session_id`

**Response:** `200 OK`
```json
{
  "session": {
    "id": "string",
    "offering_id": "string",
    "title": "string",
    "scheduled_at": "datetime",
    "venue": "string",
    "status": "upcoming | completed | cancelled",
    "notes": "string | null",
    "lecturer": { "id": "string", "first_name": "string", "last_name": "string" }
  },
  "attendance": {
    "marked": true,
    "attended": true
  }
}
```
</details>

<details>
<summary><strong>GET /student/analytics</strong> — View overall analytics (planned)</summary>
</details>

<details>
<summary><strong>GET /student/courses/{offering_id}/analytics</strong> — View course analytics (planned)</summary>
</details>

<details>
<summary><strong>POST /student/courses/{offering_id}/ai-tutor</strong> — Chat with AI tutor (planned)</summary>

**Path Parameters:** `offering_id`

**Request Body:**
```json
{
  "message": "string",
  "context_material_id": "string (uuid) | null",
  "history": [{ "role": "user | assistant", "content": "string" }]
}
```

**Response:**
```json
{
  "reply": "string"
}
```
</details>


---

## Lecturer
<details>
<summary><strong>GET /lecturer/courses</strong> — View all courses assigned to the lecturer</summary>

**Response:**
```json
{
  "courses": [
    {
      "id": "string",
      "title": "string",
      "code": "string",
      "level": 0,
      "total_students": 0,
      "is_active": true,
      "lecturers": [{ "id": "string", "name": "string" }]
    }
  ]
}
```
</details>

<details>
<summary><strong>GET /lecturer/courses/{offering_id}</strong> — View details of an assigned course</summary>

**Path Parameters:** `offering_id`

**Response:**
```json
{
  "id": "string",
  "title": "string",
  "code": "string",
  "level": 0,
  "lecturers": [{ "id": "string", "name": "string" }],
  "description": "string",
  "department": "string",
  "total_students": 0,
  "sessions": 0,
  "tasks_count": 0
}
```
</details>

<details>
<summary><strong>GET /lecturer/courses/{offering_id}/students</strong> — View all students in a course</summary>

**Path Parameters:** `offering_id`  
**Query Parameters (optional):** `status` (enum: `pending` | `approved`)

**Response:**
```json
{
  "students": [
    {
      "id": "string",
      "first_name": "string",
      "last_name": "string",
      "email": "string",
      "registration_status": "pending | approved"
    }
  ]
}
```
</details>

<details>
<summary><strong>PATCH /lecturer/courses/{offering_id}/students/{student_id}/approve</strong> — Approve or reject student registration</summary>

**Path Parameters:** `offering_id`, `student_id`

**Request Body:**
```json
{
  "status": "approved | rejected"
}
```

**Response:**
```json
{
  "message": "string"
}
```
</details>

<details>
<summary><strong>GET /lecturer/courses/{offering_id}/materials</strong> — View all materials for a course</summary>

**Path Parameters:** `offering_id`

**Response:**
```json
{
  "materials": [
    {
      "id": "string",
      "offering_id": "string",
      "uploaded_by": "string",
      "title": "string",
      "type": "string",
      "file_url": "string",
      "visibility": "string",
      "indexed": true,
      "indexed_at": "datetime",
      "created_at": "datetime"
    }
  ]
}
```
</details>

<details>
<summary><strong>POST /lecturer/courses/{offering_id}/materials</strong> — Upload course material</summary>

**Path Parameters:** `offering_id`  
**Body (multipart/form-data):**
- `title`: string
- `type`: enum (`note` | `slide` | `resource`)
- `file`: file
- `visibility`: enum (`students_only` | `ai_only` | `both`)
  - `students_only`: visible to enrolled students only (cannot be AI-indexed)
  - `ai_only`: available to the AI tutor only, not visible to students
  - `both`: visible to students AND the AI tutor

**Response:**
```json
{
  "message": "string",
  "material": {
    "id": "string",
    "title": "string",
    "type": "string",
    "file_url": "string",
    "visibility": "string",
    "uploaded_at": "datetime"
  }
}
```
</details>

<details>
<summary><strong>PATCH /lecturer/courses/{offering_id}/materials/{material_id}</strong> — Update material metadata</summary>

**Path Parameters:** `offering_id`, `material_id`

**Request Body (all optional):**
```json
{
  "title": "string",
  "visibility": "students_only | ai_only | both"
}
```

**Response:**
```json
{
  "message": "string",
  "material": { "id": "string", "title": "string", "visibility": "string" }
}
```
</details>

<details>
<summary><strong>DELETE /lecturer/courses/{offering_id}/materials/{material_id}</strong> — Delete course material</summary>

**Path Parameters:** `offering_id`, `material_id`

**Response:**
```json
{
  "message": "string"
}
```
</details>

<details>
<summary><strong>POST /lecturer/courses/{offering_id}/materials/{material_id}/index</strong> — Trigger AI indexing for material</summary>

**Path Parameters:** `offering_id`, `material_id`

**Response:**
```json
{
  "message": "string",
  "material": {
    "id": "string",
    "indexed": true,
    "indexed_at": "datetime"
  }
}
```
</details>

<details>
<summary><strong>POST /lecturer/courses/{offering_id}/tasks</strong> — Create a new task</summary>

**Path Parameters:** `offering_id`

**Request Body:**
```json
{
  "title": "string",
  "description": "string (optional)",
  "due_date": "datetime",
  "session_id": "string (optional)",
  "questions": [
    {
      "text": "string",
      "type": "mcq | free_text | document_upload",
      "score": 0,
      "options": ["string"]   // required only for mcq
    }
  ]
}
```

**Response:**
```json
{
  "message": "string",
  "task": {
    "id": "string",
    "title": "string",
    "due_date": "datetime",
    "question_count": 0
  }
}
```
</details>

<details>
<summary><strong>GET /lecturer/courses/{offering_id}/tasks</strong> — View all tasks for a course</summary>

**Path Parameters:** `offering_id`

**Response:**
```json
{
  "tasks": [
    {
      "id": "string",
      "title": "string",
      "due_date": "datetime",
      "question_count": 0,
      "total_score": 0,
      "ai_grading": true
    }
  ]
}
```
</details>

<details>
<summary><strong>GET /lecturer/courses/{offering_id}/tasks/{task_id}</strong> — View full task details</summary>

**Path Parameters:** `offering_id`, `task_id`

**Response:**
```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "due_date": "datetime",
  "total_score": 0,
  "ai_grading": true,
  "marking_guide_url": "string | null",
  "questions": [
    {
      "id": "string",
      "text": "string",
      "type": "string",
      "score": 0,
      "options": ["string"]   // only for mcq
    }
  ]
}
```
</details>

<details>
<summary><strong>PATCH /lecturer/courses/{offering_id}/tasks/{task_id}</strong> — Update task</summary>

**Path Parameters:** `offering_id`, `task_id`

**Request Body (all optional):**
```json
{
  "title": "string",
  "description": "string",
  "due_date": "datetime",
  "session_id": "string | null"
}
```

**Response:**
```json
{
  "message": "string",
  "task": { "id": "string", "title": "string", "due_date": "datetime" }
}
```
</details>

<details>
<summary><strong>DELETE /lecturer/courses/{offering_id}/tasks/{task_id}</strong> — Delete task</summary>

**Path Parameters:** `offering_id`, `task_id`

Note: Deleting a task will also permanently delete all associated student submissions and grades.

**Response:**
```json
{
  "message": "string"
}
```
</details>

<details>
<summary><strong>POST /lecturer/courses/{offering_id}/tasks/{task_id}/questions</strong> — Add question to task</summary>

**Path Parameters:** `offering_id`, `task_id`

**Request Body:**
```json
{
  "text": "string",
  "type": "mcq | free_text | document_upload",
  "score": 0,
  "options": ["string"]   // required only for mcq
}
```

**Response:**
```json
{
  "message": "string",
  "question": { "id": "string", "text": "string", "type": "string", "score": 0 }
}
```
</details>

<details>
<summary><strong>PATCH /lecturer/courses/{offering_id}/tasks/{task_id}/questions/{question_id}</strong> — Update question</summary>

**Path Parameters:** `offering_id`, `task_id`, `question_id`

**Request Body (all optional):**
```json
{
  "text": "string",
  "score": 0,
  "options": ["string"]
}
```

**Response:**
```json
{
  "message": "string",
  "question": { "id": "string", "text": "string", "score": 0 }
}
```
</details>

<details>
<summary><strong>DELETE /lecturer/courses/{offering_id}/tasks/{task_id}/questions/{question_id}</strong> — Delete question</summary>

**Path Parameters:** `offering_id`, `task_id`, `question_id`

**Response:**
```json
{
  "message": "string"
}
```
</details>

<details>
<summary><strong>POST /lecturer/courses/{offering_id}/tasks/{task_id}/marking-guide</strong> — Upload marking guide</summary>

**Path Parameters:** `offering_id`, `task_id`  
**Body (multipart):** `markingGuide` (file)

**Response:**
```json
{
  "message": "string",
  "marking_guide_url": "string"
}
```
</details>

<details>
<summary><strong>PATCH /lecturer/courses/{offering_id}/tasks/{task_id}/ai-grading</strong> — Enable/Disable AI grading</summary>

**Path Parameters:** `offering_id`, `task_id`

**Request Body:**
```json
{
  "enabled": true
}
```

**Response:**
```json
{
  "message": "string",
  "ai_grading": true
}
```
</details>

<details>
<summary><strong>GET /lecturer/courses/{offering_id}/tasks/{task_id}/submissions</strong> — View submissions for a task</summary>

**Path Parameters:** `offering_id`, `task_id`  
**Query (optional):** `graded` (boolean)

**Response:**
```json
{
  "submissions": [
    {
      "id": "string",
      "student": { "id": "string", "name": "string" },
      "submitted_at": "datetime",
      "total_score": 0,
      "grading_status": "ungraded | ai_draft | ai_approved | manually_graded"
    }
  ]
}
```
</details>

<details>
<summary><strong>GET /lecturer/courses/{offering_id}/tasks/{task_id}/submissions/{submission_id}</strong> — View specific submission</summary>

**Path Parameters:** `offering_id`, `task_id`, `submission_id`

**Response:**
```json
{
  "student": { "id": "string", "name": "string", "matric_num": "string" },
  "submitted_at": "datetime",
  "total_score": 0,
  "grading_status": "ungraded | ai_draft | ai_approved | manually_graded",
  "answers": [
    {
      "question_id": "string",
      "question_text": "string",
      "type": "string",
      "score": 0,
      "max_score": 0,
      // fields vary by type (selectedOption, text, fileUrl, feedback, etc.)
    }
  ]
}
```
</details>

<details>
<summary><strong>PATCH /lecturer/courses/{offering_id}/tasks/{task_id}/submissions/{submission_id}/grade</strong> — Grade a submission</summary>

**Path Parameters:** `offering_id`, `task_id`, `submission_id`

**Request Body:**
```json
{
  "grades": [
    {
      "question_id": "string",
      "score": 0,
      "feedback": "string (optional)"
    }
  ]
}
```

**Response:**
```json
{
  "message": "string",
  "submission": { "id": "string", "total_score": 0, "graded_at": "datetime" }
}
```
</details>

<details>
<summary><strong>POST /lecturer/courses/{offering_id}/tasks/{task_id}/submissions/approve-ai-grades</strong> — Approve AI draft grades</summary>

**Path Parameters:** `offering_id`, `task_id`

**Request Body (optional):**
```json
{
  "submission_ids": ["string"]
}
```

**Response:**
```json
{
  "message": "string",
  "approved": 0
}
```
</details>

<details>
<summary><strong>POST /lecturer/courses/{offering_id}/sessions</strong> — Schedule a new class session</summary>

**Path Parameters:** `offering_id`

**Request Body:**
```json
{
  "title": "string",
  "scheduled_at": "datetime",
  "venue": "string (optional)",
  "notes": "string (optional)"
}
```

**Response:**
```json
{
  "message": "string",
  "session": {
    "id": "string",
    "title": "string",
    "scheduled_at": "datetime",
    "venue": "string",
    "status": "string"
  }
}
```
</details>

<details>
<summary><strong>GET /lecturer/courses/{offering_id}/sessions</strong> — View all sessions for a course</summary>

**Path Parameters:** `offering_id`  
**Query (optional):** `status` (`upcoming` | `completed` | `cancelled`)

**Response:** `200 OK`
```json
{
  "sessions": [
    {
      "id": "string",
      "title": "string",
      "scheduled_at": "datetime",
      "venue": "string",
      "status": "string",
      "attendance_count": 0
    }
  ]
}
```
</details>

<details>
<summary><strong>GET /lecturer/courses/{offering_id}/sessions/{session_id}</strong> — View session details with attendance</summary>

**Path Parameters:** `offering_id`, `session_id`

**Response:** `200 OK`
```json
{
  "id": "string",
  "offering_id": "string",
  "lecturer_id": "string",
  "title": "string",
  "scheduled_at": "datetime",
  "venue": "string",
  "status": "upcoming | completed | cancelled",
  "notes": "string | null",
  "is_owner": true,
  "attendance": [
    { "student_id": "string", "name": "string", "status": "present | absent" }
  ],
  "tasks": [
    { "task_id": "string", "title": "string", "submissions_count": 0 }
  ]
}
```
</details>

<details>
<summary><strong>PATCH /lecturer/courses/{offering_id}/sessions/{session_id}</strong> — Update session</summary>

**Path Parameters:** `offering_id`, `session_id`

**Request Body (all optional):**
```json
{
  "title": "string",
  "scheduled_at": "datetime",
  "venue": "string",
  "notes": "string",
  "status": "upcoming | completed | cancelled"
}
```

**Response:** `200 OK`
```json
{
  "message": "Session updated"
}
```
</details>

<details>
<summary><strong>DELETE /lecturer/courses/{offering_id}/sessions/{session_id}</strong> — Delete session</summary>

**Path Parameters:** `offering_id`, `session_id`

**Response:** `200 OK`
```json
{
  "message": "Session deleted"
}
```
</details>

<details>
<summary><strong>POST /lecturer/courses/{offering_id}/sessions/{session_id}/attendance</strong> — Mark attendance</summary>

**Path Parameters:** `offering_id`, `session_id`

**Request Body:**
```json
{
  "records": [
    { "student_id": "string", "status": "present | absent" }
  ]
}
```

**Response:**
```json
{
  "message": "string",
  "marked": 0
}
```
</details>

<details>
<summary><strong>GET /lecturer/courses/{offering_id}/gradebook</strong> — View course gradebook</summary>

**Path Parameters:** `offering_id`

**Response:**
```json
{
  "students": [
    {
      "student_id": "string",
      "name": "string",
      "tasks": [{ "task_id": "string", "title": "string", "score": 0, "max_score": 0 }],
      "total_score": 0,
      "average": 0,
      "grade": "string"
    }
  ]
}
```
</details>

<details>
<summary><strong>PATCH /lecturer/courses/{offering_id}/gradebook/{student_id}</strong> — Manually update student grade</summary>

**Path Parameters:** `offering_id`, `student_id`

**Request Body (optional):**
```json
{
  "notes": "string",
  "manual_grade": "string"
}
```

**Response:**
```json
{
  "message": "string"
}
```
</details>

<details>
<summary><strong>POST /lecturer/courses/{offering_id}/announcements</strong> — Post announcement</summary>

**Path Parameters:** `offering_id`

**Request Body:**
```json
{
  "title": "string",
  "body": "string",
  "pinned": true
}
```

**Response:**
```json
{
  "message": "string",
  "announcement": {
    "id": "string",
    "title": "string",
    "body": "string",
    "created_at": "datetime"
  }
}
```
</details>

<details>
<summary><strong>GET /lecturer/courses/{offering_id}/announcements</strong> — View announcements</summary>

**Path Parameters:** `offering_id`  
**Query (optional):** `pinned`, `page`, `limit`

**Response:**
```json
{
  "announcements": [
    {
      "id": "string",
      "title": "string",
      "body": "string",
      "pinned": true,
      "created_at": "datetime"
    }
  ],
  "pagination": { "page": 0, "limit": 0, "total": 0 }
}
```
</details>

<details>
<summary><strong>GET /lecturer/courses/{offering_id}/announcements/{announcement_id}</strong> — View specific announcement</summary>

**Path Parameters:** `offering_id`, `announcement_id`

**Response:** `200 OK`
```json
{
  "id": "string",
  "offering_id": "string",
  "lecturer_id": "string",
  "title": "string",
  "body": "string",
  "pinned": true,
  "created_at": "datetime",
  "updated_at": "datetime"
}
```
</details>

<details>
<summary><strong>PATCH /lecturer/courses/{offering_id}/announcements/{announcement_id}</strong> — Update announcement</summary>

**Path Parameters:** `offering_id`, `announcement_id`

**Request Body (all optional):**
```json
{
  "title": "string",
  "body": "string",
  "pinned": true
}
```

**Response:** `200 OK`
```json
{
  "id": "string",
  "offering_id": "string",
  "lecturer_id": "string",
  "title": "string",
  "body": "string",
  "pinned": true,
  "created_at": "datetime",
  "updated_at": "datetime"
}
```
</details>

<details>
<summary><strong>DELETE /lecturer/courses/{offering_id}/announcements/{announcement_id}</strong> — Delete announcement</summary>

**Path Parameters:** `offering_id`, `announcement_id`

**Response:** `200 OK`
```json
{
  "message": "Announcement deleted"
}
```
</details>

<details>
<summary><strong>GET /lecturer/courses/{offering_id}/analytics</strong> — View course analytics (planned)</summary>

**Path Parameters:** `offering_id`
</details>

<details>
<summary><strong>GET /lecturer/analytics</strong> — View overall lecturer analytics (planned)</summary>
</details>

<details>
<summary><strong>PATCH /lecturer/courses/{offering_id}/ai-tutor/rules</strong> — Set or update AI tutor instructions for a course</summary>

**Path Parameters:** `offering_id`

**Request Body:**
```json
{
  "rules": "string (freeform instructions for the AI)"
}
```

**Response:**
```json
{
  "message": "string",
  "rules": "string"
}
```
</details>

<details>
<summary><strong>POST /lecturer/courses/{offering_id}/ai-tutor</strong> — Chat with AI tutor as a lecturer</summary>

**Path Parameters:** `offering_id`

**Request Body:**
```json
{
  "message": "string",
  "context_material_id": "string (uuid) | null",
  "history": [{ "role": "user | assistant", "content": "string" }]
}
```

**Response:**
```json
{
  "reply": "string"
}
```
</details>
---

## HOD

<details>
<summary><strong>GET /hod/students</strong> — View all students in the department</summary>

**Query Parameters (optional):** `search`, `page`, `limit`

**Response:**
```json
{
  "users": [
    { "id": "string", "first_name": "string", "last_name": "string", "email": "string", "role": "student" }
  ],
  "pagination": { "page": 0, "limit": 0, "total": 0 }
}
```
</details>

<details>
<summary><strong>GET /hod/lecturers</strong> — View all lecturers in the department</summary>

**Query Parameters (optional):** `search`, `page`, `limit`

**Response:** Same structure as `/hod/students`
</details>

<details>
<summary><strong>GET /hod/students/{student_id}</strong> — View specific student details</summary>

**Path Parameters:** `student_id`

**Response:**
```json
{
  "id": "string",
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "role": "student",
  "matric_num": "string",
  "admission_session": "string",
  "level_offset": 0,
  "department": { "id": "string", "name": "string" },
  "offerings": [
    {
      "id": "string",
      "course_title": "string",
      "academic_session": "string",
      "semester": "string",
      "status": "string"
    }
  ]
}
```
</details>

<details>
<summary><strong>GET /hod/lecturers/{lecturer_id}</strong> — View specific lecturer details</summary>

**Path Parameters:** `lecturer_id`

**Response:**
```json
{
  "id": "string",
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "role": "lecturer",
  "staff_id": "string",
  "authorized": true,
  "department": { "id": "string", "name": "string" },
  "offerings": [
    {
      "id": "string",
      "course_title": "string",
      "academic_session": "string",
      "semester": "string",
      "is_active": true
    }
  ]
}
```
</details>

<details>
<summary><strong>PATCH /hod/students/{student_id}/level-offset</strong> — Update student's level offset</summary>

**Path Parameters:** `student_id`

**Request Body:**
```json
{
  "level_offset": 0
}
```

**Response:**
```json
{
  "message": "string",
  "student": {
    "id": "string",
    "level_offset": 0,
    "level": 0
  }
}
```
</details>

<details>
<summary><strong>POST /hod/courses</strong> — Create a new course definition</summary>

**Request Body:**
```json
{
  "title": "string",
  "code": "string (e.g. CSC101)",
  "description": "string (optional)",
  "units": 0
}
```

**Response:**
```json
{
  "message": "string",
  "course": {
    "id": "string",
    "title": "string",
    "code": "string",
    "units": 0,
    "department": { "id": "string", "name": "string" }
  }
}
```
</details>

<details>
<summary><strong>GET /hod/courses</strong> — View all course definitions in the department</summary>

**Query Parameters (optional):** `search`, `page`, `limit`

**Response:**
```json
{
  "courses": [
    {
      "id": "string",
      "title": "string",
      "code": "string",
      "units": 0,
      "total_offerings": 0,
      "active_offering": true
    }
  ],
  "pagination": { "page": 0, "limit": 0, "total": 0 }
}
```
</details>

<details>
<summary><strong>GET /hod/courses/{course_id}</strong> — View course definition details</summary>

**Path Parameters:** `course_id`

**Response:**
```json
{
  "id": "string",
  "title": "string",
  "code": "string",
  "description": "string",
  "units": 0,
  "department": { "id": "string", "name": "string" },
  "offerings": [
    {
      "id": "string",
      "academic_session": "string",
      "semester": "string",
      "is_active": true,
      "lecturers": [
        {
          "id": "string",
          "name": "string"
        }
      ]
    }
  ]
}
```
</details>

<details>
<summary><strong>PATCH /hod/courses/{course_id}</strong> — Update course definition</summary>

**Path Parameters:** `course_id`

**Request Body (all optional):**
```json
{
  "title": "string",
  "description": "string",
  "units": 0
}
```

**Response:**
```json
{
  "message": "string",
  "course": {
    "id": "string",
    "title": "string",
    "code": "string",
    "units": 0
  }
}
```
</details>

<details>
<summary><strong>DELETE /hod/courses/{course_id}</strong> — Delete course definition</summary>

**Path Parameters:** `course_id`

**Response:**
```json
{
  "message": "string"
}
```
</details>

<details>
<summary><strong>POST /hod/courses/{course_id}/offerings</strong> — Create course offering</summary>

**Path Parameters:** `course_id`

**Request Body:**
```json
{
  "semester_id": "string",
  "lecturer_id": "string (optional)"
}
```

**Response:**
```json
{
  "message": "string",
  "offering": {
    "id": "string",
    "course_id": "string",
    "academic_session": "string",
    "semester": "string",
    "is_active": true,
    "lecturers": [{ "id": "string", "first_name": "string", "last_name": "string" }]
  }
}
```
</details>

<details>
<summary><strong>GET /hod/courses/{course_id}/offerings</strong> — View all offerings for a course</summary>

**Path Parameters:** `course_id`  
**Query Parameters (optional):** `semester_id`, `isActive`

**Response:**
```json
{
  "offerings": [
    {
      "id": "string",
      "academic_session": "string",
      "semester": "string",
      "is_active": true,
      "total_students": 0,
      "lecturers": [{ "id": "string", "first_name": "string", "last_name": "string" }]
    }
  ]
}
```
</details>

<details>
<summary><strong>GET /hod/courses/{course_id}/offerings/{offering_id}</strong> — View specific offering details</summary>

**Path Parameters:** `course_id`, `offering_id`

**Response:**
```json
{
  "id": "string",
  "course": { "id": "string", "title": "string", "code": "string" },
  "academic_session": "string",
  "semester": "string",
  "is_active": true,
  "lecturers": [{ "id": "string", "first_name": "string", "last_name": "string", "staff_id": "string" }],
  "total_students": 0,
  "total_sessions": 0,
  "total_tasks": 0
}
```
</details>

<details>
<summary><strong>PATCH /hod/courses/{course_id}/offerings/{offering_id}/activate</strong> — Activate/Deactivate offering</summary>

**Path Parameters:** `course_id`, `offering_id`

**Request Body:**
```json
{
  "is_active": true
}
```

**Response:**
```json
{
  "message": "string",
  "offering": { "id": "string", "is_active": true }
}
```
</details>

<details>
<summary><strong>POST /hod/courses/{course_id}/offerings/{offering_id}/assign</strong> — Assign lecturer to offering</summary>

**Path Parameters:** `course_id`, `offering_id`

**Request Body:**
```json
{
  "lecturer_id": "string"
}
```

**Response:**
```json
{
  "message": "string",
  "offering": {
    "id": "string",
    "lecturers": [{ "id": "string", "first_name": "string", "last_name": "string" }]
  }
}
```
</details>

<details>
<summary><strong>DELETE /hod/courses/{course_id}/offerings/{offering_id}/assign/{lecturer_id}</strong> — Unassign lecturer from offering</summary>

**Path Parameters:** `course_id`, `offering_id`, `lecturer_id`

**Response:**
```json
{
  "message": "string"
}
```
</details>

---


## Admin

<details>
<summary><strong>POST /admin/staff/authorize</strong> — Bulk authorize lecturer accounts</summary>

**Request Body:**
```json
{
  "user_ids": ["string"]
}
```

**Response:**
```json
{
  "message": "string",
  "authorized": 0,
  "failed": [
    { "user_id": "string", "reason": "string" }
  ]
}
```
</details>

<details>
<summary><strong>POST /admin/faculties</strong> — Create a new faculty</summary>

**Request Body:**
```json
{
  "name": "string (e.g. \"Faculty of Science\")",
  "code": "string (e.g. \"FOS\")"
}
```

**Response:**
```json
{
  "message": "string",
  "faculty": {
    "id": "string",
    "name": "string",
    "code": "string"
  }
}
```
</details>

<details>
<summary><strong>GET /admin/faculties</strong> — View all faculties</summary>

**Response:**
```json
{
  "faculties": [
    {
      "id": "string",
      "name": "string",
      "code": "string",
      "total_departments": 0
    }
  ]
}
```
</details>

<details>
<summary><strong>PATCH /admin/faculties/{faculty_id}</strong> — Update a faculty</summary>

**Path Parameters:** `faculty_id`

**Request Body (all optional):**
```json
{
  "name": "string",
  "code": "string"
}
```

**Response:**
```json
{
  "message": "string",
  "faculty": {
    "id": "string",
    "name": "string",
    "code": "string"
  }
}
```
</details>

<details>
<summary><strong>DELETE /admin/faculties/{faculty_id}</strong> — Delete a faculty</summary>

**Path Parameters:** `faculty_id`

**Response:**
```json
{
  "message": "string"
}
```
</details>

<details>
<summary><strong>POST /admin/faculties/{faculty_id}/departments</strong> — Create a department</summary>

**Path Parameters:** `faculty_id`

**Request Body:**
```json
{
  "name": "string (e.g. \"Computer Science\")",
  "code": "string (e.g. \"CSC\")"
}
```

**Response:**
```json
{
  "message": "string",
  "department": {
    "id": "string",
    "name": "string",
    "code": "string",
    "faculty": { "id": "string", "name": "string" }
  }
}
```
</details>

<details>
<summary><strong>GET /admin/faculties/{faculty_id}/departments</strong> — View all departments in a faculty</summary>

**Path Parameters:** `faculty_id`

**Response:**
```json
{
  "departments": [
    {
      "id": "string",
      "name": "string",
      "code": "string",
      "hod": { "id": "string", "name": "string" } | null,
      "total_courses": 0
    }
  ]
}
```
</details>

<details>
<summary><strong>GET /admin/faculties/{faculty_id}/departments/{department_id}</strong> — View specific department details</summary>

**Path Parameters:** `faculty_id`, `department_id`

**Response:**
```json
{
  "id": "string",
  "name": "string",
  "code": "string",
  "faculty": { "id": "string", "name": "string" },
  "hod": { "id": "string", "first_name": "string", "last_name": "string" } | null,
  "total_courses": 0,
  "total_students": 0,
  "total_lecturers": 0
}
```
</details>

<details>
<summary><strong>PATCH /admin/faculties/{faculty_id}/departments/{department_id}</strong> — Update a department</summary>

**Path Parameters:** `faculty_id`, `department_id`

**Request Body (all optional):**
```json
{
  "name": "string",
  "code": "string"
}
```

**Response:**
```json
{
  "message": "string",
  "department": {
    "id": "string",
    "name": "string",
    "code": "string"
  }
}
```
</details>

<details>
<summary><strong>DELETE /admin/faculties/{faculty_id}/departments/{department_id}</strong> — Delete a department</summary>

**Path Parameters:** `faculty_id`, `department_id`

**Response:**
```json
{
  "message": "string"
}
```
</details>

<details>
<summary><strong>POST /admin/departments/{department_id}/hod</strong> — Assign HOD to department</summary>

**Path Parameters:** `department_id`

**Request Body:**
```json
{
  "user_id": "string"
}
```

**Response:**
```json
{
  "message": "string"
}
```
</details>

<details>
<summary><strong>PATCH /admin/departments/{department_id}/hod</strong> — Replace current HOD</summary>

**Path Parameters:** `department_id`

**Request Body:**
```json
{
  "user_id": "string"
}
```

**Response:**
```json
{
  "message": "string"
}
```
</details>

<details>
<summary><strong>GET /admin/users</strong> — View all users across the system</summary>

**Query Parameters (optional):**  
`role` (enum: `student` | `lecturer` | `hod` | `admin`), `department`, `search`, `page`, `limit`

**Response:**
```json
{
  "users": [
    {
      "id": "string",
      "first_name": "string",
      "last_name": "string",
      "email": "string",
      "role": "string",
      "department": "string"
    }
  ],
  "pagination": {
    "page": 0,
    "limit": 0,
    "total": 0
  }
}
```
</details>

<details>
<summary><strong>POST /admin/academic-sessions</strong> — Create academic session with semesters</summary>

**Request Body:**
```json
{
  "name": "string (e.g. \"2024/2025\")",
  "semesters": [
    {
      "name": "first | second",
      "start_date": "datetime",
      "end_date": "datetime"
    }
  ]
}
```

**Response:**
```json
{
  "message": "string",
  "session": {
    "id": "string",
    "name": "string",
    "semesters": [
      {
        "id": "string",
        "name": "string",
        "start_date": "datetime",
        "end_date": "datetime",
        "is_active": false
      }
    ]
  }
}
```
</details>

<details>
<summary><strong>GET /admin/academic-sessions</strong> — Get all academic sessions</summary>

**Response:**
```json
{
  "sessions": [
    {
      "id": "string",
      "name": "string",
      "created_at": "datetime",
      "semesters": [
        {
          "id": "string",
          "name": "string",
          "start_date": "datetime",
          "end_date": "datetime",
          "is_active": true
        }
      ]
    }
  ]
}
```
</details>

<details>
<summary><strong>GET /admin/academic-sessions/{session_id}</strong> — Get single academic session</summary>

**Path Parameters:** `session_id`

**Response:**
```json
{
  "id": "string",
  "name": "string",
  "created_at": "datetime",
  "semesters": [
    {
      "id": "string",
      "name": "string",
      "start_date": "datetime",
      "end_date": "datetime",
      "is_active": true
    }
  ]
}
```
</details>

<details>
<summary><strong>PATCH /admin/academic-sessions/{session_id}</strong> — Update academic session</summary>

**Path Parameters:** `session_id`

**Request Body (optional):**
```json
{
  "name": "string (e.g. \"2024/2025\")"
}
```

**Response:**
```json
{
  "message": "string",
  "session": {
    "id": "string",
    "name": "string"
  }
}
```
</details>

<details>
<summary><strong>DELETE /admin/academic-sessions/{session_id}</strong> — Delete academic session</summary>

**Path Parameters:** `session_id`

**Response:**
```json
{
  "message": "string"
}
```
</details>

<details>
<summary><strong>PATCH /admin/academic-sessions/{session_id}/semesters/{semester_id}/activate</strong> — Activate a semester</summary>

**Path Parameters:** `session_id`, `semester_id`

**Response:**
```json
{
  "message": "string",
  "semester": {
    "id": "string",
    "name": "string",
    "is_active": true
  }
}
```
</details>

<details>
<summary><strong>PATCH /admin/academic-sessions/{session_id}/semesters/{semester_id}</strong> — Update a semester</summary>

**Path Parameters:** `session_id`, `semester_id`

**Request Body (all optional):**
```json
{
  "start_date": "datetime",
  "end_date": "datetime"
}
```

**Response:**
```json
{
  "message": "string",
  "semester": {
    "id": "string",
    "start_date": "datetime",
    "end_date": "datetime"
  }
}
```
</details>

<details>
<summary><strong>DELETE /admin/academic-sessions/{session_id}/semesters/{semester_id}</strong> — Delete a semester</summary>

**Path Parameters:** `session_id`, `semester_id`

**Response:**
```json
{
  "message": "string"
}
```
</details>

---

## Shared

<details>
<summary><strong>GET /materials/{material_id}/download</strong> — Download material file</summary>

**Path Parameters:** `material_id`  
**Response:** Binary file stream or redirect to file URL
</details>

<details>
<summary><strong>GET /notifications</strong> — Get notifications for current user</summary>

**Query Parameters (optional):** `read` (boolean), `page`, `limit`

**Response:**
```json
{
  "notifications": [
    {
      "id": "string",
      "message": "string",
      "type": "string",
      "read": false,
      "created_at": "datetime",
      "link": "string"
    }
  ],
  "unread_count": 0
}
```
</details>

<details>
<summary><strong>PATCH /notifications/read</strong> — Mark specific notifications as read</summary>

**Request Body:**
```json
{
  "notification_ids": ["string"]
}
```

**Response:**
```json
{
  "marked": 0
}
```
</details>

<details>
<summary><strong>PATCH /notifications/read-all</strong> — Mark all in-app notifications as read</summary>

**Response:**
```json
{
  "marked": 0
}
```
</details>

<details>
<summary><strong>POST /notifications/device-tokens</strong> — Register a push notification token</summary>

**Request Body:**
```json
{
  "token": "string",
  "platform": "string"
}
```

**Response:**
```json
{
  "id": "string",
  "token": "string",
  "platform": "string",
  "is_active": true
}
```
</details>

<details>
<summary><strong>DELETE /notifications/device-tokens/{token}</strong> — Deregister a push token</summary>

**Path Parameters:** `token`

**Response:** `204 No Content`
</details>

<details>
<summary><strong>GET /users</strong> — List shared users</summary>

**Query Parameters (optional):**  
`role` (string), `department` (UUID), `search` (string), `is_active` (boolean), `is_authorized` (boolean), `admission_session` (string), `level_offset` (integer), `page` (integer), `limit` (integer)

**Response:**
```json
{
  "users": [
    {
      "id": "string",
      "first_name": "string",
      "last_name": "string",
      "roles": ["string"],
      "email": "string",
      "department": { "id": "string", "name": "string" } | null,
      "avatar": "string" | null
    }
  ],
  "pagination": {
    "page": 0,
    "limit": 0,
    "total": 0
  }
}
```
</details>

<details>
<summary><strong>GET /academic-sessions</strong> — Get all academic sessions</summary>

**Response:**
```json
{
  "sessions": [
    {
      "id": "string",
      "name": "string",
      "created_at": "datetime",
      "semesters": [
        {
          "id": "string",
          "name": "string",
          "start_date": "datetime",
          "end_date": "datetime",
          "is_active": true
        }
      ]
    }
  ]
}
```
</details>

<details>
<summary><strong>GET /faculties</strong> — View all faculties</summary>

**Response:**
```json
{
  "faculties": [
    {
      "id": "string",
      "name": "string",
      "code": "string",
      "total_departments": 0
    }
  ]
}
```
</details>

<details>
<summary><strong>GET /faculties/{faculty_id}/departments</strong> — View all departments in a faculty</summary>

**Path Parameters:** `faculty_id`

**Response:**
```json
{
  "departments": [
    {
      "id": "string",
      "name": "string",
      "code": "string",
      "hod": { "id": "string", "name": "string" } | null,
      "total_courses": 0
    }
  ]
}
```
</details>
