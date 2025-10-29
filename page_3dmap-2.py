import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np # 導入 numpy 用於處理 NaN

st.title("Plotly 3D 地圖 (向量 - 地球儀)")
# --- 0. 建立中文國家名稱到 ISO 3 碼的對應字典 ---
# 這是繪製地圖的關鍵，Plotly 需要標準代碼 (ISO 3-letter codes)
# 由於您的資料包含多個國家，我將根據常見的國家名稱補齊必要的對應。
# 請在實際運行前，確認此字典涵蓋了您所有需要的 '國別'。
chinese_to_iso = {
    "中華民國": "TWN",
    "日本": "JPN",
    "韓國": "KOR",
    "美國": "USA",
    "英國": "GBR",
    "德國": "DEU",
    "法國": "FRA",
    "挪威": "NOR",
    "瑞典": "SWE",
    "荷蘭": "NLD",
    "芬蘭": "FIN",
    "奧地利": "AUT",
    "義大利": "ITA",
    "西班牙": "ESP",
    # 如果您的資料還有其他國家，請在這裡手動加入它們的 ISO 3 碼
}

# --- 1. 載入資料並篩選年份 ---
try:
    # 使用 'encoding="utf-8"' 確保中文讀取正常
    df = pd.read_csv('老化指數.csv', encoding='utf-8').query("西元年 == 2020")
except FileNotFoundError:
    st.error("找不到 '老化指數.csv' 檔案，請確認檔案路徑。")
    st.stop()

# --- 1.5 資料清理與轉換 (解決 TypeError 和地理定位問題) ---

# A. 清理 '老化指數' (解決 TypeError)
# 將 '老化指數' 轉換為數值，無法轉換的設為 NaN
df['老化指數_cleaned'] = pd.to_numeric(df['老化指數'], errors='coerce')

# B. 轉換 '國別' 欄位 (解決地理定位問題)
# 建立一個新的 ISO 代碼欄位
df['iso_alpha'] = df['國別'].map(chinese_to_iso)

# C. 移除包含錯誤或缺失資料的行
# 移除 '老化指數' 為 NaN (無法計算大小) 或 'iso_alpha' 為 NaN (無法定位) 的行
df.dropna(subset=['老化指數_cleaned', 'iso_alpha'], inplace=True)

# 檢查是否有資料可以繪製
if df.empty:
    st.warning("篩選和清洗後，2020 年的資料集為空，無法繪圖。請檢查篩選條件或資料內容。")
    st.stop()

# --- 2. 建立 3D 地理散點圖 (scatter_geo) ---
# 由於我們處理的是亞洲/歐洲國家，'orthographic' 投影可能需要調整視角才能看到所有點
fig = px.scatter_geo(
    df,
    locations="iso_alpha",          # 使用標準的 ISO 3 國家代碼
    locationmode='ISO-3',           # 告訴 Plotly 這些是 ISO 3 碼
    color="國別",                   # 依據國家名稱上色
    hover_name="國別",              # 滑鼠懸停時顯示國家名稱
    size="老化指數_cleaned",        # 點的大小代表清洗後的數值
    projection="orthographic",      # 建立 3D 地球儀效果
    title="2020年 各國老化指數分佈 (3D 地球儀)"
)

# 調整視角，確保地球儀不會完全看不到資料點（可選）
fig.update_geos(
    projection_rotation=dict(lon=10, lat=30, roll=0), # 調整視角方向
    showcountries=True,
    showocean=True,
    oceancolor="LightBlue",
    showland=True,
    landcolor="LightGreen"
)

# --- 3. 在 Streamlit 中顯示 ---
st.plotly_chart(fig, use_container_width=True)

st.title("Plotly 3D 地圖 (網格 - DEM 表面)")

# --- 1. 讀取範例 DEM 資料 ---
# Plotly 內建的 "volcano" (火山) DEM 數據 (儲存為 CSV)
# 這是一個 2D 陣列 (Grid)，每個格子的值就是海拔
z_data = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/api_docs/mt_bruno_elevation.csv")

# --- 2. 建立 3D Surface 圖 ---
# 建立一個 Plotly 的 Figure 物件，它是所有圖表元素的容器
fig = go.Figure(
    # data 參數接收一個包含所有 "trace" (圖形軌跡) 的列表。
    # 每個 trace 定義了一組數據以及如何繪製它。
    data=[
        # 建立一個 Surface (曲面) trace
        go.Surface(
            # *** 關鍵參數：z ***
            # z 參數需要一個 2D 陣列 (或列表的列表)，代表在 X-Y 平面上每個點的高度值。
            # z_data.values 會提取 pandas DataFrame 底層的 NumPy 2D 陣列。
            # Plotly 會根據這個 2D 陣列的結構來繪製 3D 曲面。
            z=z_data.values,

            # colorscale 參數指定用於根據 z 值 (高度) 對曲面進行著色的顏色映射方案。
            # "Viridis" 是 Plotly 提供的一個常用且視覺效果良好的顏色漸層。
            # 高度值較低和較高的點會有不同的顏色。
            colorscale="Viridis"
        )
    ] # data 列表結束
)

# --- 3. 調整 3D 視角和外觀 ---
# 使用 update_layout 方法來修改圖表的整體佈局和外觀設定
fig.update_layout(
    # 設定圖表的標題文字
    title="Mt. Bruno 火山 3D 地形圖 (可旋轉)",

    # 設定圖表的寬度和高度 (單位：像素)
    width=800,
    height=700,

    # scene 參數是一個字典，用於配置 3D 圖表的場景 (座標軸、攝影機視角等)
    scene=dict(
        # 設定 X, Y, Z 座標軸的標籤文字
        xaxis_title='經度 (X)',
        yaxis_title='緯度 (Y)',
        zaxis_title='海拔 (Z)'
        # 可以在 scene 字典中加入更多參數來控制攝影機初始位置、座標軸範圍等
    )
)

# 這段程式碼執行後，變數 `fig` 將包含一個設定好的 3D Surface Plotly 圖表物件。
# 你可以接著使用 fig.show() 或 st.plotly_chart(fig) 將其顯示出來。
# 這個圖表通常是互動式的，允許使用者用滑鼠旋轉、縮放和平移 3D 視角。

# --- 4. 在 Streamlit 中顯示 ---
st.plotly_chart(fig)