'use client';

import {useState,type ReactNode} from 'react';

/** A counter that does a quick scale bump when its value changes (not on first render). */
export function Bump({value,className,children}:{value:number;className?:string;children?:ReactNode}){
  const [last,setLast]=useState(value);const [changes,setChanges]=useState(0);
  if(last!==value){setLast(value);setChanges(changes+1);}
  return <span key={changes} className={className} data-bump={changes?'':undefined}>{children??value}</span>;
}
