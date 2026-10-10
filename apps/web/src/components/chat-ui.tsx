'use client';

import Link from 'next/link';
import {useId,useLayoutEffect,useRef,useState,type ReactNode} from 'react';
import {ArrowRight,ArrowUp,Check,Folder,MessageSquare,Paperclip,Search,X} from 'lucide-react';
import {Button} from '@/components/ui/button';
import {DropdownMenu,DropdownMenuContent,DropdownMenuItem,DropdownMenuLabel,DropdownMenuSeparator,DropdownMenuTrigger} from '@/components/ui/dropdown-menu';
import {api,type EventDocument,type EventMemory} from '@/lib/workspace';
import {dateLabel,eligible,fitReason,money,totalCost,type ProcurementCase} from '@/lib/demo';
import {useDemo} from './workspace-context';
import {useProjectUpdate} from './project-controls';

/** Existing create-project and upload endpoints, shared by the new chat and project chats. */
export function useProjectActions(){
  const {acceptState,refresh,notify}=useDemo();const update=useProjectUpdate();
  async function createProject(name:string){const project=await api<EventMemory>('events',{name});update(project);return project;}
  async function uploadFiles(projectId:string,files:File[]){let count=0;for(const file of files){const form=new FormData();form.set('file',file);const saved=await api<EventDocument>(`events/${projectId}/documents`,form);acceptState(previous=>({...previous,documents:[...previous.documents.filter(d=>d.id!==saved.id),saved]}));count++;}notify(`${count} ${count===1?'file':'files'} added to project memory.`);await refresh().catch(()=>notify('Files saved. Refresh the workspace to see updated project facts.'));return count;}
  return {createProject,uploadFiles};
}

export const uploadAccept='.pdf,.docx,.xlsx,.txt,.md,.csv';

export type ComposerProject={id:string;name:string};

/** Projects pill in the composer toolbar: a picker on the new chat, a locked label inside a project. */
function ProjectPicker({projects,selectedProjectId,onSelectProject,lockedProjectName,disabled}:{projects?:ComposerProject[];selectedProjectId?:string|null;onSelectProject?:(id:string|null)=>void;lockedProjectName?:string;disabled:boolean}){
  if(lockedProjectName)return <span className="kt-project-control selected locked"><button type="button" className="kt-project-pill" aria-disabled="true" title={`This chat belongs to ${lockedProjectName}`} aria-label={`Project: ${lockedProjectName}. This chat belongs to ${lockedProjectName}.`} onClick={e=>e.preventDefault()}><Folder size={17}/><span>{lockedProjectName}</span></button></span>;
  if(!projects)return null;
  const selected=projects.find(p=>p.id===selectedProjectId);
  return <span className={`kt-project-control ${selected?'selected':''}`}>
    <DropdownMenu>
      <DropdownMenuTrigger className="kt-project-pill" disabled={disabled} aria-label={selected?`Project: ${selected.name}. Change project`:'Projects: no project selected. Choose a project for this message'}><Folder size={17}/><span>{selected?selected.name:'Projects'}</span></DropdownMenuTrigger>
      <DropdownMenuContent side="top" align="start" className="kt-profile-menu kt-project-menu">
        <DropdownMenuLabel>Send to project</DropdownMenuLabel><DropdownMenuSeparator/>
        {projects.length?projects.map(p=><DropdownMenuItem key={p.id} onSelect={()=>onSelectProject?.(p.id)}><Folder size={16}/><span className="kt-project-menu-name">{p.name}</span>{p.id===selected?.id&&<Check size={15}/>}</DropdownMenuItem>):<DropdownMenuItem disabled>No projects yet</DropdownMenuItem>}
      </DropdownMenuContent>
    </DropdownMenu>
    {selected&&<button type="button" className="kt-project-clear" aria-label={`Clear project ${selected.name}`} onClick={()=>onSelectProject?.(null)}><X size={15}/></button>}
  </span>;
}

export function Composer({value,onChange,onSubmit,onAttach,disabled=false,sending=false,uploading=false,placeholder,projects,selectedProjectId,onSelectProject,lockedProjectName}:{value:string;onChange:(value:string)=>void;onSubmit:()=>void;onAttach:()=>void;disabled?:boolean;sending?:boolean;uploading?:boolean;placeholder:string;projects?:ComposerProject[];selectedProjectId?:string|null;onSelectProject?:(id:string|null)=>void;lockedProjectName?:string}){
  const ref=useRef<HTMLTextAreaElement>(null);const id=useId();
  useLayoutEffect(()=>{const el=ref.current;if(!el)return;el.style.height='auto';el.style.height=`${Math.min(el.scrollHeight,280)}px`;},[value]);
  return <form className="kt-composer" onSubmit={e=>{e.preventDefault();if(value.trim()&&!sending&&!disabled)onSubmit();}}>
    <label htmlFor={id} className="sr-only">Message KawTeam</label>
    <textarea id={id} ref={ref} rows={3} maxLength={5000} value={value} placeholder={placeholder} disabled={disabled} onChange={e=>onChange(e.target.value)} onKeyDown={e=>{if(e.key==='Enter'&&!e.shiftKey&&!e.nativeEvent.isComposing){e.preventDefault();e.currentTarget.form?.requestSubmit();}}}/>
    <div className="kt-composer-toolbar">
      <div className="kt-composer-tools">
        <ProjectPicker projects={projects} selectedProjectId={selectedProjectId} onSelectProject={onSelectProject} lockedProjectName={lockedProjectName} disabled={disabled}/>
        <button type="button" className="kt-composer-icon" aria-label="Attach files" onClick={onAttach} disabled={disabled||uploading}><Paperclip size={19}/></button>
      </div>
      <button type="submit" className="kt-composer-send" aria-label="Send message" disabled={!value.trim()||sending||disabled}><ArrowUp size={20}/></button>
    </div>
  </form>;
}

/** `enter` animates a message that just arrived; history already on screen stays still. */
export function MessageRow({role,label,enter=false,children}:{role:'user'|'assistant';label?:string;enter?:boolean;children:ReactNode}){
  return <div className={`kt-msg ${role}${enter?' kt-msg-enter':''}`}>{label&&<span className="kt-msg-label">{label}</span>}<div className="kt-msg-body">{children}</div></div>;
}

export function Thinking({label='Thinking'}:{label?:string}){return <div className="kt-msg assistant kt-msg-enter"><div className="chat-thinking"><span/><span/><span/><small>{label}</small></div></div>;}

const draftLabel={pending:'Needs approval',approved:'Approved · not sent',rejected:'Returned',sent:'Sent in demo'};

/** Supplier request inside a conversation: shortlist, enquiry draft, approval and final choice. */
export function CaseCard({request}:{request:ProcurementCase}){
  const {profile,perform,busy,isApi}=useDemo();const [confirm,setConfirm]=useState<string|null>(null);
  const organiser=profile==='organiser';const editor=profile!=='observer';const controlled=request.id==='case-totes'&&isApi;
  const ids=request.shortlistVendorIds||[];
  const shortlist=ids.length?request.vendors.filter(v=>ids.includes(v.id)||v.id===request.selectedVendorId):request.vendors;
  const draft=request.draft;const chosen=request.vendors.find(v=>v.id===request.selectedVendorId);
  const needsOrganiser=(!!draft.body&&draft.status==='pending')||shortlist.some(v=>eligible(request,v)&&v.id!==request.selectedVendorId);
  return <article className="kt-card">
    <header className="kt-card-head"><span className="kt-card-icon">{request.workflowMode==='liaise'?<MessageSquare size={17}/>:<Search size={17}/>}</span><div><strong>{request.title}</strong><span>{request.quantity} items · {money(request.budgetSen)} · by {dateLabel(request.deadline)}</span></div><span className={`status-label ${draft.body&&draft.status==='pending'?'amber':''}`}>{draft.body&&draft.status==='pending'?'Needs approval':chosen?'Decided':shortlist.length?'Shortlist':'Request saved'}</span></header>
    {shortlist.length?<ul className="kt-vendor-list">{shortlist.map(v=>{const ok=eligible(request,v);const mine=request.selectedVendorId===v.id;return <li key={v.id} className={mine?'chosen':''}>
      <span className={`kt-vendor-mark ${v.color}`}>{v.initials}</span>
      <div className="kt-vendor-info"><strong>{v.name}</strong><span>{money(totalCost(v))} · {dateLabel(v.arrival)} · {ok?'Meets your brief':fitReason(request,v)}</span></div>
      <div className="kt-vendor-actions">
        {controlled&&editor&&v.executionMode!=='live'&&<Button size="sm" variant="outline" disabled={busy} onClick={()=>void perform({type:'prepare',caseId:request.id,vendorId:v.id},'Enquiry drafted. Organiser approval required.')}>Draft enquiry</Button>}
        {mine?<span className="kt-chosen"><Check size={14}/>Your choice</span>:organiser&&ok&&(confirm===v.id?<><Button size="sm" variant="ghost" onClick={()=>setConfirm(null)}>Cancel</Button><Button size="sm" disabled={busy} onClick={async()=>{if(await perform({type:'choose',caseId:request.id,vendorId:v.id},'Your choice recorded. No order placed.'))setConfirm(null);}}>Confirm choice</Button></>:<Button size="sm" onClick={()=>setConfirm(v.id)} aria-label={`Choose ${v.name}`}>Choose</Button>)}
      </div>
    </li>;})}</ul>
    :<div className="kt-card-empty"><p>{request.workflowPlan?.find(step=>step.id==='research')?.detail||'No vendors yet.'}</p>{editor&&<Button size="sm" variant="outline" disabled={busy} onClick={()=>void perform({type:'research',caseId:request.id},'Research request finished. Check the sources and missing terms.')}><Search size={14}/>Find vendor sources</Button>}</div>}
    {confirm&&<p className="kt-card-note">Records your team’s choice. No order, payment or email.</p>}
    {draft.body&&<section className="kt-draft">
      <div className="kt-draft-head"><span>Enquiry draft · revision {draft.revision}</span><span className={`status-label ${draft.status==='pending'?'amber':''}`}>{draftLabel[draft.status]}</span></div>
      <dl><div><dt>To</dt><dd>{draft.recipient}</dd></div><div><dt>Subject</dt><dd>{draft.subject}</dd></div></dl>
      <p className="kt-draft-body">{draft.body}</p>
      {organiser&&draft.status!=='sent'&&<div className="kt-card-actions">
        <Button size="sm" variant="outline" disabled={busy} onClick={()=>void perform({type:'reject',caseId:request.id},'Draft returned for revision.')}>Return</Button>
        {draft.status==='approved'?controlled&&<Button size="sm" disabled={busy} onClick={()=>void perform({type:'send',caseId:request.id},'Sent to controlled supplier only. No external email.')}>Send in demo</Button>
        :<Button size="sm" disabled={busy} onClick={()=>void perform({type:'approve',caseId:request.id},'Exact draft approved. No message sent yet.')}><Check size={14}/>Approve draft</Button>}
      </div>}
    </section>}
    {!organiser&&needsOrganiser&&<p className="kt-card-note">Only the organiser can approve drafts and choose the vendor.</p>}
    <Link href={`/cases/${request.id}`} className="kt-card-link">Open full request<ArrowRight size={14}/></Link>
  </article>;
}
