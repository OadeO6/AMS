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

## Auth

```
[ ] POST   /auth/register/student
[ ] POST   /auth/register/lecturer
[ ] POST   /auth/login
[ ] POST   /auth/logout
[ ] POST   /auth/forgot-password
[ ] POST   /auth/reset-password
[ ] GET    /auth/me
[ ] PATCH  /auth/me
[ ] PATCH  /auth/me/student
[ ] PATCH  /auth/me/lecturer
[ ] PATCH  /auth/me/password
```
→ See: [`ENDPOINTS_DETAIL.md` — Auth](./ENDPOINTS_DETAIL.md#auth)

---

## Student

```
# Course
[ ] GET    /courses
[ ] GET    /courses/:courseId
[ ] POST   /courses/:courseId/register
[ ] DELETE /courses/:courseId/register

[ ] GET    /student/courses                       ?semesterId

# Materials
[ ] GET    /student/courses/:courseId/materials   ?type

# Tasks
[ ] GET    /student/courses/:courseId/tasks       ?status
[ ] GET    /student/courses/:courseId/tasks/:taskId
[ ] POST   /student/courses/:courseId/tasks/:taskId/submit

# Grades
[ ] GET    /student/courses/:courseId/grades

# Announcements
[ ] GET    /student/courses/:courseId/announcements
[ ] GET    /student/courses/:courseId/announcements/:announcementId
[ ] PATCH  /student/courses/:courseId/announcements/:announcementId/viewed

# Sessions
[ ] GET    /student/courses/:courseId/sessions    ?status ?lecturerId
[ ] GET    /student/courses/:courseId/sessions/:sessionId

# Attendance
[ ] GET    /student/courses/:courseId/attendance

# Analytics (plan not finished)
[ ] GET    /student/analytics
[ ] GET    /student/courses/:courseId/analytics

# AI Tutor (plan not finished)
[ ] POST   /student/courses/:courseId/ai-tutor
```
→ See: [`ENDPOINTS_DETAIL.md` — Student](./ENDPOINTS_DETAIL.md#student)

---

## Lecturer

```
# Courses
[ ] GET    /lecturer/courses                      ?semesterId
[ ] GET    /lecturer/courses/:courseId

# Students
[ ] GET    /lecturer/courses/:courseId/students   ?status
[ ] PATCH  /lecturer/courses/:courseId/students/:studentId/approve

# Materials
[ ] POST   /lecturer/courses/:courseId/materials
[ ] PATCH  /lecturer/courses/:courseId/materials/:materialId
[ ] DELETE /lecturer/courses/:courseId/materials/:materialId
[ ] POST   /lecturer/courses/:courseId/materials/:materialId/index

# Tasks
[ ] POST   /lecturer/courses/:courseId/tasks
[ ] PATCH  /lecturer/courses/:courseId/tasks/:taskId
[ ] DELETE /lecturer/courses/:courseId/tasks/:taskId
[ ] GET    /lecturer/courses/:courseId/tasks
[ ] GET    /lecturer/courses/:courseId/tasks/:taskId
[ ] POST   /lecturer/courses/:courseId/tasks/:taskId/marking-guide
[ ] PATCH  /lecturer/courses/:courseId/tasks/:taskId/ai-grading

# Questions
[ ] POST   /lecturer/courses/:courseId/tasks/:taskId/questions
[ ] PATCH  /lecturer/courses/:courseId/tasks/:taskId/questions/:questionId
[ ] DELETE /lecturer/courses/:courseId/tasks/:taskId/questions/:questionId

# Submissions
[ ] GET    /lecturer/courses/:courseId/tasks/:taskId/submissions            ?graded
[ ] GET    /lecturer/courses/:courseId/tasks/:taskId/submissions/:submissionId
[ ] PATCH  /lecturer/courses/:courseId/tasks/:taskId/submissions/:submissionId/grade
[ ] POST   /lecturer/courses/:courseId/tasks/:taskId/submissions/approve-ai-grades

# Sessions
[ ] POST   /lecturer/courses/:courseId/sessions
[ ] PATCH  /lecturer/courses/:courseId/sessions/:sessionId
[ ] DELETE /lecturer/courses/:courseId/sessions/:sessionId
[ ] GET    /lecturer/courses/:courseId/sessions                             ?status
[ ] GET    /lecturer/courses/:courseId/sessions/:sessionId
[ ] POST   /lecturer/courses/:courseId/sessions/:sessionId/attendance

# Announcements
[ ] POST   /lecturer/courses/:courseId/announcements
[ ] GET    /lecturer/courses/:courseId/announcements                        ?pinned
[ ] GET    /lecturer/courses/:courseId/announcements/:announcementId
[ ] PATCH  /lecturer/courses/:courseId/announcements/:announcementId
[ ] DELETE /lecturer/courses/:courseId/announcements/:announcementId

# Gradebook
[ ] GET    /lecturer/courses/:courseId/gradebook
[ ] PATCH  /lecturer/courses/:courseId/gradebook/:studentId

# Analytics (plan not finished)
[ ] GET    /lecturer/courses/:courseId/analytics
[ ] GET    /lecturer/analytics

# AI Tutor (plan not finished)
[ ] POST   /lecturer/courses/:courseId/ai-tutor
[ ] PATCH  /lecturer/courses/:courseId/ai-tutor/rules
```
→ See: [`ENDPOINTS_DETAIL.md` — Lecturer](./ENDPOINTS_DETAIL.md#lecturer)

---

## HOD

```
# Students
[ ] GET    /hod/students                          ?search
[ ] GET    /hod/students/:studentId
[ ] PATCH  /hod/students/:studentId/level-offset

# Lecturers
[ ] GET    /hod/lecturers                         ?search
[ ] GET    /hod/lecturers/:lecturerId

# Course Definitions
[ ] POST   /hod/courses
[ ] GET    /hod/courses                           ?search
[ ] GET    /hod/courses/:courseId
[ ] PATCH  /hod/courses/:courseId
[ ] DELETE /hod/courses/:courseId

# Offerings
[ ] POST   /hod/courses/:courseId/offerings
[ ] GET    /hod/courses/:courseId/offerings       ?semesterId ?isActive
[ ] GET    /hod/courses/:courseId/offerings/:offeringId
[ ] PATCH  /hod/courses/:courseId/offerings/:offeringId/activate
[ ] POST   /hod/courses/:courseId/offerings/:offeringId/assign
[ ] DELETE /hod/courses/:courseId/offerings/:offeringId/assign/:lecturerId
```
→ See: [`ENDPOINTS_DETAIL.md` — HOD](./ENDPOINTS_DETAIL.md#hod)

---

## Admin

```
# Faculties
[ ] POST   /admin/faculties
[ ] GET    /admin/faculties
[ ] PATCH  /admin/faculties/:facultyId
[ ] DELETE /admin/faculties/:facultyId

# Departments
[ ] POST   /admin/faculties/:facultyId/departments
[ ] GET    /admin/faculties/:facultyId/departments
[ ] GET    /admin/faculties/:facultyId/departments/:departmentId
[ ] PATCH  /admin/faculties/:facultyId/departments/:departmentId
[ ] DELETE /admin/faculties/:facultyId/departments/:departmentId
[ ] POST   /admin/departments/:departmentId/hod
[ ] PATCH  /admin/departments/:departmentId/hod

# Academic Calendar
[ ] POST   /admin/academic-sessions
[ ] GET    /admin/academic-sessions
[ ] GET    /admin/academic-sessions/:sessionId
[ ] PATCH  /admin/academic-sessions/:sessionId
[ ] DELETE /admin/academic-sessions/:sessionId
[ ] PATCH  /admin/academic-sessions/:sessionId/semesters/:semesterId/activate
[ ] PATCH  /admin/academic-sessions/:sessionId/semesters/:semesterId
[ ] DELETE /admin/academic-sessions/:sessionId/semesters/:semesterId

# Users
[ ] GET    /admin/users                           ?role ?department ?search
[ ] POST   /admin/staff/authorize
```
→ See: [`ENDPOINTS_DETAIL.md` — Admin](./ENDPOINTS_DETAIL.md#admin)

---

## Shared

```
[ ] GET    /materials/:materialId/download
[ ] GET    /notifications                         ?read
[ ] PATCH  /notifications/:notificationId/read
```
→ See: [`ENDPOINTS_DETAIL.md` — Shared](./ENDPOINTS_DETAIL.md#shared)
