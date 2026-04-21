import streamlit as st
import json
import random

# --- 1. 문제 데이터 불러오기 ---
@st.cache_data
def load_questions():
    try:
        with open("padi_questions.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
        return []

all_questions = load_questions()

# --- 2. 앱 설정 및 세션 상태 초기화 ---
st.set_page_config(page_title="PADI Open Water 모의고사", page_icon="🤿", layout="centered")

if "quiz_pool" not in st.session_state:
    # 100개 중 랜덤하게 20개를 뽑아서 퀴즈 세트로 구성 (실제 PADI 시험은 50문제지만 모바일 편의를 위해 20문제로 세팅)
    st.session_state.quiz_pool = random.sample(all_questions, min(20, len(all_questions)))
    st.session_state.current_idx = 0      
    st.session_state.score = 0            
    st.session_state.show_answer = False  

# --- 3. UI 구성 ---
st.title("🤿 PADI Open Water 다이버 모의고사")
st.progress((st.session_state.current_idx) / len(st.session_state.quiz_pool))
st.write(f"**문제 {st.session_state.current_idx + 1} / {len(st.session_state.quiz_pool)}**")

if st.session_state.current_idx < len(st.session_state.quiz_pool):
    q = st.session_state.quiz_pool[st.session_state.current_idx]
    
    st.info(f"[{q['category']}] {q['question']}")
    
    # 정답 입력 섹션 (PADI는 객관식이 주를 이룸)
    user_ans = ""
    if q['type'] == "mcq":
        user_ans = st.radio("보기를 선택하세요:", options=q['options'], key=f"q_{st.session_state.current_idx}")
    else:
        user_ans = st.text_input("정답을 입력하세요 (단답형):", key=f"q_{st.session_state.current_idx}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("제출하기"):
            st.session_state.show_answer = True

    # 정답 확인 및 해설
    if st.session_state.show_answer:
        correct_ans = q['answer']
        is_correct = False
        
        if q['type'] == "mcq":
            is_correct = (user_ans == correct_ans)
        else:
            if user_ans.strip() and correct_ans.replace(" ", "") in user_ans.replace(" ", ""):
                is_correct = True
        
        if is_correct:
            st.success("🎉 정답입니다!")
        else:
            st.error(f"앗, 오답입니다. 정답은 **{correct_ans}** 입니다.")
        
        st.write(f"💡 **해설:** {q['explanation']}")
        
        if st.button("다음 문제로 ➡️"):
            if is_correct:
                st.session_state.score += 1
            st.session_state.current_idx += 1
            st.session_state.show_answer = False
            st.rerun()

else:
    # 결과 화면 (합격 기준은 보통 75%)
    percentage = (st.session_state.score / len(st.session_state.quiz_pool)) * 100
    
    st.header("🎊 퀴즈 종료!")
    st.subheader(f"최종 점수: {st.session_state.score} / {len(st.session_state.quiz_pool)} 점 ({percentage:.1f}%)")
    
    if percentage >= 75:
        st.balloons()
        st.success("합격 기준(75%)을 넘었습니다! 안전한 다이빙 되세요. 🌊")
    else:
        st.warning("합격 기준(75%)에 미달했습니다. 매뉴얼을 다시 한번 복습해 보세요!")
    
    if st.button("다시 도전하기 🔄"):
        del st.session_state.quiz_pool
        st.rerun()

st.divider()
st.caption("본 모의고사는 PADI Open Water 다이버 코스 학습을 돕기 위한 참고용이며, 실제 자격증 취득을 대체할 수 없습니다.")
