import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import rasterio
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

# --- 設定您的 DEM 檔案名稱 (字串，無需 pd.read_tif) ---
DEM_FILE_PATH = 'DEM_tawiwan_V2025.tif'

st.title("Plotly 3D 地形圖 (台灣 DEM 數據)")
st.caption(f"數據來源: {DEM_FILE_PATH}")

# --- 1. 讀取 DEM TIF 資料 ---
@st.cache_data
def load_dem_data(file_path):
    try:
        # 使用 rasterio 讀取 TIF 檔案
        with rasterio.open(file_path) as src:
            # 讀取高程數據（Z 軸）。read(1) 讀取第一個波段。
            Z = src.read(1)
            
            # --- 關鍵診斷點 A：檢查 Z 陣列是否包含數據 ---
            rows, cols = Z.shape
            if rows == 0 or cols == 0:
                st.error(f"錯誤：TIF 檔案 '{file_path}' 讀取到的陣列維度為 {rows}x{cols} (空的)。")
                st.markdown("---")
                st.markdown("#### 診斷建議：")
                st.markdown("1. 您的 `.tif` 檔案可能過大，請嘗試使用 GIS 工具（如 QGIS）**裁剪**一個較小的區域。")
                st.markdown("2. 確認 `.tif` 檔案不是損壞的，且包含有效的高程數據。")
                return None, None, None, None
            # --- 關鍵診斷點 A 結束 ---
            
            # 獲取邊界座標 (left, bottom, right, top)
            bounds = src.bounds
            
            lon_min = bounds.left   # 最小經度 (X min)
            lat_min = bounds.bottom # 最小緯度 (Y min)
            lon_max = bounds.right  # 最大經度 (X max)
            lat_max = bounds.top    # 最大緯度 (Y max)
            
            # 建立對應 Z 陣列的 X (經度/lon) 和 Y (緯度/lat) 軸座標序列
            lon = np.linspace(lon_min, lon_max, cols)
            # Y 軸從高 (北) 到低 (南) 建立序列
            lat = np.linspace(lat_max, lat_min, rows)
            
            # 獲取座標系統名稱
            crs_name = src.crs.name
            
            return Z, lon, lat, crs_name
            
    except rasterio.errors.RasterioIOError:
        st.error(f"錯誤：無法讀取檔案 '{file_path}'。請檢查檔案名稱和路徑。")
        return None, None, None, None
    except Exception as e:
        # st.error(f"讀取 TIF 檔案時發生未知錯誤: {type(e).__name__}: {e}")
        st.error(f"讀取 TIF 檔案時發生未知錯誤: {e}")
        return None, None, None, None

Z, lon_coords, lat_coords, crs_name = load_dem_data(DEM_FILE_PATH)

if Z is not None:
    
    # --- 關鍵診斷點 B：再次確認 Z 陣列的有效性 ---
    if Z.size == 0 or np.all(np.isnan(Z)):
        st.error("錯誤：讀取到的高程陣列是空的或全部為 NoData 值。請檢查您的 TIF 檔案內容。")
        st.stop()
    # --- 關鍵診斷點 B 結束 ---
    
    # 處理 DEM 數據中常見的 NoData 值
    # 將所有小於 0 的值 (常見的 NoData 標記) 替換為 NaN
    Z[Z < 0] = np.nan 
    
    # --- 2. 建立 3D Surface 圖 ---
    fig = go.Figure(
        data=[
            go.Surface(
                z=Z,                   # 讀取到的高程陣列 (Z 軸)
                x=lon_coords,          # 經度/X 座標 (X 軸)
                y=lat_coords,          # 緯度/Y 座標 (Y 軸)
                
                # 讓 Z 軸的顏色依據高度變化
                colorscale="Terrain",  # 適合地形的顏色漸層
                showscale=True,
                colorbar_title='海拔 (公尺)' # 顏色條標題
            )
        ]
    )

    # --- 3. 調整 3D 視角和外觀 ---
    fig.update_layout(
        title=f"台灣地形 3D 曲面圖 (坐標系: {crs_name})",
        width=None,
        height=700,
        scene=dict(
            xaxis_title='經度 / X 座標',
            yaxis_title='緯度 / Y 座標',
            zaxis_title='海拔高度 (公尺)',
            
            # 調整視覺比例，讓垂直高度 (Z) 略微誇張，以增強視覺效果
            aspectratio=dict(x=1, y=1, z=0.4), 
            aspectmode='manual'
        )
    )

    # --- 4. 在 Streamlit 中顯示 ---
    st.plotly_chart(fig, use_container_width=True)

    # 顯示一些數據資訊
    st.sidebar.header("DEM 數據資訊")
    st.sidebar.write(f"陣列維度 (Cols x Rows): {Z.shape[1]} x {Z.shape[0]}")
    st.sidebar.write(f"座標系統: {crs_name}")
    st.sidebar.write(f"最大高度: {np.nanmax(Z):.2f} 公尺")
    st.sidebar.write(f"最小高度: {np.nanmin(Z):.2f} 公尺")