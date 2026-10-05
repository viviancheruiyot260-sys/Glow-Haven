import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function navClassName({ isActive }) {
  return isActive ? "nav-link nav-link-active" : "nav-link";
}

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/");
  }

  return (
    <>
      <header className="site-header">
        <div className="container header-inner">
          <Link className="logo" to="/">
            Glow <span>Haven</span>
          </Link>

          <nav className="nav-primary" aria-label="Main">
            <NavLink to="/products" className={navClassName}>
              Shop
            </NavLink>
            <NavLink to="/cart" className={navClassName}>
              Cart
            </NavLink>
            {user && (
              <NavLink to="/orders" className={navClassName}>
                Orders
              </NavLink>
            )}
          </nav>

          <div className="nav-actions">
            {user ? (
              <>
                <span className="nav-greeting" title={user.full_name}>
                  Hi, {user.full_name.split(" ")[0]}
                </span>
                <button className="btn btn-outline btn-sm" type="button" onClick={handleLogout}>
                  Log out
                </button>
              </>
            ) : (
              <>
                <NavLink to="/login" className={navClassName}>
                  Log in
                </NavLink>
                <Link className="btn btn-primary btn-sm" to="/register">
                  Sign up
                </Link>
              </>
            )}
          </div>
        </div>
      </header>

      <main className="page-main">
        <Outlet />
      </main>

      <footer className="site-footer">
        <div className="container">Made with love — Glow Haven © 2026</div>
      </footer>
    </>
  );
}
