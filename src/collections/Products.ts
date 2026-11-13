import type {CollectionConfig} from 'payload'
import {publishedOrStaff,canEdit} from '@/lib/access'
import {slugField,seoFields,pageLayout,mediaField} from '@/lib/fields'
export const Products:CollectionConfig={
 slug:'products',labels:{singular:'Товар',plural:'Продукция'},admin:{group:'Каталог',useAsTitle:'title'},
 access:{read:publishedOrStaff,create:canEdit('admin','editor','catalog'),update:canEdit('admin','editor','catalog','seo'),delete:canEdit('admin')},
 versions:{drafts:{autosave:{interval:2000}},maxPerDoc:30},
 fields:[
 {name:'title',type:'text',required:true},slugField,
 {name:'category',type:'select',label:'Категория',options:['Вешалки','Электромонтажные изделия','Хозтовары','Экструзионные изделия','Прочее']},
 {name:'summary',type:'textarea',label:'Описание'},mediaField,
 {name:'gallery',type:'array',label:'Фотографии',fields:[{name:'image',type:'upload',relationTo:'media',required:true}]},
 {name:'skus',type:'array',label:'Артикулы и размеры',fields:[
  {name:'article',type:'text',label:'Артикул',required:true},
  {name:'size',type:'text',label:'Размер / характеристика'},
  {name:'pack',type:'text',label:'Упаковка'},
 ]},
 pageLayout,...seoFields,
 ]
}
