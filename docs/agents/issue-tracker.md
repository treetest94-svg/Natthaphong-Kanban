# Issue tracker

Use local Markdown in `.scratch/kanban/issues/`. The project follows the course's thin-slice and red/green workflow; these documents record the implementation directly and do not claim that unavailable third-party Matt Pocock skills were executed.

| Ticket | Scope | State |
| --- | --- | --- |
| 01 | List and create cards through database, API and UI | Implemented |
| 02 | Move/edit/delete cards through all layers | Implemented |
| 03 | Private browser boards, validation and failure states | Implemented |
| 04 | Public source, deploy, live persistence verification | In progress |

Acceptance tests were written before endpoints. The red run reported 18 failures and one passing missing-resource assertion; the first green run passed all 19 cases. Privacy/cookie/CORS regression cases were added after narrowing access.
