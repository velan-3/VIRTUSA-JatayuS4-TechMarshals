from typing import Annotated, List
from typing_extensions import TypedDict
import sqlite3, pandas as pd
from datetime import datetime, timedelta, date
import re
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langchain_mistralai.chat_models import ChatMistralAI
import os
from fpdf import FPDF
from pathlib import Path
from PyPDF2 import PdfMerger
# Set style for better looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")
matplotlib.use('Agg') 
import os
import sys

def get_data_dir():
    base_dir = os.path.join(os.getenv("TEMP"), "VeterinaryAssistant")
    report_assets_dir = os.path.join(base_dir, "report_assets")
    os.makedirs(report_assets_dir, exist_ok=True)
    # print(report_assets_dir)
    return report_assets_dir

class ChatState(TypedDict,total=False):
    messages: Annotated[List[dict], add_messages]
    df_last30: pd.DataFrame
    df_cur:    pd.DataFrame
    df_prev:   pd.DataFrame
    viz_page:  str          # path to page‑1 PDF (charts)
    text_page: str          # path to page‑2 PDF (LLM text)
    final_pdf: str          # merged two‑page report


os.environ['MISTRAL_API_KEY'] = "VFm7zcXPtANeaSNvMeE6JANXx7Tm0bqC"

llm = ChatMistralAI(
    model="mistral-small-2506",
    temperature=0.5,
    max_tokens=800,  # Reduced for better performance
)


class EnhancedPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)         # Regular
        self.add_font("DejaVu", "B", "DejaVuSans-Bold.ttf", uni=True)
        self.add_font("DejaVu", "I", "DejaVuSans-Oblique.ttf", uni=True)
        
    def header(self):
        self.set_font('DejaVu', 'B', 20)
        self.set_text_color(41, 128, 185)  # Blue color
        self.cell(0, 10, 'Veterinary Health Analysis Report', 0, 1, 'C')
        self.ln(6)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('DejaVu', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()} - Generated on {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 0, 'C')
        
    def add_title(self, title):
        self.set_font('DejaVu', 'B', 14)
        self.set_text_color(52, 73, 94)  # Dark gray
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(3)
        
    def add_subtitle(self, subtitle):
        self.set_font('DejaVu', 'B', 12)
        self.set_text_color(52, 152, 219)  # Light blue
        self.cell(0, 8, subtitle, 0, 1, 'L')
        self.ln(2)
        
    def add_paragraph(self, text):
        self.set_font('DejaVu', '', 10)
        self.set_text_color(0, 0, 0)
        # Handle long text properly
        self.multi_cell(0, 5, text)
        self.ln(2)
        
    def add_bullet_point(self, text):
        self.set_font('DejaVu', '', 10)
        self.set_text_color(0, 0, 0)
        self.cell(10, 5, '•', 0, 0, 'L')
        # Use multi_cell for bullet points to handle wrapping
        x = self.get_x()
        y = self.get_y()
        self.multi_cell(0, 5, text)
        self.ln(1)
        
    def add_highlight_box(self, text, bg_color=(230, 245, 255)):
        self.set_fill_color(*bg_color)
        self.set_font('DejaVu', 'B', 10)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 5, text, 0, 'L', True)
        self.ln(2)


def convert_markdown_to_pdf(markdown_text, pdf):
    """Convert markdown text to formatted PDF content - FIXED VERSION"""
    lines = markdown_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            pdf.ln(2)  # Add small space for empty lines
            continue
            
        # Handle different markdown elements
        if line.startswith('### '):
            pdf.add_subtitle(line[4:])
        elif line.startswith('## '):
            pdf.add_title(line[3:])
        elif line.startswith('# '):
            pdf.add_title(line[2:])
        elif line.startswith('**') and line.endswith('**'):
            # Handle bold text as highlight
            clean_text = line[2:-2]
            pdf.add_highlight_box(clean_text)
        elif line.startswith('- ') or line.startswith('* '):
            # Handle bullet points
            pdf.add_bullet_point(line[2:])
        elif '**' in line:
            # Handle inline bold text
            clean_text = re.sub(r'\*\*(.*?)\*\*', r'\1', line)
            pdf.add_paragraph(clean_text)
        else:
            # Regular paragraph
            pdf.add_paragraph(line)


def first_day_of_month(d: date) -> date:
    return d.replace(day=1)

def previous_month_range(today: date) -> tuple[date, date]:
    first_this = first_day_of_month(today)
    last_day_prev = first_this - timedelta(days=1)
    first_prev = first_day_of_month(last_day_prev)
    return first_prev, first_this


def resource_path(relative_path):
        return os.path.abspath(relative_path)
    
def get_analysis_data(state: ChatState) -> ChatState:
    """Return last‑30‑days, current‑month, and previous‑month data tables - OPTIMIZED."""
    pat = os.path.join(os.getenv("TEMP"), "VeterinaryAssistant", "data", "cattle_data.db")
    os.makedirs(os.path.dirname(pat) , exist_ok=True)

    con = sqlite3.connect(pat)
    today = datetime.today().date()

    # date spans
    thirty_days_ago = today - timedelta(days=30)
    first_this_month = first_day_of_month(today)
    first_prev_month, first_this_month_bound = previous_month_range(today)

    # Optimized SQL - single query with conditional aggregation
    query = """
        SELECT date,
              mouth_disease_count,
               lumpy_skin_count,
               bcs,
               CASE 
                   WHEN date >= ? THEN 'last_30'
                   ELSE 'older'
               END as period_30,
               CASE 
                   WHEN date >= ? THEN 'current_month'
                   WHEN date >= ? AND date < ? THEN 'previous_month'
                   ELSE 'other'
               END as period_month
        FROM animal_data
        WHERE date >= ?
        ORDER BY date DESC
    """
    
    df_all = pd.read_sql(
        query, con, 
        params=[thirty_days_ago, first_this_month, first_prev_month, first_this_month_bound, first_prev_month]
    )
    con.close()

    # Split dataframes efficiently
    df_last30 = df_all[df_all['period_30'] == 'last_30'].drop(['period_30', 'period_month'], axis=1)
    df_cur = df_all[df_all['period_month'] == 'current_month'].drop(['period_30', 'period_month'], axis=1)
    df_prev = df_all[df_all['period_month'] == 'previous_month'].drop(['period_30', 'period_month'], axis=1)

    # Calculate summary statistics efficiently
    summary_stats = {
        'last_30_total': df_last30['mouth_disease_count'].sum() + df_last30['lumpy_skin_count'].sum(),
        'current_month_total': df_cur['mouth_disease_count'].sum() + df_cur['lumpy_skin_count'].sum(),
        'previous_month_total': df_prev['mouth_disease_count'].sum() + df_prev['lumpy_skin_count'].sum(),
        'avg_bcs_last30': df_last30['BCS'].mean() if not df_last30.empty else 0,
        'avg_bcs_current': df_cur['BCS'].mean() if not df_cur.empty else 0,
        'avg_bcs_previous': df_prev['BCS'].mean() if not df_prev.empty else 0,
    }
    
    # Calculate trends
    month_change = summary_stats['current_month_total'] - summary_stats['previous_month_total']
    change_percent = (month_change / summary_stats['previous_month_total'] * 100) if summary_stats['previous_month_total'] > 0 else 0
    
    # Create focused content for AI (no markdown formatting)
    content = f"""Analyze the veterinary health data below and provide a professional report with clear insights and recommendations.

KEY METRICS:
- Total cases last 30 days: {summary_stats['last_30_total']}
- Current month total: {summary_stats['current_month_total']}
- Previous month total: {summary_stats['previous_month_total']}
- Month change: {month_change:+d} cases ({change_percent:+.1f}%)
- Average BCS last 30 days: {summary_stats['avg_bcs_last30']:.1f}
- Average BCS current month: {summary_stats['avg_bcs_current']:.1f}
- Average BCS previous month: {summary_stats['avg_bcs_previous']:.1f}

Provide analysis in this structure:
1. Executive Summary
2. Key Findings
3. Risk Assessment
4. Recommendations
5. Monitoring Plan

Keep response concise and professional. Give response without any markdown and give response in the provided structure ."""

    return {
        "messages": [{"role": "system", "content": content}],
        "df_last30": df_last30,
        "df_cur": df_cur,
        "df_prev": df_prev,
    }


def ai_recommendation(state: ChatState) -> ChatState:
    """Generate AI recommendations with proper PDF formatting - FIXED"""
    messages = state["messages"]
    response = llm.invoke(messages)
    assistant_text = response.content
    
    # Create enhanced PDF with proper page management
    out_dir = Path(get_data_dir())
    out_dir.mkdir(exist_ok=True)
    
    pdf = EnhancedPDF()
    pdf.add_page()
    
    # Convert markdown to formatted PDF (this will handle the formatting properly)
    convert_markdown_to_pdf(assistant_text, pdf)
    
    text_page_path = out_dir / "page_text.pdf"
    pdf.output(str(text_page_path))
    
    return {
        "messages": [{"role": "assistant", "content": assistant_text}],
        "text_page": str(text_page_path),
    }


def make_visuals(state: ChatState) -> ChatState:
    """Generate visualizations with optimized performance"""
    out_dir = Path(get_data_dir())
    out_dir.mkdir(exist_ok=True)
    
    # Create figure with optimized DPI for performance
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Veterinary Health Dashboard', fontsize=20, fontweight='bold', y=0.98)
    
    # 1) Month-over-month comparison
    cur_totals = state["df_cur"][["mouth_disease_count", "lumpy_skin_count"]].sum()
    prev_totals = state["df_prev"][["mouth_disease_count", "lumpy_skin_count"]].sum()
    
    categories = ['Mouth Disease', 'Lumpy Skin']
    current_vals = [cur_totals["mouth_disease_count"], cur_totals["lumpy_skin_count"]]
    previous_vals = [prev_totals["mouth_disease_count"], prev_totals["lumpy_skin_count"]]
    
    x = range(len(categories))
    width = 0.35
    
    bars1 = ax1.bar([i - width/2 for i in x], current_vals, width, label='Current Month', 
                color='#3498db', alpha=0.8)
    bars2 = ax1.bar([i + width/2 for i in x], previous_vals, width, label='Previous Month', 
                color='#e74c3c', alpha=0.8)
    
    ax1.set_ylabel('Cases', fontweight='bold')
    ax1.set_title('Month-over-Month Comparison', fontweight='bold', pad=20)
    ax1.set_xticks(x)
    ax1.set_xticklabels(categories)
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{int(height)}', ha='center', va='bottom', fontweight='bold')
    for bar in bars2:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{int(height)}', ha='center', va='bottom', fontweight='bold')
    
    # 2) Trend analysis (optimized)
    df30 = state["df_last30"].copy()
    if not df30.empty:
        df30["date"] = pd.to_datetime(df30["date"])
        df30["total_cases"] = df30["mouth_disease_count"] + df30["lumpy_skin_count"]
        df30_grouped = df30.groupby("date").agg({
            "total_cases": "sum",
            "mouth_disease_count": "sum",
            "lumpy_skin_count": "sum"
        }).sort_index()
        
        ax2.plot(df30_grouped.index, df30_grouped["total_cases"], marker='o', linewidth=2, 
                markersize=4, color='#2ecc71', label='Total Cases')
        ax2.plot(df30_grouped.index, df30_grouped["mouth_disease_count"], marker='s', linewidth=1, 
                markersize=3, color='#f39c12', label='Mouth Disease', alpha=0.7)
        ax2.plot(df30_grouped.index, df30_grouped["lumpy_skin_count"], marker='^', linewidth=1, 
                markersize=3, color='#9b59b6', label='Lumpy Skin', alpha=0.7)
        
        ax2.set_xlabel('Date', fontweight='bold')
        ax2.set_ylabel('Cases', fontweight='bold')
        ax2.set_title('30-Day Trend', fontweight='bold', pad=20)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(axis='x', rotation=45)
    
    # 3) BCS analysis
    if not df30.empty:
        bcs_data = df30.groupby("date")["BCS"].mean().sort_index()
        ax3.plot(bcs_data.index, bcs_data.values, marker='o', linewidth=2, 
                markersize=4, color='#e67e22')
        ax3.axhline(y=3, color='red', linestyle='--', alpha=0.7, label='Critical (3)')
        ax3.axhline(y=5, color='green', linestyle='--', alpha=0.7, label='Good (5)')
        ax3.set_xlabel('Date', fontweight='bold')
        ax3.set_ylabel('Avg BCS', fontweight='bold')
        ax3.set_title('Body Condition Score', fontweight='bold', pad=20)
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        ax3.tick_params(axis='x', rotation=45)
    
    # 4) Distribution
    total_mouth = state["df_last30"]["mouth_disease_count"].sum()
    total_lumpy = state["df_last30"]["lumpy_skin_count"].sum()
    
    if total_mouth > 0 or total_lumpy > 0:
        sizes = [total_mouth, total_lumpy]
        labels = ['Mouth Disease', 'Lumpy Skin']
        colors = ['#3498db', '#e74c3c']
        
        wedges, texts, autotexts = ax4.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                          startangle=90, textprops={'fontweight': 'bold'})
        ax4.set_title('Disease Distribution', fontweight='bold', pad=20)
    
    plt.tight_layout()
    chart_path = out_dir / "dashboard.png"
    plt.savefig(chart_path, dpi=200, bbox_inches='tight')  # Reduced DPI for performance
    plt.close()
    
    # Create PDF with proper alignment
    pdf = EnhancedPDF()
    pdf.add_page()
    
    # Add title
    pdf.set_font('DejaVu', 'B', 18)
    pdf.set_text_color(41, 128, 185)
    pdf.cell(0, 15, 'Visual Analytics Dashboard', 0, 1, 'C')
    pdf.ln(6)
    
    # Add image with proper positioning
    pdf.image(str(chart_path), x=10, y=55, w=190)
    
    # Add statistics at bottom with proper spacing
    pdf.set_y(245)
    pdf.add_subtitle("Summary Statistics")
    
    total_cases = state["df_last30"]["mouth_disease_count"].sum() + state["df_last30"]["lumpy_skin_count"].sum()
    avg_bcs = state["df_last30"]["BCS"].mean() if not state["df_last30"].empty else 0
    
    pdf.add_paragraph(f"Total Cases (Last 30 Days): {total_cases}")
    pdf.add_paragraph(f"Average BCS: {avg_bcs:.2f}")
    pdf.add_paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    viz_pdf_path = out_dir / "page_visuals.pdf"
    pdf.output(str(viz_pdf_path))
    
    return {"viz_page": str(viz_pdf_path)}


def assemble_report(state: ChatState) -> ChatState:
    """Assemble report with proper page alignment - FIXED"""
    merger = PdfMerger()
    
    # Add pages without gaps
    merger.append(state["viz_page"])
    merger.append(state["text_page"])
    
    out_dir = Path(get_data_dir())
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    final_path = out_dir / f"vet_health_report_{timestamp}.pdf"
    web_path = f"/report_assets/{final_path.name}"
    merger.write(str(final_path))
    print(web_path)
    # merger.write(str(final_path))
    merger.close()
    
    return {"final_pdf": str(web_path)}


builder = StateGraph(ChatState)

builder.add_node("get_data", get_analysis_data)
builder.add_node("visualize", make_visuals)
builder.add_node("recommend", ai_recommendation)
builder.add_node("assemble", assemble_report)

builder.set_entry_point("get_data")
builder.add_edge("get_data", "visualize")
builder.add_edge("visualize", "recommend")
builder.add_edge("recommend", "assemble")
builder.add_edge("assemble", END)

graph = builder.compile()


# if __name__ == "__main__":
#     state_in = {
#         "messages": [
#             {"role": "user",
#             "content": "Generate a veterinary health report."}
#         ]
#     }
    
#     print("🚀 Generating veterinary health report...")
#     start_time = datetime.now()
#     state_out = graph.invoke(state_in)
#     end_time = datetime.now()
    
#     print(f"Report generated in {(end_time - start_time).total_seconds():.1f} seconds")
#     print(f"Report saved to: {state_out['final_pdf']}")
