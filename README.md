# GDHS_dev_dynamos
# 🩺 GDHS Dev Dynamos – Multi-Agent Medical AI

This project was built for the **Global Digital Health Summit Hackathon** 🏆.  
It uses **LangChain + LangGraph + OpenRouter (GPT-4o-mini)** to create a **multi-agent AI system** for medical reasoning, diagnosis support, and literature retrieval.

---

## 🚀 Features

- **Symptom Analyzer Agent**
  - Accepts patient symptoms, age, and history
  - Returns differential diagnoses with **ICD-10-CM (India)** codes
  - Provides risk level and rationale

- **Literature Agent**
  - Queries **PubMed** via NCBI API
  - Fetches relevant research articles
  - Summarizes abstracts (≤70 words each) using LLM
  - Provides AI-summarized references for evidence support

- **Orchestrator**
  - Chains Symptom Analyzer → Literature Agent
  - Produces a **combined diagnostic report**
  - Outputs JSON and human-readable summaries

---

## 📂 Project Structure

