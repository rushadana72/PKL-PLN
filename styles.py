"""
CSS Styles for SOSYS Material Automation
All styling and visual design elements
"""

def get_custom_css():
    """
    Returns the complete CSS styling for the application
    """
    return """
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        /* ==================== GLOBAL STYLES ==================== */
        @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@400;500;700&display=swap');
        
        :root {
            --primary: #2563eb;
            --primary-dark: #1e40af;
            --secondary: #64748b;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --background: #f8fafc;
            --surface: #ffffff;
            --border: #e2e8f0;
            --text-primary: #0f172a;
            --text-secondary: #64748b;
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }
        
        * {
            font-family: 'DM Sans', sans-serif;
        }
        
        .block-container {
            padding-top: 3rem;
            padding-bottom: 2rem;
            max-width: 900px;
            margin: 0 auto;
        }
        
        /* Hide Streamlit branding */
        #MainMenu, footer, header {visibility: hidden;}
        
        /* ==================== TYPOGRAPHY ==================== */
        h1, h2, h3 {
            font-family: 'Space Mono', monospace;
            font-weight: 700;
            letter-spacing: -0.02em;
        }
        
        /* ==================== CARDS & CONTAINERS ==================== */
        .modern-card {
            background: var(--surface);
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid var(--border);
            box-shadow: var(--shadow-sm);
            transition: all 0.3s ease;
            margin-bottom: 1.5rem;
        }
        
        .modern-card:hover {
            box-shadow: var(--shadow-md);
            transform: translateY(-2px);
        }
        
        .step-card {
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            border-radius: 16px;
            padding: 2rem;
            border: 2px solid var(--border);
            position: relative;
            overflow: hidden;
            margin-bottom: 2rem;
        }
        
        .step-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: linear-gradient(180deg, var(--primary) 0%, var(--primary-dark) 100%);
        }
        
        .step-number {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 32px;
            height: 32px;
            background: var(--primary);
            color: white;
            border-radius: 50%;
            font-weight: 700;
            font-size: 0.875rem;
            margin-right: 0.75rem;
        }
        
        .step-title {
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
        }
        
        .step-description {
            color: var(--text-secondary);
            font-size: 0.95rem;
            line-height: 1.6;
        }
        
        /* ==================== BUTTONS ==================== */
        .stButton > button {
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            font-size: 0.95rem;
            transition: all 0.3s ease;
            box-shadow: var(--shadow-sm);
            width: 100%;
        }
        
        .stButton > button:hover {
            box-shadow: var(--shadow-md);
            transform: translateY(-2px);
        }
        
        .stButton > button:active {
            transform: translateY(0);
        }
        
        /* Secondary Button - White text */
        .stButton > button[kind="secondary"] {
            background: white;
            color: white !important;
            border: 2px solid var(--primary);
        }
        
        .stButton > button[kind="secondary"]:hover {
            background: var(--primary);
            border-color: var(--primary-dark);
        }
        
        /* ==================== DOWNLOAD BUTTONS ==================== */
        .stDownloadButton > button {
            background: linear-gradient(135deg, var(--success) 0%, #059669 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            font-size: 0.95rem;
            transition: all 0.3s ease;
            box-shadow: var(--shadow-sm);
            width: 100%;
        }
        
        .stDownloadButton > button:hover {
            box-shadow: var(--shadow-md);
            transform: translateY(-2px);
            background: linear-gradient(135deg, #059669 0%, #047857 100%);
        }
        
        .stDownloadButton > button:active {
            transform: translateY(0);
        }
        
        .stDownloadButton > button:before {
            margin-right: 0.5rem;
        }
        
        /* ==================== FILE UPLOADER ==================== */
        .stFileUploader {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            border: 2px dashed var(--border);
            transition: all 0.3s ease;
        }
        
        .stFileUploader:hover {
            border-color: var(--primary);
            background: var(--background);
        }
        
        /* ==================== METRICS ==================== */
        .metric-card {
            background: var(--surface);
            border-radius: 12px;
            padding: 1.25rem;
            border: 1px solid var(--border);
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .metric-card:hover {
            box-shadow: var(--shadow-md);
        }
        
        .metric-icon {
            font-size: 1.5rem;
            margin-bottom: 0.5rem;
            opacity: 0.8;
        }
        
        .metric-value {
            font-size: 1.75rem;
            font-weight: 700;
            font-family: 'Space Mono', monospace;
            color: var(--text-primary);
            line-height: 1.2;
        }
        
        .metric-label {
            font-size: 0.75rem;
            color: var(--text-secondary);
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-top: 0.5rem;
        }
        
        /* ==================== FOOTER ==================== */
        .footer {
            margin-top: 2.5rem;
            padding: 1.25rem 0rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            color: var(--text-secondary);
            font-size: 0.8rem;
            border-top: 1px solid var(--border);
        }

        .footer-left {
            display: flex;
            align-items: center;
            gap: 0.4rem;
            font-weight: 500;
            opacity: 0.8;
        }

        .footer-right {
            display: flex;
            align-items: center;
            gap: 0.4rem;
            font-weight: 500;
        }

        /* ==================== NAVBAR ==================== */
        .navbar {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 9999;
            background: linear-gradient(135deg, #0a0f1e 0%, #0d1832 60%, #0f2050 100%);
            border-bottom: 1px solid rgba(37, 99, 235, 0.3);
            box-shadow: 0 2px 24px rgba(37, 99, 235, 0.2);
            padding: 0 2rem;
            height: 64px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .navbar-brand {
            display: flex;
            align-items: center;
            gap: 0.35rem;
            text-decoration: none;
        }

        .navbar-logo {
            width: 40px;
            height: 40px;
            object-fit: contain;
            border-radius: 8px;
            filter: drop-shadow(0 0 8px rgba(37, 99, 235, 0.6));
        }

        .navbar-logo-placeholder {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.1rem;
            color: white;
            box-shadow: 0 0 12px rgba(37, 99, 235, 0.5);
        }

        .navbar-title {
            font-family: 'Space Mono', monospace;
            font-size: 1.35rem;
            font-weight: 700;
            color: #ffffff;
            letter-spacing: 0.05em;
        }

        .navbar-title span {
            color: #3b82f6;
        }

        .navbar-badge {
            font-size: 0.68rem;
            font-weight: 600;
            color: #3b82f6;
            background: rgba(37, 99, 235, 0.15);
            border: 1px solid rgba(37, 99, 235, 0.3);
            border-radius: 999px;
            padding: 0.15rem 0.6rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .navbar-badge .fa-bolt {
            color: #ffc107; /* kuning */
            text-shadow: 0 0 5px #ffd700
        }


        /* ==================== HEADER ==================== */
        .header-wrapper {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 3rem 0 0.5rem 0;
            gap: 0.5rem;
        }

        .main-title {
            font-size: 2.2rem;
            font-weight: 700;
            line-height: 1.3;
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.25rem;
            display: block;
            text-align: center;
        }
        
        .subtitle {
            font-size: 1rem;
            color: var(--text-secondary);
            font-weight: 400;
            margin-bottom: 0.5rem;
            text-align: center;
        }
        .icon {
            margin-right: 0.5rem;
            color: var(--primary);
        }
        
        hr {
            border: none;
            border-top: 1px solid var(--border);
            margin: 2rem 0;
        }
    </style>
    """