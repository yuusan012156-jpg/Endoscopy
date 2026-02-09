import streamlit as st
import pandas as pd
import random

# アプリの基本設定
st.set_page_config(page_title="資格試験対策 模擬テスト", page_icon="🏥")

@st.cache_data
def load_data():
    df = pd.read_csv("quiz_data.csv", encoding="utf-8-sig")
    df['options'] = df['options'].apply(lambda x: str(x).split('|'))
    return df.to_dict('records')

quiz_pool = load_data()

if 'quiz_started' not in st.session_state:
    st.session_state.quiz_started = False

def start_quiz():
    sample_size = min(50, len(quiz_pool))
    st.session_state.selected_questions = random.sample(quiz_pool, sample_size)
    st.session_state.idx = 0
    st.session_state.score = 0
    st.session_state.show_answer = False
    st.session_state.quiz_started = True
    st.session_state.quiz_finished = False

st.title("🚁📖 資格試験 模擬テスト")

if not st.session_state.quiz_started:
    if st.button("テストを開始する"):
        start_quiz()
        st.rerun()

elif not st.session_state.quiz_finished:
    current_q = st.session_state.selected_questions[st.session_state.idx]
    
    # --- 解答が何個必要か自動判定 ---
    correct_answers = str(current_q['answer']).split('&')
    needed_count = len(correct_answers) # 'a&c'なら2、'a'なら1になる
    
    st.subheader(f"問題 {st.session_state.idx + 1}")
    st.markdown(f"#### {current_q['question']}")
    
    # 誘導メッセージの切り替え
    if needed_count > 1:
        st.warning(f"💡 正しいものを **{needed_count}つ** 選択してください")
    else:
        st.info("💡 正しいものを **1つ** 選択してください")

    user_choices = []
    for option in current_q['options']:
        label = option[0] # a, b, c, d, e を取得
        if st.checkbox(option, key=f"opt_{st.session_state.idx}_{label}"):
            user_choices.append(label)
    
    if not st.session_state.show_answer:
        if st.button("回答を確定する"):
            if len(user_choices) != needed_count:
                st.error(f"⚠️ {needed_count}個選択してください（現在 {len(user_choices)}個選択中）")
            else:
                st.session_state.show_answer = True
                st.rerun()
    else:
        # 正誤判定（セットで比較するので順番は関係なし）
        is_correct = set(user_choices) == set(correct_answers)
        
        if is_correct:
            st.success(f"✨ 正解！ （正解：{current_q['answer']}）")
            if 'last_idx' not in st.session_state or st.session_state.last_idx != st.session_state.idx:
                st.session_state.score += 1
                st.session_state.last_idx = st.session_state.idx
        else:
            st.error(f"❌ 不正解... 正解は 「{current_q['answer']}」")
        
        st.info(f"💡 **解説:**\n\n{current_q['explanation']}")
        
        if st.button("次の問題へ"):
            st.session_state.idx += 1
            st.session_state.show_answer = False
            if st.session_state.idx >= len(st.session_state.selected_questions):
                st.session_state.quiz_finished = True
            st.rerun()
# (以下、結果表示は前と同じ)