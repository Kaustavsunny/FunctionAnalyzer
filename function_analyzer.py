import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Define variables
x, y = sp.symbols("x y")

st.title("📈 Function Analyzer")

equation = st.text_input("Enter a function of x or x and y", "x**2 + y**2")

try:
    expr = sp.sympify(equation)
except Exception as e:
    st.error(f"Invalid expression: {e}")
    st.stop()

free_vars = expr.free_symbols
vars_used = []
if x in free_vars:
    vars_used.append(x)
if y in free_vars:
    vars_used.append(y)

# ======================================
# ============ 1D Function =============
# ======================================
if len(vars_used) == 1 and x in vars_used:
    st.header("🔹 1D Function Analysis")

    domain = sp.calculus.util.continuous_domain(expr, x, sp.S.Reals)
    discontinuities = sp.Interval(-sp.oo, sp.oo) - domain

    if discontinuities.is_EmptySet:
        st.success("✅ Function is continuous over ℝ.")
    else:
        st.warning(f"⚠️ Discontinuous at: `{discontinuities}`")

    # Differentiability
    st.subheader("Differentiability")
    try:
        derivative = sp.diff(expr, x)
        diff_domain = sp.calculus.util.continuous_domain(derivative, x, sp.S.Reals)
        diff_discont = sp.Interval(-sp.oo, sp.oo) - diff_domain

        if diff_discont.is_EmptySet:
            st.success("✅ Function is differentiable over ℝ.")
        else:
            st.warning(f"⚠️ Not differentiable at: `{diff_discont}`")
    except:
        st.warning("⚠️ Could not determine differentiability.")

    st.subheader("📌 Derivative")
    try:
        st.code(f"f'(x) = {derivative}")
    except:
        st.warning("Could not compute derivative.")

    # Plot
    st.subheader("📊 Plot")
    f_np = sp.lambdify(x, expr, modules="numpy")
    x_vals = np.linspace(-10, 10, 400)
    y_vals = np.array([f_np(v) if np.isfinite(f_np(v)) else np.nan for v in x_vals])

    fig, ax = plt.subplots()
    ax.plot(x_vals, y_vals, label=str(expr))
    ax.set_xlabel("x")
    ax.set_ylabel("f(x)")
    ax.grid(True)
    ax.legend()
    st.pyplot(fig)

    # Behavior at Infinity
    st.subheader("♾️ Behavior at Infinity")
    try:
        lim_pos = sp.limit(expr, x, sp.oo)
        lim_neg = sp.limit(expr, x, -sp.oo)
        st.write(f"Limit as x → ∞: `{lim_pos}`")
        st.write(f"Limit as x → -∞: `{lim_neg}`")
    except:
        st.warning("Could not compute limits at infinity.")

    # Extrema
    st.subheader("🔻 Global Min / Max")
    f_prime = sp.diff(expr, x)
    f_double = sp.diff(f_prime, x)
    critical_points = sp.solve(f_prime, x, domain=sp.S.Reals)
    min_pts, max_pts = [], []

    for pt in critical_points:
        try:
            second = f_double.subs(x, pt)
            val = expr.subs(x, pt).evalf()
            if second > 0:
                min_pts.append((pt, val))
            elif second < 0:
                max_pts.append((pt, val))
        except:
            continue

    if min_pts:
        best_min = min(min_pts, key=lambda t: t[1])
        st.success(f"✅ Global minimum: f(x) = {best_min[1]} at x = {best_min[0]}")
    else:
        st.info("No global minimum (or function is unbounded below).")

    if max_pts:
        best_max = max(max_pts, key=lambda t: t[1])
        st.success(f"✅ Global maximum: f(x) = {best_max[1]} at x = {best_max[0]}")
    else:
        st.info("No global maximum (or function is unbounded above).")

# ======================================
# ============ 2D Function =============
# ======================================
elif len(vars_used) == 2:
    st.header("🌐 2D Function Analysis")

    # Continuity
    st.subheader("Continuity")
    try:
        domain_x = sp.calculus.util.continuous_domain(expr, x, sp.S.Reals)
        domain_y = sp.calculus.util.continuous_domain(expr, y, sp.S.Reals)
        discont = (sp.Interval(-sp.oo, sp.oo) - domain_x).union(sp.Interval(-sp.oo, sp.oo) - domain_y)
        if discont.is_EmptySet:
            st.success("✅ Continuous over ℝ².")
        else:
            st.warning(f"⚠️ Discontinuities along: `{discont}`")
    except:
        st.warning("Could not determine continuity.")

    # Differentiability
    st.subheader("Differentiability & Partial Derivatives")
    try:
        fx = sp.diff(expr, x)
        fy = sp.diff(expr, y)
        fx_dom = sp.calculus.util.continuous_domain(fx, x, sp.S.Reals)
        fy_dom = sp.calculus.util.continuous_domain(fy, y, sp.S.Reals)
        if (fx_dom == sp.Interval(-sp.oo, sp.oo)) and (fy_dom == sp.Interval(-sp.oo, sp.oo)):
            st.success("✅ Function is differentiable (partials are continuous).")
        else:
            st.warning("⚠️ Function may not be differentiable everywhere.")
        st.code(f"∂f/∂x = {fx}")
        st.code(f"∂f/∂y = {fy}")
    except:
        st.warning("Could not compute partial derivatives.")

    # 3D Plot
    st.subheader("🌀 3D Plot")
    f_np = sp.lambdify((x, y), expr, modules="numpy")
    try:
        range_vals = np.linspace(-10, 10, 100)
        X, Y = np.meshgrid(range_vals, range_vals)
        Z = f_np(X, Y)
        fig = plt.figure(figsize=(10, 6))
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_surface(X, Y, Z, cmap='viridis')
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("f(x, y)")
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Plotting failed: {e}")

    # Global Behavior (radial limit)
    st.subheader("♾️ Behavior at Infinity")
    r, theta = sp.symbols("r theta")
    x_r = r * sp.cos(theta)
    y_r = r * sp.sin(theta)
    try:
        radial = expr.subs({x: x_r, y: y_r})
        lim_inf = sp.limit(radial, r, sp.oo)
        st.write(f"Radial limit as r → ∞: `{lim_inf}`")
        if lim_inf == sp.oo:
            st.warning("Function grows to ∞.")
        elif lim_inf == -sp.oo:
            st.warning("Function decreases to -∞.")
    except:
        st.warning("Could not determine radial behavior.")

    # Critical Points
    st.subheader("📌 Critical Point Classification")
    try:
        grad = [sp.diff(expr, x), sp.diff(expr, y)]
        crit_pts = sp.solve(grad, (x, y), dict=True)

        if not crit_pts:
            st.info("No critical points found.")
        else:
            f_xx = sp.diff(expr, x, x)
            f_yy = sp.diff(expr, y, y)
            f_xy = sp.diff(expr, x, y)
            for pt in crit_pts:
                try:
                    H = sp.Matrix([[f_xx.subs(pt), f_xy.subs(pt)],
                                   [f_xy.subs(pt), f_yy.subs(pt)]])
                    det = H.det()
                    val = expr.subs(pt).evalf()
                    if det > 0:
                        if f_xx.subs(pt) > 0:
                            kind = "Local Min"
                        else:
                            kind = "Local Max"
                    elif det < 0:
                        kind = "Saddle Point"
                    else:
                        kind = "Inconclusive"
                    st.write(f"At {pt}, f(x, y) = {val:.4f} → **{kind}**")
                except:
                    st.warning(f"Could not classify point: {pt}")
    except:
        st.warning("Could not find critical points.")

else:
    st.warning("⚠️ Please enter a valid function in one or two variables.")
