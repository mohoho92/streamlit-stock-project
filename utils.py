"""
utils.py
- 숫자 및 금원 포맷팅 헬퍼 함수
- Plotly 그래프 생성 (이중 축 차트, 일별 순매수 막대 그래프)
- 모바일 최적화 CSS 스타일 주입 함수
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

def inject_custom_css():
    """모바일 최적화 및 커스텀 CSS 주입"""
    css = """
    <style>
    /* 전체 페이지 패딩 및 마진 조정 (모바일 가독성 증대) */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
    }
    
    /* 상단 헤더 타이틀 스타일 */
    .app-header {
        text-align: center;
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: #ffffff;
        padding: 1rem 0.5rem;
        border-radius: 12px;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .app-header h1 {
        font-size: 1.4rem !important;
        font-weight: 700 !important;
        margin: 0 !important;
        color: #f8fafc !important;
    }
    .app-header p {
        font-size: 0.85rem !important;
        margin-top: 0.3rem !important;
        color: #94a3b8 !important;
    }

    /* 수급 메트릭 카드 스타일 */
    .metric-card-container {
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        gap: 8px;
        margin-bottom: 1rem;
    }
    .metric-card {
        flex: 1;
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 10px 8px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    @media (prefers-color-scheme: dark) {
        .metric-card {
            background-color: #1e293b;
            border-color: #334155;
        }
    }
    .metric-title {
        font-size: 0.75rem;
        font-weight: 600;
        color: #64748b;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 0.95rem;
        font-weight: 700;
    }
    .val-plus {
        color: #e53935 !important;
    }
    .val-minus {
        color: #1e88e5 !important;
    }
    .val-zero {
        color: #64748b !important;
    }

    /* 필터 영역 모바일 최적화 */
    div[data-baseweb="select"] {
        font-size: 0.9rem !important;
    }
    
    /* Plotly 차트 모바일 터치 패딩 */
    .js-plotly-plot .plotly .modebar {
        orientation: h !important;
        top: 0px !important;
        right: 0px !important;
    }
    
    /* 데이터 테이블 가로 스크롤 및 폰트 */
    .stDataFrame {
        font-size: 0.85rem !important;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def format_krw(val_in_krw: float, show_unit: bool = True) -> str:
    """
    금액(원 단위)을 억원 또는 백만원 단위 문자열로 변환
    - 1억 이상: 억원 단위 (예: +1,234 억)
    - 1억 미만: 백만원 단위 (예: +45 백만)
    """
    if pd.isna(val_in_krw) or val_in_krw == 0:
        return "0" + (" 억원" if show_unit else "")
        
    abs_val = abs(val_in_krw)
    sign = "+" if val_in_krw > 0 else "-"
    
    if abs_val >= 1e8: # 1억원 이상
        eon = abs_val / 1e8
        if eon >= 100:
            formatted = f"{sign}{eon:,.0f}"
        else:
            formatted = f"{sign}{eon:,.1f}"
        unit = " 억원" if show_unit else ""
        return formatted + unit
    else: # 1억원 미만
        baekman = abs_val / 1e6
        formatted = f"{sign}{baekman:,.0f}"
        unit = " 백만" if show_unit else ""
        return formatted + unit

def get_color_class(val: float) -> str:
    """양수/음수/zero에 따른 CSS 클래스명 반환"""
    if pd.isna(val) or val == 0:
        return "val-zero"
    return "val-plus" if val > 0 else "val-minus"

# 투자자 종류별 시각화 색상 정의 (한국 증권 시장 표준 톤)
INVESTOR_COLORS = {
    "외국인": "#e53935",   # 빨강
    "기관": "#1e88e5",     # 파랑
    "개인": "#fb8c00",     # 주황
    "연기금": "#8e24aa",   # 보라
    "금융투자": "#03a9f4", # 하늘색
    "투신": "#4caf50",     # 초록
}

def create_dual_axis_chart(df: pd.DataFrame, stock_name: str, selected_investors: list, chart_type: str = "Candlestick"):
    """
    [이중 축 Plotly 차트 생성]
    - Primary Y-Axis (좌측): 주가 (Candlestick 또는 Line)
    - Secondary Y-Axis (우측): 선택한 투자자들의 누적 순매수 금액 (억원)
    """
    fig = make_subplots(
        specs=[[{"secondary_y": True}]],
        shared_xaxes=True
    )
    
    # 1. 주가 차트 (좌측 Y축)
    if chart_type == "Candlestick" and all(col in df.columns for col in ['시가', '고가', '저가', '종가']):
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['시가'],
                high=df['고가'],
                low=df['저가'],
                close=df['종가'],
                name="주가 (OHLC)",
                increasing_line_color='#e53935',
                decreasing_line_color='#1e88e5',
                showlegend=True
            ),
            secondary_y=False
        )
    else:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['종가'],
                name="종가",
                line=dict(color='#2b2b2b', width=2),
                showlegend=True
            ),
            secondary_y=False
        )
        
    # 2. 투자자별 누적 순매수 라인 (우측 Y축)
    for inv in selected_investors:
        cum_col = f"{inv}_누적"
        if cum_col in df.columns:
            # 억 원 단위 변환
            y_data_eon = df[cum_col] / 1e8
            color = INVESTOR_COLORS.get(inv, "#607d8b")
            
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=y_data_eon,
                    name=f"{inv} (누적)",
                    line=dict(color=color, width=2.5),
                    hovertemplate=f"<b>{inv} 누적</b>: %{{y:,.1f}} 억원<extra></extra>"
                ),
                secondary_y=True
            )
            
    # 레이아웃 설정 (모바일 최적화)
    fig.update_layout(
        title=dict(
            text=f"<b>{stock_name}</b> 주가 vs 누적 수급 동향",
            font=dict(size=15)
        ),
        margin=dict(l=10, r=10, t=40, b=10),
        height=420,
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10)
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(245,247,250,0.5)',
        xaxis=dict(
            rangeslider=dict(visible=False),
            type='date',
            showgrid=True,
            gridcolor='#e2e8f0'
        )
    )
    
    fig.update_yaxes(
        title_text="주가 (원)", 
        secondary_y=False,
        showgrid=True,
        gridcolor='#e2e8f0',
        tickformat=","
    )
    fig.update_yaxes(
        title_text="누적 순매수 (억원)", 
        secondary_y=True,
        showgrid=False
    )
    
    return fig

def create_daily_bar_chart(df: pd.DataFrame, selected_investors: list):
    """
    [일별 투자자별 순매수 막대 그래프]
    """
    fig = go.Figure()
    
    for inv in selected_investors:
        if inv in df.columns:
            # 억 원 단위 변환
            y_data = df[inv] / 1e8
            color = INVESTOR_COLORS.get(inv, "#607d8b")
            
            fig.add_trace(
                go.Bar(
                    x=df.index,
                    y=y_data,
                    name=inv,
                    marker_color=color,
                    hovertemplate=f"<b>{inv} 순매수</b>: %{{y:,.1f}} 억원<extra></extra>"
                )
            )
            
    fig.update_layout(
        title=dict(
            text="<b>일별 투자자별 순매수 금액 (억원)</b>",
            font=dict(size=14)
        ),
        barmode='group',
        margin=dict(l=10, r=10, t=40, b=10),
        height=320,
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10)
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(245,247,250,0.5)',
        xaxis=dict(
            showgrid=True,
            gridcolor='#e2e8f0'
        ),
        yaxis=dict(
            title="순매수 금액 (억원)",
            showgrid=True,
            gridcolor='#e2e8f0'
        )
    )
    
    return fig
