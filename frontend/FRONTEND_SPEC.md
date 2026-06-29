# Student Pages

- Sign up
- Sign in
- Forgot password
- Reset password
- Dashboard
- Course discovery
- Course detail — preview mode
- Course detail — full mode
- My courses
- Sessions list
- Session detail
- Task list
- Task detail
- Task submission — review
- Announcement list
- Announcement detail
- Attendance history
- Grades
- Submission history
- Notifications
- AI tutor chat
- Analytics — overall
- Analytics — per course
- Profile & settings
- Registration status
- Lecturer profile

# Lecturer Pages

- Sign up
- Sign in
- Forgot password
- Reset password
- Dashboard
- My courses
- Course detail
- Sessions list
- Session detail
- Create / edit session
- Student list
- Student profile
- Task list
- Task detail
- Create / edit task
- Student submission view
- Task grading
- AI grading review
- Materials list
- Upload material
- Announcement list
- Create announcement
- Attendance marking
- Attendance records
- Gradebook
- AI tutor chat
- AI tutor settings
- Analytics — per course
- Analytics — overall

# HOD Pages

- Department students list
- Department student detail
- Department lecturers list
- Department lecturer detail
- Courses list
- Course definition detail
- Create / edit course definition
- Course offerings list
- Course offering detail
- Create course offering

# Admin

- Sign in
- Dashboard
- Faculties list
- Faculty detail
- Create / edit faculty
- Departments list
- Department detail
- Create / edit department
- Academic sessions list
- Academic session detail
- Create / edit academic session
- Semesters list
- Semester detail
- Create / edit semester

# Shared Components & Mini Screens

## SC-01 — Sidebar

### What happens here

- Provides primary navigation for the student.
- Highlights the currently active page.
- Shows notification badge on the Notifications link when there are unread notifications.
- Shows student name and matric number at the bottom.
- Provides sign out option.

### Major components

- Nav links: Dashboard, My Courses, Course Discovery, AI Tutor, Analytics, Notifications, Profile.
- Student identity block — name and matric number.
- Sign out button.

## SC-02 — Top bar

### What happens here

- Shows the current page title.
- Provides quick access to notifications.

### Major components

- Page title.
- Notification bell — opens a dropdown preview of the latest notifications.

## SC-03 — Course card

### Page variant

- Discovery variant — shows course info with a Register button.
- My courses variant — shows course info with a Drop option in a context menu.
- Dashboard variant — shows course info as a simple navigation trigger.

### What happens here

- Gives the student a quick glance at a course.
- Acts as a navigation trigger into the course.

### Major components

- Course title and code.
- Lecturer name (Acts as a navigation trigger to Lecturer Profile).
- Status badge — shows if the course is active or pending.
- Action area — varies depending on the variant.

## SC-L-01 — Sidebar (Lecturer)

### What happens here

- Provides primary navigation for the lecturer.
- Highlights the currently active page.
- Shows lecturer name and staff ID at the bottom.
- Provides sign out option.

### Major components

- Nav links: Dashboard, My Courses, AI Tutor, Analytics, Profile.
- Lecturer identity block — name and staff ID.
- Sign out button.

## SC-L-02 — Top bar (Lecturer)

### What happens here

- Shows the current page title.
- Provides quick access to notifications.

### Major components

- Page title.
- Notification bell — opens a dropdown preview of the latest notifications.

## SC-L-03 — Course card (Lecturer)

### What happens here

- Gives the lecturer a quick glance at a course.
- Acts as a navigation trigger into the course.

### Major components

- Course title and code.
- Department and level.
- Total students enrolled.
- Active session indicator — shows if there is an ongoing session.

## SC-H-01 — Sidebar (HOD)

### What happens here

- Provides primary navigation for the HOD.
- Extends the lecturer sidebar with an additional department management section.
- Highlights the currently active page.
- Shows HOD name and staff ID at the bottom.
- Provides sign out option.

### Major components

- Nav links (inherited from lecturer): Dashboard, My Courses, AI Tutor, Analytics, Profile.
- Department nav links: Students, Lecturers, Courses.
- HOD identity block — name and staff ID.
- Sign out button.

## SC-H-02 — Top bar (HOD)

### What happens here

- Same as the lecturer top bar.
- Shows the current page title.
- Provides quick access to notifications.

### Major components

- Page title.
- Notification bell — opens a dropdown preview of the latest notifications.

## SC-A-01 — Sidebar (Admin)

### What happens here

- Provides primary navigation for the Admin.
- Highlights the currently active page.
- Shows admin name at the bottom.
- Provides sign out option.

### Major components

- Nav links: Dashboard, Faculties, Academic Sessions, Profile.
- Admin identity block — name.
- Sign out button.

## SC-A-02 — Top bar (Admin)

### What happens here

- Shows the current page title.
- Provides quick access to notifications.

### Major components

- Page title.
- Notification bell — opens a dropdown preview of the latest notifications.

# Student Pages

## Page 1 — Sign up

### Page variant

- None.

### What happens here

- Student fills in personal and academic details to create an account.
- Redirected to Sign in on success.

### Major components

- Sign up form — collects all required student details.
- Sign in link — for students who already have an account.

### Navigation flow

- Comes from: Sign in. Leads to: Sign in.

### References

- None.

## Page 2 — Sign in

### Page variant

- None.

### What happens here

- Student signs in using email or matric number and password.
- Redirected to Dashboard on success.

### Major components

- Sign in form — accepts email or matric number and password.
- Forgot password link — navigates to Forgot password.
- Sign up link — for students who don't have an account.

### Navigation flow

- Comes from: Sign up, Forgot password. Leads to: Dashboard.

### References

- None.

## Page 3 — Forgot password

### Page variant

- None.

### What happens here

- Student submits their email to receive a password reset link.
- Page shows a confirmation message after submission.

### Major components

- Forgot password form — accepts email address.
- Sign in link — for students who remember their password.

### Navigation flow

- Comes from: Sign in. Leads to: Reset password (via email link).

### References

- None.

## Page 4 — Reset password

### Page variant

- None.

### What happens here

- Student sets a new password after clicking the reset link from their email.
- Redirected to Sign in on success.

### Major components

- Reset password form — accepts new password and confirmation.

### Navigation flow

- Comes from: Forgot password (via email link). Leads to: Sign in.

### References

- None.

## Page 5 — Dashboard

### Page variant

- None.

### What happens here

- Student gets a high level overview of their academic activity.
- Sees their registered courses.
- Sees upcoming task deadlines across all courses.
- Sees recent unread announcements across all courses.
- Sees quick stats on their overall performance.

### Major components

- Registered courses strip — a row of SC-03 course cards showing the student's active courses.
- Upcoming deadlines list — lists the next few tasks due across all courses.
- Recent announcements list — lists the latest unread announcements across all courses.
- Quick stats strip — shows high level numbers like attendance rate, GPA, and pending tasks.

### Navigation flow

- Comes from: Sign in. Leads to: Course detail, Task detail, Announcement detail, Notifications.

### References

## SC-01 Sidebar

## SC-02 Top bar

## SC-03 Course card (Dashboard variant)

## Page 6 — Course discovery

### Page variant

- None.

### What happens here

- Student browses all available courses for the current semester.
- Filters courses by department, level, or searches by name or code.
- Clicks a course to view more details and register.

### Major components

- Search and filter bar — allows filtering by department, level and searching by name or code.
- Course list — displays available courses as SC-03 course cards.
- Pagination controls — navigates through the course list.

### Navigation flow

- Comes from: Sidebar. Leads to: Course detail (preview mode).

### References

## SC-01 Sidebar

## SC-02 Top bar

## SC-03 Course card (Discovery variant)

## Page 7 — Course detail (preview mode)

### Page variant

- Preview mode — for unregistered students or students with a pending registration.

### What happens here

- Student views the details of a course before or during registration.
- Registers for the course.
- Sees their current registration status if already applied.
- Can re-apply if previously rejected.

### Major components

- Course info block — shows course title, code, level, department, lecturer name and description.
- Registration status badge — shows current status: unregistered, pending, approved or rejected.
- Registration action button — triggers registration or shows current status state.

### Navigation flow

- Comes from: Course discovery. Leads to: Course detail (full mode) if approved.

### References

## SC-01 Sidebar

## SC-02 Top bar

## Page 8 — Course detail (full mode)

### Page variant

- Full mode — for registered and approved students only.

### What happens here

- Student accesses all content and activities for a course from one place.
- Navigates between course content using tabs.
- Can drop the course from here.

### Major components

- Course header — shows course title, code, lecturer name and student's attendance rate for this course.
- Tab bar — switches between the seven course content sections: Overview, Schedule, Materials, Assignments, Announcements, Attendance, Scores.
- Drop course button — allows the student to drop the course.
- Tab content area — renders the content of the currently active tab.

### Navigation flow

- Comes from: My courses, Dashboard, Course detail (preview mode). Leads to: Session detail, Task detail, Announcement detail.

### References

## SC-01 Sidebar

## SC-02 Top bar

## Page 9 — My courses

### Page variant

- None.

### What happens here

- Student sees all courses they are registered for.
- Filters between active and pending courses.
- Drops a course from here.
- Navigates into a course.

### Major components

- Filter tabs — switches between All, Active and Pending courses.
- Course grid — displays registered courses as SC-03 course cards.

### Navigation flow

- Comes from: Sidebar, Dashboard. Leads to: Course detail (full mode), Course detail (preview mode).

### References

## SC-01 Sidebar

## SC-02 Top bar

## SC-03 Course card (My courses variant)

## Page 10 — Sessions list

### Page variant

- None. Lives as the Schedule tab inside Course detail (full mode).

### What happens here

- Student sees all scheduled sessions for the course.
- Filters sessions by status — upcoming, completed, cancelled.
- Clicks a session to view its details.

### Major components

- Filter chips — filters sessions by status.
- Sessions list — displays all sessions with title, date, time, venue, status and attendance indicator.

### Navigation flow

- Comes from: Course detail (full mode) — Schedule tab. Leads to: Session detail.

### References

## SC-01 Sidebar

## SC-02 Top bar

## Page 11 — Session detail

### Page variant

- None.

### What happens here

- Student views the details of a specific class session.
- Sees their attendance status for that session.
- Sees tasks that were part of that session and their submission status.

### Major components

- Session info block — shows title, date, time, venue, status and session notes.
- Attendance status block — shows whether attendance has been marked and the student's status for that session.
- Session tasks block — lists tasks associated with that session with title, submission status and score if graded.

### Navigation flow

- Comes from: Sessions list. Leads to: Task detail.

### References

## SC-01 Sidebar

## SC-02 Top bar

## Page 12 — Task list

### Page variant

- None. Lives as the Assignments tab inside Course detail (full mode).

### What happens here

- Student sees all tasks for the course.
- Filters tasks by status — upcoming, submitted, graded, overdue.
- Clicks a task to view its details and submit.

### Major components

- Filter chips — filters tasks by status.
- Task list — displays all tasks with title, due date, max score and submission status.

### Navigation flow

- Comes from: Course detail (full mode) — Assignments tab. Leads to: Task detail.

### References

## SC-01 Sidebar

## SC-02 Top bar

## Page 13 — Task detail

### Page variant

- Unsubmitted — student can view the task and submit answers.
- Submitted — student sees their submitted answers in read only mode.
- Graded — student sees their score and feedback alongside their submission.

### What happens here

- Student views the full task including instructions and questions.
- Answers and submits the task.
- Views their submission after submitting.
- Views their grade and feedback after grading.

### Major components

- Task info block — shows title, description, due date and total score.
- Questions area — renders each question based on its type for the student to answer.
- Submission action button — submits the student's answers.
- Grade and feedback block — shows score and lecturer feedback, visible only after grading.
- Submission history link — navigates to the full submission history for this task.

### Navigation flow

- Comes from: Task list, Dashboard. Leads to: Submission history.

### References

## SC-01 Sidebar

## SC-02 Top bar

## Page 14 — Task submission review

### Page variant

- None.

### What happens here

- Student sees a confirmation of their submitted task.
- Reviews what they submitted before leaving the page.

### Major components

- Submission summary block — shows submitted answers in read only mode and submission timestamp.
- Back to task button — returns the student to the task detail page.

### Navigation flow

- Comes from: Task detail. Leads to: Task detail.

### References

## SC-01 Sidebar

## SC-02 Top bar

## Page 15 — Submission history

### Page variant

- None.

### What happens here

- Student sees a log of all submission attempts for a specific task.
- Views the details of each attempt.

### Major components

- Submission history list — displays all attempts with attempt number, submission date and time, and status.

### Navigation flow

- Comes from: Task detail. Leads to: Task detail.

### References

## SC-01 Sidebar

## SC-02 Top bar

## Page 16 — Announcement list

### Page variant

- None. Lives as the Announcements tab inside Course detail (full mode).

### What happens here

- Student sees all announcements posted by the lecturer for the course.
- Sees which announcements are unread.
- Clicks an announcement to read the full content.

### Major components

- Announcements list — displays all announcements with title, date posted, lecturer name and unread indicator.

### Navigation flow

- Comes from: Course detail (full mode) — Announcements tab. Leads to: Announcement detail.

### References

## SC-01 Sidebar

## SC-02 Top bar

## Page 17 — Announcement detail

### Page variant

- None.

### What happens here

- Student reads the full content of an announcement.
- Announcement is marked as viewed on open.

### Major components

- Announcement content block — shows title, lecturer name, date posted and full body text.

### Navigation flow

- Comes from: Announcement list, Dashboard. Leads to: Announcement list.

### References

## SC-01 Sidebar

## SC-02 Top bar

## Page 18 — Attendance history

### Page variant

- None. Lives as the Attendance tab inside Course detail (full mode).

### What happens here

- Student sees a session by session record of their attendance for the course.
- Sees a summary of their overall attendance rate for the course.

### Major components

- Attendance summary block — shows total sessions, sessions present, sessions absent and overall attendance percentage.
- Attendance list — displays each session with date and attendance status (present or absent).

### Navigation flow

- Comes from: Course detail (full mode) — Attendance tab. Leads to: None.

### References

## SC-01 Sidebar

## SC-02 Top bar

## Page 19 — Grades

### Page variant

- None. Lives as the Scores tab inside Course detail (full mode).

### What happens here

- Student sees their grades for all tasks in the course.
- Sees a summary of their overall performance for the course.
- Clicks a task to view its full detail and feedback.

### Major components

- Grades summary block — shows total score, average and overall grade for the course.
- Grades list — displays each task with title, score, max score and date graded.

### Navigation flow

- Comes from: Course detail (full mode) — Scores tab. Leads to: Task detail.

### References

## SC-01 Sidebar

## SC-02 Top bar

## Page 20 — Notifications

### Page variant

- None.

### What happens here

- Student sees all notifications from the system.
- Marks individual notifications as read.
- Marks all notifications as read at once.
- Clicks a notification to navigate to the relevant page.

### Major components

- Mark all as read button — marks all unread notifications as read at once.
- Notifications list — displays all notifications with type, message, course name, timestamp and read/unread state.

### Navigation flow

- Comes from: Sidebar, Top bar notification bell. Leads to: Any page a notification links to.

### References

## SC-01 Sidebar

## SC-02 Top bar

## Page 21 — AI tutor chat

### Page variant

- None.

### What happens here

- Student selects a course to scope the conversation.
- Asks questions and gets responses from the AI tutor.
- Switches to a different course at any point, starting a new scoped conversation.
- Optionally pins a specific course material as context for the conversation.
- Conversation history is maintained per course for the duration of the session.

### Major components

- Course selector panel — lists all enrolled courses, allows the student to select or switch the active course at any point.
- Chat window — displays the conversation for the currently selected course.
- Material context selector — allows the student to pin a specific material for the AI to reference.
- Chat input — text input and send button.

### Navigation flow

- Comes from: Sidebar. Leads to: None.

### References

## SC-01 Sidebar

## SC-02 Top bar

## Page 22 — Analytics — overall

### Page variant

- None.

### What happens here

- Student sees a high level summary of their academic performance across all courses.
- Views their GPA, attendance rate and assignment completion rate.
- Sees a performance breakdown per course.

### Major components

- Overall stats strip — shows GPA, attendance rate and assignment completion rate as stat cards.
- Course performance table — lists each course with attendance rate, average grade and tasks submitted.

### Navigation flow

- Comes from: Sidebar. Leads to: Analytics — per course.

### References

## SC-01 Sidebar

## SC-02 Top bar

## Page 23 — Analytics — per course

### Page variant

- None.

### What happens here

- Student sees a detailed performance breakdown for a single course.
- Views their attendance trend across sessions.
- Views their grade trend across tasks.

### Major components

- Course header — shows course name and semester.
- Attendance breakdown — shows attendance status per session as a visual chart.
- Grade breakdown — shows score per task as a visual chart.
- Summary stats block — shows attendance rate, average score and tasks submitted for the course.

### Navigation flow

- Comes from: Analytics — overall. Leads to: None.

### References

## SC-01 Sidebar

## SC-02 Top bar

## Page 24 — Profile & settings

### Page variant

- None.

### What happens here

- Student views their personal and academic information.
- Updates their password.
- Manages their notification preferences.

### Major components

- Personal info block — shows full name, email, matric number, department and level.
- Change password form — allows the student to update their password.
- Notification preferences — toggles for the types of notifications the student wants to receive.

### Navigation flow

- Comes from: Sidebar. Leads to: None.

### References

## SC-01 Sidebar

## SC-02 Top bar

## Page 25 — Registration status

### Page variant

- None.

### What happens here

- Student sees all their course registration requests and their current states.
- Drops an approved registration from here.

### Major components

- Registration list — displays each registration request with course title, code, date applied and status badge.
- Drop action — available per approved registration, triggers a confirmation before dropping.

### Navigation flow

- Comes from: Sidebar, Course detail (preview mode). Leads to: Course detail (preview mode).

### References

## SC-01 Sidebar

## SC-02 Top bar

## Page 26 — Lecturer profile

### Page variant

- None.

### What happens here

- Student views the lecturer's professional profile.
- Shows contact details and a list of all courses they are currently assigned to teach.

### Major components

- Lecturer profile block — name, contact info, department.
- Course list — all assigned courses.

### Navigation flow

- Comes from: SC-03 Course card, Course detail pages, Announcement pages. Leads to: None.

### References

## SC-01 Sidebar

## SC-02 Top bar

# Lecturer Pages

## Page 1 — Sign up (Lecturer)

### Page variant

- Similar to Student sign up but collects lecturer specific details.

### What happens here

- Lecturer fills in personal and professional details to create an account.
- Redirected to Sign in on success.

### Major components

- Sign up form — collects all required lecturer details including staff ID.
- Sign in link — for lecturers who already have an account.

### Navigation flow

- Comes from: Sign in. Leads to: Sign in.

### References

- None.

## Page 2 — Sign in (Lecturer)

### Page variant

- Similar to Student sign in but accepts staff ID instead of matric number.

### What happens here

- Lecturer signs in using email or staff ID and password.
- Redirected to Dashboard on success.

### Major components

- Sign in form — accepts email or staff ID and password.
- Forgot password link — navigates to Forgot password.
- Sign up link — for lecturers who don't have an account.

### Navigation flow

- Comes from: Sign up, Forgot password. Leads to: Dashboard.

### References

- None.

## Page 3 — Forgot password (Lecturer)

### Page variant

- Similar to Student forgot password.

### What happens here

- Lecturer submits their email to receive a password reset link.
- Page shows a confirmation message after submission.

### Major components

- Forgot password form — accepts email address.
- Sign in link — for lecturers who remember their password.

### Navigation flow

- Comes from: Sign in. Leads to: Reset password (via email link).

### References

- None.

## Page 4 — Reset password (Lecturer)

### Page variant

- Similar to Student reset password.

### What happens here

- Lecturer sets a new password after clicking the reset link from their email.
- Redirected to Sign in on success.

### Major components

- Reset password form — accepts new password and confirmation.

### Navigation flow

- Comes from: Forgot password (via email link). Leads to: Sign in.

### References

- None.

## Page 5 — Dashboard (Lecturer)

### Page variant

- None.

### What happens here

- Lecturer gets a high level overview of their teaching activity.
- Sees all their assigned courses.
- Sees upcoming sessions across all courses.
- Sees pending tasks that need grading across all courses.
- Sees recent student submissions across all courses.

### Major components

- Assigned courses strip — a row of course cards showing the lecturer's active courses.
- Upcoming sessions list — lists the next few sessions across all courses.
- Pending grading list — lists tasks that have ungraded student submissions.
- Recent submissions list — lists the latest student submissions across all courses.

### Navigation flow

- Comes from: Sign in. Leads to: Course detail, Session detail, Task detail, Student submission view.

### References

## SC-L-01 Sidebar (Lecturer)

## SC-L-02 Top bar (Lecturer)

## SC-L-03 Course card (Lecturer)

## Page 6 — My courses (Lecturer)

### Page variant

- None.

### What happens here

- Lecturer sees all courses assigned to them.
- Filters courses by semester.
- Navigates into a course.

### Major components

- Semester filter — switches between semesters.
- Course grid — displays assigned courses as SC-L-03 course cards.

### Navigation flow

- Comes from: Sidebar, Dashboard. Leads to: Course detail.

### References

## SC-L-01 Sidebar (Lecturer)

## SC-L-02 Top bar (Lecturer)

## SC-L-03 Course card (Lecturer)

## Page 7 — Course detail (Lecturer)

### Page variant

- None.

### What happens here

- Lecturer accesses all content and activities for a course from one place.
- Navigates between course content using tabs.
- Gets a quick overview of the course stats.

### Major components

- Course header — shows course title, code, department, level and total students enrolled.
- Tab bar — switches between the course content sections: Overview, Sessions, Students, Tasks, Materials, Announcements, Attendance, Gradebook.
- Tab content area — renders the content of the currently active tab.

### Navigation flow

- Comes from: My courses, Dashboard. Leads to: Session detail, Student profile, Task detail, Attendance marking, Gradebook.

### References

## SC-L-01 Sidebar (Lecturer)

## SC-L-02 Top bar (Lecturer)

## Page 8 — Sessions list (Lecturer)

### Page variant

- None. Lives as the Sessions tab inside Course detail.

### What happens here

- Lecturer sees all sessions for the course.
- Filters sessions by status — upcoming, completed, cancelled.
- Creates a new session.
- Navigates into a session to view its details.

### Major components

- Create session button — navigates to Create / edit session page.
- Filter chips — filters sessions by status.
- Sessions list — displays all sessions with title, date, time, venue and status.

### Navigation flow

- Comes from: Course detail — Sessions tab. Leads to: Session detail, Create / edit session.

### References

## SC-L-01 Sidebar (Lecturer)

## SC-L-02 Top bar (Lecturer)

## Page 9 — Session detail (Lecturer)

### Page variant

- None.

### What happens here

- Lecturer views the details of a specific class session.
- Sees attendance summary for that session.
- Sees tasks associated with that session.
- Navigates to attendance marking for that session.
- Edits or cancels the session.

### Major components

- Session info block — shows title, date, time, venue, status and notes.
- Attendance summary block — shows total present, absent and attendance percentage for that session.
- Session tasks block — lists tasks associated with that session.
- Edit session button — navigates to Create / edit session page.
- Mark attendance button — navigates to Attendance marking page.

### Navigation flow

- Comes from: Sessions list, Dashboard. Leads to: Attendance marking, Create / edit session.

### References

## SC-L-01 Sidebar (Lecturer)

## SC-L-02 Top bar (Lecturer)

## Page 10 — Create / edit session (Lecturer)

### Page variant

- Create mode — lecturer creates a new session.
- Edit mode — lecturer edits an existing session.

### What happens here

- Lecturer fills in session details to create or update a session.
- Can cancel an existing session from edit mode.
- Redirected back to Sessions list on success.

### Major components

- Session form — collects session title, date, time, venue and notes.
- Cancel session button — only visible in edit mode, cancels the session after confirmation.
- Save button — creates or updates the session.

### Navigation flow

- Comes from: Sessions list, Session detail. Leads to: Sessions list.

### References

## SC-L-01 Sidebar (Lecturer)

## SC-L-02 Top bar (Lecturer)

## Page 11 — Student list (Lecturer)

### Page variant

- None. Lives as the Students tab inside Course detail.

### What happens here

- Lecturer sees all students enrolled in the course.
- Searches for a specific student.
- Approves or rejects pending student registration requests.
- Navigates to a student's profile.

### Major components

- Search bar — filters students by name or matric number.
- Pending approvals section — lists students with pending registration requests with approve and reject actions.
- Student list — displays all enrolled students with name, matric number and attendance rate.

### Navigation flow

- Comes from: Course detail — Students tab. Leads to: Student profile.

### References

## SC-L-01 Sidebar (Lecturer)

## SC-L-02 Top bar (Lecturer)

## Page 12 — Student profile (Lecturer)

### Page variant

- None.

### What happens here

- Lecturer views a specific student's profile and academic details for the course.
- Sees the student's attendance record for the course.
- Sees the student's grades for the course.
- Sees the student's submission history for the course.

### Major components

- Student info block — shows student name, matric number, department and level.
- Attendance summary block — shows attendance rate and session by session record for the course.
- Grades block — shows the student's scores across all tasks for the course.
- Submission history block — lists all the student's submissions for the course.

### Navigation flow

- Comes from: Student list. Leads to: Task detail, Student submission view.

### References

## SC-L-01 Sidebar (Lecturer)

## SC-L-02 Top bar (Lecturer)

## Page 13 — Task list (Lecturer)

### Page variant

- None. Lives as the Tasks tab inside Course detail.

### What happens here

- Lecturer sees all tasks for the course.
- Filters tasks by status.
- Creates a new task.
- Navigates into a task to view submissions and grades.

### Major components

- Create task button — navigates to Create / edit task page.
- Filter chips — filters tasks by status: all, upcoming, active, graded.
- Task list — displays all tasks with title, due date, max score, submission count and grading status.

### Navigation flow

- Comes from: Course detail — Tasks tab. Leads to: Task detail, Create / edit task.

### References

## SC-L-01 Sidebar (Lecturer)

## SC-L-02 Top bar (Lecturer)

## Page 14 — Task detail (Lecturer)

### Page variant

- None.

### What happens here

- Lecturer views the full details of a task.
- Sees a summary of student submissions and grading progress.
- Enables or disables AI grading for the task.
- Uploads a marking guide or rubric for AI grading.
- Navigates to individual student submissions.
- Navigates to the full student submission list for the task.

### Major components

- Task info block — shows title, description, due date, total score and questions.
- Submission summary block — shows total submissions, graded count and pending count.
- AI grading block — shows AI grading status with toggle to enable or disable and an upload area for the marking guide.
- Student submission list — lists all students with their submission status and score.

### Navigation flow

- Comes from: Task list, Dashboard. Leads to: Student submission view, Create / edit task, AI grading review.

### References

## SC-L-01 Sidebar (Lecturer)

## SC-L-02 Top bar (Lecturer)

## Page 15 — Create / edit task (Lecturer)

### Page variant

- Create mode — lecturer creates a new task.
- Edit mode — lecturer edits an existing task.

### What happens here

- Lecturer fills in task details and adds questions.
- Sets the due date and max score.
- Saves the task.

### Major components

- Task form — collects task title, description, due date and total score.
- Questions builder — allows the lecturer to add, edit and remove questions with type, score and options.
- Save button — creates or updates the task.

### Navigation flow

- Comes from: Task list, Task detail. Leads to: Task detail.

### References

## SC-L-01 Sidebar (Lecturer)

## SC-L-02 Top bar (Lecturer)

## Page 16 — Student submission view (Lecturer)

### Page variant

- None.

### What happens here

- Lecturer views a specific student's submission for a task.
- Sees the student's answers alongside the questions.
- Navigates to grading from here.

### Major components

- Student info block — shows student name and matric number.
- Submission detail block — displays each question alongside the student's answer.
- Grade and feedback block — shows current score and feedback if already graded.
- Grade submission button — navigates to Task grading page.

### Navigation flow

- Comes from: Task detail, Student profile. Leads to: Task grading.

### References

## SC-L-01 Sidebar (Lecturer)

## SC-L-02 Top bar (Lecturer)

## Page 17 — Task grading (Lecturer)

### Page variant

- Manual grading — lecturer grades the submission manually.
- Regrade — lecturer updates an existing grade.

### What happens here

- Lecturer assigns a score and writes feedback for a student's submission.
- Saves the grade and feedback.
- Redirected back to Student submission view on success.

### Major components

- Submission review block — shows the student's answers in read only mode for reference while grading.
- Grading form — allows the lecturer to assign a score per question and write overall feedback.
- Save grade button — saves the grade and feedback.

### Navigation flow

- Comes from: Student submission view. Leads to: Student submission view.

### References

## SC-L-01 Sidebar (Lecturer)

## SC-L-02 Top bar (Lecturer)

## Page 18 — AI grading review (Lecturer)

### Page variant

- None.

### What happens here

- Lecturer sees all AI generated grades for a task.
- Reviews each AI generated grade and feedback.
- Approves or rejects individual AI generated grades.
- Approved grades are released to students.
- Rejected grades are sent back for manual grading.

### Major components

- Task info block — shows task title and total score for reference.
- AI grading list — lists all students with their AI generated score, feedback and approval status.
- Approve and reject actions — available per student grade entry.
- Bulk approve button — approves all AI generated grades at once.

### Navigation flow

- Comes from: Task detail. Leads to: Student submission view, Task grading.

### References

## SC-L-01 Sidebar (Lecturer)

## SC-L-02 Top bar (Lecturer)

## Page 19 — Materials list (Lecturer)

### Page variant

- None. Lives as the Materials tab inside Course detail.

### What happens here

- Lecturer sees all materials uploaded for the course.
- Filters materials by type.
- Sees the visibility setting of each material.
- Navigates to upload a new material.
- Deletes an existing material.

### Major components

- Upload material button — navigates to Upload material page.
- Filter chips — filters materials by type: all, notes, slides, resources.
- Materials list — displays all materials with title, type badge, upload date, visibility badge and delete action.

### Navigation flow

- Comes from: Course detail — Materials tab. Leads to: Upload material.

### References

## SC-L-01 Sidebar (Lecturer)

## SC-L-02 Top bar (Lecturer)

## Page 20 — Upload material (Lecturer)

### Page variant

- None.

### What happens here

- Lecturer uploads a new course material.
- Sets the material title, type and visibility.
- Submits the material to make it available.

### Major components

- Upload form — collects material title, type and visibility setting.
- File upload area — drag and drop or browse to select the file to upload.
- Visibility selector — sets who can access the material: students, AI or both.
- Save button — uploads and saves the material.

### Navigation flow

- Comes from: Materials list. Leads to: Materials list.

### References

## SC-L-01 Sidebar (Lecturer)

## SC-L-02 Top bar (Lecturer)

## Page 21 — Announcement list (Lecturer)

### Page variant

- None. Lives as the Announcements tab inside Course detail.

### What happens here

- Lecturer sees all announcements posted for the course.
- Sees how many students have viewed each announcement.
- Creates a new announcement.

### Major components

- Create announcement button — navigates to Create announcement page.
- Announcements list — displays all announcements with title, date posted, body preview and viewed count.

### Navigation flow

- Comes from: Course detail — Announcements tab. Leads to: Create announcement.

### References

## SC-L-01 Sidebar (Lecturer)

## SC-L-02 Top bar (Lecturer)

## Page 22 — Create announcement (Lecturer)

### Page variant

- None.

### What happens here

- Lecturer writes and posts a new announcement for the course.
- Redirected back to Announcement list on success.

### Major components

- Announcement form — collects announcement title and body.
- Post button — publishes the announcement to the course.

### Navigation flow

- Comes from: Announcement list. Leads to: Announcement list.

### References

## SC-L-01 Sidebar (Lecturer)

## SC-L-02 Top bar (Lecturer)

## Page 23 — Attendance marking (Lecturer)

### Page variant

- None.

### What happens here

- Lecturer marks attendance for students in a specific session.
- Sees all students enrolled in the course.
- Marks each student as present or absent.
- Saves the attendance record for the session.

### Major components

- Session info block — shows the session title, date and time for reference.
- Student attendance list — lists all enrolled students with a present or absent toggle per student.
- Save attendance button — saves the attendance record for the session.

### Navigation flow

- Comes from: Session detail. Leads to: Session detail.

### References

## SC-L-01 Sidebar (Lecturer)

## SC-L-02 Top bar (Lecturer)

## Page 24 — Attendance records (Lecturer)

### Page variant

- None.

### What happens here

- Lecturer views the full attendance record for all students across all sessions.
- Filters by session or student.
- Exports the attendance record to CSV or PDF.

### Major components

- Export button — exports the attendance record in CSV or PDF format.
- Filter controls — filters the record by session or student.
- Attendance table — displays all students against all sessions with present or absent status per cell.

### Navigation flow

- Comes from: Course detail — Attendance tab. Leads to: None.

### References

## SC-L-01 Sidebar (Lecturer)

## SC-L-02 Top bar (Lecturer)

## Page 25 — Gradebook (Lecturer)

### Page variant

- None.

### What happens here

- Lecturer views the full grade record for all students across all tasks in the course.
- Hidden from students.
- Exports the gradebook to CSV or PDF.

### Major components

- Export button — exports the gradebook in CSV or PDF format.
- Gradebook table — displays all students against all tasks with scores per cell and a total column.

### Navigation flow

- Comes from: Course detail — Gradebook tab. Leads to: Student submission view.

### References

## SC-L-01 Sidebar (Lecturer)

## SC-L-02 Top bar (Lecturer)

## Page 26 — AI tutor chat (Lecturer)

### Page variant

- None.

### What happens here

- Lecturer selects a course to scope the conversation.
- Asks questions and gets responses from the AI tutor.
- Switches to a different course at any point.
- Optionally pins a specific course material as context for the conversation.
- Conversation history is maintained per course for the duration of the session.

### Major components

- Course selector panel — lists all assigned courses, allows the lecturer to select or switch the active course at any point.
- Chat window — displays the conversation for the currently selected course.
- Material context selector — allows the lecturer to pin a specific material for the AI to reference.
- Chat input — text input and send button.

### Navigation flow

- Comes from: Sidebar. Leads to: None.

### References

## SC-L-01 Sidebar (Lecturer)

## SC-L-02 Top bar (Lecturer)

## Page 27 — AI tutor settings (Lecturer)

### Page variant

- None.

### What happens here

- Lecturer configures the behaviour of the AI tutor for a specific course.
- Adds rules and instructions the AI tutor must follow when responding to students.
- Saves the configuration.

### Major components

- Course selector — selects which course the settings apply to.
- Instructions input — a text area where the lecturer writes rules and instructions for the AI tutor.
- Save button — saves the AI tutor configuration for the selected course.

### Navigation flow

- Comes from: Sidebar, Course detail. Leads to: None.

### References

## SC-L-01 Sidebar (Lecturer)

## SC-L-02 Top bar (Lecturer)

## Page 28 — Analytics — per course (Lecturer)

### Page variant

- None.

### What happens here

- Lecturer views detailed performance data for a single course.
- Sees overall attendance rate and trend across sessions.
- Sees grade distribution across all tasks.
- Sees student engagement and submission rates.

### Major components

- Course header — shows course name and semester.
- Attendance breakdown — shows attendance rate and trend across sessions.
- Grade distribution block — shows score spread across all students for each task.
- Submission rate block — shows how many students submitted each task.
- Student performance table — lists each student with their attendance rate and average grade.

### Navigation flow

- Comes from: Analytics — overall, Course detail. Leads to: Student profile.

### References

## SC-L-01 Sidebar (Lecturer)

## SC-L-02 Top bar (Lecturer)

## Page 29 — Analytics — overall (Lecturer)

### Page variant

- None.

### What happens here

- Lecturer sees a high level summary of performance data across all their assigned courses.
- Sees attendance and submission rates per course.
- Navigates into a specific course for detailed analytics.

### Major components

- Overall stats strip — shows aggregate numbers across all courses such as average attendance rate and average submission rate.
- Course analytics table — lists each assigned course with attendance rate, average grade and submission rate.

### Navigation flow

- Comes from: Sidebar. Leads to: Analytics — per course.

### References

## SC-L-01 Sidebar (Lecturer)

## SC-L-02 Top bar (Lecturer)

# HOD Pages

## Page 1 — Department students list (HOD)

### Page variant

- None.

### What happens here

- HOD views all students in the department.
- Searches for a specific student by name or matric number.
- Filters students by level.
- Navigates into a specific student's detail.

### Major components

- Search bar — filters students by name or matric number.
- Level filter — filters students by level.
- Students table — displays all students with name, matric number and level.

### Navigation flow

- Comes from: Sidebar. Leads to: Department student detail.

### References

## SC-H-01 Sidebar (HOD)

## SC-H-02 Top bar (HOD)

## Page 2 — Department student detail (HOD)

### Page variant

- None.

### What happens here

- HOD views a specific student's personal and academic details.
- Updates the student's level offset.

### Major components

- Student info block — shows student name, matric number, department and current level.
- Level offset control — allows the HOD to update the student's level offset.
- Save button — saves the updated level offset.

### Navigation flow

- Comes from: Department students list. Leads to: None.

### References

## SC-H-01 Sidebar (HOD)

## SC-H-02 Top bar (HOD)

## Page 3 — Department lecturers list (HOD)

### Page variant

- None.

### What happens here

- HOD views all lecturers in the department.
- Searches for a specific lecturer by name or staff ID.
- Navigates into a specific lecturer's detail.

### Major components

- Search bar — filters lecturers by name or staff ID.
- Lecturers table — displays all lecturers with name, staff ID and assigned courses count.

### Navigation flow

- Comes from: Sidebar. Leads to: Department lecturer detail.

### References

## SC-H-01 Sidebar (HOD)

## SC-H-02 Top bar (HOD)

## Page 4 — Department lecturer detail (HOD)

### Page variant

- None.

### What happens here

- HOD views a specific lecturer's personal and academic details.
- Sees all courses currently assigned to the lecturer.

### Major components

- Lecturer info block — shows lecturer name, staff ID and department.
- Assigned courses block — lists all courses currently assigned to the lecturer with course title and code.

### Navigation flow

- Comes from: Department lecturers list. Leads to: None.

### References

## SC-H-01 Sidebar (HOD)

## SC-H-02 Top bar (HOD)

## Page 5 — Courses list (HOD)

### Page variant

- None.

### What happens here

- HOD views all course definitions in the department.
- Searches for a specific course by name or code.
- Navigates into a specific course definition.
- Creates a new course definition.

### Major components

- Create course button — navigates to Create / edit course definition page.
- Search bar — filters courses by name or code.
- Courses table — displays all course definitions with title, code and level.

### Navigation flow

- Comes from: Sidebar. Leads to: Course definition detail, Create / edit course definition.

### References

## SC-H-01 Sidebar (HOD)

## SC-H-02 Top bar (HOD)

## Page 6 — Course definition detail (HOD)

### Page variant

- None.

### What happens here

- HOD views the full details of a course definition.
- Navigates to edit the course definition.
- Deletes the course definition.
- Views all offerings for the course.
- Navigates to create a new offering for the course.

### Major components

- Course info block — shows course title, code, level, department and description.
- Edit button — navigates to Create / edit course definition in edit mode.
- Delete button — deletes the course definition after confirmation.
- Offerings section — lists all offerings for the course with semester and status.
- Create offering button — navigates to Create course offering page.

### Navigation flow

- Comes from: Courses list. Leads to: Create / edit course definition, Create course offering, Course offering detail.

### References

## SC-H-01 Sidebar (HOD)

## SC-H-02 Top bar (HOD)

## Page 7 — Create / edit course definition (HOD)

### Page variant

- Create mode — HOD creates a new course definition.
- Edit mode — HOD updates an existing course definition.

### What happens here

- HOD fills in course details to create or update a course definition.
- Saves the course definition.
- Redirected back to Courses list on success.

### Major components

- Course definition form — collects course title, code, level and description.
- Save button — creates or updates the course definition.

### Navigation flow

- Comes from: Courses list, Course definition detail. Leads to: Courses list.

### References

## SC-H-01 Sidebar (HOD)

## SC-H-02 Top bar (HOD)

## Page 8 — Course offerings list (HOD)

### Page variant

- None.

### What happens here

- HOD views all offerings for a specific course across semesters.
- Filters offerings by semester or status.
- Navigates into a specific offering.
- Creates a new offering for the course.

### Major components

- Create offering button — navigates to Create course offering page.
- Filter controls — filters offerings by semester or active status.
- Offerings table — displays all offerings with semester, assigned lecturer, status and student count.

### Navigation flow

- Comes from: Course definition detail. Leads to: Course offering detail, Create course offering.

### References

## SC-H-01 Sidebar (HOD)

## SC-H-02 Top bar (HOD)

## Page 9 — Course offering detail (HOD)

### Page variant

- None.

### What happens here

- HOD views the full details of a specific course offering.
- Activates or deactivates the offering.
- Assigns a lecturer to the offering.
- Unassigns the current lecturer from the offering.

### Major components

- Offering info block — shows semester, status, student count and assigned lecturer.
- Activate / deactivate toggle — changes the active status of the offering after confirmation.
- Assigned lecturer block — shows the currently assigned lecturer with an unassign action.
- Assign lecturer control — allows the HOD to search and assign a lecturer to the offering.

### Navigation flow

- Comes from: Course offerings list, Course definition detail. Leads to: None.

### References

## SC-H-01 Sidebar (HOD)

## SC-H-02 Top bar (HOD)

## Page 10 — Create course offering (HOD)

### Page variant

- None.

### What happens here

- HOD creates a new offering for a course by activating it for a specific semester.
- Assigns a lecturer to the offering at creation time.
- Redirected back to Course definition detail on success.

### Major components

- Offering form — collects semester and initial active status.
- Lecturer selector — allows the HOD to search and select a lecturer to assign to the offering.
- Save button — creates the offering.

### Navigation flow

- Comes from: Course definition detail, Course offerings list. Leads to: Course definition detail.

### References

## SC-H-01 Sidebar (HOD)

## SC-H-02 Top bar (HOD)

- Admin Pages

## Page 1 — Sign in (Admin)

### Page variant

- Similar to Lecturer sign in but only accepts email and password. No staff ID option.

### What happens here

- Admin signs in using email and password.
- Redirected to Dashboard on success.

### Major components

- Sign in form — accepts email and password.
- Forgot password link — navigates to Forgot password.

### Navigation flow

- Comes from: None. Leads to: Dashboard.

### References

- None.

## Page 2 — Dashboard (Admin)

### Page variant

- None.

### What happens here

- Admin gets a high level overview of the system.
- Sees total number of faculties, departments and academic sessions.
- Sees the currently active semester.
- Navigates to any major section from here.

### Major components

- Stats strip — shows total faculties, departments and active semester.
- Quick navigation blocks — large clickable blocks for Faculties, Departments and Academic Sessions.

### Navigation flow

- Comes from: Sign in. Leads to: Faculties list, Departments list, Academic sessions list.

### References

## SC-A-01 Sidebar (Admin)

## SC-A-02 Top bar (Admin)

## Page 3 — Faculties list (Admin)

### Page variant

- None.

### What happens here

- Admin views all faculties in the system.
- Searches for a specific faculty by name.
- Creates a new faculty.
- Navigates into a specific faculty.

### Major components

- Create faculty button — navigates to Create / edit faculty page.
- Search bar — filters faculties by name.
- Faculties table — displays all faculties with name and department count.

### Navigation flow

- Comes from: Sidebar, Dashboard. Leads to: Faculty detail, Create / edit faculty.

### References

## SC-A-01 Sidebar (Admin)

## SC-A-02 Top bar (Admin)

## Page 4 — Faculty detail (Admin)

### Page variant

- None.

### What happens here

- Admin views the full details of a specific faculty.
- Sees all departments under the faculty.
- Navigates to edit the faculty.
- Deletes the faculty.
- Navigates into a specific department.
- Creates a new department under the faculty.

### Major components

- Faculty info block — shows faculty name and description.
- Edit button — navigates to Create / edit faculty in edit mode.
- Delete button — deletes the faculty after confirmation.
- Departments section — lists all departments under the faculty with name and student count.
- Create department button — navigates to Create / edit department page.

### Navigation flow

- Comes from: Faculties list. Leads to: Create / edit faculty, Department detail, Create / edit department.

### References

## SC-A-01 Sidebar (Admin)

## SC-A-02 Top bar (Admin)

## Page 5 — Create / edit faculty (Admin)

### Page variant

- Create mode — Admin creates a new faculty.
- Edit mode — Admin updates an existing faculty.

### What happens here

- Admin fills in faculty details to create or update a faculty.
- Redirected back to Faculties list on success.

### Major components

- Faculty form — collects faculty name and description.
- Save button — creates or updates the faculty.

### Navigation flow

- Comes from: Faculties list, Faculty detail. Leads to: Faculties list.

### References

## SC-A-01 Sidebar (Admin)

## SC-A-02 Top bar (Admin)

## Page 6 — Department detail (Admin)

### Page variant

- None.

### What happens here

- Admin views the full details of a specific department.
- Navigates to edit the department.
- Deletes the department.

### Major components

- Department info block — shows department name, faculty and description.
- Edit button — navigates to Create / edit department in edit mode.
- Delete button — deletes the department after confirmation.

### Navigation flow

- Comes from: Faculty detail. Leads to: Create / edit department.

### References

## SC-A-01 Sidebar (Admin)

## SC-A-02 Top bar (Admin)

## Page 7 — Create / edit department (Admin)

### Page variant

- Create mode — Admin creates a new department.
- Edit mode — Admin updates an existing department.

### What happens here

- Admin fills in department details to create or update a department.
- Redirected back to Faculty detail on success.

### Major components

- Department form — collects department name, faculty and description.
- Save button — creates or updates the department.

### Navigation flow

- Comes from: Faculty detail, Department detail. Leads to: Faculty detail.

### References

## SC-A-01 Sidebar (Admin)

## SC-A-02 Top bar (Admin)

## Page 8 — Academic sessions list (Admin)

### Page variant

- None.

### What happens here

- Admin views all academic sessions in the system.
- Sees which session is currently active.
- Creates a new academic session.
- Navigates into a specific academic session.

### Major components

- Create academic session button — navigates to Create / edit academic session page.
- Academic sessions table — displays all sessions with name, start date, end date and active status.

### Navigation flow

- Comes from: Sidebar, Dashboard. Leads to: Academic session detail, Create / edit academic session.

### References

## SC-A-01 Sidebar (Admin)

## SC-A-02 Top bar (Admin)

## Page 9 — Academic session detail (Admin)

### Page variant

- None.

### What happens here

- Admin views the full details of a specific academic session.
- Sees all semesters under the session.
- Navigates to edit the academic session.
- Deletes the academic session.
- Navigates into a specific semester.
- Activates a semester.

### Major components

- Academic session info block — shows session name, start date and end date.
- Edit button — navigates to Create / edit academic session in edit mode.
- Delete button — deletes the academic session after confirmation.
- Semesters section — lists all semesters under the session with name, status and activate action.

### Navigation flow

- Comes from: Academic sessions list. Leads to: Create / edit academic session, Semester detail.

### References

## SC-A-01 Sidebar (Admin)

## SC-A-02 Top bar (Admin)

## Page 10 — Create / edit academic session (Admin)

### Page variant

- Create mode — Admin creates a new academic session.
- Edit mode — Admin updates an existing academic session.

### What happens here

- Admin fills in academic session details to create or update a session.
- Redirected back to Academic sessions list on success.

### Major components

- Academic session form — collects session name, start date and end date.
- Save button — creates or updates the academic session.

### Navigation flow

- Comes from: Academic sessions list, Academic session detail. Leads to: Academic sessions list.

### References

## SC-A-01 Sidebar (Admin)

## SC-A-02 Top bar (Admin)

## Page 11 — Semester detail (Admin)

### Page variant

- None.

### What happens here

- Admin views the full details of a specific semester.
- Activates or deactivates the semester.
- Navigates to edit the semester.
- Deletes the semester.

### Major components

- Semester info block — shows semester name, start date, end date and current status.
- Activate / deactivate toggle — changes the active status of the semester after confirmation.
- Edit button — navigates to Create / edit semester in edit mode.
- Delete button — deletes the semester after confirmation.

### Navigation flow

- Comes from: Academic session detail. Leads to: Create / edit semester.

### References

## SC-A-01 Sidebar (Admin)

## SC-A-02 Top bar (Admin)

## Page 12 — Create / edit semester (Admin)

### Page variant

- Create mode — Admin creates a new semester under an academic session.
- Edit mode — Admin updates an existing semester.

### What happens here

- Admin fills in semester details to create or update a semester.
- Redirected back to Academic session detail on success.

### Major components

- Semester form — collects semester name, start date and end date.
- Save button — creates or updates the semester.

### Navigation flow

- Comes from: Academic session detail, Semester detail. Leads to: Academic session detail.

### References

## SC-A-01 Sidebar (Admin)

## SC-A-02 Top bar (Admin)
