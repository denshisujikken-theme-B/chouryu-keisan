from loadflow import PowerSystem, LoadFlow
import getdata
import draw_graph
import numpy as np

import pygame
from sys import exit

pygame.init()

video_infos = pygame.display.Info()
H = video_infos.current_h * 0.8
W = H * 1.75
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption('Load Flow Calculator')
clock = pygame.time.Clock()

# ---- constants ----
DAY = (73, 136, 205)
SUNDOWN = (232, 169, 79)
NIGHT = (1, 25, 50)
# -------------------

# ---- load image ----


def load_image(path):
    return pygame.image.load(path).convert_alpha()


bg_surf = load_image('images/bg.png')
bg_surf = pygame.transform.smoothscale(bg_surf, (W, H))
bg_rect = bg_surf.get_rect(topleft=(0, 0))

graph_bg_surf = load_image('images/graph_bg.png')
graph_bg_surf = pygame.transform.smoothscale(graph_bg_surf, (W, H))
graph_bg_rect = graph_bg_surf.get_rect(topleft=(0, 0))

display_date_surf = [load_image(
    f'images/display_date/{i}.png') for i in range(8)]
display_date_surf = [pygame.transform.smoothscale(
    display_date_surf[i], (W*0.07, W*0.07)) for i in range(8)]
display_date_rect = display_date_surf[0].get_rect(topleft=(W*0.04, H*0.06))

calendar_surf = load_image('images/calendar.png')
calendar_surf = pygame.transform.smoothscale(
    calendar_surf, (W*0.21, W*0.15))
calendar_rect = calendar_surf.get_rect(topleft=(W*0.12, H*0.06))

calendar_date_surf = [load_image(
    f'images/calendar_date/{i}.png') for i in range(8)]
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
calendar_date_rect = rect_1 + rect_2 + rect_3

voltmeter_surf = load_image('images/voltmeter.png')
voltmeter_surf = pygame.transform.smoothscale(
    voltmeter_surf, (W*0.2, W*0.12))
voltmeter_rect = [0] * 4
voltmeter_rect[0] = voltmeter_surf.get_rect(topright=(W*0.98, H*0.3))
voltmeter_rect[1] = voltmeter_surf.get_rect(topright=(W*0.76, H*0.3))
voltmeter_rect[2] = voltmeter_surf.get_rect(topleft=(W*0.24, H*0.3))
voltmeter_rect[3] = voltmeter_surf.get_rect(topleft=(W*0.02, H*0.3))

panel_surf = load_image('images/panel.png')
panel_surf = pygame.transform.smoothscale(panel_surf, (H*0.324, H*0.2))
panel_rect = panel_surf.get_rect(topleft=(W*0.1, H*0.7))

thermal_surf = load_image('images/thermal.png')
thermal_surf = pygame.transform.smoothscale(thermal_surf, (H*0.324, H*0.2))
thermal_rect = thermal_surf.get_rect(topright=(W*0.9, H*0.7))

hand_surf = load_image('images/hand.png')
hand_origin_surf = load_image('images/hand_origin.png')
hand_origin_surf = pygame.transform.smoothscale(
    hand_origin_surf, (H*0.014, H*0.014))
hand_origins = [voltmeter_rect[i].midbottom for i in range(4)]
hand_origin_rects = [hand_origin_surf.get_rect(
    center=hand_origins[i]) for i in range(4)]

graph_button_surf = load_image('images/graph.png')
graph_button_surf = pygame.transform.smoothscale(
    graph_button_surf, (W*0.07, W*0.07))
graph_button_rect = graph_button_surf.get_rect(topright=(W*0.96, H*0.06))

timeline_surf = load_image('images/timeline.png')
timeline_surf = pygame.transform.smoothscale(
    timeline_surf, (W*0.5, H*0.02))
timeline_rect = timeline_surf.get_rect(center=(W*0.5, H*0.06))

time_font = pygame.font.SysFont("Monaco", 15)

time_indicator_surf = load_image('images/time_indicator.png')
time_indicator_surf = pygame.transform.scale(
    time_indicator_surf, (W*0.015, W*0.015))

control_surf = load_image('images/control.png')
control_surf = pygame.transform.smoothscale(control_surf, (W*0.3, W*0.15))
control_rect = control_surf.get_rect(midtop=(W*0.5, H*0.87))

play_surf = load_image('images/play.png')
play_surf = pygame.transform.smoothscale(play_surf, (W*0.03, W*0.03))
play_rect = play_surf.get_rect(
    center=(control_rect.midtop[0]+W*0.01, control_rect.midtop[1]+H*0.08))

stop_surf = load_image('images/stop.png')
stop_surf = pygame.transform.smoothscale(stop_surf, (W*0.03, W*0.03))
stop_rect = stop_surf.get_rect(
    center=(control_rect.midtop[0], control_rect.midtop[1]+H*0.08))

slide_surf = load_image('images/slide.png')
slide_surf = pygame.transform.scale(slide_surf, (W*0.07, W*0.014))
slide_control_rect = slide_surf.get_rect(
    center=(control_rect.midtop[0]-W*0.08, control_rect.midtop[1]+H*0.08))
slide_ratio_rect = slide_surf.get_rect(
    center=(W*0.5, H*0.18))

slider_surf = load_image('images/slider.png')
slider_surf = pygame.transform.scale(slider_surf, (W*0.01, W*0.02))
slider_control_rect = slider_surf.get_rect(
    center=(control_rect.midtop[0]-W*0.08, control_rect.midtop[1]+H*0.08))
slider_ratio_rect = slider_surf.get_rect(
    center=(W*0.5, H*0.18))

gauge_left = load_image('images/gauge_left.png')
gauge_right = load_image('images/gauge_right.png')

loop_active_surf = load_image('images/loop_active.png')
loop_inactive_surf = load_image('images/loop_inactive.png')
loop_active_surf = pygame.transform.smoothscale(loop_active_surf,
                                                (W*0.035, W*0.035))
loop_inactive_surf = pygame.transform.smoothscale(loop_inactive_surf,
                                                  (W*0.035, W*0.035))
loop_active_rect = loop_active_surf.get_rect(
    center=(control_rect.midtop[0]+W*0.09, control_rect.midtop[1]+H*0.08))
loop_inactive_rect = loop_inactive_surf.get_rect(
    center=(control_rect.midtop[0]+W*0.09, control_rect.midtop[1]+H*0.08))

energy_surf = load_image('images/energy.png')
arrow_surf = load_image('images/arrow.png')

legend_surf = load_image('images/legend.png')
legend_surf = pygame.transform.smoothscale(legend_surf, (H*0.11, H*0.11))


def legend_rect(rect):
    x, y = rect
    return (x+W*0.07, y+H*0.32)
# --------------------

# ---- hand ----


def get_hand_surf(V, theta):
    hs = pygame.transform.smoothscale(
        hand_surf, (H*0.007, H*0.28*V))
    hs = pygame.transform.rotate(hs, -theta)

    return hs
# --------------

# ---- power_gauge ----


def get_gauge_surf(guage_surf, power):
    gs = pygame.transform.scale(guage_surf, (-W*0.04*power, H*0.02))

    return gs
# ---------------------


# ---- energy ----
center0 = np.asarray(thermal_rect.center)
center1 = np.asarray(voltmeter_rect[1].center)
center2 = np.asarray(voltmeter_rect[2].center)
center3 = np.asarray(panel_rect.center)
distance01 = np.linalg.norm(center1-center0)
distance12 = np.linalg.norm(center2-center1)
distance23 = np.linalg.norm(center3-center2)
arg01 = np.arctan((center0[1]-center1[1]) /
                  (center0[0]-center1[0])) * 180/3.14
arg23 = np.arctan((center3[1]-center2[1]) /
                  (center2[0]-center3[0])) * 180/3.14

energywidth = W*0.01


def get_energy_surfs(p):
    size = 1 - 2 * abs(time - int(time) - 0.5)
    es01 = pygame.transform.scale(
        energy_surf, (distance01*1.2, abs(p[0, 1]) * energywidth))
    es01 = pygame.transform.rotate(es01, -arg01)
    es12 = pygame.transform.scale(
        energy_surf, (distance12*1.2, abs(p[1, 2]) * energywidth))
    es23 = pygame.transform.scale(
        energy_surf, (distance23*1.2, abs(p[2, 3]) * energywidth))
    es23 = pygame.transform.rotate(es23, arg23)

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


center01 = (center0 + center1) / 2
center12 = (center1 + center2) / 2
center23 = (center2 + center3) / 2


def get_energy_rects(surfs, p):
    er01 = surfs[0].get_rect(center=tuple(center01))
    er12 = surfs[1].get_rect(center=tuple(center12))
    er23 = surfs[2].get_rect(center=tuple(center23))

    devide = time - int(time)
    start01 = 0.75 * center0 + 0.25 * center1
    end01 = 0.25 * center0 + 0.75 * center1
    start12 = 0.75 * center1 + 0.25 * center2
    end12 = 0.25 * center1 + 0.75 * center2
    start23 = 0.75 * center2 + 0.25 * center3
    end23 = 0.25 * center2 + 0.75 * center3
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
selected_date = 0
calendar_active = False
# ------------------

# ---- graph ----
graph_active = False
# ---------------

# ---- sky ----


def sky_color(time):
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
time = 0
period = 12  # 1 ~ 24

linewidth = timeline_rect.width
startpoint = timeline_rect.midleft

period_left = slide_control_rect.midleft

dragging_time = False


def time_pos(time):

    return (startpoint[0] + time*linewidth/24, startpoint[1])


def period_pos(period):

    return (period_left[0] + period*slidewidth/23, period_left[1])


def format_time(time):
    hour = int(time)
    minute = int((time - hour) * 6) * 10

    return f'{hour:02}:{minute:02}'
# --------------


# ---- control ----
play = False
sliding = False
loop_active = False
# -----------------

# ---- ratio ----
ratio = 0.5

changing_ratio = False

slidewidth = slide_ratio_rect.width
ratio_left = slide_ratio_rect.midleft


def ratio_pos(ratio):

    return (ratio_left[0] + ratio*slidewidth, slide_ratio_rect.midleft[1])
# ---------------


# ---- loadflow ----
ps = PowerSystem(4)

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

lf = LoadFlow(ps)


def get_v_p(date, time):
    global calculated, V
    d_s = getdata.getdata(date, time)

    tan = np.sqrt(1 / (0.85 ** 2) - 1)
    d = d_s[0]
    s = d_s[1]
    ps.P[1] = - d * ratio
    ps.Q[1] = - d * ratio * tan
    ps.P[2] = - d * (1-ratio)
    ps.Q[2] = - d * (1-ratio) * tan
    ps.P[3] = s

    if not calculated:
        lf.calculate()
        calculated = True

        set_graph_data(lf.V)

    if lf.V is None:
        return None, None, None
    else:
        return lf.V, [theta * 180/3.14 for theta in lf.theta], lf.power.real


def set_graph_data(V_list):
    global V_temp, got_data
    if int(time) == 0:
        V_temp = [[0]*24 for _ in range(4)]
    if V_temp is not None:
        for i, v in enumerate(V_list):
            V_temp[i][int(time)] = v
        if int(time) == 23:
            if not got_data:
                figs.append(draw_graph.draw_graph(
                    date, *V_temp))
                if len(figs) > 4:
                    figs.pop(0)
                V_temp = [[0]*24 for _ in range(4)]
                got_data = True


V_temp = [[0]*24 for _ in range(4)]  # 4x24 の２次元配列. 各ノードの
figs = []

fig_rects = [(0, 0), (W*0.5, 0), (0, H*0.5), (W*0.5, H*0.5)]
got_data = False
# ------------------
calculated = False
hour = 0
date = 0
failed = False

while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not graph_active:
                if display_date_rect.collidepoint(event.pos):
                    calendar_active = not calendar_active
                if calendar_active:
                    for i in range(8):
                        if calendar_date_rect[i].collidepoint(event.pos):
                            selected_date = i
                            calendar_active = False
                            time = 0
                            ratio = 0.5
                            period = 12
                            got_data = False

                if graph_button_rect.collidepoint(event.pos):
                    graph_active = True
                    play = False
                    for i, fig in enumerate(figs):
                        figs[i] = pygame.transform.smoothscale(
                            fig, (W*0.5, H*0.5))

                if timeline_rect.collidepoint(event.pos):
                    time = int(
                        (event.pos[0] - startpoint[0]) * 24/linewidth)+0.5
                    dragging_time = True
                    V_temp = None

                if not play:
                    if play_rect.collidepoint(event.pos):
                        play = True
                        if failed:
                            failed = False
                            time = 0.
                elif stop_rect.collidepoint(event.pos):
                    play = False
                    time = int(time) + 0.5

                if not loop_active:
                    if loop_active_rect.collidepoint(event.pos):
                        loop_active = True
                elif loop_inactive_rect.collidepoint(event.pos):
                    loop_active = False

                if slider_ratio_rect.collidepoint(event.pos):
                    changing_ratio = True
                    got_data = False

                if slider_control_rect.collidepoint(event.pos):
                    sliding = True

            else:
                graph_active = False
        if event.type == pygame.MOUSEMOTION:
            if dragging_time:
                time_temp = int(
                    (pygame.mouse.get_pos()[0] - startpoint[0])
                    * 24/linewidth) + 0.5
                if 0 <= time_temp < 24:
                    time = time_temp
            if changing_ratio:
                ratio_temp = (pygame.mouse.get_pos()[0]
                              - ratio_left[0]) / slidewidth
                if 0 <= ratio_temp <= 1:
                    ratio = ratio_temp
            if sliding:
                period_temp = int(
                    (pygame.mouse.get_pos()[0] - period_left[0])
                    * 23/slidewidth)
                if 1 <= period_temp <= 24:
                    period = period_temp

        if event.type == pygame.MOUSEBUTTONUP:
            dragging_time = False
            changing_ratio = False
            sliding = False

    screen.fill(sky_color(time))
    screen.blit(bg_surf, bg_rect)

    pygame.draw.line(screen, (0, 0, 0),
                     panel_rect.center, voltmeter_rect[2].center, width=3)
    pygame.draw.line(screen, (0, 0, 0),
                     voltmeter_rect[1].center, voltmeter_rect[2].center,
                     width=3)
    pygame.draw.line(screen, (0, 0, 0),
                     thermal_rect.center, voltmeter_rect[1].center, width=3)

    # --loadflow--
    V, theta, p = get_v_p(selected_date, int(time))
    if V is not None:
        hand_surfs = [get_hand_surf(v, t) for v, t in zip(V, theta)]
        hand_rects = [hs.get_rect(center=ho)
                      for hs, ho in zip(hand_surfs, hand_origins)]
        energy_surfs = get_energy_surfs(p)
        energy_rects = get_energy_rects(energy_surfs, p)
    else:
        failed = True
        play = False
    if not failed:
        for es, er in zip(energy_surfs, energy_rects):
            screen.blit(es, er)
    screen.blit(voltmeter_surf, voltmeter_rect[0])
    screen.blit(voltmeter_surf, voltmeter_rect[1])
    screen.blit(voltmeter_surf, voltmeter_rect[2])
    screen.blit(voltmeter_surf, voltmeter_rect[3])
    screen.blit(panel_surf, panel_rect)
    screen.blit(thermal_surf, thermal_rect)
    if not failed:
        for i in range(4):
            screen.blit(hand_surfs[i], hand_rects[i])
            screen.blit(hand_origin_surf, hand_origin_rects[i])
    # --loadflow--

    screen.blit(graph_button_surf, graph_button_rect)

    screen.blit(timeline_surf, timeline_rect)
    time_indicator_rect = time_indicator_surf.get_rect(
        midbottom=time_pos(time))
    screen.blit(time_indicator_surf, time_indicator_rect)
    time_text_surf = time_font.render(f'{format_time(time)}', True,
                                      (255, 255, 255))
    time_text_rect = time_text_surf.get_rect(center=(W*0.22, H*0.06))
    screen.blit(time_text_surf, time_text_rect)

    gauge_left_surf = get_gauge_surf(gauge_left, ps.P[2])
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
        calculated = False
        hour = int(time)
        date = selected_date

    pygame.display.update()
    clock.tick(24)
