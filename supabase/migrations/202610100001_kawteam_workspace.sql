create schema if not exists kawteam_private;
create extension if not exists pgcrypto with schema extensions;
create table public.kawteam_workspaces (
 id uuid primary key, name text not null, credential_digest text not null,
 created_at timestamptz not null default now()
);
create table public.kawteam_records (
 workspace_id uuid not null references public.kawteam_workspaces(id),
 kind text not null check(kind in ('case','event','document','thread')),
 id text not null check(length(id) between 1 and 150),
 data jsonb not null check(jsonb_typeof(data)='object'),
 revision integer not null default 1 check(revision>0),
 updated_at timestamptz not null default now(),
 primary key(workspace_id,kind,id)
);
create table public.kawteam_actions (
 workspace_id uuid not null references public.kawteam_workspaces(id),
 request_id text not null, payload_hash text not null, actor text not null,
 record_kind text not null, record_id text not null, result jsonb not null,
 occurred_at timestamptz not null default now(),
 primary key(workspace_id,request_id)
);
alter table public.kawteam_workspaces enable row level security;
alter table public.kawteam_records enable row level security;
alter table public.kawteam_actions enable row level security;
revoke all on public.kawteam_workspaces, public.kawteam_records, public.kawteam_actions from anon, authenticated;

create function kawteam_private.authorize(p_workspace uuid,p_secret text) returns void
language plpgsql security definer set search_path='' as $$
begin
 if not exists(select 1 from public.kawteam_workspaces where id=p_workspace
   and credential_digest=encode(extensions.digest(p_secret,'sha256'),'hex')) then
   raise exception 'Workspace access denied' using errcode='42501';
 end if;
end; $$;
revoke all on schema kawteam_private from public;
revoke all on function kawteam_private.authorize(uuid,text) from public;

create function public.kawteam_read(p_workspace uuid,p_secret text) returns jsonb
language plpgsql security definer set search_path='' as $$
declare snapshot jsonb;
begin
 perform kawteam_private.authorize(p_workspace,p_secret);
 select jsonb_build_object('version',2,
  'cases',coalesce(jsonb_agg(data || jsonb_build_object('backendRevision',revision) order by updated_at desc) filter(where kind='case'),'[]'::jsonb),
  'events',coalesce(jsonb_agg(data || jsonb_build_object('backendRevision',revision) order by updated_at desc) filter(where kind='event'),'[]'::jsonb),
  'threads',coalesce(jsonb_agg(data || jsonb_build_object('backendRevision',revision) order by updated_at desc) filter(where kind='thread'),'[]'::jsonb),
  'documents',coalesce(jsonb_agg((data - 'originalBase64' - 'text') || jsonb_build_object('backendRevision',revision) order by updated_at desc) filter(where kind='document'),'[]'::jsonb))
 into snapshot from public.kawteam_records where workspace_id=p_workspace;
 return snapshot;
end; $$;

create function public.kawteam_record(p_workspace uuid,p_secret text,p_kind text,p_id text) returns jsonb
language plpgsql security definer set search_path='' as $$
declare result jsonb;
begin
 perform kawteam_private.authorize(p_workspace,p_secret);
 select data || jsonb_build_object('backendRevision',revision) into result
 from public.kawteam_records where workspace_id=p_workspace and kind=p_kind and id=p_id;
 return result;
end; $$;

create function public.kawteam_request(p_workspace uuid,p_secret text,p_key text,p_hash text) returns jsonb
language plpgsql security definer set search_path='' as $$
declare found public.kawteam_actions;
begin
 perform kawteam_private.authorize(p_workspace,p_secret);
 select * into found from public.kawteam_actions where workspace_id=p_workspace and request_id=p_key;
 if found.request_id is null then return null; end if;
 if found.payload_hash<>p_hash then raise exception 'Idempotency key reused for another action'; end if;
 return found.result;
end; $$;

create function public.kawteam_commit(p_workspace uuid,p_secret text,p_kind text,p_id text,
 p_data jsonb,p_expected integer,p_key text,p_hash text,p_actor text) returns jsonb
language plpgsql security definer set search_path='' as $$
declare current_revision integer; next_revision integer; result jsonb; previous jsonb;
begin
 perform kawteam_private.authorize(p_workspace,p_secret);
 if p_actor not in ('organiser','teammate') then raise exception 'Read-only profile' using errcode='42501'; end if;
 if length(p_key)>150 or length(p_hash)<>64 or octet_length(p_data::text)>12000000 then raise exception 'Invalid payload'; end if;
 perform pg_advisory_xact_lock(hashtextextended(p_workspace::text || p_key,0));
 previous:=public.kawteam_request(p_workspace,p_secret,p_key,p_hash);
 if previous is not null then return previous; end if;
 select revision into current_revision from public.kawteam_records
 where workspace_id=p_workspace and kind=p_kind and id=p_id for update;
 if coalesce(current_revision,0)<>p_expected then raise exception 'Stale revision' using errcode='40001'; end if;
 next_revision:=p_expected+1;
 insert into public.kawteam_records(workspace_id,kind,id,data,revision)
 values(p_workspace,p_kind,p_id,p_data-'backendRevision',next_revision)
 on conflict(workspace_id,kind,id) do update set data=excluded.data,revision=excluded.revision,updated_at=now();
 result:=p_data || jsonb_build_object('backendRevision',next_revision);
 insert into public.kawteam_actions(workspace_id,request_id,payload_hash,actor,record_kind,record_id,result)
 values(p_workspace,p_key,p_hash,p_actor,p_kind,p_id,result);
 return result;
end; $$;
revoke all on function public.kawteam_read(uuid,text), public.kawteam_record(uuid,text,text,text),
 public.kawteam_request(uuid,text,text,text), public.kawteam_commit(uuid,text,text,text,jsonb,integer,text,text,text) from public;
grant execute on function public.kawteam_read(uuid,text), public.kawteam_record(uuid,text,text,text),
 public.kawteam_request(uuid,text,text,text), public.kawteam_commit(uuid,text,text,text,jsonb,integer,text,text,text) to anon,authenticated;
insert into public.kawteam_workspaces(id,name,credential_digest) values('a86971a9-7f0a-4169-9f29-d31a7ca719b1','KawTeam','19441f73686be93a1ab515c77876ffcdc9fdcb372bc8efa96c3f6914c94edc40');
