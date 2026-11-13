import type {Metadata} from 'next'
import Script from 'next/script'
import './site.css'
import './site-overrides.css'
export const metadata:Metadata={title:'Практик Пласт — литьё, экструзия, изделия',description:'Контрактное производство и продажа пластиковых изделий для бизнеса.',robots:{index:false,follow:false}}
export default function Layout({children}:{children:React.ReactNode}){
 return <html lang="ru"><body>{children}<Script src="/assets/main.js" strategy="afterInteractive"/></body></html>
}
