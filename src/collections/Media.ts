import type {CollectionConfig} from 'payload'
import { canEdit } from '@/lib/access'
const durable=Boolean(process.env.S3_BUCKET&&process.env.S3_ACCESS_KEY_ID&&process.env.S3_SECRET_ACCESS_KEY)
export const Media:CollectionConfig={
 slug:'media',labels:{singular:'Медиафайл',plural:'Медиатека'},
 admin:{useAsTitle:'alt',group:'Контент'},
 access:{read:()=>true,create:()=>durable,update:canEdit('admin','editor','catalog'),delete:canEdit('admin')},
 upload:{mimeTypes:['image/jpeg','image/png','image/webp','image/avif'],imageSizes:[
  {name:'thumbnail',width:400,height:300,position:'centre'},
  {name:'card',width:900,height:680,position:'centre'}
 ],adminThumbnail:'thumbnail'},
 fields:[{name:'alt',type:'text',label:'Альтернативный текст (SEO)',required:true},{name:'caption',type:'text',label:'Подпись'}]
}
