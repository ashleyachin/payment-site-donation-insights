'use client'

import { useRouter } from 'next/navigation'
import { FormEvent, useEffect, useState } from 'react'

export default function LoginPage() {
  const router = useRouter()
  const [next, setNext] = useState('/')
  useEffect(() => {
    const p = new URLSearchParams(window.location.search)
    const n = p.get('next')
    if (n && n.startsWith('/')) setNext(n)
  }, [])
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await fetch('/api/auth', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password }),
      })
      if (!res.ok) {
        setError('Incorrect password.')
        setLoading(false)
        return
      }
      router.push(next.startsWith('/') ? next : '/')
      router.refresh()
    } catch {
      setError('Something went wrong.')
    }
    setLoading(false)
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#f3f6fb',
        padding: 24,
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: 400,
          background: '#fff',
          border: '1px solid #d9e2ef',
          borderRadius: 12,
          padding: 28,
          boxShadow: '0 4px 24px rgba(16, 36, 63, 0.08)',
        }}
      >
        <h1 style={{ margin: '0 0 8px', fontSize: 22, color: '#16355f' }}>Sign in</h1>
        <p style={{ margin: '0 0 20px', fontSize: 13, color: '#5c6e86' }}>
          Enter the site password to open the donation insights dashboard.
        </p>
        <form onSubmit={onSubmit}>
          <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: '#10243f', marginBottom: 6 }}>
            Password
          </label>
          <input
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{
              width: '100%',
              boxSizing: 'border-box',
              padding: '10px 12px',
              fontSize: 15,
              border: '1px solid #d9e2ef',
              borderRadius: 8,
              marginBottom: 16,
            }}
            placeholder="Password"
          />
          {error ? (
            <p style={{ color: '#8d2031', fontSize: 13, margin: '0 0 12px' }}>{error}</p>
          ) : null}
          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              padding: '12px 16px',
              fontSize: 15,
              fontWeight: 600,
              color: '#183a72',
              background: '#e8efff',
              border: '1px solid #b8c8ea',
              borderRadius: 8,
              cursor: loading ? 'wait' : 'pointer',
            }}
          >
            {loading ? 'Signing in…' : 'Continue'}
          </button>
        </form>
      </div>
    </div>
  )
}
