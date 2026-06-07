
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import LineString, box
import time

# ==========================================
# 1. 매개변수 곡선 정의
# ==========================================

def x_func(t):
    return 10*(t-np.sin(t))
    # return 10*np.cos(t)
def y_func(t):
    return 10*(1-np.cos(t))
    # return 10*np.sin(t)
t_vals = np.linspace(0, 2 * np.pi, 10000)

points = [(x_func(t), y_func(t)) for t in t_vals]
curve = LineString(points)
true_L = curve.length

# ==========================================
# 2. AABB & buffer
# ==========================================
minx, miny, maxx, maxy = curve.bounds
curve_width = maxx - minx
curve_height = maxy - miny

# AABB의 폭과 높이 중 더 큰 값을 d_c로 설정 (상대적 격자 간격의 기준)
d_c = max(curve_width, curve_height)



margin = d_c * 0.1
if margin == 0: margin = 1

b_minx, b_maxx = minx - margin, maxx + margin
b_miny, b_maxy = miny - margin, maxy + margin

grid_box = box(b_minx, b_miny, b_maxx, b_maxy)
box_corners = [(minx, miny), (maxx, miny), (maxx, maxy), (minx, maxy)]
diag_length = np.sqrt(curve_width**2 + curve_height**2) + 10 # 넉넉한 직선 길이

# ==========================================
# 3. Defining Function
# ==========================================

# (1) 소수점 각도를 "π/n"
def format_theta(val):
    n_float = np.pi / val

    # 만약 정수라면 (예: 2.0, 3.0) 꼬리표 떼고 정수로 출력
    if abs(n_float - round(n_float)) < 1e-5:
        n = int(round(n_float))
        if n == 1: return "π"
        return f"π/{n}"
    # 소수점이 있는 경우
    else:
        n = round(n_float, 1)
        return f"π/{n}"

# (2) Sweep
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

# (3) 개별 샘플
def visualize_sample(ax, k, d_theta_val, sample_idx):
    r = k * d_c
    angles = np.arange(0, np.pi, d_theta_val)
    total_intersections = 0

    # 곡선 그리기
    x_coords, y_coords = curve.xy
    ax.plot(x_coords, y_coords, color='blue', linewidth=2, label="Curve", zorder=2)

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

            # 격자 선 시각화
            clipped_line = line.intersection(grid_box)
            if not clipped_line.is_empty:
                if clipped_line.geom_type == 'LineString':
                    ax.plot(*clipped_line.xy, color='dimgray', alpha=0.5, linewidth=0.5, zorder=1)
                elif clipped_line.geom_type == 'MultiLineString':
                    for geom in clipped_line.geoms:
                        ax.plot(*geom.xy, color='dimgray', alpha=0.5, linewidth=0.5, zorder=1)

            # 교점 시각화
            intersection = curve.intersection(line)
            if not intersection.is_empty:
                if intersection.geom_type == 'Point':
                    total_intersections += 1
                    ax.plot(intersection.x, intersection.y, 'ro', markersize=2, zorder=3)
                elif intersection.geom_type in ['MultiPoint', 'GeometryCollection']:
                    for geom in intersection.geoms:
                        if geom.geom_type == 'Point':
                            total_intersections += 1
                            ax.plot(geom.x, geom.y, 'ro', markersize=2, zorder=3)

    ax.set_aspect('equal')
    ax.set_xlim(minx - margin, maxx + margin)
    ax.set_ylim(miny - margin, maxy + margin)

    L_est = 0.5 * total_intersections * r * d_theta_val
    error_rate = (L_est - true_L) / true_L * 100

    theta_str = format_theta(d_theta_val)
    print(f"▶ [Sample {sample_idx}] k: {k:.3f}, Δθ: {theta_str} | n={total_intersections} | Error: {error_rate:.2f}%")
    ax.set_title(f"Sample {sample_idx}: k={k:.3f}, dθ={theta_str}\nError: {error_rate:.2f}%")


# ==========================================
# 4. Calculation
# ==========================================
# [사용자 설정 파트] Sweep 범위 및 해상도 조절
# --------------------------------------------------
K_START = 0.02          # k 시작값 (예: 0.02 -> 2%)
K_END   = 0.15          # k 끝값   (예: 0.15 -> 15%)
K_STEPS = 10            # k 분할 단계 수 (해상도)

k_vals = np.linspace(K_START, K_END, K_STEPS)

d_theta_vals = np.array([
    np.pi/12, np.pi/10, np.pi/8, np.pi/7, np.pi/6,
    np.pi/5, np.pi/4, np.pi/3, np.pi/2
])
# --------------------------------------------------

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
# 5. 그래프 생성 및 동시 출력 설정
# ==========================================

# 1. 히트맵
fig1 = plt.figure(figsize=(14, 6))
max_abs_err = np.max(np.abs(E))

theta_labels = [format_theta(v) for v in d_theta_vals]

ax1 = fig1.add_subplot(1, 2, 1)
contour = ax1.contourf(K, D_THETA, E, levels=20, cmap='RdBu_r', vmin=-max_abs_err, vmax=max_abs_err)
fig1.colorbar(contour, ax=ax1, label='Error (%) \n (+: Over, -: Under)')
ax1.set_xlabel('k = r/d_c')
ax1.set_ylabel('Δθ (rad)')
ax1.set_title('2D Heatmap')

ax1.set_yticks(d_theta_vals)
ax1.set_yticklabels(theta_labels)
ax1.set_title('2D Heatmap')

# 2. 3D plot
ax2 = fig1.add_subplot(1, 2, 2, projection='3d')
surf = ax2.plot_surface(K, D_THETA, E, cmap='RdBu_r', edgecolor='none', alpha=0.9,
                        vmin=-max_abs_err, vmax=max_abs_err)
ax2.set_xlabel('k = r/d_c')
ax2.set_ylabel('Δθ (rad)')
ax2.set_yticks(d_theta_vals)
ax2.set_yticklabels(theta_labels)
ax2.set_zlabel('Error (%)')
ax2.set_title('3D Surface Plot')
fig1.tight_layout()

# 2. 5개 샘플 격자 모음 창 (Figure 2)
sample_params = [
    (0.02, np.pi/12),  # Case 1: 매우 촘촘함
    (0.05, np.pi/8),   # Case 2: 촘촘함
    (0.08, np.pi/6),   # Case 3: 중간
    (0.11, np.pi/4),   # Case 4: 엉성함
    (0.15, np.pi/3),    # Case 5: 매우 엉성함
    (0.15, np.pi/2)
]

print("Samples")
# 2행 3열의 그리드 생성 (총 6개 자리)
fig2, axes = plt.subplots(2, 3, figsize=(15, 10))
axes = axes.flatten()

# 5개의 자리에 그래프 그리기
for idx, (k_val, theta_val) in enumerate(sample_params):
    visualize_sample(axes[idx], k_val, theta_val, idx+1)

# 6번째 빈 공간은 숨김 처리
# axes[5].set_visible(False)
# fig2.tight_layout()

# ==========================================
# 6. 최종 출력: 모든 창을 한 번에 띄우기
# ==========================================
plt.show()
