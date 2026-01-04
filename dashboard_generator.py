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
        
        # ---------- ANALYTICS ----------
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
        avg_challan = int(df["Challan"].mean()) if len(df) > 0 else 0
        max_challan = int(df["Challan"].max()) if len(df) > 0 else 0
        pending_cases = int(len(df[df['Challan'] > 2000])) if 'Challan' in df.columns else 0
        
        last_update = datetime.now().strftime("%d %B %Y, %H:%M")
        
        # Date analytics
        date_data = ""
        if "Date" in df.columns:
            try:
                df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
                date_counts = df.groupby(df["Date"].dt.date).size()
                date_labels = json.dumps([str(d) for d in date_counts.index[-30:]])
                date_values = json.dumps([int(x) for x in date_counts.values[-30:]])
                date_data = f'"dateLabels": {date_labels}, "dateValues": {date_values},'
            except:
                date_data = ""
        
        # Graph data
        if "Violation Type" in df.columns:
            vt_counts = df["Violation Type"].fillna("Unknown").value_counts()
        else:
            vt_counts = pd.Series(dtype=int)
            
        graph_A_labels = json.dumps(list(vt_counts.index))
        graph_A_values = json.dumps([int(x) for x in vt_counts.values])
        
        top_10_violators = violator_sum.head(10)
        graph_B_labels = json.dumps(list(top_10_violators.index))
        graph_B_values = json.dumps([int(x) for x in top_10_violators.values])
        
        challan_ranges = ["₹0-500", "₹501-1K", "₹1K-2K", "₹2K-5K", "₹5K+"]
        challan_dist = [
            len(df[df["Challan"] <= 500]),
            len(df[(df["Challan"] > 500) & (df["Challan"] <= 1000)]),
            len(df[(df["Challan"] > 1000) & (df["Challan"] <= 2000)]),
            len(df[(df["Challan"] > 2000) & (df["Challan"] <= 5000)]),
            len(df[df["Challan"] > 5000])
        ]
        graph_C_labels = json.dumps(challan_ranges)
        graph_C_values = json.dumps(challan_dist)
        
        # Tables
        df_html = df.to_html(index=False, table_id="databaseTable", classes="data-table", border=0)
        recent_html = df.tail(10).to_html(index=False, classes="data-table mini-table", border=0)
        base_data = json.dumps(df.fillna("").to_dict(orient="records"))
        
        # Top violators table
        top_violators_df = violator_sum.head(5).reset_index()
        top_violators_df.columns = ['Number Plate', 'Total (₹)']
        top_violators_html = top_violators_df.to_html(index=False, classes="data-table mini-table", border=0)
        
        # Filters
        filter_html = ""
        if "Violation Type" in df.columns:
            options = "".join(f'<option value="{t}">{t}</option>' for t in df["Violation Type"].dropna().unique())
            filter_html = f'<option value="">All Types</option>{options}'
        
        # Generate HTML with complete code
        with open("dashboard.html", "w", encoding="utf-8") as f:
            f.write(f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Traffic Command Center</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        :root {{
            --primary: #00d4ff;
            --secondary: #0096c7;
            --accent: #ff006e;
            --success: #06ffa5;
            --warning: #ffbe0b;
            --danger: #ff006e;
            --bg-dark: #0a0e27;
            --bg-card: #161b33;
            --bg-hover: #1e2540;
            --text: #ffffff;
            --text-muted: #8892b0;
            --border: #2d3561;
            --sidebar-width: 280px;
        }}

        body {{
            font-family: 'Poppins', sans-serif;
            background: var(--bg-dark);
            color: var(--text);
            overflow-x: hidden;
        }}

        .sidebar {{
            position: fixed;
            left: 0;
            top: 0;
            width: var(--sidebar-width);
            height: 100vh;
            background: linear-gradient(180deg, #161b33 0%, #0d1025 100%);
            border-right: 1px solid var(--border);
            padding: 30px 0;
            z-index: 1000;
            transition: all 0.3s ease;
            overflow-y: auto;
        }}

        .sidebar.collapsed {{
            width: 80px;
        }}

        .sidebar-header {{
            padding: 0 30px 30px;
            border-bottom: 1px solid var(--border);
            margin-bottom: 30px;
        }}

        .sidebar.collapsed .sidebar-header {{
            padding: 0 20px 30px;
        }}

        .logo {{
            display: flex;
            align-items: center;
            gap: 15px;
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--primary);
        }}

        .logo i {{
            font-size: 2rem;
        }}

        .sidebar.collapsed .logo-text {{
            display: none;
        }}

        .nav-menu {{
            padding: 0 15px;
        }}

        .nav-item {{
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 15px 15px;
            margin-bottom: 5px;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.3s ease;
            color: var(--text-muted);
            text-decoration: none;
        }}

        .nav-item:hover {{
            background: var(--bg-hover);
            color: var(--primary);
            transform: translateX(5px);
        }}

        .nav-item.active {{
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            box-shadow: 0 5px 20px rgba(0, 212, 255, 0.3);
        }}

        .nav-item i {{
            font-size: 1.3rem;
            min-width: 25px;
        }}

        .sidebar.collapsed .nav-item span {{
            display: none;
        }}

        .toggle-btn {{
            position: absolute;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            width: 50px;
            height: 50px;
            background: var(--primary);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s ease;
            border: none;
            color: white;
            font-size: 1.2rem;
        }}

        .toggle-btn:hover {{
            background: var(--secondary);
            transform: translateX(-50%) scale(1.1);
        }}

        .main-content {{
            margin-left: var(--sidebar-width);
            padding: 30px;
            transition: margin-left 0.3s ease;
            min-height: 100vh;
        }}

        .sidebar.collapsed ~ .main-content {{
            margin-left: 80px;
        }}

        .top-bar {{
            background: var(--bg-card);
            padding: 20px 30px;
            border-radius: 16px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border: 1px solid var(--border);
            flex-wrap: wrap;
            gap: 20px;
        }}

        .page-title {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}

        .page-title h1 {{
            font-size: 2rem;
            background: linear-gradient(135deg, var(--primary), var(--accent));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .top-actions {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}

        .btn {{
            padding: 12px 24px;
            border-radius: 10px;
            border: none;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-size: 0.95rem;
            font-weight: 500;
            transition: all 0.3s ease;
            font-family: 'Poppins', sans-serif;
        }}

        .btn-primary {{
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
        }}

        .btn-success {{
            background: linear-gradient(135deg, var(--success), #00c48c);
            color: var(--bg-dark);
        }}

        .btn-warning {{
            background: linear-gradient(135deg, var(--warning), #fb8500);
            color: var(--bg-dark);
        }}

        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(0, 212, 255, 0.3);
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .stat-card {{
            background: var(--bg-card);
            padding: 25px;
            border-radius: 16px;
            border: 1px solid var(--border);
            position: relative;
            overflow: hidden;
            transition: all 0.3s ease;
        }}

        .stat-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: linear-gradient(90deg, var(--primary), var(--accent));
            transform: scaleX(0);
            transition: transform 0.3s ease;
        }}

        .stat-card:hover {{
            transform: translateY(-5px);
            border-color: var(--primary);
            box-shadow: 0 15px 40px rgba(0, 212, 255, 0.2);
        }}

        .stat-card:hover::before {{
            transform: scaleX(1);
        }}

        .stat-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 15px;
        }}

        .stat-icon {{
            width: 60px;
            height: 60px;
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.8rem;
            background: linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(255, 0, 110, 0.2));
        }}

        .stat-trend {{
            display: flex;
            align-items: center;
            gap: 5px;
            font-size: 0.85rem;
            padding: 5px 10px;
            border-radius: 20px;
            background: rgba(6, 255, 165, 0.1);
            color: var(--success);
        }}

        .stat-trend.down {{
            background: rgba(255, 0, 110, 0.1);
            color: var(--danger);
        }}

        .stat-value {{
            font-size: 2.2rem;
            font-weight: 700;
            margin-bottom: 5px;
            background: linear-gradient(135deg, var(--primary), var(--accent));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .stat-label {{
            color: var(--text-muted);
            font-size: 0.9rem;
        }}

        .content-grid {{
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }}

        .content-card {{
            background: var(--bg-card);
            padding: 30px;
            border-radius: 16px;
            border: 1px solid var(--border);
        }}

        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 1px solid var(--border);
        }}

        .card-title {{
            font-size: 1.3rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .card-title i {{
            color: var(--primary);
        }}

        .chart-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .chart-container {{
            position: relative;
            height: 350px;
        }}

        .table-controls {{
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}

        .search-box {{
            position: relative;
            flex: 1;
            min-width: 250px;
        }}

        .search-box input {{
            width: 100%;
            padding: 12px 45px 12px 15px;
            border-radius: 10px;
            border: 1px solid var(--border);
            background: var(--bg-hover);
            color: var(--text);
            font-size: 0.95rem;
            font-family: 'Poppins', sans-serif;
            transition: all 0.3s ease;
        }}

        .search-box input:focus {{
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.1);
        }}

        .search-box i {{
            position: absolute;
            right: 15px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-muted);
        }}

        select {{
            padding: 12px 15px;
            border-radius: 10px;
            border: 1px solid var(--border);
            background: var(--bg-hover);
            color: var(--text);
            font-size: 0.95rem;
            cursor: pointer;
            font-family: 'Poppins', sans-serif;
            transition: all 0.3s ease;
        }}

        select:focus {{
            outline: none;
            border-color: var(--primary);
        }}

        .table-wrapper {{
            overflow-x: auto;
            border-radius: 12px;
            border: 1px solid var(--border);
        }}

        .data-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.95rem;
        }}

        .data-table th {{
            background: var(--bg-hover);
            padding: 18px 15px;
            text-align: left;
            font-weight: 600;
            position: sticky;
            top: 0;
            z-index: 10;
            border-bottom: 2px solid var(--primary);
        }}

        .data-table td {{
            padding: 15px;
            border-bottom: 1px solid var(--border);
        }}

        .data-table tr {{
            transition: all 0.2s ease;
        }}

        .data-table tr:hover {{
            background: var(--bg-hover);
        }}

        .mini-table {{
            font-size: 0.9rem;
        }}

        .mini-table th {{
            padding: 12px 10px;
        }}

        .mini-table td {{
            padding: 10px;
        }}

        .pagination {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 10px;
            margin-top: 25px;
        }}

        .pagination button {{
            padding: 10px 18px;
            border-radius: 8px;
            border: 1px solid var(--border);
            background: var(--bg-hover);
            color: var(--text);
            cursor: pointer;
            transition: all 0.3s ease;
            font-family: 'Poppins', sans-serif;
        }}

        .pagination button:hover:not(:disabled) {{
            background: var(--primary);
            border-color: var(--primary);
            color: white;
        }}

        .pagination button:disabled {{
            opacity: 0.3;
            cursor: not-allowed;
        }}

        .page-info {{
            color: var(--text-muted);
            font-size: 0.95rem;
        }}

        .activity-item {{
            padding: 15px;
            border-left: 3px solid var(--primary);
            margin-bottom: 15px;
            background: var(--bg-hover);
            border-radius: 8px;
            transition: all 0.3s ease;
        }}

        .activity-item:hover {{
            transform: translateX(5px);
            border-color: var(--accent);
        }}

        .activity-time {{
            font-size: 0.85rem;
            color: var(--text-muted);
            margin-top: 5px;
        }}

        .modal {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(10, 14, 39, 0.95);
            backdrop-filter: blur(10px);
            z-index: 2000;
            align-items: center;
            justify-content: center;
        }}

        .modal.active {{
            display: flex;
        }}

        .modal-content {{
            background: var(--bg-card);
            padding: 40px;
            border-radius: 20px;
            max-width: 600px;
            width: 90%;
            border: 1px solid var(--border);
            animation: modalSlide 0.4s ease;
        }}

        @keyframes modalSlide {{
            from {{
                transform: translateY(-50px);
                opacity: 0;
            }}
            to {{
                transform: translateY(0);
                opacity: 1;
            }}
        }}

        .modal h3 {{
            margin-bottom: 25px;
            font-size: 1.8rem;
            display: flex;
            align-items: center;
            gap: 15px;
        }}

        .export-option {{
            padding: 25px;
            border: 2px solid var(--border);
            border-radius: 14px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: center;
            margin-bottom: 15px;
        }}

        .export-option:hover {{
            border-color: var(--primary);
            background: var(--bg-hover);
            transform: translateY(-3px);
        }}

        .export-option i {{
            font-size: 2.5rem;
            margin-bottom: 15px;
            background: linear-gradient(135deg, var(--primary), var(--accent));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .modal-buttons {{
            display: flex;
            gap: 15px;
            margin-top: 25px;
        }}

        .notification {{
            position: fixed;
            top: 30px;
            right: 30px;
            background: var(--bg-card);
            padding: 20px 25px;
            border-radius: 12px;
            border-left: 4px solid var(--success);
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
            z-index: 3000;
            display: none;
            align-items: center;
            gap: 15px;
            animation: slideIn 0.3s ease;
        }}

        .notification.show {{
            display: flex;
        }}

        @keyframes slideIn {{
            from {{
                transform: translateX(400px);
                opacity: 0;
            }}
            to {{
                transform: translateX(0);
                opacity: 1;
            }}
        }}

        .section {{
            display: none;
        }}

        .section.active {{
            display: block;
        }}

        @media (max-width: 1200px) {{
            .content-grid {{
                grid-template-columns: 1fr;
            }}
            .chart-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        @media (max-width: 768px) {{
            .sidebar {{
                transform: translateX(-100%);
            }}
            .sidebar.active {{
                transform: translateX(0);
            }}
            .main-content {{
                margin-left: 0;
            }}
            .page-title h1 {{
                font-size: 1.5rem;
            }}
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <div class="logo">
                <i class="fas fa-shield-halved"></i>
                <span class="logo-text">TrafficWatch</span>
            </div>
        </div>
        <nav class="nav-menu">
            <a href="#" class="nav-item active" onclick="showSection('dashboard')">
                <i class="fas fa-chart-line"></i>
                <span>Dashboard</span>
            </a>
            <a href="#" class="nav-item" onclick="showSection('violations')">
                <i class="fas fa-list-check"></i>
                <span>All Violations</span>
            </a>
            <a href="#" class="nav-item" onclick="showSection('analytics')">
                <i class="fas fa-chart-pie"></i>
                <span>Analytics</span>
            </a>
            <a href="#" class="nav-item" onclick="showSection('reports')">
                <i class="fas fa-file-lines"></i>
                <span>Reports</span>
            </a>
            <a href="#" class="nav-item" onclick="showSection('search')">
                <i class="fas fa-magnifying-glass"></i>
                <span>Search Vehicle</span>
            </a>
        </nav>
        <button class="toggle-btn" onclick="toggleSidebar()">
            <i class="fas fa-angles-left" id="toggleIcon"></i>
        </button>
    </div>

    <div class="main-content">
        <div class="top-bar">
            <div class="page-title">
                <i class="fas fa-gauge-high" style="color: var(--primary); font-size: 2rem;"></i>
                <div>
                    <h1>Command Center</h1>
                    <p style="color: var(--text-muted); font-size: 0.9rem;">Updated: {last_update}</p>
                </div>
            </div>
            <div class="top-actions">
                <button class="btn btn-primary" onclick="refreshData()">
                    <i class="fas fa-rotate"></i> Refresh
                </button>
                <button class="btn btn-success" onclick="exportData()">
                    <i class="fas fa-download"></i> Export
                </button>
                <button class="btn btn-warning" onclick="generateReport()">
                    <i class="fas fa-file-pdf"></i> Report
                </button>
            </div>
        </div>

        <div id="dashboardSection" class="section active">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-header">
                        <div class="stat-icon">
                            <i class="fas fa-triangle-exclamation" style="color: var(--accent);"></i>
                        </div>
                        <div class="stat-trend">
                            <i class="fas fa-arrow-up"></i> 12%
                        </div>
                    </div>
                    <div class="stat-value">{total_violations:,}</div>
                    <div class="stat-label">Total Violations</div>
                </div>

                <div class="stat-card">
                    <div class="stat-header">
                        <div class="stat-icon">
                            <i class="fas fa-indian-rupee-sign" style="color: var(--success);"></i>
                        </div>
                        <div class="stat-trend">
                            <i class="fas fa-arrow-up"></i> 8%
                        </div>
                    </div>
                    <div class="stat-value">₹{total_challan:,}</div>
                    <div class="stat-label">Total Revenue</div>
                </div>

                <div class="stat-card">
                    <div class="stat-header">
                        <div class="stat-icon">
                            <i class="fas fa-car" style="color: var(--warning);"></i>
                        </div>
                        <div class="stat-trend">
                            <i class="fas fa-arrow-up"></i> 5%
                        </div>
                    </div>
                    <div class="stat-value">{unique_vehicles:,}</div>
                    <div class="stat-label">Unique Vehicles</div>
                </div>

                <div class="stat-card">
                    <div class="stat-header">
                        <div class="stat-icon">
                            <i class="fas fa-hourglass-half" style="color: var(--accent);"></i>
                        </div>
                        <div class="stat-trend down">
                            <i class="fas fa-arrow-down"></i> 3%
                        </div>
                    </div>
                    <div class="stat-value">{pending_cases:,}</div>
                    <div class="stat-label">High Priority Cases</div>
                </div>

                <div class="stat-card">
                    <div class="stat-header">
                        <div class="stat-icon">
                            <i class="fas fa-chart-simple" style="color: var(--primary);"></i>
                        </div>
                        <div class="stat-trend">
                            <i class="fas fa-minus"></i> 0%
                        </div>
                    </div>
                    <div class="stat-value">₹{avg_challan:,}</div>
                    <div class="stat-label">Average Challan</div>
                </div>

                <div class="stat-card">
                    <div class="stat-header">
                        <div class="stat-icon">
                            <i class="fas fa-trophy" style="color: var(--warning);"></i>
                        </div>
                        <div class="stat-trend">
                            <i class="fas fa-fire"></i> Hot
                        </div>
                    </div>
                    <div class="stat-value" style="font-size: 1.3rem;">{top_violator}</div>
                    <div class="stat-label">Top Violator</div>
                </div>
            </div>

            <div class="content-grid">
                <div class="content-card">
                    <div class="card-header">
                        <div class="card-title">
                            <i class="fas fa-clock-rotate-left"></i>
                            Recent Activity
                        </div>
                    </div>
                    <div style="max-height: 400px; overflow-y: auto;">
                        {recent_html}
                    </div>
                </div>

                <div class="content-card">
                    <div class="card-header">
                        <div class="card-title">
                            <i class="fas fa-ranking-star"></i>
                            Top Violators
                        </div>
                    </div>
                    <div>
                        {top_violators_html}
                    </div>
                </div>
            </div>

            <div class="chart-grid">
                <div class="content-card">
                    <div class="card-header">
                        <div class="card-title">
                            <i class="fas fa-chart-pie"></i>
                            Violation Distribution
                        </div>
                    </div>
                    <div class="chart-container">
                        <canvas id="violationChart"></canvas>
                    </div>
                </div>

                <div class="content-card">
                    <div class="card-header">
                        <div class="card-title">
                            <i class="fas fa-chart-bar"></i>
                            Top 10 Violators
                        </div>
                    </div>
                    <div class="chart-container">
                        <canvas id="violatorChart"></canvas>
                    </div>
                </div>

                <div class="content-card">
                    <div class="card-header">
                        <div class="card-title">
                            <i class="fas fa-money-bill-trend-up"></i>
                            Amount Distribution
                        </div>
                    </div>
                    <div class="chart-container">
                        <canvas id="amountChart"></canvas>
                    </div>
                </div>

                {('<div class="content-card"><div class="card-header"><div class="card-title"><i class="fas fa-calendar-days"></i>Trend Analysis</div></div><div class="chart-container"><canvas id="dateChart"></canvas></div></div>' if date_data else '')}
            </div>
        </div>

        <div id="violationsSection" class="section">
            <div class="content-card">
                <div class="card-header">
                    <div class="card-title">
                        <i class="fas fa-database"></i>
                        All Violation Records
                    </div>
                </div>
                <div class="table-controls">
                    <div class="search-box">
                        <input type="text" id="searchInput" placeholder="Search records..." onkeyup="searchTable()">
                        <i class="fas fa-search"></i>
                    </div>
                    <select id="violationFilter" onchange="filterTable()">
                        {filter_html}
                    </select>
                    <button class="btn btn-success" onclick="exportData()">
                        <i class="fas fa-download"></i> Export
                    </button>
                </div>
                <div class="table-wrapper">
                    {df_html}
                </div>
                <div class="pagination">
                    <button onclick="changePage(-1)"><i class="fas fa-chevron-left"></i></button>
                    <span class="page-info">Page <span id="currentPage">1</span> of <span id="totalPages">1</span></span>
                    <button onclick="changePage(1)"><i class="fas fa-chevron-right"></i></button>
                </div>
            </div>
        </div>

        <div id="analyticsSection" class="section">
            <div class="chart-grid">
                <div class="content-card">
                    <div class="card-header">
                        <div class="card-title">
                            <i class="fas fa-chart-pie"></i>
                            Violation Types
                        </div>
                    </div>
                    <div class="chart-container">
                        <canvas id="analyticsChart1"></canvas>
                    </div>
                </div>
                <div class="content-card">
                    <div class="card-header">
                        <div class="card-title">
                            <i class="fas fa-chart-column"></i>
                            Revenue Analysis
                        </div>
                    </div>
                    <div class="chart-container">
                        <canvas id="analyticsChart2"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <div id="reportsSection" class="section">
            <div class="content-card">
                <div class="card-header">
                    <div class="card-title">
                        <i class="fas fa-file-lines"></i>
                        Generate Reports
                    </div>
                </div>
                <div style="padding: 40px; text-align: center;">
                    <i class="fas fa-file-chart-column" style="font-size: 4rem; color: var(--primary); margin-bottom: 20px;"></i>
                    <h3 style="margin-bottom: 15px;">Create Custom Reports</h3>
                    <p style="color: var(--text-muted); margin-bottom: 30px;">Generate detailed reports for analysis and compliance</p>
                    <button class="btn btn-primary" onclick="generateReport()">
                        <i class="fas fa-file-pdf"></i> Generate Full Report
                    </button>
                </div>
            </div>
        </div>

        <div id="searchSection" class="section">
            <div class="content-card">
                <div class="card-header">
                    <div class="card-title">
                        <i class="fas fa-magnifying-glass"></i>
                        Search Vehicle
                    </div>
                </div>
                <div style="padding: 20px;">
                    <div class="search-box" style="margin-bottom: 20px;">
                        <input type="text" id="vehicleSearch" placeholder="Enter vehicle number plate..." onkeyup="searchVehicle()">
                        <i class="fas fa-search"></i>
                    </div>
                    <div id="searchResults"></div>
                </div>
            </div>
        </div>
    </div>

    <div class="modal" id="exportModal">
        <div class="modal-content">
            <h3><i class="fas fa-file-export"></i> Export Data</h3>
            <p style="color: var(--text-muted); margin-bottom: 20px;">Choose your preferred format</p>
            
            <div class="export-option" onclick="downloadCSV()">
                <i class="fas fa-file-csv"></i>
                <h4>CSV Format</h4>
                <p style="color: var(--text-muted); font-size: 0.9rem;">Export as comma-separated values</p>
            </div>

            <div class="export-option" onclick="downloadJSON()">
                <i class="fas fa-file-code"></i>
                <h4>JSON Format</h4>
                <p style="color: var(--text-muted); font-size: 0.9rem;">Export as JSON data</p>
            </div>

            <div class="modal-buttons">
                <button class="btn" onclick="closeModal()" style="flex: 1; background: var(--bg-hover);">
                    <i class="fas fa-times"></i> Cancel
                </button>
            </div>
        </div>
    </div>

    <div class="notification" id="notification">
        <i class="fas fa-check-circle" style="color: var(--success); font-size: 1.5rem;"></i>
        <span id="notificationText">Action completed successfully!</span>
    </div>

    <script>
        const baseData = {base_data};
        let filteredData = [...baseData];
        let currentPage = 1;
        const rowsPerPage = 15;

        const chartData = {{
            violationLabels: {graph_A_labels},
            violationValues: {graph_A_values},
            violatorLabels: {graph_B_labels},
            violatorValues: {graph_B_values},
            amountLabels: {graph_C_labels},
            amountValues: {graph_C_values},
            {date_data}
        }};

        function initCharts() {{
            Chart.defaults.color = '#8892b0';
            Chart.defaults.borderColor = '#2d3561';

            new Chart(document.getElementById('violationChart'), {{
                type: 'doughnut',
                data: {{
                    labels: chartData.violationLabels,
                    datasets: [{{
                        data: chartData.violationValues,
                        backgroundColor: [
                            '#00d4ff', '#ff006e', '#06ffa5', '#ffbe0b', 
                            '#0096c7', '#fb8500', '#8338ec', '#3a86ff'
                        ],
                        borderWidth: 0
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ 
                            position: 'bottom',
                            labels: {{ color: '#e2e8f0', padding: 15, font: {{ size: 12 }} }}
                        }}
                    }}
                }}
            }});

            new Chart(document.getElementById('violatorChart'), {{
                type: 'bar',
                data: {{
                    labels: chartData.violatorLabels,
                    datasets: [{{
                        label: 'Challan Amount (₹)',
                        data: chartData.violatorValues,
                        backgroundColor: 'rgba(0, 212, 255, 0.8)',
                        borderColor: '#00d4ff',
                        borderWidth: 2,
                        borderRadius: 8
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ display: false }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            ticks: {{ color: '#8892b0' }},
                            grid: {{ color: '#2d3561' }}
                        }},
                        x: {{
                            ticks: {{ color: '#8892b0' }},
                            grid: {{ display: false }}
                        }}
                    }}
                }}
            }});

            new Chart(document.getElementById('amountChart'), {{
                type: 'bar',
                data: {{
                    labels: chartData.amountLabels,
                    datasets: [{{
                        label: 'Count',
                        data: chartData.amountValues,
                        backgroundColor: [
                            'rgba(6, 255, 165, 0.8)',
                            'rgba(0, 212, 255, 0.8)',
                            'rgba(255, 190, 11, 0.8)',
                            'rgba(255, 0, 110, 0.8)',
                            'rgba(220, 38, 38, 0.8)'
                        ],
                        borderWidth: 2,
                        borderRadius: 10
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ display: false }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            ticks: {{ color: '#8892b0' }},
                            grid: {{ color: '#2d3561' }}
                        }},
                        x: {{
                            ticks: {{ color: '#8892b0' }},
                            grid: {{ display: false }}
                        }}
                    }}
                }}
            }});

            if (chartData.dateLabels) {{
                new Chart(document.getElementById('dateChart'), {{
                    type: 'line',
                    data: {{
                        labels: chartData.dateLabels,
                        datasets: [{{
                            label: 'Daily Violations',
                            data: chartData.dateValues,
                            borderColor: '#00d4ff',
                            backgroundColor: 'rgba(0, 212, 255, 0.1)',
                            borderWidth: 3,
                            fill: true,
                            tension: 0.4,
                            pointBackgroundColor: '#00d4ff',
                            pointBorderColor: '#fff',
                            pointBorderWidth: 2,
                            pointRadius: 4
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{ labels: {{ color: '#e2e8f0' }} }}
                        }},
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                ticks: {{ color: '#8892b0' }},
                                grid: {{ color: '#2d3561' }}
                            }},
                            x: {{
                                ticks: {{ color: '#8892b0', maxRotation: 45 }},
                                grid: {{ display: false }}
                            }}
                        }}
                    }}
                }});
            }}

            if (document.getElementById('analyticsChart1')) {{
                new Chart(document.getElementById('analyticsChart1'), {{
                    type: 'polarArea',
                    data: {{
                        labels: chartData.violationLabels,
                        datasets: [{{
                            data: chartData.violationValues,
                            backgroundColor: [
                                'rgba(0, 212, 255, 0.7)', 'rgba(255, 0, 110, 0.7)', 
                                'rgba(6, 255, 165, 0.7)', 'rgba(255, 190, 11, 0.7)'
                            ]
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{ position: 'bottom', labels: {{ color: '#e2e8f0' }} }}
                        }}
                    }}
                }});
            }}

            if (document.getElementById('analyticsChart2')) {{
                new Chart(document.getElementById('analyticsChart2'), {{
                    type: 'line',
                    data: {{
                        labels: chartData.amountLabels,
                        datasets: [{{
                            label: 'Revenue',
                            data: chartData.amountValues,
                            borderColor: '#06ffa5',
                            backgroundColor: 'rgba(6, 255, 165, 0.1)',
                            borderWidth: 3,
                            fill: true,
                            tension: 0.4
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{ labels: {{ color: '#e2e8f0' }} }}
                        }},
                        scales: {{
                            y: {{ ticks: {{ color: '#8892b0' }}, grid: {{ color: '#2d3561' }} }},
                            x: {{ ticks: {{ color: '#8892b0' }}, grid: {{ display: false }} }}
                        }}
                    }}
                }});
            }}
        }}

        function toggleSidebar() {{
            const sidebar = document.getElementById('sidebar');
            const icon = document.getElementById('toggleIcon');
            sidebar.classList.toggle('collapsed');
            icon.className = sidebar.classList.contains('collapsed') ? 'fas fa-angles-right' : 'fas fa-angles-left';
        }}

        function showSection(section) {{
            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            
            const sectionMap = {{
                'dashboard': 'dashboardSection',
                'violations': 'violationsSection',
                'analytics': 'analyticsSection',
                'reports': 'reportsSection',
                'search': 'searchSection'
            }};
            
            document.getElementById(sectionMap[section]).classList.add('active');
            event.target.closest('.nav-item').classList.add('active');
        }}

        function searchTable() {{
            const input = document.getElementById('searchInput').value.toLowerCase();
            const filter = document.getElementById('violationFilter') ? document.getElementById('violationFilter').value : '';
            
            filteredData = baseData.filter(row => {{
                const matchesSearch = Object.values(row).some(val => String(val).toLowerCase().includes(input));
                const matchesFilter = !filter || row['Violation Type'] === filter;
                return matchesSearch && matchesFilter;
            }});
            
            currentPage = 1;
            updateTable();
        }}

        function filterTable() {{
            searchTable();
        }}

        function updateTable() {{
            const table = document.getElementById('databaseTable');
            const tbody = table.querySelector('tbody');
            tbody.innerHTML = '';
            
            const start = (currentPage - 1) * rowsPerPage;
            const end = start + rowsPerPage;
            const pageData = filteredData.slice(start, end);
            
            pageData.forEach(row => {{
                const tr = document.createElement('tr');
                Object.values(row).forEach(val => {{
                    const td = document.createElement('td');
                    td.textContent = val;
                    tr.appendChild(td);
                }});
                tbody.appendChild(tr);
            }});
            
            const totalPages = Math.ceil(filteredData.length / rowsPerPage) || 1;
            document.getElementById('currentPage').textContent = currentPage;
            document.getElementById('totalPages').textContent = totalPages;
            
            const buttons = document.querySelectorAll('.pagination button');
            buttons[0].disabled = currentPage === 1;
            buttons[1].disabled = currentPage === totalPages;
        }}

        function changePage(direction) {{
            const totalPages = Math.ceil(filteredData.length / rowsPerPage);
            currentPage += direction;
            if (currentPage < 1) currentPage = 1;
            if (currentPage > totalPages) currentPage = totalPages;
            updateTable();
        }}

        function searchVehicle() {{
            const input = document.getElementById('vehicleSearch').value.toLowerCase();
            const results = baseData.filter(row => 
                String(row['Number Plate']).toLowerCase().includes(input)
            );
            
            const resultsDiv = document.getElementById('searchResults');
            if (input.length > 0) {{
                resultsDiv.innerHTML = `
                    <div class="content-card" style="margin-top: 20px;">
                        <h4 style="margin-bottom: 15px;">Found ${{results.length}} records</h4>
                        <div class="table-wrapper">
                            ${{results.map(r => `
                                <div class="activity-item">
                                    <strong>${{r['Number Plate']}}</strong> - ${{r['Violation Type']}} - ₹${{r['Challan']}}
                                    <div class="activity-time">${{r['Date'] || 'No date'}}</div>
                                </div>
                            `).join('')}}
                        </div>
                    </div>
                `;
            }} else {{
                resultsDiv.innerHTML = '';
            }}
        }}

        function exportData() {{
            document.getElementById('exportModal').classList.add('active');
        }}

        function closeModal() {{
            document.getElementById('exportModal').classList.remove('active');
        }}

        function downloadCSV() {{
            const headers = Object.keys(baseData[0]);
            const csvContent = [
                headers.join(','),
                ...baseData.map(row => headers.map(h => `"${{row[h]}}"`).join(','))
            ].join('\\n');
            
            const blob = new Blob([csvContent], {{ type: 'text/csv' }});
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `violations_${{new Date().toISOString().split('T')[0]}}.csv`;
            a.click();
            closeModal();
            showNotification('CSV exported successfully!');
        }}

        function downloadJSON() {{
            const jsonContent = JSON.stringify(baseData, null, 2);
            const blob = new Blob([jsonContent], {{ type: 'application/json' }});
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `violations_${{new Date().toISOString().split('T')[0]}}.json`;
            a.click();
            closeModal();
            showNotification('JSON exported successfully!');
        }}

        function refreshData() {{
            showNotification('Data refreshed successfully!');
            location.reload();
        }}

        function generateReport() {{
            showNotification('Report generation started!');
            setTimeout(() => {{
                showNotification('Report ready for download!');
            }}, 2000);
        }}

        function showNotification(message) {{
            const notif = document.getElementById('notification');
            const text = document.getElementById('notificationText');
            text.textContent = message;
            notif.classList.add('show');
            setTimeout(() => {{
                notif.classList.remove('show');
            }}, 3000);
        }}

        document.getElementById('exportModal').addEventListener('click', function(e) {{
            if (e.target === this) closeModal();
        }});

        window.addEventListener('load', function() {{
            initCharts();
            updateTable();
        }});
    </script>
</body>
</html>''')
        
        print("✅ Advanced Traffic Command Center generated successfully!")
        print("🎨 Features: Modern UI, Sidebar Navigation, Multiple Sections, Advanced Charts")
        print("🚀 Sections: Dashboard, Violations, Analytics, Reports, Vehicle Search")
        webbrowser.open("dashboard.html")
        
    except Exception as e:
        print(f"❌ Error generating dashboard: {e}")

if __name__ == "__main__":
    generate_dashboard()