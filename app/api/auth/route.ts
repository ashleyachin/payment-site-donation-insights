import { NextResponse } from 'next/server'
import { getSessionTokenValue } from '@/lib/session'

export const runtime = 'edge'

export async function POST(request: Request) {
  let body: { password?: string }
  try {
    body = await request.json()
  } catch {
    return NextResponse.json({ error: 'Invalid body' }, { status: 400 })
  }

  const password = body.password
  if (!password || password !== process.env.SITE_PASSWORD) {
    return NextResponse.json({ error: 'Invalid password' }, { status: 401 })
  }

  const token = await getSessionTokenValue(process.env.AUTH_SECRET)
  if (!token) {
    return NextResponse.json({ error: 'Server misconfigured' }, { status: 500 })
  }

  const isProd = process.env.VERCEL === '1' || process.env.NODE_ENV === 'production'
  const res = NextResponse.json({ ok: true })
  res.cookies.set('ck_site_auth', token, {
    httpOnly: true,
    secure: isProd,
    sameSite: 'lax',
    path: '/',
    maxAge: 60 * 60 * 24 * 30,
  })
  return res
}
