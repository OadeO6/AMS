# Database Schema

> Defines the core data models and their relationships.
> **How to update:** Add fields as they are finalized. Keep types simple and readable.
> Avoid adding every index or constraint here — this is for structure and relationships, not migrations.
> If a model becomes complex (e.g. analytics, AI pipeline), move it to `/specs/schema/` and reference it here.

---

## Models

### User
```
id
firstName, lastName, email, passwordHash
role                enum: student | lecturer | hod | admin
departmentId        FK → Department
phone, avatar       nullable

# student only
admission_year      int | null
levelOffset         int | null  (default: 0)

# lecturer only
staff_id            string | null
isAuthorized        bool | null

createdAt, updatedAt
```

### Faculty
```
id
name, code
createdAt
```

### Department
```
id
facultyId           FK → Faculty
name, code
hodId               FK → User | null
createdAt
```

### AcademicSession
```
id
name                (e.g. "2024/2025")
createdAt
```

### Semester
```
id
academicSessionId   FK → AcademicSession
name                enum: first | second
startDate, endDate
isActive            bool (only one true globally)
```

### Course
```
id
departmentId        FK → Department
title, code
description         nullable
units               int
createdAt
```

### CourseOffering
```
id
courseId            FK → Course
semesterId          FK → Semester
lecturerId          FK → User | null
isActive            bool
```

### CourseRegistration
```
id
offeringId          FK → CourseOffering
studentId           FK → User
status              enum: pending | approved | rejected
createdAt
```

### Material
```
id
offeringId          FK → CourseOffering
uploadedBy          FK → User
title
type                enum: note | slide | resource
fileUrl             string (stores object key, not full URL)
visibility          enum: students_only | ai_only | both
indexed             bool (default: false)
indexedAt           nullable
createdAt
```

### Task
```
id
offeringId          FK → CourseOffering
sessionId           FK → ClassSession | null
title
description         nullable
dueDate
aiGrading           bool (default: false)
markingGuideUrl     string | null (stores object key)
createdAt
```

### Question
```
id
taskId              FK → Task
text
type                enum: mcq | free_text | document_upload
score               number
options             string[] | null  (only for mcq)
```

### Submission
```
id
taskId              FK → Task
studentId           FK → User
submittedAt
gradingStatus       enum: ungraded | ai_draft | ai_approved | manually_graded
totalScore          number | null
gradedAt            nullable
```

### Answer
```
id
submissionId        FK → Submission
questionId          FK → Question
selectedOption      string | null   (mcq)
textAnswer          string | null   (free_text)
fileUrl             string | null   (stores object key)
score               number | null
feedback            string | null
```

### ClassSession
```
id
offeringId          FK → CourseOffering
lecturerId          FK → User  (owner)
title
scheduledAt
venue               nullable
status              enum: upcoming | completed | cancelled
notes               nullable
createdAt
```

### Attendance
```
id
sessionId           FK → ClassSession
studentId           FK → User
status              enum: present | absent
markedAt
markedBy            FK → User
```

### Announcement
```
id
offeringId          FK → CourseOffering
lecturerId          FK → User
title
body
pinned              bool (default: false)
createdAt, updatedAt
```

### AnnouncementView
```
id
announcementId      FK → Announcement
studentId           FK → User
viewedAt
```

### Notification
```
id
userId              FK → User
message
type                string
read                bool (default: false)
link                nullable
createdAt
```

### GradebookEntry
```
id
offeringId          FK → CourseOffering
studentId           FK → User
manualGrade         string | null
notes               string | null
updatedAt
```

### AITutorRule
```
id
offeringId          FK → CourseOffering
rules               text
updatedAt
```

---

## Key Relationships

```
Faculty         → has many Departments
Department      → has many Courses, Users
AcademicSession → has many Semesters
Semester        → has many CourseOfferings
Course          → has many CourseOfferings
CourseOffering  → has many Materials, Tasks, Sessions, Announcements, Registrations
Task            → has many Questions, Submissions
Submission      → has many Answers
ClassSession    → has many Attendance records
```
