import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import LineString, box

# ==========================================
# 매개변수 곡선
# ==========================================

def x_func(t):
    return 10*(t-np.sin(t))
def y_func(t):
    return 10*(1-np.cos(t))

t_vals = np.linspace(0, 2 * np.pi, 10000)

# 점들을 생성하고 Shapely의 선(LineString) 객체로 변환
points = [(x_func(t), y_func(t)) for t in t_vals]
curve = LineString(points)

# ==========================================
# 10% 여백이 적용된 바운딩 박스
# ==========================================
minx, miny, maxx, maxy = curve.bounds
curve_width = maxx - minx
curve_height = maxy - miny

# 곡선의 너비/높이 중 큰 값의 10%를 버퍼(여백)로 설정
margin = max(curve_width, curve_height) * 0.1 
if margin == 0: margin = 1

# 10% 확장된 새로운 화면 영역 (b_ = buffered)
b_minx, b_maxx = minx - margin, maxx + margin
b_miny, b_maxy = miny - margin, maxy + margin

# 격자를 그릴 '10% 여백 박스(Polygon)' 객체 생성
grid_box = box(b_minx, b_miny, b_maxx, b_maxy)
box_corners = list(grid_box.exterior.coords) # 박스의 4개 꼭짓점

# ==========================================
# 격자
# ==========================================
r = 1.0  # 격자 간격
d_theta = np.pi / 4  # 각도 간격
angles = np.arange(0, np.pi, d_theta) 

total_intersections = 0
fig, ax = plt.subplots(figsize=(10, 6))

# 매개변수 곡선 그리기
x_coords, y_coords = curve.xy
ax.plot(x_coords, y_coords, color='blue', linewidth=2, label="Parametric Curve", zorder=2)

diag_length = np.sqrt((b_maxx - b_minx)**2 + (b_maxy - b_miny)**2)

# ==========================================
# 교점 계산 및 시각화
# ==========================================

# 무작위 선을 긋고 '정확한 교점' 찾기
for theta in angles:
    projections = [x * np.cos(theta) + y * np.sin(theta) for x, y in box_corners]
    p_min, p_max = min(projections), max(projections)

    k_vals = np.arange(np.floor(p_min / r), np.ceil(p_max / r) + 1)
    for k in k_vals:
        p = k * r
        # 직선 위의 기준점과 방향
        pt_x, pt_y = p * np.cos(theta), p * np.sin(theta)
        dir_x, dir_y = -np.sin(theta), np.cos(theta)
        
        # 선분 생성
        line = LineString([(pt_x - diag_length*dir_x, pt_y - diag_length*dir_y),
                           (pt_x + diag_length*dir_x, pt_y + diag_length*dir_y)])

        clipped_line = line.intersection(grid_box)
        
        if not clipped_line.is_empty:
            if clipped_line.geom_type == 'LineString':
                ax.plot(*clipped_line.xy, color='dimgray', alpha=0.8, linewidth=0.7, zorder=1)
            elif clipped_line.geom_type == 'MultiLineString':
                for geom in clipped_line.geoms:
                    ax.plot(*geom.xy, color='dimgray', alpha=0.8, linewidth=0.7, zorder=1)
        
        # 교점 계산 (원래 곡선과 만나는 점)
        intersection = curve.intersection(line)
        
        # 교점이 존재하면 카운트하고 빨간 점 찍기
        if not intersection.is_empty:
            if intersection.geom_type == 'Point':
                total_intersections += 1
                ax.plot(intersection.x, intersection.y, 'ro', markersize=1, zorder=3)
            elif intersection.geom_type in ['MultiPoint', 'GeometryCollection']:
                for geom in intersection.geoms:
                    if geom.geom_type == 'Point':
                        total_intersections += 1
                        ax.plot(geom.x, geom.y, 'ro', markersize=1, zorder=3)

ax.set_aspect('equal')

curve_width = maxx - minx
curve_height = maxy - miny

margin = max(curve_width, curve_height) * 0.1 

if margin == 0:
    margin = 1

ax.set_xlim(minx - margin, maxx + margin)
ax.set_ylim(miny - margin, maxy + margin)

# ==========================================
# 출력
# ==========================================
L = 0.5 * total_intersections * r * d_theta

true_L = curve.length

error_rate = (L - true_L) / true_L * 100

print(f"====================================")
print(f"교점 수(n): {total_intersections}개")
print(f"코시-크로프턴 근사: {L:.4f}")
print(f"실제 길이: {true_L:.4f}")
print(f"오차율: {error_rate:.2f}%")
print(f"====================================")
