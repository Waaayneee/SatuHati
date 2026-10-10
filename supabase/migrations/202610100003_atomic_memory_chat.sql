-- Keep uploaded documents and derived memory in one transaction.
create or replace function public.kawteam_upload(p_workspace uuid,p_secret text,p_document jsonb,p_facts jsonb,p_actor text) returns jsonb
language plpgsql security definer set search_path='' as $$
declare event_id text:=p_document->>'eventId'; event_data jsonb; existing jsonb; saved jsonb; doc_id text:=p_document->>'id';
begin
 perform kawteam_private.authorize(p_workspace,p_secret);
 if p_actor not in ('organiser','teammate') then raise exception 'Read-only profile' using errcode='42501'; end if;
 perform pg_advisory_xact_lock(hashtextextended(p_workspace::text || 'event' || event_id,0));
 event_data:=public.kawteam_record(p_workspace,p_secret,'event',event_id);
 if event_data is null then raise exception 'Event missing'; end if;
 select data into existing from public.kawteam_records where workspace_id=p_workspace and kind='document'
 and data->>'eventId'=event_id and data->>'contentDigest'=p_document->>'contentDigest' limit 1;
 if existing is not null then return existing-'originalBase64'-'text'; end if;
 if (select count(*) from public.kawteam_records where workspace_id=p_workspace and kind='document' and data->>'eventId'=event_id)>=20 then raise exception 'Maximum 20 documents per event'; end if;
 saved:=public.kawteam_commit(p_workspace,p_secret,'document',doc_id,p_document,0,'upload-doc-'||doc_id,encode(extensions.digest(p_document::text,'sha256'),'hex'),p_actor);
 event_data:=event_data || jsonb_build_object('facts',coalesce(event_data->'facts','{}'::jsonb)||p_facts,'memoryVersion',coalesce((event_data->>'memoryVersion')::int,0)+1);
 perform public.kawteam_commit(p_workspace,p_secret,'event',event_id,event_data,(event_data->>'backendRevision')::int,'upload-event-'||doc_id,encode(extensions.digest(event_data::text,'sha256'),'hex'),p_actor);
 return saved-'originalBase64'-'text';
end; $$;

create or replace function public.kawteam_documents(p_workspace uuid,p_secret text,p_event text) returns jsonb
language plpgsql security definer set search_path='' as $$
begin
 perform kawteam_private.authorize(p_workspace,p_secret);
 return coalesce((select jsonb_agg(data-'originalBase64') from public.kawteam_records where workspace_id=p_workspace and kind='document' and data->>'eventId'=p_event),'[]'::jsonb);
end; $$;

-- Append against the latest thread and atomically persist a resulting case.
create or replace function public.kawteam_chat(p_workspace uuid,p_secret text,p_event text,p_message jsonb,p_case jsonb,p_actor text) returns jsonb
language plpgsql security definer set search_path='' as $$
declare thread_id text:='event-'||p_event; thread_data jsonb; prior jsonb; user_message jsonb; message_id text:=p_message->>'id';
begin
 perform kawteam_private.authorize(p_workspace,p_secret);
 if p_actor not in ('organiser','teammate') then raise exception 'Read-only profile' using errcode='42501'; end if;
 if public.kawteam_record(p_workspace,p_secret,'event',p_event) is null then raise exception 'Event missing'; end if;
 perform pg_advisory_xact_lock(hashtextextended(p_workspace::text || 'thread' || thread_id,0));
 thread_data:=coalesce(public.kawteam_record(p_workspace,p_secret,'thread',thread_id),jsonb_build_object('id',thread_id,'eventId',p_event,'messages','[]'::jsonb,'backendRevision',0));
 if p_message->>'role'='user' then
   select value into prior from jsonb_array_elements(thread_data->'messages') where value->>'id'=message_id limit 1;
   if prior is not null then
     if prior->>'body'<>p_message->>'body' then raise exception 'Idempotency key reused for a different message'; end if;
     return thread_data;
   end if;
 elsif p_message->>'role'='assistant' then
   select value into prior from jsonb_array_elements(thread_data->'messages') where value->>'inReplyTo'=p_message->>'inReplyTo' limit 1;
   if prior is not null then return thread_data; end if;
   select value into user_message from jsonb_array_elements(thread_data->'messages') where value->>'id'=p_message->>'inReplyTo' and value->>'role'='user' limit 1;
   if user_message is null then raise exception 'Missing user message'; end if;
 else raise exception 'Invalid message role'; end if;
 if jsonb_array_length(thread_data->'messages')>=150 then raise exception 'Conversation limit reached'; end if;
 if p_case is not null then
   if p_message->>'role'<>'assistant' or p_case->>'eventId'<>p_event or p_message->>'caseId'<>p_case->>'id' then raise exception 'Invalid resulting request'; end if;
   perform public.kawteam_commit(p_workspace,p_secret,'case',p_case->>'id',p_case,0,'chat-case-'||(p_case->>'id'),encode(extensions.digest(p_case::text,'sha256'),'hex'),p_actor);
 end if;
 thread_data:=jsonb_set(thread_data,'{messages}',(thread_data->'messages')||jsonb_build_array(p_message));
 return public.kawteam_commit(p_workspace,p_secret,'thread',thread_id,thread_data,(thread_data->>'backendRevision')::int,'chat-message-'||message_id,encode(extensions.digest(p_message::text,'sha256'),'hex'),p_actor);
end; $$;

revoke all on function public.kawteam_upload(uuid,text,jsonb,jsonb,text) from public;
revoke all on function public.kawteam_documents(uuid,text,text) from public;
revoke all on function public.kawteam_chat(uuid,text,text,jsonb,jsonb,text) from public;
grant execute on function public.kawteam_upload(uuid,text,jsonb,jsonb,text) to anon,authenticated;
grant execute on function public.kawteam_documents(uuid,text,text) to anon,authenticated;
grant execute on function public.kawteam_chat(uuid,text,text,jsonb,jsonb,text) to anon,authenticated;
