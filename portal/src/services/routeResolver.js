import { getNavigationByDocType } from '../config/navigation'

/**
 * Centralized Route Resolver for ITS Project Operations Portal.
 * Resolves list routes, document detail routes, new document actions, and report routes.
 */
export function resolveDocTypeRoute(docType, name = null, action = null) {
  if (!docType) return '/portal/project-management'

  const navInfo = getNavigationByDocType(docType)
  let baseRoute = ''

  if (navInfo && navInfo.moduleRoute) {
    baseRoute = navInfo.moduleRoute
  } else {
    const slug = docType.toLowerCase().replace(/ /g, '-')
    baseRoute = `/portal/project-management/${slug}`
  }

  if (action === 'new') {
    return `${baseRoute}?action=new`
  }

  if (name) {
    return `${baseRoute}/${encodeURIComponent(name)}`
  }

  return baseRoute
}

export function resolveReportRoute(reportName, refDocType = null) {
  if (refDocType) {
    return resolveDocTypeRoute(refDocType)
  }
  return '/portal/reporting'
}
