import { NextResponse } from 'next/server'

export const runtime = 'edge'

export async function POST(request: Request) {
  const url = new URL(request.url)
  const res = NextResponse.redirect(new URL('/login', url.origin), { status: 303 })
  res.cookies.set('ck_site_auth', '', {
    httpOnly: true,
    secure: process.env.VERCEL === '1' || process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    path: '/',
    maxAge: 0,
  })
  return res
}
