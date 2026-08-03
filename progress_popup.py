import streamlit as st
import streamlit.components.v1 as components

steps = [
    "Loading Financial Data",
    "Creating QUBO Model",
    "Running Classical Optimization",
    "Running Quantum Optimization",
    "Generating Comparison"
]

def show_progress(current_step):

    html = f"""
    <style>

    #overlay {{
        position: fixed;
        top:0;
        left:0;
        width:100%;
        height:100%;
        background:rgba(0,0,0,0.55);
        display:flex;
        justify-content:center;
        align-items:center;
        z-index:99999;
    }}

    #popup {{
        width:520px;
        background:white;
        border-radius:15px;
        padding:30px;
        box-shadow:0 10px 35px rgba(0,0,0,.3);
        font-family:Arial;
    }}

    h2 {{
        text-align:center;
        margin-bottom:25px;
    }}

    .progress-container {{
        width:100%;
        height:15px;
        background:#e6e6e6;
        border-radius:10px;
        overflow:hidden;
        margin-bottom:25px;
    }}

    .progress-bar {{
        width:{(current_step+1)/len(steps)*100}%;
        height:100%;
        background:#00c853;
        transition:.4s;
    }}

    .step {{
        padding:10px;
        font-size:18px;
    }}

    .done {{
        color:green;
        font-weight:bold;
    }}

    .running {{
        color:#ff9800;
        font-weight:bold;
    }}

    .pending {{
        color:grey;
    }}

    </style>

    <div id="overlay">

        <div id="popup">

            <h2>🚀 Portfolio Optimization</h2>

            <div class="progress-container">
                <div class="progress-bar"></div>
            </div>

    """

    for i, step in enumerate(steps):

        if i < current_step:
            html += f'<div class="step done">✅ {step}</div>'

        elif i == current_step:
            html += f'<div class="step running">⏳ {step}</div>'

        else:
            html += f'<div class="step pending">⬜ {step}</div>'

    html += """
        </div>
    </div>
    """

    components.html(html, height=600)