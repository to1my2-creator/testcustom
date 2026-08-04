import streamlit as st
import os

# 1. 頁面基礎設定
st.set_page_config(page_title="AI 智慧報關系統", layout="wide", page_icon="🛃")

st.title("🛃 AI 智慧報關與稅則比對系統")
st.caption("輸入貨物資訊，系統將自動比對關務稅則、簽審規定與市場價格風險")

# 初始化 Session State (記憶狀態)
if "analyzed" not in st.session_state:
    st.session_state.analyzed = False
if "result_data" not in st.session_state:
    st.session_state.result_data = {}

# 2. 簡易動態稅則資料庫 (模擬搜尋邏輯)
TAX_DATABASE = {
    "耳機": {
        "tariffs": [
            "【首選】HS 8518.30.00.00-8 (符合度 94.5%) - 頭戴/塞耳式耳機",
            "【備選】HS 8517.62.00.00-5 (符合度 76.2%) - 其他接收轉換聲音器具"
        ],
        "reg_warning": "⚠️ **管制與簽審提示**：該商品涉及 **NCC 電信管制** 與 **BSMI 鋰電池檢驗**，報關時需備妥相關合格證號。",
        "benchmark_price": 2800
    },
    "電視": {
        "tariffs": [
            "【首選】HS 8528.72.00.00-3 (符合度 92.1%) - 彩色液晶電視機",
            "【備選】HS 8528.52.00.00-0 (符合度 71.0%) - 其他監視器"
        ],
        "reg_warning": "⚠️ **管制與簽審提示**：該商品涉及 **BSMI 商品檢驗** (能源效率與安全規格) 及 **貨物稅 (13%)**。",
        "benchmark_price": 15000
    },
    "手機": {
        "tariffs": [
            "【首選】HS 8517.13.00.00-0 (符合度 98.0%) - 智慧型手機",
            "【備選】HS 8517.18.00.00-5 (符合度 60.0%) - 其他電話機"
        ],
        "reg_warning": "⚠️ **管制與簽審提示**：該商品涉及 **NCC 型式認證**，進口需檢附電信管制射頻器材進口許可證。",
        "benchmark_price": 20000
    }
}

# 3. 輸入表單區塊
with st.form("declaration_form"):
    col1, col2 = st.columns(2)
    with col1:
        prod_name = st.text_input("貨物名稱", "主動降噪無線藍牙耳機")
        prod_price = st.number_input("申報單價 (TWD/CIF)", value=1200)
        prod_qty = st.number_input("申報數量", value=500)
    with col2:
        origin = st.text_input("生產產地", "中國 (CN)")
        spec_desc = st.text_area("特殊規格與功能說明", "內建 Bluetooth 5.3 模組、可充電式鋰電池 (350mAh)")
    
    submit_btn = st.form_submit_button("🚀 開始 AI 報關分析")

# 4. 按下分析按鈕時處理邏輯
if submit_btn:
    st.session_state.analyzed = True
    
    # 判斷輸入關鍵字並選取對應稅則資料
    selected_key = "耳機"
    for k in TAX_DATABASE.keys():
        if k in prod_name:
            selected_key = k
            break
            
    data = TAX_DATABASE[selected_key]
    
    # 計算價格偏離率
    est_cif = data["benchmark_price"] * 0.6
    diff_rate = ((prod_price - est_cif) / est_cif) * 100
    
    # 寫入 Session State
    st.session_state.result_data = {
        "prod_name": prod_name,
        "prod_price": prod_price,
        "tariffs": data["tariffs"],
        "reg_warning": data["reg_warning"],
        "est_cif": est_cif,
        "diff_rate": diff_rate
    }

# 5. 展示分析結果 (基於 Session State，避免按按鈕時刷新不見)
if st.session_state.analyzed:
    res = st.session_state.result_data
    st.divider()
    st.subheader("📊 AI 分析與比對結果")
    
    # 選擇稅則 (需求 1 & 4)
    selected_hs = st.radio(
        "請選擇您欲採納申報的稅則：",
        options=res["tariffs"]
    )
    
    # 簽審規定 (需求 2)
    st.warning(res["reg_warning"])
    
    # 價格偏離度比對 (需求 3)
    if res["diff_rate"] < -20:
        st.error(f"⚠️ **價格風險警示**：您申報的單價 (TWD {res['prod_price']}) **低於市場完稅均價 {abs(res['diff_rate']):.1f}%**，易引發海關 C3 查驗並要求補件證明。")
    elif res["diff_rate"] > 20:
        st.info(f"💡 **價格提醒**：您申報的單價高於市場完稅均價 {res['diff_rate']:.1f}%。")
    else:
        st.success(f"✅ **價格正常**：申報金額符合市場行情均價（推估完稅均價為 TWD {res['est_cif']:.0f}）。")
    
    # 確認匯出按鈕 (需求 4)
    if st.button("確認選擇並匯出報關單 (XML/PDF)"):
        st.balloons()
        st.success(f"🎉 申報成功！已確認採納稅則：\n`{selected_hs}`\n系統已自動封裝報關 XML 檔案。")
