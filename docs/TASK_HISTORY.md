# Task History

> Tracks meaningful decisions and completed planning milestones.
> **How to update:** Add a single line or short entry per task/decision. No prose. No duplicates.
> If a decision has significant detail, put it in the relevant spec file and reference it here.
> Keep this file under 100 lines — archive old entries to `TASK_HISTORY_ARCHIVE.md` if needed.

---

## Completed

- Defined system roles: Student, Lecturer, HOD, Admin
- Defined features: Dashboard, Materials, Tasks, Announcements, AI Tutor, Auto-grading, Attendance
- Defined all functional requirements per role
- Defined full endpoint list (~100 endpoints) — see `ENDPOINTS.md`
- Decided on Course vs CourseOffering model (HOD manages definitions, offerings are per-semester instances)
- Decided `:courseId` in student/lecturer routes refers to offeringId under the hood
- Decided academic hierarchy: AcademicSession → Semester → CourseOffering
- Decided one active semester at a time (Admin controlled)
- Decided one active offering per course at a time (HOD enforced)
- Decided single user table with role-specific nullable fields
- Decided level is computed at runtime, not stored (see BUSINESS_RULES.md)
- Decided task types: mcq | free_text | document_upload (one type per task, mixed questions allowed)
- Decided marking guide is uploaded separately, required before AI grading can be enabled
- Decided material visibility: students_only | ai_only | both
- Decided gradingStatus: ungraded | ai_draft | ai_approved | manually_graded
- Decided class sessions are owned by the lecturer who creates them
- Decided attendance is always tied to a session, never standalone
- Decided tasks can be optionally linked to a session via sessionId
- Dropped: registration window, level cap/duration, level storage

---

## In Progress

- Database schema definition
- Business rules document
- Architecture document
- Frontend screen definitions
