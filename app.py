import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="消化器内視鏡技師 模擬テスト", page_icon="🏥")

@st.cache_data
def load_data():
    questions = []
    try:
        with open("quiz_data.csv", "r", encoding="utf-8-sig") as f:
            lines = f.readlines()
            
        for line in lines[1:]: # 1行目（見出し）を飛ばす
            if not line.strip(): continue
            
            # 「、」または「,」で一旦細かく分割
            parts = line.replace('、', ',').split(',')
            
            # --- 超頑丈な仕分けロジック ---
            # 1. 選択肢（| を含む項目）を探す
            opt_idx = -1
            for i, p in enumerate(parts):
                if '|' in p:
                    opt_idx = i
                    break
            
            if opt_idx != -1:
                # 選択肢より前はすべて「問題文」として結合
                q_text = "、".join(parts[:opt_idx])
                # 選択肢
                options = parts[opt_idx].strip().split('|')
                # 選択肢の直後は「正解」
                ans = parts[opt_idx + 1].strip()
                # それ以降はすべて「解説」として結合
                expl = "、".join(parts[opt_idx + 2:]).strip()
                
                questions.append({
                    "question": q_text,
                    "options": options,
                    "answer": ans,
                    "explanation": expl
                })
        return questions
    except Exception as e:
        st.error(f"データの読み込みに失敗しました。ファイルを確認してください。")
        return []

quiz_pool = load_data()

# --- 以下、セッション管理と画面表示（前回と同じですが、不具合を防ぐため全貼り付け推奨） ---
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

st.title("🏥 消化器内視鏡技師 模擬テスト")

if not st.session_state.quiz_started:
    st.write(f"現在の登録問題数: {len(quiz_pool)}問")
    if st.button("テストを開始する", key="start_btn"):
        start_quiz()
        st.rerun()

elif not st.session_state.quiz_finished:
    current_q = st.session_state.selected_questions[st.session_state.idx]
    ans_raw = str(current_q['answer'])
    correct_labels = [a.strip() for a in ans_raw.split('&')]
    needed_count = len(correct_labels)
    
    st.subheader(f"問題 {st.session_state.idx + 1} / 50")
    st.info(f"💡 正解を **{needed_count}つ** 選んでください")
    st.markdown(f"#### {current_q['question']}")

    user_choices = []
    for i, option in enumerate(current_q['options']):
        label = option[0] if "." in option[:3] else option
        if st.checkbox(option, key=f"q{st.session_state.idx}_opt{i}"):
            user_choices.append(label)
    
    if not st.session_state.show_answer:
        if st.button("回答を確定する"):
            if len(user_choices) != needed_count:
                st.error(f"⚠️ {needed_count}個選択してください")
            else:
                st.session_state.show_answer = True
                st.rerun()
    else:
        is_correct = set(user_choices) == set(correct_labels)
        if is_correct:
            st.success(f"✨ 正解！ （正解：{ans_raw}）")
            if 'last_idx' not in st.session_state or st.session_state.last_idx != st.session_state.idx:
                st.session_state.score += 1
                st.session_state.last_idx = st.session_state.idx
        else:
            st.error(f"❌ 不正解... 正解は 「{ans_raw}」")
        st.info(f"💡 **解説:**\n\n{current_q['explanation']}")
        if st.button("次の問題へ"):
            st.session_state.idx += 1
            st.session_state.show_answer = False
            if st.session_state.idx >= len(st.session_state.selected_questions):
                st.session_state.quiz_finished = True
            st.rerun()
else:
    st.header("🏁 テスト終了")
    st.metric("正解率", f"{(st.session_state.score / len(st.session_state.selected_questions)) * 100:.1f}%")
    if st.button("もう一度挑戦"):
        start_quiz()
        st.rerun()