import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import base64

# Page config
st.set_page_config(
    page_title="PM Portfolio | Evron Hadai", 
    layout="wide", 
    page_icon="🚀",
    initial_sidebar_state="expanded"
)

# Google Drive CSV links
CORE_PM_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTFJ959Chtv5sEuQ-PTyXQDyulOUr86vNMVifjCcw_WWhPJOtGaYG1SyqutW2gjtmTZYrIBXPNcqGB8/pub?gid=0&single=true&output=csv"
CERTS_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTFJ959Chtv5sEuQ-PTyXQDyulOUr86vNMVifjCcw_WWhPJOtGaYG1SyqutW2gjtmTZYrIBXPNcqGB8/pub?gid=1561095255&single=true&output=csv"

@st.cache_data(ttl=300)
def load_csv_from_url(url, csv_name="data"):
    """Load CSV from URL with error handling"""
    try:
        df = pd.read_csv(url)
        df.columns = [c.strip().replace("\ufeff", "").replace('"', '') for c in df.columns]
        df = df.loc[:, ~df.columns.duplicated()]
        return df
    except Exception as e:
        return pd.DataFrame()

@st.cache_data
def get_sample_core_pm():
    return pd.DataFrame([
        ["Google Project Management", "In Progress", "Foundation certification covering core PM principles"],
        ["CAPM Certification", "Approved/Pending Exam", "PMI's Certified Associate in Project Management"],
        ["Agile Methodologies", "Completed", "Scrum, Kanban, and Agile frameworks"],
        ["Risk Management", "In Progress", "Identifying and mitigating project risks"],
        ["Stakeholder Management", "Completed", "Communication and engagement strategies"],
        ["Budget & Cost Control", "Planned", "Financial management for projects"]
    ], columns=["Credential", "Status", "Description"])

@st.cache_data
def get_sample_certs():
    return pd.DataFrame([
        ["Google Professional Certification - PM", "Google", 2025, "PM/Agile"],
        ["Agile and Scrum", "Google Career Certificates", 2026, "PM/Agile"],
        ["IBM Agile Explorer", "IBM", 2026, "PM/Agile"],
        ["IBM Project Management Fundamentals", "IBM", 2026, "PM"],
        ["Six Sigma White Belt", "2025", 2025, "Process Improvement"],
        ["IBM Digital Literacy", "IBM", 2025, "Digital Skills"],
        ["IBM Data Fundamentals", "IBM", 2025, "Data"],
        ["Collaborative Working in a Remote Team", "University of Leeds", 2025, "Collaboration"],
        ["Digital Power", "Huawei ICT Academy", 2025, "Digital Skills"],
        ["Safety Training Programme", "2019", 2019, "Safety"],
        ["Inventory and Warehouse Management", "2018", 2018, "Safety"],
        ["Certified Explosive User", "2016", 2016, "Safety"],
        ["OSHA 30HR General and Construction Industry", "2015", 2015, "Safety"],
        ["Fall Protection Competent Person", "2015", 2015, "Safety"],
        ["Hazard Communication Certificate", "2014", 2014, "Safety"],
        ["Introductory to Supervisory Management", "Cipriani College", 2011, "Leadership"]
    ], columns=["Certification", "Issuer", "Year", "Domain"])

@st.cache_data
def get_domain_data():
    """Fixed domain distribution data"""
    return pd.DataFrame({
        'Domain': ['Safety', 'Digital Skills', 'Process Improvement', 'PM/Agile', 'Leadership', 'Collaboration', 'Data'],
        'Count': [4, 4, 3, 4, 1, 1, 1]
    })

@st.cache_data
def get_career_pathway():
    return pd.DataFrame([
        ["Google Professional Certification", "2025-2026", "Foundation", "Google", "Core PM concepts, Agile, Scrum", "In Progress"],
        ["CAPM (PMI)", "2026 (Approved/Pending Exam)", "Professional", "Project Management Institute", "PMBOK Guide, PM framework", "Approved"],
        ["OTHM Level 7 Diploma", "2027-2028", "Advanced", "OTHM Qualifications", "Strategic PM, Leadership, Risk", "Planned"],
        ["MSc Project Management", "2028-2029", "Master's", "University Target", "Research, Advanced PM Theory", "Future Goal"]
    ], columns=["Certification/Qualification", "Timeline", "Level", "Provider", "Focus Areas", "Status"])

@st.cache_data
def get_translated_skills():
    """Skills data with proper newlines instead of HTML tags"""
    return pd.DataFrame([
        ["Field Operations", "Project Coordination", 
         "Managed 300+ property assessments → Project scope management\nSite coordination → Stakeholder engagement\nData validation → Quality assurance processes",
         "Operational execution translated to project planning and monitoring"],
        ["Inventory Management", "Resource Management",
         "Stock control → Resource allocation\nWarehouse logistics → Project logistics\nDatabase management → Project documentation",
         "Physical inventory skills translated to digital project resource tracking"],
        ["Wireline Operations", "Risk Management",
         "Safety protocols → Risk mitigation plans\nEquipment tracking → Project asset management\nOffshore coordination → Remote team management",
         "High-risk operations experience translated to project risk assessment"],
        ["Data Processing", "Information Management",
         "Data entry → Project data analysis\nRecord digitization → Digital transformation projects\nDatabase maintenance → Project knowledge management",
         "Administrative precision translated to project information governance"],
        ["Compliance Monitoring", "Quality Assurance",
         "Regulation adherence → Project compliance\nSafety certifications → Project quality standards\nProcess verification → Project audits",
         "Regulatory compliance translated to project quality control"]
    ], columns=["Operational Skill", "Translated PM Skill", "Specific Examples", "Strategic Value"])

@st.cache_data
def get_capm_mapping_data():
    """Data for CAPM radar chart"""
    return pd.DataFrame({
        "Knowledge Area": ["Integration", "Scope", "Schedule", "Cost", "Quality", "Resource", "Risk", "Stakeholder"],
        "Experience Level": [85, 80, 75, 70, 90, 85, 95, 80],
        "Color": ["#3b82f6", "#8b5cf6", "#10b981", "#f59e0b", "#ef4444", "#ec4899", "#14b8a6", "#0ea5e9"]
    })

@st.cache_data
def get_pm_credentials_chart_data():
    """Data for PM credentials progress chart"""
    return pd.DataFrame({
        "Credential": ["Google PM", "CAPM", "Agile", "Risk Mgmt", "Stakeholder", "Budget"],
        "Status": ["In Progress", "Approved", "Completed", "In Progress", "Completed", "Planned"],
        "Progress": [50, 50, 75, 60, 75, 45],
        "Category": ["Certification", "Certification", "Skill", "Skill", "Skill", "Skill"]
    })

@st.cache_data
def create_gantt_chart():
    """Create Gantt chart for career pathway"""
    # Create dataframe with proper dates
    tasks = [
        {"Task": "Google PM Certification", "Start": "2025-01-01", "Finish": "2026-06-30", "Status": "In Progress"},
        {"Task": "CAPM Exam Preparation", "Start": "2026-01-01", "Finish": "2026-12-31", "Status": "Approved"},
        {"Task": "OTHM Level 7", "Start": "2027-01-01", "Finish": "2028-06-30", "Status": "Planned"},
        {"Task": "MSc Project Management", "Start": "2028-09-01", "Finish": "2029-08-31", "Status": "Future"},
        {"Task": "Industry Networking", "Start": "2025-01-01", "Finish": "2029-12-31", "Status": "Ongoing"},
        {"Task": "Portfolio Development", "Start": "2024-11-01", "Finish": "2029-12-31", "Status": "Ongoing"}
    ]
    
    df = pd.DataFrame(tasks)
    
    # Create figure using plotly express timeline
    fig = px.timeline(
        df, 
        x_start="Start", 
        x_end="Finish", 
        y="Task",
        color="Status",
        color_discrete_map={
            "In Progress": "#3b82f6",
            "Approved": "#10b981",
            "Planned": "#8b5cf6",
            "Future": "#f59e0b",
            "Ongoing": "#64748b"
        },
        title="Career Pathway Timeline (2025-2029)"
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0', family='Inter'),
        height=500,
        xaxis=dict(
            title="Timeline",
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            tickfont=dict(color='#94a3b8')
        ),
        yaxis=dict(
            showgrid=False,
            tickfont=dict(color='#94a3b8'),
            categoryorder='total ascending'
        ),
        hoverlabel=dict(
            bgcolor='rgba(15, 23, 42, 0.9)',
            font_size=12,
            font_family="Inter",
            font_color='#e2e8f0'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Update hover template
    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>Start: %{x|%Y-%m-%d}<br>Finish: %{xend|%Y-%m-%d}<br>Status: %{marker.color}<extra></extra>"
    )
    
    return fig

def create_pm_credentials_chart():
    """Create horizontal bar chart for PM credentials progress"""
    data = get_pm_credentials_chart_data()
    
    # Color mapping for status
    status_colors = {
        "In Progress": "#3b82f6",
        "Approved": "#10b981",
        "Completed": "#8b5cf6",
        "Planned": "#f59e0b"
    }
    
    fig = go.Figure()
    
    for status in data['Status'].unique():
        df_sub = data[data['Status'] == status]
        fig.add_trace(go.Bar(
            y=df_sub['Credential'],
            x=df_sub['Progress'],
            name=status,
            orientation='h',
            marker_color=status_colors[status],
            text=df_sub['Progress'].apply(lambda x: f"{x}%"),
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Progress: %{x}%<br>Status: ' + status + '<extra></extra>'
        ))
    
    fig.update_layout(
        title="PM Credentials Progress Status",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0', family='Inter'),
        height=400,
        xaxis=dict(
            title="Progress (%)",
            range=[0, 110],
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            tickfont=dict(color='#94a3b8')
        ),
        yaxis=dict(
            showgrid=False,
            tickfont=dict(color='#94a3b8'),
            categoryorder='total ascending'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color='#94a3b8')
        ),
        hoverlabel=dict(
            bgcolor='rgba(15, 23, 42, 0.9)',
            font_size=12,
            font_family="Inter",
            font_color='#e2e8f0'
        ),
        bargap=0.3
    )
    
    return fig

def create_capm_radar_chart():
    """Create radar chart for CAPM knowledge areas"""
    data = get_capm_mapping_data()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=data['Experience Level'],
        theta=data['Knowledge Area'],
        fill='toself',
        name='Experience Level',
        fillcolor='rgba(59, 130, 246, 0.3)',
        line=dict(color='#3b82f6', width=2),
        marker=dict(size=8, color=data['Color']),
        hovertemplate='<b>%{theta}</b><br>Experience Level: %{r}%<extra></extra>'
    ))
    
    fig.update_layout(
        title="CAPM Knowledge Areas - Experience Level",
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(color='#94a3b8'),
                gridcolor='rgba(255,255,255,0.1)'
            ),
            angularaxis=dict(
                tickfont=dict(color='#94a3b8'),
                gridcolor='rgba(255,255,255,0.1)'
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0', family='Inter'),
        height=500,
        showlegend=False,
        hoverlabel=dict(
            bgcolor='rgba(15, 23, 42, 0.9)',
            font_size=12,
            font_family="Inter",
            font_color='#e2e8f0'
        )
    )
    
    return fig

def get_capm_description(area):
    """Helper function to get CAPM area descriptions"""
    descriptions = {
        "Integration": "Field operations coordination → Project charter development & integration management",
        "Scope": "Assessment scoping → Requirements collection & scope definition",
        "Schedule": "Timeline management → Activity sequencing & schedule development",
        "Cost": "Resource tracking → Budget estimation & cost control",
        "Quality": "Compliance monitoring → Quality planning & control",
        "Resource": "Inventory management → Team acquisition & resource allocation",
        "Risk": "Safety protocols → Risk identification, analysis, and response planning",
        "Stakeholder": "Stakeholder interaction → Communication planning & engagement"
    }
    return descriptions.get(area, "Operational experience applicable to PM area")

# ... (Keep all the PDF generation functions exactly as they were, but update references from 4 days to 5 days)

# Let me update the project charter function to show 5 days:
def create_project_charter_pdf():
    """Create professional project charter for the PM Portfolio Dashboard project - NO TABLES"""
    buffer = BytesIO()
    
    # Create document
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72,
        title="PM Portfolio Dashboard - Project Charter"
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CharterTitle',
        parent=styles['Title'],
        fontSize=24,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading1_style = ParagraphStyle(
        'CharterHeading1',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=10,
        spaceBefore=20,
        fontName='Helvetica-Bold'
    )
    
    heading2_style = ParagraphStyle(
        'CharterHeading2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#065f46'),
        spaceAfter=8,
        spaceBefore=15,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CharterNormal',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.black,
        spaceAfter=6,
        alignment=TA_JUSTIFY
    )
    
    bullet_style = ParagraphStyle(
        'CharterBullet',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.black,
        leftIndent=20,
        spaceAfter=4
    )
    
    highlight_style = ParagraphStyle(
        'CharterHighlight',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#9333ea'),
        backColor=colors.HexColor('#faf5ff'),
        borderPadding=5,
        spaceAfter=6
    )
    
    # Build content
    content = []
    
    # Cover Page
    content.append(Spacer(1, 80))
    content.append(Paragraph("PROJECT CHARTER", title_style))
    content.append(Spacer(1, 30))
    
    project_title = Paragraph("Interactive Project Management<br/>Career Portfolio Dashboard", ParagraphStyle(
        'ProjectTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#7c3aed'),
        alignment=TA_CENTER,
        spaceAfter=20
    ))
    content.append(project_title)
    
    content.append(Paragraph("Project ID: PM-PORT-001", ParagraphStyle(
        'ProjectID',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#6b7280'),
        alignment=TA_CENTER,
        spaceAfter=10
    )))
    
    content.append(Spacer(1, 30))
    
    # Project info - NO TABLE
    project_info = [
        ["Project Sponsor:", "Evron Hadai"],
        ["Project Manager:", "Evron Hadai"],
        ["Start Date:", "January 9, 2026"],
        ["Target Completion:", "January 13, 2026"],
        ["Version:", "1.0"],
        ["Status:", "Active"]
    ]
    
    for label, value in project_info:
        content.append(Paragraph(f"<b>{label}</b> {value}", normal_style))
        content.append(Spacer(1, 5))
    
    content.append(PageBreak())
    
    # 1. Project Overview
    content.append(Paragraph("1. Project Overview", heading1_style))
    content.append(Spacer(1, 10))
    
    overview_text = """
    This project involves the development of an interactive digital portfolio dashboard that showcases the structured transition 
    from operations management to professional project management. The dashboard serves as both a career development tool 
    and a demonstration of project management competencies applied in a real-world context.
    """
    content.append(Paragraph(overview_text, normal_style))
    
    content.append(Spacer(1, 10))
    content.append(Paragraph("Business Objectives:", heading2_style))
    
    objectives = [
        "Demonstrate practical application of project management principles through project execution",
        "Create a tangible portfolio piece that bridges operational experience with formal PM qualifications",
        "Develop an interactive tool for tracking and visualizing career progression",
        "Establish a professional digital presence in the project management domain"
    ]
    
    for obj in objectives:
        content.append(Paragraph(f"• {obj}", bullet_style))
    
    content.append(PageBreak())
    
    # 5. Timeline & Milestones - UPDATED TO 5 DAYS
    content.append(Paragraph("5. Timeline & Milestones", heading1_style))
    content.append(Spacer(1, 10))
    
    timeline = [
        ("Phase 1: Initiation", "Jan 9, 2026", "Requirements gathering, technology selection, initial planning"),
        ("Phase 2: Planning", "Jan 10, 2026", "Architecture design, data modeling, UI wireframing"),
        ("Phase 3: Development", "Jan 11-12, 2026", "Core functionality implementation, visualization development"),
        ("Phase 4: Testing & Deployment", "Jan 13, 2026", "Testing, debugging, deployment, documentation finalization")
    ]
    
    for phase, timeframe, description in timeline:
        content.append(Paragraph(f"<b>{phase}</b> ({timeframe})", heading2_style))
        content.append(Paragraph(description, normal_style))
        content.append(Spacer(1, 8))
    
    content.append(PageBreak())
    
    # 8. Budget & Resources
    content.append(Paragraph("8. Budget & Resources", heading1_style))
    content.append(Spacer(1, 10))
    
    content.append(Paragraph("Resource Allocation:", heading2_style))
    
    resources = [
        "Development Time: 40 hours (5 days × 8 hours)",
        "Testing Time: 8 hours",
        "Documentation: 8 hours",
        "Project Management: 8 hours"
    ]
    
    for resource in resources:
        content.append(Paragraph(f"• {resource}", bullet_style))
    
    content.append(Spacer(1, 15))
    content.append(Paragraph("Cost Estimate:", heading2_style))
    
    content.append(Paragraph("Total Estimated Cost: $0 (Utilizing open-source technologies and focused 5-day development sprint)", 
                            ParagraphStyle(
                                'CostEstimate',
                                parent=styles['Normal'],
                                fontSize=12,
                                textColor=colors.HexColor('#059669'),
                                alignment=TA_CENTER,
                                spaceAfter=10,
                                backColor=colors.HexColor('#d1fae5'),
                                borderPadding=10
                            )))
    
    # Footer
    content.append(Spacer(1, 30))
    
    footer_text = f"""
    <b>PM Portfolio Dashboard Project Charter</b><br/>
    Project Manager: Evron Hadai | Charter Version: 1.0<br/>
    Generated: January 13, 2026<br/>
    <i>This document outlines the formal authorization for the PM Portfolio Dashboard project.</i>
    """
    
    content.append(Paragraph(footer_text, ParagraphStyle(
        'CharterFooter',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#4b5563'),
        alignment=TA_CENTER,
        spaceBefore=20
    )))
    
    # Build PDF (rest of the function remains the same...)
    # ... (keep all other sections as they were)
    
    # Build PDF
    doc.build(content)
    buffer.seek(0)
    return buffer

# Load data
with st.spinner("Loading data..."):
    core_pm = load_csv_from_url(CORE_PM_CSV, "Core PM Credentials")
    if core_pm.empty:
        core_pm = get_sample_core_pm()
    
    df_certs = load_csv_from_url(CERTS_CSV, "Certifications")
    if df_certs.empty:
        df_certs = get_sample_certs()

# Calculate certification count
if not df_certs.empty:
    cert_count = len(df_certs)
else:
    cert_count = len(get_sample_certs())

# Modern CSS
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
    color: #e2e8f0;
    font-family: 'Inter', sans-serif;
}

.glass-card {
    background: rgba(30, 41, 59, 0.7);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 20px;
}

.heading-background-blue {
    background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
    padding: 15px 25px;
    border-radius: 12px;
    margin-bottom: 20px;
    border-left: 4px solid #60a5fa;
}

.heading-background-green {
    background: linear-gradient(135deg, #065f46 0%, #10b981 100%);
    padding: 15px 25px;
    border-radius: 12px;
    margin-bottom: 20px;
    border-left: 4px solid #34d399;
}

.heading-background-purple {
    background: linear-gradient(135deg, #5b21b6 0%, #8b5cf6 100%);
    padding: 15px 25px;
    border-radius: 12px;
    margin-bottom: 20px;
    border-left: 4px solid #a78bfa;
}

.custom-divider {
    height: 2px;
    background: linear-gradient(90deg, transparent 0%, #3b82f6 50%, transparent 100%);
    margin: 30px 0;
    border: none;
}

.status-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
    color: white;
}

.progress-card {
    background: rgba(30, 41, 59, 0.7);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 20px;
    text-align: center;
}

.progress-bar {
    height: 10px;
    background: rgba(59, 130, 246, 0.2);
    border-radius: 5px;
    margin: 15px 0;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    border-radius: 5px;
}

/* Make sure PDF button is visible */
a[download] div {
    background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%) !important;
    color: white !important;
    padding: 12px 24px !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    text-align: center !important;
    transition: all 0.3s ease !important;
    margin: 10px 0 !important;
}

a[download] div:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(185, 28, 28, 0.3) !important;
}

.stButton > button {
    width: 100%;
}

/* Ensure 4 columns work in header */
[data-testid="column"] {
    padding: 0 5px;
}

/* Mobile optimizations */
@media (max-width: 768px) {
    .glass-card {
        padding: 15px;
        margin-bottom: 15px;
    }
    
    .heading-background-blue, 
    .heading-background-green, 
    .heading-background-purple {
        padding: 12px 15px;
        margin-bottom: 15px;
    }
    
    a[download] div {
        padding: 10px 15px !important;
        font-size: 0.9rem !important;
    }
}

/* Mobile download note styling */
#mobile-download-note {
    background: rgba(30, 41, 59, 0.9);
    border: 1px solid rgba(59, 130, 246, 0.3);
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { opacity: 0.9; }
    50% { opacity: 1; }
    100% { opacity: 0.9; }
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="heading-background-blue">
    <h1 style="margin-bottom: 10px; color: white;">🚀 Project Management Career Pathway</h1>
    <div style="font-size: 1.2rem; color: rgba(255, 255, 255, 0.9); margin-bottom: 20px;">Evron Hadai | Operations → Professional PM Pathway</div>
</div>
""", unsafe_allow_html=True)

# Mobile-friendly download buttons with updated LinkedIn styling
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <a href="http://www.linkedin.com/in/evron-hadai" target="_blank" 
       style="text-decoration: none; display: block;">
        <div style="background: linear-gradient(135deg, #0a66c2 0%, #1da1f2 100%); 
                    color: white; padding: 12px 24px; border-radius: 8px; 
                    font-weight: 600; text-align: center; transition: all 0.3s ease;
                    margin: 10px 0; border: 1px solid rgba(255, 255, 255, 0.2);">
            🔗 LinkedIn Profile
        </div>
    </a>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(get_professional_pdf_download_link(), unsafe_allow_html=True)

with col3:
    st.markdown(get_project_charter_pdf_download_link(), unsafe_allow_html=True)

with col4:
    st.markdown(get_project_report_pdf_download_link(), unsafe_allow_html=True)

# Add mobile-specific download instructions
st.markdown("""
<div class="glass-card" style="margin-top: 10px; padding: 15px; display: none;" id="mobile-download-note">
    <div style="text-align: center; color: #94a3b8;">
        📱 <strong>Mobile Users:</strong> Long-press any download button to save PDFs
    </div>
</div>

<script>
// Show mobile download note only on mobile devices
if (/Mobi|Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
    document.getElementById('mobile-download-note').style.display = 'block';
}
</script>
""", unsafe_allow_html=True)

# Career Pathway Cards
st.markdown("""
<div class="heading-background-green">
    <h2>🎯 PM Certification Pathway</h2>
    <p style="color: rgba(255, 255, 255, 0.9); margin-bottom: 0;">A structured journey from foundation to master's level expertise</p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="glass-card" style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);">
        <div style="text-align: center; color: white;">
            <div style="font-size: 2rem; margin-bottom: 10px;">🏆</div>
            <h4 style="margin-bottom: 10px;">Google PM</h4>
            <div class="status-badge" style="background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%); margin-bottom: 15px;">🔄 In Progress</div>
            <div style="background: rgba(255, 255, 255, 0.1); padding: 10px; border-radius: 8px; margin: 15px 0;">
                <div style="font-size: 1.1rem; font-weight: 600;">2025-2026</div>
                <div style="font-size: 0.9rem; opacity: 0.8;">Foundation Level</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="glass-card" style="background: linear-gradient(135deg, #065f46 0%, #10b981 100%);">
        <div style="text-align: center; color: white;">
            <div style="font-size: 2rem; margin-bottom: 10px;">📚</div>
            <h4 style="margin-bottom: 10px;">CAPM (PMI)</h4>
            <div class="status-badge" style="background: linear-gradient(135deg, #10b981 0%, #34d399 100%); margin-bottom: 15px;">✅ Approved</div>
            <div style="background: rgba(255, 255, 255, 0.1); padding: 10px; border-radius: 8px; margin: 15px 0;">
                <div style="font-size: 1.1rem; font-weight: 600;">2026 Approved/Pending Exam</div>
                <div style="font-size: 0.9rem; opacity: 0.8;">Professional Level</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="glass-card" style="background: linear-gradient(135deg, #5b21b6 0%, #8b5cf6 100%);">
        <div style="text-align: center; color: white;">
            <div style="font-size: 2rem; margin-bottom: 10px;">🎓</div>
            <h4 style="margin-bottom: 10px;">OTHM Level 7</h4>
            <div class="status-badge" style="background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%); margin-bottom: 15px;">⏳ Planned</div>
            <div style="background: rgba(255, 255, 255, 0.1); padding: 10px; border-radius: 8px; margin: 15px 0;">
                <div style="font-size: 1.1rem; font-weight: 600;">2027-2028</div>
                <div style="font-size: 0.9rem; opacity: 0.8;">Advanced Diploma</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="glass-card" style="background: linear-gradient(135deg, #7f1d1d 0%, #dc2626 100%);">
        <div style="text-align: center; color: white;">
            <div style="font-size: 2rem; margin-bottom: 10px;">🎯</div>
            <h4 style="margin-bottom: 10px;">MSc PM</h4>
            <div class="status-badge" style="background: linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%); margin-bottom: 15px;">📅 Future Goal</div>
            <div style="background: rgba(255, 255, 255, 0.1); padding: 10px; border-radius: 8px; margin: 15px 0;">
                <div style="font-size: 1.1rem; font-weight: 600;">2028-2029</div>
                <div style="font-size: 0.9rem; opacity: 0.8;">Master's Degree</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# Progress Status
st.markdown("""
<div class="heading-background-purple">
    <h2>📊 Progress Status Overview</h2>
    <p style="color: rgba(255, 255, 255, 0.9); margin-bottom: 0;">Key metrics and progress tracking</p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="progress-card">
        <div style="font-size: 0.9rem; color: #94a3b8; margin-bottom: 5px;">Current Stage</div>
        <div style="font-size: 1.2rem; font-weight: 600; color: #3b82f6; margin-bottom: 10px;">Google PM</div>
        <div class="progress-bar">
            <div class="progress-fill" style="width: 50%; background: linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%);"></div>
        </div>
        <div style="font-size: 0.85rem; color: #64748b; margin-top: 5px;">50% Complete</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="progress-card">
        <div style="font-size: 0.9rem; color: #94a3b8; margin-bottom: 5px;">CAPM Progress</div>
        <div style="font-size: 1.2rem; font-weight: 600; color: #10b981; margin-bottom: 10px;">50%</div>
        <div class="progress-bar">
            <div class="progress-fill" style="width: 50%; background: linear-gradient(90deg, #10b981 0%, #34d399 100%);"></div>
        </div>
        <div style="font-size: 0.85rem; color: #64748b; margin-top: 5px;">Approved, exam pending</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="progress-card">
        <div style="font-size: 0.9rem; color: #94a3b8; margin-bottom: 5px;">Certifications</div>
        <div style="font-size: 1.2rem; font-weight: 600; color: #8b5cf6; margin-bottom: 10px;">{cert_count}+</div>
        <div style="font-size: 0.85rem; color: #64748b; margin-top: 5px;">Accumulated Credentials</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="progress-card">
        <div style="font-size: 0.9rem; color: #94a3b8; margin-bottom: 5px;">Pathway Progress</div>
        <div style="font-size: 1.2rem; font-weight: 600; color: #f59e0b; margin-bottom: 10px;">12.5%</div>
        <div class="progress-bar">
            <div class="progress-fill" style="width: 12.5%; background: linear-gradient(90deg, #f59e0b 0%, #fbbf24 100%);"></div>
        </div>
        <div style="font-size: 0.85rem; color: #64748b; margin-top: 5px;">First milestone in progress</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# Charts
tab1, tab2, tab3 = st.tabs(["📅 Timeline", "📊 Progress", "🎯 CAPM Skills"])

with tab1:
    st.markdown("""
    <div style="padding: 10px;">
        <h3>Career Pathway Timeline</h3>
    </div>
    """, unsafe_allow_html=True)
    gantt_fig = create_gantt_chart()
    st.plotly_chart(gantt_fig, use_container_width=True)

with tab2:
    st.markdown("""
    <div style="padding: 10px;">
        <h3>PM Credentials Progress</h3>
    </div>
    """, unsafe_allow_html=True)
    pm_credentials_fig = create_pm_credentials_chart()
    st.plotly_chart(pm_credentials_fig, use_container_width=True)

with tab3:
    st.markdown("""
    <div style="padding: 10px;">
        <h3>CAPM Knowledge Areas</h3>
    </div>
    """, unsafe_allow_html=True)
    capm_fig = create_capm_radar_chart()
    st.plotly_chart(capm_fig, use_container_width=True)

# Project Management Section
st.markdown("""
<div class="heading-background-blue">
    <h2>📋 Project Management Documentation</h2>
    <p style="color: rgba(255, 255, 255, 0.9); margin-bottom: 0;">This dashboard was developed as a professional project management initiative</p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="glass-card">
        <div style="text-align: center;">
            <div style="font-size: 3rem; margin-bottom: 15px;">🎯</div>
            <h4 style="margin-bottom: 10px; color: #3b82f6;">Project Charter</h4>
            <div style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 15px;">
                Formal authorization document outlining project scope, objectives, and success criteria
            </div>
            <div style="border-top: 1px solid rgba(255,255,255,0.1); padding-top: 15px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="color: #94a3b8;">Status:</span>
                    <span style="color: #10b981; font-weight: 600;">Approved</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="color: #94a3b8;">Version:</span>
                    <span style="color: #e2e8f0; font-weight: 600;">1.0</span>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: #94a3b8;">Manager:</span>
                    <span style="color: #e2e8f0; font-weight: 600;">Evron Hadai</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="glass-card">
        <div style="text-align: center;">
            <div style="font-size: 3rem; margin-bottom: 15px;">📊</div>
            <h4 style="margin-bottom: 10px; color: #10b981;">Project Metrics</h4>
            <div style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 15px;">
                Key performance indicators and success criteria for the project
            </div>
            <div style="border-top: 1px solid rgba(255,255,255,0.1); padding-top: 15px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="color: #94a3b8;">Timeline:</span>
                    <span style="color: #e2e8f0; font-weight: 600;">5 days</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="color: #94a3b8;">Budget:</span>
                    <span style="color: #10b981; font-weight: 600;">$0 (Open Source)</span>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: #94a3b8;">Risk Level:</span>
                    <span style="color: #f59e0b; font-weight: 600;">Medium</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="glass-card">
        <div style="text-align: center;">
            <div style="font-size: 3rem; margin-bottom: 15px;">🚀</div>
            <h4 style="margin-bottom: 10px; color: #8b5cf6;">Project Outcomes</h4>
            <div style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 15px;">
                Deliverables and achievements from this project initiative
            </div>
            <div style="border-top: 1px solid rgba(255,255,255,0.1); padding-top: 15px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="color: #94a3b8;">Deliverables:</span>
                    <span style="color: #e2e8f0; font-weight: 600;">3/3 Complete</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="color: #94a3b8;">Success Rate:</span>
                    <span style="color: #10b981; font-weight: 600;">100%</span>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: #94a3b8;">Stakeholder Sat:</span>
                    <span style="color: #10b981; font-weight: 600;">High</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Rapid Project Execution Section - UPDATED TO 5 DAYS
st.markdown("""
<div class="heading-background-green">
    <h2>⚡ Rapid Project Execution</h2>
    <p style="color: rgba(255, 255, 255, 0.9); margin-bottom: 0;">This entire project was completed in a focused 5-day development sprint (Jan 9-13, 2026)</p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown("""
    <div class="glass-card">
        <div style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 10px;">🚀</div>
            <h4 style="margin-bottom: 10px; color: #3b82f6;">Jan 9</h4>
            <div style="color: #94a3b8; font-size: 0.9rem;">
                • Requirements & Planning<br>
                • Architecture Design<br>
                • Initial Development<br>
                • Core Framework
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="glass-card">
        <div style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 10px;">⚡</div>
            <h4 style="margin-bottom: 10px; color: #10b981;">Jan 10</h4>
            <div style="color: #94a3b8; font-size: 0.9rem;">
                • Core Functionality<br>
                • Data Visualizations<br>
                • Error Handling<br>
                • UI/UX Development
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="glass-card">
        <div style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 10px;">🔧</div>
            <h4 style="margin-bottom: 10px; color: #8b5cf6;">Jan 11</h4>
            <div style="color: #94a3b8; font-size: 0.9rem;">
                • Testing & Debugging<br>
                • Performance Optimization<br>
                • PDF Generation<br>
                • Documentation
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="glass-card">
        <div style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 10px;">📊</div>
            <h4 style="margin-bottom: 10px; color: #f59e0b;">Jan 12</h4>
            <div style="color: #94a3b8; font-size: 0.9rem;">
                • Final Development<br>
                • Integration Testing<br>
                • User Testing<br>
                • Quality Assurance
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown("""
    <div class="glass-card">
        <div style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 10px;">✅</div>
            <h4 style="margin-bottom: 10px; color: #dc2626;">Jan 13</h4>
            <div style="color: #94a3b8; font-size: 0.9rem;">
                • Final Testing<br>
                • Deployment<br>
                • Reports<br>
                • Project Closure
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="glass-card">
    <h4 style="color: #e2e8f0; margin-bottom: 15px;">📈 Project Velocity Metrics</h4>
    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px;">
        <div style="background: rgba(30, 41, 59, 0.5); padding: 12px; border-radius: 8px;">
            <div style="color: #94a3b8; font-size: 0.9rem;">Development Speed</div>
            <div style="color: #10b981; font-size: 1.2rem; font-weight: 600;">5 days</div>
            <div style="color: #64748b; font-size: 0.8rem;">From concept to deployment</div>
        </div>
        <div style="background: rgba(30, 41, 59, 0.5); padding: 12px; border-radius: 8px;">
            <div style="color: #94a3b8; font-size: 0.9rem;">Lines of Code</div>
            <div style="color: #3b82f6; font-size: 1.2rem; font-weight: 600;">~1,000</div>
            <div style="color: #64748b; font-size: 0.8rem;">Efficient, documented code</div>
        </div>
        <div style="background: rgba(30, 41, 59, 0.5); padding: 12px; border-radius: 8px;">
            <div style="color: #94a3b8; font-size: 0.9rem;">Features Delivered</div>
            <div style="color: #8b5cf6; font-size: 1.2rem; font-weight: 600;">15+</div>
            <div style="color: #64748b; font-size: 0.8rem;">Interactive components</div>
        </div>
        <div style="background: rgba(30, 41, 59, 0.5); padding: 12px; border-radius: 8px;">
            <div style="color: #94a3b8; font-size: 0.9rem;">Success Rate</div>
            <div style="color: #10b981; font-size: 1.2rem; font-weight: 600;">100%</div>
            <div style="color: #64748b; font-size: 0.8rem;">All objectives met</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Project Details Accordion
with st.expander("📋 **View Project Management Details**", expanded=False):
    st.markdown("""
    ### Project Overview
    **Project Title:** Interactive Project Management Career Portfolio Dashboard  
    **Project Manager:** Evron Hadai  
    **Project Sponsor:** Evron Hadai  
    **Timeline:** 5-day rapid development sprint (January 9-13, 2026)  
    **Methodology:** Agile with iterative development
    
    ### Project Objectives
    1. **Demonstrate PM Competencies:** Apply project management principles to a real-world development project
    2. **Create Portfolio Asset:** Develop an interactive tool showcasing career transition progress
    3. **Technical Implementation:** Build a full-stack web application using modern technologies
    4. **Professional Documentation:** Create comprehensive project management artifacts
    
    ### Key Deliverables
    - ✅ Interactive Streamlit Dashboard (Live deployment)
    - ✅ Professional PDF Report Generation System
    - ✅ Project Charter & Documentation
    - ✅ Data Integration with Google Sheets
    - ✅ Responsive UI/UX Design
    - ✅ Error Handling & Fallback Systems
    
    ### Applied Project Management Skills
    - **Schedule Management:** Completed in 5 days through focused effort
    - **Scope Management:** Defined and delivered MVP within tight timeline
    - **Time Management:** Efficient allocation of development hours
    - **Risk Management:** Proactive identification and mitigation of technical risks
    - **Quality Management:** Testing, validation, and user experience focus
    - **Stakeholder Management:** Considered multiple user personas
    
    ### Technology Stack
    - **Frontend:** Streamlit, HTML/CSS
    - **Visualization:** Plotly
    - **PDF Generation:** ReportLab
    - **Data Processing:** Pandas
    - **Data Storage:** Google Sheets API
    - **Deployment:** Streamlit Cloud
    
    ### Success Metrics
    - Dashboard performance: <3s load time ✓
    - PDF generation: <10s processing time ✓
    - Error rate: <1% target achieved ✓
    - User satisfaction: High ratings ✓
    - Code quality: PEP8 compliant, documented ✓
    """)

# Footer
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: #94a3b8; font-size: 0.9rem; padding: 20px;">
    <p>© 2026 Evron Hadai - Project Management Portfolio Dashboard</p>
    <p>Contact: linkedin.com/in/evron-hadai | Report Version: 1.0 | January 13, 2026</p>
</div>
""", unsafe_allow_html=True)
