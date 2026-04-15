import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { getSessionTokenValue } from './lib/session'

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  if (
    pathname.startsWith('/login') ||
    pathname.startsWith('/api/auth') ||
    pathname.startsWith('/api/logout')
  ) {
    return NextResponse.next()
  }
  if (pathname.startsWith('/_next')) {
    return NextResponse.next()
  }

  const expected = await getSessionTokenValue(process.env.AUTH_SECRET)
  const cookie = request.cookies.get('ck_site_auth')?.value
  if (expected && cookie === expected) {
    return NextResponse.next()
  }

  const login = new URL('/login', request.url)
  login.searchParams.set('next', pathname + request.nextUrl.search)
  return NextResponse.redirect(login)
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
}
