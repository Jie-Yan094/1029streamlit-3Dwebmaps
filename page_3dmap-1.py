import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

st.title("Pydeck 3D 地圖 (向量 - 密度圖)")
# --- 1. 讀取醫院資料 ---
try:
    # 讀取您上傳的 CSV 檔案
    data = pd.read_csv("臺北市公私立醫院-114.07.csv")
    
    # 確定經緯度欄位名稱 (根據 CSV 內容)
    lat_col = '緯度'
    lon_col = '經度'
    
    # 計算數據的中心點，讓地圖預設視角更準確
    center_lat = data[lat_col].mean()
    center_lon = data[lon_col].mean()
    
except Exception as e:
    st.error(f"讀取 CSV 失敗，請檢查檔案路徑或欄位名稱: {e}")
    # 如果失敗，使用一個預設的臺北中心點作為備用
    center_lat = 25.0478
    center_lon = 121.5170
    data = pd.DataFrame({'lat': [25.0478], 'lon': [121.5170]}) # 備用空資料
    lat_col = 'lat'
    lon_col = 'lon'


# --- 2. 設定 Pydeck 圖層 (Layer) ---
layer_hexagon = pdk.Layer(
    'HexagonLayer',
    data=data,
    # 使用 CSV 中的實際欄位名稱
    get_position=f'[{lon_col}, {lat_col}]', 
    radius=300, # 調整半徑，300 米適合市區醫院點的密度分佈
    elevation_scale=5,
    elevation_range=[0, 1000],
    pickable=True,
    extruded=True,
    # 設定顏色，讓密度高的區域顏色更深或更高
    color_range=[
        [255, 255, 178, 20],  # 淡黃
        [255, 237, 160, 100],
        [254, 201, 128, 150],
        [252, 141, 60, 180],
        [227, 76, 76, 210],
        [189, 0, 38, 255]   # 紅色 (最高密度)
    ]
)

# --- 3. 設定攝影機視角 (View State) ---
view_state_hexagon = pdk.ViewState(
    latitude=center_lat,
    longitude=center_lon,
    zoom=11.5, # 稍微放大一點以涵蓋整個臺北市
    pitch=50,
)

# --- 4. 組合圖層和視角並顯示 ---
r_hexagon = pdk.Deck(
    layers=[layer_hexagon],
    initial_view_state=view_state_hexagon,
    # 提示文字顯示該區域的醫院數量
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