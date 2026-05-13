# Business Rules

> Captures system-wide logic and constraints that are not obvious from the endpoint schema alone.
> **How to update:** Add rules as they are decided. One rule per entry, keep it concise.
> If a rule requires significant elaboration, create a file under `/specs/rules/` and reference it here.
> Review this file whenever implementing auth, middleware, or any conditional logic.

---

## Academic Structure

- An AcademicSession (e.g. "2024/2025") contains two semesters: first and second
- Only one semester can be active globally at a time — Admin controls this
- Activating a semester automatically deactivates the currently active one
- A CourseOffering is tied to a specific semester
- Only one active offering per course at a time — backend enforces on creation
- An active semester cannot be deleted; a different semester must be activated first
- A session cannot be deleted if any of its semesters are active
- A semester cannot be deleted if `CourseOfferings` are linked to it
- A session cannot be deleted if any of its semesters have linked offerings

---

## Semester & Write Access

- Any write operation under `/courses/:courseId/*` requires the offering's semester to be active
- If semester is inactive → 403 "No active semester"
- Read operations (GET) are always allowed regardless of semester state
- This applies to: task submissions, session creation, attendance marking, material uploads, announcements

---

## Course & Offering Resolution

- `:courseId` in student/lecturer routes refers to a CourseOffering ID, not a Course definition ID
- The course title, code, units etc. are joined from the Course definition for display
- `GET /courses` returns active offerings for the currently active semester only
- `GET /student/courses` defaults to active semester; accepts optional `semesterId` for past semesters
- `GET /lecturer/courses` defaults to active semester; accepts optional `semesterId` for past semesters

---

## Student Registration

- Student can register for a course if: the semester is active AND they are not already registered
- Registration status starts as `pending` — lecturer must approve
- A student can drop a course (DELETE /courses/:courseId/register) only while semester is active

---

## Level Computation

- Student level is never stored — always computed at runtime
- Formula: `level = (currentSessionYear - admission_year + 1) + levelOffset`
- `admission_year` is stored as the start year only (e.g. 2021, not "2021/2022")
- `levelOffset` defaults to 0; only updated by HOD for deferrals/repeats
- Frontend formats level for display (e.g. `3 → 300 level`)
- No cap on level — no programme duration enforced

---

## Session Ownership

- A session is owned by the lecturer who created it
- Only the session owner can: edit the session, cancel it, mark attendance
- Other lecturers on the same course can view sessions but not modify them
- `isOwner: boolean` is returned in session detail responses for lecturer

---

## Attendance

- Attendance is always tied to a class session — never standalone
- Attendance can only be marked by the session owner
- `attended: boolean | null` — null means attendance has not been taken yet for that session

---

## Materials & AI Tutor

- Material visibility: `students_only` | `ai_only` | `both`
- Only materials with visibility `ai_only` or `both` can be indexed for the AI tutor
- Indexing `students_only` material is rejected with 400
- AI tutor only uses indexed materials for grounding (RAG)
- Lecturer can set custom rules/instructions for the AI tutor per course

---

## Task & Grading

- A task has one type — all questions are the same type (mcq | free_text | document_upload)
- `totalScore` on a task is computed as the sum of all question scores — never stored directly
- Marking guide must be uploaded before AI grading can be enabled
- Enabling AI grading without a marking guide → 400 validation error
- `gradingStatus` enum: `ungraded` | `ai_draft` | `ai_approved` | `manually_graded`
- MCQ answers can be auto-graded once correct answers are defined (future feature)
- Bulk AI grade approval sets all `ai_draft` submissions to `ai_approved`

---

## Lecturer Authorization

- Lecturers self-register but cannot access lecturer routes until authorized by Admin
- Unauthorized lecturer → 403 on all lecturer-scoped routes
- HOD cannot assign an unauthorized lecturer to an offering

---

## HOD Scope

- HOD can only manage users, courses, and offerings within their own department
- HOD cannot access or modify data belonging to other departments

---

## Admin

- Admin has global access across all faculties, departments, and users
- Only Admin can create/activate academic sessions and semesters
- Only Admin can assign or replace a HOD for a department
- Only Admin can bulk-authorize lecturer accounts

---

## Course Offering Lecturers

- A `CourseOffering` can have multiple lecturers via the `OfferingLecturer` junction table
- Only users with the `lecturer` role AND `is_authorized = true` can be assigned to an offering
- Assigning a lecturer who is already assigned returns `409 CONFLICT`
- Removing all lecturers from an offering is allowed — the offering becomes unassigned
- Lecturer access to an offering's routes (sessions, tasks, etc.) requires an `OfferingLecturer` row
