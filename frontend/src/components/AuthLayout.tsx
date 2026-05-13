import { Link, Outlet } from "react-router-dom";

export function AuthLayout() {
  return (
    <div className="auth-shell">
      <section className="hero-panel">
        <span className="eyebrow">Mental Health Assistant</span>
        <h1>Build a steady support loop around reflection, scheduling, and care.</h1>
        <p>
          Start with authentication. Once this layer is solid, the rest of the frontend can build on a stable API session.
        </p>
        <div className="hero-links">
          <Link to="/login">Login</Link>
          <Link to="/register">Create account</Link>
        </div>
      </section>
      <section className="form-panel">
        <Outlet />
      </section>
    </div>
  );
}
