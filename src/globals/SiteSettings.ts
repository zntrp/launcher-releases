import type {GlobalConfig} from 'payload'
import {canEdit} from '@/lib/access'
import {pageLayout,seoFields} from '@/lib/fields'
export const SiteSettings:GlobalConfig={
 slug:'site-settings',label:'Главная страница и контакты',admin:{group:'Дизайн сайта',
 preview:()=>'/api/preview?secret='+encodeURIComponent(process.env.PREVIEW_SECRET||'')+'&path=%2F'},
 access:{read:()=>true,update:canEdit('admin','editor')},
 versions:{drafts:{autosave:{interval:2000}},max:30},
 fields:[
 {name:'brand',type:'text',label:'Название',defaultValue:'ПРАКТИК ПЛАСТ'},
 {name:'phone',type:'text',label:'Телефон'},
 {name:'email',type:'email',label:'Почта'},
 {name:'heroTitle',type:'text',label:'Главный заголовок',defaultValue:'Пластиковые изделия для вашего бизнеса. От чертежа до партии.'},
 {name:'heroLead',type:'textarea',label:'Описание'},
 {name:'heroImage',type:'upload',relationTo:'media',label:'Фотография первого экрана'},
 {name:'servicesHeading',type:'text',label:'Заголовок секции услуг',defaultValue:'От задачи до готового изделия'},
 {name:'productsHeading',type:'text',label:'Заголовок каталога',defaultValue:'Продукция для предприятий'},
 {name:'stepsHeading',type:'text',label:'Заголовок этапов',defaultValue:'Четыре шага к обсуждению заказа'},
 {name:'articlesHeading',type:'text',label:'Заголовок статей',defaultValue:'Материалы о производстве'},
 pageLayout,...seoFields
 ]
}
