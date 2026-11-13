import type {CollectionConfig} from 'payload'
import {publishedOrStaff,canEdit} from '@/lib/access'
import {slugField,seoFields,pageLayout,mediaField} from '@/lib/fields'
export const Articles:CollectionConfig={
 slug:'articles',labels:{singular:'Статья',plural:'Блог / статьи'},admin:{group:'Контент',useAsTitle:'title'},
 access:{read:publishedOrStaff,create:canEdit('admin','editor','seo'),update:canEdit('admin','editor','seo'),delete:canEdit('admin')},
 versions:{drafts:{autosave:{interval:2000}},maxPerDoc:30},
 fields:[{name:'title',type:'text',required:true},slugField,mediaField,
 {name:'excerpt',type:'textarea',label:'Аннотация'},
 pageLayout,...seoFields]
}
