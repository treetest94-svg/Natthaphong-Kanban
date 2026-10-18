# Kanban domain

Scope: the uploaded Kanban assignment, not the separate expense-tracker homework on the course page.

A board has three columns: To do, Doing, Done. A card has an integer ID, nonempty trimmed title of 1–240 characters, status and creation time. Users can create, move, edit and delete cards. Changes persist in Supabase. Search and filters affect only the view.

The initial shared-table proposal was rejected by automatic approval review because it granted all anonymous visitors table-wide CRUD. The implemented design is materially narrower: an HttpOnly cookie holds a random 256-bit board capability, the database stores only its SHA-256 hash, and the exposed RPC scopes every operation to that hash. Anonymous clients cannot query the table itself. Clearing cookies or changing browsers creates a different board.

React never receives database credentials or board tokens. It calls same-origin FastAPI endpoints with cookies. FastAPI validates JSON and calls the Supabase RPC using the publishable key. There is no fake or localStorage database fallback.
