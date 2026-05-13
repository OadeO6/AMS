# AI Design : AMS Academic Management System

> Specification for the AI features in AMS: the course-scoped AI Tutor and the Automatic Task Grading pipeline.
> This document covers the planned architecture, stack, data flow, and integration points.
> **Status: Planned : not yet implemented.**

---

## Table of Contents

- [Overview](#overview)
- [AI Stack Summary](#ai-stack-summary)
- [Feature 1: AI Tutor](#feature-1-ai-tutor)
- [Feature 2: Automatic Task Grading](#feature-2-automatic-task-grading)
- [Shared Components](#shared-components)
- [Integration with AMS Backend](#integration-with-ams-backend)
- [Ethics & Human-in-the-Loop](#ethics--human-in-the-loop)
- [Constraints & Guardrails](#constraints--guardrails)

---

## Overview

AMS includes two AI-powered features:

1. **AI Tutor** : A course-scoped chatbot that answers student (and lecturer) questions strictly based on uploaded course materials. It uses a Retrieval-Augmented Generation (RAG) pipeline to ground every response in the actual content the lecturer has uploaded, preventing hallucinations.

2. **Automatic Task Grading** : An AI-assisted grading system that evaluates student submissions against an uploaded marking guide/rubric. Every AI-generated grade is treated as a draft and requires mandatory lecturer review before it is finalized.

Both features are designed around a **Human-in-the-Loop** principle : the AI assists, it does not decide.

---

## AI Stack Summary

| Component | Tool | Purpose |
|---|---|---|
| LLM | **Google Gemini 1.5 Flash** (tutor) · **Gemini 1.5 Pro** (grading) | Response generation |
| Embedding Model | **Gemini text-embedding** (`models/text-embedding-004`) | Converts text chunks into vector representations |
| Vector Database | **ChromaDB** | Stores and retrieves embedded material chunks |
| Document Parser | **PyMuPDF** (`fitz`) for PDFs · **python-docx** for Word files | Extracts raw text from uploaded materials |
| Chunking | **LangChain** `RecursiveCharacterTextSplitter` | Splits documents into overlapping chunks before indexing |
| Orchestration | **LangChain** | Ties the RAG retrieval and generation pipeline together |
| AI SDK | **Google Generative AI Python SDK** (`google-generativeai`) | Interface for Gemini LLM and embedding API calls |

---

## Feature 1: AI Tutor

### Purpose

The AI Tutor acts as a course assistant : available to both students and lecturers. It answers questions about course content, explains concepts, and guides students through material. Critically, it is **only allowed to use information from the course's indexed materials**. It will not draw on general knowledge outside of those documents.

Lecturers can also configure a set of custom rules or instructions that shape how the tutor behaves for their specific course (e.g. tone, topics to avoid, focus areas).

### RAG Pipeline

```
Material Upload (by Lecturer)
        │
        ▼
Document Parser
(PyMuPDF for PDF · python-docx for DOCX)
        │
        ▼
Text Chunker
(LangChain RecursiveCharacterTextSplitter)
  chunk_size=800, chunk_overlap=100
        │
        ▼
Embedding Model
(Gemini text-embedding-004)
        │
        ▼
ChromaDB
(stored with metadata: course_id, material_id, visibility)
        │
        │         At query time
        ▼
User Question ──→ Embed Question ──→ ChromaDB Retriever
                                      (top-k chunks, filtered by course_id)
                                              │
                                              ▼
                                        Gemini 1.5 Flash
                                        (question + context chunks
                                         + lecturer instructions)
                                              │
                                              ▼
                                        AI Tutor Response
```

### Material Visibility & Indexing Rules

Not all uploaded materials are available to the AI tutor. Each material has a `visibility` field that controls this:

| Visibility | Shown to Students | Indexed for AI |
|---|---|---|
| `students_only` | ✅ | ❌ |
| `ai_only` | ❌ | ✅ |
| `both` | ✅ | ✅ |

Attempting to index a `students_only` material will be rejected with a `400` error.

### Course Isolation

Every chunk stored in ChromaDB is tagged with its `course_id` as metadata. All retrieval queries filter strictly by `course_id`, ensuring a student in one course cannot receive content from another course's materials.

### Lecturer Instructions

Lecturers can provide a freeform instruction string per course (e.g. `"Always respond in a Socratic style. Do not give direct answers to assignment questions."`). This is prepended to the LLM system prompt at query time.

### Prompt Structure (AI Tutor)

```
System:
  You are an academic assistant for the course "{course_name}".
  You must only answer using the provided course material excerpts below.
  If the answer is not found in the materials, say so clearly : do not guess.
  {lecturer_instructions}

Context (retrieved chunks):
  [Chunk 1] ...
  [Chunk 2] ...
  ...

User:
  {student_question}
```

---

## Feature 2: Automatic Task Grading

### Purpose

When a lecturer enables AI grading for a task, submitted student responses are evaluated by the LLM against the uploaded marking guide. The system produces a score and written feedback for each submission. This output is flagged as an **AI draft** : the lecturer must review and either approve or override it before the grade is visible to the student.

### Grading Pipeline

```
Lecturer uploads Marking Guide
        │
        ▼
Document Parser extracts rubric text
(PyMuPDF / python-docx)
        │
        ▼
Lecturer enables AI grading on the task
        │
        │       When student submits
        ▼
Student Submission + Marking Guide
        │
        ▼
Gemini 1.5 Pro
(structured prompt: rubric + submission → JSON output)
        │
        ▼
{ "score": <int>, "feedback": "<string>", "breakdown": [...] }
        │
        ▼
Stored as gradingStatus = "ai_draft"
        │
        ▼
Lecturer reviews → approves or overrides
        │
        ▼
gradingStatus = "ai_approved" or "manually_graded"
        │
        ▼
Grade visible to student
```

### Grading Status Lifecycle

```
ungraded ──→ ai_draft ──→ ai_approved
                     └──→ manually_graded  (lecturer overrides score)
```

Manual grading (no AI) goes directly: `ungraded → manually_graded`.

### Prompt Structure (Grading)

```
System:
  You are an academic grader. You will be given a student submission and a marking guide.
  Evaluate the submission strictly against the marking guide criteria.
  Respond ONLY with a valid JSON object in the following format:
  {
    "score": <integer>,
    "max_score": <integer>,
    "feedback": "<overall feedback string>",
    "breakdown": [
      { "criterion": "<criterion name>", "awarded": <int>, "max": <int>, "comment": "<string>" }
    ]
  }
  Do not include any text outside the JSON object.

Marking Guide:
  {rubric_text}

Student Submission:
  {submission_text}
```

### Supported Submission Types

| Task Type | Grading Approach |
|---|---|
| `free_text` | LLM evaluates written response against rubric |
| `document_upload` | Document parsed first, then evaluated as text |
| `mcq` | Rule-based auto-grading (no LLM required) : future feature |

---

## Shared Components

### Document Parser

A shared utility used by both the indexing pipeline (AI Tutor) and the grading pipeline.

```python
# Supports:
# - PDF files via PyMuPDF (fitz)
# - Word documents via python-docx

def parse_document(file_path: str, mime_type: str) -> str:
    if mime_type == "application/pdf":
        return parse_pdf(file_path)       # PyMuPDF
    elif mime_type in ("application/vnd.openxmlformats-officedocument"
                       ".wordprocessingml.document",):
        return parse_docx(file_path)      # python-docx
    else:
        raise UnsupportedFileTypeError(mime_type)
```

### ChromaDB Collection Structure

One ChromaDB collection is used for the entire system. Each document chunk is stored with the following metadata:

```json
{
  "course_id": "uuid",
  "material_id": "uuid",
  "visibility": "ai_only | both",
  "chunk_index": 0,
  "source_filename": "lecture_3_notes.pdf"
}
```

Retrieval always filters by `course_id` and `visibility` to enforce isolation and access rules.

---

## Integration with AMS Backend

The AI features integrate into the existing FastAPI layered architecture as additional services.

```
backend/src/app/api/v1/ai.py              ← route handlers for /tutor and /grading endpoints
    │
    ▼
backend/src/app/services/ai_tutor.py      ← RAG pipeline: retrieve chunks → call Gemini → return response
backend/src/app/services/ai_grading.py    ← parse submission + rubric → call Gemini → store ai_draft result
    │
    ▼
backend/src/app/repositories/chroma.py    ← ChromaDB read/write (index material, retrieve chunks)
backend/src/app/repositories/material.py  ← fetch material file path + PostgreSQL metadata
    │
    ▼
ChromaDB (vectors) + PostgreSQL (metadata) + File Storage (raw files)
```

New background task via ARQ:

- `index_material_task` : triggered when a lecturer uploads a material with `ai_only` or `both` visibility. Parses, chunks, embeds, and stores to ChromaDB asynchronously so the upload endpoint returns immediately.

---

## Ethics & Human-in-the-Loop

AMS is designed so that AI outputs are always subordinate to human judgment:

- **AI Tutor** responses are clearly labelled as AI-generated in the UI.
- **AI Grading** results are never exposed to students until a lecturer has reviewed and approved them.
- Lecturers can override any AI-generated score at any time, even after approval (`manually_graded`).
- Bulk approval of AI grades is supported, but the lecturer is always made aware of what they are approving.
- The AI tutor is explicitly restricted from answering outside course materials : reducing the risk of misinformation.

---

## Constraints & Guardrails

- A marking guide **must** be uploaded before AI grading can be enabled on a task. Attempting to enable it without a guide returns `400`.
- Only materials with visibility `ai_only` or `both` are eligible for indexing. Indexing `students_only` material returns `400`.
- The AI tutor operates per-course : it has no awareness of other courses or global system data.
- Gemini API keys are stored as environment variables and never exposed in API responses or logs.
- All AI-generated content is stored in the database : responses are not streamed and discarded. This supports auditability.
