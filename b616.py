import csv
import time
import random
import logging
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

plt.rc(
    "font", family=["Arial", "Microsoft Yahei", "Heiti TC", "sans-serif"]
)  # 设定制表使用的字库


# 以下为读取本地数据和用户自定义函数


def xlsx_tolist():
    xlsx = pd.read_excel(r"put_your_score_here.xlsx")
    xlsx = xlsx[["title", "label", "detail", "score"]]
    xlsx.dropna(inplace=True)  # 删除未填入分数的行 credits to GK
    return xlsx.values.tolist()


def custom_input():
    custom_num = int(input("Hi, B616 here, 请输入显示/计算的成绩行数 e.g.30: "))
    if custom_num <= 0 or custom_num > len(in_list):
        print("输入量不符合数据量, 重来")
        time.sleep(0.5)
        exit()
    return custom_num


def read_ptt_history_csv():
    with open("ptt_history.csv", mode="r", newline="") as f:
        reader = csv.reader(f)

        x_time = []  # x-axis 年月日时间
        y_realptt = []  # y-axis 用户输入的实际ptt
        y_baseptt = []  # y-axis 仅b30底分的ptt
        y_maxiptt = []  # y-axis r10=b10时的理论最高ptt
        for row in reader:
            x_time.append(row[0])
            y_realptt.append(float(row[1]))
            y_baseptt.append(float(row[2]))
            y_maxiptt.append(float(row[3]))

    return x_time, y_realptt, y_baseptt, y_maxiptt


# 以下为排序和计算函数


def get_desc_ra_list():
    invalid_score = []
    for row in in_list:
        score = row[3]  # 玩家输入的得分(score)
        detail = row[2]  # 谱面的细节定数(detail)
        if score >= 10002237 or score < 1002237:
            # 不合法的score(2237为1far时score不超过10M的物量阈值)
            invalid_score.append(row)
            continue
        if score >= 10000000:
            # 很不幸,你的准度并不会在PM后带来任何rating提升, 准度b歇歇吧
            rating = detail + 2
            row.append(rating)
            continue
        if score >= 9800000:
            # 认认真真的推分哥, salute! 请保持下去, 飞升之路就在脚下
            rating = detail + (score - 9800000) / 200000 + 1
            row.append(rating)
            continue
        if score >= 1002237:
            # 没有ex还想吃分? ex以下单曲rating低得可怜, 能不能推推
            rating = detail + (score - 9500000) / 300000
            rating = max(rating, 0)  # 0单曲ra真的有可能出现的, 我猜是你家猫打的(
            row.append(rating)
            continue
    if len(invalid_score) != 0:  # 如果有出现不合法的score输入:
        for error_row in invalid_score:
            print(
                "Your score of",
                error_row[0],
                "is",
                error_row[3],
                ", which might be invalid, please check xlsx then run again",
            )
        time.sleep(1)
        input("Press enter to continue")
    # 最后返回添加了rating的列表
    return sorted(in_list, key=lambda s: s[4], reverse=True)


def get_cust_avg():
    ra_sum = 0
    for row in desc_ra_list[0:custom_num]:
        ra_sum += row[4]
    return ra_sum / custom_num


def get_b30_avg():
    b10_sum = 0
    for row in desc_ra_list[0:10]:
        b10_sum += row[4]  # row[4]为上个方法append的单曲rating值
    restb20_sum = 0
    for row in desc_ra_list[10:30]:
        restb20_sum += row[4]
    return (
        (restb20_sum + b10_sum) / 30,  # 纯b30底分
        (restb20_sum + b10_sum * 2) / 40,  # r10=b10时的最高ptt计算公式
    )


def write_ptt_history_csv():
    with open("ptt_history.csv", mode="a", newline="") as f:
        line = [
            time.strftime("%Y-%m-%d", time.localtime()),
            real_ptt_input,
            str(b30_only),
            str(b30_withr10),
        ]
        writer = csv.writer(f)
        writer.writerow(line)


# 以下为数据分析呈现函数


def show_desc_ra_list():
    print()

    def print_row(row):
        print(f"{row[0]} {row[1]} {row[2]} score: {int(row[3])} rating: {row[4]:.4f}")

    rows = desc_ra_list[0:custom_num]
    for row in rows[:30]:  # Print at most 30 rows
        print_row(row)
    print()

    if custom_num_over30:  # If >= 30 rows, print b30 info
        print(f"b30底分: {b30_only:.4f} (忽略r10)")
        print(f"r10=b10时的理论最高ptt: {b30_withr10:.4f}")
        print("---------b30 finished---------")
        print()

    for row in rows[30:]:  # Print the rest
        print_row(row)

    if custom_num != 30:  # No need for repeated b30
        print(f"b{custom_num}底分: {cust_average:.4f} (忽略r10)")
        print(f"---------b{custom_num} finished---------")


def suggest_song():
    target_rating = desc_ra_list[30][4]  # B30th的单曲ra, 超过这个就能推B30底分
    for i in range(min(len(desc_ra_list), 80), 30, -1):
        line = desc_ra_list[random.randint(30, i - 1)]
        # line=randint的范围会随着循环逐渐从30到min(len(desc_ra_list), 80)
        # 每轮上限-1直到最后指定30, 所以接近B30th的分数有更高概率被选中
        detail = line[2]
        # 以下是一个比较取巧的判断方式, 通过目标rating和谱面定数之差确认能否推荐(能否满足if/elif)
        dt_ra_diff = target_rating - detail
        if dt_ra_diff >= 1 and dt_ra_diff < 2:  # 说明需要的score在980w到1000w之间
            target_score = 9800000 + (target_rating - detail - 1) * 200000
            title = line[0]
            label = line[1]
            print(
                f"只要把 {title} 的 {label} 难度"
                f"推到 {int(target_score)+1} 就可以推b30底分了哦~"
            )
            print()
            break
        elif dt_ra_diff > 0 and dt_ra_diff < 1:  # 说明需要的score在950w到980w之间
            target_score = 9500000 + (target_rating - detail) * 300000
            title = line[0]
            label = line[1]
            print(
                f"只要把 {title} 的 {label} 难度"
                f"推到 {int(target_score)+1} 就可以推b30底分了哦~"
            )
            print()
            break


def draw_rt_sc_chart():
    # 生成 rating/定数 图
    def rating2detail_chart():
        desc_dtra_list = sorted(
            desc_ra_list[0:custom_num], key=lambda s: (s[2], s[4]), reverse=True
        )  # 对ra_list排序: 根据定数倒序, 同定数下rating倒序
        sg_title = []  # song title (曲名)
        x_detail = []  # x-axis detail (定数)
        y_rating = []  # y-axis rating (单曲ptt)
        for row in desc_dtra_list:
            sg_title.append(row[0])
            x_detail.append(row[2])
            y_rating.append(row[4])

        lx_dt = min(x_detail)
        mx_dt = max(x_detail)
        ptp_xdt = mx_dt - lx_dt  # 上下限 ptp of numpy
        ly_rt = min(y_rating)
        my_rt = max(y_rating)
        ptp_yrt = my_rt - ly_rt
        ###################下一段是对图表进行初始化和自定义###################
        fig, ax = plt.subplots()
        ax.scatter(x_detail, y_rating, s=(20 - pow(custom_num, 0.5)))
        ax.set_xlabel("谱面定数", fontsize=12)
        ax.set_ylabel("单曲Rating", fontsize=12)
        ax.axis([lx_dt - 0.01, mx_dt + 0.05, ly_rt - 0.01, my_rt + 0.02])
        # 设置坐标轴的取值范围
        ax.tick_params(
            axis="both", which="major", labelright=True, labelsize=10, pad=2, color="r"
        )
        # 设置刻度标记的样式
        ax.xaxis.set_major_locator(ticker.MultipleLocator(0.1))
        ax.yaxis.set_major_locator(ticker.MultipleLocator(0.1))
        # 横纵轴标注以0.1为单位步进 (即arcaea官方定数的最小单位)
        ax.grid(axis="y", color="r", linestyle="--", linewidth=0.4)
        # 设置图表的外观样式
        if custom_num_over30:  # 生成ptt横线
            ax.axhline(
                y=b30_withr10,
                color="b",
                linewidth=1,
                linestyle="dotted",
                label=f"理论最高  ptt:{b30_withr10:.4f}",
            )
            ax.axhline(
                y=float(real_ptt_input),
                color="c",
                linewidth=1,
                linestyle="dashed",
                label=f"当前实际  ptt:{real_ptt_input}",
            )
            ax.axhline(
                y=b30_only,
                color="g",
                linewidth=1,
                linestyle="dotted",
                label=f"仅b30底分ptt:{b30_only:.4f}",
            )
            ax.legend(loc="best")  # 自动调整图例到最佳位置
        ###################下一段是对每个点生成曲名文字标注###################
        last_ra = 0  # 上一轮的rating单曲ptt
        last_dt = 0  # 上一轮的detail谱面定数,定数不会为0所以第一轮必进else
        last_labelen = 0  # 上一轮曲名长度
        for i, label in enumerate(sg_title):
            x = x_detail[i]
            y = y_rating[i]
            if (
                last_ra - y < (0.005 * ptp_yrt) and last_dt == x
            ):  # 如果跟上一个(同定数的)成绩在y轴距离过近:
                extend_len += last_labelen  # 根据曲名长度累积的 额外位移距离因数
                extend_counter += 1  # 根据重叠个数累积的 基础位移距离因数
                ax.annotate(
                    label,
                    xy=(x, y),
                    xytext=(
                        x + extend_counter * pow(ptp_xdt, 0.5) / 40 + extend_len / 180,
                        y - ptp_yrt / 400,
                    ),
                    fontsize=max(3, 10 - ptp_xdt - 0.04 * custom_num),
                )
            else:
                extend_len = 0
                extend_counter = 0
                ax.annotate(
                    label,
                    xy=(x, y),
                    xytext=(
                        x + ptp_xdt / 800,
                        y - ptp_yrt / 400,
                    ),
                    fontsize=max(4, 10 - ptp_xdt - 0.04 * custom_num),
                )
            # 以上的魔数都是为了调整annotation位置, 很抱歉都是试出来的, 因为adjust太烂
            last_ra = y
            last_dt = x
            last_labelen = len(label)
        plt.show()

    #  生成 score/定数 图
    def score2detail_chart():
        desc_dtsc_list = sorted(
            desc_ra_list[0:custom_num], key=lambda s: (s[2], s[3]), reverse=True
        )  # 对ra_list排序: 根据定数倒序, 同定数下score倒序
        sg_title = []  # song title (曲名)
        x_detail = []  # x-axis detail (定数)
        y1_score = []  # y-axis score (单曲得分)
        for row in desc_dtsc_list:
            sg_title.append(row[0])
            x_detail.append(row[2])
            y1_score.append(row[3])

        lx_dt = min(x_detail)
        mx_dt = max(x_detail)
        ptp_xdt = mx_dt - lx_dt
        ly_sc = min(y1_score)
        my_sc = max(y1_score)
        ptp_ysc = my_sc - ly_sc
        ###################下一段是对图表进行初始化和自定义###################
        fig, ax = plt.subplots()
        ax.scatter(x_detail, y1_score, s=(20 - pow(custom_num, 0.5)))
        ax.set_xlabel("谱面定数", fontsize=12)
        ax.set_ylabel("单曲Score", fontsize=12)
        ax.axis([lx_dt - 0.01, mx_dt + 0.05, ly_sc - 1500, 1e7 + 5000])
        # 设置坐标轴的取值范围, Y轴最高固定取10M+5000(即PM线上一些)
        ax.tick_params(
            axis="both", which="major", labelright=True, labelsize=10, pad=2, color="r"
        )
        # 设置刻度标记的样式
        ax.xaxis.set_major_locator(ticker.MultipleLocator(0.1))
        # 横轴标注以0.1为单位步进 (即arcaea官方定数的最小单位)
        ax.grid(axis="y", color="r", linestyle="--", linewidth=0.4)
        # 设置图表的外观样式
        ###################下一段是对每个点生成曲名文字标注###################
        last_sc = 0  # 上一轮的score数值
        last_dt = 0  # 上一轮的谱面定数
        last_labelen = 0  # 上一轮曲名长度
        for i, label in enumerate(sg_title):
            x = x_detail[i]
            y = y1_score[i]
            if (
                last_sc - y < (0.008 * ptp_ysc) and last_dt == x
            ):  # 如果两个同定数的成绩y轴距离过近:
                extend_len += last_labelen
                extend_counter += 1
                ax.annotate(
                    label,
                    xy=(x, y),
                    xytext=(
                        x + extend_counter * pow(ptp_xdt, 0.5) / 40 + extend_len / 180,
                        y - ptp_ysc / 400,
                    ),
                    fontsize=max(4, 10 - ptp_xdt - 0.04 * custom_num),
                )
            else:
                extend_len = 0
                extend_counter = 0
                ax.annotate(
                    label,
                    xy=(x, y),
                    xytext=(
                        x + ptp_xdt / 800,
                        y - ptp_ysc / 400,
                    ),
                    fontsize=max(3, 10 - ptp_xdt - 0.04 * custom_num),
                )
                # 以上的魔数都是为了调整annotation位置
            last_sc = y
            last_dt = x
            last_labelen = len(label)
        ################################################################
        plt.show()

    rating2detail_chart()
    score2detail_chart()


def draw_history_b30_chart():
    line = read_ptt_history_csv()  # 打开csv并读取用户过去填入的数据
    x_time = line[0]
    if len(x_time) == 0:
        print("ptt_history数据为空, 跳过生成b30折线图")
        time.sleep(1)
        return
    x_time = [datetime.strptime(d, "%Y-%m-%d") for d in x_time]
    dot_size = max((50 - pow(len(x_time), 0.5)), 8)

    y_realptt = line[1]
    y_maxiptt = line[2]
    y_baseptt = line[3]
    plt.scatter(x_time, y_realptt, s=dot_size, label="真实ptt")
    plt.scatter(x_time, y_baseptt, s=dot_size, label="仅底分ptt")
    plt.scatter(x_time, y_maxiptt, s=dot_size, label="理论最高ptt")
    plt.tick_params(axis="x", labelrotation=61.6)
    plt.xlabel("年-月-日", fontsize=12)
    plt.ylabel("ptt", fontsize=12)
    plt.legend(loc="best")
    plt.show()


if __name__ == "__main__":

    logging.getLogger("matplotlib.font_manager").setLevel(
        logging.ERROR
    )  # 忽略字体Error级以下的报错

    in_list = xlsx_tolist()  # 读入xlsx文件转换成标准list
    custom_num = custom_input()  # 让用户输入想要查看的成绩数量
    custom_num_over30 = custom_num >= 30

    desc_ra_list = get_desc_ra_list()  # 数据有效性检查, 返回倒序排列ra的list
    cust_average = get_cust_avg()  # 根据用户输入的成绩数量计算rating均值
    if custom_num_over30:
        b30_pack = get_b30_avg()  # 计算b30并return以下两个数据:
        b30_only = b30_pack[0]  # 仅考虑b30底分的ptt
        b30_withr10 = b30_pack[1]  # r10=b10时的理论最高ptt
        real_ptt_input = input("请输入当前您的实际ptt(例 12.47): ")
        if input("是否要更新历史ptt数据(Y/N): ").upper() == "Y":  # y和Y都会确认
            write_ptt_history_csv()  # 把 real_ptt_input和b30_withr10 存档, 用来生成变化图像
        print()

    show_desc_ra_list()  # 展示根据rating排序的分数列表
    if len(desc_ra_list) > 30:  # 如果有超过30行数据则:
        suggest_song()  # 尝试给用户推荐一个能替换b30th的谱面
    draw_rt_sc_chart()  # 展示rating or score/detail关系图
    draw_history_b30_chart()  # 展示b30/time, ptt变化记录
