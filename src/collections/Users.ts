import type {CollectionConfig} from 'payload'
import {canEdit} from '@/lib/access'
export const Users:CollectionConfig={
 slug:'users',auth:{verify:false,maxLoginAttempts:6,lockTime:900000},
 admin:{useAsTitle:'email',group:'Управление'},
 access:{
  read:({req})=>req.user&&(req.user as {role?:string}).role==='admin'?true:{id:{equals:req.user?.id||'0'}},
  create:async({req})=>{
   if(req.user)return (req.user as {role?:string}).role==='admin'
   const n=await req.payload.count({collection:'users',overrideAccess:true})
   return n.totalDocs===0
  },
  update:canEdit('admin'),delete:canEdit('admin')
 },
 hooks:{beforeChange:[async({data,operation,req})=>{
  if(operation==='create'&&!req.user){
   const count=await req.payload.count({collection:'users',overrideAccess:true})
   if(count.totalDocs===0)return {...data,role:'admin'}
  }
  return data
 }]},
 fields:[
  {name:'role',type:'select',required:true,defaultValue:'viewer',options:[
   {label:'Администратор',value:'admin'},
   {label:'Редактор',value:'editor'},
   {label:'Каталог',value:'catalog'},
   {label:'SEO',value:'seo'},
   {label:'Наблюдатель',value:'viewer'}
  ],access:{update:({req})=>(req.user as {role?:string}|null)?.role==='admin'}},
  {name:'displayName',type:'text',label:'Имя'}
 ]
}
