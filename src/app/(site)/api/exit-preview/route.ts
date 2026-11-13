import {draftMode} from 'next/headers'
import {NextRequest,NextResponse} from 'next/server'
export const dynamic='force-dynamic'
export async function GET(req:NextRequest){(await draftMode()).disable();return NextResponse.redirect(new URL('/',req.url))}
