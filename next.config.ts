import {withPayload} from '@payloadcms/next/withPayload'
import type {NextConfig} from 'next'
import path from 'node:path'
import {fileURLToPath} from 'node:url'
const root=path.dirname(fileURLToPath(import.meta.url))
const nextConfig:NextConfig={
 images:{unoptimized:true},
 serverExternalPackages:['sharp'],
 webpack:(config)=>{
  config.resolve.extensionAlias={
   '.cjs':['.cts','.cjs'],
   '.js':['.ts','.tsx','.js','.jsx'],
   '.mjs':['.mts','.mjs'],
  }
  return config
 },
 turbopack:{root}
}
export default withPayload(nextConfig,{devBundleServerPackages:false})
