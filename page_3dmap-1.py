import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

st.title("Pydeck 3D 地圖 (向量 - 密度圖)")
# --- 1. 讀取醫院資料 (假設此處已成功運行並讀取到 36 筆資料) ---
# 為了完整性，我重貼讀取邏輯，請確保它運行正常
st.write("臺北市公私立醫院資料密度圖")
try:
    data = pd.read_csv("臺北市公私立醫院-114.07.csv")
    lat_col = '緯度'
    lon_col = '經度'
    
    # 檢查筆數 (請在 Streamlit 運行時觀察此輸出)
    st.write(f"【數據檢查】成功載入 {len(data)} 筆資料。") 
    
    center_lat = data[lat_col].mean()
    center_lon = data[lon_col].mean()
    
except Exception as e:
    st.error(f"讀取 CSV 失敗: {e}")
    # 備用數據，若運行環境無法找到 CSV 檔案
    data = pd.DataFrame({'lat': [25.0478], 'lon': [121.5170]})
    lat_col = 'lat'
    lon_col = 'lon'
    center_lat = 25.0478
    center_lon = 121.5170


# --- 2. 設定 Pydeck 圖層 (Layer) ---
layer_hexagon = pdk.Layer(
    'HexagonLayer',
    data=data,
    get_position=f'[{lon_col}, {lat_col}]', 
    radius=2000,
    elevation_scale=4,
    elevation_range=[0, 1000],
    pickable=True,
    extruded=True,
)

# --- 3. 設定攝影機視角 (View State) ---
view_state_hexagon = pdk.ViewState(
    latitude=center_lat,
    longitude=center_lon,
    zoom=10,
    pitch=50,
)

# --- 4. 組合圖層和視角並顯示 ---
r_hexagon = pdk.Deck(
    layers=[layer_hexagon],
    initial_view_state=view_state_hexagon,
    tooltip={"text": "此區域共有 {elevationValue} 家醫院"} 
)

st.pydeck_chart(r_hexagon)

st.title("Pydeck 3D 地圖 (網格 - DEM 數據)")

# --- 1. 讀取真實 DEM 資料 (taipie.csv) ---
try:
    # 讀取您上傳的 CSV 檔案
    df_dem = pd.read_csv("taipie.csv")
    
    # 確定欄位名稱
    LON_COL = 'X'
    LAT_COL = 'Y'
    ELEVATION_COL = 'GRID_CODE'
    
    # 確保資料中含有必要的欄位
    if not all(col in df_dem.columns for col in [LON_COL, LAT_COL, ELEVATION_COL]):
        st.error(f"CSV 檔案缺少必要的欄位。請確認檔案中含有: {LON_COL}, {LAT_COL}, {ELEVATION_COL}")
        st.stop()
        
    # 計算數據的中心點，用於設定視角
    base_lat = df_dem[LAT_COL].mean()
    base_lon = df_dem[LON_COL].mean()
    
except FileNotFoundError:
    st.error("找不到 'taipie.csv' 檔案，請確認檔案路徑正確。")
    st.stop()
except Exception as e:
    st.error(f"讀取或處理 CSV 發生錯誤: {e}")
    st.stop()

st.write(f"他好慢我們等他一下......")

# --- 2. 設定 Pydeck 圖層 (GridLayer) ---
layer_grid = pdk.Layer(
    'GridLayer',
    data=df_dem,
    # 使用 CSV 中的實際經緯度欄位
    get_position=f'[{LON_COL}, {LAT_COL}]', 
    # 使用 GRID_CODE 欄位作為高度權重
    get_elevation_weight=ELEVATION_COL, 
    elevation_scale=1, # 比例因子設為 1，讓 GRID_CODE 的值直接決定高度
    
    # cell_size 需要根據您的數據經緯度間距來設定。
    # 由於您的 X/Y 座標間距可能是固定的 (例如 0.0002度)，
    # 這裡保留您範例的 2000 米 (或 0.02 度)，您可能需要根據實際數據間距調整。
    cell_size=2000, 
    
    extruded=True,
    pickable=True
)

# --- 3. 設定視角 (View) ---
view_state_grid = pdk.ViewState(
    latitude=base_lat, 
    longitude=base_lon, 
    zoom=10, # 提高 zoom 級別，讓您能看清網格細節
    pitch=50
)

# --- 4. 組合並顯示地圖 ---
r_grid = pdk.Deck(
    layers=[layer_grid],
    initial_view_state=view_state_grid,
    tooltip={"text": f"{ELEVATION_COL}: {{elevationValue}} 公尺"} 
)
st.pydeck_chart(r_grid)