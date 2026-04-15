const SALT = 'ck-site-auth-v1'

export async function getSessionTokenValue(authSecret: string | undefined): Promise<string | null> {
  if (!authSecret) return null
  const enc = new TextEncoder()
  const data = enc.encode(`${SALT}:${authSecret}`)
  const buf = await crypto.subtle.digest('SHA-256', data)
  return Array.from(new Uint8Array(buf))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('')
}
