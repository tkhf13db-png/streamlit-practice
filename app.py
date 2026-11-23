from __future__ import annotations

import json
import re
import unicodedata
import uuid
from pathlib import Path
from typing import Any

import streamlit as st


DATA_DIR = Path(__file__).parent / "data"
MENUS_FILE = DATA_DIR / "menus.json"
REVIEWS_FILE = DATA_DIR / "reviews.json"
MENU_REQUESTS_FILE = DATA_DIR / "menu_requests.json"
MENU_EDIT_REQUESTS_FILE = DATA_DIR / "menu_edit_requests.json"

MENU_CATEGORIES = ["麺類", "丼もの", "その他", "定食", "軽食", "デザート"]
CATEGORY_COLORS = {
    "麺類": "blue",
    "丼もの": "orange",
    "その他": "green",
    "定食": "violet",
    "軽食": "yellow",
    "デザート": "red",
}

DEFAULT_MENUS = [
    {
        "id": "yokokoku-power-bowl",
        "name": "横国パワー丼",
        "category": "丼もの",
        "price": 620,
        "description": "ボリューム満点で、学食でも特に人気の高い丼メニューです。",
    },
    {
        "id": "chicken-katsu-curry",
        "name": "チキンカツカレー",
        "category": "その他",
        "price": 710,
        "description": "カツの食感とカレーのスパイスがマッチした定番メニュー。",
    },
    {
        "id": "spicy-miso-pork-bowl",
        "name": "辛みそ豚丼",
        "category": "丼もの",
        "price": 680,
        "description": "辛みそと豚肉の相性が良く、満足度が高い一品。",
    },
    {
        "id": "shoyu-ramen",
        "name": "醤油ラーメン",
        "category": "麺類",
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
        "category": "麺類",
        "price": 450,
        "description": "温かいうどんは、忙しい昼食にぴったりの定番メニュー。",
    },
    {
        "id": "tonkotsu-shoyu-ramen",
        "name": "豚骨醤油ラーメン",
        "category": "麺類",
        "price": 580,
        "description": "豚骨のコクと醤油の香りを楽しめるラーメン。",
    },
    {
        "id": "shio-ramen",
        "name": "塩ラーメン",
        "category": "麺類",
        "price": 520,
        "description": "すっきりした味わいの定番塩ラーメン。",
    },
    {
        "id": "sapporo-miso-ramen",
        "name": "札幌味噌ラーメン",
        "category": "麺類",
        "price": 620,
        "description": "濃厚な味噌スープが特徴の札幌風ラーメン。",
    },
    {
        "id": "mentai-kamatama-udon",
        "name": "明太釜玉うどん",
        "category": "麺類",
        "price": 540,
        "description": "明太子と卵のまろやかさを合わせた釜玉うどん。",
    },
    {
        "id": "kake-udon",
        "name": "かけうどん",
        "category": "麺類",
        "price": 400,
        "description": "だしの風味を味わえるシンプルなうどん。",
    },
    {
        "id": "kake-soba",
        "name": "かけそば",
        "category": "麺類",
        "price": 400,
        "description": "温かいだしで楽しむ定番のそば。",
    },
    {
        "id": "sauce-shrimp-cutlet-bowl",
        "name": "ソース海老かつ丼",
        "category": "丼もの",
        "price": 680,
        "description": "海老かつとソースの組み合わせを楽しめる丼。",
    },
    {
        "id": "two-salmon-bowl",
        "name": "二種のサーモン丼",
        "category": "丼もの",
        "price": 780,
        "description": "二種類のサーモンを味わえる丼メニュー。",
    },
    {
        "id": "tori-zangi",
        "name": "鳥ザンギ",
        "category": "その他",
        "price": 580,
        "description": "ジューシーに揚げた北海道風の鶏料理。",
    },
    {
        "id": "cheese-in-hamburger",
        "name": "チーズインハンバーグ",
        "category": "その他",
        "price": 720,
        "description": "中からチーズがとろけるハンバーグ。",
    },
    {
        "id": "karaage-curry",
        "name": "から揚げカレー",
        "category": "その他",
        "price": 680,
        "description": "から揚げをトッピングしたボリューム満点のカレー。",
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


def render_category(category: str) -> None:
    st.badge(
        category,
        icon={
            "麺類": ":material/ramen_dining:",
            "丼もの": ":material/rice_bowl:",
            "その他": ":material/restaurant:",
            "定食": ":material/dining:",
            "軽食": ":material/lunch_dining:",
            "デザート": ":material/icecream:",
        }.get(category),
        color=CATEGORY_COLORS.get(category, "gray"),
    )


BLOCKED_PATTERNS = [
    (
        "暴力・脅迫",
        re.compile(r"(殺す|殺害|ぶっ殺|死ね|絞め殺|爆弾|爆破|刺す|殴る|襲撃|武器)", re.IGNORECASE),
    ),
    (
        "差別・侮辱",
        re.compile(r"(カス|ゴミ|消えろ|クズ|障害者差別表現|差別)", re.IGNORECASE),
    ),
    (
        "性的・わいせつな内容",
        re.compile(r"(性的|わいせつ|エロ|性行為|援交|AV女優)", re.IGNORECASE),
    ),
    (
        "危険行為・違法行為",
        re.compile(r"(麻薬|覚醒剤|大麻|違法薬物|窃盗|盗み方|爆弾の作り方)", re.IGNORECASE),
    ),
]


def find_blocked_reason(comment: str) -> str | None:
    normalized = unicodedata.normalize("NFKC", comment).lower()
    normalized = re.sub(r"\s+", "", normalized)
    for reason, pattern in BLOCKED_PATTERNS:
        if pattern.search(normalized):
            return reason
    return None


def get_admin_password() -> str | None:
    try:
        password = st.secrets["admin"]["password"]
    except (KeyError, FileNotFoundError):
        return None

    return str(password).strip() or None


def ensure_review_fields(reviews: list[dict[str, Any]]) -> bool:
    changed = False
    for review_index, review in enumerate(reviews):
        if not review.get("id"):
            identity = (
                f"{review.get('menu_id', '')}:"
                f"{review.get('rating', '')}:"
                f"{review.get('comment', '')}:"
                f"{review_index}"
            )
            review["id"] = str(uuid.uuid5(uuid.NAMESPACE_URL, identity))
            changed = True
        if "likes" not in review:
            review["likes"] = 0
            changed = True
        elif not isinstance(review["likes"], int) or isinstance(review["likes"], bool) or review["likes"] < 0:
            review["likes"] = 0
            changed = True
    return changed


def display_price_warning() -> None:
    st.markdown(
        "<div style='color: #d32f2f; font-size: 2rem; font-weight: bold; margin-top: 0.25rem;'>料金が高すぎます</div>",
        unsafe_allow_html=True,
    )


st.set_page_config(
    page_title="横国学食レビューサイト",
    page_icon=":material/restaurant:",
    layout="wide",
)

menus = load_json(MENUS_FILE, DEFAULT_MENUS)
reviews = load_json(REVIEWS_FILE, [])
menu_requests = load_json(MENU_REQUESTS_FILE, [])
menu_edit_requests = load_json(MENU_EDIT_REQUESTS_FILE, [])
if ensure_review_fields(reviews):
    save_json(REVIEWS_FILE, reviews)

st.session_state.setdefault("liked_review_ids", set())
st.session_state.setdefault("menu_request_success", False)

if st.session_state.menu_request_success:
    st.success("申請が送信されました。")
    st.session_state.menu_request_success = False

with st.container(border=True):
    hero_icon, hero_text = st.columns([1, 6], vertical_alignment="center")
    with hero_icon:
        st.markdown(
            "<div style='font-size: 3.5rem; text-align: center; color: #2563eb;'>🍜</div>",
            unsafe_allow_html=True,
        )
    with hero_text:
        st.title("横国学食レビューサイト", anchor=False, icon=":material/restaurant:")
        st.markdown(
            "**今日の学食選びを、もっと楽しく。** "
            "横浜国立大学のメニューをみんなの口コミで見つけよう。",
        )

    st.markdown(
        ":blue-badge[麺類] "
        ":orange-badge[丼もの] "
        ":green-badge[その他] "
        ":violet-badge[定食] "
        ":yellow-badge[軽食] "
        ":red-badge[デザート]",
    )

with st.sidebar:
    st.header("メニュー追加を申請", icon=":material/add:")
    with st.form("add_menu_request_form", clear_on_submit=True):
        menu_name = st.text_input("メニュー名", placeholder="例：チキン南蛮定食")
        category = st.selectbox("カテゴリ", MENU_CATEGORIES)
        price = st.number_input(
            "価格（円）",
            min_value=0,
            value=400,
            step=10,
            help="値段は普通盛りのものになります",
        )
        description = st.text_area("ひとこと紹介", placeholder="どんなメニューか教えてください")
        add_request = st.form_submit_button("管理者へ申請", type="primary", width="stretch")

    if add_request:
        if price > 1000:
            display_price_warning()
        elif not menu_name.strip():
            st.error("メニュー名を入力してください。")
        elif any(menu["name"] == menu_name.strip() for menu in menus):
            st.error("同じ名前のメニューがすでにあります。")
        elif any(
            request.get("status") == "pending"
            and request["name"] == menu_name.strip()
            for request in menu_requests
        ):
            st.error("このメニューは申請済みです。管理者の承認をお待ちください。")
        else:
            menu_requests.append(
                {
                    "id": str(uuid.uuid4()),
                    "name": menu_name.strip(),
                    "category": category,
                    "price": int(price),
                    "description": description.strip() or "紹介文はまだありません。",
                    "status": "pending",
                }
            )
            save_json(MENU_REQUESTS_FILE, menu_requests)
            st.session_state.menu_request_success = True
            st.rerun()

    st.header("運営管理", icon=":material/admin_panel_settings:")
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False

    admin_password = get_admin_password()
    if st.session_state.admin_authenticated:
        st.success("運営モードでログイン中")
        if st.button("ログアウト", width="stretch"):
            st.session_state.admin_authenticated = False
            st.rerun()
    else:
        if admin_password:
            entered_password = st.text_input(
                "管理者パスワード",
                type="password",
                key="admin_password",
            )
            if st.button("ログイン", type="primary", width="stretch"):
                if entered_password == admin_password:
                    st.session_state.admin_authenticated = True
                    st.success("ログインしました。")
                    st.rerun()
                else:
                    st.error("パスワードが違います。")
        else:
            st.caption("公開版では運営モードへ直接入れます。")
            if st.button("運営モードへ入る", type="primary", width="stretch"):
                st.session_state.admin_authenticated = True
                st.success("ログインしました。")
                st.rerun()

total_reviews = len(reviews)
average_rating = (
    sum(review["rating"] for review in reviews) / total_reviews if total_reviews else 0
)
metric_columns = st.columns(3)
with metric_columns[0]:
    with st.container(border=True):
        st.markdown(":blue-badge[メニュー]")
        st.metric("登録メニュー", f"{len(menus)}品")
with metric_columns[1]:
    with st.container(border=True):
        st.markdown(":orange-badge[口コミ]")
        st.metric("投稿されたレビュー", f"{total_reviews}件")
with metric_columns[2]:
    with st.container(border=True):
        st.markdown(":violet-badge[評価]")
        st.metric(
            "全体の平均評価",
            f"{average_rating:.1f} / 5" if total_reviews else "—",
        )

if st.session_state.admin_authenticated:
    with st.expander("運営管理：メニュー追加申請", icon=":material/add_circle:"):
        pending_requests = [
            request for request in menu_requests if request.get("status") == "pending"
        ]
        if not pending_requests:
            st.info("新しいメニュー追加申請はありません。")
        for request_index, request in enumerate(pending_requests):
            card = st.container(border=True)
            card.subheader(request["name"])
            card.caption(f"{request['category']} · {request['price']:,}円")
            card.write(request["description"])
            approve, reject = card.columns(2)
            if approve.button(
                "承認して追加",
                key=f"approve_menu_{request['id']}",
                type="primary",
                width="stretch",
            ):
                if any(menu["name"] == request["name"] for menu in menus):
                    st.error("同じ名前のメニューがすでに登録されています。")
                else:
                    menus.append(
                        {
                            "id": f"menu-{uuid.uuid4()}",
                            "name": request["name"],
                            "category": request["category"],
                            "price": int(request["price"]),
                            "description": request["description"],
                        }
                    )
                    request["status"] = "approved"
                    save_json(MENUS_FILE, menus)
                    save_json(MENU_REQUESTS_FILE, menu_requests)
                    st.success(f"{request['name']}をメニューに追加しました。")
                    st.rerun()
            if reject.button(
                "申請を却下",
                key=f"reject_menu_{request['id']}",
                type="secondary",
                width="stretch",
            ):
                request["status"] = "rejected"
                save_json(MENU_REQUESTS_FILE, menu_requests)
                st.success(f"{request['name']}の申請を却下しました。")
                st.rerun()

    with st.expander("運営管理：メニュー編集申請", icon=":material/edit:"):
        pending_edit_requests = [
            request
            for request in menu_edit_requests
            if request.get("status") == "pending"
        ]
        if not pending_edit_requests:
            st.info("新しいメニュー編集申請はありません。")
        for request in pending_edit_requests:
            card = st.container(border=True)
            card.subheader(request["current_name"])
            card.caption(
                f"{request['category']} · {request['price']:,}円"
            )
            card.write(request["description"])
            approve, reject = card.columns(2)
            if approve.button(
                "承認して編集",
                key=f"approve_edit_{request['id']}",
                type="primary",
                width="stretch",
            ):
                target = next(
                    (
                        menu
                        for menu in menus
                        if menu["id"] == request["menu_id"]
                    ),
                    None,
                )
                if target is None:
                    st.error("編集対象のメニューが見つかりません。")
                elif any(
                    menu["name"] == request["name"]
                    and menu["id"] != request["menu_id"]
                    for menu in menus
                ):
                    st.error("同じ名前のメニューがすでに登録されています。")
                else:
                    target["name"] = request["name"]
                    target["category"] = request["category"]
                    target["price"] = int(request["price"])
                    target["description"] = request["description"]
                    request["status"] = "approved"
                    save_json(MENUS_FILE, menus)
                    save_json(MENU_EDIT_REQUESTS_FILE, menu_edit_requests)
                    st.success("メニュー編集を承認しました。")
                    st.rerun()
            if reject.button(
                "申請を却下",
                key=f"reject_edit_{request['id']}",
                type="secondary",
                width="stretch",
            ):
                request["status"] = "rejected"
                save_json(MENU_EDIT_REQUESTS_FILE, menu_edit_requests)
                st.success("メニュー編集申請を却下しました。")
                st.rerun()

    with st.expander("運営管理：登録メニューの削除", icon=":material/delete:"):
        if not menus:
            st.info("削除できるメニューはありません。")
        for menu_index, menu in enumerate(menus):
            card = st.container(border=True)
            card.write(
                f"**{menu['name']}** — {menu['category']} / "
                f"{menu['price']:,}円（普通盛り）"
            )
            if card.button(
                "このメニューを削除",
                key=f"delete_menu_{menu['id']}",
                type="secondary",
                width="stretch",
            ):
                menus.pop(menu_index)
                related_review_ids = {
                    review["id"]
                    for review in reviews
                    if review["menu_id"] == menu["id"]
                }
                reviews[:] = [
                    review
                    for review in reviews
                    if review["menu_id"] != menu["id"]
                ]
                st.session_state.liked_review_ids.difference_update(related_review_ids)
                save_json(MENUS_FILE, menus)
                save_json(REVIEWS_FILE, reviews)
                st.success(f"{menu['name']}と関連レビューを削除しました。")
                st.rerun()

    with st.expander("運営管理：レビューの削除", icon=":material/admin_panel_settings:"):
        if not reviews:
            st.info("削除できるレビューはありません。")
        else:
            for review_index, review in enumerate(reviews):
                menu = next(
                    (item for item in menus if item["id"] == review["menu_id"]),
                    None,
                )
                menu_name = menu["name"] if menu else "削除済みメニュー"
                comment = review.get("comment", "").strip()
                card = st.container(border=True)
                card.write(f"**{menu_name}**  /  評価：{render_stars(review['rating'])}")
                card.write(comment or "コメントなし")
                if card.button(
                    "このレビューを削除",
                    key=f"delete_review_{review_index}",
                    type="secondary",
                    width="stretch",
                ):
                    reviews.pop(review_index)
                    save_json(REVIEWS_FILE, reviews)
                    st.success("レビューを削除しました。")
                    st.rerun()

st.header("メニュー一覧", icon=":material/menu_book:")
def render_menu_card(menu: dict[str, Any]) -> None:
    average, count = get_review_stats(menu["id"], reviews)
    with st.container(border=True):
        info, score = st.columns([3, 1])
        with info:
            st.subheader(menu["name"])
            render_category(menu["category"])
            st.caption(f"{menu['price']:,}円")
            st.caption("値段は普通盛りのものになります")
            st.write(menu["description"])
        with score:
            if count:
                st.metric("平均評価", f"{average:.1f} / 5")
                st.write(render_stars(average))
                st.caption(f"{count}件のレビュー")
            else:
                st.caption("まだ評価がありません")

        if st.session_state.admin_authenticated:
            with st.expander("メニューを編集", icon=":material/edit:"):
                with st.form(f"edit_menu_form_{menu['id']}"):
                    edited_name = st.text_input("メニュー名", value=menu["name"])
                    edited_category = st.selectbox(
                        "カテゴリ",
                        MENU_CATEGORIES,
                        index=MENU_CATEGORIES.index(menu["category"]),
                    )
                    edited_price = st.number_input(
                        "価格（円）",
                        min_value=0,
                        value=int(menu["price"]),
                        step=10,
                        help="値段は普通盛りのものになります",
                    )
                    edited_description = st.text_area(
                        "ひとこと紹介",
                        value=menu["description"],
                        height=100,
                    )
                    edit_submitted = st.form_submit_button(
                        "変更を保存",
                        type="primary",
                    )

                if edit_submitted:
                    if edited_price > 1000:
                        display_price_warning()
                    else:
                        name = edited_name.strip()
                        if not name:
                            st.error("メニュー名を入力してください。")
                        elif name != menu["name"] and any(
                            other["name"] == name
                            for other in menus
                            if other["id"] != menu["id"]
                        ):
                            st.error("同じ名前のメニューがすでにあります。")
                        else:
                            menu["name"] = name
                            menu["category"] = edited_category
                            menu["price"] = int(edited_price)
                            menu["description"] = (
                                edited_description.strip()
                                or "紹介文はまだありません。"
                            )
                            save_json(MENUS_FILE, menus)
                            st.success("メニューを更新しました。")
                            st.rerun()
        else:
            with st.expander("メニュー編集を申請", icon=":material/edit_square:"):
                with st.form(f"edit_request_form_{menu['id']}"):
                    requested_name = st.text_input(
                        "変更後のメニュー名",
                        value=menu["name"],
                    )
                    requested_category = st.selectbox(
                        "変更後のカテゴリ",
                        MENU_CATEGORIES,
                        index=MENU_CATEGORIES.index(menu["category"]),
                    )
                    requested_price = st.number_input(
                        "変更後の価格（円）",
                        min_value=0,
                        value=int(menu["price"]),
                        step=10,
                        help="値段は普通盛りのものになります",
                    )
                    requested_description = st.text_area(
                        "変更後のひとこと紹介",
                        value=menu["description"],
                        height=100,
                    )
                    request_submitted = st.form_submit_button(
                        "管理者へ編集申請",
                        type="primary",
                    )

                if request_submitted:
                    if requested_price > 1000:
                        display_price_warning()
                    elif not requested_name.strip():
                        st.error("メニュー名を入力してください。")
                    elif any(
                        other["name"] == requested_name.strip()
                        for other in menus
                        if other["id"] != menu["id"]
                    ):
                        st.error("同じ名前のメニューがすでにあります。")
                    else:
                        menu_edit_requests.append(
                            {
                                "id": str(uuid.uuid4()),
                                "menu_id": menu["id"],
                                "current_name": menu["name"],
                                "name": requested_name.strip(),
                                "category": requested_category,
                                "price": int(requested_price),
                                "description": (
                                    requested_description.strip()
                                    or "紹介文はまだありません。"
                                ),
                                "status": "pending",
                            }
                        )
                        save_json(
                            MENU_EDIT_REQUESTS_FILE,
                            menu_edit_requests,
                        )
                        st.success("申請が送信されました。")

        with st.expander("このメニューを評価する", icon=":material/rate_review:"):
            with st.form(f"review_form_{menu['id']}"):
                rating = st.slider("評価（★5点満点）", min_value=1, max_value=5, value=4)
                comment = st.text_area(
                    "コメント（任意）",
                    placeholder="味や量、コスパなどの感想を書いてください",
                    max_chars=300,
                )
                submitted = st.form_submit_button("レビューを投稿", type="primary")

            if submitted:
                blocked_reason = find_blocked_reason(comment)
                if blocked_reason:
                    st.error(
                        f"投稿できませんでした。{blocked_reason}に当たる表現が含まれている可能性があります。"
                    )
                    st.stop()
                reviews.append(
                    {
                        "id": str(uuid.uuid4()),
                        "menu_id": menu["id"],
                        "rating": rating,
                        "comment": comment.strip(),
                        "likes": 0,
                    }
                )
                save_json(REVIEWS_FILE, reviews)
                st.success(f"{menu['name']}への評価を投稿しました。")

        menu_reviews = [review for review in reviews if review["menu_id"] == menu["id"]]
        with st.expander(
            f"レビューコメント（{len(menu_reviews)}件）",
            icon=":material/comment:",
        ):
            if not menu_reviews:
                st.caption("まだコメントはありません")
            for review in reversed(menu_reviews[-10:]):
                review_id = review["id"]
                liked = review_id in st.session_state.liked_review_ids
                comment = review.get("comment", "")
                if comment:
                    st.markdown(f"> **{render_stars(review['rating'])}**　{comment}")
                else:
                    st.caption(f"{render_stars(review['rating'])}　コメントなし")

                like_label = "いいね済み" if liked else "いいね"
                if st.button(
                    f":material/thumb_up: {like_label}  {review.get('likes', 0)}",
                    key=f"like_review_{review_id}",
                    type="secondary",
                    width="content",
                ):
                    if liked:
                        st.session_state.liked_review_ids.remove(review_id)
                        review["likes"] = max(0, int(review.get("likes", 0)) - 1)
                    else:
                        st.session_state.liked_review_ids.add(review_id)
                        review["likes"] = int(review.get("likes", 0)) + 1
                    save_json(REVIEWS_FILE, reviews)
                    st.rerun()


category_tabs = st.tabs(MENU_CATEGORIES)
for tab, category in zip(category_tabs, MENU_CATEGORIES):
    with tab:
        tab_menus = [menu for menu in menus if menu["category"] == category]
        if not tab_menus:
            st.info("このジャンルにはまだメニューがありません。")
        for menu in tab_menus:
            render_menu_card(menu)
