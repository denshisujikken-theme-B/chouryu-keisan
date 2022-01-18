import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('module://pygame_matplotlib.backend_pygame')


def draw_graph(n, v1, v2, v3, v4):
    fig, axes = plt.subplots(1, 1,)

    c1, c2, c3, c4 = "yellow", "green", "red", "blue"  # 各プロットの色
    l1, l2, l3, l4 = "ノード1", "ノード2", "ノード3", "ノード4"

    date = ['4/7', '4/17', '6/3', '6/7', '8/9', '10/3', '1/7', '3/15']

    axes.plot(v1, color=c1, label=l1)
    axes.plot(v2, color=c2, label=l2)
    axes.plot(v3, color=c3, label=l3)
    axes.plot(v4, color=c4, label=l4)
    axes.set_title(f'Voltage[pu]-Time({date[n]})')
    axes.set_xlim(0, 23)
    # axes.set_ylim(0.80, 1.02)
    axes.set_xticks([0, 6, 12, 18])
    axes.set_xticklabels(["0:00", "6:00", "12:00", "18:00"])
    axes.grid()

    fig.canvas.draw()
    return fig
