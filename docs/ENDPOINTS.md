# Endpoint Specifications

> The single source of truth for all API endpoints.
> **How to update:** When an endpoint is added, modified, or removed — update it here immediately.
> Keep definitions concise: params, body, and response only. No implementation details.
> If an endpoint group grows very large or complex, extract it to `/specs/endpoints/` and reference it here.
> Endpoints marked `(plan not finished)` need further definition before implementation.

---

> **Note:** In student and lecturer routes, `:courseId` refers to a **CourseOffering ID**, not a Course definition ID.
> The distinction is only explicit in HOD routes.

---

## Developer Instructions

> **How to update:** When an endpoint is added, modified, or removed:
> 1. Update the route list in **this file** immediately.
> 2. Update the full spec entry in **`ENDPOINTS_DETAIL.md`** to match.
> 3. Log the change in **`DOC_HISTORY.md`**.
>
> **Keep in sync with:** `ENDPOINTS_DETAIL.md` — these two files must always agree.
> This file stays concise (route list only). `ENDPOINTS_DETAIL.md` holds the full definitions.
> Endpoints marked `(plan not finished)` need further definition before implementation.
>
> **Status markers** — update as you implement:
> `[ ]` planned · `[~]` in progress · `[x]` implemented & tested

---

## System & Health

```
[x] GET    /healthz
[x] GET    /readyz
```
→ See: [`ENDPOINTS_DETAIL.md` — System & Health](./ENDPOINTS_DETAIL.md#system--health)

---

## Auth

```
[x] POST   /auth/register/student
[x] POST   /auth/register/lecturer
[x] POST   /auth/login
[x] POST   /auth/logout
[x] POST   /auth/forgot-password
[x] POST   /auth/reset-password
[x] POST   /auth/refresh
[x] GET    /auth/me
[x] PATCH  /auth/me
[x] PATCH  /auth/me/student
[x] PATCH  /auth/me/lecturer
[x] PATCH  /auth/me/password
```
→ See: [`ENDPOINTS_DETAIL.md` — Auth](./ENDPOINTS_DETAIL.md#auth)

---

## Student

```
# Course
[x] GET    /courses
[x] GET    /courses/:courseId
[x] POST   /courses/:courseId/register
[x] DELETE /courses/:courseId/register

[x] GET    /student/courses                       ?semesterId

# Materials
[x] GET    /student/courses/:courseId/materials   ?type

# Tasks
[x] GET    /student/courses/:courseId/tasks       ?status
[x] GET    /student/courses/:courseId/tasks/:taskId
[x] POST   /student/courses/:courseId/tasks/:taskId/submit

# Grades
[x] GET    /student/courses/:courseId/grades

# Announcements
[x] GET    /student/courses/:courseId/announcements
[x] GET    /student/courses/:courseId/announcements/:announcementId
[x] PATCH  /student/courses/:courseId/announcements/:announcementId/viewed

# Sessions
[x] GET    /student/courses/:courseId/sessions    ?status ?lecturerId
[x] GET    /student/courses/:courseId/sessions/:sessionId

# Attendance
[x] GET    /student/courses/:courseId/attendance

# Analytics
[x] GET    /student/analytics
[x] GET    /student/courses/:courseId/analytics

# AI Tutor
[x] POST   /student/courses/:courseId/ai-tutor
```
→ See: [`ENDPOINTS_DETAIL.md` — Student](./ENDPOINTS_DETAIL.md#student)

---

## Lecturer

```
# Courses
[x] GET    /lecturer/courses                      ?semesterId
[x] GET    /lecturer/courses/:courseId

# Students
[x] GET    /lecturer/courses/:courseId/students   ?status
[x] PATCH  /lecturer/courses/:courseId/students/:studentId/approve

# Materials
[x] POST   /lecturer/courses/:courseId/materials
[x] PATCH  /lecturer/courses/:courseId/materials/:materialId
[x] DELETE /lecturer/courses/:courseId/materials/:materialId
[x] POST   /lecturer/courses/:courseId/materials/:materialId/index

# Tasks
[x] POST   /lecturer/courses/:courseId/tasks
[x] PATCH  /lecturer/courses/:courseId/tasks/:taskId
[x] DELETE /lecturer/courses/:courseId/tasks/:taskId
[x] GET    /lecturer/courses/:courseId/tasks
[x] GET    /lecturer/courses/:courseId/tasks/:taskId
[x] POST   /lecturer/courses/:courseId/tasks/:taskId/marking-guide
[x] PATCH  /lecturer/courses/:courseId/tasks/:taskId/ai-grading

# Questions
[x] POST   /lecturer/courses/:courseId/tasks/:taskId/questions
[x] PATCH  /lecturer/courses/:courseId/tasks/:taskId/questions/:questionId
[x] DELETE /lecturer/courses/:courseId/tasks/:taskId/questions/:questionId

# Submissions
[x] GET    /lecturer/courses/:courseId/tasks/:taskId/submissions            ?graded
[x] GET    /lecturer/courses/:courseId/tasks/:taskId/submissions/:submissionId
[x] PATCH  /lecturer/courses/:courseId/tasks/:taskId/submissions/:submissionId/grade
[x] POST   /lecturer/courses/:courseId/tasks/:taskId/submissions/approve-ai-grades

# Sessions
[x] POST   /lecturer/courses/:courseId/sessions
[x] PATCH  /lecturer/courses/:courseId/sessions/:sessionId
[x] DELETE /lecturer/courses/:courseId/sessions/:sessionId
[x] GET    /lecturer/courses/:courseId/sessions                             ?status
[x] GET    /lecturer/courses/:courseId/sessions/:sessionId
[x] POST   /lecturer/courses/:courseId/sessions/:sessionId/attendance

# Announcements
[x] POST   /lecturer/courses/:courseId/announcements
[x] GET    /lecturer/courses/:courseId/announcements                        ?pinned
[x] GET    /lecturer/courses/:courseId/announcements/:announcementId
[x] PATCH  /lecturer/courses/:courseId/announcements/:announcementId
[x] DELETE /lecturer/courses/:courseId/announcements/:announcementId

# Gradebook
[x] GET    /lecturer/courses/:courseId/gradebook
[x] PATCH  /lecturer/courses/:courseId/gradebook/:studentId

# Analytics
[x] GET    /lecturer/courses/:courseId/analytics
[x] GET    /lecturer/analytics

# AI Tutor
[x] POST   /lecturer/courses/:courseId/ai-tutor
[x] PATCH  /lecturer/courses/:courseId/ai-tutor/rules
```
→ See: [`ENDPOINTS_DETAIL.md` — Lecturer](./ENDPOINTS_DETAIL.md#lecturer)

---

## HOD

```
# Students
[x] GET    /hod/students                          ?search
[x] GET    /hod/students/:studentId
[x] PATCH  /hod/students/:studentId/level-offset

# Lecturers
[x] GET    /hod/lecturers                         ?search
[x] GET    /hod/lecturers/:lecturerId

# Course Definitions
[x] POST   /hod/courses
[x] GET    /hod/courses                           ?search
[x] GET    /hod/courses/:courseId
[x] PATCH  /hod/courses/:courseId
[x] DELETE /hod/courses/:courseId

# Offerings
[x] POST   /hod/courses/:courseId/offerings
[x] GET    /hod/courses/:courseId/offerings       ?semesterId ?isActive
[x] GET    /hod/courses/:courseId/offerings/:offeringId
[x] PATCH  /hod/courses/:courseId/offerings/:offeringId/activate
[x] POST   /hod/courses/:courseId/offerings/:offeringId/assign
[x] DELETE /hod/courses/:courseId/offerings/:offeringId/assign/:lecturerId
```
→ See: [`ENDPOINTS_DETAIL.md` — HOD](./ENDPOINTS_DETAIL.md#hod)

---

## Admin

```
# Faculties
[x] POST   /admin/faculties
[x] GET    /admin/faculties
[x] PATCH  /admin/faculties/:facultyId
[x] DELETE /admin/faculties/:facultyId

# Departments
[x] POST   /admin/faculties/:facultyId/departments
[x] GET    /admin/faculties/:facultyId/departments
[x] GET    /admin/faculties/:facultyId/departments/:departmentId
[x] PATCH  /admin/faculties/:facultyId/departments/:departmentId
[x] DELETE /admin/faculties/:facultyId/departments/:departmentId
[x] POST   /admin/departments/:departmentId/hod
[x] PATCH  /admin/departments/:departmentId/hod

# Academic Calendar
[x] POST   /admin/academic-sessions
[x] GET    /admin/academic-sessions
[x] GET    /admin/academic-sessions/:sessionId
[x] PATCH  /admin/academic-sessions/:sessionId
[x] DELETE /admin/academic-sessions/:sessionId
[x] PATCH  /admin/academic-sessions/:sessionId/semesters/:semesterId/activate
[x] PATCH  /admin/academic-sessions/:sessionId/semesters/:semesterId
[x] DELETE /admin/academic-sessions/:sessionId/semesters/:semesterId

# Users
[x] GET    /admin/users                           ?role ?department ?search
[x] POST   /admin/staff/authorize
```
→ See: [`ENDPOINTS_DETAIL.md` — Admin](./ENDPOINTS_DETAIL.md#admin)

---

## Shared

```
[x] GET    /materials/:materialId/download
[x] GET    /notifications                         ?read
[x] PATCH  /notifications/read
[x] PATCH  /notifications/read-all
[x] POST   /notifications/device-tokens
[x] DELETE /notifications/device-tokens/:token
```
→ See: [`ENDPOINTS_DETAIL.md` — Shared](./ENDPOINTS_DETAIL.md#shared)
