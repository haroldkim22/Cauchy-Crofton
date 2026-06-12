# Cauchy-Crofton

## 개요
**코시-크로프턴 공식(Cauchy-Crofton Formula)** 을 이용하여 평면 곡선의 길이를 추정하고, 설정값에 따른 오차율을 분석하는 코드.

## 코드 구조

### 1️⃣ **기본 구현** (CC_ver1.py, CC_ver2.py)

매개변수 곡선을 정의하고, 규칙적인 격자 직선들과의 교점을 계산하여 곡선의 길이를 추정합니다.

**주요 기능:**
- 사용자 정의 매개변수 곡선 설정
- 다양한 각도와 간격의 격자 구성
- 교점 개수로부터 곡선 길이 추정
- 시각화 (matplotlib)

**차이점:**
- `CC_ver1.py`: AI가 제시한 초기 버전
- `CC_ver2.py`: 최종 버전 --> **그냥 이거 쓰세요**

### 2️⃣ **오차 분석** (CC_sweep_ver1.py, CC_sweep_only.py, CC_sweep_visualize.py)

격자 간격과 각도 간격을 변화시키면서 추정 오차율을 분석하고 시각화합니다.

**주요 기능:**
- 여러 매개변수 조합에 대한 오차율 계산
- 상대적 격자 간격(`k`)과 각도 간격(`d_theta`)의 영향 분석
- 오차 그래프 시각화

**차이점:**
- `CC_sweep_ver1.py`: AI가 제시한 초기 버전
- `CC_sweep_only.py`: 변수별로 sweep 후 오차율 분포만 도출함
- `CC_sweep_visualize.py`: 변수별로 sweep 후 오차율 분포 및 몇몇 샘플들을 시각화함 --> **그냥 이거 쓰세요**

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

2. 변수 sweep 범위 설정:
각도 간격은 사용 가능한 값이 제한되어 있기에 굳이 변경하지 마세요
```python
K_START = 0.02    
K_END   = 0.50     
K_STEPS = 30

d_theta_vals = np.array([
    np.pi/12, np.pi/10, np.pi/8, np.pi/7, np.pi/6,
    np.pi/5, np.pi/4, np.pi/3, np.pi/2
])
```


2. 스크립트 실행:
```bash
python CC_ver1.py        # 기본 구현
python CC_sweep_ver1.py  # 오차 분석
```

