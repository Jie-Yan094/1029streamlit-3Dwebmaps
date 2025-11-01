import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

st.title("Pydeck 3D 地圖 (向量 - 密度圖)")
# --- 1. 讀取醫院資料 (假設此處已成功運行並讀取到 36 筆資料) ---
# 為了完整性，我重貼讀取邏輯，請確保它運行正常
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
    
    # ⬇️ 關鍵調整點：嘗試改變這個數值 ⬇️
    radius=1500, # 嘗試從 300 調整為 400 或 200 
    
    elevation_scale=5,
    elevation_range=[0, 1000],
    pickable=True,
    extruded=True,
    color_range=[
        [255, 255, 178, 20], [255, 237, 160, 100], [254, 201, 128, 150],
        [252, 141, 60, 180], [227, 76, 76, 210], [189, 0, 38, 255]
    ]
)

# --- 3. 設定攝影機視角 (View State) ---
view_state_hexagon = pdk.ViewState(
    latitude=center_lat,
    longitude=center_lon,
    zoom=12,
    pitch=50,
)

# --- 4. 組合圖層和視角並顯示 ---
r_hexagon = pdk.Deck(
    layers=[layer_hexagon],
    initial_view_state=view_state_hexagon,
    tooltip={"text": "此區域共有 {elevationValue} 家醫院"} 
)

st.pydeck_chart(r_hexagon)

# ===============================================
#          第二個地圖：模擬 DEM
# ===============================================

st.title("Pydeck 3D 地圖 (網格 - DEM 模擬)")

# --- 1. 模擬 DEM 網格資料 ---
x, y = np.meshgrid(np.linspace(-1, 1, 50), np.linspace(-1, 1, 50))
z = np.exp(-(x**2 + y**2) * 2) * 1000

data_dem_list = [] # 修正: 建立一個列表來收集字典
base_lat, base_lon = 25.0, 121.5
for i in range(50):
    for j in range(50):
        data_dem_list.append({ # 修正: 將字典附加到列表中
            "lon": base_lon + x[i, j] * 0.1,
            "lat": base_lat + y[i, j] * 0.1,
            "elevation": z[i, j]
        })
df_dem = pd.DataFrame(data_dem_list) # 從列表創建 DataFrame

# --- 2. 設定 Pydeck 圖層 (GridLayer) ---
layer_grid = pdk.Layer( # 稍微改個名字避免混淆
    'GridLayer',
    data=df_dem,
    get_position='[lon, lat]',
    get_elevation_weight='elevation', # 使用 'elevation' 欄位當作高度
    elevation_scale=1,
    cell_size=2000,
    extruded=True,
    pickable=True # 加上 pickable 才能顯示 tooltip
)

# --- 3. 設定視角 (View) ---
view_state_grid = pdk.ViewState( # 稍微改個名字避免混淆
    latitude=base_lat, longitude=base_lon, zoom=10, pitch=50
)

# --- 4. 組合並顯示 (第二個地圖) ---
r_grid = pdk.Deck( # 稍微改個名字避免混淆
    layers=[layer_grid],
    initial_view_state=view_state_grid,
    # mapbox_key=MAPBOX_KEY, # <--【修正點】移除這裡的 mapbox_key
    tooltip={"text": "海拔高度: {elevationValue} 公尺"} # GridLayer 用 elevationValue
)
st.pydeck_chart(r_grid)