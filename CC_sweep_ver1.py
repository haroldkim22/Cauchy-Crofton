import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import LineString, box
import time

# ==========================================
# 1. 매개변수 곡선 설정
# ==========================================
def x_func(t):
    return 10 * (t - np.sin(t))
def y_func(t):
    return 10 * (1 - np.cos(t))

t_vals = np.linspace(0, 2 * np.pi, 10000)
points = [(x_func(t), y_func(t)) for t in t_vals]
curve = LineString(points)
true_L = curve.length

# ==========================================
# 2. AABB 및 기준 길이(d_c) 계산
# ==========================================
minx, miny, maxx, maxy = curve.bounds
curve_width = maxx - minx
curve_height = maxy - miny

# AABB의 폭과 높이 중 더 큰 값을 d_c로 설정 (상대적 격자 간격의 기준)
d_c = max(curve_width, curve_height)
box_corners = [(minx, miny), (maxx, miny), (maxx, maxy), (minx, maxy)]
diag_length = np.sqrt(curve_width**2 + curve_height**2) + 10 # 넉넉한 직선 길이

# ==========================================
# 3. 코시-크로프턴 오차율 계산 함수
# ==========================================
def get_error_rate(k, d_theta):
    r = k * d_c  # 상대적 비율 k를 실제 격자 간격 r로 변환
    angles = np.arange(0, np.pi, d_theta)
    total_intersections = 0
    
    for theta in angles:
        # AABB 꼭짓점들을 투영하여 해당 각도에서 격자가 덮어야 할 범위 계산
        projections = [x * np.cos(theta) + y * np.sin(theta) for x, y in box_corners]
        p_min, p_max = min(projections), max(projections)
        
        k_idx_vals = np.arange(np.floor(p_min / r), np.ceil(p_max / r) + 1)
        for k_idx in k_idx_vals:
            p = k_idx * r
            pt_x, pt_y = p * np.cos(theta), p * np.sin(theta)
            dir_x, dir_y = -np.sin(theta), np.cos(theta)
            
            # 격자 직선 생성
            line = LineString([(pt_x - diag_length*dir_x, pt_y - diag_length*dir_y),
                               (pt_x + diag_length*dir_x, pt_y + diag_length*dir_y)])
            
            # 곡선과 직선의 교점 계산 (속도 최적화를 위해 bounds 교차 여부 사전 확인)
            if (curve.bounds[0] <= line.bounds[2] and line.bounds[0] <= curve.bounds[2] and 
                curve.bounds[1] <= line.bounds[3] and line.bounds[1] <= curve.bounds[3]):
                
                intersection = curve.intersection(line)
                if not intersection.is_empty:
                    if intersection.geom_type == 'Point':
                        total_intersections += 1
                    elif intersection.geom_type in ['MultiPoint', 'GeometryCollection']:
                        for geom in intersection.geoms:
                            if geom.geom_type == 'Point':
                                total_intersections += 1
                                
    # 코시-크로프턴 근사값 및 오차율(절댓값 %) 반환
    L_est = 0.5 * total_intersections * r * d_theta
    return abs((L_est - true_L) / true_L) * 100

# ==========================================
# 4. Sweep (변수 반복 탐색) 영역 설정
# ==========================================
# 연산 시간을 고려하여 k와 d_theta를 각각 10단계씩 분할 (총 100번의 시뮬레이션)
# 더 정밀한 그래프를 원하시면 10을 20이나 30으로 늘리시면 됩니다. (단, 시간 오래 걸림)
k_vals = np.linspace(0.02, 0.15, 10)  # k: 2% ~ 15%
d_theta_vals = np.linspace(np.pi/12, np.pi/3, 10)  # d_theta: 15도 ~ 60도

K, D_THETA = np.meshgrid(k_vals, d_theta_vals)
E = np.zeros_like(K)

print("오차율 분석을 위한 Sweep을 시작합니다. 잠시만 기다려주세요...")
start_time = time.time()

# 이변수함수 E(k, d_theta) 배열 채우기
total_steps = K.shape[0] * K.shape[1]
step_count = 0
for i in range(K.shape[0]):
    for j in range(K.shape[1]):
        E[i, j] = get_error_rate(K[i, j], D_THETA[i, j])
        step_count += 1
        # 진행 상황 출력
        if step_count % 10 == 0:
            print(f"진행률: {step_count}/{total_steps} 완료...")

print(f"Sweep 완료! 소요 시간: {time.time() - start_time:.2f}초")

# ==========================================
# 5. 결과 시각화 (2D 히트맵 & 3D 표면 플롯)
# ==========================================
# 한글 폰트 설정 (깨짐 방지)
plt.rcParams['font.family'] = 'Malgun Gothic' # 윈도우 기준 (맥은 'AppleGothic')
plt.rcParams['axes.unicode_minus'] = False

fig = plt.figure(figsize=(14, 6))

# (1) 2D 히트맵 (등고선 플롯)
ax1 = fig.add_subplot(1, 2, 1)
# 오차율이 낮을수록 파란색, 높을수록 붉은색(열화상)으로 표현
contour = ax1.contourf(K, D_THETA, E, levels=20, cmap='RdYlBu_r') 
fig.colorbar(contour, ax=ax1, label='오차율 (%)')
ax1.set_xlabel('상대적 격자 간격 (k = r/d_c)')
ax1.set_ylabel('각도 증분 (Δθ, rad)')
ax1.set_title('오차율 이변수함수 2D 히트맵')

# (2) 3D 표면 플롯
ax2 = fig.add_subplot(1, 2, 2, projection='3d')
surf = ax2.plot_surface(K, D_THETA, E, cmap='RdYlBu_r', edgecolor='none', alpha=0.9)
ax2.set_xlabel('상대적 격자 간격 (k)')
ax2.set_ylabel('각도 증분 (Δθ)')
ax2.set_zlabel('오차율 (%)')
ax2.set_title('오차율 이변수함수 3D 표면 플롯')

plt.tight_layout()
plt.show()
