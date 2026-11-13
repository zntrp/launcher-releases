import {draftMode} from 'next/headers'
import {NextRequest,NextResponse} from 'next/server'
export const dynamic='force-dynamic'
export async function GET(req:NextRequest){
  const secret=req.nextUrl.searchParams.get('secret')
  const target=req.nextUrl.searchParams.get('path')||'/'
  if(!process.env.PREVIEW_SECRET||secret!==process.env.PREVIEW_SECRET)return new NextResponse('Forbidden',{status:403})
  if(!/^\/[a-z0-9/_-]*$/.test(target)||target.startsWith('//'))return new NextResponse('Bad path',{status:400})
  const d=await draftMode();d.enable()
  return NextResponse.redirect(new URL(target,req.url))
}
