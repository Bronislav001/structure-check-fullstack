import React, { Suspense, lazy } from 'react'
import { NavLink, Route, Routes } from 'react-router-dom'
import { useAuth } from './state/auth'
import Home from './pages/Home'
import Template from './pages/Template'
import Login from './pages/Login'
import Register from './pages/Register'
import Hero from './components/Hero'
import RequirePerm from './components/RequirePerm'
import { hasPermission, PERMS } from './lib/rbac'
import NotFound from './pages/NotFound'

const Validate = lazy(() => import('./pages/Validate'))
const History = lazy(() => import('./pages/History'))
const AdminUsers = lazy(() => import('./pages/AdminUsers'))

function LinkChip({ to, children }: { to: string; children: React.ReactNode }) {
  return <NavLink to={to} className={({ isActive }) => `link ${isActive ? 'active' : ''}`}>{children}</NavLink>
}

function RouteLoader() {
  return <div className="card"><div className="muted">Загружаем раздел…</div></div>
}

export default function App() {
  const { user, isAuthed, logout } = useAuth()
  const role = user?.role || 'guest'

  return (
    <>
      <div className="nav">
        <div className="nav-inner">
          <div className="links">
            <div className="brand">Struct Check</div>
            <LinkChip to="/">Главная</LinkChip>
            <LinkChip to="/template">Эталон</LinkChip>
            {hasPermission(role, PERMS.CHECKS_CREATE) && <LinkChip to="/validate">Проверка</LinkChip>}
            {hasPermission(role, PERMS.CHECKS_READ_OWN) && <LinkChip to="/history">История</LinkChip>}
            {hasPermission(role, PERMS.USERS_READ_ANY) && <LinkChip to="/admin/users">Пользователи</LinkChip>}
          </div>
          <div className="right">
            {isAuthed ? (
              <>
                <span className="badge">{user?.name || 'Пользователь'} · {role}</span>
                <button className="btn" onClick={() => logout()}>Выйти</button>
              </>
            ) : (
              <>
                <LinkChip to="/register">Регистрация</LinkChip>
                <LinkChip to="/login">Вход</LinkChip>
              </>
            )}
          </div>
        </div>
      </div>

      <Hero />

      <div className="container">
        <Suspense fallback={<RouteLoader />}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/template" element={<Template />} />
            <Route path="/validate" element={<RequirePerm perm={PERMS.CHECKS_CREATE}><Validate /></RequirePerm>} />
            <Route path="/history" element={<RequirePerm perm={PERMS.CHECKS_READ_OWN}><History /></RequirePerm>} />
            <Route path="/admin/users" element={<RequirePerm perm={PERMS.USERS_READ_ANY}><AdminUsers /></RequirePerm>} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Suspense>
      </div>
    </>
  )
}
