import json
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


# ===== 단계 C: 모드 2 (data.json) =====

def generate_pattern(n, kind):
    """n×n 십자가(Cross) 또는 X 패턴을 자동 생성한다. n은 홀수를 가정한다."""
    mid = n // 2
    grid = []
    for i in range(n):
        row = []
        for j in range(n):
            if kind == "Cross":
                on = (i == mid or j == mid)
            else:
                on = (i == j or i + j == n - 1)
            row.append(1.0 if on else 0.0)
        grid.append(row)
    return grid


def has_shape(m, n):
    """m이 n×n 모양의 2차원 리스트인지 확인한다."""
    if not isinstance(m, list) or len(m) != n:
        return False
    for row in m:
        if not isinstance(row, list) or len(row) != n:
            return False
    return True


def all_numbers(m):
    """2차원 리스트의 모든 값이 숫자인지 확인한다."""
    for row in m:
        for v in row:
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                return False
    return True


def matrix_size(m):
    """2차원 리스트의 '행×열' 크기를 문자열로 돌려준다 (오류 메시지용)."""
    if not isinstance(m, list):
        return "배열 아님"
    cols = len(m[0]) if m and isinstance(m[0], list) else 0
    return f"{len(m)}×{cols}"


def parse_size_key(key, prefix_parts):
    """'size_13' 또는 'size_13_2'에서 13을 뽑는다. 형식이 틀리면 None."""
    parts = key.split("_")
    if len(parts) != prefix_parts or parts[0] != "size":
        return None
    try:
        return int(parts[1])
    except ValueError:
        return None


def load_filters(raw_filters):
    """filters 영역을 읽어 {n: {'Cross': 배열, 'X': 배열}} 형태로 정리한다."""
    filters = {}
    for key, pair in raw_filters.items():
        n = parse_size_key(key, 2)
        if n is None or not isinstance(pair, dict):
            print(f"✗ {key}: 필터 키 형식 오류 → 건너뜀")
            continue
        normalized = {}
        for label_key, grid in pair.items():
            label = normalize_label(label_key)
            if label is None:
                print(f"✗ {key}.{label_key}: 알 수 없는 필터 라벨 → 건너뜀")
            elif not has_shape(grid, n):
                print(f"✗ {key}.{label_key}: {n}×{n}이 아님 ({matrix_size(grid)}) → 건너뜀")
            elif not all_numbers(grid):
                print(f"✗ {key}.{label_key}: 숫자가 아닌 값 포함 → 건너뜀")
            else:
                normalized[label] = grid
        if "Cross" in normalized and "X" in normalized:
            filters[n] = normalized
            print(f"✓ {key:<8} 필터 로드 완료 (Cross, X)")
        else:
            print(f"✗ {key}: Cross/X 필터가 모두 있어야 함 → 사용 불가")
    return filters


def analyze_case(key, case, filters):
    """패턴 한 건을 분석한다. (통과 여부, 실패 사유)를 돌려준다."""
    print(f"--- {key} ---")

    def fail(reason):
        print(f"FAIL: {reason}")
        return False, reason

    n = parse_size_key(key, 3)
    if n is None:
        return fail("키 형식 오류 (size_N_idx 형식이 아님)")
    if n not in filters:
        return fail(f"size_{n} 필터가 없음")
    if not isinstance(case, dict) or "input" not in case or "expected" not in case:
        return fail("스키마 오류 (input 또는 expected 없음)")

    pattern = case["input"]
    if not has_shape(pattern, n):
        return fail(f"크기 불일치 (패턴 {matrix_size(pattern)}, 필터 {n}×{n})")
    if not all_numbers(pattern):
        return fail("데이터 오류 (숫자가 아닌 값 포함)")

    expected = normalize_label(case["expected"])
    if expected is None:
        return fail(f"알 수 없는 expected 라벨: {case['expected']!r}")

    score_cross = mac(pattern, filters[n]["Cross"])
    score_x = mac(pattern, filters[n]["X"])
    result = judge(score_cross, score_x, "Cross", "X")

    print(f"Cross 점수: {score_cross}")
    print(f"X 점수: {score_x}")

    if result == expected:
        print(f"판정: {result} | expected: {expected} | PASS")
        return True, ""
    if result == "UNDECIDED":
        print(f"판정: {result} | expected: {expected} | FAIL (동점 규칙)")
        return False, f"동점(UNDECIDED) 처리 규칙에 따라 FAIL (|차이| = {abs(score_cross - score_x):.2e})"
    print(f"판정: {result} | expected: {expected} | FAIL")
    return False, f"판정 불일치 (판정 {result}, expected {expected})"


def run_mode2(path="data.json"):
    section("[1] 필터 로드")
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"오류: {path} 파일을 찾을 수 없습니다. main.py와 같은 폴더에서 실행하세요.")
        return
    except json.JSONDecodeError as e:
        print(f"오류: {path}의 JSON 형식이 잘못되었습니다. ({e})")
        return

    filters = load_filters(data.get("filters", {}))

    section("[2] 패턴 분석 (라벨 정규화 적용)")
    total = 0
    passed = 0
    failures = []
    for key, case in data.get("patterns", {}).items():
        total += 1
        ok, reason = analyze_case(key, case, filters)
        if ok:
            passed += 1
        else:
            failures.append((key, reason))

    section(f"[3] 성능 분석 (평균/{REPEAT}회)")
    results = []
    for n in (3, 5, 13, 25):
        pattern = generate_pattern(n, "Cross")
        filt = generate_pattern(n, "Cross")
        results.append((n, measure_mac_ms(pattern, filt)))
    print_perf_table(results)

    section("[4] 결과 요약")
    print(f"총 테스트: {total}개")
    print(f"통과: {passed}개")
    print(f"실패: {len(failures)}개")
    if failures:
        print()
        print("실패 케이스:")
        for key, reason in failures:
            print(f"- {key}: {reason}")
    print()
    print('(상세 원인 분석 및 복잡도 설명은 README.md의 "결과 리포트" 섹션에 작성)')


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
            run_mode2()
            break
        print("1 또는 2를 입력하세요.")


if __name__ == "__main__":
    main()