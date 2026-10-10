'use client';

import Link from 'next/link';
import {useState} from 'react';
import {ArrowRight,CheckCircle2,Clock3,Folder,ShieldCheck} from 'lucide-react';
import {Button} from '@/components/ui/button';
import {Calendar} from '@/components/ui/calendar';
import {useDemo} from './workspace-context';
import {money,totalCost} from '@/lib/demo';
import type {WorkspaceState} from '@/lib/workspace';

export type ScheduledItem={id:string;projectId?:string;project:string;label:string;date:string;href:string};
export function scheduledItems(state:WorkspaceState):ScheduledItem[]{
  const items:ScheduledItem[]=[];
  for(const project of state.events){for(const [key,label] of [['eventDate','Event date'],['deadline','Delivery deadline']]){const date=project.facts[key];if(typeof date==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(date))items.push({id:`${project.id}-${key}`,projectId:project.id,project:project.name,label,date,href:`/projects/${project.id}`});}}
  for(const c of state.cases){if(items.some(d=>d.projectId===c.eventId&&d.date===c.deadline))continue;const project=state.events.find(p=>p.id===c.eventId);items.push({id:c.id,projectId:c.eventId,project:project?.name||c.title,label:c.title,date:c.deadline,href:`/cases/${c.id}`});}
  return items.sort((a,b)=>a.date.localeCompare(b.date));
}
const longDate=(iso:string)=>new Date(iso+'T12:00:00').toLocaleDateString('en-GB',{day:'numeric',month:'long',year:'numeric'});
const shortDate=(iso:string)=>new Date(iso+'T12:00:00').toLocaleDateString('en-GB',{day:'numeric',month:'short'});

export function Schedule({large=false}:{large?:boolean}){
  const {state}=useDemo();const dates=scheduledItems(state);const [selected,setSelected]=useState<Date>();
  const selectedISO=selected?`${selected.getFullYear()}-${String(selected.getMonth()+1).padStart(2,'0')}-${String(selected.getDate()).padStart(2,'0')}`:null;
  const visible=selectedISO?dates.filter(d=>d.date===selectedISO):dates;
  return <section className={`schedule-panel ${large?'large-schedule':''}`}><div className="panel-heading"><div><span className="section-caption">LOOKING AHEAD</span><h2>{large?'Your schedule':'On the calendar'}</h2></div>{!large&&<Link href="/calendar" aria-label="Open calendar"><ArrowRight size={17}/></Link>}</div><Calendar mode="single" selected={selected} onSelect={setSelected} modifiers={{scheduled:dates.map(d=>new Date(d.date+'T12:00:00'))}} modifiersClassNames={{scheduled:'scheduled-day'}} className="kt-calendar"/><div className="schedule-agenda"><div className="agenda-heading"><span>{selectedISO?shortDate(selectedISO):'Upcoming dates'}</span>{selected&&<button onClick={()=>setSelected(undefined)}>Show all</button>}</div>{(large?visible:visible.slice(0,3)).map(item=><Link href={item.href} className="agenda-item" key={item.id}><span className="agenda-date"><strong>{new Date(item.date+'T12:00:00').getDate()}</strong><small>{new Date(item.date+'T12:00:00').toLocaleDateString('en-GB',{month:'short'})}</small></span><span><strong>{item.project}</strong><small>{large?longDate(item.date):item.label}</small></span><ArrowRight size={14}/></Link>)}{!visible.length&&<p className="quiet-empty">{selected?'Nothing scheduled for this day.':'Dates from your project plans will appear here.'}</p>}</div><p className="schedule-note">Dates from saved project plans and supplier requests.</p></section>;
}

export function ApprovalQueue({projectId}:{projectId?:string}){
  const {state,profile,perform,busy}=useDemo();const [filter,setFilter]=useState('pending');const candidates=state.cases.filter(c=>(!projectId||c.eventId===projectId)&&c.draft.body);const cases=candidates.filter(c=>filter==='all'||c.draft.status===filter);
  return <div className={projectId?'project-tab-page':'workspace-page'}><div className="workspace-heading"><div><span className="page-kicker">HUMAN CHECKPOINTS</span><h1>{projectId?'Project approvals':'Approvals'}</h1><p>Review the exact message. Keep the final call with your team.</p></div><span className="approval-count"><ShieldCheck size={17}/>{candidates.filter(c=>c.draft.status==='pending').length} waiting</span></div><div className="queue-filters">{[['pending','Needs review'],['approved','Approved'],['all','All messages']].map(([key,label])=><button className={filter===key?'active':''} key={key} onClick={()=>setFilter(key)}>{label}</button>)}</div><div className="approval-queue">{cases.map(c=><article className="queue-card" key={c.id}><div className="queue-card-top"><span className="section-caption">{state.events.find(p=>p.id===c.eventId)?.name||'Supplier request'}</span><span className={`status-label ${c.draft.status==='pending'?'amber':''}`}>{c.draft.status==='pending'?'Approval needed':c.draft.status==='sent'?'Sent in demo':c.draft.status}</span></div><h2>{c.draft.subject}</h2><div className="queue-recipient"><span>TO</span>{c.draft.recipient}<span>REV {c.draft.revision}</span></div><p className="queue-message">{c.draft.body}</p><div className="queue-bottom"><span><Clock3 size={14}/>Approval expires after 30 minutes</span><div><Link href={`/cases/${c.id}/conversations`} className="subtle-link">Open conversation<ArrowRight size={14}/></Link>{c.draft.status==='pending'&&<><Button variant="outline" disabled={profile!=='organiser'||busy} onClick={()=>void perform({type:'reject',caseId:c.id},'Message returned for revision.')}>Return</Button><Button disabled={profile!=='organiser'||busy} onClick={()=>void perform({type:'approve',caseId:c.id},'Exact draft approved. Nothing sent yet.')}>Approve message<CheckCircle2 size={16}/></Button></>}</div></div></article>)}</div>{!cases.length&&<div className="panel-empty"><CheckCircle2 size={30}/><h2>{filter==='pending'?'Nothing waiting for approval.':'No messages in this view.'}</h2><p>Outgoing drafts appear here once a supplier request is ready.</p></div>}<p className="queue-footnote">Approval does not choose a vendor or place an order. External email is not connected.</p></div>;
}

export function ProjectVendors({projectId,embedded=false}:{projectId?:string;embedded?:boolean}){
  const {state}=useDemo();const records=state.cases.filter(c=>!projectId||c.eventId===projectId).flatMap(c=>c.vendors.map(v=>({vendor:v,case:c}))).filter((r,i,all)=>all.findIndex(other=>other.vendor.id===r.vendor.id)===i);
  return <div className={embedded?undefined:projectId?'project-tab-page':'workspace-page'}>{!embedded&&<div className="workspace-heading"><div><span className="page-kicker">RELATIONSHIPS, REMEMBERED</span><h1>{projectId?'Project vendors':'Vendor library'}</h1><p>Keep the relationship. Get fresh terms for the next request.</p></div></div>}<div className="vendor-library-grid">{records.map(({vendor:v,case:c})=><Link href={`/cases/${c.id}/vendors`} key={v.id} className="vendor-record"><div className="vendor-record-top"><span className="vendor-letter">{v.initials}</span><span className="status-label">{v.executionMode==='demo'||!v.executionMode?'Sample vendor':'Public source'}</span></div><h2>{v.name}</h2><p>{v.location}</p><div><span>{c.selectedVendorId===v.id?'Previously chosen by your team':v.status}</span><ArrowRight size={16}/></div><small>{v.executionMode==='live'?'Terms need supplier confirmation':(totalCost(v)===null?money(v.goodsSen)+' goods · delivery unconfirmed':money(totalCost(v)))+' · illustrative quote only'}</small></Link>)}</div>{!records.length&&<div className="panel-empty"><Folder size={30}/><h2>No vendor relationships yet.</h2><p>Suppliers from this project’s requests will be kept here.</p></div>}</div>;
}

type ActivityItem={id:string;kind:'Project'|'Chat'|'Approval'|'Request';title:string;detail:string;at:string;href:string};
export function activityItems(state:WorkspaceState):ActivityItem[]{
  const items:ActivityItem[]=[];
  for(const p of state.events)if(p.createdAt)items.push({id:`project-${p.id}`,kind:'Project',title:p.name,detail:'Project created',at:p.createdAt,href:`/projects/${p.id}`});
  for(const t of state.threads){const last=t.messages.at(-1);const p=state.events.find(e=>e.id===t.eventId);if(!last||!p)continue;const task=p.tasks?.find(x=>x.id===t.taskId);items.push({id:`thread-${t.id}`,kind:'Chat',title:task?`${p.name} · ${task.name}`:p.name,detail:last.body,at:last.time,href:task?`/projects/${p.id}/tasks/${task.id}`:`/projects/${p.id}`});}
  for(const c of state.cases){const p=state.events.find(e=>e.id===c.eventId);for(const e of c.events)if(e.occurredAt)items.push({id:`case-${c.id}-${e.id}`,kind:e.kind==='human'||e.kind==='mail'?'Approval':'Request',title:e.title,detail:`${p?.name||c.title} · ${e.detail}`,at:e.occurredAt,href:`/cases/${c.id}`});}
  return items.sort((a,b)=>Date.parse(b.at)-Date.parse(a.at)).slice(0,30);
}
const when=(iso:string)=>new Date(iso).toLocaleString('en-MY',{day:'numeric',month:'short',hour:'2-digit',minute:'2-digit',timeZone:'Asia/Kuala_Lumpur'});

export function RecentActivity(){
  const {state,loading}=useDemo();const items=activityItems(state);
  return <div className="workspace-page"><div className="workspace-heading"><div><span className="page-kicker">OVERVIEW</span><h1>Recent activity</h1><p>Latest projects, conversations and approvals.</p></div></div><div className="activity-list">{items.map(item=><Link href={item.href} key={item.id} className="activity-item"><span className={`activity-kind-tag ${item.kind.toLowerCase()}`}>{item.kind}</span><div><strong>{item.title}</strong><p>{item.detail}</p></div><time dateTime={item.at}>{when(item.at)}</time><ArrowRight size={15}/></Link>)}</div>{loading&&<p className="quiet-empty">Loading activity…</p>}{!loading&&!items.length&&<div className="panel-empty"><Clock3 size={30}/><h2>No activity yet.</h2><p>Projects, conversations and approvals will appear here.</p></div>}</div>;
}
