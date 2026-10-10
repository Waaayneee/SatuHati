create or replace function public.kawteam_commit(p_workspace uuid,p_secret text,p_kind text,p_id text,
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
 perform pg_advisory_xact_lock(hashtextextended(p_workspace::text || p_kind || p_id,0));
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
