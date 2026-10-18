# Glossary

- **Card:** one task with a title and a status.
- **Status:** exactly `todo`, `doing` or `done`.
- **Board:** a private collection of cards linked to one browser cookie.
- **Capability:** an unguessable 256-bit token that authorizes access to one board.
- **RLS:** PostgreSQL Row Level Security, enabled with no direct anonymous table access.
- **RPC:** the constrained PostgreSQL function that checks the board capability for every action.
- **Thin slice:** one usable behavior across database, API and frontend.
