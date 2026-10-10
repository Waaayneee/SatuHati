'use client';

import Link from 'next/link';
import Image from 'next/image';
import {usePathname,useRouter} from 'next/navigation';
import {useEffect,useState} from 'react';
import {ArrowRight,CalendarDays,Check,ChevronDown,ChevronsUpDown,Clock3,Folder,LayoutGrid,Menu,MessageSquare,Plus,Settings2,ShieldCheck,SquarePen,X} from 'lucide-react';
import {DropdownMenu,DropdownMenuContent,DropdownMenuItem,DropdownMenuLabel,DropdownMenuSeparator,DropdownMenuTrigger} from '@/components/ui/dropdown-menu';

import {profiles} from '@/lib/demo';
import {useDemo} from './workspace-context';
import {CreateProject} from './project-controls';
import {ApprovalQueue,RecentActivity,Schedule} from './project-overview';
import {ProjectWorkspace} from './project-workspace';
import {NewChat} from './chat-home';
import {CaseView} from './legacy-case';
import {ConnectionsPage} from './connections-page';
import {Bump} from './bump';

// The catch-all page remounts the app on every navigation, so the previous route is kept here, written after commit.
let previousRoute:{path:string;project?:string}|null=null;

const overviewItems=[{href:'/activity',name:'Recent activity',icon:Clock3},{href:'/approvals',name:'Approvals',icon:ShieldCheck},{href:'/calendar',name:'Calendar',icon:CalendarDays}];

export function ProjectApp(){
  const path=usePathname();const router=useRouter();const {state,profile,switchProfile,loading}=useDemo();const [newProject,setNewProject]=useState(false);const [mobileOpen,setMobileOpen]=useState(false);const [overviewOpen,setOverviewOpen]=useState(true);const [chatKey,setChatKey]=useState(0);
  const person=profiles.find(p=>p.id===profile)!;const parts=path.split('/').filter(Boolean);const selected=parts[0]==='projects'?state.events.find(p=>p.id===parts[1]):null;const currentCase=parts[0]==='cases'?state.cases.find(c=>c.id===parts[1]):null;
  const taskId=selected&&parts[2]==='tasks'?parts[3]:undefined;const tab=selected&&!taskId?(parts[2]||'chat'):'chat';
  const approvals=state.cases.filter(c=>c.draft.body&&c.draft.status==='pending').length;
  const isNewChat=['/','/workspace','/demo','/events','/casebook','/brief/new'].includes(path);
  const chatMode=isNewChat||(!!selected&&(!!taskId||tab==='chat'));
  const overviewActive=overviewItems.some(item=>item.href===path)||path==='/inbox';
  const section=isNewChat?'New chat':selected?(selected.tasks?.find(t=>t.id===taskId)?.name||selected.name):currentCase||parts[0]==='cases'?'Supplier request':parts[0]==='projects'?'Project':path==='/activity'?'Recent activity':path==='/approvals'||path==='/inbox'?'Approvals':path==='/calendar'?'Calendar':path==='/connections'||path==='/vendors'?'Connections':'Not found';
  useEffect(()=>{if(path==='/vendors')router.replace('/connections#vendor-library');else if(path==='/inbox')router.replace('/approvals');},[path,router]);
  // Main content enters on every route change; switching tabs inside the same project keeps its heading and tab bar still.
  // Decided once per route, so later re-renders (e.g. the 15s refresh) never restart the entrance.
  const routeProject=parts[0]==='projects'?parts[1]:undefined;
  const sameProject=()=>!!routeProject&&previousRoute?.project===routeProject&&previousRoute.path!==path;
  const [route,setRoute]=useState(()=>({path,tabOnly:sameProject()}));
  if(route.path!==path)setRoute({path,tabOnly:sameProject()});
  useEffect(()=>{previousRoute={path,project:routeProject};},[path,routeProject]);
  const close=()=>setMobileOpen(false);
  function startChat(){close();setChatKey(key=>key+1);router.push('/');}
  return <div className="kt-app"><a href="#workspace-content" className="skip-link">Skip to content</a><aside className={`kt-sidebar ${mobileOpen?'open':''}`}>
    <Link href="/" className="kt-brand" onClick={startChat}><Image src="/brand/kawteam-wordmark.png" alt="KawTeam" width={607} height={160} loading="eager"/></Link>
    <button className="kt-new-chat" onClick={startChat}><SquarePen size={19}/>New chat</button>
    <nav aria-label="Overview"><button className={`kt-nav-link kt-nav-toggle ${overviewActive&&!overviewOpen?'active':''}`} aria-expanded={overviewOpen} onClick={()=>setOverviewOpen(!overviewOpen)}><LayoutGrid size={20} strokeWidth={1.7}/>Overview<ChevronDown size={17} className="kt-nav-chevron"/></button><div className="kt-subnav" data-open={overviewOpen} inert={!overviewOpen}><div>{overviewItems.map(item=><Link href={item.href} key={item.href} onClick={close} className={`kt-nav-link ${path===item.href?'active':''}`}><item.icon size={18} strokeWidth={1.7}/>{item.name}{item.href==='/approvals'&&approvals>0&&<Bump value={approvals}/>}</Link>)}</div></div></nav>
    <div className="sidebar-project-heading"><span>PROJECTS</span></div>
    <nav className="sidebar-project-list" aria-label="Your projects"><button className="sidebar-new-project" onClick={()=>setNewProject(true)} disabled={profile==='observer'}><Plus size={18}/>New project</button>{state.events.map(project=><div key={project.id}><Link href={`/projects/${project.id}`} onClick={close} className={`sidebar-project-link ${selected?.id===project.id?'selected':''}`}><Folder size={18} strokeWidth={1.6}/><span>{project.name}</span>{selected?.id===project.id&&!!project.tasks?.length&&<ChevronDown size={15}/>}</Link>{selected?.id===project.id&&!!project.tasks?.length&&<div className="sidebar-task-list">{project.tasks.map(task=><Link href={`/projects/${project.id}/tasks/${task.id}`} key={task.id} onClick={close} className={taskId===task.id?'active':''}><MessageSquare size={14}/><span>{task.name}</span></Link>)}</div>}</div>)}{loading&&<span className="sidebar-empty">Loading projects…</span>}{!loading&&!state.events.length&&<span className="sidebar-empty">Your projects will live here.</span>}</nav>
    <div className="sidebar-bottom-nav"><Link href="/connections" onClick={close} className={`kt-nav-link ${path==='/connections'?'active':''}`}><Settings2 size={19}/>Connections</Link></div>
    <DropdownMenu><DropdownMenuTrigger className="kt-sidebar-profile" aria-label={`Switch profile, currently ${person.role}`}><span className="kt-profile-avatar">{person.initials}</span><span className="kt-sidebar-profile-text">{person.name}<small>{person.role}</small></span><ChevronsUpDown size={17}/></DropdownMenuTrigger><DropdownMenuContent side="top" align="start" className="kt-profile-menu"><DropdownMenuLabel>Switch profile</DropdownMenuLabel><DropdownMenuSeparator/>{profiles.map(p=><DropdownMenuItem key={p.id} onSelect={()=>void switchProfile(p.id)}><span className="menu-avatar">{p.initials}</span><span>{p.name}<small>{p.role}</small></span>{profile===p.id&&<Check size={15}/>}</DropdownMenuItem>)}</DropdownMenuContent></DropdownMenu>
  </aside>{mobileOpen&&<button className="kt-sidebar-backdrop" aria-label="Close navigation" onClick={close}/>}
    <div className={`kt-main ${chatMode?'chat-mode':''}`}><header className="kt-topbar"><div className="kt-breadcrumb"><button className="kt-mobile-menu" aria-expanded={mobileOpen} aria-label="Open navigation" onClick={()=>setMobileOpen(true)}><Menu size={21}/></button><span>{section}</span></div></header>
      <main id="workspace-content" data-enter={route.tabOnly?'tab':'page'}>{isNewChat?<NewChat key={chatKey}/>:selected?<ProjectWorkspace key={`${selected.id}-${taskId||tab}`} project={selected} tab={tab} taskId={taskId}/>:parts[0]==='projects'?<div className="panel-empty">{loading?<p>Opening project…</p>:<><Folder size={30}/><h1>Project not found.</h1><Link href="/">Start a new chat</Link></>}</div>:currentCase?<div className="supplier-detail-wrap"><CaseView brief={currentCase} tab={parts[2]||'overview'}/></div>:parts[0]==='cases'?<div className="panel-empty">{loading?'Opening supplier request…':'This supplier request is not in your workspace.'}</div>:path==='/activity'?<RecentActivity/>:path==='/approvals'||path==='/inbox'?<ApprovalQueue/>:path==='/calendar'?<div className="workspace-page"><div className="workspace-heading"><div><span className="page-kicker">DATES THAT MATTER</span><h1>Calendar</h1><p>Delivery dates and project deadlines, kept together.</p></div></div><Schedule large/></div>:path==='/connections'||path==='/vendors'?<ConnectionsPage/>:<div className="panel-empty"><h1>This page isn’t here.</h1><Link href="/">Start a new chat<ArrowRight size={16}/></Link></div>}</main>{!chatMode&&<footer className="kt-footer"><span>KawTeam · Keep the work moving.</span><span>Human approval. Human decision.</span></footer>}</div><CreateProject open={newProject} onOpenChange={setNewProject}/>{mobileOpen&&<button className="kt-sidebar-close" aria-label="Close sidebar" onClick={close}><X size={18}/></button>}
  </div>;
}
