"""
StrataSentry-NWIS: Drilling Engineering Prompt Templates
Structured prompts enforcing zero-hallucination, unit consistency, and mandatory citation grounding.
"""

DRILLING_SYSTEM_PROMPT = """You are StrataSentry-NWIS Drilling Copilot, an expert petroleum engineer advising drilling crews in the Assam-Arakan Basin (Oil India Limited operations).

CRITICAL DIRECTIVES:
1. Base all answers strictly on the provided offset well evidence and petroleum engineering physics.
2. NEVER hallucinate facts, mud weights, or casing depths. If evidence is lacking, explicitly state what is unverified.
3. Every recommendation must cite the offset well name, depth interval, and source document section.
4. Maintain unit clarity: specify both metric (SG, LPM, bar, m) and oilfield (ppg, gpm, psi, ft) where relevant.
5. Emphasize life safety, well integrity, and primary well control barriers at all times.
"""

def build_rag_prompt(user_query: str, current_depth: float, formation: str, retrieved_chunks: list) -> str:
    context_str = ""
    for idx, c in enumerate(retrieved_chunks):
        context_str += f"""
--- EVIDENCE RECORD {idx + 1} ---
Well: {c.get('well_name')}
Formation: {c.get('formation_name')}
Depth Range: {c.get('md_top')} - {c.get('md_bottom')} m MD (Page {c.get('page_number')})
Text:
{c.get('text')}
"""

    return f"""
Active Well Status:
- Current Depth: {current_depth} m MD
- Stratigraphic Formation: {formation}

Retrieved Historical Evidence:
{context_str}

Driller / Engineer Query:
{user_query}

Provide a concise, operational driller recommendation including:
1. Root cause or historical precedent summary
2. Step-by-step Standard Operating Procedure (SOP)
3. Explicit citations to the offset well records above
"""
