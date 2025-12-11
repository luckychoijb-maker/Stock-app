import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime, timedelta

# 페이지 설정
st.set_page_config(page_title="월간 주식 랭킹", layout="wide")

# --- 데이터 수집 함수 (캐싱 적용) ---
@st.cache_data
def get_stock_data():
    progress_text = "데이터 수집 중... 잠시만 기다려주세요."
    my_bar = st.progress(0, text=progress_text)

    df_kospi = fdr.StockListing('KOSPI')
    top100 = df_kospi[df_kospi['Marcap'] > 0].sort_values('Marcap', ascending=False).head(100)

    today = datetime.now()
    first_day_this_month = today.replace(day=1)
    last_day_last_month = first_day_this_month - timedelta(days=1)
    first_day_last_month = last_day_last_month.replace(day=1)

    str_start = first_day_last_month.strftime('%Y-%m-%d')
    str_end = last_day_last_month.strftime('%Y-%m-%d')
    str_today = today.strftime('%Y-%m-%d')

    results = []
    total = len(top100)
    count = 0

    for idx, row in top100.iterrows():
        code = row['Code']
        name = row['Name']
        count += 1
        my_bar.progress(count / total, text=f"[{count}/{total}] {name} 분석 중...")

        try:
            df_price = fdr.DataReader(code, str_start, str_today)
            if len(df_price) > 0:
                df_last_month = df_price.loc[str_start:str_end]
                if len(df_last_month) > 0:
                    start_p = df_last_month.iloc[0]['Open']
                    end_p = df_last_month.iloc[-1]['Close']
                    cur_p = df_price.iloc[-1]['Close']

                    if start_p > 0:
                        rate = (end_p - start_p) / start_p * 100
                        results.append({
                            '종목명': name,
                            '수익률(%)': round(rate, 2),
                            '지난달_시가': f"{start_p:,}원",
                            '지난달_종가': f"{end_p:,}원",
                            '현재가': f"{cur_p:,}원"
                        })
        except:
            continue

    my_bar.empty()
    return pd.DataFrame(results), str_start, str_end

# --- 화면 구성 ---
st.title("📈 월간 KOSPI 시총 100위 등락률")

if st.button("데이터 불러오기"):
    with st.spinner('분석 중...'):
        df_result, start, end = get_stock_data()

    st.success(f"기준: {start} ~ {end}")
    col1, col2 = st.columns(2)
    view_cols = ['종목명', '수익률(%)', '지난달_시가', '지난달_종가', '현재가']

    with col1:
        st.subheader("🔥 급등 Top 10")
        st.dataframe(df_result.sort_values(by='수익률(%)', ascending=False).head(10)[view_cols], hide_index=True)

    with col2:
        st.subheader("💧 급락 Top 10")
        st.dataframe(df_result.sort_values(by='수익률(%)', ascending=True).head(10)[view_cols], hide_index=True)
