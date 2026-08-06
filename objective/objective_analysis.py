import numpy as np


def binary_objective_breakdown(x,expected_returns,covariance_matrix,liquidity_scores,transaction_cost_vector,correlation_matrix,config):
    
    x = np.asarray(x)

    risk_aversion = config["risk_aversion"]
    transaction_cost = config["transaction_cost"]
    liquidity_weight = config["liquidity_weight"]

    lambda_div = 0.05

    return_term = np.dot(expected_returns, x)

    liquidity_term = liquidity_weight * np.dot(
        liquidity_scores,
        x
    )


    transaction_term = transaction_cost * np.dot(
        transaction_cost_vector,
        x
    )


    risk_term = (
        risk_aversion
        * x.T
        @ covariance_matrix
        @ x
    )

    corr_penalty = np.maximum(correlation_matrix, 0)

    diversification_term = 0

    n = len(x)

    for i in range(n):
        for j in range(i + 1, n):

            diversification_term += (
                lambda_div
                * corr_penalty[i, j]
                * x[i]
                * x[j]
            )


    objective_value = (
        -return_term
        -liquidity_term
        +transaction_term
        +risk_term
        +diversification_term
    )

    return {
        "expected_return": float(return_term),
        "risk_penalty": float(risk_term),
        "transaction_cost": float(transaction_term),
        "liquidity_reward": float(liquidity_term),
        "diversification_penalty": float(diversification_term),
        "binary_objective": float(objective_value),
    }

def classical_continuous_breakdown(weights,expected_returns,covariance_matrix,transaction_cost_vector,previous_weights,config):
    q = config["risk_aversion"]
    eta = config["transaction_cost"]
    alpha = 0.001

    # Return
    portfolio_return = np.dot(weights, expected_returns)

    # Variance
    portfolio_variance = (
        weights.T
        @ covariance_matrix
        @ weights
    )

    # Transaction Cost
    transaction_cost = np.sum(
        transaction_cost_vector *
        np.abs(weights - previous_weights)
    )

    # Cash Penalty
    unused_cash = 1 - np.sum(weights)

    # Final Objective
    objective = (
        q * portfolio_variance
        - portfolio_return
        + eta * transaction_cost
        + alpha * unused_cash
    )

    return {
        "expected_return": float(portfolio_return),
        "risk_penalty": float(q * portfolio_variance),
        "transaction_cost": float(eta * transaction_cost),
        "unused_cash_penalty": float(alpha * unused_cash),
        "continuous_objective": float(objective)
    }

def quantum_continuous_breakdown(weights,expected_returns,covariance_matrix,transaction_cost_vector,liquidity_scores,previous_weights,config):
    q = config["risk_aversion"]
    eta=config["transaction_cost"]
    alpha=0.001

    # Return
    portfolio_return = np.dot(
        weights,
        expected_returns
    )

    # Variance
    portfolio_variance = (
        weights.T
        @ covariance_matrix
        @ weights
    )

    transaction_cost = np.sum(
        transaction_cost_vector *
        np.abs(weights - previous_weights)
    )
    
    unused_cash = 1 - np.sum(weights)    

    objective = (
        q * portfolio_variance
        - portfolio_return
        + eta * transaction_cost
        + alpha * unused_cash
    )

    return {
        "expected_return": float(portfolio_return),
        "risk_penalty": float(q * portfolio_variance),
        "transaction_cost": float(eta * transaction_cost),
        "unused_cash_penalty": float(alpha * unused_cash),
        "continuous_objective": float(objective),
    }