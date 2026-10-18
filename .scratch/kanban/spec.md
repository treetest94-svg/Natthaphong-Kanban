# Kanban specification

## Objective
Build a cloud-persisted three-column Kanban application and provide public GitHub and frontend links.

## Acceptance criteria
1. Cards appear under To do, Doing or Done according to status.
2. A nonempty task can be created in any column.
3. A card can move between all columns, with drag-and-drop and an accessible select control.
4. A card can be deleted. Editing its title is an additional convenience.
5. Every mutation reaches FastAPI and Supabase and the list reloads from the API.
6. Refreshing the same browser preserves the board.
7. Loading, save-pending, empty, search-empty and request-error states are visible.
8. Invalid input is rejected by the API and database.
9. One browser board cannot read, update or delete another board's cards.
10. No real environment files, database credentials, cookies or private board tokens are committed.

## Stack
React + TypeScript + Vite; Python FastAPI and uv; Supabase Postgres; Vercel cloud hosting. Vercel is an alternative deployment platform listed in the course guide and supports the Python backend and static frontend under one origin.

## Out of scope
The separate expense-tracker homework, quizzes, and LMS submission. The course lists login, sharing and admin as possible change requests; the core screenshot does not require them. This implementation includes privacy and title editing as bounded extensions.
