import random
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

# ============================================================
# 基本関数
# ============================================================
def make_initial_population(N, p00, p01, p11, rng):
    """
    N個体の二倍体集団を作る
    [0,0], [0,1], [1,1] の割合で初期化（端数は自動調整）
    """
    n00 = int(N * p00)
    n01 = int(N * p01)
    n11 = N - n00 - n01  # 端数調整

    pop = []
    pop.extend([[0, 0]] * n00)
    pop.extend([[0, 1]] * n01)
    pop.extend([[1, 1]] * n11)

    rng.shuffle(pop)
    return pop


def generate_next(population, rng):
    """
    次世代を作る（Wright–Fisher型）
    各子個体はランダムに選ばれた2親から1アレルずつ受け取る
    """
    next_pop = []
    for _ in range(len(population)):
        p1, p2 = rng.sample(population, 2)
        a1 = rng.choice(p1)
        a2 = rng.choice(p2)
        next_pop.append([a1, a2])
    return next_pop


def calc_freq0(population):
    """対立遺伝子0の頻度（0の個数 / 全アレル数）"""
    total = 2 * len(population)
    n0 = sum(1 for g in population for a in g if a == 0)
    return n0 / total


# ============================================================
# Streamlit UI
# ============================================================
st.set_page_config(
    page_title="遺伝的浮動シミュレーション（授業用）",
    layout="wide"
)

# タイトル（st.title は文字サイズ調整しづらいのでHTMLで小さめに）
st.markdown(
    "<h3 style='margin-bottom:0.2em;'>🧬 遺伝的浮動（Genetic Drift）雑草学2025　O.Watanabe</h3>",
    unsafe_allow_html=True
)

st.markdown("""
- 有限個体群  
- 自然選択なし  
- 突然変異なし  
- 移入なし  

**反復10回・ボタン1回で10世代ずつ進行**
""")

# ------------------------------------------------------------
# サイドバー設定
# ------------------------------------------------------------
with st.sidebar:
    st.header("モデル設定")

    N = st.number_input("個体数 N", 2, 5000, 10, 1)
    seed = st.number_input("乱数シード", 0, 10**9, 1234, 1)

    st.subheader("初期遺伝子型割合")
    p00 = st.number_input("[0,0]", 0.0, 1.0, 0.50)
    p01 = st.number_input("[0,1]", 0.0, 1.0, 0.40)
    p11 = st.number_input("[1,1]", 0.0, 1.0, 0.10)

    # ===== 解説（サイドバーに常駐）=====
    st.markdown("---")
    st.markdown("### 📘 モデルの考え方（解説）")

    st.markdown("""
**① このモデルは何を表しているか**

有限個体群では  
👉 **ランダムな配偶子抽出だけで**  
対立遺伝子頻度が世代ごとに変動する。

これが **遺伝的浮動（Genetic Drift）**。
""")

    st.markdown("""
**② なぜ N が小さいと変動が激しいのか？**

サンプリング誤差が大きくなる。

これは  
- コイン投げを **10回** 行う場合  
- コイン投げを **1000回** 行う場合  

の違いと同じで、試行回数が少ないほど結果が偏りやすい。
""")

    st.markdown("""
**③ 線がバラつく意味**

同じ条件でも  
👉 **歴史（偶然）によって結果が変わる**。

進化は「決定論」ではなく **確率過程**。
""")

    st.markdown("""
**④ 固定（0 or 1）とは？**

集団中のすべての個体が同じ対立遺伝子だけを持つ状態。

小集団ほど  
👉 **より早く固定が起こりやすい**。
""")

replicates = 10  # ★ 固定で10反復

# ------------------------------------------------------------
# session_state 初期化
# ------------------------------------------------------------
if "populations" not in st.session_state:
    st.session_state.populations = []

if "freq_history" not in st.session_state:
    st.session_state.freq_history = []  # freq_history[rep][gen]

if "generation" not in st.session_state:
    st.session_state.generation = 0

# 乱数生成器
rng = random.Random(seed)

# ------------------------------------------------------------
# 操作ボタン
# ------------------------------------------------------------
col1, col2 = st.columns(2)
init_btn = col1.button("🟩 初期化（反復10回）", use_container_width=True)
step_btn = col2.button("➡️ 次の世代へ（+10世代）", use_container_width=True)

# ------------------------------------------------------------
# 初期化処理
# ------------------------------------------------------------
if init_btn:
    st.session_state.populations = []
    st.session_state.freq_history = []
    st.session_state.generation = 0

    for _ in range(replicates):
        pop = make_initial_population(N, p00, p01, p11, rng)
        st.session_state.populations.append(pop)
        st.session_state.freq_history.append([calc_freq0(pop)])

# ------------------------------------------------------------
# 10世代まとめて進める（全反復）
# ------------------------------------------------------------
if step_btn and st.session_state.populations:
    for _ in range(10):
        for i in range(replicates):
            st.session_state.populations[i] = generate_next(
                st.session_state.populations[i], rng
            )
            st.session_state.freq_history[i].append(
                calc_freq0(st.session_state.populations[i])
            )
        st.session_state.generation += 1

# ------------------------------------------------------------
# 表示
# ------------------------------------------------------------
if not st.session_state.populations:
    st.info("「初期化（反復10回）」を押してください。")
    st.stop()

st.metric("現在の世代", st.session_state.generation)

# ===== グラフ =====
st.markdown("### 対立遺伝子0の頻度推移（反復10回）")

fig, ax = plt.subplots(figsize=(8, 3), dpi=120)
for freq in st.session_state.freq_history:
    ax.plot(range(len(freq)), freq, alpha=0.9)

ax.set_xlabel("Generation")
ax.set_ylabel("Allele-0 frequency")
ax.set_ylim(0, 1)
ax.set_title("Genetic drift (10 replicates, +10 generations per step)")
st.pyplot(fig)

# ===== テーブル（積み上げ / long）=====
st.markdown("### 0アレル頻度テーブル（積み上げ：世代 × 反復）")

# wide → long 変換
df_wide = pd.DataFrame(
    {f"rep_{i+1}": freq for i, freq in enumerate(st.session_state.freq_history)}
)
df_wide.insert(0, "generation", df_wide.index)

df_long = df_wide.melt(
    id_vars=["generation"],
    var_name="replicate",
    value_name="allele0_freq"
).sort_values(["generation", "replicate"]).reset_index(drop=True)

st.dataframe(df_long, use_container_width=True, height=450)

# ===== CSV ダウンロード（long版）=====
st.download_button(
    "📥 CSVでダウンロード（積み上げ形式）",
    df_long.to_csv(index=False).encode("utf-8"),
    file_name="allele0_frequency_table_long.csv",
    mime="text/csv"
)
