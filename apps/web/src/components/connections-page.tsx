'use client';

import Link from 'next/link';
import {useState} from 'react';
import {ArrowRight} from 'lucide-react';
import {Button} from '@/components/ui/button';
import {money,type ProcurementCase} from '@/lib/demo';
import {useDemo} from './workspace-context';
import {ProjectVendors} from './project-overview';
import {OutcomeReport} from './outcome-report';
import {Connections} from './legacy-case';

function requestStatus(c:ProcurementCase){
  const chosen=c.vendors.find(v=>v.id===c.selectedVendorId);
  if(c.draft.body&&c.draft.status==='pending')return 'Awaiting approval';
  if(chosen)return `Chosen: ${chosen.name}`;
  return c.vendors.length?'Comparing options':'Request saved';
}

/** Vendor library, past supplier requests with outcome reports, and provider status. */
export function ConnectionsPage(){
  const {state,loading}=useDemo();const [open,setOpen]=useState<string|null>(null);
  return <div className="workspace-page connections-page">
    <div className="workspace-heading"><div><span className="page-kicker">WORKSPACE</span><h1>Connections</h1><p>Vendors, past supplier requests and provider status.</p></div></div>
    <nav className="connections-jump" aria-label="Connections sections"><a href="#vendor-library">Vendor library</a><a href="#supplier-requests">Supplier requests</a><a href="#providers">AI providers</a></nav>
    <section id="vendor-library" className="connections-section"><h2>Vendor library</h2><ProjectVendors embedded/></section>
    <section id="supplier-requests" className="connections-section"><h2>Supplier requests</h2><div className="request-list">{state.cases.map(c=><article className="request-row" key={c.id}><div className="request-row-head"><div><strong>{c.title}</strong><span>{state.events.find(p=>p.id===c.eventId)?.name||'No project'} · {c.quantity} items · {money(c.budgetSen)} · {requestStatus(c)}</span></div><Button size="sm" variant="outline" aria-expanded={open===c.id} onClick={()=>setOpen(open===c.id?null:c.id)}>{open===c.id?'Hide outcome report':'Outcome report'}</Button><Link href={`/cases/${c.id}`} className="subtle-link">Open<ArrowRight size={14}/></Link></div>{open===c.id&&<div className="supplier-detail-wrap request-report"><OutcomeReport brief={c}/></div>}</article>)}{loading&&<p className="quiet-empty">Loading supplier requests…</p>}{!loading&&!state.cases.length&&<p className="quiet-empty">Supplier requests from your chats will appear here.</p>}</div></section>
    <section id="providers" className="connections-section"><h2>AI provider status</h2><Connections embedded/></section>
  </div>;
}
