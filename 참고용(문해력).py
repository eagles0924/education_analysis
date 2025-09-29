from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# import koreanize_matplotlib # 한글 폰트 

# 경고 메시지(DtypeWarning) 숨김 설정
import warnings
warnings.filterwarnings('ignore', category=pd.errors.DtypeWarning)

BASE = Path(__file__).parent

# ===== 파일 경로 =====
FILE_23 = BASE / "23학년도 A세트 전체학년.csv"
FILE_24 = BASE / "24학년도 A세트 전체학년.csv"

# ===== 매핑 (원본 코드 유지) =====
# 2023 (컬럼 접두사: sk; 8학년=코드 2, 10학년=코드 1)
mapping_2023 = {
    4: {
        "어휘력":[1,2,13,23,14,29,35],
        "탐색 및 확인":[3,5,8,11,14,17,21,24,27,30,33,36],
        "통합 및 해석":[6,9,12,15,18,20,22,28,31,37],
        "평가 및 적용":[4,7,10,16,19,26,32,34,38],
    },
    6: {
        "어휘력":[1,2,3,4,17,23,27,36],
        "탐색 및 확인":[5,8,11,14,19,22,24,28,30,32,34,37,38],
        "통합 및 해석":[6,9,12,15,18,21,25,29,31,33,39],
        "평가 및 적용":[7,10,13,16,20,26,35,40],
    },
    2: {  # 8학년(중2)
        "어휘력":[1,3,17,25,28,30,36,44],
        "탐색 및 확인":[2,5,8,12,15,20,23,27,31,33,37,38,41],
        "통합 및 해석":[4,6,9,10,13,16,18,21,24,32,34,39,42],
        "평가 및 적용":[7,11,14,19,22,26,29,35,40,43],
    },
    1: {  # 10학년(고1)
        "어휘력":[1,2,3,15,23,26,31,38,42,46],
        "탐색 및 확인":[4,8,12,16,17,20,24,28,33,35,36,39,44],
        "통합 및 해석":[7,9,10,13,14,22,25,29,32,37,40,41,43],
        "평가 및 적용":[5,6,11,18,19,21,27,30,34,45],
    },
}

# 2024 (컬럼 접두사: 문해력; 8학년=8, 10학년=10)
mapping_2024 = {
    4: {
        "어휘력":[3,5,8,11,22,34,37],
        "탐색 및 확인":[1,4,7,10,13,17,20,23,26,29,30,32],
        "통합 및 해석":[2,6,12,14,15,18,21,24,27,28,31,35],
        "평가 및 적용":[9,16,19,25,33,36,38],
    },
    6: {
        "어휘력":[6,9,15,17,23,27,34,36],
        "탐색 및 확인":[2,3,5,8,11,14,18,25,28,30,32,35],
        "통합 및 해석":[1,4,13,16,19,21,26,29,31,37,39],
        "평가 및 적용":[7,10,12,20,22,24,33,38,40],
    },
    8: {
        "어휘력":[2,8,15,18,23,35,36,40],
        "탐색 및 확인":[1,4,7,11,14,20,24,27,30,32,37,42],
        "통합 및 해석":[3,5,9,12,17,21,25,28,31,33,39,43],
        "평가 및 적용":[6,10,13,16,19,22,26,29,34,38,41,44],
    },
    10: {
        "어휘력":[7,13,22,25,32,36,40,46],
        "탐색 및 확인":[1,9,12,17,20,27,28,31,35],
        "통합 및 해석":[2,4,5,6,10,11,14,16,18,21,24,29,33,34,38,39,41,43,44,45],
        "평가 및 적용":[3,8,15,19,23,26,30,37,42],
    },
}

# ===== 영역별 색상 (수정됨) =====
AREA_COLORS = {
    "어휘력": "#4C78A8",         # 파랑 (Vega)
    "탐색 및 확인": "#F58518", # 주황 (Vega)
    "통합 및 해석": "#54A24B", # 초록 (Vega)
    "평가 및 적용": "#D9C168", # 노란색
}

def area_scores(df, area_numbers, prefix):
    cols = [f"{prefix}{n:02d}" for n in area_numbers if f"{prefix}{n:02d}" in df.columns]
    if not cols:
        return None
    # 정답/오답(1/0)의 평균이 정답률(0~1)
    return df[cols].mean(axis=1, skipna=True).dropna()

def get_scores_df(df, grade_code, mapping, prefix):
    df_g = df[df["학년"] == grade_code]
    data = {}
    for area, nums in mapping[grade_code].items():
        s = area_scores(df_g, nums, prefix)
        if s is not None:
            data[area] = s.values
    return pd.DataFrame(data)

def plot_single_year_grade(df_scores, year, grade, outpath):
    labels = list(df_scores.columns)
    data = [df_scores[c].dropna().values for c in labels]

    fig, ax = plt.subplots(figsize=(8,6)) # Figure와 Axes 객체를 함께 생성
    
    # 바이올린 플롯 그리기
    v = ax.violinplot(data, showmeans=False, showmedians=True, showextrema=False)

    # 개별 바이올린 색상, 테두리 지정 
    for body, lab in zip(v['bodies'], labels):
        body.set_facecolor(AREA_COLORS.get(lab, "#777777"))
        body.set_alpha(0.7)
        # 테두리 설정
        body.set_edgecolor('black') 
        body.set_linewidth(0.8)

    # 내부 박스(이상치 숨김)
    # 중앙값(median) 표시를 위해 박스 플롯을 겹쳐 사용
    ax.boxplot(data, widths=0.1, showfliers=False, medianprops=dict(color="black"))

    # Q1, Q2, Q3 수치 표시 (추가됨)
    for i, d in enumerate(data):
        q1, median, q3 = np.percentile(d, [25, 50, 75])
        x = i + 1 # 바이올린의 x 위치 (1부터 시작)
        
        # 텍스트 오프셋 설정 
        offset_y_q1 = 0.03
        offset_y_q2 = 0.03
        offset_y_q3 = 0.03
        offset_x_text = 0.15

        # Q1 (25th percentile) 표시
        ax.text(x + offset_x_text, q1 - offset_y_q1, f"Q1={q1:.2f}",
                color='blue', va='center', ha='left', fontsize=9)
        # Q2 (Median, 50th percentile) 표시
        ax.text(x + offset_x_text, median - offset_y_q2, f"Q2={median:.2f}",
                color='red', va='center', ha='left', fontsize=9)
        # Q3 (75th percentile) 표시
        ax.text(x + offset_x_text, q3 + offset_y_q3, f"Q3={q3:.2f}",
                color='green', va='center', ha='left', fontsize=9)

    # Axes 꾸미기
    ax.set_xticks(np.arange(1, len(labels)+1), labels, rotation=10)
    ax.set_ylabel("정답률")
    ax.set_ylim(0, 1.05)
    
    # 제목 형식 변경
    ax.set_title(f"{year}학년도 문해력 영역별 정답률 분포 ({grade}학년)")
    
    # 플롯 주변 테두리 제거 
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # y축 그리드 추가 및 바이올린 뒤로 배치
    ax.grid(True, linestyle='--', alpha=0.6, axis='y')
    ax.set_axisbelow(True)

    plt.tight_layout()
    plt.savefig(outpath, dpi=220)
    plt.close()

def main():
    # 데이터 로드 
    df23 = pd.read_csv(FILE_23, encoding="utf-8-sig")
    df24 = pd.read_csv(FILE_24, encoding="utf-8-sig")

    # 2023: 학년 코드 주의(8→2, 10→1)
    jobs_2023 = [(2023, 4, 4), (2023, 6, 6), (2023, 8, 2), (2023, 10, 1)]
    for year, disp_grade, code in jobs_2023:
        scores = get_scores_df(df23, code, mapping_2023, prefix="sk")
        out = BASE / f"violin_{year}_{disp_grade}th.png"
        plot_single_year_grade(scores, year, disp_grade, out)

    # 2024: 학년 코드 그대로(8, 10)
    jobs_2024 = [(2024, 4, 4), (2024, 6, 6), (2024, 8, 8), (2024, 10, 10)]
    for year, disp_grade, code in jobs_2024:
        scores = get_scores_df(df24, code, mapping_2024, prefix="문해력")
        out = BASE / f"violin_{year}_{disp_grade}th.png"
        plot_single_year_grade(scores, year, disp_grade, out)

    print("완료! violin_2023_4th/6th/8th/10th.png, violin_2024_4th/6th/8th/10th.png 생성됨.")

if __name__ == "__main__":
    main()