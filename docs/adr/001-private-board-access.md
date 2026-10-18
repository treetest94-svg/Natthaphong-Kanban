# ADR 001: Private browser boards with scoped capabilities

Accepted.

Use a randomly generated 32-byte token in an HttpOnly, SameSite=Lax cookie (Secure on Vercel). Keep only its hash in the cards table. A SECURITY DEFINER RPC validates the token shape, hashes it, uses fixed SQL and includes the board hash in every operation. It returns only card fields, never the hash.

RLS remains enabled and direct privileges on the table are revoked for anonymous and authenticated application roles. Execute is granted only for the scoped RPC. The Supabase security advisor flags anonymous execution of any SECURITY DEFINER function; this is deliberate here because capability verification occurs inside the function. It is not unrestricted table access.

Trade-off: clearing cookies loses access; there is no account recovery, user sharing, or administrator feature. For a production multi-user app, use Supabase Auth with ownership policies, rate limiting and recovery instead. This assignment requires basic card operations and cloud persistence.
