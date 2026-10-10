'use client';
import {useEffect,useState} from 'react';
import {api} from '@/lib/workspace';
import {money,type ProcurementCase} from '@/lib/demo';
import {useDemo} from './workspace-context';
import {Icon} from './icon';

type Report={status:string;recommendedVendorId:string|null;selectedVendorId:string|null;potentialSavingsSen:number|null;savingsPercent:number|null;savingsLabel:string|null;generatedAt:string;caveats:string[];candidates:{id:string;name:string;totalSen:number|null;fit:string;arrival:string|null;quoteRef:string;conditions:string[]}[]};
export function OutcomeReport({brief}:{brief:ProcurementCase}){
  const {isApi}=useDemo();const [report,setReport]=useState<Report|null>(null);const [error,setError]=useState('');
  useEffect(()=>{let alive=true;if(isApi)api<Report>(`cases/${brief.id}/report`).then(value=>{if(alive){setReport(value);setError('');}}).catch(error=>{if(alive)setError(error.message);});return()=>{alive=false;};},[isApi,brief.id,brief.backendRevision]);
  if(!isApi)return null;
  if(error)return <p role="alert" className="error-text">Report unavailable: {error}</p>;
  if(!report)return <p className="role-note">Checking the latest offer terms…</p>;
  const recommended=report.candidates.find(v=>v.id===report.recommendedVendorId);
  return <section className="outcome-report"><div className="outcome-report-heading"><div><span className="eyebrow">THE COMPLETE PICTURE</span><h2>An outcome you can check.</h2></div><button className="button secondary" onClick={()=>window.print()}><Icon name="download" size={16}/>Print report</button></div><div className="outcome-summary"><div><span>RECOMMENDATION FOR REVIEW</span><h3>{recommended?.name||'No confirmed qualifying offer yet'}</h3><p>{report.status.replaceAll('_',' ')} · final choice stays with your team.</p></div>{report.potentialSavingsSen!==null&&<div className="savings-note"><span>{report.savingsLabel}</span><strong>{money(report.potentialSavingsSen)}<small>{report.savingsPercent}%</small></strong><p>Same supplier, same 300-tote scope. No purchase made.</p></div>}</div><div className="table-scroll"><table className="report-table"><thead><tr><th>Supplier</th><th>All-in price</th><th>Verification</th><th>Evidence</th></tr></thead><tbody>{report.candidates.map(v=><tr key={v.id}><td>{v.name}</td><td>{money(v.totalSen)}</td><td>{v.fit}</td><td>{v.quoteRef}</td></tr>)}</tbody></table></div><div className="report-caveats">{report.caveats.map(text=><p key={text}><Icon name="shield" size={14}/>{text}</p>)}</div><p className="report-generated">Generated {new Date(report.generatedAt).toLocaleString('en-MY',{timeZone:'Asia/Kuala_Lumpur'})} MYT · {report.selectedVendorId?'Team choice recorded':'Awaiting a human decision'}</p></section>;
}
