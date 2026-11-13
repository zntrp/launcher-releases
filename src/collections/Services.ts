import type {CollectionConfig} from 'payload'
import {publishedOrStaff,canEdit} from '@/lib/access'
import {slugField,seoFields,pageLayout,mediaField} from '@/lib/fields'
export const Services:CollectionConfig={
 slug:'services',labels:{singular:'Услуга',plural:'Услуги'},admin:{group:'Каталог',useAsTitle:'title'},
 access:{read:publishedOrStaff,create:canEdit('admin','editor','catalog'),update:canEdit('admin','editor','catalog','seo'),delete:canEdit('admin')},
 versions:{drafts:{autosave:{interval:2000}},maxPerDoc:30},
 fields:[{name:'title',type:'text',required:true},slugField,{name:'summary',type:'textarea',label:'Краткое описание'},mediaField,pageLayout,...seoFields]
}
