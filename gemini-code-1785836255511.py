import streamlit as st
import openai

st.set_page_config(page_title="AI 智慧報關系統", layout="wide")

st.title("🛃 AI 智慧報關與稅則比對系統")
st.caption("輸入貨物資訊，自動分析建議稅則、簽審規定與市場價格風險")

# 1. 使用者輸入表單
with st.form("declaration_form"):
    col1, col2 = st.columns(2)
    with col1:
        prod_name = st.text_input("貨物名稱", "主動降噪無線藍牙耳機")
        prod_price = st.number_input("申報單價 (TWD/CIF)", value=1200)
        prod_qty = st.number_input("申報數量", value=500)
    with col2:
        origin = st.text_input("生產產地", "中國 (CN)")
        spec_desc = st.text_area("特殊規格與功能說明", "內建 Bluetooth 5.3 模組、可充電式鋰電池 (350mAh)")
    
    submit_btn = st.form_submit_button("開始 AI 報關分析")

# 2. 觸發分析
if submit_btn:
    st.divider()
    st.subheader("📊 AI 分析與比對結果")
    
    # 模擬/實作 API 分析邏輯
    st.success("✅ 稅則檢索完成！")
    
    # 展示建議稅則選單
    selected_hs = st.radio(
        "請選擇您欲採納申報的稅則：",
        options=[
            "【首選】HS 8518.30.00.00-8 (符合度 94.5%) - 頭戴/塞耳式耳機",
            "【備選】HS 8517.62.00.00-5 (符合度 76.2%) - 其他接收轉換聲音器具"
        ]
    )
    
    # 簽審提醒
    st.warning("⚠️ **管制與簽審提示**：該商品涉及 **NCC 電信管制** 與 **BSMI 鋰電池檢驗**，報關時需備妥相關合格證號。")
    
    # 價格風險比對
    est_cif = 2800 * 0.6  # 假設市價 2800
    diff_rate = ((prod_price - est_cif) / est_cif) * 100
    
    st.error(f"⚠️ **價格風險警示**：您申報的金額 (TWD {prod_price}) 低於市場完稅均價 {abs(diff_rate):.1f}%，易引發海關 C3 查驗。")
    
    if st.button("確認選擇並匯出報關單 (XML/PDF)"):
        st.balloons()
        st.success(f"已確認選擇稅則：{selected_hs}，已成功發送至報關系統！")