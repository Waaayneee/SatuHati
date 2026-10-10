'use client';

import Link from 'next/link';
import {useRouter} from 'next/navigation';
import {useEffect,useRef,useState,type FormEvent} from 'react';
import {api,type EventDocument,type EventMemory,type WorkspaceState,type ChatMessage} from '@/lib/workspace';
import {money,profiles} from '@/lib/demo';
import {useDemo} from './workspace-context';
import {Icon} from './icon';

function MemoryDialog({document,onClose}:{document:EventDocument;onClose:()=>void}){
  const ref=useRef<HTMLDialogElement>(null);
  useEffect(()=>{const dialog=ref.current;dialog?.showModal();return()=>{if(dialog?.open)dialog.close();};},[]);
  return <dialog ref={ref} className="dialog memory-dialog" aria-label="Document memory" onCancel={e=>{e.preventDefault();onClose();}}>
    <div className="dialog-head"><h2>{document.name}</h2><button className="icon-button" aria-label="Close document" onClick={onClose}><Icon name="close"/></button></div>
    <p className="dialog-intro">Readable content saved for this event. {document.sample?'Illustrative sample document.':''}</p>
    <pre className="document-text">{document.text}</pre>
  </dialog>;
}

function NewEventDialog({onClose,onCreated}:{onClose:()=>void;onCreated:(id:string)=>void}){
  const {refresh,notify}=useDemo();const ref=useRef<HTMLDialogElement>(null);const [name,setName]=useState('');const [saving,setSaving]=useState(false);
  useEffect(()=>{const d=ref.current;d?.showModal();return()=>{if(d?.open)d.close();};},[]);
  async function submit(e:FormEvent){e.preventDefault();setSaving(true);try{const event=await api<EventMemory>('events',{name});await refresh();onCreated(event.id);onClose();}catch(error){notify(error instanceof Error?error.message:'Could not create event.');}finally{setSaving(false);}}
  return <dialog ref={ref} className="dialog" aria-label="Create an event" onCancel={e=>{e.preventDefault();onClose();}}><div className="dialog-head"><h2>A place for your next big thing.</h2><button className="icon-button" aria-label="Close event dialog" onClick={onClose}><Icon name="close"/></button></div><p className="dialog-intro">Give it a name. Add its proposal and plans next. KawTeam keeps the context together.</p><form onSubmit={submit} className="event-name-form"><label>Event name<input autoFocus value={name} onChange={e=>setName(e.target.value)} placeholder="e.g. Tech Night 2026" maxLength={100} required/></label><button className="button primary" disabled={saving}>{saving?'Creating…':'Create event'}<Icon name="arrow" size={17}/></button></form></dialog>;
}

export function ChatWorkspace(){
  const {state,profile,loading,refresh,acceptState,notify,connections,isApi}=useDemo();
  const [selected,setSelected]=useState('');const [input,setInput]=useState('');const [sending,setSending]=useState(false);const [uploading,setUploading]=useState(false);
  const [newEvent,setNewEvent]=useState(false);const [preview,setPreview]=useState<EventDocument|null>(null);
  const fileInput=useRef<HTMLInputElement>(null);const end=useRef<HTMLDivElement>(null);
  const pendingRequest=useRef<{message:string;eventId:string|undefined;id:string}|null>(null);
  const current=state.events.find(e=>e.id===selected)||state.events.find(e=>e.id==='tech-night')||state.events[0];
  const documents=state.documents.filter(d=>d.eventId===current?.id);
  const messages=state.threads.find(t=>t.eventId===current?.id)?.messages||[];
  const person=profiles.find(p=>p.id===profile)!;
  useEffect(()=>{const id=new URLSearchParams(window.location.search).get('event')||localStorage.getItem('kawteam:event');const frame=requestAnimationFrame(()=>{if(id)setSelected(id);});return()=>cancelAnimationFrame(frame);},[]);
  useEffect(()=>{if(messages.length)end.current?.scrollIntoView({behavior:'smooth',block:'nearest'});},[messages.length]);
  function select(id:string){setSelected(id);localStorage.setItem('kawteam:event',id);}
  async function send(e:FormEvent){e.preventDefault();if(!input.trim()||sending)return;const message=input;setInput('');setSending(true);
    const previous=pendingRequest.current;
    const request=previous?.message===message&&previous?.eventId===current?.id?previous:{message,eventId:current?.id,id:crypto.randomUUID()};pendingRequest.current=request;
    try{const result=await api<{eventId:string;assistant:ChatMessage;state:WorkspaceState}>('chat',{message,eventId:request.eventId,requestId:request.id});select(result.eventId);acceptState(result.state);pendingRequest.current=null;}
    catch(error){setInput(message);notify(error instanceof Error?error.message:'Message failed.');}finally{setSending(false);}}
  async function upload(files:FileList|null){if(!files||!current)return;setUploading(true);
    try{for(const file of Array.from(files)){const form=new FormData();form.set('file',file);await api(`events/${current.id}/documents`,form);}await refresh();notify('Documents saved to this event’s memory.');}
    catch(error){notify(error instanceof Error?error.message:'Upload failed.');await refresh().catch(()=>{});}finally{setUploading(false);if(fileInput.current)fileInput.current.value='';}}
  async function openDocument(id:string){try{setPreview(await api<EventDocument>(`documents/${id}`));}catch(error){notify(error instanceof Error?error.message:'Could not open document.');}}
  return <div className="page chat-page">
    <div className="chat-page-heading"><div><span className="eyebrow">GOOD PLANS, IN GOOD COMPANY</span><h1>Your event.<br/><em>A conversation away.</em></h1></div><div className="chat-heading-note"><span className="note-spark">✳</span><p>Bring the plans.<br/>We’ll remember the details.</p></div></div>
    <div className="chat-workspace">
      <section className="conversation-paper" aria-label="Event assistant">
        <div className="conversation-top"><div><span className="assistant-mark">k<span>✳</span></span><div><strong>KawTeam</strong><small>Your event’s extra pair of hands</small></div></div><span className="chat-connection"><span className="status-dot"/>{connections?.ai==='configured'?'AI connected':'AI connection pending'}</span></div>
        <div className="event-context-bar"><Icon name="cases" size={17}/><label htmlFor="event-context">IN CONTEXT</label><select id="event-context" value={current?.id||''} onChange={e=>select(e.target.value)}>{!state.events.length&&<option value="">Choose an event</option>}{state.events.map(event=><option key={event.id} value={event.id}>{event.name}{event.sample?' · sample':''}</option>)}</select><span>{documents.length} {documents.length===1?'document':'documents'}</span></div>
        <div className="chat-messages" aria-live="polite">
          {loading?<div className="chat-welcome"><span className="assistant-orbit">✳</span><h2>Opening your event memory…</h2></div>:!messages.length?<div className="chat-welcome"><span className="assistant-orbit">✳</span><span className="eyebrow">LESS REPEATING. MORE GETTING THERE.</span><h2>Let’s make<br/><em>good things happen.</em></h2><p>{current?`Talk to KawTeam about ${current.name}. Its saved proposal, plans and budget stay in context.`:'Create an event and add its plans. Then talk naturally—no procurement form to fill in.'}</p><div className="suggested-prompts"><button onClick={()=>setInput(`Find vendors for ${current?.name||'my event'} within RM1,000.`)}><Icon name="search" size={17}/><span>Find the right vendors<small>With your event’s budget in mind</small></span><Icon name="arrow" size={15}/></button><button onClick={()=>setInput(`What do you know about ${current?.name||'my event'} from the uploaded proposal?`)}><Icon name="file" size={17}/><span>Pick up from the proposal<small>Use the details you’ve already shared</small></span><Icon name="arrow" size={15}/></button></div></div>:messages.map(message=><article key={message.id} className={`chat-message ${message.role}`}><div className="chat-message-label"><span>{message.role==='user'?person.initials:'✳'}</span><strong>{message.role==='user'?'Your team':message.provider==='setup_required'?'Connection note':'KawTeam'}</strong><small>{new Date(message.time).toLocaleTimeString('en-MY',{hour:'2-digit',minute:'2-digit',timeZone:'Asia/Kuala_Lumpur'})}</small></div><p>{message.body}</p>{!!message.citations?.length&&<div className="citation-list">{message.citations.map(id=><button key={id} onClick={()=>void openDocument(id)}><Icon name="file" size={13}/>{state.documents.find(d=>d.id===id)?.name||'Event source'}</button>)}</div>}{message.caseId&&<Link className="chat-task-link" href={`/cases/${message.caseId}`}><Icon name="cases" size={19}/><span>Supplier request saved<small>Context, budget and next steps in one place</small></span><Icon name="arrow" size={17}/></Link>}</article>)}
          {sending&&<div className="chat-working"><span className="working-dot"/>Reading your event context…</div>}<div ref={end}/>
        </div>
        <form className="chat-composer" onSubmit={send}><label className="sr-only" htmlFor="chat-input">Message KawTeam</label><textarea id="chat-input" rows={2} value={input} onChange={e=>setInput(e.target.value)} onKeyDown={e=>{if(e.key==='Enter'&&!e.shiftKey&&!e.nativeEvent.isComposing){e.preventDefault();e.currentTarget.form?.requestSubmit();}}} placeholder={`Find vendors for ${current?.name||'my event'} within RM1,000…`} maxLength={5000} disabled={profile==='observer'||!isApi||sending}/><div className="composer-bottom"><button type="button" className="composer-attach" onClick={()=>fileInput.current?.click()} disabled={!current||profile==='observer'||uploading}><Icon name="plus" size={17}/>Add event files</button><span>Enter to send · Shift + Enter for a new line</span><button className="send-message" aria-label="Send message" disabled={!input.trim()||sending||profile==='observer'||!isApi}><Icon name="arrow" size={20}/></button></div></form>
        <p className="chat-footnote"><Icon name="shield" size={13}/>Your team approves outreach and makes the final vendor decision.</p>
      </section>
      <aside className="event-memory-panel" aria-label="Event memory"><div className="memory-panel-top"><span className="eyebrow">THE CONTEXT WE KEEP</span><button className="icon-button" aria-label="Create event" onClick={()=>setNewEvent(true)} disabled={profile==='observer'||!isApi}><Icon name="plus" size={18}/></button></div><h2>{current?.name||'Your next event'}</h2>{current?.sample&&<span className="sample-tag">Illustrative sample event</span>}<p className="memory-description">Upload once. Mention the event by name. Keep the whole team on the same page.</p><div className="memory-facts">{current?.facts.budgetSen&&<div><span>Saved budget</span><strong>{money(Number(current.facts.budgetSen))}</strong></div>}{current?.facts.deadline&&<div><span>Delivery deadline</span><strong>{String(current.facts.deadline)}</strong></div>}{current?.facts.location&&<div><span>Location</span><strong>{String(current.facts.location)}</strong></div>}</div><div className="memory-documents-heading"><h3>Event files <span>{documents.length}</span></h3><Icon name="file" size={16}/></div><div className="memory-files">{documents.map(doc=><button key={doc.id} className="memory-file" onClick={()=>void openDocument(doc.id)}><span><Icon name="file" size={18}/></span><div><strong>{doc.name}</strong><small>{Math.max(1,Math.round(doc.size/1024))} KB · Ready in memory</small></div><Icon name="check" size={14}/></button>)}{!documents.length&&<p className="memory-empty">No files yet. Start with the proposal, budget sheet or event plan.</p>}</div><input ref={fileInput} type="file" className="sr-only" aria-label="Upload event files" accept=".pdf,.docx,.xlsx,.txt,.md,.csv" multiple onChange={e=>void upload(e.target.files)}/><button className="memory-upload" onClick={()=>fileInput.current?.click()} disabled={!current||profile==='observer'||uploading}><Icon name="plus" size={19}/><strong>{uploading?'Reading your documents…':'Add to event memory'}</strong><span>PDF, Word, Excel or text · up to 3 MB each</span></button><div className="memory-note"><Icon name="leaf" size={19}/><p>New details in your message take priority. A different budget won’t quietly change your saved proposal.</p></div>{current&&<Link href="/casebook" className="text-action">See supplier requests<Icon name="arrow" size={16}/></Link>}</aside>
    </div>
    {newEvent&&<NewEventDialog onClose={()=>setNewEvent(false)} onCreated={select}/>} {preview&&<MemoryDialog document={preview} onClose={()=>setPreview(null)}/>}
  </div>;
}

export function EventLibrary(){const router=useRouter();const {state,profile,isApi}=useDemo();const [creating,setCreating]=useState(false);return <div className="page"><span className="eyebrow">EVERY EVENT HAS A STORY</span><div className="section-head"><div><h1 className="page-title">The plans, remembered.</h1><p className="page-intro">Proposals, budgets and conversations. A shared memory for each event.</p></div><button className="button primary" onClick={()=>setCreating(true)} disabled={profile==='observer'||!isApi}><Icon name="plus" size={17}/>New event</button></div><div className="event-library">{state.events.map(event=><Link key={event.id} className="event-library-card" href={`/?event=${event.id}`}><span className="event-library-art">✳</span><div><span className="eyebrow">{event.sample?'SAMPLE EVENT':'YOUR TEAM’S EVENT'}</span><h2>{event.name}</h2><p>{state.documents.filter(d=>d.eventId===event.id).length} files in memory · {state.threads.find(t=>t.eventId===event.id)?.messages.length||0} messages</p></div><Icon name="arrow"/></Link>)}</div>{!state.events.length&&<p className="memory-empty">Create an event to start building its memory.</p>}{creating&&<NewEventDialog onClose={()=>setCreating(false)} onCreated={id=>{localStorage.setItem('kawteam:event',id);router.push(`/projects/${id}`);}}/>}</div>;}
