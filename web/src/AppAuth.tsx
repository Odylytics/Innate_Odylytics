import { useState } from 'react'
import { ApiError, api, type AccountStatus } from './api'
import { store } from './App'
import Demo from './Demo'
import { useT } from './i18n'

// Phone app (#/app): sign up (one account per email) or sign in with email + password, then the rhythm set-up and the wallet.
// Only the account summary is kept in localStorage, never the password.
const KEY = 'innate.account'

type L = { en: string; vi: string }

export default function AppAuth() {
  const [account, setAccount] = useState<AccountStatus | null>(() => {
    try { return JSON.parse(store.get(KEY) ?? 'null') } catch { return null }
  })
  const signIn = (a: AccountStatus) => { store.set(KEY, JSON.stringify(a)); setAccount(a) }
  const signOut = () => { try { localStorage.removeItem(KEY) } catch { /* private mode */ } setAccount(null) }
  if (account) return <Demo key={account.user_id} storyCase={null} account={account} onLogout={signOut} />
  return <AuthForm onSignedIn={signIn} />
}

function AuthForm({ onSignedIn }: { onSignedIn: (a: AccountStatus) => void }) {
  const { lang } = useT()
  const tx = (x: L) => x[lang]
  const [mode, setMode] = useState<'signup' | 'login'>('signup')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<L | null>(null)

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    setBusy(true); setError(null)
    try {
      onSignedIn(mode === 'signup'
        ? await api.signup({ email, password, full_name: fullName.trim() || undefined })
        : await api.login({ email, password }))
    } catch (err) {
      const st = err instanceof ApiError ? err.status : -1
      setError(st === 409 ? { en: 'This email already has an account. Sign in instead.', vi: 'Email này đã có tài khoản. Hãy đăng nhập.' }
        : st === 401 && mode === 'login' ? { en: 'Wrong email or password.', vi: 'Sai email hoặc mật khẩu.' }
        : st === 422 ? { en: 'Check the email, and use a password of at least 6 characters.', vi: 'Kiểm tra lại email, mật khẩu cần ít nhất 6 ký tự.' }
        : st === 0 ? { en: 'Cannot reach the Innate API.', vi: 'Không kết nối được API Innate.' }
        : { en: `Error ${st}: ${(err as Error).message}`, vi: `Lỗi ${st}: ${(err as Error).message}` })
    } finally { setBusy(false) }
  }

  const field = { width: '100%', padding: '12px 14px', border: '1px solid var(--line)', borderRadius: 10, fontSize: 16, background: 'var(--surface)', color: 'var(--text)' }
  return (
    <div className="ws wrap" style={{ maxWidth: 440 }}>
      <h1>{mode === 'signup' ? tx({ en: 'Create your Innate wallet', vi: 'Tạo ví Innate' }) : tx({ en: 'Sign in', vi: 'Đăng nhập' })}</h1>
      <p className="muted">{tx({
        en: 'One account per email. After signing up you set up your touch rhythm; from then on, even someone with your password and PIN is checked against it.',
        vi: 'Mỗi email một tài khoản. Sau khi đăng ký, bạn thiết lập nhịp chạm; từ đó, kể cả người biết mật khẩu và PIN của bạn cũng bị so với nhịp này.',
      })}</p>
      <div className="row" role="tablist" style={{ gap: 8, margin: '16px 0' }}>
        <button role="tab" aria-selected={mode === 'signup'} className={`btn small ${mode === 'signup' ? '' : 'ghost'}`} onClick={() => { setMode('signup'); setError(null) }}>{tx({ en: 'Sign up', vi: 'Đăng ký' })}</button>
        <button role="tab" aria-selected={mode === 'login'} className={`btn small ${mode === 'login' ? '' : 'ghost'}`} onClick={() => { setMode('login'); setError(null) }}>{tx({ en: 'Sign in', vi: 'Đăng nhập' })}</button>
      </div>
      <form onSubmit={submit} style={{ display: 'grid', gap: 12 }}>
        {mode === 'signup' && <label>{tx({ en: 'Name (optional)', vi: 'Tên (không bắt buộc)' })}
          <input style={field} value={fullName} onChange={(e) => setFullName(e.target.value)} maxLength={100} autoComplete="name" /></label>}
        <label>Email
          <input style={field} type="email" required value={email} onChange={(e) => setEmail(e.target.value)} maxLength={254} autoComplete="email" inputMode="email" /></label>
        <label>{tx({ en: 'Password', vi: 'Mật khẩu' })}
          <input style={field} type="password" required minLength={mode === 'signup' ? 6 : undefined} value={password} onChange={(e) => setPassword(e.target.value)}
            maxLength={128} autoComplete={mode === 'signup' ? 'new-password' : 'current-password'} /></label>
        {mode === 'signup' && <p className="muted mini">{tx({ en: 'Demo app: do not reuse a real password.', vi: 'App demo: đừng dùng lại mật khẩu thật.' })}</p>}
        {error && <p className="callout strong" role="alert">{tx(error)}</p>}
        <button className="btn" type="submit" disabled={busy}>{busy ? '…' : mode === 'signup' ? tx({ en: 'Create account', vi: 'Tạo tài khoản' }) : tx({ en: 'Sign in', vi: 'Đăng nhập' })}</button>
      </form>
    </div>
  )
}
