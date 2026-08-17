"""
app.py
- 국내 주식 투자자별 수급동향 모바일 최적화 Streamlit 대시보드 메인 애플리케이션
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

from data_loader import (
    get_stock_list,
    get_date_range,
    fetch_market_summary,
    fetch_stock_trading_data
)
from utils import (
    inject_custom_css,
    format_krw,
    get_color_class,
    create_dual_axis_chart,
    create_daily_bar_chart
)

# 1. 페이지 세팅 (모바일 최적화: wide 레이아웃 & 사이드바 접음)
st.set_page_config(
    page_title="국내 주식 수급동향 대시보드",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. 커스텀 CSS 주입
inject_custom_css()

# 3. 상단 타이틀 헤더
st.markdown("""
<div class="app-header">
    <h1>📈 국내 주식 수급동향 대시보드</h1>
    <p>외국인 · 기관 · 개인 · 연기금 실시간 수급 및 주가 추이 분석</p>
</div>
""", unsafe_allow_html=True)

# 4. 시장 전체 수급 요약 메트릭 카드
market_summary = fetch_market_summary()

kospi = market_summary.get("KOSPI", {})
kosdaq = market_summary.get("KOSDAQ", {})

st.markdown("##### 🏛️ 시장 전체 수급 요약 (최근)")

m_col1, m_col2 = st.columns(2)

with m_col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">KOSPI 수급 요약</div>
        <div style="display:flex; justify-content:space-around; margin-top:6px;">
            <div>
                <span style="font-size:0.75rem; color:#64748b;">개인</span><br/>
                <span class="metric-value {get_color_class(kospi.get('개인', 0))}">{format_krw(kospi.get('개인', 0))}</span>
            </div>
            <div>
                <span style="font-size:0.75rem; color:#64748b;">외국인</span><br/>
                <span class="metric-value {get_color_class(kospi.get('외국인', 0))}">{format_krw(kospi.get('외국인', 0))}</span>
            </div>
            <div>
                <span style="font-size:0.75rem; color:#64748b;">기관</span><br/>
                <span class="metric-value {get_color_class(kospi.get('기관', 0))}">{format_krw(kospi.get('기관', 0))}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with m_col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">KOSDAQ 수급 요약</div>
        <div style="display:flex; justify-content:space-around; margin-top:6px;">
            <div>
                <span style="font-size:0.75rem; color:#64748b;">개인</span><br/>
                <span class="metric-value {get_color_class(kosdaq.get('개인', 0))}">{format_krw(kosdaq.get('개인', 0))}</span>
            </div>
            <div>
                <span style="font-size:0.75rem; color:#64748b;">외국인</span><br/>
                <span class="metric-value {get_color_class(kosdaq.get('외국인', 0))}">{format_krw(kosdaq.get('외국인', 0))}</span>
            </div>
            <div>
                <span style="font-size:0.75rem; color:#64748b;">기관</span><br/>
                <span class="metric-value {get_color_class(kosdaq.get('기관', 0))}">{format_krw(kosdaq.get('기관', 0))}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='margin: 1rem 0; border: 0; border-top: 1px solid #e2e8f0;'/>", unsafe_allow_html=True)

# 5. 종목 검색 및 필터 옵션 영역
st.markdown("##### 🔍 종목 및 기간 선택")

popular_stocks = get_stock_list()
stock_options = [f"{name} ({code})" for code, name in popular_stocks.items()]
stock_options.append("직접 종목코드 입력...")

f_col1, f_col2, f_col3 = st.columns([2, 1.2, 1])

with f_col1:
    selected_option = st.selectbox(
        "종목 선택",
        options=stock_options,
        index=0,
        label_visibility="collapsed"
    )
    
    if selected_option == "직접 종목코드 입력...":
        custom_code = st.text_input("6자리 종목코드 입력 (예: 005930)", value="005930")
        ticker = custom_code.strip()
        stock_name = f"종목({ticker})"
    else:
        # Extract code and name
        stock_name = selected_option.split(" (")[0]
        ticker = selected_option.split("(")[1].replace(")", "").strip()

with f_col2:
    period_selected = st.selectbox(
        "조회 기간",
        options=["1주일", "1개월", "3개월", "6개월", "1년"],
        index=1,
        label_visibility="collapsed"
    )

with f_col3:
    chart_style = st.selectbox(
        "차트 형태",
        options=["Candlestick", "Line"],
        index=0,
        label_visibility="collapsed"
    )

# 투자자 종류 선택 멀티 칩
selected_investors = st.multiselect(
    "차트 표시 투자자 선택",
    options=["외국인", "기관", "개인", "연기금", "금융투자", "투신"],
    default=["외국인", "기관", "개인", "연기금"]
)

if not selected_investors:
    selected_investors = ["외국인", "기관"]

# 6. 데이터 조회 및 가공
start_date, end_date = get_date_range(period_selected)

with st.spinner(f"{stock_name}({ticker}) 수급 데이터를 로딩 중입니다..."):
    df_stock = fetch_stock_trading_data(ticker, stock_name, start_date, end_date)

if df_stock.empty:
    st.error("해당 기간의 주가 및 수급 데이터를 불러올 수 없습니다.")
else:
    # 7. 선택 종목 요약 메트릭
    latest_row = df_stock.iloc[-1]
    latest_close = int(latest_row['종가']) if '종가' in latest_row else 0
    latest_change = latest_row['등락률'] if '등락률' in latest_row else 0.0
    
    # 선택 기간 내 누적 순매수 합계
    cum_foreign = df_stock['외국인'].sum() if '외국인' in df_stock.columns else 0
    cum_inst = df_stock['기관'].sum() if '기관' in df_stock.columns else 0
    cum_indiv = df_stock['개인'].sum() if '개인' in df_stock.columns else 0
    cum_pension = df_stock['연기금'].sum() if '연기금' in df_stock.columns else 0

    st.markdown(f"#### 📌 {stock_name} ({ticker}) - {period_selected} 수급 현황")
    
    s_col1, s_col2, s_col3, s_col4 = st.columns(4)
    with s_col1:
        st.metric(
            label="현재가 (종가)",
            value=f"{latest_close:,} 원",
            delta=f"{latest_change:+.2f}%"
        )
    with s_col2:
        st.metric(
            label=f"{period_selected} 외국인 누적",
            value=format_krw(cum_foreign),
            delta=None
        )
    with s_col3:
        st.metric(
            label=f"{period_selected} 기관 누적",
            value=format_krw(cum_inst),
            delta=None
        )
    with s_col4:
        st.metric(
            label=f"{period_selected} 개인 누적",
            value=format_krw(cum_indiv),
            delta=None
        )

    # 8. 차트 탭 영역
    tab1, tab2 = st.tabs(["📊 주가 & 누적 수급 추이", "📉 일별 순매수 막대 그래프"])
    
    with tab1:
        fig_dual = create_dual_axis_chart(df_stock, stock_name, selected_investors, chart_style)
        st.plotly_chart(fig_dual, use_container_width=True, config={"displayModeBar": False})
        
    with tab2:
        fig_bar = create_daily_bar_chart(df_stock, selected_investors)
        st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

    # 9. 일별 상세 수급 데이터 테이블
    st.markdown("##### 📋 일별 상세 수급 데이터")
    
    # 데이터프레임 가공 (최신순 내림차순 정렬)
    df_table = df_stock.sort_index(ascending=False).copy()
    
    # 날짜 포맷
    df_table['날짜'] = df_table.index.strftime("%Y-%m-%d")
    
    # 표시용 컬럼 정리
    table_cols = ['날짜', '종가', '등락률', '외국인', '기관', '개인', '연기금', '금융투자', '투신', '거래량']
    existing_cols = [c for c in table_cols if c in df_table.columns]
    df_table_display = df_table[existing_cols].copy()
    
    # 수치 포맷팅 (원 -> 억원)
    formatted_df = df_table_display.copy()
    money_cols = ['외국인', '기관', '개인', '연기금', '금융투자', '투신']
    
    for col in money_cols:
        if col in formatted_df.columns:
            formatted_df[col] = formatted_df[col].apply(lambda x: format_krw(x, show_unit=False))
            
    if '종가' in formatted_df.columns:
        formatted_df['종가'] = formatted_df['종가'].apply(lambda x: f"{int(x):,}")
    if '등락률' in formatted_df.columns:
        formatted_df['등락률'] = formatted_df['등락률'].apply(lambda x: f"{x:+.2f}%")
    if '거래량' in formatted_df.columns:
        formatted_df['거래량'] = formatted_df['거래량'].apply(lambda x: f"{int(x):,}")

    st.dataframe(
        formatted_df,
        use_container_width=True,
        height=300,
        hide_index=True
    )

    # 10. CSV 다운로드 버튼
    csv_data = df_table_display.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label=f"📥 {stock_name} 상세 수급 데이터 CSV 다운로드",
        data=csv_data,
        file_name=f"{stock_name}_{ticker}_supply_demand_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

# 하단 푸터
st.markdown("""
<div style="text-align: center; color: #94a3b8; font-size: 0.75rem; margin-top: 2rem;">
    본 서비스는 한국거래소(KRX) 공시 데이터 기반 정보 제공 목적으로 제작되었으며, 투자 권유나 추천이 아닙니다.<br/>
    Data Source: PyKRX / FinanceDataReader | Built with Streamlit & Plotly
</div>
""", unsafe_allow_html=True)
