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

# ===============================================
#          第二個地圖：模擬 DEM
# ===============================================

st.title("Pydeck 3D 地圖 (網格 - DEM 模擬)")

# --- 1. 讀取範例 DEM 資料 ---
z_data = pd.read_csv("taipie.csv")
X_COL = 'X' 
Y_COL = 'Y' 
Z_COL = 'GRID_CODE'
# 1.2 進行資料透視 (Pivot) 轉換，將長格式數據轉為矩陣
# 我們以 Y 為索引 (Row)，X 為欄位 (Column)，GRID_CODE 為數值
try:
    z_matrix = z_data.pivot(index=Y_COL, columns=X_COL, values=Z_COL)
    
    # 1.3 提取用於繪圖的軸數據和 Z 矩陣
    # x_data (水平軸，對應列)
    x_data = z_matrix.columns.values 
    # y_data (垂直軸，對應索引)
    y_data = z_matrix.index.values
    # z_data_matrix (高程矩陣)
    z_values = z_matrix.values

except Exception as e:
    st.error(f"無法將 CSV 資料轉換為矩陣結構，請檢查 X, Y, GRID_CODE 欄位名稱是否正確: {e}")
    # 為了防止程式崩潰，這裡建議退出或使用簡單圖表，但請您優先檢查欄位名稱
    st.stop()


# --- 2. 建立 3D Surface 圖 ---
fig = go.Figure(
    data=[
        go.Surface(
            x=x_data,
            y=y_data,
            z=z_values,
            colorscale="Viridis"
        )
    ]
)

# --- 3. 調整 3D 視角和外觀 ---
fig.update_layout(
    # 設定圖表的標題文字 (改為符合資料內容)
    title="臺北地區 DEM 3D 地形圖 (GRID_CODE 作為高程)",

    # 設定圖表的寬度和高度 (單位：像素)
    width=800,
    height=700,

    # scene 字典用於配置 3D 圖表的場景
    scene=dict(
        # 設定 X, Y, Z 座標軸的標籤文字
        xaxis_title='X 座標 (經度)',
        yaxis_title='Y 座標 (緯度)',
        zaxis_title='高程 (GRID_CODE)'
    )
)

# --- 4. 在 Streamlit 中顯示 ---
st.plotly_chart(fig)