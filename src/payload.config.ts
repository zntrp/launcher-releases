import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { buildConfig } from 'payload'
import { postgresAdapter } from '@payloadcms/db-postgres'
import { lexicalEditor } from '@payloadcms/richtext-lexical'
import { s3Storage } from '@payloadcms/storage-s3'
import sharp from 'sharp'
import {seedPreview} from './lib/seed'
import { Users } from './collections/Users'
import { Media } from './collections/Media'
import { Products } from './collections/Products'
import { Services } from './collections/Services'
import { Pages } from './collections/Pages'
import { Articles } from './collections/Articles'
import { SiteSettings } from './globals/SiteSettings'

const dirname=path.dirname(fileURLToPath(import.meta.url))
const s3Ready=Boolean(process.env.S3_BUCKET&&process.env.S3_ACCESS_KEY_ID&&process.env.S3_SECRET_ACCESS_KEY)
const plugins=s3Ready?[s3Storage({
  collections:{media:{prefix:'praktik-plast/media',generateFileURL:({filename,prefix})=>{
    const key=prefix?`${prefix}/${filename}`:filename
    return process.env.S3_PUBLIC_URL?`${process.env.S3_PUBLIC_URL.replace(/\/$/,'')}/${key}`:`/api/media/file/${filename}`
  }}},
  bucket:process.env.S3_BUCKET!,
  config:{
    credentials:{accessKeyId:process.env.S3_ACCESS_KEY_ID!,secretAccessKey:process.env.S3_SECRET_ACCESS_KEY!},
    region:process.env.S3_REGION||'auto',
    ...(process.env.S3_ENDPOINT?{endpoint:process.env.S3_ENDPOINT,forcePathStyle:true}:{})
  }
})]:[]

export default buildConfig({
  secret:process.env.PAYLOAD_SECRET||'',
  serverURL:process.env.NEXT_PUBLIC_SERVER_URL||(process.env.RENDER_EXTERNAL_HOSTNAME?'https://'+process.env.RENDER_EXTERNAL_HOSTNAME:'http://localhost:3000'),
  admin:{
    user:Users.slug,
    meta:{titleSuffix:' — Практик Пласт'},
    importMap:{baseDir:dirname},
    livePreview:{
      url:({data,collectionConfig})=>{
        const slug=(data as {slug?:string}).slug||''
        const prefix=collectionConfig?.slug==='products'?'/produkciya':collectionConfig?.slug==='services'?'/uslugi':collectionConfig?.slug==='articles'?'/stati':'/stranicy'
        const address=`${prefix}/${slug}`
        return `/api/preview?secret=${encodeURIComponent(process.env.PREVIEW_SECRET||'')}&path=${encodeURIComponent(address)}`
      },
      collections:['pages','services','products','articles'],
      globals:['site-settings']
    },
  },
  db:postgresAdapter({
    pool:{connectionString:process.env.DATABASE_URL||''},
    push:process.env.NODE_ENV!=='production'||process.env.PREVIEW_SCHEMA_PUSH==='true'
  }),
  editor:lexicalEditor(),
  collections:[Users,Media,Products,Services,Articles,Pages],
  globals:[SiteSettings],
  plugins,
  sharp,
  onInit: async (payload) => {
    if(process.env.PREVIEW_AUTO_SEED==='true') await seedPreview(payload)
  },
  typescript:{outputFile:path.resolve(dirname,'payload-types.ts')},
})
