import streamlit as st
import pandas as pd
import random

# アプリの基本設定
st.set_page_config(page_title="消化器内視鏡技師 模擬テスト", page_icon="🏥")

@st.cache_data
def load_data():
    try:
        # 全角の「、」を区切り文字として指定。空行は無視する。
        df = pd.read_csv("quiz_data.csv", encoding="utf-8-sig", sep='、', engine='python', skip_blank_lines=True)
        
        # 念のため、問題文(question)が空の行を完全に削除
        df = df.dropna(subset=['question'])
        
        # データの整形
        df['options'] = df['options'].apply(lambda x: [o.strip() for o in str(x).split('|')])
        return df.to_dict('records')
    except Exception as e:
        st.error(f"⚠️ CSVの読み込みに失敗しました。1行目の見出しが全角の『、』で区切られているか確認してください。")
        st.stop()

# データの読み込み
quiz_pool = load_data()

# セッション管理
if 'quiz_started' not in st.session_state:
    st.session_state.quiz_started = False

def start_quiz():
    # 200問から50問をランダムに選ぶ
    sample_size = min(50, len(quiz_pool))
    st.session_state.selected_questions = random.sample(quiz_pool, sample_size)
    st.session_state.idx = 0
    st.session_state.score = 0
    st.session_state.show_answer = False
    st.session_state.quiz_started = True
    st.session_state.quiz_finished = False

st.title("🏥 消化器内視鏡技師 模擬テスト")

# --- 画面表示のロジック ---
if not st.session_state.quiz_started:
    st.write(f"現在の登録問題数: {len(quiz_pool)}問")
    if st.button("テストを開始する"):
        start_quiz()
        st.rerun()

elif not st.session_state.quiz_finished:
    current_q = st.session_state.selected_questions[st.session_state.idx]
    
    # 解答形式の判定
    ans_raw = str(current_q['answer'])
    correct_labels = [a.strip() for a in ans_raw.split('&')]
    needed_count = len(correct_labels)
    
    st.subheader(f"問題 {st.session_state.idx + 1} / 50")
    st.markdown(f"#### {current_q['question']}")
    
    if needed_count > 1:
        st.warning(f"💡 正解を **{needed_count}つ** 選んでください")
    else:
        st.info("💡 正解を **1つ** 選んでください")

    user_choices = []
    # 選択肢の表示
    for option in current_q['options']:
        # 判定用ラベル（a.などの一文字、または全文）を決定
        if "." in option[:3]:
            label = option[0]
        else:
            label = option
            
        if st.checkbox(option, key=f"opt_{st.session_state.idx}_{option}"):
            user_choices.append(label)
    
    if not st.session_state.show_answer:
        if st.button("回答を確定する"):
            if len(user_choices) != needed_count:
                st.error(f"⚠️ {needed_count}個選択してください（現在 {len(user_choices)}個）")
            else:
                st.session_state.show_answer = True
                st.rerun()
    else:
        # 正誤判定
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
    # 結果表示
    total = len(st.session_state.selected_questions)
    percent = (st.session_state.score / total) * 100
    st.header("🏁 テスト終了")
    st.metric("正解率", f"{percent:.1f}%")
    if st.button("もう一度挑戦（問題をシャッフル）"):
        start_quiz()
        st.rerun()