import time

EPSILON = 1e-9
REPEAT = 10


def mac(pattern, filt):
    """두 n×n 배열을 같은 위치끼리 곱한 뒤 모두 더한다."""
    total = 0.0
    n = len(pattern)
    for i in range(n):
        for j in range(n):
            total += pattern[i][j] * filt[i][j]
    return total


def judge(score_a, score_b, label_a, label_b):
    """두 점수를 비교한다. 차이가 EPSILON보다 작으면 동점으로 본다."""
    if abs(score_a - score_b) < EPSILON:
        return "UNDECIDED"
    if score_a > score_b:
        return label_a
    return label_b


LABEL_MAP = {
    "+": "Cross",
    "cross": "Cross",
    "x": "X",
}


def normalize_label(raw):
    """여러 형태의 라벨을 표준 라벨(Cross/X)로 바꾼다. 모르는 라벨이면 None."""
    key = str(raw).strip().lower()
    return LABEL_MAP.get(key)


# ===== 단계 B: 모드 1 =====

def section(title):
    print()
    print("#" + "-" * 40)
    print("# " + title)
    print("#" + "-" * 40)


def read_matrix(title, n=3):
    """n줄을 입력받아 n×n 배열로 만든다. 형식이 틀린 줄은 다시 입력받는다."""
    print(f"{title} ({n}줄 입력, 공백 구분)")
    rows = []
    while len(rows) < n:
        parts = input().split()
        if len(parts) != n:
            print(f"입력 형식 오류: 각 줄에 {n}개의 숫자를 공백으로 구분해 입력하세요. "
                  f"({len(rows) + 1}번째 줄 다시 입력)")
            continue
        try:
            row = [float(p) for p in parts]
        except ValueError:
            print(f"입력 형식 오류: 숫자만 입력하세요. ({len(rows) + 1}번째 줄 다시 입력)")
            continue
        rows.append(row)
    return rows


def measure_mac_ms(pattern, filt, repeat=REPEAT):
    """MAC 연산을 repeat번 반복해 1회 평균 시간(ms)을 돌려준다."""
    start = time.perf_counter()
    for _ in range(repeat):
        mac(pattern, filt)
    end = time.perf_counter()
    return (end - start) * 1000 / repeat


def print_perf_table(results):
    """results: [(n, 평균ms), ...]"""
    print(f"{'크기':<10}{'평균 시간(ms)':>14}{'연산 횟수':>12}")
    print("-" * 40)
    for n, ms in results:
        print(f"{f'{n}×{n}':<10}{ms:>14.4f}{n * n:>12}")


def run_mode1():
    section("[1] 필터 입력")
    filter_a = read_matrix("필터 A")
    print()
    filter_b = read_matrix("필터 B")
    print()
    print("✓ 필터 A, B 저장 완료")

    section("[2] 패턴 입력")
    pattern = read_matrix("패턴")

    section("[3] MAC 결과")
    score_a = mac(pattern, filter_a)
    score_b = mac(pattern, filter_b)
    avg_ms = measure_mac_ms(pattern, filter_a)
    result = judge(score_a, score_b, "A", "B")

    print(f"A 점수: {score_a}")
    print(f"B 점수: {score_b}")
    print(f"연산 시간(평균/{REPEAT}회): {avg_ms:.4f} ms")
    if result == "UNDECIDED":
        print(f"판정: 판정 불가 (|A-B| < {EPSILON})")
    else:
        print(f"판정: {result}")

    section(f"[4] 성능 분석 (평균/{REPEAT}회)")
    print_perf_table([(3, avg_ms)])


def main():
    print("=== Mini NPU Simulator ===")
    print()
    print("[모드 선택]")
    print("1. 사용자 입력 (3x3)")
    print("2. data.json 분석")
    while True:
        choice = input("선택: ").strip()
        if choice == "1":
            run_mode1()
            break
        if choice == "2":
            print("(단계 C에서 구현 예정)")
            break
        print("1 또는 2를 입력하세요.")


if __name__ == "__main__":
    main()