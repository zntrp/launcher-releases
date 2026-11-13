import type { Field, Block } from 'payload'
export const slugField:Field={name:'slug',label:'URL (латиницей)',type:'text',required:true,unique:true,index:true,validate:(value:unknown)=>typeof value==='string'&&/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(value)||'Используйте латинские буквы, цифры и дефис'}
export const seoFields: Field[]=[
  {type:'collapsible',label:'SEO',fields:[
    {name:'metaTitle',label:'Meta Title',type:'text',maxLength:180},
    {name:'metaDescription',label:'Meta Description',type:'textarea',maxLength:450},
    {name:'noIndex',label:'Запретить индексирование',type:'checkbox',defaultValue:false},
    {name:'canonical',label:'Canonical URL',type:'text'},
  ]}
]
export const HeroBlock:Block={slug:'hero',labels:{singular:'Первый экран',plural:'Первый экран'},fields:[
 {name:'eyebrow',type:'text',label:'Надзаголовок'},
 {name:'title',type:'text',label:'Заголовок H1',required:true},
 {name:'subtitle',type:'textarea',label:'Подзаголовок'},
 {name:'image',type:'upload',relationTo:'media',label:'Изображение'},
 {name:'buttonText',type:'text',label:'Текст кнопки'},
 {name:'buttonHref',type:'text',label:'Ссылка кнопки',defaultValue:'/zapros-rascheta'},
]}
export const TextBlock:Block={slug:'text',labels:{singular:'Текст',plural:'Текст'},fields:[
 {name:'heading',type:'text',label:'Заголовок H2'},
 {name:'body',type:'richText',label:'Содержимое'},
]}
export const ImageBlock:Block={slug:'image',labels:{singular:'Изображение',plural:'Изображения'},fields:[
 {name:'image',type:'upload',relationTo:'media',required:true},
 {name:'caption',type:'text',label:'Подпись'},
]}
export const CTABlock:Block={slug:'cta',labels:{singular:'Призыв к действию',plural:'Призывы к действию'},fields:[
 {name:'heading',type:'text',required:true},
 {name:'text',type:'textarea'},
 {name:'buttonText',type:'text',defaultValue:'Запросить расчёт'},
 {name:'buttonHref',type:'text',defaultValue:'/zapros-rascheta'},
]}
export const FAQBlock:Block={slug:'faq',labels:{singular:'FAQ',plural:'FAQ'},fields:[
 {name:'heading',type:'text',defaultValue:'Частые вопросы'},
 {name:'items',type:'array',fields:[{name:'question',type:'text',required:true},{name:'answer',type:'textarea',required:true}]}
]}
export const CardsBlock:Block={slug:'cards',labels:{singular:'Карточки',plural:'Карточки'},fields:[
 {name:'heading',type:'text'},
 {name:'items',type:'array',maxRows:12,fields:[
   {name:'title',type:'text',required:true},{name:'description',type:'textarea'},
   {name:'image',type:'upload',relationTo:'media'},{name:'href',type:'text'}
 ]}
]}
export const pageLayout:Field={name:'layout',type:'blocks',label:'Визуальный конструктор страницы',blocks:[HeroBlock,TextBlock,ImageBlock,CTABlock,FAQBlock,CardsBlock]}
export const mediaField:Field={name:'cover',label:'Обложка / основное фото',type:'upload',relationTo:'media'}
