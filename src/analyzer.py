# analyzer.py - Single Question Personality Profiler with Auto-Expansion (50 words min, robust MBTI parsing)
import os
import random
import base64
import datetime
import subprocess
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF

# ------------------------ STORY PROMPTS ------------------------
story_prompts = [
    "A struggling scientist builds a tool that bypasses paywalls, opening access to research for all. Reflect on the ethics, and your stance.",
    "A teacher hacks a grading system to expose unfair evaluation standards. Discuss your perspective.",
    "An online community bans anonymity to prevent abuse. Do you agree or disagree?",
    "A child speaks against a school’s unfair policy and goes viral. Is it bravery or immaturity?",
    "A company introduces brain-chip implants for cognitive enhancement. Would you opt in or stay away?"
]

current_prompt = random.choice(story_prompts)

# ------------------------ STREAMLIT UI ------------------------
st.title("🧠 MCP Personality Profiler (Single Question Mode)")
st.markdown("Answer the scenario below. Minimum **50 words** required. If your answer is too short, the system will auto‑expand it for analysis.")

st.subheader("Scenario:")
st.info(current_prompt)

response = st.text_area("✍️ Your response:", key="user_response", height=200)

submitted = st.button("🧠 Analyze Me")

# ------------------------ SETTINGS ------------------------
MIN_WORDS = 50

# ------------------------ EXPANSION FUNCTION ------------------------
def expand_short_answer(answer, min_words=50):
    if len(answer.split()) >= min_words or not answer.strip():
        return answer
    prompt = f"Expand this short response into a thoughtful, detailed answer (~100-120 words) while keeping the original meaning:\n\n'{answer}'"
    try:
        result = subprocess.run(
            ["ollama", "run", "deepseek-r1:7b"],
            input=prompt.encode(),
            capture_output=True,
            timeout=90
        )
        expanded_text = result.stdout.decode().strip()
        return expanded_text if expanded_text else answer
    except Exception:
        return answer

# ------------------------ ANALYSIS FUNCTION ------------------------
def analyze_with_deepseek(answer):
    prompt = f"""
You are a personality psychologist AI. Analyze the following reflective answer
and rate it from 1 to 5 in these traits:

- Openness
- Conscientiousness
- Extraversion
- Agreeableness
- Neuroticism
- Honesty-Humility
- Emotional Stability
- Creativity
- Assertiveness
- Empathy

Then guess their MBTI type (e.g., INFP, ESTJ) and write a 4–5 sentence summary.

Format:
Openness: X/5  
Conscientiousness: X/5  
Extraversion: X/5  
Agreeableness: X/5  
Neuroticism: X/5  
Honesty-Humility: X/5  
Emotional Stability: X/5  
Creativity: X/5  
Assertiveness: X/5  
Empathy: X/5  
MBTI: XXXX  
Summary: [Your summary]

User Response:
{answer}
"""
    try:
        result = subprocess.run(
            ["ollama", "run", "deepseek-r1:7b"],
            input=prompt.encode(),
            capture_output=True,
            timeout=120
        )
        return result.stdout.decode().strip()
    except Exception as e:
        return f"Error: {str(e)}"

# ------------------------ RADAR CHART ------------------------
def generate_chart(scores):
    labels = list(scores.keys())
    values = list(scores.values())
    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
    values += values[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6,6), subplot_kw=dict(polar=True))
    ax.fill(angles, values, color='skyblue', alpha=0.5)
    ax.plot(angles, values, color='blue', linewidth=2)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_title("Personality Trait Radar", size=16, pad=20)
    output_path = os.path.join(os.getcwd(), "chart.png")
    fig.savefig(output_path, bbox_inches="tight")
    plt.close()
    return output_path

# ------------------------ PDF REPORT ------------------------
def generate_pdf(scores, mbti, summary, chart_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Personality Profile Report", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.cell(0, 10, f"Predicted MBTI: {mbti}", ln=True)
    pdf.ln(10)
    pdf.multi_cell(0, 8, summary)
    pdf.ln(5)
    pdf.cell(0, 10, "Trait Scores:", ln=True)
    for trait, value in scores.items():
        pdf.cell(0, 8, f"- {trait}: {value}/5", ln=True)
    if os.path.exists(chart_path):
        pdf.image(chart_path, x=30, w=150)
    pdf_output = os.path.join(os.getcwd(), "personality_report.pdf")
    pdf.output(pdf_output)
    return pdf_output

# ------------------------ FINAL OUTPUT ------------------------
if submitted:
    if len(response.split()) < MIN_WORDS:
        st.warning(f"⚠️ Your response is shorter than {MIN_WORDS} words. Auto‑expanding it for analysis...")
    final_answer = expand_short_answer(response, min_words=MIN_WORDS)

    st.info("🧠 Analyzing your reflections with DeepSeek-R1... Please wait.")
    result_text = analyze_with_deepseek(final_answer)

    # Debug: Show raw AI output
    st.text_area("🔍 Raw AI Output", result_text, height=200)

    if result_text.startswith("Error") or "Openness" not in result_text:
        st.error("⚠️ AI failed to analyze your response. Try providing more detail.")
        st.stop()
    else:
        lines = result_text.split("\n")
        scores = {}
        for line in lines:
            if ":" in line and any(trait in line for trait in [
                "Openness","Conscientiousness","Extraversion","Agreeableness",
                "Neuroticism","Honesty-Humility","Emotional Stability",
                "Creativity","Assertiveness","Empathy"
            ]):
                try:
                    trait, value = line.split(":")
                    scores[trait.strip()] = float(value.strip().replace("/5",""))
                except:
                    continue

        mbti_line = next((l for l in lines if l.strip().lower().startswith("mbti")), None)
        if mbti_line:
            try:
                mbti = mbti_line.split(":")[1].strip()
            except:
                mbti = "???"
            summary_index = lines.index(mbti_line)+1
        else:
            mbti = "???"
            summary_index = len(lines)

        summary = "\n".join(lines[summary_index:]).strip()
        chart_path = generate_chart(scores)
        pdf_path = generate_pdf(scores, mbti, summary, chart_path)

        st.success(f"✅ Predicted MBTI: **{mbti}**")
        st.subheader("📝 Personality Summary")
        st.write(summary)

        st.subheader("📊 Trait Radar Chart")
        st.image(chart_path, use_container_width=True)

        with open(pdf_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="personality_report.pdf">📄 Download PDF Report</a>'
            st.markdown(href, unsafe_allow_html=True)
