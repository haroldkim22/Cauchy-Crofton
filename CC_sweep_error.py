import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import LineString, box
import time

# ==========================================
# 1. 매개변수 곡선 정의
# ==========================================

def x_func(t):
    # return 10*(t-np.sin(t))
    return 10*np.cos(t)
def y_func(t):
    # return 10*(1-np.cos(t))
    return 10*np.sin(t)
t_vals = np.linspace(0, 2 * np.pi, 10000)

points = [(x_func(t), y_func(t)) for t in t_vals]
curve = LineString(points)
true_L = curve.length

# ==========================================
# 2. (10% 여백이 적용된 바운딩 박스) AABB
# ==========================================
minx, miny, maxx, maxy = curve.bounds
curve_width = maxx - minx
curve_height = maxy - miny

# AABB의 폭과 높이 중 더 큰 값을 d_c로 설정 (상대적 격자 간격의 기준)
d_c = max(curve_width, curve_height)
box_corners = [(minx, miny), (maxx, miny), (maxx, maxy), (minx, maxy)]
diag_length = np.sqrt(curve_width**2 + curve_height**2) + 10 # 넉넉한 직선 길이

# # 곡선의 너비/높이 중 큰 값의 10%를 버퍼(여백)로 설정
# margin = max(curve_width, curve_height) * 0.1 
# if margin == 0: margin = 1

# # 10% 확장된 새로운 화면 영역 (b_ = buffered)
# b_minx, b_maxx = minx - margin, maxx + margin
# b_miny, b_maxy = miny - margin, maxy + margin

# # 격자를 그릴 '10% 여백 박스(Polygon)' 객체 생성
# grid_box = box(b_minx, b_miny, b_maxx, b_maxy)
# box_corners = list(grid_box.exterior.coords) # 박스의 4개 꼭짓점

# ==========================================
# 3. 배경 그리기
# ==========================================
# r = 1.0  # 격자 간격
# d_theta = np.pi / 4  # 각도 간격
# angles = np.arange(0, np.pi, d_theta) 

# total_intersections = 0
# fig, ax = plt.subplots(figsize=(10, 6))

# # 매개변수 곡선 그리기
# x_coords, y_coords = curve.xy
# ax.plot(x_coords, y_coords, color='blue', linewidth=2, label="Parametric Curve", zorder=2)

# diag_length = np.sqrt((b_maxx - b_minx)**2 + (b_maxy - b_miny)**2)

# ==========================================
# 4. 교점 계산 및 시각화
# ==========================================

# 무작위 선을 긋고 '정확한 교점' 찾기
# for theta in angles:
#     projections = [x * np.cos(theta) + y * np.sin(theta) for x, y in box_corners]
#     p_min, p_max = min(projections), max(projections)

#     k_vals = np.arange(np.floor(p_min / r), np.ceil(p_max / r) + 1)
#     for k in k_vals:
#         p = k * r
#         # 직선 위의 기준점과 방향
#         pt_x, pt_y = p * np.cos(theta), p * np.sin(theta)
#         dir_x, dir_y = -np.sin(theta), np.cos(theta)
        
#         # 선분 생성
#         line = LineString([(pt_x - diag_length*dir_x, pt_y - diag_length*dir_y),
#                            (pt_x + diag_length*dir_x, pt_y + diag_length*dir_y)])

#         clipped_line = line.intersection(grid_box)
        
#         if not clipped_line.is_empty:
#             if clipped_line.geom_type == 'LineString':
#                 ax.plot(*clipped_line.xy, color='dimgray', alpha=0.8, linewidth=0.7, zorder=1)
#             elif clipped_line.geom_type == 'MultiLineString':
#                 for geom in clipped_line.geoms:
#                     ax.plot(*geom.xy, color='dimgray', alpha=0.8, linewidth=0.7, zorder=1)
        
#         # 교점 계산 (원래 곡선과 만나는 점)
#         intersection = curve.intersection(line)
        
#         # 교점이 존재하면 카운트하고 빨간 점 찍기
#         if not intersection.is_empty:
#             if intersection.geom_type == 'Point':
#                 total_intersections += 1
#                 ax.plot(intersection.x, intersection.y, 'ro', markersize=1, zorder=3)
#             elif intersection.geom_type in ['MultiPoint', 'GeometryCollection']:
#                 for geom in intersection.geoms:
#                     if geom.geom_type == 'Point':
#                         total_intersections += 1
#                         ax.plot(geom.x, geom.y, 'ro', markersize=1, zorder=3)
# 
# ax.set_aspect('equal')

# curve_width = maxx - minx
# curve_height = maxy - miny

# margin = max(curve_width, curve_height) * 0.1 

# if margin == 0:
#     margin = 1

# ax.set_xlim(minx - margin, maxx + margin)
# ax.set_ylim(miny - margin, maxy + margin)

# ==========================================
# 연산, Sweep
# ==========================================
def get_error_rate(k, d_theta):
    r = k * d_c
    angles = np.arange(0, np.pi, d_theta)
    total_intersections = 0
    
    for theta in angles:
        projections = [x * np.cos(theta) + y * np.sin(theta) for x, y in box_corners]
        p_min, p_max = min(projections), max(projections)
        
        k_idx_vals = np.arange(np.floor(p_min / r), np.ceil(p_max / r) + 1)
        for k_idx in k_idx_vals:
            p = k_idx * r
            pt_x, pt_y = p * np.cos(theta), p * np.sin(theta)
            dir_x, dir_y = -np.sin(theta), np.cos(theta)
            
            line = LineString([(pt_x - diag_length*dir_x, pt_y - diag_length*dir_y),
                               (pt_x + diag_length*dir_x, pt_y + diag_length*dir_y)])
               
            # 곡선과 직선의 교점 계산 (속도 최적화를 위해 bounds 교차 여부 사전 확인)
            # if (curve.bounds[0] <= line.bounds[2] and line.bounds[0] <= curve.bounds[2] and 
            #     curve.bounds[1] <= line.bounds[3] and line.bounds[1] <= curve.bounds[3]):
            
            intersection = curve.intersection(line)
            if not intersection.is_empty:
                if intersection.geom_type == 'Point':
                    total_intersections += 1
                elif intersection.geom_type in ['MultiPoint', 'GeometryCollection']:
                    for geom in intersection.geoms:
                        if geom.geom_type == 'Point':
                            total_intersections += 1
                                
    L_est = 0.5 * total_intersections * r * d_theta
    return (L_est - true_L) / true_L * 100


# --------------------------------------------------
# [사용자 설정 파트] Sweep 범위 및 해상도 조절
# --------------------------------------------------
K_START = 0.02          # k 시작값 (예: 0.02 -> 2%)
K_END   = 0.15          # k 끝값   (예: 0.15 -> 15%)
K_STEPS = 10            # k 분할 단계 수 (해상도)

THETA_START = np.pi/12  # d_theta 시작값 (예: 15도)
THETA_END   = np.pi/3   # d_theta 끝값   (예: 60도)
THETA_STEPS = 10        # d_theta 분할 단계 수 (해상도)
# --------------------------------------------------

# 설정한 변수를 바탕으로 배열 생성
k_vals = np.linspace(K_START, K_END, K_STEPS) 
d_theta_vals = np.linspace(THETA_START, THETA_END, THETA_STEPS) 

K, D_THETA = np.meshgrid(k_vals, d_theta_vals)
E = np.zeros_like(K)

print("Sweep start...")
start_time = time.time()

total_steps = K.shape[0] * K.shape[1]
step_count = 0
for i in range(K.shape[0]):
    for j in range(K.shape[1]):
        E[i, j] = get_error_rate(K[i, j], D_THETA[i, j])
        step_count += 1
        if step_count % 10 == 0:
            print(f"Progress: {step_count}/{total_steps} done...")

print(f"Sweep completed! Time: {time.time() - start_time:.2f} sec")

# ==========================================
# 출력
# ==========================================
# L = 0.5 * total_intersections * r * d_theta

# true_L = curve.length

# error_rate = (L - true_L) / true_L * 100

# print(f"====================================")
# print(f"교점 수(n): {total_intersections}개")
# print(f"코시-크로프턴 근사: {L:.4f}")
# print(f"실제 길이: {true_L:.4f}")
# print(f"오차율: {error_rate:.2f}%")
# print(f"====================================")


fig = plt.figure(figsize=(14, 6))

# (1) 2D 히트맵 (등고선 플롯)
ax1 = fig.add_subplot(1, 2, 1)
max_abs_err = np.max(np.abs(E))
# 오차율이 낮을수록 파란색, 높을수록 붉은색(열화상)으로 표현
contour = ax1.contourf(K, D_THETA, E, levels=20, cmap='RdBu_r', 
                       vmin=-max_abs_err, vmax=max_abs_err)
fig.colorbar(contour, ax=ax1, label='Error (%)')
ax1.set_xlabel('k = r/d_c')
ax1.set_ylabel('Δθ (rad)')
ax1.set_title('Heatmap')

# (2) 3D 표면 플롯
ax2 = fig.add_subplot(1, 2, 2, projection='3d')
surf = ax2.plot_surface(K, D_THETA, E, cmap='RdBu_r', edgecolor='none', alpha=0.9,
                        vmin=-max_abs_err, vmax=max_abs_err)
ax2.set_xlabel('k = r/d_c')
ax2.set_ylabel('Δθ (rad)')
ax2.set_zlabel('Error (%)')
ax2.set_title('3D plot')

plt.tight_layout()
plt.show()
