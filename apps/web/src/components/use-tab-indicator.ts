'use client';

import {useLayoutEffect,type RefObject} from 'react';

const lastTab=new Map<string,{left:number;width:number}>();

/** Slides the active tab's pill (its ::after) from the tab that was active before, in the same group.
 *  One layout read per tab change, no observers; survives the tab bar remounting. */
export function useTabIndicator(nav:RefObject<HTMLElement|null>,group:string,active:string){
  useLayoutEffect(()=>{
    const tab=nav.current?.querySelector<HTMLElement>('a.active');if(!tab)return;
    const now={left:tab.offsetLeft,width:tab.offsetWidth};const before=lastTab.get(group);lastTab.set(group,now);
    nav.current?.querySelectorAll('[data-slide]').forEach(el=>{if(el!==tab)el.removeAttribute('data-slide');});
    if(!before||!now.width||(before.left===now.left&&before.width===now.width))return;
    tab.style.setProperty('--kt-tab-from-x',`${before.left-now.left}px`);
    tab.style.setProperty('--kt-tab-from-sx',String(before.width/now.width));
    tab.setAttribute('data-slide','');
  },[nav,group,active]);
}
