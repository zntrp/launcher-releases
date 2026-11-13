import type { Access, FieldAccess } from 'payload'
type Role='admin'|'editor'|'catalog'|'seo'|'viewer'
const roleOf=(user:unknown): Role | undefined => {
  if (!user || typeof user!=='object') return undefined
  return (user as {role?:Role}).role
}
export const canEdit=(...allowed:Role[]): Access => ({req}) => allowed.includes(roleOf(req.user) as Role)
export const canEditField=(...allowed:Role[]): FieldAccess => ({req}) => allowed.includes(roleOf(req.user) as Role)
export const publishedOrStaff: Access=({req})=>req.user?true:{_status:{equals:'published'}}
export const publicRead:Access=()=>true
