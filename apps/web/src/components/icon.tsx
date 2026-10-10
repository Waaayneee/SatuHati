import type { CSSProperties } from 'react';
export type IconName = 'arrow' | 'plus' | 'cases' | 'mail' | 'people' | 'connect' | 'chevron' | 'check' | 'close' | 'search' | 'clock' | 'external' | 'spark' | 'file' | 'shield' | 'pin' | 'download' | 'menu' | 'leaf' | 'edit';
const paths: Record<IconName, React.ReactNode> = {
  arrow: <path d="M4 12h15M13 6l6 6-6 6"/>, plus: <path d="M12 5v14M5 12h14"/>,
  cases: <><path d="M3 7h6l2 2h10v11H3z"/><path d="M3 7V4h6l2 3h10v2"/></>,
  mail: <><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 6 9 7 9-7"/></>,
  people: <><circle cx="9" cy="8" r="3"/><path d="M3 20v-2a6 6 0 0 1 12 0v2M16 5a3 3 0 0 1 0 6M18 15a5 5 0 0 1 3 5"/></>,
  connect: <><path d="m10 14 4-4M8 16l-1 1a4 4 0 0 1-6-6l4-4a4 4 0 0 1 6 0M16 8l1-1a4 4 0 1 1 6 6l-4 4a4 4 0 0 1-6 0" transform="translate(-1 -1)"/></>,
  chevron: <path d="m8 10 4 4 4-4"/>, check: <path d="m5 12 4 4L19 6"/>, close: <path d="m6 6 12 12M6 18 18 6"/>,
  search: <><circle cx="10" cy="10" r="6"/><path d="m15 15 6 6"/></>,
  clock: <><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></>,
  external: <path d="M14 3h7v7M21 3l-11 11M10 3H3v18h18v-7"/>,
  spark: <path d="m12 3 2.5 6.5L21 12l-6.5 2.5L12 21l-2.5-6.5L3 12l6.5-2.5z"/>,
  file: <path d="M5 3h9l5 5v13H5zM14 3v6h5M8 13h8M8 17h6"/>,
  shield: <><path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6z"/><path d="m8 12 3 3 5-6"/></>,
  pin: <><path d="M18 10c0 5-6 11-6 11S6 15 6 10a6 6 0 1 1 12 0"/><circle cx="12" cy="10" r="2"/></>,
  download: <path d="M12 3v12m-5-5 5 5 5-5M4 17v4h16v-4"/>,
  menu: <path d="M4 6h16M4 12h16M4 18h16"/>,
  leaf: <path d="M20 4C5 2 1 12 6 17c6 6 15 0 14-13zM5 20 16 9"/>,
  edit: <path d="m4 16 12-12 4 4L8 20H4zM13 7l4 4"/>,
};
export function Icon({ name, size = 20, style }: { name: IconName; size?: number; style?: CSSProperties }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" data-icon={name} style={style}>{paths[name]}</svg>;
}
