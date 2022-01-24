from loadflow import PowerSystem, LoadFlow
import getdata
import draw_graph
import numpy as np

import pygame
from sys import exit

pygame.init()

video_infos = pygame.display.Info()
H = video_infos.current_h * 0.8  # ウィンドウの横幅を画面の0.8倍に固定
W = H * 1.75  # ウィンドウの縦幅を横幅の1.75倍に固定
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption('Load Flow Calculator')
clock = pygame.time.Clock()

# ---- constants ----
# 昼、朝焼け&夕焼け、夜の空の色のRGB値
DAY = (73, 136, 205)
SUNDOWN = (232, 169, 79)
NIGHT = (1, 25, 50)
# -------------------

# ---- load image ----
# Surface と Rect のセットアップ
# 基本的には(静的な画像に関しては)
# 1. 画像を Surf として読み込み
# 2. 画像をスケール
# 3. Rect (位置)を設定


def load_image(path):  # 画像ファイルのパスから透過 pngの Surface を返す
    return pygame.image.load(path).convert_alpha()


bg_surf = load_image('images/bg.png')  # 背景画像
bg_surf = pygame.transform.smoothscale(bg_surf, (W, H))  # ウィンドウいっぱいのサイズ
# Surface の topleft を座標 (0, 0) に
bg_rect = bg_surf.get_rect(topleft=(0, 0))

graph_bg_surf = load_image('images/graph_bg.png')  # グラフ表示画面の半透背景
graph_bg_surf = pygame.transform.smoothscale(graph_bg_surf, (W, H))
graph_bg_rect = graph_bg_surf.get_rect(topleft=(0, 0))

display_date_surf = [load_image(
    f'images/display_date/{i}.png') for i in range(8)]  # 左上の日付の画像(0~7)を配列に格納
display_date_surf = [pygame.transform.smoothscale(
    display_date_surf[i], (W*0.07, W*0.07)) for i in range(8)]
display_date_rect = display_date_surf[0].get_rect(topleft=(W*0.04, H*0.06))

calendar_surf = load_image('images/calendar.png')  # 日付クリック時に表示されるカレンダーの枠
calendar_surf = pygame.transform.smoothscale(
    calendar_surf, (W*0.21, W*0.15))
calendar_rect = calendar_surf.get_rect(topleft=(W*0.12, H*0.06))

calendar_date_surf = [load_image(
    f'images/calendar_date/{i}.png') for i in range(8)]  # カレンダーの日付の画像
calendar_date_surf = [pygame.transform.smoothscale(
    calendar_date_surf[i], (W*0.07, W*0.02)) for i in range(8)]
rect_1 = [
    calendar_date_surf[i].get_rect(
        topleft=(W*(0.12+i*0.07), H*0.06+W*0.03))
    for i in range(3)]
rect_2 = [
    calendar_date_surf[i].get_rect(
        topleft=(W*(0.12+i*0.07), H*0.06+W*0.06))
    for i in range(3)]
rect_3 = [
    calendar_date_surf[i].get_rect(
        topleft=(W*(0.12+i*0.07), H*0.06+W*0.12))
    for i in range(2)]
calendar_date_rect = rect_1 + rect_2 + rect_3  # それぞれの日付に対する Rect を格納した配列

voltmeter_surf = load_image('images/voltmeter.png')  # 電圧計
voltmeter_surf = pygame.transform.smoothscale(
    voltmeter_surf, (W*0.2, W*0.12))
voltmeter_rect = [0] * 4  # 4つの電圧計の Rect 用の配列
voltmeter_rect[0] = voltmeter_surf.get_rect(topright=(W*0.98, H*0.3))
voltmeter_rect[1] = voltmeter_surf.get_rect(topright=(W*0.76, H*0.3))
voltmeter_rect[2] = voltmeter_surf.get_rect(topleft=(W*0.24, H*0.3))
voltmeter_rect[3] = voltmeter_surf.get_rect(topleft=(W*0.02, H*0.3))

panel_surf = load_image('images/panel.png')  # 太陽光パネル
panel_surf = pygame.transform.smoothscale(panel_surf, (H*0.324, H*0.2))
panel_rect = panel_surf.get_rect(topleft=(W*0.1, H*0.7))

thermal_surf = load_image('images/thermal.png')  # 火力発電所
thermal_surf = pygame.transform.smoothscale(thermal_surf, (H*0.324, H*0.2))
thermal_rect = thermal_surf.get_rect(topright=(W*0.9, H*0.7))

hand_surf = load_image('images/hand.png')  # 電圧計の指針
# 指針のスケール、向き、Rect は動的に変化するためここでは定義しない
hand_origin_surf = load_image('images/hand_origin.png')  # 指針の回転中心の円
hand_origin_surf = pygame.transform.smoothscale(
    hand_origin_surf, (H*0.014, H*0.014))
hand_origins = [voltmeter_rect[i].midbottom for i in range(4)]
hand_origin_rects = [hand_origin_surf.get_rect(
    center=hand_origins[i]) for i in range(4)]

graph_button_surf = load_image('images/graph.png')  # グラフ表示ボタン
graph_button_surf = pygame.transform.smoothscale(
    graph_button_surf, (W*0.07, W*0.07))
graph_button_rect = graph_button_surf.get_rect(topright=(W*0.96, H*0.06))

timeline_surf = load_image('images/timeline.png')  # 時刻を表す数直線
timeline_surf = pygame.transform.smoothscale(
    timeline_surf, (W*0.5, H*0.02))
timeline_rect = timeline_surf.get_rect(center=(W*0.5, H*0.06))

time_font = pygame.font.SysFont("Monaco", 15)  # 時間のデジタル表示フォントオブジェクト

time_indicator_surf = load_image('images/time_indicator.png')  # 現在時刻を表す指針
time_indicator_surf = pygame.transform.scale(
    time_indicator_surf, (W*0.015, W*0.015))

control_surf = load_image('images/control.png')  # 下部のコントロールパネル背景
control_surf = pygame.transform.smoothscale(control_surf, (W*0.3, W*0.15))
control_rect = control_surf.get_rect(midtop=(W*0.5, H*0.87))

play_surf = load_image('images/play.png')  # プレイボタン
play_surf = pygame.transform.smoothscale(play_surf, (W*0.03, W*0.03))
play_rect = play_surf.get_rect(
    center=(control_rect.midtop[0]+W*0.01, control_rect.midtop[1]+H*0.08))

stop_surf = load_image('images/stop.png')  # ストップボタン
stop_surf = pygame.transform.smoothscale(stop_surf, (W*0.03, W*0.03))
stop_rect = stop_surf.get_rect(
    center=(control_rect.midtop[0], control_rect.midtop[1]+H*0.08))

slide_surf = load_image('images/slide.png')  # スライダーボタン
slide_surf = pygame.transform.scale(slide_surf, (W*0.07, W*0.014))
# コントロールパネルのスライダーボタン
slide_control_rect = slide_surf.get_rect(
    center=(control_rect.midtop[0]-W*0.08, control_rect.midtop[1]+H*0.08))
# 需要割合変更用スライダーボタン
slide_ratio_rect = slide_surf.get_rect(
    center=(W*0.5, H*0.18))

slider_surf = load_image('images/slider.png')  # スライダー背景
slider_surf = pygame.transform.scale(slider_surf, (W*0.01, W*0.02))
# コントロールパネルのスライダー背景
slider_control_rect = slider_surf.get_rect(
    center=(control_rect.midtop[0]-W*0.08, control_rect.midtop[1]+H*0.08))
# 需要割合変更用スライダー背景
slider_ratio_rect = slider_surf.get_rect(
    center=(W*0.5, H*0.18))

gauge_left = load_image('images/gauge_left.png')  # 電力需要のゲージ
gauge_right = load_image('images/gauge_right.png')
# 動的に変化するため画像の読み込みだけしている

loop_active_surf = load_image('images/loop_active.png')  # ループボタン(アクティブ)
loop_inactive_surf = load_image(
    'images/loop_inactive.png')  # ループボタン(非アクティブ)
loop_active_surf = pygame.transform.smoothscale(loop_active_surf,
                                                (W*0.035, W*0.035))
loop_inactive_surf = pygame.transform.smoothscale(loop_inactive_surf,
                                                  (W*0.035, W*0.035))
loop_active_rect = loop_active_surf.get_rect(
    center=(control_rect.midtop[0]+W*0.09, control_rect.midtop[1]+H*0.08))
loop_inactive_rect = loop_inactive_surf.get_rect(
    center=(control_rect.midtop[0]+W*0.09, control_rect.midtop[1]+H*0.08))

energy_surf = load_image('images/energy.png')  # ノード間の電力の流れ(棒)
arrow_surf = load_image('images/arrow.png')  # ノード間の電力の流れ(矢印)
# 動的に変化するため読み込みだけしている

legend_surf = load_image('images/legend.png')  # グラフの凡例
legend_surf = pygame.transform.smoothscale(legend_surf, (H*0.11, H*0.11))


def legend_rect(rect):  # 凡例の位置指定用の関数
    x, y = rect
    return (x+W*0.07, y+H*0.32)
# --------------------

# ---- hand ----
# 電圧計の指針の長さ、傾きを電圧の大きさ、位相を元に求め、変換した Surface を返す
# 進み位相で右に傾くように theta にはマイナス符号がついている


def get_hand_surf(V, theta):
    hs = pygame.transform.smoothscale(
        hand_surf, (H*0.007, H*0.28*V))
    hs = pygame.transform.rotate(hs, -theta)

    return hs
# --------------

# ---- power_gauge ----
# 電力需要を表すゲージをスケールする
# Surface と 電力需要から Surface を返す


def get_gauge_surf(guage_surf, power):
    gs = pygame.transform.scale(guage_surf, (-W*0.04*power, H*0.02))

    return gs
# ---------------------


# ---- energy ----
# 各ノードの Rect の center どうしを有効電力の流れを表す棒で繋ぎ、矢印を表示する
# 棒の太さは有効電力の大きさに比例し、また、矢印の大きさもこれに比例する
# 矢印は脈動するようにアニメーションする
center0 = np.asarray(thermal_rect.center)
center1 = np.asarray(voltmeter_rect[1].center)
center2 = np.asarray(voltmeter_rect[2].center)
center3 = np.asarray(panel_rect.center)
# 各ノードの中心座標を numpy 配列に変換し距離を求める
distance01 = np.linalg.norm(center1-center0)
distance12 = np.linalg.norm(center2-center1)
distance23 = np.linalg.norm(center3-center2)
# 棒の傾きを求める
arg01 = np.arctan((center0[1]-center1[1]) /
                  (center0[0]-center1[0])) * 180/3.14
arg23 = np.arctan((center3[1]-center2[1]) /
                  (center2[0]-center3[0])) * 180/3.14

energywidth = W*0.01  # 有効電力が1の時の棒の幅


def get_energy_surfs(p):  # 電力潮流の行列 p を入力し、棒と矢印の Surface を格納した配列を返す
    size = 1 - 2 * abs(time - int(time) - 0.5)  # 矢印の脈動用に時刻と矢印の大きさを対応づける
    # ノード間の有効電力などから棒の Surface を設定
    es01 = pygame.transform.scale(
        energy_surf, (distance01*1.2, abs(p[0, 1]) * energywidth))
    es01 = pygame.transform.rotate(es01, -arg01)
    es12 = pygame.transform.scale(
        energy_surf, (distance12*1.2, abs(p[1, 2]) * energywidth))
    es23 = pygame.transform.scale(
        energy_surf, (distance23*1.2, abs(p[2, 3]) * energywidth))
    es23 = pygame.transform.rotate(es23, arg23)
    # 矢印の大きさ(脈動)と向き(電力の流れる方向)の設定
    # 大きさは最大の大きさ(棒の幅の2倍の幅)を毎時間ごとの 30分を最大値とする三角波(上記 size)とかけたもの
    # 向きは p[i, j] の符号から決まる
    as01 = pygame.transform.scale(
        arrow_surf, (W*0.05*size, abs(p[0, 1]) * energywidth * 2 * size))
    if p[0, 1] > 0:
        as01 = pygame.transform.rotate(as01, 180-arg01)
    else:
        as01 = pygame.transform.rotate(as01, -arg01)
    as12 = pygame.transform.scale(
        arrow_surf, (W*0.05*size, abs(p[1, 2]) * energywidth * 2 * size))
    if p[1, 2] > 0:
        as12 = pygame.transform.rotate(as12, 180)
    as23 = pygame.transform.scale(
        arrow_surf, (W*0.05*size, abs(p[2, 3]) * energywidth * 2 * size))
    if p[2, 3] > 0:
        as23 = pygame.transform.rotate(as23, arg23-180)
    else:
        as23 = pygame.transform.rotate(as23, arg23)

    return [es01, es12, es23, as01, as12, as23]


# 棒の中心位置(ノード間の中心が棒の中心)
center01 = (center0 + center1) / 2
center12 = (center1 + center2) / 2
center23 = (center2 + center3) / 2


def get_energy_rects(surfs, p):  # 棒と矢印の Rect を格納した配列を Surface と p により求めて返す
    # 棒の Rect
    er01 = surfs[0].get_rect(center=tuple(center01))
    er12 = surfs[1].get_rect(center=tuple(center12))
    er23 = surfs[2].get_rect(center=tuple(center23))
    # 時刻を元に矢印の Rect を決定(脈動用)
    devide = time - int(time)
    # 矢印の動き始める位置と動き終わる位置(変数名に惑わされない。end から start に動くこともある)
    start01 = 0.75 * center0 + 0.25 * center1
    end01 = 0.25 * center0 + 0.75 * center1
    start12 = 0.75 * center1 + 0.25 * center2
    end12 = 0.25 * center1 + 0.75 * center2
    start23 = 0.75 * center2 + 0.25 * center3
    end23 = 0.25 * center2 + 0.75 * center3
    # 毎時間、時間が過ぎるのと合わせて矢印が動く
    # 動く方向は p[i, j] の符号により決まる
    if p[0, 1] > 0:
        pos01 = (1-devide) * start01 + devide * end01
    else:
        pos01 = devide * start01 + (1-devide) * end01
    if p[1, 2] > 0:
        pos12 = (1-devide) * start12 + devide * end12
    else:
        pos12 = devide * start12 + (1-devide) * end12
    if p[2, 3] > 0:
        pos23 = (1-devide) * start23 + devide * end23
    else:
        pos23 = devide * center2 + (1-devide) * center3
    ar01 = surfs[3].get_rect(center=tuple(pos01))
    ar12 = surfs[4].get_rect(center=tuple(pos12))
    ar23 = surfs[5].get_rect(center=tuple(pos23))

    return [er01, er12, er23, ar01, ar12, ar23]
# ----------------


# ---- calendar ----
selected_date = 0  # カレンダーの日付をクリックすると対応する日付が代入される。
calendar_active = False  # カレンダーが開いているときに True
# ------------------

# ---- graph ----
graph_active = False  # グラフが表示されているときに True
# ---------------

# ---- sky ----
# 背景画像は透過 png になっており、空が透過、海と陸地も半透になっている。
# そのため、その裏を空の色で塗りつぶすと、空を希望の色にでき、海や陸地の明るさも影響をうける


def sky_color(time):  # 時刻から空の色を返す
    # RGB値をベクトルと見ると、空の色が変わる境界では２つのベクトルを内分した値を返す
    if 7 <= time < 17:
        return DAY
    if 17 <= time < 18:
        return tuple((time - 17) * SUNDOWN[i] + (18 - time) * DAY[i]
                     for i in range(3))
    if 6 < time < 7:
        return tuple((time - 6) * DAY[i] + (7 - time) * SUNDOWN[i]
                     for i in range(3))
    if time == 6 or time == 18:
        return SUNDOWN
    if 5 <= time < 6:
        return tuple((time - 5) * SUNDOWN[i] + (6 - time) * NIGHT[i]
                     for i in range(3))
    if 18 < time < 19:
        return tuple((time - 18) * NIGHT[i] + (19 - time) * SUNDOWN[i]
                     for i in range(3))
    if (0 <= time < 5) or (19 <= time < 24):
        return NIGHT


# -------------

# ---- time ----
time = 0  # 現在時刻
period = 12  # 1 ~ 24. 時間変化の周期(現実の時間)。例えば 12 の時は 12 秒で 1日

linewidth = timeline_rect.width  # 時刻を表す数直線の長さ
startpoint = timeline_rect.midleft  # 数直線の左端の位置

period_left = slide_control_rect.midleft  # コントロールパネルのスライダー背景の左端

dragging_time = False  # 時刻を示す指針をドラッグしている時 True


def time_pos(time):  # 時刻を示す指針の位置

    return (startpoint[0] + time*linewidth/24, startpoint[1])


def period_pos(period):  # コントロールパネルのスライダーの位置

    return (period_left[0] + period*slidewidth/23, period_left[1])


def format_time(time):  # 時刻のデジタル表示を hh:mm の形式にフォーマット
    hour = int(time)
    minute = int((time - hour) * 6) * 10

    return f'{hour:02}:{minute:02}'
# --------------


# ---- control ----
play = False  # プレイ中(時間が経っている間)に True
sliding = False  # コントロールパネルのスライダーをスライドしているときに True
loop_active = False  # ループがアクティブの時 True
# -----------------

# ---- ratio ----
ratio = 0.5  # 電力需要の割合。

changing_ratio = False  # スライダーで割合をスライドしている時に True

slidewidth = slide_ratio_rect.width  # スライダーの幅(割合、コントロールパネル共通)
ratio_left = slide_ratio_rect.midleft  # 割合スライダーの左端


def ratio_pos(ratio):  # 割合スライダーのボタンの位置

    return (ratio_left[0] + ratio*slidewidth, slide_ratio_rect.midleft[1])
# ---------------


# ---- loadflow ----
# 潮流計算
ps = PowerSystem(4)  # 電力系統を初期化

ps.r[0, 1] = 0.26 / 100
ps.x[0, 1] = 2.40 / 100
ps.b[0, 1] = 0.51 * 2 / 100

ps.r[2, 1] = 0.18 / 100
ps.x[2, 1] = 1.56 / 100
ps.b[2, 1] = 2.03 * 2 / 100

ps.r[2, 3] = 0.43 / 100
ps.x[2, 3] = 2.60 / 100
ps.b[2, 3] = 0.41 * 2 / 100

ps.bc[1] = 0.01
ps.bc[2] = 0.01

ps.V[0] = 1.
ps.theta[0] = 0.
ps.V[3] = 1.

lf = LoadFlow(ps)  # 潮流計算の準備


def get_v_p(date, time):  # 日時から電圧(配列)、位相(配列)、有効電力(行列)を返す
    global calculated, V
    d_s = getdata.getdata(date, time)  # 需要と太陽光発電量を取得

    tan = np.sqrt(1 / (0.85 ** 2) - 1)  # 無効電力と有効電力の比
    d = d_s[0]  # 需要
    s = d_s[1]  # 太陽光発電量
    ps.P[1] = - d * ratio  # 設定した割合を適用
    ps.Q[1] = - d * ratio * tan
    ps.P[2] = - d * (1-ratio)
    ps.Q[2] = - d * (1-ratio) * tan
    ps.P[3] = s

    if not calculated:  # 現在の時間(hour)に計算済みでない場合、計算する
        lf.calculate()  # 計算
        calculated = True  # 計算済みフラグを立てる

        set_graph_data(lf.V)  # グラフのデータを設定する

    if lf.V is None:  # 計算失敗の場合(lf.V が None) None を返す
        return None, None, None
    else:  # theta はラジアンから度数法に変換
        return lf.V, [theta * 180/3.14 for theta in lf.theta], lf.P


def set_graph_data(V_list):  # 配列 V からグラフ描画
    global V_temp, got_data
    if int(time) == 0:  # 時間 0 で V_temp を初期化
        V_temp = [[0]*24 for _ in range(4)]
    if V_temp is not None:  # V_temp が None でない時、グラフ描画
        if V_list is not None:
            for i, v in enumerate(V_list):
                V_temp[i][int(time)] = v  # V_list から各ノードの各時間のデータを格納
        if int(time) == 23:  # 23時にグラフを描画
            if not got_data:  # 既に1日のデータを描画ずみでない時にグラフを描画
                figs.append(draw_graph.draw_graph(
                    date, *V_temp))  # グラフを Surface として配列に格納
                if len(figs) > 4:  # グラフが4つより多い時、一番古いものを削除
                    figs.pop(0)
                got_data = True  # 描画済みフラグを立てる


V_temp = [[0]*24 for _ in range(4)]  # 4x24 の２次元配列. 各ノードの24時間分の電圧
figs = []  # 描画されたグラフの Surface を格納

fig_rects = [(0, 0), (W*0.5, 0), (0, H*0.5), (W*0.5, H*0.5)]
got_data = False  # 需要の割合または日付を変更すると False、描画を終えると True
# ------------------
calculated = False  # 毎時 False になり、計算を終えると True
hour = 0  # 現在の時間
date = 0  # 現在の日付
failed = False  # 計算に失敗した時 True

while True:
    # while 文の一回のループが１フレームである

    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # バツボタンを押すと発生
            pygame.quit()
            exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            # hogehoge_rect.collidepoint(event.pos) は hogehoge_rect をクリック
            # したときに True
            if not graph_active:
                if display_date_rect.collidepoint(event.pos):
                    calendar_active = not calendar_active
                if calendar_active:
                    for i in range(8):
                        if calendar_date_rect[i].collidepoint(event.pos):
                            selected_date = i
                            calendar_active = False
                            time = 0  # 日付変更で time=0
                            ratio = 0.5  # 日付変更で ratio リセット
                            period = 12  # 日付変更で period リセット
                            got_data = False  # 日付変更でグラフ描画フラグ下ろす

                if graph_button_rect.collidepoint(event.pos):
                    graph_active = True
                    play = False  # グラフ表示時、時間の更新をストップ
                    for i, fig in enumerate(figs):  # グラフをスケール
                        figs[i] = pygame.transform.smoothscale(
                            fig, (W*0.5, H*0.5))

                if timeline_rect.collidepoint(event.pos):
                    # クリックした時刻から時刻を更新
                    time = int(
                        (event.pos[0] - startpoint[0]) * 24/linewidth)+0.5
                    dragging_time = True  # 時刻をドラッグ開始
                    V_temp = None  # グラフデータ取得止める

                if not play:  # スタートボタン表示時
                    if play_rect.collidepoint(event.pos):
                        play = True
                        if failed:  # 計算失敗で止まってる場合、time=0 からやり直す
                            failed = False
                            time = 0.
                elif stop_rect.collidepoint(event.pos):
                    play = False
                    time = int(time) + 0.5  # 止める際は毎時の30分で止める

                if not loop_active:
                    if loop_active_rect.collidepoint(event.pos):
                        loop_active = True
                elif loop_inactive_rect.collidepoint(event.pos):
                    loop_active = False

                if slider_ratio_rect.collidepoint(event.pos):
                    changing_ratio = True  # 需要割合変更開始
                    got_data = False  # グラフデータ取得済みフラグ下ろす

                if slider_control_rect.collidepoint(event.pos):
                    sliding = True  # コントロールパネルのスライダー変更開始

            else:  # グラフがアクティブなら非表示にする
                graph_active = False
        if event.type == pygame.MOUSEMOTION:  # マウスが動いている時
            if dragging_time:  # 時刻変更中
                time_temp = int(
                    (pygame.mouse.get_pos()[0] - startpoint[0])
                    * 24/linewidth) + 0.5  # マウスの位置から時刻を取得
                if 0 <= time_temp < 24:  # 有効な時刻の場合に反映
                    time = time_temp
            if changing_ratio:  # 需要割合変更中
                ratio_temp = (pygame.mouse.get_pos()[0]
                              - ratio_left[0]) / slidewidth
                if 0 <= ratio_temp <= 1:
                    ratio = ratio_temp
            if sliding:  # 周期変更中
                period_temp = int(
                    (pygame.mouse.get_pos()[0] - period_left[0])
                    * 23/slidewidth)
                if 1 <= period_temp <= 24:
                    period = period_temp

        if event.type == pygame.MOUSEBUTTONUP:
            dragging_time = False
            changing_ratio = False
            sliding = False

    screen.fill(sky_color(time))  # 空の色で背景を塗りつぶす
    screen.blit(bg_surf, bg_rect)  # 背景描画
    # ノード間を黒い線で繋ぐ
    pygame.draw.line(screen, (0, 0, 0),
                     panel_rect.center, voltmeter_rect[2].center, width=3)
    pygame.draw.line(screen, (0, 0, 0),
                     voltmeter_rect[1].center, voltmeter_rect[2].center,
                     width=3)
    pygame.draw.line(screen, (0, 0, 0),
                     thermal_rect.center, voltmeter_rect[1].center, width=3)

    # --loadflow--
    # 潮流計算の可視化
    V, theta, p = get_v_p(selected_date, int(time))
    if V is not None:  # 計算成功した場合
        # 電圧計の指針の Surface と Rect を設定
        hand_surfs = [get_hand_surf(v, t) for v, t in zip(V, theta)]
        hand_rects = [hs.get_rect(center=ho)
                      for hs, ho in zip(hand_surfs, hand_origins)]
        # ノード間の棒と矢印の Surface と Rect を設定
        energy_surfs = get_energy_surfs(p)
        energy_rects = get_energy_rects(energy_surfs, p)
    else:
        failed = True
        play = False  # 失敗した場合、時間停止
    if not failed:  # 成功の場合、ノード間の棒と矢印を描画
        for es, er in zip(energy_surfs, energy_rects):
            screen.blit(es, er)
    # 矢印の上から各ノードと電圧計本体を描画(成功の場合。失敗の時は棒と矢印を描画せずに)
    screen.blit(voltmeter_surf, voltmeter_rect[0])
    screen.blit(voltmeter_surf, voltmeter_rect[1])
    screen.blit(voltmeter_surf, voltmeter_rect[2])
    screen.blit(voltmeter_surf, voltmeter_rect[3])
    screen.blit(panel_surf, panel_rect)
    screen.blit(thermal_surf, thermal_rect)
    if not failed:  # 成功の場合、電圧計の指針を描画
        for i in range(4):
            screen.blit(hand_surfs[i], hand_rects[i])
            screen.blit(hand_origin_surf, hand_origin_rects[i])
    # --loadflow--

    screen.blit(graph_button_surf, graph_button_rect)

    screen.blit(timeline_surf, timeline_rect)
    time_indicator_rect = time_indicator_surf.get_rect(
        midbottom=time_pos(time))  # 時間を指す指針の Rect を設定
    screen.blit(time_indicator_surf, time_indicator_rect)  # それを描画
    time_text_surf = time_font.render(f'{format_time(time)}', True,
                                      (255, 255, 255))  # デジタル時刻の Surface
    time_text_rect = time_text_surf.get_rect(center=(W*0.22, H*0.06))
    screen.blit(time_text_surf, time_text_rect)  # デジタル時刻の描画

    gauge_left_surf = get_gauge_surf(gauge_left, ps.P[2])  # 需要ゲージ
    gauge_right_surf = get_gauge_surf(gauge_right, ps.P[1])
    gauge_left_rect = gauge_left_surf.get_rect(midright=(W*0.5, H*0.27))
    gauge_right_rect = gauge_right_surf.get_rect(midleft=(W*0.5, H*0.27))
    screen.blit(gauge_left_surf, gauge_left_rect)
    screen.blit(gauge_right_surf, gauge_right_rect)

    screen.blit(display_date_surf[selected_date], display_date_rect)
    if calendar_active:
        screen.blit(calendar_surf, calendar_rect)
        for i in range(8):
            screen.blit(calendar_date_surf[i], calendar_date_rect[i])

    screen.blit(control_surf, control_rect)
    if not play:
        screen.blit(play_surf, play_rect)
    else:
        screen.blit(stop_surf, stop_rect)
    screen.blit(slide_surf, slide_control_rect)
    slider_control_rect = slider_surf.get_rect(
        center=period_pos(period))
    screen.blit(slider_surf, slider_control_rect)
    if loop_active:
        screen.blit(loop_active_surf, loop_active_rect)
    else:
        screen.blit(loop_inactive_surf, loop_inactive_rect)

    screen.blit(slide_surf, slide_ratio_rect)
    slider_ratio_rect = slider_surf.get_rect(
        center=ratio_pos(ratio))
    screen.blit(slider_surf, slider_ratio_rect)

    if graph_active:
        screen.blit(graph_bg_surf, graph_bg_rect)
        for fig, fig_rect in zip(figs, fig_rects):
            screen.blit(fig, fig_rect)
            l_rect = legend_surf.get_rect(topleft=legend_rect(fig_rect))
            screen.blit(legend_surf, l_rect)

    if play:
        time += 1/period
        if time >= 24:
            time = 0.
            if not loop_active:
                play = False
    if int(time) != hour or selected_date != date:
        # この if 文が True になるのは現在のループの間に時間(hour)が変更になった、
        # または日付が変更になった場合である。この時、計算済みフラグが降ろされる
        calculated = False
        hour = int(time)
        date = selected_date

    pygame.display.update()
    clock.tick(24)
