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

## Auth

<details>
<summary><strong>POST /auth/register/lecturer</strong> — Register new lecturer</summary>

**Request Body:**
```json
{
  "firstName": "string",
  "lastName": "string",
  "email": "string",
  "password": "string",
  "staff_id": "string",
  "department_id": "string"
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
<summary><strong>POST /auth/register/student</strong> — Register new student</summary>

**Request Body:**
```json
{
  "firstName": "string",
  "lastName": "string",
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
  "message": "string"
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
  "accessToken": "string"
}
```
</details>

<details>
<summary><strong>POST /auth/logout</strong> — Logout current user</summary>

**Response:**
```json
{
  "message": "string"
}
```
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
  "newPassword": "string"
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

**Response (Student):**
```json
{
  "id": "string",
  "firstName": "string",
  "lastName": "string",
  "email": "string",
  "role": "student",
  "matric_num": "string",
  "admission_session": "string",
  "levelOffset": 0,
  "department": { "id": "string", "name": "string" }
}
```

**Response (Lecturer):**
```json
{
  "id": "string",
  "firstName": "string",
  "lastName": "string",
  "email": "string",
  "role": "lecturer",
  "staff_id": "string",
  "authorized": true,
  "department": { "id": "string", "name": "string" }
}
```
</details>

<details>
<summary><strong>PATCH /auth/me</strong> — Update current user profile</summary>

**Request Body (all optional):**
```json
{
  "firstName": "string",
  "lastName": "string",
  "phone": "string",
  "avatar": "file (multipart)"
}
```

**Response:**
```json
{
  "message": "string",
  "user": { "id": "string", "firstName": "string", "lastName": "string", "email": "string", ... }
}
```
</details>

<details>
<summary><strong>PATCH /auth/me/password</strong> — Change password</summary>

**Request Body:**
```json
{
  "currentPassword": "string",
  "newPassword": "string",
  "confirmPassword": "string"
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
      "lecturer": { "id": "string", "firstName": "string", "lastName": "string" },
      "totalStudents": 0
    }
  ],
  "pagination": { "page": 0, "limit": 0, "total": 0 }
}
```
</details>

<details>
<summary><strong>GET /courses/:courseId</strong> — View single course details</summary>

**Path Parameters:** `courseId`

**Response:**
```json
{
  "id": "string",
  "title": "string",
  "code": "string",
  "description": "string",
  "level": 0,
  "department": "string",
  "lecturer": { "id": "string", "firstName": "string", "lastName": "string" },
  "isRegistered": true,
  "totalStudents": 0
}
```
</details>

<details>
<summary><strong>POST /courses/:courseId/register</strong> — Register for a course</summary>

**Path Parameters:** `courseId`

**Response:**
```json
{
  "message": "string",
  "status": "pending | approved"
}
```
</details>

<details>
<summary><strong>DELETE /courses/:courseId/register</strong> — Drop course registration</summary>

**Path Parameters:** `courseId`

**Response:**
```json
{
  "message": "string"
}
```
</details>

<details>
<summary><strong>GET /student/courses</strong> — View registered courses</summary>

**Query Parameters (optional):** `status` (`pending` | `approved`), `semesterId`

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
      "lecturer": { "id": "string", "firstName": "string", "lastName": "string" }
    }
  ]
}
```
</details>

<details>
<summary><strong>GET /student/courses/:courseId/materials</strong> — View course materials</summary>

**Path Parameters:** `courseId`  
**Query (optional):** `type` (`note` | `slide` | `resource`)

**Response:**
```json
{
  "materials": [
    {
      "id": "string",
      "title": "string",
      "type": "string",
      "fileUrl": "string",
      "uploadedAt": "datetime",
      "visibility": "string"
    }
  ]
}
```
</details>

<details>
<summary><strong>GET /student/courses/:courseId/tasks</strong> — View tasks for a course</summary>

**Path Parameters:** `courseId`  
**Query (optional):** `status` (`upcoming` | `ungraded` | `ai_draft` | `ai_approved` | `manually_graded` | `overdue`)

**Response:**
```json
{
  "tasks": [
    {
      "id": "string",
      "title": "string",
      "dueDate": "datetime",
      "maxScore": 0,
      "submissionStatus": "string",
      "score": 0
    }
  ]
}
```
</details>

<details>
<summary><strong>GET /student/courses/:courseId/tasks/:taskId</strong> — View specific task</summary>

**Path Parameters:** `courseId`, `taskId`

**Response:**
```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "dueDate": "datetime",
  "totalScore": 0,
  "questions": [
    {
      "id": "string",
      "text": "string",
      "type": "string",
      "score": 0,
      "options": ["string"]
    }
  ],
  "submission": { "submittedAt": "datetime", "answers": [] } | null
}
```
</details>

<details>
<summary><strong>POST /student/courses/:courseId/tasks/:taskId/submit</strong> — Submit task</summary>

**Path Parameters:** `courseId`, `taskId`  
**Body (multipart):** `answers[]` (with appropriate fields based on question type)

**Response:**
```json
{
  "message": "string",
  "submission": { "id": "string", "submittedAt": "datetime", "answersCount": 0 }
}
```
</details>

<details>
<summary><strong>GET /student/courses/:courseId/grades</strong> — View grades for a course</summary>

**Path Parameters:** `courseId`

**Response:**
```json
{
  "grades": [
    {
      "taskId": "string",
      "taskTitle": "string",
      "score": 0,
      "maxScore": 0,
      "gradedAt": "datetime",
      "feedback": "string"
    }
  ],
  "summary": {
    "totalScore": 0,
    "average": 0,
    "grade": "string"
  }
}
```
</details>

<details>
<summary><strong>GET /student/courses/:courseId/announcements</strong> — View course announcements</summary>

**Path Parameters:** `courseId`  
**Query (optional):** `viewed`, `pinned`, `page`, `limit`

**Response:**
```json
{
  "announcements": [
    {
      "id": "string",
      "title": "string",
      "body": "string",
      "createdAt": "datetime",
      "lecturer": { "id": "string", "firstName": "string", "lastName": "string" },
      "viewed": true
    }
  ],
  "pagination": { "page": 0, "limit": 0, "total": 0 }
}
```
</details>

<details>
<summary><strong>GET /student/courses/:courseId/attendance</strong> — View personal attendance</summary>

**Path Parameters:** `courseId`

**Response:**
```json
{
  "attendance": [
    {
      "sessionId": "string",
      "sessionDate": "datetime",
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
<summary><strong>GET /student/courses/:courseId/sessions</strong> — View course sessions</summary>

**Path Parameters:** `courseId`  
**Query (optional):** `status` (`upcoming` | `completed` | `cancelled`)

**Response:**
```json
{
  "sessions": [
    {
      "id": "string",
      "title": "string",
      "scheduledAt": "datetime",
      "venue": "string",
      "status": "string",
      "attended": true | null,
      "lecturer": { "id": "string", "firstName": "string", "lastName": "string" }
    }
  ]
}
```
</details>

<details>
<summary><strong>GET /student/courses/:courseId/sessions/:sessionId</strong> — View specific session</summary>

**Path Parameters:** `courseId`, `sessionId`
</details>

<details>
<summary><strong>GET /student/analytics</strong> — View overall analytics (planned)</summary>
</details>

<details>
<summary><strong>GET /student/courses/:courseId/analytics</strong> — View course analytics (planned)</summary>
</details>

<details>
<summary><strong>POST /student/courses/:courseId/ai-tutor</strong> — Chat with AI tutor (planned)</summary>

**Path Parameters:** `courseId`

**Request Body:**
```json
{
  "message": "string",
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
      "totalStudents": 0,
      "isActive": true,
      "lecturers": [{ "id": "string", "name": "string" }]
    }
  ]
}
```
</details>

<details>
<summary><strong>GET /lecturer/courses/:courseId</strong> — View details of an assigned course</summary>

**Path Parameters:** `courseId`

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
  "totalStudents": 0,
  "sessions": 0,
  "tasksCount": 0
}
```
</details>

<details>
<summary><strong>GET /lecturer/courses/:courseId/students</strong> — View all students in a course</summary>

**Path Parameters:** `courseId`  
**Query Parameters (optional):** `status` (enum: `pending` | `approved`)

**Response:**
```json
{
  "students": [
    {
      "id": "string",
      "firstName": "string",
      "lastName": "string",
      "email": "string",
      "registrationStatus": "pending | approved"
    }
  ]
}
```
</details>

<details>
<summary><strong>PATCH /lecturer/courses/:courseId/students/:studentId/approve</strong> — Approve or reject student registration</summary>

**Path Parameters:** `courseId`, `studentId`

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
<summary><strong>POST /lecturer/courses/:courseId/materials</strong> — Upload course material</summary>

**Path Parameters:** `courseId`  
**Body (multipart/form-data):**
- `title`: string
- `type`: enum (`note` | `slide` | `resource`)
- `file`: file
- `visibility`: enum (`students_only` | `ai_only` | `both`)

**Response:**
```json
{
  "message": "string",
  "material": {
    "id": "string",
    "title": "string",
    "type": "string",
    "fileUrl": "string",
    "visibility": "string",
    "uploadedAt": "datetime"
  }
}
```
</details>

<details>
<summary><strong>PATCH /lecturer/courses/:courseId/materials/:materialId</strong> — Update material metadata</summary>

**Path Parameters:** `courseId`, `materialId`

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
<summary><strong>DELETE /lecturer/courses/:courseId/materials/:materialId</strong> — Delete course material</summary>

**Path Parameters:** `courseId`, `materialId`

**Response:**
```json
{
  "message": "string"
}
```
</details>

<details>
<summary><strong>POST /lecturer/courses/:courseId/materials/:materialId/index</strong> — Trigger AI indexing for material</summary>

**Path Parameters:** `courseId`, `materialId`

**Response:**
```json
{
  "message": "string",
  "material": {
    "id": "string",
    "indexed": true,
    "indexedAt": "datetime"
  }
}
```
</details>

<details>
<summary><strong>POST /lecturer/courses/:courseId/tasks</strong> — Create a new task</summary>

**Path Parameters:** `courseId`

**Request Body:**
```json
{
  "title": "string",
  "description": "string (optional)",
  "dueDate": "datetime",
  "sessionId": "string (optional)",
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
    "dueDate": "datetime",
    "questionCount": 0
  }
}
```
</details>

<details>
<summary><strong>GET /lecturer/courses/:courseId/tasks</strong> — View all tasks for a course</summary>

**Path Parameters:** `courseId`

**Response:**
```json
{
  "tasks": [
    {
      "id": "string",
      "title": "string",
      "dueDate": "datetime",
      "questionCount": 0,
      "totalScore": 0,
      "aiGrading": true
    }
  ]
}
```
</details>

<details>
<summary><strong>GET /lecturer/courses/:courseId/tasks/:taskId</strong> — View full task details</summary>

**Path Parameters:** `courseId`, `taskId`

**Response:**
```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "dueDate": "datetime",
  "totalScore": 0,
  "aiGrading": true,
  "markingGuideUrl": "string | null",
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
<summary><strong>PATCH /lecturer/courses/:courseId/tasks/:taskId</strong> — Update task</summary>

**Path Parameters:** `courseId`, `taskId`

**Request Body (all optional):**
```json
{
  "title": "string",
  "description": "string",
  "dueDate": "datetime",
  "sessionId": "string | null"
}
```

**Response:**
```json
{
  "message": "string",
  "task": { "id": "string", "title": "string", "dueDate": "datetime" }
}
```
</details>

<details>
<summary><strong>DELETE /lecturer/courses/:courseId/tasks/:taskId</strong> — Delete task</summary>

**Path Parameters:** `courseId`, `taskId`

**Response:**
```json
{
  "message": "string"
}
```
</details>

<details>
<summary><strong>POST /lecturer/courses/:courseId/tasks/:taskId/questions</strong> — Add question to task</summary>

**Path Parameters:** `courseId`, `taskId`

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
<summary><strong>PATCH /lecturer/courses/:courseId/tasks/:taskId/questions/:questionId</strong> — Update question</summary>

**Path Parameters:** `courseId`, `taskId`, `questionId`

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
<summary><strong>DELETE /lecturer/courses/:courseId/tasks/:taskId/questions/:questionId</strong> — Delete question</summary>

**Path Parameters:** `courseId`, `taskId`, `questionId`

**Response:**
```json
{
  "message": "string"
}
```
</details>

<details>
<summary><strong>POST /lecturer/courses/:courseId/tasks/:taskId/marking-guide</strong> — Upload marking guide</summary>

**Path Parameters:** `courseId`, `taskId`  
**Body (multipart):** `markingGuide` (file)

**Response:**
```json
{
  "message": "string",
  "markingGuideUrl": "string"
}
```
</details>

<details>
<summary><strong>PATCH /lecturer/courses/:courseId/tasks/:taskId/ai-grading</strong> — Enable/Disable AI grading</summary>

**Path Parameters:** `courseId`, `taskId`

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
  "aiGrading": true
}
```
</details>

<details>
<summary><strong>GET /lecturer/courses/:courseId/tasks/:taskId/submissions</strong> — View submissions for a task</summary>

**Path Parameters:** `courseId`, `taskId`  
**Query (optional):** `graded` (boolean)

**Response:**
```json
{
  "submissions": [
    {
      "id": "string",
      "student": { "id": "string", "name": "string" },
      "submittedAt": "datetime",
      "totalScore": 0,
      "gradingStatus": "ungraded | ai_draft | ai_approved | manually_graded"
    }
  ]
}
```
</details>

<details>
<summary><strong>GET /lecturer/courses/:courseId/tasks/:taskId/submissions/:submissionId</strong> — View specific submission</summary>

**Path Parameters:** `courseId`, `taskId`, `submissionId`

**Response:**
```json
{
  "student": { "id": "string", "name": "string", "matric_num": "string" },
  "submittedAt": "datetime",
  "totalScore": 0,
  "gradingStatus": "ungraded | ai_draft | ai_approved | manually_graded",
  "answers": [
    {
      "questionId": "string",
      "questionText": "string",
      "type": "string",
      "score": 0,
      "maxScore": 0,
      // fields vary by type (selectedOption, text, fileUrl, feedback, etc.)
    }
  ]
}
```
</details>

<details>
<summary><strong>PATCH /lecturer/courses/:courseId/tasks/:taskId/submissions/:submissionId/grade</strong> — Grade a submission</summary>

**Path Parameters:** `courseId`, `taskId`, `submissionId`

**Request Body:**
```json
{
  "grades": [
    {
      "questionId": "string",
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
  "submission": { "id": "string", "totalScore": 0, "gradedAt": "datetime" }
}
```
</details>

<details>
<summary><strong>POST /lecturer/courses/:courseId/tasks/:taskId/submissions/approve-ai-grades</strong> — Approve AI draft grades</summary>

**Path Parameters:** `courseId`, `taskId`

**Request Body (optional):**
```json
{
  "submissionIds": ["string"]
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
<summary><strong>POST /lecturer/courses/:courseId/sessions</strong> — Schedule a new class session</summary>

**Path Parameters:** `courseId`

**Request Body:**
```json
{
  "title": "string",
  "scheduledAt": "datetime",
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
    "scheduledAt": "datetime",
    "venue": "string",
    "status": "string"
  }
}
```
</details>

<details>
<summary><strong>GET /lecturer/courses/:courseId/sessions</strong> — View all sessions for a course</summary>

**Path Parameters:** `courseId`  
**Query (optional):** `status` (`upcoming` | `completed` | `cancelled`)

**Response:**
```json
{
  "sessions": [
    {
      "id": "string",
      "title": "string",
      "scheduledAt": "datetime",
      "venue": "string",
      "status": "string",
      "attendanceCount": 0
    }
  ]
}
```
</details>

<details>
<summary><strong>GET /lecturer/courses/:courseId/sessions/:sessionId</strong> — View session details with attendance</summary>

**Path Parameters:** `courseId`, `sessionId`

**Response:**
```json
{
  "session": { "id": "string", "title": "string", "scheduledAt": "datetime", "venue": "string", "status": "string" },
  "lecturer": { "id": "string", "firstName": "string", "lastName": "string" },
  "isOwner": true,
  "attendance": [
    { "studentId": "string", "name": "string", "status": "present | absent" }
  ],
  "tasks": [
    { "taskId": "string", "title": "string", "submissionsCount": 0 }
  ]
}
```
</details>

<details>
<summary><strong>POST /lecturer/courses/:courseId/sessions/:sessionId/attendance</strong> — Mark attendance</summary>

**Path Parameters:** `courseId`, `sessionId`

**Request Body:**
```json
{
  "records": [
    { "studentId": "string", "status": "present | absent" }
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
<summary><strong>GET /lecturer/courses/:courseId/gradebook</strong> — View course gradebook</summary>

**Path Parameters:** `courseId`

**Response:**
```json
{
  "students": [
    {
      "studentId": "string",
      "name": "string",
      "tasks": [{ "taskId": "string", "title": "string", "score": 0, "maxScore": 0 }],
      "totalScore": 0,
      "average": 0,
      "grade": "string"
    }
  ]
}
```
</details>

<details>
<summary><strong>PATCH /lecturer/courses/:courseId/gradebook/:studentId</strong> — Manually update student grade</summary>

**Path Parameters:** `courseId`, `studentId`

**Request Body (optional):**
```json
{
  "notes": "string",
  "manualGrade": "string"
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
<summary><strong>POST /lecturer/courses/:courseId/announcements</strong> — Post announcement</summary>

**Path Parameters:** `courseId`

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
    "createdAt": "datetime"
  }
}
```
</details>

<details>
<summary><strong>GET /lecturer/courses/:courseId/announcements</strong> — View announcements</summary>

**Path Parameters:** `courseId`  
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
      "createdAt": "datetime"
    }
  ],
  "pagination": { "page": 0, "limit": 0, "total": 0 }
}
```
</details>

<details>
<summary><strong>GET /lecturer/courses/:courseId/announcements/:announcementId</strong> — View specific announcement</summary>

**Path Parameters:** `courseId`, `announcementId`
</details>

<details>
<summary><strong>PATCH /lecturer/courses/:courseId/announcements/:announcementId</strong> — Update announcement</summary>

**Path Parameters:** `courseId`, `announcementId`
</details>

<details>
<summary><strong>DELETE /lecturer/courses/:courseId/announcements/:announcementId</strong> — Delete announcement</summary>

**Path Parameters:** `courseId`, `announcementId`
</details>

<details>
<summary><strong>GET /lecturer/courses/:courseId/analytics</strong> — View course analytics (planned)</summary>

**Path Parameters:** `courseId`
</details>

<details>
<summary><strong>GET /lecturer/analytics</strong> — View overall lecturer analytics (planned)</summary>
</details>

<details>
<summary><strong>PATCH /lecturer/courses/:courseId/ai-tutor/rules</strong> — Set or update AI tutor instructions for a course</summary>

**Path Parameters:** `courseId`

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
---

## HOD

<details>
<summary><strong>GET /hod/students</strong> — View all students in the department</summary>

**Query Parameters (optional):** `search`, `page`, `limit`

**Response:**
```json
{
  "users": [
    { "id": "string", "firstName": "string", "lastName": "string", "email": "string", "role": "student" }
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
<summary><strong>GET /hod/students/:studentId</strong> — View specific student details</summary>

**Path Parameters:** `studentId`

**Response:**
```json
{
  "id": "string",
  "firstName": "string",
  "lastName": "string",
  "email": "string",
  "role": "student",
  "matric_num": "string",
  "admission_session": "string",
  "levelOffset": 0,
  "department": { "id": "string", "name": "string" },
  "offerings": [
    {
      "id": "string",
      "courseTitle": "string",
      "academicSession": "string",
      "semester": "string",
      "status": "string"
    }
  ]
}
```
</details>

<details>
<summary><strong>GET /hod/lecturers/:lecturerId</strong> — View specific lecturer details</summary>

**Path Parameters:** `lecturerId`

**Response:**
```json
{
  "id": "string",
  "firstName": "string",
  "lastName": "string",
  "email": "string",
  "role": "lecturer",
  "staff_id": "string",
  "authorized": true,
  "department": { "id": "string", "name": "string" },
  "offerings": [
    {
      "id": "string",
      "courseTitle": "string",
      "academicSession": "string",
      "semester": "string",
      "isActive": true
    }
  ]
}
```
</details>

<details>
<summary><strong>PATCH /hod/students/:studentId/level-offset</strong> — Update student's level offset</summary>

**Path Parameters:** `studentId`

**Request Body:**
```json
{
  "levelOffset": 0
}
```

**Response:**
```json
{
  "message": "string",
  "student": {
    "id": "string",
    "levelOffset": 0,
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
      "totalOfferings": 0,
      "activeOffering": true
    }
  ],
  "pagination": { "page": 0, "limit": 0, "total": 0 }
}
```
</details>

<details>
<summary><strong>GET /hod/courses/:courseId</strong> — View course definition details</summary>

**Path Parameters:** `courseId`

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
      "academicSession": "string",
      "semester": "string",
      "isActive": true,
      "lecturer": { "id": "string", "name": "string" }
    }
  ]
}
```
</details>

<details>
<summary><strong>PATCH /hod/courses/:courseId</strong> — Update course definition</summary>

**Path Parameters:** `courseId`

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
<summary><strong>DELETE /hod/courses/:courseId</strong> — Delete course definition</summary>

**Path Parameters:** `courseId`

**Response:**
```json
{
  "message": "string"
}
```
</details>

<details>
<summary><strong>POST /hod/courses/:courseId/offerings</strong> — Create course offering</summary>

**Path Parameters:** `courseId`

**Request Body:**
```json
{
  "semesterId": "string",
  "lecturerId": "string (optional)"
}
```

**Response:**
```json
{
  "message": "string",
  "offering": {
    "id": "string",
    "courseId": "string",
    "academicSession": "string",
    "semester": "string",
    "isActive": true,
    "lecturer": { "id": "string", "firstName": "string", "lastName": "string" }
  }
}
```
</details>

<details>
<summary><strong>GET /hod/courses/:courseId/offerings</strong> — View all offerings for a course</summary>

**Path Parameters:** `courseId`  
**Query Parameters (optional):** `semesterId`, `isActive`

**Response:**
```json
{
  "offerings": [
    {
      "id": "string",
      "academicSession": "string",
      "semester": "string",
      "isActive": true,
      "totalStudents": 0,
      "lecturer": { "id": "string", "firstName": "string", "lastName": "string" }
    }
  ]
}
```
</details>

<details>
<summary><strong>GET /hod/courses/:courseId/offerings/:offeringId</strong> — View specific offering details</summary>

**Path Parameters:** `courseId`, `offeringId`

**Response:**
```json
{
  "id": "string",
  "course": { "id": "string", "title": "string", "code": "string" },
  "academicSession": "string",
  "semester": "string",
  "isActive": true,
  "lecturer": { "id": "string", "firstName": "string", "lastName": "string", "staff_id": "string" },
  "totalStudents": 0,
  "totalSessions": 0,
  "totalTasks": 0
}
```
</details>

<details>
<summary><strong>PATCH /hod/courses/:courseId/offerings/:offeringId/activate</strong> — Activate/Deactivate offering</summary>

**Path Parameters:** `courseId`, `offeringId`

**Request Body:**
```json
{
  "isActive": true
}
```

**Response:**
```json
{
  "message": "string",
  "offering": { "id": "string", "isActive": true }
}
```
</details>

<details>
<summary><strong>POST /hod/courses/:courseId/offerings/:offeringId/assign</strong> — Assign lecturer to offering</summary>

**Path Parameters:** `courseId`, `offeringId`

**Request Body:**
```json
{
  "lecturerId": "string"
}
```

**Response:**
```json
{
  "message": "string",
  "offering": {
    "id": "string",
    "lecturer": { "id": "string", "firstName": "string", "lastName": "string" }
  }
}
```
</details>

<details>
<summary><strong>DELETE /hod/courses/:courseId/offerings/:offeringId/assign/:lecturerId</strong> — Unassign lecturer from offering</summary>

**Path Parameters:** `courseId`, `offeringId`, `lecturerId`

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
  "userIds": ["string"]
}
```

**Response:**
```json
{
  "message": "string",
  "authorized": 0,
  "failed": [
    { "userId": "string", "reason": "string" }
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
      "totalDepartments": 0
    }
  ]
}
```
</details>

<details>
<summary><strong>PATCH /admin/faculties/:facultyId</strong> — Update a faculty</summary>

**Path Parameters:** `facultyId`

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
<summary><strong>DELETE /admin/faculties/:facultyId</strong> — Delete a faculty</summary>

**Path Parameters:** `facultyId`

**Response:**
```json
{
  "message": "string"
}
```
</details>

<details>
<summary><strong>POST /admin/faculties/:facultyId/departments</strong> — Create a department</summary>

**Path Parameters:** `facultyId`

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
<summary><strong>GET /admin/faculties/:facultyId/departments</strong> — View all departments in a faculty</summary>

**Path Parameters:** `facultyId`

**Response:**
```json
{
  "departments": [
    {
      "id": "string",
      "name": "string",
      "code": "string",
      "hod": { "id": "string", "name": "string" } | null,
      "totalCourses": 0
    }
  ]
}
```
</details>

<details>
<summary><strong>GET /admin/faculties/:facultyId/departments/:departmentId</strong> — View specific department details</summary>

**Path Parameters:** `facultyId`, `departmentId`

**Response:**
```json
{
  "id": "string",
  "name": "string",
  "code": "string",
  "faculty": { "id": "string", "name": "string" },
  "hod": { "id": "string", "firstName": "string", "lastName": "string" } | null,
  "totalCourses": 0,
  "totalStudents": 0,
  "totalLecturers": 0
}
```
</details>

<details>
<summary><strong>PATCH /admin/faculties/:facultyId/departments/:departmentId</strong> — Update a department</summary>

**Path Parameters:** `facultyId`, `departmentId`

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
<summary><strong>DELETE /admin/faculties/:facultyId/departments/:departmentId</strong> — Delete a department</summary>

**Path Parameters:** `facultyId`, `departmentId`

**Response:**
```json
{
  "message": "string"
}
```
</details>

<details>
<summary><strong>POST /admin/departments/:departmentId/hod</strong> — Assign HOD to department</summary>

**Path Parameters:** `departmentId`

**Request Body:**
```json
{
  "userId": "string"
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
<summary><strong>PATCH /admin/departments/:departmentId/hod</strong> — Replace current HOD</summary>

**Path Parameters:** `departmentId`

**Request Body:**
```json
{
  "userId": "string"
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
      "firstName": "string",
      "lastName": "string",
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
      "startDate": "datetime",
      "endDate": "datetime"
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
        "startDate": "datetime",
        "endDate": "datetime",
        "isActive": false
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
      "createdAt": "datetime",
      "semesters": [
        {
          "id": "string",
          "name": "string",
          "startDate": "datetime",
          "endDate": "datetime",
          "isActive": true
        }
      ]
    }
  ]
}
```
</details>

<details>
<summary><strong>GET /admin/academic-sessions/:sessionId</strong> — Get single academic session</summary>

**Path Parameters:** `sessionId`

**Response:**
```json
{
  "id": "string",
  "name": "string",
  "createdAt": "datetime",
  "semesters": [
    {
      "id": "string",
      "name": "string",
      "startDate": "datetime",
      "endDate": "datetime",
      "isActive": true
    }
  ]
}
```
</details>

<details>
<summary><strong>PATCH /admin/academic-sessions/:sessionId</strong> — Update academic session</summary>

**Path Parameters:** `sessionId`

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
<summary><strong>DELETE /admin/academic-sessions/:sessionId</strong> — Delete academic session</summary>

**Path Parameters:** `sessionId`

**Response:**
```json
{
  "message": "string"
}
```
</details>

<details>
<summary><strong>PATCH /admin/academic-sessions/:sessionId/semesters/:semesterId/activate</strong> — Activate a semester</summary>

**Path Parameters:** `sessionId`, `semesterId`

**Response:**
```json
{
  "message": "string",
  "semester": {
    "id": "string",
    "name": "string",
    "isActive": true
  }
}
```
</details>

<details>
<summary><strong>PATCH /admin/academic-sessions/:sessionId/semesters/:semesterId</strong> — Update a semester</summary>

**Path Parameters:** `sessionId`, `semesterId`

**Request Body (all optional):**
```json
{
  "startDate": "datetime",
  "endDate": "datetime"
}
```

**Response:**
```json
{
  "message": "string",
  "semester": {
    "id": "string",
    "startDate": "datetime",
    "endDate": "datetime"
  }
}
```
</details>

<details>
<summary><strong>DELETE /admin/academic-sessions/:sessionId/semesters/:semesterId</strong> — Delete a semester</summary>

**Path Parameters:** `sessionId`, `semesterId`

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
<summary><strong>GET /materials/:materialId/download</strong> — Download material file</summary>

**Path Parameters:** `materialId`  
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
      "createdAt": "datetime",
      "link": "string"
    }
  ],
  "unreadCount": 0
}
```
</details>

<details>
<summary><strong>PATCH /notifications/:notificationId/read</strong> — Mark notification as read</summary>

**Path Parameters:** `notificationId`

**Response:**
```json
{
  "message": "string"
}
```
</details>