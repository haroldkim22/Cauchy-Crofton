# Cauchy-Crofton

코시-크로프턴 공식을 이용하여 평면 곡선의 길이를 추정하는 프로젝트입니다.

## 프로젝트 개요

이 저장소는 **코시-크로프턴 공식(Cauchy-Crofton Formula)**을 구현하고 검증하는 파이썬 코드들을 포함합니다. 코시-크로프턴 공식은 곡선과 무작위 직선 격자의 교점 개수로부터 곡선의 길이를 추정할 수 있는 수학 정리입니다.

## 코드 구조

### 1️⃣ **기본 구현** (CC_ver1.py, CC_ver2.py)

매개변수 곡선(Parametric Curve)을 정의하고, 규칙적인 격자 직선들과의 교점을 계산하여 곡선의 길이를 추정합니다.

**주요 기능:**
- 사용자 정의 매개변수 곡선 설정
- 다양한 각도와 간격의 격자 구성
- 교점 개수로부터 곡선 길이 추정
- 시각화 (matplotlib 사용)

**차이점:**
- `CC_ver1.py`: 기본적인 구현
- `CC_ver2.py`: 바운딩 박스 최적화 추가

### 2️⃣ **오차 분석** (CC_sweep_ver1.py, CC_sweep_visualize.py, CC_sweep_only.py)

격자 간격과 각도 간격을 변화시키면서 추정 오차율을 분석하고 시각화합니다.

**주요 기능:**
- 여러 매개변수 조합에 대한 오차율 계산
- 격자 간격(`k`)과 각도 간격(`d_theta`)의 영향 분석
- 오차 그래프 시각화
- 성능 최적화 (경계 상자 교차 사전 확인)

## 필요 라이브러리

```bash
pip install numpy matplotlib shapely
```

## 사용 방법

1. 매개변수 곡선 정의하기:
```python
def x_func(t):
    return 10 * (t - np.sin(t))  # 예: 사이클로이드

def y_func(t):
    return 10 * (1 - np.cos(t))
```

2. 스크립트 실행:
```bash
python CC_ver1.py        # 기본 구현
python CC_sweep_ver1.py  # 오차 분석
```

## 주요 특징

- 📊 **정확한 교점 계산**: Shapely 라이브러리를 사용한 기하학 연산
- ⚡ **최적화**: AABB(Axis-Aligned Bounding Box)를 이용한 성능 개선
- 📈 **오차 분석**: 다양한 격자 조건에서 추정 정확도 평가
- 🎨 **시각화**: 곡선과 격자, 교점을 명확하게 표시
