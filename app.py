from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import streamlit as st


DATA_DIR = Path(__file__).parent / "data"
MENUS_FILE = DATA_DIR / "menus.json"
REVIEWS_FILE = DATA_DIR / "reviews.json"

MENU_CATEGORIES = ["定食", "ごはん", "麺", "軽食", "デザート", "その他"]

DEFAULT_MENUS = [
    {
        "id": "yokokoku-power-bowl",
        "name": "横国パワー丼",
        "category": "ごはん",
        "price": 620,
        "description": "ボリューム満点で、学食でも特に人気の高い丼メニューです。",
    },
    {
        "id": "chicken-katsu-curry",
        "name": "チキンカツカレー",
        "category": "ごはん",
        "price": 710,
        "description": "カツの食感とカレーのスパイスがマッチした定番メニュー。",
    },
    {
        "id": "spicy-miso-pork-bowl",
        "name": "辛みそ豚丼",
        "category": "ごはん",
        "price": 680,
        "description": "辛みそと豚肉の相性が良く、満足度が高い一品。",
    },
    {
        "id": "shoyu-ramen",
        "name": "醤油ラーメン",
        "category": "麺",
        "price": 520,
        "description": "あっさりした醤油スープで、どの時間帯でも食べやすい。",
    },
    {
        "id": "chicken-namban",
        "name": "チキン南蛮",
        "category": "定食",
        "price": 750,
        "description": "甘酢と揚げ物のバランスがよく、満足感のある定食。",
    },
    {
        "id": "udon",
        "name": "うどん",
        "category": "麺",
        "price": 450,
        "description": "温かいうどんは、忙しい昼食にぴったりの定番メニュー。",
    },
]


def load_json(path: Path, default: Any) -> Any:
    """Load a JSON file, creating it with a default value when needed."""
    DATA_DIR.mkdir(exist_ok=True)
    if not path.exists():
        save_json(path, default)
        return default

    try:
        with path.open(encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        st.error(f"{path.name}を読み込めませんでした: {error}")
        return default


def save_json(path: Path, data: Any) -> None:
    """Persist JSON data using UTF-8 so Japanese text is preserved."""
    DATA_DIR.mkdir(exist_ok=True)
    try:
        with path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
    except OSError as error:
        st.error(f"{path.name}を保存できませんでした: {error}")


def get_review_stats(menu_id: str, reviews: list[dict[str, Any]]) -> tuple[float, int]:
    ratings = [review["rating"] for review in reviews if review["menu_id"] == menu_id]
    if not ratings:
        return 0.0, 0
    return sum(ratings) / len(ratings), len(ratings)


def render_stars(rating: float) -> str:
    if rating == 0:
        return "☆☆☆☆☆"
    filled = round(rating)
    return "★" * filled + "☆" * (5 - filled)


def display_price_warning() -> None:
    st.markdown(
        "<div style='color: #d32f2f; font-size: 2rem; font-weight: bold; margin-top: 0.25rem;'>料金が高すぎます</div>",
        unsafe_allow_html=True,
    )


st.set_page_config(
    page_title="Campus Eats | 学食レビュー",
    page_icon=":material/restaurant:",
    layout="wide",
)

menus = load_json(MENUS_FILE, DEFAULT_MENUS)
reviews = load_json(REVIEWS_FILE, [])

st.title("Campus Eats", anchor=False, icon=":material/restaurant:")
st.caption("みんなの口コミで、今日の学食選びをもっと楽しく。")

with st.sidebar:
    st.header("メニューを追加", icon=":material/add:")
    with st.form("add_menu_form", clear_on_submit=True):
        menu_name = st.text_input("メニュー名", placeholder="例：チキン南蛮定食")
        category = st.selectbox("カテゴリ", MENU_CATEGORIES)
        price = st.number_input("価格（円）", min_value=0, value=400, step=10)
        description = st.text_area("ひとこと紹介", placeholder="どんなメニューか教えてください")
        add_menu = st.form_submit_button("メニューを追加", type="primary", width="stretch")

    if add_menu:
        if price > 1000:
            display_price_warning()
        elif not menu_name.strip():
            st.error("メニュー名を入力してください。")
        elif any(menu["name"] == menu_name.strip() for menu in menus):
            st.error("同じ名前のメニューがすでにあります。")
        else:
            menus.append(
                {
                    "id": f"menu-{len(menus) + 1}",
                    "name": menu_name.strip(),
                    "category": category,
                    "price": int(price),
                    "description": description.strip() or "紹介文はまだありません。",
                }
            )
            save_json(MENUS_FILE, menus)
            st.success("メニューを追加しました。")
            st.rerun()

    st.header("表示を絞り込む", icon=":material/filter_list:")
    categories = ["すべて"] + sorted({menu["category"] for menu in menus})
    selected_category = st.selectbox("カテゴリ", categories, label_visibility="collapsed")

filtered_menus = [
    menu for menu in menus if selected_category == "すべて" or menu["category"] == selected_category
]

total_reviews = len(reviews)
average_rating = (
    sum(review["rating"] for review in reviews) / total_reviews if total_reviews else 0
)
metric_columns = st.columns(3)
metric_columns[0].metric("登録メニュー", f"{len(menus)}品")
metric_columns[1].metric("投稿されたレビュー", f"{total_reviews}件")
metric_columns[2].metric("全体の平均評価", f"{average_rating:.1f} / 5" if total_reviews else "—")

st.header("メニュー一覧", icon=":material/menu_book:")
if not filtered_menus:
    st.info("このカテゴリにはまだメニューがありません。サイドバーから追加できます。")

for menu in filtered_menus:
    average, count = get_review_stats(menu["id"], reviews)
    with st.container(border=True):
        info, score = st.columns([3, 1])
        with info:
            st.subheader(menu["name"])
            st.caption(f"{menu['category']} · {menu['price']:,}円")
            st.write(menu["description"])
        with score:
            if count:
                st.metric("平均評価", f"{average:.1f} / 5")
                st.write(render_stars(average))
                st.caption(f"{count}件のレビュー")
            else:
                st.caption("まだ評価がありません")

        with st.expander("メニューを編集", icon=":material/edit:"):
            with st.form(f"edit_menu_form_{menu['id']}"):
                edited_name = st.text_input("メニュー名", value=menu["name"])
                edited_category = st.selectbox("カテゴリ", MENU_CATEGORIES, index=MENU_CATEGORIES.index(menu["category"]))
                edited_price = st.number_input("価格（円）", min_value=0, value=int(menu["price"]), step=10)
                edited_description = st.text_area("ひとこと紹介", value=menu["description"], height=100)
                edit_submitted = st.form_submit_button("変更を保存", type="primary")

            if edit_submitted:
                if edited_price > 1000:
                    display_price_warning()
                else:
                    name = edited_name.strip()
                    if not name:
                        st.error("メニュー名を入力してください。")
                    elif name != menu["name"] and any(other["name"] == name for other in menus if other["id"] != menu["id"]):
                        st.error("同じ名前のメニューがすでにあります。")
                    else:
                        menu["name"] = name
                        menu["category"] = edited_category
                        menu["price"] = int(edited_price)
                        menu["description"] = edited_description.strip() or "紹介文はまだありません。"
                        save_json(MENUS_FILE, menus)
                        st.success("メニューを更新しました。")
                        st.rerun()

        with st.expander("このメニューを評価する", icon=":material/rate_review:"):
            with st.form(f"review_form_{menu['id']}"):
                rating = st.slider("評価（★5点満点）", min_value=1, max_value=5, value=4)
                comment = st.text_area(
                    "コメント（任意）",
                    placeholder="味や量、コスパなどの感想を書いてください",
                )
                submitted = st.form_submit_button("レビューを投稿", type="primary")

            if submitted:
                reviews.append(
                    {
                        "menu_id": menu["id"],
                        "rating": rating,
                        "comment": comment.strip(),
                    }
                )
                save_json(REVIEWS_FILE, reviews)
                st.success(f"{menu['name']}への評価を投稿しました。")

        menu_reviews = [review for review in reviews if review["menu_id"] == menu["id"]]
        for review in reversed(menu_reviews[-3:]):
            comment = review.get("comment", "")
            if comment:
                st.markdown(f"> **{render_stars(review['rating'])}**　{comment}")
            else:
                st.caption(f"{render_stars(review['rating'])}　コメントなし")
