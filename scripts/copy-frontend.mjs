import {cp,mkdir} from 'node:fs/promises';
await mkdir('public',{recursive:true});
await cp('frontend/dist','public',{recursive:true});
console.log('Copied the Vite frontend into public/ for the CDN.');
