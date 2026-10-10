'use client';

import Link from 'next/link';
import {useRouter} from 'next/navigation';
import {useEffect,useRef,useState,type FormEvent} from 'react';
import {ArrowRight,FolderPlus,Paperclip,Search,ShieldCheck} from 'lucide-react';
import {Button} from '@/components/ui/button';
import {api,type ChatMessage,type EventMemory,type WorkspaceState} from '@/lib/workspace';
import {eligible} from '@/lib/demo';
import {useDemo} from './workspace-context';
import {CaseCard,Composer,MessageRow,Thinking,uploadAccept,useProjectActions} from './chat-ui';

type Card={kind:'create';name:string}|{kind:'exists';projectId:string;name:string}|{kind:'pick';message?:string;files?:File[]}|{kind:'approvals';caseIds:string[]}|{kind:'open';projectId:string};
type LocalMessage={id:string;role:'user'|'assistant';body:string;card?:Card};

const createIntent=/^\s*(?:please\s+)?(?:start|create|make|add|begin|set\s+up|open)\s+(?:a\s+|an\s+)?(?:new\s+)?project\b(.*)$/i;
const approvalIntent=/\b(?:approv\w*|needs?\s+my\s+(?:review|attention|decision)|pending|awaiting)\b/i;
const escape=(value:string)=>value.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
const mentions=(message:string,projects:EventMemory[])=>projects.filter(p=>new RegExp(`(?<!\\w)${escape(p.name)}(?!\\w)`,'i').test(message));

function NameForm({initial,label,disabled,onSubmit,onCancel}:{initial:string;label:string;disabled:boolean;onSubmit:(name:string)=>void;onCancel?:()=>void}){
  const [name,setName]=useState(initial);
  function submit(e:FormEvent){e.preventDefault();if(name.trim())onSubmit(name.trim());}
  return <form className="kt-inline-form" onSubmit={submit}><label className="sr-only" htmlFor="new-project-name">Project name</label><input id="new-project-name" autoFocus value={name} onChange={e=>setName(e.target.value)} placeholder="Project name" maxLength={100}/>{onCancel&&<Button type="button" size="sm" variant="ghost" onClick={onCancel}>Cancel</Button>}<Button size="sm" disabled={disabled||!name.trim()}>{label}</Button></form>;
}

export function NewChat(){
  const router=useRouter();const {state,profile,loading,acceptState,notify}=useDemo();const {createProject,uploadFiles}=useProjectActions();
  const [messages,setMessages]=useState<LocalMessage[]>([]);const [input,setInput]=useState('');const [working,setWorking]=useState('');const [done,setDone]=useState<string[]>([]);const [naming,setNaming]=useState<string|null>(null);
  const fileInput=useRef<HTMLInputElement>(null);const scrollPane=useRef<HTMLDivElement>(null);const pending=useRef<{message:string;projectId:string;id:string}|null>(null);
  const observer=profile==='observer';
  useEffect(()=>{if(scrollPane.current)scrollPane.current.scrollTop=scrollPane.current.scrollHeight;},[messages.length,working]);
  const say=(role:LocalMessage['role'],body:string,card?:Card)=>{const id=crypto.randomUUID();setMessages(previous=>[...previous,{id,role,body,card}]);return id;};
  const finish=(id:string)=>setDone(previous=>[...previous,id]);
  const readOnly=()=>say('assistant','You’re viewing as Observer, which is read-only. Switch profile to make changes.');

  async function create(name:string,cardId?:string){
    if(observer)return readOnly();
    setWorking('Creating project');
    try{const project=await createProject(name);if(cardId)finish(cardId);router.push(`/projects/${project.id}`);}
    catch(error){const message=error instanceof Error?error.message:'Could not create project.';notify(message);say('assistant',message);}
    finally{setWorking('');}
  }
  async function send(message:string,projectId:string){
    if(observer)return readOnly();
    const request=pending.current?.message===message&&pending.current.projectId===projectId?pending.current:{message,projectId,id:crypto.randomUUID()};pending.current=request;
    setWorking('Reading the project context');
    try{const result=await api<{assistant:ChatMessage;state:WorkspaceState;eventId:string}>('chat',{message,eventId:projectId,taskId:null,requestId:request.id});acceptState(result.state);pending.current=null;router.push(`/projects/${result.eventId}`);}
    catch(error){const text=error instanceof Error?error.message:'Could not save your message.';notify(text);say('assistant',text);}
    finally{setWorking('');}
  }
  async function upload(files:File[],projectId:string){
    if(observer)return readOnly();
    setWorking('Reading your files');
    try{await uploadFiles(projectId,files);say('assistant',`Added to ${state.events.find(p=>p.id===projectId)?.name||'your project'}.`,{kind:'open',projectId});}
    catch(error){const text=error instanceof Error?error.message:'Could not upload the file.';notify(text);say('assistant',text);}
    finally{setWorking('');}
  }
  async function pickProject(card:LocalMessage,projectId:string){
    finish(card.id);setNaming(null);
    if(card.card?.kind!=='pick')return;
    if(card.card.files)await upload(card.card.files,projectId);
    else if(card.card.message)await send(card.card.message,projectId);
  }
  async function pickNew(card:LocalMessage,name:string){
    if(observer)return readOnly();
    setWorking('Creating project');
    try{const project=await createProject(name);setWorking('');await pickProject(card,project.id);}
    catch(error){const text=error instanceof Error?error.message:'Could not create project.';notify(text);say('assistant',text);setWorking('');}
  }

  const attention=state.cases.filter(c=>(c.draft.body&&c.draft.status==='pending')||(!c.selectedVendorId&&c.vendors.some(v=>eligible(c,v))));
  function handle(text:string){
    say('user',text);setInput('');
    const match=text.match(createIntent);
    if(match){
      const rest=match[1].trim();const named=rest.match(/^(?:called|named|titled)\s+["“']?(.+?)["”']?[.!]?$/i);
      const name=(named?.[1]||rest.replace(/^(?:for|about|:)\s*/i,'')).replace(/^["“']|["”'.!]+$/g,'').trim();
      const existing=state.events.find(p=>p.name.toLowerCase()===name.toLowerCase());
      if(existing)return void say('assistant',`A project called ${existing.name} already exists.`,{kind:'exists',projectId:existing.id,name});
      if(observer)return void readOnly();
      if(named&&name&&name.length<=100&&!/\s(?:and|then)\s/i.test(name))return void create(name);
      return void say('assistant',name?`Create a project called “${name}”?`:'What should we call the new project?',{kind:'create',name});
    }
    if(approvalIntent.test(text))return void say('assistant',attention.length?'Here’s what is waiting on a human decision.':'Nothing needs approval right now.',{kind:'approvals',caseIds:attention.map(c=>c.id)});
    if(observer)return void readOnly();
    const found=mentions(text,state.events);
    if(found.length===1)return void send(text,found[0].id);
    say('assistant',state.events.length?'Which project is this for?':'Let’s create a project for this first.',{kind:'pick',message:text});
  }
  function attach(files:FileList|null){
    if(!files?.length)return;const list=Array.from(files);if(fileInput.current)fileInput.current.value='';
    say('user',`Attached ${list.map(f=>f.name).join(', ')}`);
    if(observer)return void readOnly();
    say('assistant',state.events.length?'Which project should these files go to?':'Let’s create a project for these files first.',{kind:'pick',files:list});
  }

  function renderCard(message:LocalMessage){
    const card=message.card;const closed=done.includes(message.id)||!!working;if(!card)return null;
    if(card.kind==='approvals')return <div className="kt-card-stack">{state.cases.filter(c=>card.caseIds.includes(c.id)).map(c=><CaseCard request={c} key={c.id}/>)}</div>;
    if(card.kind==='open')return <Link className="kt-card-link" href={`/projects/${card.projectId}`}>Open project<ArrowRight size={14}/></Link>;
    if(card.kind==='exists')return done.includes(message.id)?null:<div className="kt-choice-row"><Button size="sm" onClick={()=>router.push(`/projects/${card.projectId}`)}>Open {state.events.find(p=>p.id===card.projectId)?.name}</Button>{naming===message.id?<NameForm initial={card.name} label="Create" disabled={closed||observer} onSubmit={name=>void create(name,message.id)} onCancel={()=>setNaming(null)}/>:<Button size="sm" variant="outline" disabled={closed||observer} onClick={()=>setNaming(message.id)}>Create another</Button>}</div>;
    if(card.kind==='create')return done.includes(message.id)?null:<NameForm initial={card.name} label="Create project" disabled={closed||observer} onSubmit={name=>void create(name,message.id)}/>;
    if(done.includes(message.id))return null;
    return <div className="kt-choice-row">{state.events.map(p=><Button key={p.id} size="sm" variant="outline" disabled={closed} onClick={()=>void pickProject(message,p.id)}>{p.name}</Button>)}{naming===message.id?<NameForm initial="" label="Create" disabled={closed||observer} onSubmit={name=>void pickNew(message,name)} onCancel={()=>setNaming(null)}/>:<Button size="sm" variant="ghost" disabled={closed||observer} onClick={()=>setNaming(message.id)}><FolderPlus size={14}/>New project</Button>}</div>;
  }

  const composer=<Composer value={input} onChange={setInput} onSubmit={()=>handle(input.trim())} onAttach={()=>fileInput.current?.click()} sending={!!working} uploading={!!working} disabled={loading} placeholder={observer?'Observer view · ask what needs approval':'Message KawTeam…'}/>;
  return <div className="kt-chat">
    <input className="sr-only" ref={fileInput} type="file" multiple accept={uploadAccept} aria-label="Upload project files" onChange={e=>attach(e.target.files)}/>
    {messages.length?<>
      <div className="kt-chat-scroll" ref={scrollPane} aria-live="polite"><div className="kt-thread">{messages.map(m=><MessageRow key={m.id} role={m.role}>{m.body&&<p>{m.body}</p>}{m.role==='assistant'&&renderCard(m)}</MessageRow>)}{working&&<Thinking label={working}/>}</div></div>
      <div className="kt-composer-dock">{composer}</div>
    </>:<div className="kt-chat-empty">
      <h1>What are we going to KawTeam today?</h1>
      {composer}
      <div className="kt-chips"><button onClick={()=>handle('Start a new project')} disabled={loading}><FolderPlus size={15}/>Start a new project</button><button onClick={()=>handle('Find shirt printing vendors for 50 shirts within RM2,000')} disabled={loading}><Search size={15}/>Find shirt printing vendors for 50 shirts within RM2,000</button><button onClick={()=>handle('Show what needs my approval')} disabled={loading}><ShieldCheck size={15}/>Show what needs my approval</button><button onClick={()=>fileInput.current?.click()} disabled={loading}><Paperclip size={15}/>Upload a project file</button></div>
    </div>}
  </div>;
}
