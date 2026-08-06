import streamlit as st

def objective_playground():
    st.subheader("🎯 Portfolio Objective Playground")

    st.markdown(
        """
        Tune the optimization parameters below and observe how the
        objective function changes in real time.
        """
    )

    # ------------------------
    # Portfolio Parameters
    # ------------------------

    col1, col2 = st.columns(2)

    with col1:
        expected_return = st.slider(
            "Expected Return",
            -0.20, 0.50, 0.12, 0.01
        )

        portfolio_risk = st.slider(
            "Portfolio Risk",
            0.00, 1.00, 0.25, 0.01
        )

        transaction_cost = st.slider(
            "Transaction Cost",
            0.00, 0.10, 0.01, 0.001
        )

    with col2:
        liquidity = st.slider(
            "Liquidity Score",
            0.00, 1.00, 0.80, 0.01
        )

        diversification = st.slider(
            "Diversification Score",
            0.00, 1.00, 0.70, 0.01
        )

    st.divider()

    st.markdown("### Optimization Weights")

    c1, c2 = st.columns(2)

    with c1:
        risk_aversion = st.slider(
            "Risk Aversion (λ)",
            0.0, 5.0, 1.0, 0.1
        )

        transaction_weight = st.slider(
            "Transaction Weight (α)",
            0.0, 2.0, 0.10, 0.01
        )

    with c2:
        liquidity_weight = st.slider(
            "Liquidity Weight (β)",
            0.0, 2.0, 0.10, 0.01
        )

        diversification_weight = st.slider(
            "Diversification Weight (γ)",
            0.0, 2.0, 0.10, 0.01
        )

    # ------------------------
    # Objective Function
    # ------------------------

    objective = (
        expected_return
        - risk_aversion * portfolio_risk
        - transaction_weight * transaction_cost
        + liquidity_weight * liquidity
        + diversification_weight * diversification
    )

    st.divider()

    st.latex(
        r"""
        f(x)=
        R
        -\lambda \sigma^2
        -\alpha T
        +\beta L
        +\gamma D
        """
    )

    m1, m2, m3, m4, m5 = st.columns(5)

    m1.metric("Return", f"{expected_return:.4f}")
    m2.metric("Risk", f"{portfolio_risk:.4f}")
    m3.metric("Transaction", f"{transaction_cost:.4f}")
    m4.metric("Liquidity", f"{liquidity:.4f}")
    m5.metric("Objective", f"{objective:.4f}")

    st.progress(min(max((objective + 1) / 2, 0), 1))

    status_color = "🟢"
    status = "Excellent"

    if objective < -0.3:
        status_color = "🔴"
        status = "Poor"

    elif objective < 0.3:
        status_color = "🟡"
        status = "Moderate"

    st.subheader(f"{status_color} Objective Evaluation")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Objective Value", f"{objective:.4f}")

    with col2:
        st.metric("Optimization Quality", status)

    with st.expander("📘 Objective Breakdown"):
        st.write(f"Return Contribution : **{expected_return:.4f}**")
        st.write(f"Risk Penalty : **{-risk_aversion*portfolio_risk:.4f}**")
        st.write(f"Transaction Penalty : **{-transaction_weight*transaction_cost:.4f}**")
        st.write(f"Liquidity Reward : **{liquidity_weight*liquidity:.4f}**")
        st.write(f"Diversification Reward : **{diversification_weight*diversification:.4f}**")

    return objective