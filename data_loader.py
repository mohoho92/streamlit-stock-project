"""
data_loader.py
- 한국 주식 시장 수급 데이터 및 주가 데이터 수집 및 캐싱 로직
- PyKRX / FinanceDataReader 연동 및 API 오류 시 모의(Mock) 데이터 생성 Fallback 제공
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st

# 주요 인기 종목 리스트 (기본 제공 및 커스텀 검색 가능)
POPULAR_STOCKS = {
    "005930": "삼성전자",
    "000660": "SK하이닉스",
    "373220": "LG에너지솔루션",
    "207940": "삼성바이오로직스",
    "005380": "현대차",
    "000270": "기아",
    "035420": "NAVER",
    "035720": "카카오",
    "068270": "셀트리온",
    "005490": "POSCO홀딩스",
    "247540": "에코프로비엠",
    "086520": "에코프로",
    "196170": "알테오젠",
    "028300": "HLB"
}

def get_stock_list():
    """주요 종목 dict 반환"""
    return POPULAR_STOCKS

def get_date_range(period_str: str):
    """
    기간 선택 문자열(1주일, 1개월, 3개월, 6개월, 1년)에 따른 시작일, 종료일(YYYYMMDD) 계산
    """
    today = datetime.today()
    
    # 주말 처리: 일요일(6)이면 금요일로, 토요일(5)이면 금요일로
    if today.weekday() == 6:
        end_dt = today - timedelta(days=2)
    elif today.weekday() == 5:
        end_dt = today - timedelta(days=1)
    else:
        end_dt = today
        
    if period_str == "1주일":
        start_dt = end_dt - timedelta(days=7)
    elif period_str == "1개월":
        start_dt = end_dt - timedelta(days=30)
    elif period_str == "3개월":
        start_dt = end_dt - timedelta(days=90)
    elif period_str == "6개월":
        start_dt = end_dt - timedelta(days=180)
    elif period_str == "1년":
        start_dt = end_dt - timedelta(days=365)
    else:
        start_dt = end_dt - timedelta(days=30)
        
    start_str = start_dt.strftime("%Y%m%d")
    end_str = end_dt.strftime("%Y%m%d")
    return start_str, end_str

def _generate_mock_market_summary():
    """모의 전체 시장 수급 요약 데이터 (단위: 원)"""
    return {
        "KOSPI": {
            "개인": 1250 * 1e8,       # +1250억
            "외국인": -840 * 1e8,      # -840억
            "기관": -390 * 1e8,       # -390억
        },
        "KOSDAQ": {
            "개인": -310 * 1e8,       # -310억
            "외국인": 450 * 1e8,       # +450억
            "기관": -120 * 1e8,       # -120억
        }
    }

@st.cache_data(ttl=1800)
def fetch_market_summary():
    """
    KOSPI / KOSDAQ 최근 영업일 전체 투자자별 순매수 요약 데이터 조회
    """
    try:
        from pykrx import stock
        today_str = datetime.today().strftime("%Y%m%d")
        start_str = (datetime.today() - timedelta(days=5)).strftime("%Y%m%d")
        
        # KOSPI
        df_kospi = stock.get_market_net_purchases_of_equities_by_ticker(start_str, today_str, "KOSPI")
        # KOSDAQ
        df_kosdaq = stock.get_market_net_purchases_of_equities_by_ticker(start_str, today_str, "KOSDAQ")
        
        if df_kospi.empty or df_kosdaq.empty:
            return _generate_mock_market_summary()
            
        summary = {
            "KOSPI": {
                "개인": float(df_kospi["개인"].sum() if "개인" in df_kospi.columns else 0),
                "외국인": float(df_kospi["외국인합계"].sum() if "외국인합계" in df_kospi.columns else 0),
                "기관": float(df_kospi["기관합계"].sum() if "기관합계" in df_kospi.columns else 0),
            },
            "KOSDAQ": {
                "개인": float(df_kosdaq["개인"].sum() if "개인" in df_kosdaq.columns else 0),
                "외국인": float(df_kosdaq["외국인합계"].sum() if "외국인합계" in df_kosdaq.columns else 0),
                "기관": float(df_kosdaq["기관합계"].sum() if "기관합계" in df_kosdaq.columns else 0),
            }
        }
        return summary
    except Exception as e:
        print(f"[Warning] PyKRX fetch_market_summary Exception: {e}. Fallback to mock.")
        return _generate_mock_market_summary()

def _generate_mock_stock_data(ticker: str, stock_name: str, start_date: str, end_date: str):
    """
    PyKRX API 호출 실패 시 활용하는 모의(Mock) 주가 및 수급 데이터 생성기
    """
    dates = pd.date_range(start=pd.to_datetime(start_date), end=pd.to_datetime(end_date), freq='B')
    n = len(dates)
    if n == 0:
        dates = pd.date_range(end=datetime.today(), periods=30, freq='B')
        n = len(dates)
        
    np.random.seed(abs(hash(ticker)) % 10000)
    
    # 기본 주가 생성 (랜덤 워크)
    base_price = 70000 if ticker == "005930" else 120000
    returns = np.random.normal(0.0005, 0.018, n)
    price_paths = base_price * np.exp(np.cumsum(returns))
    
    close_prices = np.round(price_paths, -2)
    open_prices = np.round(close_prices * (1 + np.random.normal(0, 0.005, n)), -2)
    high_prices = np.maximum(open_prices, close_prices) + np.round(np.abs(np.random.normal(500, 300, n)), -2)
    low_prices = np.minimum(open_prices, close_prices) - np.round(np.abs(np.random.normal(500, 300, n)), -2)
    volumes = np.random.randint(500000, 5000000, n)
    
    # 순매수 금액 생성 (원 단위) - 보통 십억~백억원 단위
    foreign_net = np.random.normal(20, 150, n) * 1e8
    inst_net = np.random.normal(-10, 100, n) * 1e8
    indiv_net = -(foreign_net + inst_net) + np.random.normal(0, 10, n) * 1e8
    pension_net = np.random.normal(5, 30, n) * 1e8
    fin_invest_net = np.random.normal(-5, 40, n) * 1e8
    trust_net = np.random.normal(0, 25, n) * 1e8
    
    df = pd.DataFrame({
        '시가': open_prices,
        '고가': high_prices,
        '저가': low_prices,
        '종가': close_prices,
        '거래량': volumes,
        '등락률': np.round(np.concatenate([[0], np.diff(close_prices) / close_prices[:-1] * 100]), 2),
        '개인': indiv_net,
        '외국인': foreign_net,
        '기관': inst_net,
        '연기금': pension_net,
        '금융투자': fin_invest_net,
        '투신': trust_net,
    }, index=dates)
    
    df.index.name = '날짜'
    
    # 누적 수급 산출
    df['개인_누적'] = df['개인'].cumsum()
    df['외국인_누적'] = df['외국인'].cumsum()
    df['기관_누적'] = df['기관'].cumsum()
    df['연기금_누적'] = df['연기금'].cumsum()
    df['금융투자_누적'] = df['금융투자'].cumsum()
    df['투신_누적'] = df['투신'].cumsum()
    
    return df

@st.cache_data(ttl=1800)
def fetch_stock_trading_data(ticker: str, stock_name: str, start_date: str, end_date: str):
    """
    특정 종목의 주가(OHLCV) 및 일별 투자자별 순매수 거래대금 데이터 조회
    """
    try:
        from pykrx import stock
        
        # 1. 주가 데이터 조회
        df_ohlcv = stock.get_market_ohlcv_by_date(start_date, end_date, ticker)
        
        # 2. 투자자별 거래대금 (순매수) 데이터 조회
        df_trading = stock.get_market_trading_value_by_date(start_date, end_date, ticker)
        
        if df_ohlcv.empty or df_trading.empty:
            print(f"[Info] Empty PyKRX data returned for {ticker}. Using fallback mock data.")
            return _generate_mock_stock_data(ticker, stock_name, start_date, end_date)
            
        # 데이터 병합 (날짜 인덱스 기준)
        df = pd.merge(df_ohlcv, df_trading, left_index=True, right_index=True, how='inner')
        
        # 컬럼 이름 정제 및 매핑
        col_rename = {
            '외국인합계': '외국인',
            '기관합계': '기관',
            '연기금등': '연기금'
        }
        df = df.rename(columns=col_rename)
        
        # 기본 필수 투자자 컬럼 보장
        for col in ['개인', '외국인', '기관', '연기금', '금융투자', '투신']:
            if col not in df.columns:
                df[col] = 0
                
        # 등락률 계산 (PyKRX가 등락률 컬럼을 제공하는 경우 활용, 없으면 계산)
        if '등락률' not in df.columns and '종가' in df.columns:
            df['등락률'] = df['종가'].pct_change().fillna(0) * 100
            df['등락률'] = df['등락률'].round(2)
            
        # 누적 순매수 금액 산출 (차트용)
        df['개인_누적'] = df['개인'].cumsum()
        df['외국인_누적'] = df['외국인'].cumsum()
        df['기관_누적'] = df['기관'].cumsum()
        df['연기금_누적'] = df['연기금'].cumsum()
        df['금융투자_누적'] = df['금융투자'].cumsum()
        df['투신_누적'] = df['투신'].cumsum()
        
        return df
        
    except Exception as e:
        print(f"[Warning] PyKRX fetch_stock_trading_data error for {ticker}: {e}. Fallback to mock.")
        return _generate_mock_stock_data(ticker, stock_name, start_date, end_date)
