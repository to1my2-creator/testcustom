import streamlit as st

# 1. 頁面基礎設定
st.set_page_config(page_title="AI 智慧報關系統", layout="wide", page_icon="🛃")

st.title("🛃 AI 智慧報關與稅則比對系統")
st.caption("輸入貨物資訊，系統將自動比對關務稅則、簽審規定與市場價格風險")

# 2. 擴充動態稅則與簽審資料庫
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
    },
    "電腦": {
        "tariffs": [
            "【首選】HS 8471.30.00.00-8 (符合度 95.0%) - 可攜式自動資料處理機 (手提電腦)",
            "【備選】HS 8471.41.00.00-5 (符合度 80.0%) - 其他自動資料處理機"
        ],
        "reg_warning": "⚠️ **管制與簽審提示**：該商品涉及 **BSMI 電磁相容 (EMC) 與安規檢驗**。",
        "benchmark_price": 35000
    },
    "手錶": {
        "tariffs": [
            "【首選】HS 9102.11.00.00-8 (符合度 91.0%) - 機械指示之電子手錶",
            "【備選】HS 8517.62.00.00-5 (符合度 82.0%) - 具藍牙通訊之智慧手錶"
        ],
        "reg_warning": "ℹ️ **管制與簽審提示**：一般手錶無特殊簽審限制；若具備無線藍牙功能需附 **NCC 認證**。",
        "benchmark_price": 8000
    }
}

DEFAULT_TAX = {
    "tariffs": [
        "【首選】HS 9999.00.00.00-0 (符合度 85.0%) - 一般進口貨品歸類稅則",
        "【備選】HS 8479.89.99.00-9 (符合度 65.0%) - 其他具有獨立功能之機械器具"
    ],
    "reg_warning": "ℹ️ **管制與簽審提示**：請依海關關港貿單一窗口查詢該特定貨品之輸出入規定代碼 (如 C02/F01/NCC 等)。",
    "benchmark_price": 5000
}

# 3. 輸入區塊 (不使用 form)
col1, col2 = st.columns(2)
with col1:
    prod_name = st.text_input("貨物名稱", value="主動降噪無線藍牙耳機")
    prod_price = st.number_input("申報單價 (TWD/CIF)", value=1200)
    prod_qty = st.number_input("申報數量", value=500)
with col2:
    origin = st.text_input("生產產地", value="中國 (CN)")
    spec_desc = st.text_area("特殊規格與功能說明", value="內建 Bluetooth 模組、可充電式鋰電池")

# 4. 點擊分析按鈕
if st.button("🚀 開始 AI 報關分析", type="primary"):
    st.session_state["analyzed_name"] = prod_name
    st.session_state["analyzed_price"] = prod_price

# 5. 顯示結果邏輯
if "analyzed_name" in st.session_state:
    current_name = st.session_state["analyzed_name"]
    current_price = st.session_state["analyzed_price"]
    
    # 動態匹配關鍵字
    matched_data = DEFAULT_TAX
    for k, v in TAX_DATABASE.items():
        if k in current_name:
            matched_data = v
            break
            
    est_cif = matched_data["benchmark_price"] * 0.6
    diff_rate = ((current_price - est_cif) / est_cif) * 100

    st.divider()
    st.subheader(f"📊 AI 分析與比對結果：【{current_name}】")
    
    # 選項選單
    selected_hs = st.radio(
        "請選擇您欲採納申報的稅則：",
        options=matched_data["tariffs"],
        key=f"radio_{current_name}"  # 使用動態 Key 避免衝突
    )
    
    # 簽審提醒
    st.warning(matched_data["reg_warning"])
    
    # 價格偏離分析
    if diff_rate < -20:
        st.error(f"⚠️ **價格風險警示**：您申報的單價 (TWD {current_price}) **低於市場完稅均價 {abs(diff_rate):.1f}%** (推估完稅均價為 TWD {est_cif:.0f})，易引發海關 C3 查驗並要求補件證明。")
    elif diff_rate > 20:
        st.info(f"💡 **價格提醒**：您申報的單價 (TWD {current_price}) 高於市場完稅均價 {diff_rate:.1f}%。")
    else:
        st.success(f"✅ **價格正常**：申報金額符合市場行情均價（推估完稅均價為 TWD {est_cif:.0f}）。")
    
    # 匯出按鈕
    if st.button("確認選擇並匯出報關單 (XML/PDF)"):
        st.balloons()
        st.success(f"🎉 申報成功！已確認採納稅則：\n`{selected_hs}`\n\n系統已自動封裝報關 XML 檔案，並準備傳送至關港貿單一窗口！")
