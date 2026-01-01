# import pandas as pd
# from datetime import datetime
# import webbrowser
# import json
# import os
# import math

# def generate_dashboard():
#     try:
#         # ---------- LOAD DATA ----------
#         df = pd.read_csv("challan_database.csv")

#         if df.empty:
#             print("📊 No data found — dashboard not generated.")
#             return

#         if "Challan" not in df.columns:
#             raise ValueError("CSV must contain a 'Challan' column.")
#         if "Number Plate" not in df.columns:
#             raise ValueError("CSV must contain a 'Number Plate' column.")

#         df["Challan"] = pd.to_numeric(df["Challan"], errors="coerce").fillna(0)

#         # ---------- BASIC STATS ----------
#         violator_sum = df.groupby("Number Plate")["Challan"].sum().sort_values(ascending=False)
#         top_violator = violator_sum.idxmax() if not violator_sum.empty else "N/A"
#         top_violator_amount = int(violator_sum.max()) if not violator_sum.empty else 0

#         if "Violation Type" in df.columns and not df["Violation Type"].dropna().empty:
#             most_violated_rule = df["Violation Type"].mode()[0]
#         else:
#             most_violated_rule = "N/A"

#         total_challan = int(df["Challan"].sum())
#         last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#         # ---------- GRAPH DATA ----------
#         if "Violation Type" in df.columns:
#             vt_counts = df["Violation Type"].fillna("Unknown").value_counts()
#         else:
#             vt_counts = pd.Series(dtype=int)

#         graph_A_labels = json.dumps(list(vt_counts.index))
#         graph_A_values = json.dumps([int(x) for x in vt_counts.values])
#         graph_B_labels = json.dumps(list(violator_sum.index))
#         graph_B_values = json.dumps([int(x) for x in violator_sum.values])

#         # ---------- TABLES ----------
#         df_html = df.to_html(index=False, table_id="databaseTable", classes="data-table", border=0)
#         recent_html = df.tail(5).to_html(index=False, classes="data-table", border=0)
#         base_data = json.dumps(df.fillna("").to_dict(orient="records"))

#         # ---------- ALERT ----------
#         alert_html = ""
#         if top_violator_amount > 5000:
#             alert_html = f"<div class='alert-card'>🚨 ALERT: {top_violator} has high challans ₹{top_violator_amount}!</div>"

#         # ---------- FILTER ----------
#         filter_html = ""
#         if "Violation Type" in df.columns:
#             options = "".join(f"<option value='{t}'>{t}</option>" for t in df["Violation Type"].dropna().unique())
#             filter_html = f"""
#             <select id='filterSelect' onchange='filterByType()' class='filter'>
#               <option value=''>Filter by Violation Type</option>
#               {options}
#             </select>
#             """

#         # ---------- HTML START ----------
#         html_top = f"""<!DOCTYPE html>
# <html lang='en'>
# <head>
# <meta charset='utf-8'/>
# <title>🚦 Traffic Dashboard</title>
# <meta name='viewport' content='width=device-width, initial-scale=1'/>
# <script src='https://cdn.jsdelivr.net/npm/chart.js'></script>
# <link href='https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap' rel='stylesheet'>

# <style>
# :root {{
#   --accent: #10B981;
#   --accent-dark: #059669;
#   --accent-light: rgba(16, 185, 129, 0.1);
#   --accent-glow: rgba(16, 185, 129, 0.3);
#   --bg-primary: #FFFFFF;
#   --bg-secondary: #F9FAFB;
#   --text-primary: #111827;
#   --text-secondary: #6B7280;
#   --card-bg: #FFFFFF;
#   --card-border: #E5E7EB;
#   --glass-blur: none;
#   --border-radius: 16px;
#   --btn-radius: 20px;
#   --card-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
#   --sidebar-width: 300px;
#   --font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
#   --transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
#   --gradient-primary: linear-gradient(135deg, #10B981 0%, #059669 100%);
#   --gradient-secondary: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
#   --mode: light;
# }}

# /* Clean Dark */
# body.clean-dark {{
#   --accent: #10B981;
#   --accent-dark: #059669;
#   --accent-light: rgba(16, 185, 129, 0.15);
#   --accent-glow: rgba(16, 185, 129, 0.4);
#   --bg-primary: #0F172A;
#   --bg-secondary: #1E293B;
#   --text-primary: #F1F5F9;
#   --text-secondary: #94A3B8;
#   --card-bg: #1E293B;
#   --card-border: #334155;
#   --glass-blur: none;
#   --border-radius: 16px;
#   --btn-radius: 20px;
#   --card-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
#   --gradient-primary: linear-gradient(135deg, #10B981 0%, #059669 100%);
#   --gradient-secondary: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
#   --mode: dark;
# }}

# /* Professional Light */
# body.professional-light {{
#   --accent: #007AFF;
#   --accent-dark: #0056CC;
#   --accent-light: rgba(0, 122, 255, 0.1);
#   --accent-glow: rgba(0, 122, 255, 0.3);
#   --bg-primary: #FFFFFF;
#   --bg-secondary: #F8F9FA;
#   --text-primary: #1C1C1E;
#   --text-secondary: #8E8E93;
#   --card-bg: #FFFFFF;
#   --card-border: #E5E5EA;
#   --glass-blur: none;
#   --border-radius: 16px;
#   --btn-radius: 12px;
#   --card-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
#   --gradient-primary: linear-gradient(135deg, #007AFF 0%, #5856D6 100%);
#   --gradient-secondary: linear-gradient(135deg, #FF2D55 0%, #FF9500 100%);
#   --mode: light;
# }}

# /* Professional Dark */
# body.professional-dark {{
#   --accent: #007AFF;
#   --accent-dark: #0056CC;
#   --accent-light: rgba(0, 122, 255, 0.15);
#   --accent-glow: rgba(0, 122, 255, 0.4);
#   --bg-primary: #000000;
#   --bg-secondary: #1C1C1E;
#   --text-primary: #FFFFFF;
#   --text-secondary: #8E8E93;
#   --card-bg: #1C1C1E;
#   --card-border: #2C2C2E;
#   --glass-blur: none;
#   --border-radius: 16px;
#   --btn-radius: 12px;
#   --card-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
#   --gradient-primary: linear-gradient(135deg, #007AFF 0%, #5856D6 100%);
#   --gradient-secondary: linear-gradient(135deg, #FF2D55 0%, #FF9500 100%);
#   --mode: dark;
# }}

# /* Elegant Light - Changed to Red theme */
# body.elegant-light {{
#   --accent: #DC2626;
#   --accent-dark: #B91C1C;
#   --accent-light: rgba(220, 38, 38, 0.1);
#   --accent-glow: rgba(220, 38, 38, 0.3);
#   --bg-primary: #FEF2F2;
#   --bg-secondary: #FECACA;
#   --text-primary: #7F1D1D;
#   --text-secondary: #B91C1C;
#   --card-bg: #FFFFFF;
#   --card-border: #FCA5A5;
#   --glass-blur: none;
#   --border-radius: 16px;
#   --btn-radius: 12px;
#   --card-shadow: 0 8px 32px rgba(220, 38, 38, 0.1);
#   --gradient-primary: linear-gradient(135deg, #DC2626 0%, #B91C1C 100%);
#   --gradient-secondary: linear-gradient(135deg, #EF4444 0%, #F59E0B 100%);
#   --mode: light;
# }}

# /* Elegant Dark - Changed to Red dark theme */
# body.elegant-dark {{
#   --accent: #EF4444;
#   --accent-dark: #DC2626;
#   --accent-light: rgba(239, 68, 68, 0.15);
#   --accent-glow: rgba(239, 68, 68, 0.4);
#   --bg-primary: #1C1917;
#   --bg-secondary: #2C1A1A;
#   --text-primary: #FECACA;
#   --text-secondary: #FCA5A5;
#   --card-bg: #2C1A1A;
#   --card-border: #7F1D1D;
#   --glass-blur: none;
#   --border-radius: 16px;
#   --btn-radius: 12px;
#   --card-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
#   --gradient-primary: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
#   --gradient-secondary: linear-gradient(135deg, #EF4444 0%, #F59E0B 100%);
#   --mode: dark;
# }}

# /* Royal Purple Light */
# body.royal-purple-light {{
#   --accent: #7C3AED;
#   --accent-dark: #6D28D9;
#   --accent-light: rgba(124, 58, 237, 0.1);
#   --accent-glow: rgba(124, 58, 237, 0.3);
#   --bg-primary: #FDF4FF;
#   --bg-secondary: #FAE8FF;
#   --text-primary: #701A75;
#   --text-secondary: #A21CAF;
#   --card-bg: #FFFFFF;
#   --card-border: #F0ABFC;
#   --glass-blur: none;
#   --border-radius: 20px;
#   --btn-radius: 25px;
#   --card-shadow: 0 8px 32px rgba(124, 58, 237, 0.1);
#   --gradient-primary: linear-gradient(135deg, #7C3AED 0%, #A855F7 100%);
#   --gradient-secondary: linear-gradient(135deg, #EC4899 0%, #F59E0B 100%);
#   --mode: light;
# }}

# /* Royal Purple Dark */
# body.royal-purple-dark {{
#   --accent: #7C3AED;
#   --accent-dark: #6D28D9;
#   --accent-light: rgba(124, 58, 237, 0.15);
#   --accent-glow: rgba(124, 58, 237, 0.4);
#   --bg-primary: #1E1B2E;
#   --bg-secondary: #2A2640;
#   --text-primary: #F1F5F9;
#   --text-secondary: #C4B5FD;
#   --card-bg: #2A2640;
#   --card-border: #3E3659;
#   --glass-blur: none;
#   --border-radius: 20px;
#   --btn-radius: 25px;
#   --card-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
#   --gradient-primary: linear-gradient(135deg, #7C3AED 0%, #A855F7 100%);
#   --gradient-secondary: linear-gradient(135deg, #EC4899 0%, #F59E0B 100%);
#   --mode: dark;
# }}

# * {{
#   box-sizing: border-box;
#   margin: 0;
#   padding: 0;
# }}

# body {{
#   font-family: var(--font-family);
#   color: var(--text-primary);
#   min-height: 100vh;
#   transition: var(--transition);
#   overflow-x: hidden;
#   background: var(--bg-primary);
# }}

# /* Animated Background */
# .animated-bg {{
#   position: fixed;
#   top: 0;
#   left: 0;
#   width: 100%;
#   height: 100%;
#   z-index: -1;
#   pointer-events: none;
# }}

# .bubble {{
#   position: absolute;
#   border-radius: 50%;
#   background: var(--accent);
#   animation: float 2s infinite ease-in-out;
#   opacity: 0.08;
#   filter: blur(60px);
# }}

# .bubble:nth-child(odd) {{
#   animation-duration: 2s;
#   animation-delay: -2s;
# }}

# .bubble:nth-child(even) {{
#   animation-duration: 2s;
#   animation-delay: -2s;
# }}

# @keyframes float {{
#   0%, 100% {{ 
#     transform: translate(0, 0) rotate(0deg) scale(1);
#     opacity: 0.08;
#   }}
#   25% {{ 
#     transform: translate(150px, -200px) rotate(90deg) scale(1.4);
#     opacity: 0.12;
#   }}
#   50% {{ 
#     transform: translate(-120px, -250px) rotate(180deg) scale(1.1);
#     opacity: 0.06;
#   }}
#   75% {{ 
#     transform: translate(-200px, -150px) rotate(270deg) scale(1.3);
#     opacity: 0.1;
#   }}
# }}

# /* Floating Particles */
# .particle {{
#   position: absolute;
#   width: 50px;
#   height: 50px;
#   background: var(--accent);
#   border-radius: 50%;
#   animation: particleFloat 5s infinite linear;
#   opacity: 0.3;
# }}

# @keyframes particleFloat {{
#   0% {{ transform: translateY(100vh) translateX(0) rotate(0deg); opacity: 0; }}
#   10% {{ opacity: 0.3; }}
#   90% {{ opacity: 0.3; }}
#   100% {{ transform: translateY(-100px) translateX(150px) rotate(360deg); opacity: 0; }}
# }}

# /* Glow Effects */
# .glow {{
#   position: fixed;
#   width: 300px;
#   height: 300px;
#   border-radius: 50%;
#   background: var(--accent);
#   filter: blur(150px);
#   opacity: 0.08;
#   animation: glowMove 30s infinite ease-in-out;
#   z-index: -1;
# }}

# .glow-1 {{
#   top: 10%;
#   left: 5%;
#   animation-delay: 0s;
# }}

# .glow-2 {{
#   top: 70%;
#   right: 5%;
#   animation-delay: -15s;
# }}

# .glow-3 {{
#   bottom: 20%;
#   left: 20%;
#   animation-delay: -10s;
# }}

# @keyframes glowMove {{
#   0%, 100% {{ transform: translate(0, 0) scale(1); opacity: 0.08; }}
#   33% {{ transform: translate(80px, -100px) scale(1.4); opacity: 0.12; }}
#   66% {{ transform: translate(-100px, 80px) scale(0.9); opacity: 0.06; }}
# }}

# /* Sidebar */
# .sidebar {{
#   width: var(--sidebar-width);
#   position: fixed;
#   top: 0;
#   bottom: 0;
#   left: 0;
#   padding: 40px 25px;
#   z-index: 1000;
#   overflow-y: auto;
#   transition: var(--transition);
#   background: var(--bg-secondary);
#   border-right: 1px solid var(--card-border);
#   backdrop-filter: var(--glass-blur);
# }}

# .sidebar h2 {{
#   text-align: center;
#   margin-bottom: 40px;
#   font-weight: 800;
#   font-size: 26px;
#   color: var(--text-primary);
#   position: relative;
# }}

# .sidebar h2::after {{
#   content: '';
#   position: absolute;
#   bottom: -15px;
#   left: 50%;
#   transform: translateX(-50%);
#   width: 60px;
#   height: 4px;
#   background: var(--gradient-primary);
#   border-radius: 2px;
# }}

# .sidebar a {{
#   display: flex;
#   align-items: center;
#   gap: 15px;
#   padding: 18px 25px;
#   margin: 12px 0;
#   background: var(--card-bg);
#   border: 1px solid var(--card-border);
#   border-radius: var(--border-radius);
#   color: var(--text-primary);
#   text-decoration: none;
#   transition: var(--transition);
#   font-weight: 600;
#   cursor: pointer;
#   box-shadow: var(--card-shadow);
#   position: relative;
#   overflow: hidden;
# }}

# .sidebar a::before {{
#   content: '';
#   position: absolute;
#   top: 0;
#   left: -100%;
#   width: 100%;
#   height: 100%;
#   background: var(--gradient-primary);
#   transition: var(--transition);
#   opacity: 0.1;
# }}

# .sidebar a:hover::before {{
#   left: 0;
# }}

# .sidebar a:hover {{
#   transform: translateX(8px);
#   border-color: var(--accent);
#   box-shadow: 0 8px 25px var(--accent-glow);
# }}

# /* Theme Controls */
# .theme-folder {{
#   margin-top: 30px;
#   background: var(--card-bg);
#   border: 1px solid var(--card-border);
#   border-radius: var(--border-radius);
#   padding: 25px;
#   box-shadow: var(--card-shadow);
#   backdrop-filter: var(--glass-blur);
# }}

# .theme-folder h4 {{
#   margin: 0;
#   cursor: pointer;
#   display: flex;
#   justify-content: space-between;
#   align-items: center;
#   font-weight: 700;
#   color: var(--text-primary);
#   padding: 12px 0;
#   font-size: 16px;
# }}

# .theme-colors {{
#   display: none;
#   grid-template-columns: 1fr;
#   gap: 12px;
#   margin-top: 20px;
# }}

# .theme-option {{
#   padding: 16px 20px;
#   border: 2px solid var(--card-border);
#   border-radius: var(--border-radius);
#   background: var(--card-bg);
#   color: var(--text-primary);
#   cursor: pointer;
#   transition: var(--transition);
#   font-weight: 600;
#   font-size: 14px;
#   text-align: left;
#   position: relative;
#   overflow: hidden;
# }}

# .theme-option::before {{
#   content: '';
#   position: absolute;
#   top: 0;
#   left: -100%;
#   width: 100%;
#   height: 100%;
#   background: var(--gradient-primary);
#   transition: var(--transition);
#   opacity: 0.1;
# }}

# .theme-option:hover::before {{
#   left: 0;
# }}

# .theme-option:hover {{
#   transform: translateX(5px);
#   border-color: var(--accent);
#   box-shadow: 0 4px 15px var(--accent-glow);
# }}

# .theme-option.active {{
#   border-color: var(--accent);
#   background: var(--accent);
#   color: white;
#   box-shadow: 0 4px 20px var(--accent-glow);
#   transform: translateX(5px);
# }}

# /* Color Picker Section */
# .color-folder {{
#   margin-top: 25px;
#   background: var(--card-bg);
#   border: 1px solid var(--card-border);
#   border-radius: var(--border-radius);
#   padding: 25px;
#   box-shadow: var(--card-shadow);
#   backdrop-filter: var(--glass-blur);
# }}

# .color-folder h4 {{
#   margin: 0;
#   cursor: pointer;
#   display: flex;
#   justify-content: space-between;
#   align-items: center;
#   font-weight: 700;
#   color: var(--text-primary);
#   padding: 12px 0;
#   font-size: 16px;
# }}

# .color-palette {{
#   display: none;
#   flex-wrap: wrap;
#   gap: 12px;
#   margin-top: 20px;
#   justify-content: center;
# }}

# .color-option {{
#   width: 40px;
#   height: 40px;
#   border: 3px solid var(--card-border);
#   border-radius: 50%;
#   cursor: pointer;
#   transition: var(--transition);
#   position: relative;
# }}

# .color-option::before {{
#   content: '';
#   position: absolute;
#   top: -6px;
#   left: -6px;
#   right: -6px;
#   bottom: -6px;
#   border-radius: 50%;
#   background: var(--gradient-primary);
#   opacity: 0;
#   transition: var(--transition);
# }}

# .color-option:hover {{
#   transform: scale(1.15) rotate(5deg);
#   box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
# }}

# .color-option:hover::before {{
#   opacity: 0.3;
# }}

# .color-option.active {{
#   border-color: white;
#   transform: scale(1.1);
#   box-shadow: 0 0 0 3px var(--accent), 0 8px 25px rgba(0, 0, 0, 0.4);
# }}

# .color-option.active::before {{
#   opacity: 0.4;
# }}

# /* Main Content */
# .main {{
#   margin-left: var(--sidebar-width);
#   padding: 40px;
#   min-height: 100vh;
#   transition: var(--transition);
# }}

# /* Header */
# header {{
#   background: var(--card-bg);
#   border: 1px solid var(--card-border);
#   border-radius: var(--border-radius);
#   padding: 30px 40px;
#   margin-bottom: 30px;
#   box-shadow: var(--card-shadow);
#   display: flex;
#   justify-content: space-between;
#   align-items: center;
#   backdrop-filter: var(--glass-blur);
#   position: relative;
#   overflow: hidden;
# }}

# header::before {{
#   content: '';
#   position: absolute;
#   top: 0;
#   left: 0;
#   width: 100%;
#   height: 100%;
#   background: var(--gradient-primary);
#   opacity: 0.03;
#   z-index: -1;
# }}

# header h2 {{
#   font-size: 32px;
#   font-weight: 800;
#   color: var(--text-primary);
#   margin: 0;
# }}

# header p {{
#   color: var(--text-secondary);
#   margin: 8px 0 0 0;
#   font-size: 15px;
#   font-weight: 500;
# }}

# .header-controls {{
#   display: flex;
#   gap: 15px;
#   align-items: center;
# }}

# .btn-light {{
#   background: var(--gradient-primary);
#   border: none;
#   color: white;
#   border-radius: var(--btn-radius);
#   padding: 16px 32px;
#   cursor: pointer;
#   font-weight: 700;
#   transition: var(--transition);
#   box-shadow: 0 4px 20px var(--accent-glow);
#   font-family: var(--font-family);
#   position: relative;
#   overflow: hidden;
#   text-transform: uppercase;
#   letter-spacing: 0.5px;
#   font-size: 14px;
# }}

# .btn-light::before {{
#   content: '';
#   position: absolute;
#   top: 0;
#   left: -100%;
#   width: 100%;
#   height: 100%;
#   background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
#   transition: var(--transition);
# }}

# .btn-light:hover::before {{
#   left: 100%;
# }}

# .btn-light:hover {{
#   transform: translateY(-3px);
#   box-shadow: 0 8px 30px var(--accent-glow);
# }}

# /* Cards */
# .cards {{
#   display: flex;
#   flex-wrap: wrap;
#   gap: 25px;
#   margin-bottom: 30px;
# }}

# .card {{
#   flex: 1;
#   min-width: 280px;
#   padding: 30px;
#   background: var(--card-bg);
#   border: 1px solid var(--card-border);
#   border-radius: var(--border-radius);
#   text-align: center;
#   transition: var(--transition);
#   box-shadow: var(--card-shadow);
#   backdrop-filter: var(--glass-blur);
#   position: relative;
#   overflow: hidden;
# }}

# .card::before {{
#   content: '';
#   position: absolute;
#   top: 0;
#   left: 0;
#   width: 100%;
#   height: 4px;
#   background: var(--gradient-primary);
# }}

# .card:hover {{
#   transform: translateY(-8px) scale(1.02);
#   box-shadow: 0 16px 40px rgba(0, 0, 0, 0.15);
#   border-color: var(--accent);
# }}

# .card h3 {{
#   color: var(--text-secondary);
#   font-size: 14px;
#   font-weight: 600;
#   margin-bottom: 12px;
#   text-transform: uppercase;
#   letter-spacing: 1px;
# }}

# .card p {{
#   color: var(--text-primary);
#   font-size: 16px;
#   margin-bottom: 20px;
#   font-weight: 500;
# }}

# .card h2 {{
#   color: var(--accent);
#   font-size: 36px;
#   font-weight: 800;
# }}

# /* Animated Counter */
# .animated-counter {{
#   font-size: 36px;
#   font-weight: 800;
#   color: var(--accent);
#   margin-bottom: 20px;
# }}

# /* Alert */
# .alert-card {{
#   background: linear-gradient(135deg, rgba(255, 59, 48, 0.1), rgba(255, 69, 58, 0.05));
#   border-left: 6px solid #FF3B30;
#   padding: 25px;
#   border-radius: var(--border-radius);
#   margin-bottom: 30px;
#   border: 1px solid rgba(255, 59, 48, 0.2);
#   backdrop-filter: var(--glass-blur);
#   animation: pulse 2s infinite;
# }}

# @keyframes pulse {{
#   0% {{ box-shadow: 0 0 0 0 rgba(255, 59, 48, 0.4); }}
#   70% {{ box-shadow: 0 0 0 15px rgba(255, 59, 48, 0); }}
#   100% {{ box-shadow: 0 0 0 0 rgba(255, 59, 48, 0); }}
# }}

# /* Controls */
# .controls {{
#   display: flex;
#   gap: 20px;
#   margin-bottom: 30px;
#   flex-wrap: wrap;
# }}

# input[type="text"], select.filter {{
#   flex: 1;
#   min-width: 320px;
#   padding: 18px 25px;
#   border-radius: var(--border-radius);
#   border: 2px solid var(--card-border);
#   background: var(--card-bg);
#   color: var(--text-primary);
#   font-size: 16px;
#   transition: var(--transition);
#   font-family: var(--font-family);
#   backdrop-filter: var(--glass-blur);
# }}

# input[type="text"]:focus, select.filter:focus {{
#   outline: none;
#   border-color: var(--accent);
#   box-shadow: 0 0 0 4px var(--accent-glow);
#   transform: translateY(-2px);
# }}

# input[type="text"]::placeholder {{
#   color: var(--text-secondary);
# }}

# /* Tables */
# .data-table {{
#   width: 100%;
#   border-collapse: collapse;
#   background: var(--card-bg);
#   border: 1px solid var(--card-border);
#   border-radius: var(--border-radius);
#   overflow: hidden;
#   box-shadow: var(--card-shadow);
#   backdrop-filter: var(--glass-blur);
# }}

# .data-table th {{
#   background: var(--gradient-primary);
#   color: white;
#   padding: 20px;
#   text-align: center;
#   font-weight: 700;
#   font-size: 14px;
#   text-transform: uppercase;
#   letter-spacing: 0.5px;
# }}

# .data-table td {{
#   padding: 18px;
#   border-bottom: 1px solid var(--card-border);
#   text-align: center;
#   color: var(--text-primary);
#   font-weight: 500;
#   transition: var(--transition);
# }}

# .data-table tr:hover td {{
#   background: var(--accent-light);
#   transform: scale(1.01);
# }}

# /* Sections */
# .section {{
#   display: none;
#   animation: fadeInUp 0.6s ease-out;
# }}

# .section.visible {{
#   display: block;
# }}

# @keyframes fadeInUp {{
#   from {{ opacity: 0; transform: translateY(30px); }}
#   to {{ opacity: 1; transform: translateY(0); }}
# }}

# /* Graph Container */
# .graph-container {{
#   background: var(--card-bg);
#   border: 1px solid var(--card-border);
#   border-radius: var(--border-radius);
#   padding: 40px;
#   box-shadow: var(--card-shadow);
#   position: relative;
#   overflow: hidden;
#   min-height: 600px;
#   backdrop-filter: var(--glass-blur);
# }}

# .graph-container::before {{
#   content: '';
#   position: absolute;
#   top: 0;
#   left: 0;
#   right: 0;
#   height: 4px;
#   background: var(--gradient-primary);
# }}

# /* Graph Switch */
# .graph-switch {{
#   text-align: center;
#   margin-bottom: 30px;
#   display: flex;
#   gap: 15px;
#   justify-content: center;
#   flex-wrap: wrap;
# }}

# .graph-btn {{
#   padding: 16px 32px;
#   border: none;
#   border-radius: var(--btn-radius);
#   background: var(--card-bg);
#   color: var(--text-primary);
#   cursor: pointer;
#   font-weight: 700;
#   transition: var(--transition);
#   border: 2px solid var(--card-border);
#   font-family: var(--font-family);
#   text-transform: uppercase;
#   letter-spacing: 0.5px;
#   font-size: 14px;
#   position: relative;
#   overflow: hidden;
# }}

# .graph-btn::before {{
#   content: '';
#   position: absolute;
#   top: 0;
#   left: -100%;
#   width: 100%;
#   height: 100%;
#   background: var(--gradient-primary);
#   transition: var(--transition);
#   opacity: 0.1;
# }}

# .graph-btn:hover::before {{
#   left: 0;
# }}

# .graph-btn:hover {{
#   transform: translateY(-3px);
#   border-color: var(--accent);
#   box-shadow: 0 6px 20px var(--accent-glow);
# }}

# .graph-btn.active {{
#   background: var(--gradient-primary);
#   color: white;
#   border-color: transparent;
#   box-shadow: 0 4px 20px var(--accent-glow);
#   transform: translateY(-2px);
# }}

# /* Canvas */
# .chart-wrap {{
#   position: relative;
#   width: 100%;
#   height: 500px;
#   margin: 0 auto;
# }}

# canvas {{
#   width: 100% !important;
#   height: 100% !important;
#   display: none;
#   opacity: 0;
#   transition: opacity 0.6s ease;
# }}

# canvas.visible {{
#   display: block;
#   opacity: 1;
# }}

# /* Stats Grid */
# .stats-grid {{
#   display: grid;
#   grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
#   gap: 20px;
#   margin-bottom: 30px;
# }}

# .stat-item {{
#   background: var(--card-bg);
#   border: 1px solid var(--card-border);
#   border-radius: var(--border-radius);
#   padding: 25px;
#   text-align: center;
#   transition: var(--transition);
#   box-shadow: var(--card-shadow);
#   backdrop-filter: var(--glass-blur);
# }}

# .stat-item:hover {{
#   transform: translateY(-5px);
#   border-color: var(--accent);
# }}

# .stat-number {{
#   font-size: 32px;
#   font-weight: 800;
#   color: var(--accent);
#   margin-bottom: 8px;
# }}

# .stat-label {{
#   font-size: 14px;
#   color: var(--text-secondary);
#   font-weight: 600;
#   text-transform: uppercase;
#   letter-spacing: 0.5px;
# }}

# /* Mode Toggle */
# .mode-toggle {{
#   background: var(--card-bg);
#   border: 2px solid var(--card-border);
#   border-radius: var(--btn-radius);
#   padding: 12px 20px;
#   cursor: pointer;
#   transition: var(--transition);
#   display: flex;
#   align-items: center;
#   gap: 8px;
#   font-weight: 600;
#   color: var(--text-primary);
# }}

# .mode-toggle:hover {{
#   border-color: var(--accent);
#   transform: translateY(-2px);
# }}

# /* Export Modal */
# .modal {{
#   display: none;
#   position: fixed;
#   top: 0;
#   left: 0;
#   width: 100%;
#   height: 100%;
#   background: rgba(0, 0, 0, 0.5);
#   z-index: 2000;
#   backdrop-filter: blur(5px);
# }}

# .modal-content {{
#   position: absolute;
#   top: 50%;
#   left: 50%;
#   transform: translate(-50%, -50%);
#   background: var(--card-bg);
#   border: 1px solid var(--card-border);
#   border-radius: var(--border-radius);
#   padding: 40px;
#   box-shadow: var(--card-shadow);
#   min-width: 400px;
# }}

# .modal-buttons {{
#   display: flex;
#   gap: 15px;
#   margin-top: 25px;
#   justify-content: center;
# }}

# /* Responsive */
# @media (max-width: 1024px) {{
#   .sidebar {{
#     width: 280px;
#   }}
#   .main {{
#     margin-left: 280px;
#   }}
# }}

# @media (max-width: 768px) {{
#   .sidebar {{
#     width: 100%;
#     position: relative;
#     height: auto;
#   }}
#   .main {{
#     margin-left: 0;
#     padding: 25px;
#   }}
#   .cards {{
#     flex-direction: column;
#   }}
#   .graph-switch {{
#     flex-direction: column;
#     align-items: center;
#   }}
#   .controls {{
#     flex-direction: column;
#   }}
#   input[type="text"], select.filter {{
#     min-width: 100%;
#   }}
#   .header-controls {{
#     flex-direction: column;
#     gap: 10px;
#   }}
#   .modal-content {{
#     min-width: 90%;
#     margin: 20px;
#   }}
# }}
# </style>
# </head>
# <body class="clean-light">
#   <div class="animated-bg" id="animatedBg"></div>
#   <div class="glow glow-1"></div>
#   <div class="glow glow-2"></div>
#   <div class="glow glow-3"></div>
  
#   <div class='sidebar'>
#     <h2>🚦 TRAFFIC ANALYTICS</h2>
#     <a onclick="showSection('dashboard')">📊 Dashboard Overview</a>
#     <a onclick="showSection('activity')">⚡ Recent Activity</a>
#     <a onclick="showSection('statistics')">📈 Analytics & Charts</a>
#     <a onclick="exportData()">📁 Export Data</a>
#     <a onclick="showSection('about')">ℹ️ About Project</a>
    
#     <div class='theme-folder'>
#       <h4 onclick="toggleThemeColors()">🎨 THEME STYLES <span id='themeArrow'>▶</span></h4>
#       <div id='themeColors' class='theme-colors'>
#         <div class='theme-option active' onclick="setTheme('clean-light')">🌿 Clean</div>
#         <div class='theme-option' onclick="setTheme('professional-light')">💼 Professional</div>
#         <div class='theme-option' onclick="setTheme('elegant-light')">✨ Elegant</div>
#         <div class='theme-option' onclick="setTheme('royal-purple-light')">👑 Royal Purple</div>
#       </div>
#     </div>

#     <div class='color-folder'>
#       <h4 onclick="toggleColorPalette()">🎨 ACCENT COLORS <span id='colorArrow'>▶</span></h4>
#       <div id='colorPalette' class='color-palette'>
#         <div class='color-option active' style='background:#10B981' onclick="setAccentColor('#10B981')"></div>
#         <div class='color-option' style='background:#007AFF' onclick="setAccentColor('#007AFF')"></div>
#         <div class='color-option' style='background:#8B5CF6' onclick="setAccentColor('#8B5CF6')"></div>
#         <div class='color-option' style='background:#7C3AED' onclick="setAccentColor('#7C3AED')"></div>
#         <div class='color-option' style='background:#2563EB' onclick="setAccentColor('#2563EB')"></div>
#         <div class='color-option' style='background:#DC2626' onclick="setAccentColor('#DC2626')"></div>
#         <div class='color-option' style='background:#EA580C' onclick="setAccentColor('#EA580C')"></div>
#         <div class='color-option' style='background:#CA8A04' onclick="setAccentColor('#CA8A04')"></div>
#         <div class='color-option' style='background:#16A34A' onclick="setAccentColor('#16A34A')"></div>
#         <div class='color-option' style='background:#0891B2' onclick="setAccentColor('#0891B2')"></div>
#         <div class='color-option' style='background:#9333EA' onclick="setAccentColor('#9333EA')"></div>
#         <div class='color-option' style='background:#DB2777' onclick="setAccentColor('#DB2777')"></div>
#       </div>
#     </div>
#   </div>
#   <div class='main'>
#     <div id='dashboard_section' class='section visible'>
#       <header>
#         <div>
#           <h2>🚨 TRAFFIC VIOLATION DASHBOARD</h2>
#           <p>Last Updated: {last_update}</p>
#         </div>
#         <div class="header-controls">
#           <button class='mode-toggle' onclick="toggleDarkMode()">
#             <span id='modeIcon'>🌙</span>
#             <span id='modeText'>Dark Mode</span>
#           </button>
#           <button class='btn-light' onclick='refreshData()'>
#             <span id='refreshText'>🔄 Refresh Data</span>
#           </button>
#         </div>
#       </header>

#       {alert_html}

#       <!-- Stats Grid -->
#       <div class='stats-grid'>
#         <div class='stat-item'>
#           <div class='stat-number' id="totalViolations">{len(df)}</div>
#           <div class='stat-label'>Total Violations</div>
#         </div>
#         <div class='stat-item'>
#           <div class='stat-number' id="uniqueVehicles">{len(df['Number Plate'].unique())}</div>
#           <div class='stat-label'>Unique Vehicles</div>
#         </div>
#         <div class='stat-item'>
#           <div class='stat-number' id="violationTypes">{len(df['Violation Type'].unique()) if 'Violation Type' in df.columns else 'N/A'}</div>
#           <div class='stat-label'>Violation Types</div>
#         </div>
#       </div>

#       <div class='cards'>
#         <div class='card'>
#           <h3>👤 TOP VIOLATOR</h3>
#           <p>{top_violator}</p>
#           <div class="animated-counter">₹{top_violator_amount}</div>
#         </div>
#         <div class='card'>
#           <h3>⚠️ MOST VIOLATED RULE</h3>
#           <p>{most_violated_rule}</p>
#           <div class="animated-counter" id="violationCount">{vt_counts.max() if not vt_counts.empty else 0}</div>
#         </div>
#         <div class='card'>
#           <h3>💰 TOTAL CHALLAN</h3>
#           <p>Total Amount Collected</p>
#           <div class="animated-counter">₹{total_challan}</div>
#         </div>
#       </div>

#       <div class='controls'>
#         <input id='searchInput' type='text' placeholder='🔍 Search by name, number plate, or violation type...' oninput='applySearch()'>
#         {filter_html}
#       </div>

#       {df_html}
#     </div>

#     <div id='activity_section' class='section'>
#       <h2 style="color: var(--text-primary); margin-bottom: 25px; font-size: 28px; font-weight: 800;">⚡ RECENT VIOLATION ACTIVITY</h2>
#       {recent_html}
#     </div>

#     <div id='statistics_section' class='section'>
#       <h2 style="color: var(--text-primary); margin-bottom: 25px; font-size: 28px; font-weight: 800;">📈 ANALYTICS & CHARTS</h2>
#       <div class='graph-switch'>
#         <button class='graph-btn active' onclick="showGraph('A')" id="btnA">📊 VIOLATION DISTRIBUTION</button>
#         <button class='graph-btn' onclick="showGraph('B')" id="btnB">💰 TOP VIOLATORS</button>
#       </div>
#       <div class='graph-container'>
#         <div class='chart-wrap'><canvas id='chartA' class='visible'></canvas></div>
#         <div class='chart-wrap'><canvas id='chartB'></canvas></div>
#       </div>
#     </div>

#     <div id='about_section' class='section'>
#       <div style="padding: 40px; border-radius: var(--border-radius); background: var(--card-bg); border: 1px solid var(--card-border); box-shadow: var(--card-shadow); backdrop-filter: var(--glass-blur); position: relative; overflow: hidden;">
#         <div style="position: absolute; top: 0; left: 0; width: 100%; height: 4px; background: var(--gradient-primary);"></div>
#         <h2 style="color: var(--text-primary); margin-bottom: 25px; font-size: 28px; font-weight: 800;">ℹ️ ABOUT THIS PROJECT</h2>
#         <p style="color: var(--text-primary); line-height: 1.7; margin-bottom: 20px; font-size: 16px; font-weight: 500;">
#           Created <strong style="color: var(--accent);"></strong> — A professional, interactive traffic analytics dashboard featuring:
#         </p>
# <p style="font-size: 16px; font-weight: 600; color: var(--text-primary);">
#   Interactive Traffic Analytics Dashboard Featuring:
# </p>

# <ul style="color: var(--text-primary); line-height: 1.7; margin-left: 25px; font-size: 15px; font-weight: 500; list-style-type: disc;">
#   <li>The project is titled “Automated Traffic Violation Detection.”</li>
#   <li>It aims to automatically detect helmet violations and triple riding using AI and computer vision.</li>
#   <li>The system processes live CCTV footage or recorded videos.</li>
#   <li>YOLOv8 is used for real-time detection of helmets, bikes, and riders.</li>
#   <li>EasyOCR reads the vehicle number plate from detected images.</li>
#   <li>Detected violations are automatically classified and stored with proof images.</li>
#   <li>The system creates a challan record for each violation.</li>
#   <li>A dashboard interface displays all records with search, filters, graphs, and export options.</li>
#   <li>The dashboard helps in analyzing violations and tracking repeat offenders.</li>
#   <li>The system reduces manual monitoring and improves accuracy in traffic rule enforcement.</li>
#   <li>Evidence is organized in structured folders (helmet, number plate, full image).</li>
#   <li>The model achieved about 87% precision, 84% recall, and 97% mAP@50.</li>
# </ul>

#       </div>
#     </div>
#   </div>

#   <!-- Export Modal -->
#   <div id="exportModal" class="modal">
#     <div class="modal-content">
#       <h3 style="color: var(--text-primary); margin-bottom: 20px; text-align: center;">📁 Export Data</h3>
#       <p style="color: var(--text-secondary); text-align: center; margin-bottom: 30px;">Choose your preferred export format:</p>
#       <div class="modal-buttons">
#         <button class="btn-light" onclick="downloadCSV()">📊 Export CSV</button>
#         <button class="btn-light" onclick="downloadJSON()">📋 Export JSON</button>
#         <button class="btn-light" onclick="downloadPDF()">📄 Export PDF</button>
#         <button class="mode-toggle" onclick="closeModal()" style="background: var(--card-bg);">Cancel</button>
#       </div>
#     </div>
#   </div>

# <script>
# const A_LABELS = {graph_A_labels};
# const A_VALUES = {graph_A_values};
# const B_LABELS = {graph_B_labels};
# const B_VALUES = {graph_B_values};
# const BASE_DATA = {base_data};

# let FILTERED = [...BASE_DATA];
# let chartA, chartB;
# let currentGraph = 'A';
# let currentAccentColor = '#10B981';

# // Theme configurations with dark/light variants
# const themeConfigs = {{
#     'clean-light': {{ mode: 'light', accent: '#10B981' }},
#     'clean-dark': {{ mode: 'dark', accent: '#10B981' }},
#     'professional-light': {{ mode: 'light', accent: '#007AFF' }},
#     'professional-dark': {{ mode: 'dark', accent: '#007AFF' }},
#     'elegant-light': {{ mode: 'light', accent: '#8B5CF6' }},
#     'elegant-dark': {{ mode: 'dark', accent: '#8B5CF6' }},
#     'royal-purple-light': {{ mode: 'light', accent: '#7C3AED' }},
#     'royal-purple-dark': {{ mode: 'dark', accent: '#7C3AED' }}
# }};

# function createBubbles() {{
#     const bg = document.getElementById('animatedBg');
#     bg.innerHTML = '';
    
#     // Create large floating bubbles - increased count and size
#     const bubbleCount = 20;
#     for (let i = 0; i < bubbleCount; i++) {{
#         const bubble = document.createElement('div');
#         bubble.className = 'bubble';
#         const size = Math.random() * 500 + 300; // Larger bubbles
#         bubble.style.width = size + 'px';
#         bubble.style.height = size + 'px';
#         bubble.style.left = Math.random() * 100 + '%';
#         bubble.style.top = Math.random() * 100 + '%';
#         bubble.style.background = currentAccentColor;
#         bubble.style.opacity = Math.random() * 0.1 + 0.05;
#         bubble.style.animationDelay = Math.random() * 20 + 's';
#         bg.appendChild(bubble);
#     }}
    
#     // Create small floating particles - increased count
#     const particleCount = 50;
#     for (let i = 0; i < particleCount; i++) {{
#         const particle = document.createElement('div');
#         particle.className = 'particle';
#         particle.style.left = Math.random() * 100 + '%';
#         particle.style.animationDelay = Math.random() * 15 + 's';
#         particle.style.background = currentAccentColor;
#         particle.style.opacity = Math.random() * 0.3 + 0.1;
#         bg.appendChild(particle);
#     }}
# }}

# function toggleThemeColors() {{
#     const el = document.getElementById('themeColors');
#     const arrow = document.getElementById('themeArrow');
#     el.style.display = (el.style.display === 'grid') ? 'none' : 'grid';
#     arrow.textContent = (el.style.display === 'grid') ? '▼' : '▶';
# }}

# function toggleColorPalette() {{
#     const el = document.getElementById('colorPalette');
#     const arrow = document.getElementById('colorArrow');
#     el.style.display = (el.style.display === 'flex') ? 'none' : 'flex';
#     arrow.textContent = (el.style.display === 'flex') ? '▼' : '▶';
# }}

# function setTheme(themeName) {{
#     document.body.className = themeName;
    
#     // Update active theme option
#     document.querySelectorAll('.theme-option').forEach(opt => opt.classList.remove('active'));
#     event.target.classList.add('active');
    
#     // Set the accent color for this theme
#     const themeColor = themeConfigs[themeName].accent;
#     setAccentColor(themeColor, true);
    
#     // Update mode toggle
#     updateModeToggle(themeConfigs[themeName].mode);
    
#     createBubbles();
#     updateChartColors();
# }}

# function setAccentColor(color, fromTheme = false) {{
#     currentAccentColor = color;
    
#     if (!fromTheme) {{
#         // Update color palette active state
#         document.querySelectorAll('.color-option').forEach(opt => opt.classList.remove('active'));
#         event.target.classList.add('active');
#     }}
    
#     // Update CSS custom properties
#     document.documentElement.style.setProperty('--accent', color);
    
#     // Generate darker and lighter variants
#     const rgb = hexToRgb(color);
#     const darker = adjustBrightness(color, -20);
#     const lighter = `rgba(${{rgb.r}}, ${{rgb.g}}, ${{rgb.b}}, 0.1)`;
#     const glow = `rgba(${{rgb.r}}, ${{rgb.g}}, ${{rgb.b}}, 0.3)`;
    
#     document.documentElement.style.setProperty('--accent-dark', darker);
#     document.documentElement.style.setProperty('--accent-light', lighter);
#     document.documentElement.style.setProperty('--accent-glow', glow);
    
#     // Update gradients
#     const gradient1 = `linear-gradient(135deg, ${{color}} 0%, ${{darker}} 100%)`;
#     document.documentElement.style.setProperty('--gradient-primary', gradient1);
    
#     createBubbles();
#     updateChartColors();
# }}

# function toggleDarkMode() {{
#     const currentTheme = document.body.className;
#     const currentConfig = themeConfigs[currentTheme];
    
#     if (currentConfig.mode === 'light') {{
#         // Switch to dark version
#         const darkTheme = currentTheme.replace('-light', '-dark');
#         if (themeConfigs[darkTheme]) {{
#             setTheme(darkTheme);
#         }}
#     }} else {{
#         // Switch to light version
#         const lightTheme = currentTheme.replace('-dark', '-light');
#         if (themeConfigs[lightTheme]) {{
#             setTheme(lightTheme);
#         }}
#     }}
# }}

# function updateModeToggle(mode) {{
#     const modeIcon = document.getElementById('modeIcon');
#     const modeText = document.getElementById('modeText');
    
#     if (mode === 'dark') {{
#         modeIcon.textContent = '☀️';
#         modeText.textContent = 'Light Mode';
#     }} else {{
#         modeIcon.textContent = '🌙';
#         modeText.textContent = 'Dark Mode';
#     }}
# }}

# function adjustBrightness(hex, percent) {{
#     const rgb = hexToRgb(hex);
#     const r = Math.max(0, Math.min(255, rgb.r + rgb.r * (percent / 100)));
#     const g = Math.max(0, Math.min(255, rgb.g + rgb.g * (percent / 100)));
#     const b = Math.max(0, Math.min(255, rgb.b + rgb.b * (percent / 100)));
#     return `rgb(${{Math.round(r)}}, ${{Math.round(g)}}, ${{Math.round(b)}})`;
# }}

# function hexToRgb(hex) {{
#     const result = /^#?([a-f\\d]{{2}})([a-f\\d]{{2}})([a-f\\d]{{2}})$/i.exec(hex);
#     return result ? {{
#         r: parseInt(result[1], 16),
#         g: parseInt(result[2], 16),
#         b: parseInt(result[3], 16)
#     }} : {{r: 0, g: 0, b: 0}};
# }}

# function animateCounters() {{
#     const counters = document.querySelectorAll('.animated-counter');
#     counters.forEach(counter => {{
#         const text = counter.textContent;
#         if (text.includes('₹')) {{
#             const target = parseInt(text.replace('₹', '').replace(/,/g, '')) || 0;
#             let current = 0;
#             const increment = target / 30;
#             const timer = setInterval(() => {{
#                 current += increment;
#                 if (current >= target) {{
#                     current = target;
#                     clearInterval(timer);
#                 }}
#                 counter.textContent = '₹' + Math.round(current).toLocaleString();
#             }}, 30);
#         }}
#     }});
# }}

# function updateChartColors() {{
#     const color = currentAccentColor;
#     const isLightTheme = document.documentElement.style.getPropertyValue('--mode') === 'light';
    
#     const gridColor = isLightTheme ? 'rgba(0,0,0,0.1)' : 'rgba(255,255,255,0.1)';
#     const textColor = isLightTheme ? '#1C1C1E' : '#FFFFFF';
    
#     if (chartA) {{
#         chartA.data.datasets[0].backgroundColor = generateColorPalette(color, A_LABELS.length);
#         chartA.options.scales.x.ticks.color = textColor;
#         chartA.options.scales.y.ticks.color = textColor;
#         chartA.options.plugins.legend.labels.color = textColor;
#         chartA.update();
#     }}
    
#     if (chartB) {{
#         chartB.data.datasets[0].backgroundColor = generateColorPalette(color, B_LABELS.length);
#         chartB.options.scales.x.ticks.color = textColor;
#         chartB.options.scales.y.ticks.color = textColor;
#         chartB.options.plugins.legend.labels.color = textColor;
#         chartB.update();
#     }}
# }}

# function generateColorPalette(baseColor, count) {{
#     const colors = [];
#     const base = hexToRgb(baseColor);
    
#     for (let i = 0; i < count; i++) {{
#         const factor = 0.7 + (i * 0.3 / count);
#         const r = Math.round(base.r * factor);
#         const g = Math.round(base.g * factor);
#         const b = Math.round(base.b * factor);
#         colors.push(`rgba(${{r}}, ${{g}}, ${{b}}, 0.8)`);
#     }}
#     return colors;
# }}

# function showSection(sectionName) {{
#     document.querySelectorAll('.section').forEach(section => {{
#         section.classList.remove('visible');
#     }});
#     document.getElementById(sectionName + '_section').classList.add('visible');
# }}

# function showGraph(graphId) {{
#     document.querySelectorAll('canvas').forEach(canvas => {{
#         canvas.classList.remove('visible');
#     }});
#     document.querySelectorAll('.graph-btn').forEach(btn => {{
#         btn.classList.remove('active');
#     }});
    
#     document.getElementById('chart' + graphId).classList.add('visible');
#     document.getElementById('btn' + graphId).classList.add('active');
    
#     currentGraph = graphId;
#     initChart(graphId);
# }}

# function initChart(graphId) {{
#     const ctx = document.getElementById('chart' + graphId).getContext('2d');
#     const isLightTheme = document.documentElement.style.getPropertyValue('--mode') === 'light';
    
#     const gridColor = isLightTheme ? 'rgba(0,0,0,0.1)' : 'rgba(255,255,255,0.1)';
#     const textColor = isLightTheme ? '#1C1C1E' : '#FFFFFF';
    
#     if (graphId === 'A' && !chartA) {{
#         chartA = new Chart(ctx, {{
#             type: 'doughnut',
#             data: {{
#                 labels: A_LABELS,
#                 datasets: [{{
#                     data: A_VALUES,
#                     backgroundColor: generateColorPalette(currentAccentColor, A_LABELS.length),
#                     borderColor: isLightTheme ? '#FFFFFF' : '#1C1C1E',
#                     borderWidth: 3,
#                     hoverOffset: 20,
#                 }}]
#             }},
#             options: {{
#                 responsive: true,
#                 maintainAspectRatio: false,
#                 plugins: {{
#                     legend: {{
#                         position: 'right',
#                         labels: {{
#                             color: textColor,
#                             font: {{ size: 13, weight: '600' }},
#                             padding: 25,
#                         }}
#                     }},
#                 }},
#                 cutout: '55%',
#             }}
#         }});
#     }} else if (graphId === 'B' && !chartB) {{
#         chartB = new Chart(ctx, {{
#             type: 'bar',
#             data: {{
#                 labels: B_LABELS.slice(0, 10),
#                 datasets: [{{
#                     label: 'Challan Amount',
#                     data: B_VALUES.slice(0, 10),
#                     backgroundColor: generateColorPalette(currentAccentColor, 10),
#                     borderColor: isLightTheme ? '#FFFFFF' : '#1C1C1E',
#                     borderWidth: 2,
#                     borderRadius: 8,
#                 }}]
#             }},
#             options: {{
#                 responsive: true,
#                 maintainAspectRatio: false,
#                 scales: {{
#                     x: {{
#                         ticks: {{
#                             color: textColor,
#                             font: {{ size: 12, weight: '600' }},
#                         }},
#                         grid: {{
#                             color: gridColor,
#                         }}
#                     }},
#                     y: {{
#                         ticks: {{
#                             color: textColor,
#                             font: {{ size: 12, weight: '600' }},
#                             callback: function(value) {{
#                                 return '₹' + value;
#                             }}
#                         }},
#                         grid: {{
#                             color: gridColor,
#                         }}
#                     }}
#                 }},
#             }}
#         }});
#     }}
# }}

# function applySearch() {{
#     const searchTerm = document.getElementById('searchInput').value.toLowerCase();
#     const rows = document.querySelectorAll('#databaseTable tbody tr');
    
#     rows.forEach(row => {{
#         const text = row.textContent.toLowerCase();
#         row.style.display = text.includes(searchTerm) ? '' : 'none';
#     }});
# }}

# function filterByType() {{
#     const filterValue = document.getElementById('filterSelect').value.toLowerCase();
#     const rows = document.querySelectorAll('#databaseTable tbody tr');
    
#     rows.forEach(row => {{
#         const violationType = row.cells[3]?.textContent.toLowerCase() || '';
#         row.style.display = !filterValue || violationType.includes(filterValue) ? '' : 'none';
#     }});
# }}

# function refreshData() {{
#     const refreshBtn = document.querySelector('#refreshText');
#     const originalText = refreshBtn.textContent;
#     refreshBtn.textContent = '🔄 Refreshing...';
    
#     setTimeout(() => {{
#         refreshBtn.textContent = '✅ Data Refreshed!';
#         animateCounters();
#         setTimeout(() => {{
#             refreshBtn.textContent = originalText;
#         }}, 2000);
#     }}, 1500);
# }}

# // Export functionality
# function exportData() {{
#   document.getElementById('exportModal').style.display = 'block';
# }}

# function closeModal() {{
#   document.getElementById('exportModal').style.display = 'none';
# }}

# function downloadCSV() {{
#   const headers = Object.keys(BASE_DATA[0]);
#   const csvContent = [
#     headers.join(','),
#     ...BASE_DATA.map(row => headers.map(header => `"${{row[header]}}"`).join(','))
#   ].join('\\n');
  
#   const blob = new Blob([csvContent], {{ type: 'text/csv' }});
#   const url = window.URL.createObjectURL(blob);
#   const a = document.createElement('a');
#   a.href = url;
#   a.download = 'traffic_data.csv';
#   a.click();
#   window.URL.revokeObjectURL(url);
#   closeModal();
# }}

# function downloadJSON() {{
#   const jsonContent = JSON.stringify(BASE_DATA, null, 2);
#   const blob = new Blob([jsonContent], {{ type: 'application/json' }});
#   const url = window.URL.createObjectURL(blob);
#   const a = document.createElement('a');
#   a.href = url;
#   a.download = 'traffic_data.json';
#   a.click();
#   window.URL.revokeObjectURL(url);
#   closeModal();
# }}

# function downloadPDF() {{
#   // Create a simple PDF using print functionality
#   const originalContent = document.body.innerHTML;
#   const printContent = document.getElementById('dashboard_section').innerHTML;
  
#   document.body.innerHTML = `
#     <!DOCTYPE html>
#     <html>
#     <head>
#       <title>Traffic Violation Report</title>
#       <style>
#         body {{ font-family: Arial, sans-serif; margin: 20px; }}
#         h1 {{ color: #333; text-align: center; }}
#         table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
#         th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
#         th {{ background-color: #f2f2f2; }}
#         .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
#         .stat-item {{ text-align: center; }}
#       </style>
#     </head>
#     <body>
#       <h1>Traffic Violation Report</h1>
#       <div class="stats">
#         <div class="stat-item">
#           <h3>Total Violations</h3>
#           <p>${{BASE_DATA.length}}</p>
#         </div>
#         <div class="stat-item">
#           <h3>Total Challan Amount</h3>
#           <p>₹${{BASE_DATA.reduce((sum, row) => sum + (parseInt(row.Challan) || 0), 0)}}</p>
#         </div>
#       </div>
#       ${{printContent}}
#       <p style="text-align: center; margin-top: 30px; color: #666;">
#         Generated on ${{new Date().toLocaleDateString()}}
#       </p>
#     </body>
#     </html>
#   `;
  
#   window.print();
#   document.body.innerHTML = originalContent;
#   closeModal();
# }}

# // Initialize dashboard
# document.addEventListener('DOMContentLoaded', function() {{
#     initChart('A');
#     createBubbles();
#     animateCounters();
    
#     // Close modal when clicking outside
#     window.addEventListener('click', function(event) {{
#         const modal = document.getElementById('exportModal');
#         if (event.target === modal) {{
#             closeModal();
#         }}
#     }});
# }});
# </script>
# </body>
# </html>"""

#         # ---------- WRITE FILE ----------
#         with open("dashboard.html", "w", encoding="utf-8") as f:
#             f.write(html_top)

#         print("✅ Dashboard generated successfully!")
#         webbrowser.open("dashboard.html")

#     except Exception as e:
#         print(f"❌ Error generating dashboard: {e}")

# if __name__ == "__main__":
#     generate_dashboard()


















import pandas as pd
from datetime import datetime
import webbrowser
import json
import os

def generate_dashboard():
    try:
        # ---------- LOAD DATA ----------
        df = pd.read_csv("challan_database.csv")

        if df.empty:
            print("📊 No data found — dashboard not generated.")
            return

        if "Challan" not in df.columns:
            raise ValueError("CSV must contain a 'Challan' column.")
        if "Number Plate" not in df.columns:
            raise ValueError("CSV must contain a 'Number Plate' column.")

        df["Challan"] = pd.to_numeric(df["Challan"], errors="coerce").fillna(0)

        # ---------- BASIC STATS ----------
        violator_sum = df.groupby("Number Plate")["Challan"].sum().sort_values(ascending=False)
        top_violator = violator_sum.idxmax() if not violator_sum.empty else "N/A"
        top_violator_amount = int(violator_sum.max()) if not violator_sum.empty else 0

        if "Violation Type" in df.columns and not df["Violation Type"].dropna().empty:
            most_violated_rule = df["Violation Type"].mode()[0]
            violation_counts = df["Violation Type"].value_counts()
        else:
            most_violated_rule = "N/A"
            violation_counts = pd.Series()

        total_challan = int(df["Challan"].sum())
        total_violations = len(df)
        unique_vehicles = len(df['Number Plate'].unique())
        violation_types = len(df['Violation Type'].unique()) if 'Violation Type' in df.columns else 0
        last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # ---------- GRAPH DATA ----------
        if "Violation Type" in df.columns:
            vt_counts = df["Violation Type"].fillna("Unknown").value_counts()
        else:
            vt_counts = pd.Series(dtype=int)

        graph_A_labels = json.dumps(list(vt_counts.index))
        graph_A_values = json.dumps([int(x) for x in vt_counts.values])
        graph_B_labels = json.dumps(list(violator_sum.index))
        graph_B_values = json.dumps([int(x) for x in violator_sum.values])

        # ---------- TABLES ----------
        df_html = df.to_html(index=False, table_id="databaseTable", classes="data-table", border=0)
        recent_html = df.tail(10).to_html(index=False, classes="data-table", border=0)
        base_data = json.dumps(df.fillna("").to_dict(orient="records"))

        # ---------- ALERTS ----------
        alerts = []
        if top_violator_amount > 5000:
            alerts.append(f"🚨 High Value Alert: {top_violator} has accumulated challans of ₹{top_violator_amount:,}")
        
        if total_violations > 100:
            alerts.append(f"⚠️ High Activity: {total_violations} violations recorded this period")
        
        if violator_sum.size > 1 and violator_sum.iloc[0] > violator_sum.iloc[1] * 3:
            alerts.append(f"📈 Priority Case: {top_violator} shows significantly higher violations than others")

        alert_html = "".join([f'<div class="alert-card">{alert}</div>' for alert in alerts])

        # ---------- FILTERS ----------
        filter_html = ""
        if "Violation Type" in df.columns:
            options = "".join(f"<option value='{t}'>{t}</option>" for t in df["Violation Type"].dropna().unique())
            filter_html = f"""
            <select id='filterSelect' onchange='filterTable()' class='filter'>
              <option value=''>All Violation Types</option>
              {options}
            </select>
            """

        # ---------- HTML START ----------
        html_top = f"""<!DOCTYPE html>
<html lang='en'>
<head>
<meta charset='utf-8'/>
<title>Traffic Violation Dashboard - Government Portal</title>
<meta name='viewport' content='width=device-width, initial-scale=1'/>
<script src='https://cdn.jsdelivr.net/npm/chart.js'></script>
<link href='https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap' rel='stylesheet'>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">

<style>
:root {{
  --primary: #3b82f6;
  --primary-dark: #1d4ed8;
  --primary-light: #60a5fa;
  --secondary: #94a3b8;
  --accent: #ef4444;
  --success: #10b981;
  --warning: #f59e0b;
  --bg-primary: #0f172a;
  --bg-secondary: #1e293b;
  --card-bg: #1e293b;
  --text-primary: #f1f5f9;
  --text-secondary: #cbd5e1;
  --border: #334155;
  --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.4), 0 4px 6px -2px rgba(0, 0, 0, 0.3);
}}

* {{
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}}

body {{
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
  line-height: 1.6;
  min-height: 100vh;
}}

.container {{
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100vh;
}}

/* Header */
.header {{
  background: linear-gradient(135deg, var(--primary-dark), var(--primary));
  color: white;
  padding: 30px 0;
  margin-bottom: 30px;
  border-radius: 12px;
  box-shadow: var(--shadow-lg);
  position: relative;
  overflow: hidden;
}}

.header::before {{
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 100" fill="%23ffffff" opacity="0.1"><polygon points="0,0 1000,50 1000,100 0,100"/></svg>');
  background-size: cover;
}}

.header-content {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 40px;
  position: relative;
  z-index: 2;
}}

.header h1 {{
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 8px;
}}

.header p {{
  opacity: 0.9;
  font-size: 16px;
  font-weight: 500;
}}

.last-update {{
  text-align: right;
  font-size: 14px;
  opacity: 0.9;
}}

.last-update i {{
  margin-right: 8px;
}}

/* Stats Grid */
.stats-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 30px;
}}

.stat-card {{
  background: var(--card-bg);
  padding: 30px;
  border-radius: 12px;
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}}

.stat-card::before {{
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 6px;
  height: 100%;
  background: var(--primary);
}}

.stat-card:hover {{
  transform: translateY(-5px);
  box-shadow: var(--shadow-lg);
  border-color: var(--primary-light);
}}

.stat-card.warning::before {{ background: var(--warning); }}
.stat-card.danger::before {{ background: var(--accent); }}
.stat-card.success::before {{ background: var(--success); }}

.stat-number {{
  font-size: 36px;
  font-weight: 800;
  color: var(--text-primary);
  margin-bottom: 8px;
  line-height: 1;
}}

.stat-label {{
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}}

/* Alerts */
.alert-container {{
  margin-bottom: 30px;
}}

.alert-card {{
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(245, 158, 11, 0.1));
  border-left: 4px solid var(--warning);
  padding: 20px 25px;
  border-radius: 8px;
  margin-bottom: 15px;
  color: var(--text-primary);
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: var(--shadow);
  border: 1px solid rgba(245, 158, 11, 0.3);
  transition: transform 0.2s ease;
}}

.alert-card:hover {{
  transform: translateX(5px);
}}

.alert-card.danger {{
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(239, 68, 68, 0.1));
  border-left-color: var(--accent);
  border-color: rgba(239, 68, 68, 0.3);
}}

/* Controls */
.controls {{
  display: flex;
  gap: 16px;
  margin-bottom: 25px;
  flex-wrap: wrap;
  align-items: center;
  background: var(--card-bg);
  padding: 24px;
  border-radius: 12px;
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
}}

.search-box {{
  flex: 1;
  min-width: 300px;
  padding: 14px 20px;
  border: 2px solid var(--border);
  border-radius: 8px;
  font-size: 15px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  transition: all 0.3s ease;
}}

.search-box:focus {{
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
  background: var(--bg-primary);
}}

.search-box::placeholder {{
  color: var(--text-secondary);
}}

.filter {{
  padding: 14px 20px;
  border: 2px solid var(--border);
  border-radius: 8px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 15px;
  min-width: 220px;
  transition: all 0.3s ease;
  cursor: pointer;
}}

.filter:focus {{
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}}

.filter option {{
  background: var(--card-bg);
  color: var(--text-primary);
  padding: 10px;
}}

.export-btn {{
  padding: 14px 24px;
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}}

.export-btn:hover {{
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}}

.export-btn.print {{
  background: linear-gradient(135deg, var(--success), #059669);
}}

.export-btn.print:hover {{
  background: linear-gradient(135deg, #059669, #047857);
}}

/* Tables */
.table-container {{
  background: var(--card-bg);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--shadow);
  margin-bottom: 30px;
  border: 1px solid var(--border);
  overflow-x: auto;
}}

.data-table {{
  width: 100%;
  border-collapse: collapse;
  min-width: 800px;
}}

.data-table th {{
  background: linear-gradient(135deg, var(--primary-dark), var(--primary));
  color: white;
  padding: 18px 20px;
  text-align: left;
  font-weight: 600;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 2px solid var(--border);
}}

.data-table td {{
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
  font-size: 14px;
  color: var(--text-primary);
  transition: background-color 0.2s ease;
}}

.data-table tr:last-child td {{
  border-bottom: none;
}}

.data-table tr:hover td {{
  background-color: rgba(59, 130, 246, 0.1);
}}

/* Charts Section */
.charts-section {{
  margin: 40px 0;
}}

.section-title {{
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 30px;
  display: flex;
  align-items: center;
  gap: 12px;
}}

.section-title i {{
  color: var(--primary);
}}

.charts-grid {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  margin-bottom: 40px;
}}

.chart-container {{
  background: var(--card-bg);
  padding: 30px;
  border-radius: 12px;
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
  transition: transform 0.3s ease;
  position: relative;
}}

.chart-container:hover {{
  transform: translateY(-5px);
  box-shadow: var(--shadow-lg);
}}

.chart-title {{
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 25px;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 10px;
}}

.chart-title i {{
  color: var(--primary);
  font-size: 18px;
}}

/* Navigation */
.nav-tabs {{
  display: flex;
  background: var(--card-bg);
  border-radius: 12px;
  padding: 8px;
  margin-bottom: 30px;
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
  flex-wrap: wrap;
}}

.nav-tab {{
  flex: 1;
  padding: 16px 24px;
  text-align: center;
  background: none;
  border: none;
  color: var(--text-secondary);
  font-weight: 600;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-width: 200px;
}}

.nav-tab.active {{
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  color: white;
  box-shadow: var(--shadow);
}}

.nav-tab:hover:not(.active) {{
  background: var(--bg-secondary);
  color: var(--text-primary);
}}

.tab-content {{
  display: none;
  animation: fadeInUp 0.5s ease;
}}

.tab-content.active {{
  display: block;
}}

@keyframes fadeInUp {{
  from {{ 
    opacity: 0; 
    transform: translateY(20px); 
  }}
  to {{ 
    opacity: 1; 
    transform: translateY(0); 
  }}
}}

/* Footer */
.footer {{
  text-align: center;
  padding: 40px 0;
  margin-top: 60px;
  border-top: 1px solid var(--border);
  color: var(--text-secondary);
  font-size: 14px;
  background: var(--card-bg);
  border-radius: 12px;
  box-shadow: var(--shadow);
}}

/* Modal */
.modal {{
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  z-index: 1000;
  backdrop-filter: blur(4px);
}}

.modal-content {{
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: var(--card-bg);
  padding: 40px;
  border-radius: 16px;
  box-shadow: var(--shadow-lg);
  min-width: 450px;
  border: 1px solid var(--border);
  animation: modalSlideIn 0.3s ease;
}}

@keyframes modalSlideIn {{
  from {{
    opacity: 0;
    transform: translate(-50%, -60%);
  }}
  to {{
    opacity: 1;
    transform: translate(-50%, -50%);
  }}
}}

.modal h3 {{
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 20px;
  color: var(--text-primary);
  text-align: center;
}}

.modal p {{
  color: var(--text-secondary);
  text-align: center;
  margin-bottom: 30px;
  font-size: 15px;
}}

.modal-buttons {{
  display: flex;
  gap: 15px;
  margin-top: 25px;
  flex-wrap: wrap;
  justify-content: center;
}}

/* Search Stats */
.search-stats {{
  background: var(--bg-secondary);
  padding: 12px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-top: 15px;
  border: 1px solid var(--border);
}}

/* Responsive */
@media (max-width: 1200px) {{
  .charts-grid {{
    grid-template-columns: 1fr;
  }}
}}

@media (max-width: 768px) {{
  .header-content {{
    flex-direction: column;
    text-align: center;
    gap: 20px;
    padding: 0 20px;
  }}
  
  .last-update {{
    text-align: center;
  }}
  
  .controls {{
    flex-direction: column;
    align-items: stretch;
  }}
  
  .search-box, .filter {{
    min-width: 100%;
    margin-bottom: 10px;
  }}
  
  .nav-tabs {{
    flex-direction: column;
  }}
  
  .nav-tab {{
    min-width: 100%;
  }}
  
  .modal-content {{
    min-width: 90%;
    margin: 20px;
    padding: 30px 20px;
  }}
  
  .modal-buttons {{
    flex-direction: column;
  }}
  
  .stats-grid {{
    grid-template-columns: 1fr;
  }}
}}

/* Print Styles */
@media print {{
  body {{
    background: white !important;
    color: black !important;
  }}
  
  .nav-tabs, .controls, .footer, .export-btn {{
    display: none !important;
  }}
  
  .header {{
    background: #1d4ed8 !important;
    -webkit-print-color-adjust: exact;
  }}
  
  .stat-card {{
    background: white !important;
    color: black !important;
    border: 1px solid #ddd !important;
  }}
  
  .table-container {{
    box-shadow: none !important;
    border: 1px solid #ddd !important;
  }}
}}
</style>
</head>
<body>
  <div class='container'>
    <!-- Header -->
    <div class='header'>
      <div class='header-content'>
        <div>
          <h1><i class="fas fa-traffic-light"></i> Traffic Violation Management System</h1>
          <p>Government Traffic Enforcement Dashboard</p>
        </div>
        <div class='last-update'>
          <i class="fas fa-sync-alt"></i>Last Updated: {last_update}
        </div>
      </div>
    </div>

    <!-- Alerts -->
    {alert_html}

    <!-- Stats Overview -->
    <div class='stats-grid'>
      <div class='stat-card'>
        <div class='stat-number'>{total_violations}</div>
        <div class='stat-label'>Total Violations Recorded</div>
      </div>
      <div class='stat-card success'>
        <div class='stat-number'>₹{total_challan:,}</div>
        <div class='stat-label'>Total Revenue Generated</div>
      </div>
      <div class='stat-card'>
        <div class='stat-number'>{unique_vehicles}</div>
        <div class='stat-label'>Unique Vehicles Monitored</div>
      </div>
      <div class='stat-card danger'>
        <div class='stat-number'>{top_violator}</div>
        <div class='stat-label'>Top Violator Vehicle</div>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class='nav-tabs'>
      <button class='nav-tab active' onclick="showTab('violations')">
        <i class="fas fa-list"></i>Violation Records
      </button>
      <button class='nav-tab' onclick="showTab('analytics')">
        <i class="fas fa-chart-bar"></i>Analytics & Charts
      </button>
      <button class='nav-tab' onclick="showTab('recent')">
        <i class="fas fa-clock"></i>Recent Activity
      </button>
    </div>

    <!-- Violations Tab -->
    <div id='violations' class='tab-content active'>
      <div class='controls'>
        <input type='text' id='searchInput' class='search-box' placeholder='🔍 Search by vehicle number, violation type...' oninput='applySearch()'>
        {filter_html}
        <button class='export-btn' onclick='exportData()'>
          <i class="fas fa-download"></i>Export Data
        </button>
        <button class='export-btn print' onclick='printReport()'>
          <i class="fas fa-print"></i>Print Report
        </button>
      </div>
      <div id="searchStats" class="search-stats">
        Showing {len(df)} of {len(df)} records
      </div>
      <div class='table-container'>
        {df_html}
      </div>
    </div>

    <!-- Analytics Tab -->
    <div id='analytics' class='tab-content'>
      <div class='charts-section'>
        <h2 class='section-title'><i class="fas fa-chart-pie"></i>Violation Analytics</h2>
        <div class='charts-grid'>
          <div class='chart-container'>
            <div class='chart-title'><i class="fas fa-chart-pie"></i>Violation Type Distribution</div>
            <canvas id='violationChart'></canvas>
          </div>
          <div class='chart-container'>
            <div class='chart-title'><i class="fas fa-trophy"></i>Top Violators by Challan Amount</div>
            <canvas id='violatorChart'></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Activity Tab -->
    <div id='recent' class='tab-content'>
      <h2 class='section-title'><i class="fas fa-bell"></i>Recent Violation Activity</h2>
      <div class='table-container'>
        {recent_html}
      </div>
    </div>

    <!-- Footer -->
    <div class='footer'>
      <p><strong>Traffic Violation Management System</strong> © 2024 | Official Government Portal</p>
      <p>For official use only | Data is updated in real-time</p>
    </div>
  </div>

  <!-- Export Modal -->
  <div id="exportModal" class="modal">
    <div class="modal-content">
      <h3>Export Data</h3>
      <p>Choose your preferred export format:</p>
      <div class="modal-buttons">
        <button class="export-btn" onclick="downloadCSV()"><i class="fas fa-file-csv"></i> CSV Format</button>
        <button class="export-btn" onclick="downloadJSON()"><i class="fas fa-file-code"></i> JSON Format</button>
        <button class="export-btn" onclick="downloadPDF()"><i class="fas fa-file-pdf"></i> PDF Report</button>
        <button class="export-btn" onclick="closeModal()" style="background: var(--secondary);">Cancel</button>
      </div>
    </div>
  </div>

<script>
const VIOLATION_LABELS = {graph_A_labels};
const VIOLATION_VALUES = {graph_A_values};
const VIOLATOR_LABELS = {graph_B_labels};
const VIOLATOR_VALUES = {graph_B_values};
const BASE_DATA = {base_data};

let violationChart, violatorChart;
let currentFilter = '';
let currentSearch = '';

function showTab(tabName) {{
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {{
        tab.classList.remove('active');
    }});
    
    // Remove active class from all buttons
    document.querySelectorAll('.nav-tab').forEach(button => {{
        button.classList.remove('active');
    }});
    
    // Show selected tab and activate button
    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');
    
    // Initialize charts if showing analytics tab
    if (tabName === 'analytics') {{
        setTimeout(() => {{
            initializeCharts();
        }}, 100);
    }}
}}

function applySearch() {{
    currentSearch = document.getElementById('searchInput').value.toLowerCase();
    filterTable();
}}

function filterByType() {{
    currentFilter = document.getElementById('filterSelect').value.toLowerCase();
    filterTable();
}}

function filterTable() {{
    const rows = document.querySelectorAll('#databaseTable tbody tr');
    let visibleCount = 0;
    
    rows.forEach(row => {{
        const rowText = row.textContent.toLowerCase();
        const violationType = row.cells[3]?.textContent.toLowerCase() || '';
        
        const matchesSearch = !currentSearch || rowText.includes(currentSearch);
        const matchesFilter = !currentFilter || violationType.includes(currentFilter);
        
        const isVisible = matchesSearch && matchesFilter;
        row.style.display = isVisible ? '' : 'none';
        if (isVisible) visibleCount++;
    }});
    
    updateSearchStats(visibleCount);
}}

function updateSearchStats(count) {{
    const statsElement = document.getElementById('searchStats');
    if (statsElement) {{
        statsElement.textContent = `Showing ${{count}} of ${{BASE_DATA.length}} records`;
    }}
}}

function initializeCharts() {{
    // Destroy existing charts if they exist
    if (violationChart) {{
        violationChart.destroy();
    }}
    if (violatorChart) {{
        violatorChart.destroy();
    }}
    
    // Violation Type Chart (Doughnut)
    const violationCtx = document.getElementById('violationChart').getContext('2d');
    violationChart = new Chart(violationCtx, {{
        type: 'doughnut',
        data: {{
            labels: VIOLATION_LABELS,
            datasets: [{{
                data: VIOLATION_VALUES,
                backgroundColor: [
                    '#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6',
                    '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1'
                ],
                borderWidth: 3,
                borderColor: '#1e293b',
                hoverOffset: 20
            }}]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: true,
            plugins: {{
                legend: {{
                    position: 'right',
                    labels: {{
                        padding: 20,
                        usePointStyle: true,
                        font: {{
                            size: 12,
                            weight: '600'
                        }},
                        color: '#cbd5e1'
                    }}
                }},
                tooltip: {{
                    backgroundColor: '#1e293b',
                    titleColor: '#f1f5f9',
                    bodyColor: '#cbd5e1',
                    borderColor: '#334155',
                    borderWidth: 1,
                    callbacks: {{
                        label: function(context) {{
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${{label}}: ${{value}} (${{percentage}}%)`;
                        }}
                    }}
                }}
            }},
            cutout: '60%'
        }}
    }});
    
    // Violator Chart (Bar)
    const violatorCtx = document.getElementById('violatorChart').getContext('2d');
    const topViolators = VIOLATOR_LABELS.slice(0, 8);
    const topValues = VIOLATOR_VALUES.slice(0, 8);
    
    violatorChart = new Chart(violatorCtx, {{
        type: 'bar',
        data: {{
            labels: topViolators,
            datasets: [{{
                label: 'Challan Amount (₹)',
                data: topValues,
                backgroundColor: '#3b82f6',
                borderColor: '#1d4ed8',
                borderWidth: 2,
                borderRadius: 6,
                borderSkipped: false,
            }}]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: true,
            scales: {{
                y: {{
                    beginAtZero: true,
                    ticks: {{
                        callback: function(value) {{
                            return '₹' + value.toLocaleString();
                        }},
                        font: {{
                            weight: '600'
                        }},
                        color: '#cbd5e1'
                    }},
                    grid: {{
                        color: '#334155'
                    }}
                }},
                x: {{
                    ticks: {{
                        font: {{
                            weight: '600'
                        }},
                        color: '#cbd5e1'
                    }},
                    grid: {{
                        display: false
                    }}
                }}
            }},
            plugins: {{
                legend: {{
                    display: false
                }},
                tooltip: {{
                    backgroundColor: '#1e293b',
                    titleColor: '#f1f5f9',
                    bodyColor: '#cbd5e1',
                    borderColor: '#334155',
                    borderWidth: 1,
                    callbacks: {{
                        label: function(context) {{
                            return `Challan Amount: ₹${{context.parsed.y.toLocaleString()}}`;
                        }}
                    }}
                }}
            }}
        }}
    }});
}}

// Export functionality
function exportData() {{
    document.getElementById('exportModal').style.display = 'block';
}}

function closeModal() {{
    document.getElementById('exportModal').style.display = 'none';
}}

function downloadCSV() {{
    try {{
        const headers = Object.keys(BASE_DATA[0]);
        const csvContent = [
            headers.join(','),
            ...BASE_DATA.map(row => headers.map(header => 
                `"${{String(row[header] || '').replace(/"/g, '""')}}"`
            ).join(','))
        ].join('\\n');
        
        const blob = new Blob(['\\ufeff' + csvContent], {{ type: 'text/csv;charset=utf-8;' }});
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'traffic_violation_data.csv';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        closeModal();
    }} catch (error) {{
        console.error('Error generating CSV:', error);
        alert('Error generating CSV file. Please try again.');
    }}
}}

function downloadJSON() {{
    try {{
        const jsonContent = JSON.stringify(BASE_DATA, null, 2);
        const blob = new Blob([jsonContent], {{ type: 'application/json' }});
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'traffic_violation_data.json';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        closeModal();
    }} catch (error) {{
        console.error('Error generating JSON:', error);
        alert('Error generating JSON file. Please try again.');
    }}
}}

function downloadPDF() {{
    // Simple PDF generation using browser print
    const originalTitle = document.title;
    document.title = 'Traffic Violation Report - ' + new Date().toLocaleDateString();
    window.print();
    document.title = originalTitle;
    closeModal();
}}

function printReport() {{
    const originalTitle = document.title;
    document.title = 'Traffic Violation Report - ' + new Date().toLocaleDateString();
    window.print();
    document.title = originalTitle;
}}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {{
    // Initialize search functionality
    updateSearchStats(BASE_DATA.length);
    
    // Initialize charts if on analytics tab
    if (document.getElementById('analytics').classList.contains('active')) {{
        initializeCharts();
    }}
    
    // Set up filter event listener
    const filterSelect = document.getElementById('filterSelect');
    if (filterSelect) {{
        filterSelect.addEventListener('change', filterByType);
    }}
}});

// Close modal when clicking outside
window.addEventListener('click', function(event) {{
    const modal = document.getElementById('exportModal');
    if (event.target === modal) {{
        closeModal();
    }}
}});

// Handle escape key to close modal
document.addEventListener('keydown', function(event) {{
    if (event.key === 'Escape') {{
        closeModal();
    }}
}});
</script>
</body>
</html>"""

        # ---------- WRITE FILE ----------
        with open("dashboard.html", "w", encoding="utf-8") as f:
            f.write(html_top)

        print("✅ Dark theme dashboard generated successfully!")
        webbrowser.open("dashboard.html")

    except Exception as e:
        print(f"❌ Error generating dashboard: {e}")

if __name__ == "__main__":
    generate_dashboard()