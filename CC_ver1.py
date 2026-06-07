import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import LineString

# ==========================================
# 1. 매개변수 곡선(Parametric Curve) 정의하기
# ==========================================
# 아래 x_func와 y_func의 수식을 원하는 대로 수정하세요!
# (numpy 함수인 np.sin, np.cos, np.exp 등을 사용합니다)

def x_func(t):
    # 예시: 하트 모양 곡선의 x(t)
    return 16 * np.sin(t)**3

def y_func(t):
    # 예시: 하트 모양 곡선의 y(t)
    return 13 * np.cos(t) - 5 * np.cos(2*t) - 2 * np.cos(3*t) - np.cos(4*t)

# t의 범위 설정 (기본 0 ~ 2*pi) 및 점의 개수(촘촘할수록 정확함)
t_vals = np.linspace(0, 2 * np.pi, 2000)

# 점들을 생성하고 Shapely의 선(LineString) 객체로 변환
points = [(x_func(t), y_func(t)) for t in t_vals]
curve = LineString(points)

# ==========================================
# 2. 격자 변수 및 자동 크기 조절(Auto-scaling)
# ==========================================
r = 1.0  # 격자 선 사이의 간격 (곡선 크기에 맞춰 적절히 조절하세요)
d_theta = np.pi / 4  # 각도 간격 (기본 4방향)
angles = np.arange(0, np.pi, d_theta) 

# 곡선의 바운딩 박스(크기)를 파악해서 그물망 범위를 자동으로 계산합니다!
minx, miny, maxx, maxy = curve.bounds
max_radius = np.sqrt(max(abs(minx), abs(maxx))**2 + max(abs(miny), abs(maxy))**2)
k_max = int(np.ceil(max_radius / r)) + 1
k_vals = np.arange(-k_max, k_max + 1)
line_length = max_radius * 2.5 # 직선이 화면을 충분히 덮도록 길이 설정

# ==========================================
# 3. 교점 계산 및 시각화
# ==========================================
total_intersections = 0
fig, ax = plt.subplots(figsize=(8, 8))

# 매개변수 곡선 그리기
x_coords, y_coords = curve.xy
ax.plot(x_coords, y_coords, color='blue', linewidth=2, label="Parametric Curve")

# 무작위 선을 긋고 '정확한 교점' 찾기
for theta in angles:
    for k in k_vals:
        # 직선의 중심점과 방향 계산
        pt_x, pt_y = k * r * np.cos(theta), k * r * np.sin(theta)
        dir_x, dir_y = -np.sin(theta), np.cos(theta)
        
        # 선분 생성
        line = LineString([(pt_x - line_length*dir_x, pt_y - line_length*dir_y),
                           (pt_x + line_length*dir_x, pt_y + line_length*dir_y)])
        
        # 교점 계산
        intersection = curve.intersection(line)
        
        # 교점이 존재하면 카운트하고 점 찍기
        if not intersection.is_empty:
            ax.plot(*line.xy, color='gray', alpha=0.3) # 직선 그리기
            
            # 교점이 1개일 때
            if intersection.geom_type == 'Point':
                total_intersections += 1
                ax.plot(intersection.x, intersection.y, 'ro', markersize=3)
            # 교점이 여러 개일 때
            elif intersection.geom_type in ['MultiPoint', 'GeometryCollection']:
                for geom in intersection.geoms:
                    if geom.geom_type == 'Point':
                        total_intersections += 1
                        ax.plot(geom.x, geom.y, 'ro', markersize=3)

# 화면 출력
plt.axis('equal')
plt.title(f"Cauchy-Crofton Formula Simulation\nTotal Intersections (n): {total_intersections}")
plt.show()

# ==========================================
# 4. 코시-크로프튼 공식 결과 출력
# ==========================================
L = 0.5 * total_intersections * r * d_theta

print(f"====================================")
print(f"🎯 자동으로 세어진 교점 개수(n): {total_intersections}개")
print(f"📏 코시-크로프튼 추정 길이(L): {L:.4f}")
print(f"====================================")
