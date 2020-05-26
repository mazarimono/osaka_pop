import re
import time
from datetime import date
from pathlib import Path

import pandas as pd
from requests_html import HTMLSession


def get_links(pop_url):

    session = HTMLSession()
    r = session.get(pop_url)
    r.html.render(10)
    data_block = r.html.find(".mol_attachfileblock")
    excel_block = data_block[0]
    csv_block = data_block[1]
    csv_block_links = csv_block.absolute_links

    csv_links = []

    for i in csv_block_links:
        if re.search(".csv", i):
            i = _make_prop_path(i)
            csv_links.append(i)
    return csv_links


def _make_prop_path(pop_url):
    sep_csv = pop_url.split("/")
    front_path = "/".join(sep_csv[:4])
    back_path = "/".join(sep_csv[5:])
    prop_path = "/".join([front_path, back_path])
    return prop_path


def _make_date(text):
    # text : "H29-2-jinkoidou.csv"の形で入力
    # 平成に1988を足すと西暦にになる
    # 令和に2018を足すと西暦になる

    split_text = text.split("-")  # ファイル名を"-"で分割する
    year_num = int(split_text[0][1:])  # 和暦の年の数値
    month_num = int(split_text[1])  # 月の数値

    head_text = text[0].upper()

    if head_text == "H":
        seireki_num = 1988 + year_num
    elif head_text == "R":
        seireki_num = 2018 + year_num
    else:
        pass

    dt = date(seireki_num, month_num, 1)

    return dt


# 日付入りのデータフレームを作成する


def save_dataframe(osaka_path):

    sep_path = osaka_path.split("/")
    file_name = sep_path[-1]
    title_date = _make_date(file_name)

    df = pd.read_csv(osaka_path)
    df["日付"] = title_date

    df.to_csv(f"./data/month_data/{title_date}_jinkouidou.csv")


if __name__ == "__main__":
    # データの取り込み
    osaka_pop_url = "https://www.city.osaka.lg.jp/toshikeikaku/page/0000014987.html"
    osaka_jinkou_links = get_links(osaka_pop_url)
    for i in osaka_jinkou_links:
        if re.search("jinkouido", i):
            print(i)
            save_dataframe(i)

            time.sleep(1)

    # データの結合

    p = Path("./data/month_data/")
    all_csv = list(p.glob("*.csv"))

    data_f = pd.DataFrame()
    for i in all_csv:
        df = pd.read_csv(i, index_col=0, parse_dates=["日付"]).dropna()
        data_f = pd.concat([data_f, df])

    data_f.sort_values("日付").reset_index(drop=True)
    data_f = data_f.dropna(1)
    d
    data_f.to_csv("./data/total_data/all.csv")
