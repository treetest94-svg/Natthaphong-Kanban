create table public.cards (
 id bigint generated always as identity primary key,
 board_hash text not null check (board_hash ~ '^[a-f0-9]{64}$'),
 title text not null check (length(btrim(title)) between 1 and 240),
 status text not null default 'todo' check (status in ('todo','doing','done')),
 created_at timestamptz not null default now()
);
create index cards_board_idx on public.cards(board_hash,id);
alter table public.cards enable row level security;
-- No anonymous table access. A capability-scoped RPC is the only application entry.
revoke all on public.cards from anon, authenticated;
create function public.kanban_cards(p_board_token text,p_action text,p_card_id bigint default null,p_title text default null,p_status text default null)
returns jsonb language plpgsql security definer set search_path=public,pg_temp as $$
declare v_hash text; v_card public.cards%rowtype; v_result jsonb;
begin
 if p_board_token is null or p_board_token !~ '^[a-f0-9]{64}$' then raise exception 'Invalid board capability'; end if;
 v_hash:=encode(sha256(convert_to(p_board_token,'UTF8')),'hex');
 if p_action='list' then
  select coalesce(jsonb_agg(jsonb_build_object('id',id,'title',title,'status',status,'created_at',created_at) order by id),'[]'::jsonb)
  into v_result from public.cards where board_hash=v_hash;
  return v_result;
 elsif p_action='create' then
  insert into public.cards(board_hash,title,status) values(v_hash,btrim(p_title),coalesce(p_status,'todo')) returning * into v_card;
 elsif p_action='update' then
  update public.cards set title=coalesce(btrim(p_title),title),status=coalesce(p_status,status) where id=p_card_id and board_hash=v_hash returning * into v_card;
  if not found then return null; end if;
 elsif p_action='delete' then
  delete from public.cards where id=p_card_id and board_hash=v_hash;
  return to_jsonb(found);
 else raise exception 'Invalid action';
 end if;
 return jsonb_build_object('id',v_card.id,'title',v_card.title,'status',v_card.status,'created_at',v_card.created_at);
end;
$$;
revoke all on function public.kanban_cards(text,text,bigint,text,text) from public,anon,authenticated;
grant execute on function public.kanban_cards(text,text,bigint,text,text) to anon;
