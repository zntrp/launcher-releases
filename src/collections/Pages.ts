import type {CollectionConfig} from 'payload'
import { publishedOrStaff, canEdit } from '@/lib/access'
import {slugField,seoFields,pageLayout,mediaField} from '@/lib/fields'
const preview=(prefix:string,slug:string)=>'/api/preview?secret='+encodeURIComponent(process.env.PREVIEW_SECRET||'')+'&path='+encodeURIComponent(prefix+'/'+slug)
export const Pages:CollectionConfig={
 slug:'pages',labels:{singular:'Страница',plural:'Страницы'},
 admin:{group:'Контент',useAsTitle:'title',defaultColumns:['title','slug','_status','updatedAt'],
 preview:({slug})=>preview('/stranicy',String(slug||'')),
 livePreview:{url:({data})=>preview('/stranicy',String(data.slug||''))}},
 access:{read:publishedOrStaff,create:canEdit('admin','editor','seo'),update:canEdit('admin','editor','seo'),delete:canEdit('admin')},
 versions:{drafts:{autosave:{interval:2000}},maxPerDoc:30},
 fields:[{name:'title',type:'text',label:'Заголовок',required:true},slugField,mediaField,pageLayout,...seoFields]
}
