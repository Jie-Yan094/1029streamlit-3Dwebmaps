import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import rasterio
import numpy as np # 導入 numpy 用於處理 NaN
import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Plotly 3D 地圖 (向量 - 地球儀)")

# --- 0. 建立中文國家名稱到 ISO 3 碼的對應字典 ---
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

# --- 1. 載入完整資料 ---
try:
    # 使用 'encoding="utf-8"' 確保中文讀取正常
    df_full = pd.read_csv('老化指數.csv', encoding='utf-8')
except FileNotFoundError:
    st.error("找不到 '老化指數.csv' 檔案，請確認檔案路徑。")
    st.stop()

# --- 1.5 資料清理與轉換 (解決 TypeError 和地理定位問題) ---

# A. 清理 '老化指數' (解決 TypeError)
# 必須對完整資料集進行此操作
df_full['老化指數_cleaned'] = pd.to_numeric(df_full['老化指數'], errors='coerce')

# B. 轉換 '國別' 欄位 (解決地理定位問題)
# 建立一個新的 ISO 代碼欄位
df_full['iso_alpha'] = df_full['國別'].map(chinese_to_iso)

# C. 移除包含錯誤或缺失資料的行 (基於必要的欄位)
df_cleaned = df_full.dropna(subset=['老化指數_cleaned', 'iso_alpha', '西元年'])

# 確保 '西元年' 是整數類型，以便後續選取
df_cleaned['西元年'] = df_cleaned['西元年'].astype(int)

# --- 2. 使用者選擇年份 ---
available_years = sorted(df_cleaned['西元年'].unique(), reverse=True)

if not available_years:
    st.warning("資料集中找不到有效的年份資料，無法繪圖。")
    st.stop()

# 預設選擇最新的年份 (或您可以設定為 2020)
default_year = 2020 if 2020 in available_years else available_years[0]

selected_year = st.selectbox(
    "請選擇要顯示的年份(2020後為推估數值):",
    options=available_years,
    index=available_years.index(default_year) if default_year in available_years else 0
)

# --- 3. 根據選擇的年份篩選資料 ---
df_plot = df_cleaned[df_cleaned['西元年'] == selected_year].copy()

# 檢查是否有資料可以繪製
if df_plot.empty:
    st.warning(f"{selected_year} 年的資料集為空或資料不完整，無法繪圖。請嘗試選擇其他年份。")
    st.stop()

# --- 4. 建立 3D 地理散點圖 (scatter_geo) ---
fig = px.scatter_geo(
    df_plot,
    locations="iso_alpha",          # 使用標準的 ISO 3 國家代碼
    locationmode='ISO-3',           # 告訴 Plotly 這些是 ISO 3 碼
    color="國別",                   # 依據國家名稱上色
    hover_name="國別",              # 滑鼠懸停時顯示國家名稱
    size="老化指數_cleaned",        # 點的大小代表清洗後的數值
    projection="orthographic",      # 建立 3D 地球儀效果
    title=f"{selected_year}年 各國老化指數分佈 (3D 地球儀)"
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

# --- 5. 在 Streamlit 中顯示 ---
st.plotly_chart(fig, use_container_width=True)
st.title("Plotly 3D 地圖 (網格 - DEM 表面)")

# --- 1. 讀取範例 DEM 資料 ---
z_data = pd.read_csv("taipie.csv")

# ----------------------------------------------------
# ⚠️ 修正 NameError 的關鍵步驟：定義 x, y, z 變數 ⚠️
#    將 CSV 中的欄位提取為 Series
# ----------------------------------------------------
# X 軸數據：使用 'Row' 欄位
x = z_data['X']

# Y 軸數據：使用 'Column' 欄位
y = z_data['Y']

# Z 軸數據（高程）：使用 'Value' 欄位
z = z_data['GRID_CODE'] 
# ----------------------------------------------------


# --- 2. 建立 3D Surface 圖 ---
# 為了繪製 3D 表面圖，Plotly 要求 x, y, z 數據必須是『矩陣 (Matrix)』結構，
# 而不是我們現在的『點列表 (List of Points)』結構。
# 我們需要使用 .pivot() 將 Row/Column/Value 的點列表轉換為矩陣。

# 2.1 進行資料透視 (Pivot) 轉換為矩陣結構
z_matrix = z_data.pivot(index='X', columns='Y', values='GRID_CODE')

# 2.2 從矩陣中提取 x, y, z 數據
# 提取 x (Columns 標籤), y (Index 標籤), z (Value 矩陣)
x_data = z_matrix.columns
y_data = z_matrix.index
z_data_matrix = z_matrix.values

# 建立一個 Plotly 的 Figure 物件
fig = go.Figure(
    data=[
        # 建立一個 Surface (曲面) trace
        go.Surface(
            # 使用轉換後的矩陣數據
            x=x_data,             # X 座標
            y=y_data,             # Y 座標
            z=z_data_matrix,      # Z 數值（高程矩陣）
            colorscale="Viridis"
        )
    ]
)

# --- 3. 調整 3D 視角和外觀 ---
# ... (此處程式碼保持不變) ...
fig.update_layout(
    title="DEM 表面 3D 圖 (可旋轉)", # 建議修改標題以符合資料內容
    width=800,
    height=700,
    scene=dict(
        xaxis_title='Row Index (X)', # 由於您使用 Row/Column，建議修改標籤
        yaxis_title='Column Index (Y)',
        zaxis_title='海拔/高程 (Z)'
    )
)

# --- 4. 在 Streamlit 中顯示 ---
st.plotly_chart(fig)