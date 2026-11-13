import type {Payload} from 'payload'
import {fallbackProducts,fallbackServices,fallbackArticles} from './fixtures'
export async function seedPreview(payload:Payload){
 if(process.env.PREVIEW_AUTO_SEED!=='true')return
 const groups=[['products',fallbackProducts],['services',fallbackServices],['articles',fallbackArticles]] as const
 for(const [collection,items] of groups){
  const count=await payload.count({collection,overrideAccess:true})
  if(count.totalDocs>0)continue
  for(const item of items){
   await payload.create({
     collection,
     overrideAccess:true,
     data:{slug:item.slug,title:item.title,_status:'published',...(collection==='articles'?{excerpt:item.summary}:{summary:item.summary})}
   })
  }
  payload.logger.info('Seeded '+collection+' for test preview')
 }
}
