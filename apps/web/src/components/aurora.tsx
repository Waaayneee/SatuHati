'use client';

import {usePathname} from 'next/navigation';
import {useEffect,useState,type CSSProperties} from 'react';

const chatPaths=['/','/workspace','/demo','/events','/casebook','/brief/new'];

/** Background view for a route. Blob positions per view live in theme.css (.kt-aurora[data-view]). */
export function auroraView(path:string){
  if(chatPaths.includes(path))return 'chat';
  const [first,,third,fourth]=path.split('/').filter(Boolean);
  if(first==='projects'){if(third==='tasks')return fourth?'chat':'tasks';return third&&['files','approvals','vendors'].includes(third)?third:'chat';}
  if(first==='activity')return 'activity';
  if(first==='approvals'||first==='inbox')return 'approvals';
  if(first==='calendar')return 'calendar';
  if(first==='connections'||first==='vendors')return 'connections';
  if(first==='cases')return 'cases';
  return 'chat';
}

/** True on devices that draw without a GPU (software WebGL or none) or with very little CPU or memory. */
function isWeakDevice(){
  const nav=navigator as Navigator&{deviceMemory?:number};
  if((nav.hardwareConcurrency||8)<=2||(nav.deviceMemory||8)<=2)return true;
  try{
    const gl=document.createElement('canvas').getContext('webgl');
    if(!gl)return true;
    const info=gl.getExtension('WEBGL_debug_renderer_info');
    const renderer=String(gl.getParameter(info?info.UNMASKED_RENDERER_WEBGL:gl.RENDERER));
    gl.getExtension('WEBGL_lose_context')?.loseContext();
    return /swiftshader|llvmpipe|software|basic render/i.test(renderer);
  }catch{return false;}
}

/** The fixed aurora behind the app. Only its data attributes change on navigation; it never remounts. */
export function Aurora(){
  const path=usePathname();
  const [pointer,setPointer]=useState({x:0,y:0});

  useEffect(()=>{
    const handlePointerMove=(event:PointerEvent)=>{
      const x=(event.clientX/window.innerWidth - .5)*2;
      const y=(event.clientY/window.innerHeight - .5)*2;
      setPointer({x:x*90,y:y*90});
    };
    const handlePointerLeave=()=>setPointer({x:0,y:0});
    window.addEventListener('pointermove',handlePointerMove);
    window.addEventListener('pointerleave',handlePointerLeave);
    return ()=>{
      window.removeEventListener('pointermove',handlePointerMove);
      window.removeEventListener('pointerleave',handlePointerLeave);
    };
  },[]);

  // Weak devices get data-perf="lite" on <html>: no live blur, still aurora (theme.css). Checked once per load.
  useEffect(()=>{if(isWeakDevice())document.documentElement.dataset.perf='lite';},[]);

  const style:CSSProperties={
    ['--pointer-x' as string]: `${pointer.x}px`,
    ['--pointer-y' as string]: `${pointer.y}px`,
  };

  return <div key={path} className="kt-aurora" aria-hidden="true" data-view={auroraView(path)} style={style}><span/><span/><span/><span/><span/></div>;
}
