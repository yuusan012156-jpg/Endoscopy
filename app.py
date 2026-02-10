import streamlit as st
import pandas as pd
import random
import time
import os
import csv

# 1. アプリの基本設定
st.set_page_config(page_title="内視鏡認定技師 試験対策", page_icon="🩺", layout="wide")

# --- データ読み込み ---
@st.cache_data(show_spinner="問題を読み込んでいます...")
def load_data():
    file_path = "quiz_data_medical.csv"
    if not os.path.exists(file_path):
        st.error(f"ファイル '{file_path}' が見つかりません。")
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(
            file_path, 
            encoding="utf-8-sig", 
            sep=',', 
            engine='python',
            on_bad_lines='warn',
            quoting=csv.QUOTE_MINIMAL
        )
        
        required = ['question', 'category', 'options', 'answer', 'explanation']
        if not all(col in df.columns for col in required):
            st.error(f"CSVの列名が正しくありません。期待される列: {required}")
            return pd.DataFrame()

        def clean_opt(opt_str):
            opts = [o.strip() for o in str(opt_str).split('|')]
            return [o[2:].strip() if "." in o[:3] else o for o in opts]
        
        df['clean_options'] = df['options'].apply(clean_opt)
        return df
    except Exception as e:
        st.error(f"読み込みエラーが発生しました: {e}")
        return pd.DataFrame()

df_all = load_data()

# --- 2. セッション状態の初期化 ---
if 'history' not in st.session_state: st.session_state.history = []
if 'page' not in st.session_state: st.session_state.page = "🏠 ホーム"
if 'quiz_started' not in st.session_state: st.session_state.quiz_started = False
if 'is_paused' not in st.session_state: st.session_state.is_paused = False
if 'elapsed_time' not in st.session_state: st.session_state.elapsed_time = 0 # 蓄積された経過時間

# --- 3. クイズ開始関数 ---
def start_quiz(q_count, mode, target_cat=None):
    cats = ["基礎", "臨床", "機器", "薬理", "処置", "管理"]
    if df_all.empty: return
    
    if mode == "全分野からバランスよく":
        all_pool = df_all.sample(frac=1).to_dict('records')
        selected = []
        per_cat = q_count // len(cats)
        for c in cats:
            c_df = df_all[df_all['category'] == c]
            if not c_df.empty:
                selected.extend(c_df.sample(min(per_cat, len(c_df))).to_dict('records'))
        needed = q_count - len(selected)
        if needed > 0:
            already_q = [x['question'] for x in selected]
            leftovers = [x for x in all_pool if x['question'] not in already_q]
            selected.extend(leftovers[:needed])
        random.shuffle(selected)
    else:
        target_df = df_all[df_all['category'] == target_cat]
        selected = target_df.sample(min(q_count, len(target_df))).to_dict('records')

    for q in selected:
        labels = ['a', 'b', 'c', 'd', 'e']
        ans_labels = str(q['answer']).split('&')
        correct_texts = [q['clean_options'][labels.index(l)] for l in ans_labels if l in labels and labels.index(l) < len(q['clean_options'])]
        shuffled_opts = q['clean_options'][:]
        random.shuffle(shuffled_opts)
        q['display_options'] = [f"{labels[i]}. {t}" for i, t in enumerate(shuffled_opts)]
        new_ans = [labels[i] for i, txt in enumerate(shuffled_opts) if txt in correct_texts]
        q['correct_labels'] = "&".join(sorted(new_ans))

    st.session_state.selected_questions = selected
    st.session_state.idx = 0
    st.session_state.score = 0
    st.session_state.show_answer = False
    st.session_state.quiz_started = True
    st.session_state.is_paused = False
    st.session_state.page = "🩺 模擬テスト"
    st.session_state.elapsed_time = 0 # 時間をリセット
    st.session_state.start_timestamp = time.time() # 開始時刻を記録

# --- 4. サイドバーと同期 ---
st.sidebar.markdown("### 🩺 内視鏡認定技師\n### 試験対策システム")
st.sidebar.divider()
options = ["🏠 ホーム", "📊 成績・習熟度"]
if st.session_state.page == "🩺 模擬テスト": options.insert(1, "🩺 模擬テスト")
current_sel = st.sidebar.radio("メニュー", options, index=options.index(st.session_state.page))

if current_sel != st.session_state.page:
    if st.session_state.page == "🩺 模擬テスト":
        # 移動時に経過時間を保存
        st.session_state.elapsed_time += (time.time() - st.session_state.start_timestamp)
        st.session_state.is_paused = True
    st.session_state.page = current_sel
    st.rerun()

st.caption("内視鏡認定技師 試験対策")
st.header(st.session_state.page)
st.divider()

# --- 5. 各メイン画面 ---
if st.session_state.page == "🏠 ホーム":
    if st.session_state.is_paused:
        st.warning(f"⚠️ テストが第 {st.session_state.idx + 1} 問で中断されています。")
        c1, c2 = st.columns(2)
        if c1.button("▶️ 続きから再開する", use_container_width=True):
            st.session_state.start_timestamp = time.time() # 再開時刻をセット
            st.session_state.page = "🩺 模擬テスト"; st.rerun()
        if c2.button("🗑️ 破棄して新しく始める", use_container_width=True):
            st.session_state.is_paused = False; st.session_state.quiz_started = False; st.rerun()
    
    if not st.session_state.is_paused:
        with st.container(border=True):
            st.subheader("📝 出題セッティング")
            col1, col2 = st.columns(2)
            q_count = col1.selectbox("問題数", [30, 35, 50, 70])
            mode = col2.radio("出題形式", ["全分野からバランスよく", "苦手分野を指定"])
            target_cat = st.selectbox("特訓分野", ["基礎", "臨床", "機器", "薬理", "処置", "管理"]) if mode == "苦手分野を指定" else None
            st.info("⏱️ このテストでは経過時間を計測します（制限時間なし）")
            if st.button("🚀 テストを開始する", use_container_width=True):
                start_quiz(q_count, mode, target_cat); st.rerun()

elif st.session_state.page == "🩺 模擬テスト":
    # 現在の総経過時間を計算
    total_sec = st.session_state.elapsed_time + (time.time() - st.session_state.start_timestamp)
    m, s = divmod(int(total_sec), 60)
    
    # ヘッダーに経過時間を表示
    st.subheader(f"⏱️ 経過時間 {m:02d}:{s:02d} | 問題 {st.session_state.idx + 1} / {len(st.session_state.selected_questions)}")
    
    if st.button("⬅️ 一時中断してホームに戻る"):
        st.session_state.elapsed_time += (time.time() - st.session_state.start_timestamp)
        st.session_state.is_paused = True
        st.session_state.page = "🏠 ホーム"; st.rerun()

    q = st.session_state.selected_questions[st.session_state.idx]
    st.caption(f"カテゴリ: 【{q['category']}】")
    st.markdown(f"### {q['question']}")
    
    ans_labels = q['correct_labels'].split('&')
    st.info(f"💡 正解を **{len(ans_labels)}つ** 選んでください")
    
    user_choices = []
    for opt in q['display_options']:
        if st.checkbox(opt, key=f"med_{st.session_state.idx}_{opt}"):
            user_choices.append(opt[0])
    
    if not st.session_state.show_answer:
        if st.button("回答を確定", use_container_width=True):
            if len(user_choices) != len(ans_labels): st.error(f"{len(ans_labels)}個選んでください")
            else: st.session_state.show_answer = True; st.rerun()
    else:
        is_ok = set(user_choices) == set(ans_labels)
        if is_ok: st.success(f"⭕ 正解！ (正解: {q['correct_labels']})")
        else: st.error(f"❌ 不正解... 正解は {q['correct_labels']}")
        st.markdown(f"**【解説】**\n{q['explanation']}")
        
        if st.button("次の問題へ", use_container_width=True):
            st.session_state.history.append({"cat": q['category'], "correct": is_ok, "q": q['question']})
            if st.session_state.idx + 1 < len(st.session_state.selected_questions):
                st.session_state.idx += 1; st.session_state.show_answer = False
            else:
                st.balloons()
                # 最終時間を確定
                st.session_state.final_time = total_sec
                st.session_state.quiz_started = False
                st.session_state.page = "📊 成績・習熟度"
            st.rerun()

elif st.session_state.page == "📊 成績・習熟度":
    if not st.session_state.history: st.info("データがありません。")
    else:
        if 'final_time' in st.session_state:
            fm, fs = divmod(int(st.session_state.final_time), 60)
            st.success(f"🎊 テスト完了！ 総解答時間: {fm}分{fs}秒")
            
        h_df = pd.DataFrame(st.session_state.history)
        c1, c2 = st.columns(2)
        with c1: st.subheader("分野別正解率 (%)"); st.bar_chart(h_df.groupby('cat')['correct'].mean() * 100)
        with c2: st.subheader("学習回数"); st.bar_chart(h_df.groupby('cat')['q'].count())
        st.subheader("🚩 最近間違えた問題")
        st.table(h_df[h_df['correct'] == False][['cat', 'q']].tail(10))