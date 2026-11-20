from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from html import escape

import streamlit as st


st.set_page_config(
    page_title="위기의 구단! 우리 팀의 약점을 보완하라!",
    page_icon="⚾",
    layout="wide",
)

PLAYERS = {
    "김영웅": {"at_bats": 25, "hits": 10, "walks": 0},
    "안현민": {"at_bats": 30, "hits": 10, "walks": 10},
}
GOALS = {
    "안타를 잘 치는 선수": {
        "icon": "⚾",
        "description": "안타를 많이 치는 선수를 영입하고 싶어요.",
        "metric": "타율",
        "candidate": "김영웅",
    },
    "출루를 잘하는 선수": {
        "icon": "🧤",
        "description": "안타뿐 아니라 볼넷으로도 출루를 잘하는 선수를 영입하고 싶어요.",
        "metric": "출루율",
        "candidate": "안현민",
    },
}
THREE_PLACES = Decimal("0.001")


def rate_for(player: str, metric: str) -> Decimal:
    record = PLAYERS[player]
    if metric == "타율":
        numerator, denominator = record["hits"], record["at_bats"]
    else:
        numerator = record["hits"] + record["walks"]
        denominator = record["at_bats"] + record["walks"]
    return Decimal(numerator) / Decimal(denominator)


def displayed_rate(value: Decimal) -> str:
    return f"{value.quantize(THREE_PLACES, rounding=ROUND_HALF_UP):.3f}"


def format_ratio(player: str, metric: str) -> str:
    record = PLAYERS[player]
    if metric == "타율":
        return f'{record["hits"]} ÷ {record["at_bats"]}'
    return (
        f'({record["hits"]} + {record["walks"]}) ÷ '
        f'({record["at_bats"]} + {record["walks"]})'
    )


def init_state() -> None:
    defaults = {
        "stage": "intro",
        "goal": None,
        "calculation_correct": {"김영웅": False, "안현민": False},
        "calculation_submitted": False,
        "comparison_correct": False,
        "decimal_correct": [False, False, False],
        "decimal_submitted": False,
        "recruited_candidate": None,
        "final_player": None,
        "final_metric": None,
        "reason": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_metric() -> str:
    return GOALS[st.session_state.goal]["metric"]


def render_player_card(player: str) -> None:
    record = PLAYERS[player]
    st.markdown(
        f"""
        <div class="player-card">
          <div class="player-name">⚾ {player} 선수</div>
          <div class="record-grid">
            <div><span>타수</span><strong>{record["at_bats"]}</strong></div>
            <div><span>안타</span><strong>{record["hits"]}</strong></div>
            <div><span>볼넷</span><strong>{record["walks"]}</strong></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.markdown(
        '<div class="top-ball">⚾ 2026 DREAM LEAGUE · 우리 구단 문제 해결단</div>',
        unsafe_allow_html=True,
    )
    st.title("위기의 구단! 우리 팀의 약점을 보완하라!")
    stage_order = [
        "intro",
        "goal",
        "analysis",
        "compare",
        "decimals",
        "signing",
        "final_pick",
        "report",
    ]
    stage_labels = ["작전 회의", "영입 목표", "기록 분석", "선수 비교", "소수 미션", "후보 등록", "최종 선택", "보고서"]
    current_index = stage_order.index(st.session_state.stage)
    if st.session_state.stage != "intro":
        steps = "　›　".join(
            f"**{label}**" if i == current_index else label
            for i, label in enumerate(stage_labels)
        )
        st.markdown(f'<div class="step-strip">{steps}</div>', unsafe_allow_html=True)
        st.progress(current_index / (len(stage_order) - 1))
    goal = st.session_state.goal
    status = GOALS[goal]["description"] if goal else "아직 영입 목표를 정하지 않았어요."
    st.markdown(
        f'<div class="goal-banner">🎯 현재 영입 목표　{status}</div>',
        unsafe_allow_html=True,
    )
    st.divider()


def render_intro() -> None:
    st.markdown(
        """
        <div class="hero-card">
          <div class="hero-label">⚠️ 감독님의 긴급 작전 지시</div>
          <h2>큰일 났어요! 우리 구단이 위기에 빠졌습니다!</h2>
          <p>최근 우리 팀은 득점 기회를 많이 놓치고 있습니다. 안타를 잘 치는 선수도 부족하고, 볼넷을 얻어 출루하는 선수도 많지 않습니다.</p>
          <p>다음 시즌 우승을 위해서는 우리 팀에 꼭 필요한 새로운 타자를 영입해야 합니다.</p>
          <p>감독님은 여러분에게 특별한 임무를 맡겼습니다.</p>
          <blockquote>“우리 팀의 약점을 파악하고, 그 약점을 보완할 선수를 찾아라! 단순히 기록이 높은 선수가 아니라 우리 팀에 정말 필요한 선수를 선택해야 한다!”</blockquote>
          <p>여러분은 이제 우리 구단의 문제 해결단입니다.</p>
          <p class="hero-last">과연 우리 팀을 위기에서 구해낼 수 있을까요?</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.info("기록을 직접 계산하고 비교해 우리 팀에 필요한 능력을 찾아보세요!")
    if st.button("⚾ 게임 시작하기", type="primary", use_container_width=True):
        st.session_state.stage = "goal"
        st.rerun()


def render_goal() -> None:
    st.header("1회말 | 우리 팀에 필요한 선수는?")
    st.markdown(
        '<div class="coach-bubble">“먼저 우리 팀을 어떤 능력으로 강하게 만들지 작전 목표를 정해 보자!”</div>',
        unsafe_allow_html=True,
    )
    left, right = st.columns(2)
    for column, goal in zip((left, right), GOALS):
        with column:
            detail = GOALS[goal]
            st.markdown(
                f"""
                <div class="choice-card">
                  <div class="choice-icon">{detail["icon"]}</div>
                  <h3>{goal}</h3>
                  <p>{detail["description"]}</p>
                  <div class="metric-tag">활용할 지표: {detail["metric"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(
                f"{goal} 선택하기",
                key=f"goal_{goal}",
                type="primary",
                use_container_width=True,
            ):
                st.session_state.goal = goal
                st.session_state.stage = "analysis"
                st.rerun()


def render_analysis() -> None:
    metric = get_metric()
    st.header("2회말 | 선수 기록을 분석하라")
    if metric == "타율":
        question = "두 선수의 안타 수는 같지만, 누가 안타를 더 잘 치는 선수일까요?"
        formula = "타율 = 안타 수 ÷ 타수"
        explanation = "타율은 타수 중 안타를 친 비율을 나타내요. 볼넷은 타율 계산 시에는 이용하지 않아요."
    else:
        question = "안타 수가 같더라도 볼넷을 많이 얻는 선수는 더 많이 출루할 수 있을까요?"
        formula = "출루율 = (안타 수 + 볼넷) ÷ (타수 + 볼넷)"
        explanation = "출루율은 안타와 볼넷으로 출루한 비율이에요."
    st.markdown(f'<div class="coach-bubble">“{question}”</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="formula-box"><strong>{formula}</strong><br>{explanation}</div>', unsafe_allow_html=True)
    first, second = st.columns(2)
    with first:
        render_player_card("김영웅")
    with second:
        render_player_card("안현민")
    st.subheader(f"직접 계산하기 | {metric}")
    st.caption("각 선수의 계산 결과를 소수로 입력해 보세요. 소수 셋째 자리까지의 값으로 확인합니다. 예: 0.400")
    with st.form("calculation_form"):
        cols = st.columns(2)
        answers: dict[str, str] = {}
        for column, player in zip(cols, PLAYERS):
            with column:
                st.markdown(f"**{player} 선수**")
                st.markdown(f"`{format_ratio(player, metric)} = ?`")
                answers[player] = st.text_input(
                    f"{player} 선수의 {metric}",
                    key=f"answer_{metric}_{player}",
                    placeholder="예: 0.400",
                )
        submitted = st.form_submit_button("계산 결과 확인하기", type="primary", use_container_width=True)
    if submitted:
        correct = {}
        for player, raw_answer in answers.items():
            try:
                parsed = Decimal(raw_answer.strip())
                if not parsed.is_finite() or parsed < 0 or parsed > 1:
                    raise InvalidOperation
                rounded = parsed.quantize(THREE_PLACES, rounding=ROUND_HALF_UP)
                expected = rate_for(player, metric).quantize(
                    THREE_PLACES, rounding=ROUND_HALF_UP
                )
                correct[player] = rounded == expected
            except (InvalidOperation, ValueError):
                correct[player] = False
        st.session_state.calculation_correct = correct
        st.session_state.calculation_submitted = True
    if st.session_state.calculation_submitted:
        feedback = st.columns(2)
        for column, player in zip(feedback, PLAYERS):
            with column:
                if st.session_state.calculation_correct[player]:
                    st.success(
                        f'{player} 선수 정답! {format_ratio(player, metric)} = '
                        f'**{displayed_rate(rate_for(player, metric))}**'
                    )
                else:
                    st.warning(f"{player} 선수의 계산을 다시 확인해 보세요.")
    if all(st.session_state.calculation_correct.values()):
        st.success("두 선수의 계산을 모두 마쳤어요! 실제 비교에서는 반올림하기 전의 값을 사용합니다.")
        if st.button("계산 결과 비교하기", type="primary", use_container_width=True):
            st.session_state.stage = "compare"
            st.rerun()
    else:
        st.caption("두 선수 모두 정답을 입력하면 비교 미션이 열립니다.")


def render_compare() -> None:
    metric = get_metric()
    goal = st.session_state.goal
    candidate = GOALS[goal]["candidate"]
    other_player = "안현민" if candidate == "김영웅" else "김영웅"
    st.header("3회말 | 기록이 알려주는 답은?")
    st.markdown(
        f'<div class="coach-bubble">“{goal} 목표에 맞춰 생각해 보자. 두 선수 중 {metric}이 더 높은 선수는 누구일까?”</div>',
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2)
    for column, player in zip((c1, c2), PLAYERS):
        with column:
            st.metric(f"{player} 선수 · {metric}", displayed_rate(rate_for(player, metric)))
    with st.form("player_comparison"):
        answer = st.radio(
            f"두 선수 중 {metric}이 더 높은 선수는 누구일까요?",
            list(PLAYERS),
            horizontal=True,
            key="player_comparison_answer",
        )
        submitted = st.form_submit_button("선택 확인하기", type="primary", use_container_width=True)
    if submitted:
        st.session_state.comparison_correct = answer == candidate
        st.session_state.comparison_answer = answer
    if st.session_state.comparison_correct:
        st.success(f"정답이에요! **{candidate} 선수**의 {metric}이 더 높습니다.")
    elif hasattr(st.session_state, "comparison_answer"):
        st.warning(
            f"선택한 선수는 {st.session_state.comparison_answer} 선수예요. "
            f"두 계산 결과를 다시 비교해 보세요."
        )
    if st.session_state.comparison_correct:
        st.markdown(
            f"""
            <div class="learning-note">
              <strong>비교해 보기</strong><br>
              {candidate}: {displayed_rate(rate_for(candidate, metric))} &nbsp;›&nbsp;
              {other_player}: {displayed_rate(rate_for(other_player, metric))}<br>
              소수 셋째 자리까지 나타낸 값으로도 {candidate} 선수의 수가 더 큽니다.
              선수의 평가는 어떤 능력을 중요하게 보는지에 따라 달라질 수 있어요.
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("소수 크기 비교 미션으로", type="primary", use_container_width=True):
            st.session_state.stage = "decimals"
            st.rerun()


DECIMAL_QUESTIONS = [
    {
        "question": "0.400과 0.333 중 어느 수가 더 클까요?",
        "options": ["0.400", "0.333", "같아요"],
        "answer": "0.400",
        "explanation": "소수 첫째 자리와 둘째 자리는 같고, 셋째 자리에서 0이 3보다 크므로 0.400이 더 커요.",
    },
    {
        "question": "0.400과 0.500 중 어느 수가 더 클까요?",
        "options": ["0.400", "0.500", "같아요"],
        "answer": "0.500",
        "explanation": "소수 첫째 자리에서 4와 5를 비교하면 5가 더 크므로 0.500이 더 커요.",
    },
    {
        "question": "0.400과 0.4는 같은 수일까요?",
        "options": ["0.400이 더 커요", "0.4가 더 커요", "같아요"],
        "answer": "같아요",
        "explanation": "소수 끝에 0을 붙이거나 빼도 수의 크기는 바뀌지 않아요. 0.400 = 0.4입니다.",
    },
]


def render_decimals() -> None:
    st.header("4회말 | 소수의 크기를 비교하라")
    st.markdown(
        '<div class="coach-bubble">“기록을 읽을 때는 소수의 자릿값을 살펴보자. 세 문제를 모두 풀어야 다음 작전으로 갈 수 있어!”</div>',
        unsafe_allow_html=True,
    )
    with st.form("decimal_comparisons"):
        answers = []
        for index, item in enumerate(DECIMAL_QUESTIONS):
            st.markdown(f"**미션 {index + 1}. {item['question']}**")
            answers.append(
                st.radio(
                    f"미션 {index + 1} 답",
                    item["options"],
                    horizontal=True,
                    key=f"decimal_answer_{index}",
                    label_visibility="collapsed",
                )
            )
        submitted = st.form_submit_button("소수 비교 답안 확인하기", type="primary", use_container_width=True)
    if submitted:
        st.session_state.decimal_correct = [
            answer == item["answer"]
            for answer, item in zip(answers, DECIMAL_QUESTIONS)
        ]
        st.session_state.decimal_submitted = True
    if st.session_state.decimal_submitted:
        for index, item in enumerate(DECIMAL_QUESTIONS):
            if st.session_state.decimal_correct[index]:
                st.success(f"미션 {index + 1} 정답! {item['explanation']}")
            else:
                st.warning(
                    f"미션 {index + 1}을 다시 생각해 보세요. 정답은 **{item['answer']}**예요. "
                    f"{item['explanation']}"
                )
    if all(st.session_state.decimal_correct):
        st.success("소수 비교 미션을 모두 해결했어요!")
        if st.button("영입 후보 등록하기", type="primary", use_container_width=True):
            st.session_state.stage = "signing"
            st.rerun()


def render_signing() -> None:
    goal = st.session_state.goal
    candidate = GOALS[goal]["candidate"]
    st.header("5회말 | 첫 영입 후보 등록")
    st.markdown(
        f'<div class="coach-bubble">“우리 팀 목표가 {goal}이야. 분석 결과에 따라 {candidate} 선수를 첫 영입 후보로 등록할까?”</div>',
        unsafe_allow_html=True,
    )
    render_player_card(candidate)
    st.markdown(
        f"선택한 목표에 맞는 지표는 **{GOALS[goal]['metric']}**이고, "
        f"{candidate} 선수의 {GOALS[goal]['metric']}은 "
        f"**{displayed_rate(rate_for(candidate, GOALS[goal]['metric']))}**입니다."
    )
    left, right = st.columns(2)
    with left:
        if st.button("✅ 영입하기", type="primary", use_container_width=True):
            st.session_state.recruited_candidate = candidate
            st.session_state.stage = "final_pick"
            st.rerun()
    with right:
        if st.button("🔎 다시 생각하기", use_container_width=True):
            st.session_state.stage = "analysis"
            st.rerun()


def render_final_pick() -> None:
    st.header("9회말 | 최종 영입 결정을 내려라")
    st.markdown(
        f'<div class="coach-bubble">“첫 후보는 {st.session_state.recruited_candidate} 선수로 등록했어. '
        "하지만 마지막 선택은 기록과 우리 팀의 필요를 다시 생각해서 결정해 보자!”</div>",
        unsafe_allow_html=True,
    )
    st.info("어떤 선수가 무조건 더 뛰어난 것은 아니에요. 우리 팀이 중요하게 생각하는 능력과 선택 이유를 함께 적어 주세요.")
    with st.form("final_report_form"):
        player = st.radio("최종 영입 선수", list(PLAYERS), horizontal=True, key="final_player_choice")
        metric = st.radio("활용한 통계 지표", ["타율", "출루율"], horizontal=True, key="final_metric_choice")
        st.markdown("**선수를 선택한 이유**")
        st.caption("예: 우리 팀에는 안타를 더 많이 치는 능력이 필요하다. 따라서 타율이 더 높은 선수를 선택했다.")
        st.caption("예: 우리 팀에는 다양한 방법으로 출루하는 능력이 필요하다. 따라서 출루율이 더 높은 선수를 선택했다.")
        reason = st.text_area(
            "영입 이유",
            placeholder="우리 팀에 어떤 능력이 필요한지, 선택한 지표와 선수 기록을 근거로 작성해 보세요.",
            height=180,
            key="final_reason_input",
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("최종 영입 보고서 작성하기", type="primary", use_container_width=True)
    if submitted:
        if not reason.strip():
            st.error("선택 이유를 작성해 주세요. 기록을 근거로 생각을 정리해 봅시다.")
        else:
            st.session_state.final_player = player
            st.session_state.final_metric = metric
            st.session_state.reason = reason.strip()
            st.session_state.stage = "report"
            st.rerun()


def report_html() -> str:
    player = st.session_state.final_player
    metric = st.session_state.final_metric
    rows = "".join(
        f"<tr><th>{name}</th><td>{PLAYERS[name]['at_bats']}</td>"
        f"<td>{PLAYERS[name]['hits']}</td><td>{PLAYERS[name]['walks']}</td>"
        f"<td>{displayed_rate(rate_for(name, '타율'))}</td>"
        f"<td>{displayed_rate(rate_for(name, '출루율'))}</td></tr>"
        for name in PLAYERS
    )
    return f"""<!doctype html>
<html lang="ko"><meta charset="utf-8"><title>우리 구단 최종 영입 보고서</title>
<style>
body{{font-family:Arial,sans-serif;color:#173b2c;max-width:900px;margin:40px auto;padding:24px;line-height:1.7}}
header{{border-bottom:5px solid #16834b;padding-bottom:16px}}h1{{color:#12653b}}
table{{border-collapse:collapse;width:100%;margin:18px 0}}th,td{{border:1px solid #bdd4c5;padding:10px;text-align:center}}
th{{background:#e8f5ec}}.reason{{white-space:pre-wrap;background:#f3f8f4;padding:18px;border-left:5px solid #16834b}}
footer{{margin-top:32px;background:#e8f5ec;padding:18px;text-align:center;font-weight:bold}}
@media print{{body{{margin:0 auto}}button{{display:none}}}}
</style><body><header><p>⚾ 2026 DREAM LEAGUE · 공식 문서</p>
<h1>우리 구단 최종 영입 보고서</h1></header>
<p><b>선택한 선수 유형:</b> {escape(st.session_state.goal)}</p>
<p><b>처음에 선택한 영입 목표:</b> {escape(GOALS[st.session_state.goal]['description'])}</p>
<p><b>첫 영입 후보 등록:</b> {escape(st.session_state.recruited_candidate or '')}</p>
<h2>선수 기록 및 지표</h2><table><thead><tr><th>선수</th><th>타수</th><th>안타</th><th>볼넷</th><th>타율</th><th>출루율</th></tr></thead>
<tbody>{rows}</tbody></table>
<p><b>계산식:</b> 타율 = 안타 ÷ 타수 &nbsp; | &nbsp; 출루율 = (안타 + 볼넷) ÷ (타수 + 볼넷)</p>
<h2>최종 영입 결정</h2><p><b>최종 영입 선수:</b> {escape(player)}</p>
<p><b>활용한 통계 지표:</b> {escape(metric)} ({displayed_rate(rate_for(player, metric))})</p>
<h2>영입 이유</h2><div class="reason">{escape(st.session_state.reason)}</div>
<footer>🏆 축하합니다! 여러분의 판단으로 우리 구단의 약점을 보완할 수 있게 되었습니다!</footer>
<p><button onclick="window.print()">인쇄하기 / PDF로 저장</button></p></body></html>"""


def render_report() -> None:
    st.markdown(
        '<div class="report-heading"><span>⚾ 2026 DREAM LEAGUE · 공식 문서</span>'
        "<h1>우리 구단 최종 영입 보고서</h1></div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"**선택한 선수 유형:** {st.session_state.goal}  \n"
        f"**처음에 선택한 영입 목표:** {GOALS[st.session_state.goal]['description']}  \n"
        f"**첫 영입 후보 등록:** {st.session_state.recruited_candidate}"
    )
    st.subheader("선수 기록 및 계산 결과")
    table_rows = []
    for name, record in PLAYERS.items():
        table_rows.append(
            {
                "선수": name,
                "타수": record["at_bats"],
                "안타": record["hits"],
                "볼넷": record["walks"],
                "타율": displayed_rate(rate_for(name, "타율")),
                "출루율": displayed_rate(rate_for(name, "출루율")),
            }
        )
    st.table(table_rows)
    st.markdown(
        "**타율 = 안타 수 ÷ 타수**  \n"
        "**출루율 = (안타 수 + 볼넷) ÷ (타수 + 볼넷)**"
    )
    st.subheader("최종 영입 결정")
    left, right = st.columns(2)
    with left:
        st.metric("최종 영입 선수", st.session_state.final_player)
    with right:
        st.metric(
            f"활용한 지표 · {st.session_state.final_metric}",
            displayed_rate(rate_for(st.session_state.final_player, st.session_state.final_metric)),
        )
    st.markdown("### 영입 이유")
    st.markdown(f'<div class="reason-card">{escape(st.session_state.reason)}</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="victory">🏆 축하합니다! 여러분의 판단으로 우리 구단의 약점을 보완할 수 있게 되었습니다! 🏆</div>',
        unsafe_allow_html=True,
    )
    st.download_button(
        "📄 인쇄용 보고서 HTML 다운로드",
        data=report_html(),
        file_name="우리_구단_최종_영입_보고서.html",
        mime="text/html",
        use_container_width=True,
    )
    st.caption("다운로드한 HTML 보고서를 브라우저에서 열고 ‘인쇄하기 / PDF로 저장’을 누르면 PDF로 보관할 수 있어요.")
    if st.button("처음부터 다시 하기", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        init_state()
        st.rerun()


st.markdown(
    """
    <style>
    .stApp {background: linear-gradient(180deg,#f3fbf5 0%,#ffffff 46%,#f2f8ff 100%); color:#173b2c}
    .block-container {max-width: 1050px; padding-top: 1.4rem; padding-bottom: 3rem}
    h1 {color:#11643b; letter-spacing:-.04em}
    h2,h3 {color:#185b3a}
    .top-ball {color:#24714a;font-weight:800;letter-spacing:.08em;font-size:.86rem}
    .step-strip {background:#e7f4eb;border-radius:14px;padding:12px 16px;margin:10px 0;color:#315d43;font-size:.88rem}
    .goal-banner {background:#eaf3ff;border:1px solid #c9def6;border-radius:12px;padding:12px 16px;color:#234d76;font-weight:700}
    .hero-card,.choice-card,.player-card {background:#fff;border:1px solid #d5e8d9;border-radius:20px;box-shadow:0 8px 24px #184d2a12}
    .hero-card {padding:clamp(20px,5vw,42px);border-top:8px solid #25a45c;margin:12px 0 20px}
    .hero-card h2 {margin-top:12px}
    .hero-card p {font-size:1.05rem;line-height:1.8}
    .hero-label {color:#c25b32;font-weight:800}
    .hero-card blockquote {background:#f0f8f2;border-left:5px solid #39a866;padding:14px 18px;margin:18px 0;font-weight:700}
    .hero-last {color:#12653b;font-weight:800}
    .coach-bubble {position:relative;background:#eaf4ff;border:1px solid #c7def5;border-radius:18px;padding:17px 20px;margin:12px 0 20px;color:#204e76;font-weight:700}
    .choice-card {padding:24px;min-height:220px;margin:8px 0 12px}
    .choice-icon {font-size:2.4rem}
    .metric-tag {display:inline-block;background:#eaf5ed;color:#17683b;padding:7px 12px;border-radius:99px;font-weight:700}
    .player-card {padding:20px;margin:6px 0 14px;border-bottom:5px solid #42a76b}
    .player-name {font-size:1.3rem;font-weight:800;color:#155d37;margin-bottom:14px}
    .record-grid {display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
    .record-grid div {background:#f3f8f4;border-radius:12px;padding:12px;text-align:center}
    .record-grid span {display:block;color:#567263;font-size:.88rem}
    .record-grid strong {display:block;font-size:1.45rem;color:#194b31}
    .formula-box,.learning-note,.reason-card {background:#f0f7f2;border:1px solid #d3e8d8;border-radius:14px;padding:17px 20px;margin:14px 0}
    .formula-box strong {font-size:1.15rem;color:#135f38}
    .report-heading {border-bottom:5px solid #16834b;padding:12px 6px 4px;margin-bottom:18px}
    .report-heading span {color:#43815a;font-weight:700}
    .reason-card {white-space:pre-wrap;font-size:1.04rem;line-height:1.8}
    .victory {background:linear-gradient(100deg,#e7f6eb,#fff6d8);border:2px solid #86c596;border-radius:18px;padding:22px;text-align:center;font-size:1.2rem;font-weight:900;color:#145d35;margin:22px 0}
    div.stButton > button,div.stFormSubmitButton > button {min-height:3rem;border-radius:12px;font-weight:750}
    @media (max-width:640px) {
      .block-container {padding-left:1rem;padding-right:1rem}
      .step-strip {font-size:.76rem;line-height:1.8}
      .record-grid {gap:6px}
      .record-grid div {padding:9px 5px}
      .record-grid strong {font-size:1.2rem}
    }
    </style>
    """,
    unsafe_allow_html=True,
)

init_state()
render_header()

page_renderers = {
    "intro": render_intro,
    "goal": render_goal,
    "analysis": render_analysis,
    "compare": render_compare,
    "decimals": render_decimals,
    "signing": render_signing,
    "final_pick": render_final_pick,
    "report": render_report,
}
page_renderers[st.session_state.stage]()
