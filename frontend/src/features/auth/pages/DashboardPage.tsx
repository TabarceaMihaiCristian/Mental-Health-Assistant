import { Link } from "react-router-dom";
import { useAuth } from "../../../app/use-auth";

export function DashboardPage() {
  const { logout, user } = useAuth();

  return (
    <main className="dashboard-shell">
      <header className="dashboard-header">
        <div>
          <span className="eyebrow">Authenticated</span>
          <h1>{user?.full_name ?? "User"}</h1>
          <p>{user?.email}</p>
        </div>
        <button className="secondary-button" onClick={logout} type="button">
          Logout
        </button>
      </header>

      <section className="card-grid">
        <article className="dashboard-card">
          <h2>Session ready</h2>
          <p>Your account is active and you can move through the workspace securely.</p>
        </article>
        <article className="dashboard-card">
          <h2>Specialist Directory</h2>
          <p>Browse active specialists, inspect their profile details, and use that as the base for booking next.</p>
        </article>
        <article className="dashboard-card">
          <h2>Role</h2>
          <p>{user?.role ?? "Unknown"}</p>
        </article>
      </section>

      <nav className="inline-nav">
        <Link to="/specialists">Open specialist directory</Link>
      </nav>
    </main>
  );
}
