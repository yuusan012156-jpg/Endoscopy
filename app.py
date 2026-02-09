import streamlit as st
import pandas as pd
import random
import csv

# アプリの基本設定
st.set_page_config(page_title="資格試験対策 模擬テスト", page_icon="🏥")

@st.cache_data
def load_data():
    try:
        # quoting=csv.QUOTE_MINIMAL を指定して、カンマが含まれるデータの誤認識を抑制
        df = pd.read_csv("quiz_data.csv", encoding="utf-8-sig", quoting=csv.QUOTE_MINIMAL)
        
        # データのクリーニング：選択肢を分割し、前後の空白を除去
        df['options'] = df['options'].apply(lambda x: [o.strip() for o in str(x).split('|')])
        return df.to_dict('records')
    except Exception as e:
        st.error(f"⚠️ CSVの読み込み中にエラーが発生しました：{e}")
        st.info("ヒント: 文中の半角カンマ(,)を全角(、)に直すと解決することが多いです。")
        st.stop()

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

st.title("🏥 消化器内視鏡技師 模擬テスト")

if not st.session_state.quiz_started:
    st.write(f"現在の登録問題数: {len(quiz_pool)}問")
    if st.button("テストを開始する"):
        start_quiz()
        st.rerun()

elif not st.session_state.quiz_finished:
    current_q = st.session_state.selected_questions[st.session_state.idx]
    
    # --- 解答が何個必要か自動判定 ---
    ans_raw = str(current_q['answer'])
    correct_labels = ans_raw.split('&')
    needed_count = len(correct_labels)
    
    st.subheader(f"問題 {st.session_state.idx + 1}")
    st.markdown(f"#### {current_q['question']}")
    
    if needed_count > 1:
        st.warning(f"💡 正解を **{needed_count}つ** 選んでください")
    else:
        st.info("💡 正解を **1つ** 選んでください")

    user_choices = []
    # 選択肢の表示
    for option in current_q['options']:
        # 判定用ラベルの取得（a. 形式なら 'a'、そうでなければ選択肢全文）
        label = option[0] if "." in option[:3] else option
        
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
        # 正誤判定：ラベル同士、または全文同士で比較
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
# 結果表示は以前と同様import streamlit as st
import pandas as pd
import random
import csv

# アプリの基本設定
st.set_page_config(page_title="資格試験対策 模擬テスト", page_icon="🏥")

@st.cache_data
def load_data():
    try:
        # quoting=csv.QUOTE_MINIMAL を指定して、カンマが含まれるデータの誤認識を抑制
        df = pd.read_csv("quiz_data.csv", encoding="utf-8-sig", quoting=csv.QUOTE_MINIMAL)
        
        # データのクリーニング：選択肢を分割し、前後の空白を除去
        df['options'] = df['options'].apply(lambda x: [o.strip() for o in str(x).split('|')])
        return df.to_dict('records')
    except Exception as e:
        st.error(f"⚠️ CSVの読み込み中にエラーが発生しました：{e}")
        st.info("ヒント: 文中の半角カンマ(,)を全角(、)に直すと解決することが多いです。")
        st.stop()

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

st.title("🏥 消化器内視鏡技師 模擬テスト")

if not st.session_state.quiz_started:
    st.write(f"現在の登録問題数: {len(quiz_pool)}問")
    if st.button("テストを開始する"):
        start_quiz()
        st.rerun()

elif not st.session_state.quiz_finished:
    current_q = st.session_state.selected_questions[st.session_state.idx]
    
    # --- 解答が何個必要か自動判定 ---
    ans_raw = str(current_q['answer'])
    correct_labels = ans_raw.split('&')
    needed_count = len(correct_labels)
    
    st.subheader(f"問題 {st.session_state.idx + 1}")
    st.markdown(f"#### {current_q['question']}")
    
    if needed_count > 1:
        st.warning(f"💡 正解を **{needed_count}つ** 選んでください")
    else:
        st.info("💡 正解を **1つ** 選んでください")

    user_choices = []
    # 選択肢の表示
    for option in current_q['options']:
        # 判定用ラベルの取得（a. 形式なら 'a'、そうでなければ選択肢全文）
        label = option[0] if "." in option[:3] else option
        
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
        # 正誤判定：ラベル同士、または全文同士で比較
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
# 結果表示は以前と同様