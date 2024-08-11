import pandas as pd
import streamlit as st
import io
import random

def load_quiz_data(file):
    # UTF-8エンコードで読み込み
    with io.TextIOWrapper(file, encoding='utf-8', errors='replace') as f:
        df = pd.read_csv(f)
    return df

def filter_quiz_data(df, selected_years, selected_categories):
    # 選択された年と分野に基づいてデータをフィルタリング
    if "すべて" in selected_years:
        selected_years = df['year'].unique().tolist()
    if "すべて" in selected_categories:
        selected_categories = df['category'].unique().tolist()
    
    filtered_df = df[df['year'].isin(selected_years) & df['category'].isin(selected_categories)]
    
    quiz_data = []
    for _, row in filtered_df.iterrows():
        options = [row["option1"], row["option2"], row["option3"], row["option4"], row["option5"]]
        correct_option = row["answer"]
        shuffled_options = options[:]
        random.shuffle(shuffled_options)
        
        quiz_data.append({
            "question": row["question"],
            "options": shuffled_options,
            "correct_option": correct_option  # 正解オプションのテキストを保存
        })
    return quiz_data

def main():
    st.title("国家試験対策アプリ")

    # セッション状態の初期化
    if "quiz_data" not in st.session_state:
        st.session_state.quiz_data = []
    if "incorrect_data" not in st.session_state:
        st.session_state.incorrect_data = []
    if "current_quiz_data" not in st.session_state:
        st.session_state.current_quiz_data = []
    if "answers" not in st.session_state:
        st.session_state.answers = {}
    if "shuffled_options" not in st.session_state:
        st.session_state.shuffled_options = {}
    if "highlighted_questions" not in st.session_state:
        st.session_state.highlighted_questions = set()
    if "submit_count" not in st.session_state:
        st.session_state.submit_count = 0  # 回答ボタンが押された回数

    uploaded_file = st.file_uploader("問題データのCSVファイルをアップロードしてください", type="csv")
    if uploaded_file is not None:
        try:
            df = load_quiz_data(uploaded_file)
            years = df['year'].unique().tolist()
            categories = df['category'].unique().tolist()

            # 「すべて」オプションをリストに追加
            years.insert(0, "すべて")
            categories.insert(0, "すべて")

            # 年と分野を選択
            selected_years = st.multiselect("過去問の回数を選択してください", years)
            selected_categories = st.multiselect("分野を選択してください", categories)

            if selected_years and selected_categories:
                # 選択した年と分野に基づいてデータをフィルタリング
                st.session_state.quiz_data = filter_quiz_data(df, selected_years, selected_categories)
                st.session_state.current_quiz_data = st.session_state.quiz_data.copy()
                st.session_state.answers = {quiz["question"]: None for quiz in st.session_state.current_quiz_data}

            if st.session_state.current_quiz_data:
                for i, quiz in enumerate(st.session_state.current_quiz_data):
                    question_number = i + 1
                    is_highlighted = question_number in st.session_state.highlighted_questions
                    highlight_style = "background-color: #ffcccc;" if is_highlighted else ""

                    st.markdown(f"**<div style='padding: 10px; {highlight_style}'>問題 {question_number}</div>**", unsafe_allow_html=True)
                    st.markdown(f"<p style='margin-bottom: 0;'>{quiz['question']}</p>", unsafe_allow_html=True)

                    # 選択肢の順序を保持する
                    if quiz["question"] not in st.session_state.shuffled_options:
                        st.session_state.shuffled_options[quiz["question"]] = quiz["options"]
                    
                    options = st.session_state.shuffled_options[quiz["question"]]

                    selected_option = st.radio(
                        "",
                        options=options,
                        index=st.session_state.answers.get(quiz["question"], None),
                        key=f"question_{i}_radio"
                    )

                    if selected_option is not None:
                        st.session_state.answers[quiz["question"]] = selected_option

                    st.write("")  # 次の問題との間にスペースを追加

                # 回答ボタン
                if st.button("回答"):
                    # スコアと正答率の計算
                    score = 0
                    total_questions = len(st.session_state.quiz_data)  # 全問題数を取得
                    incorrect_data = []
                    for i, quiz in enumerate(st.session_state.current_quiz_data):
                        correct_option = quiz["correct_option"]
                        selected_option = st.session_state.answers.get(quiz["question"], None)

                        is_correct = correct_option == selected_option

                        if is_correct:
                            score += 1
                            st.session_state.highlighted_questions.discard(i + 1)  # 正解の問題番号からハイライトを削除
                        else:
                            incorrect_data.append(quiz)
                            st.session_state.highlighted_questions.add(i + 1)  # 不正解の問題番号を追加

                    accuracy_rate = (score / total_questions) * 100
                    st.write(f"あなたのスコア: {score} / {total_questions}")
                    st.write(f"正答率: {accuracy_rate:.2f}%")

                    if len(st.session_state.current_quiz_data) == 0:
                        st.success(f"すべての問題に正解しました！")

                    st.session_state.current_quiz_data = incorrect_data.copy()  # 不正解データを次の問題セットに設定

                    # 回答ボタンが押された後に状態をリセット
                    st.session_state.submit_count = 0

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()
