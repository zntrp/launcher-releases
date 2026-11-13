import config from '@payload-config'
import {getPayload} from 'payload'
import {draftMode} from 'next/headers'
export type Kind='products'|'services'|'articles'|'pages'
export async function cms(){return getPayload({config})}
export async function isDraft(){return (await draftMode()).isEnabled}
export async function getPublished(kind:Kind,limit=200){
 const payload=await cms()
 const draft=await isDraft()
 return payload.find({collection:kind,limit,depth:2,draft,sort:'title',overrideAccess:false,user:undefined,
   where:draft?{}:{_status:{equals:'published'}}})
}
export async function getOne(kind:Kind,slug:string){
 const payload=await cms()
 const draft=await isDraft()
 const result=await payload.find({collection:kind,depth:2,draft,limit:1,where:{and:[{slug:{equals:slug}},...(!draft?[{_status:{equals:'published'}}]:[])]}})
 return result.docs[0]||null
}
export function toMediaURL(media:unknown):string|undefined {
 if(media&&typeof media==='object'){
  const obj=media as {url?:string}
  return obj.url?.startsWith('/')||obj.url?.startsWith('https://')?obj.url:undefined
 }
 return undefined
}
