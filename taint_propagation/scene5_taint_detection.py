from manim import *
from pygments.styles.monokai import MonokaiStyle
from pygments.token import Name, Keyword


class TaintStyle(MonokaiStyle):
    styles = MonokaiStyle.styles.copy()
    styles[Name.Function] = "#a6e22e"
    styles[Name.Builtin] = "#66d9ef"
    styles[Keyword] = "#f92672"


class TaintDetectionScene(Scene):
    def construct(self):
        title = Text("Taint Propagation: Detection", font_size=36)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title))
        self.wait(0.4)

        subtitle = Text(
            "DFSan позволяет остановить выполнение, если tainted данные доходят до sink",
            font_size=16,
            color=YELLOW,
        )
        subtitle.next_to(title, DOWN, buff=0.3)
        self.play(Write(subtitle))
        self.wait(0.7)

        # Блок кода
        code_str = """void execute_command(const char *user) {
    char cmd[256];
    snprintf(cmd, sizeof(cmd), "echo Hello %s", user);

    dfsan_label cmd_label = dfsan_get_label(cmd);
    if (cmd_label != 0) {
        report_taint_violation(cmd_label, "system(cmd)");
        return;
    }

    system(cmd);
}"""

        code = Code(
            code_string=code_str,
            language="c++",
            tab_width=4,
            formatter_style=TaintStyle,
            background="rectangle",
            add_line_numbers=False,
            background_config={
                "stroke_width": 2,
                "stroke_color": GREEN,
                "fill_color": BLACK,
                "fill_opacity": 0.9,
            },
        )

        code_label = Text(
            "Обнаружение tainted данных перед системным вызовом",
            font_size=16,
            color=GREEN,
        )
        code_label.next_to(code, UP, buff=0.12)

        code_grp = VGroup(code, code_label)
        code_grp.scale(0.6)
        code_grp.move_to(UP * 0.35)

        self.play(Create(code), Write(code_label))
        self.wait(0.6)

        # Подсветка блоков
        line_count = 11
        line_height = code.height / (line_count + 2)

        def highlight_lines(first: int, last: int, color):
            span = last - first + 1
            rect = RoundedRectangle(
                corner_radius=0.04,
                width=code.width * 0.96,
                height=line_height * span,
                color=color,
                fill_color=color,
                fill_opacity=0.22,
                stroke_width=2.5,
            )
            rect.move_to(
                code.get_top() + DOWN * line_height * (first - 0.5),
                aligned_edge=UP,
            )
            return rect

        def show_step(first, last, color, title, text, side="left"):
            hl = highlight_lines(first, last, color)
            desc = VGroup(
                Text(title, font_size=11, color=color, weight=BOLD),
                Text(text, font_size=9, color=WHITE),
            ).arrange(DOWN, buff=0.05, aligned_edge=LEFT)

            shift_dir = LEFT if side == "left" else RIGHT
            desc.next_to(hl, shift_dir, buff=0.25)

            self.play(Create(hl), FadeIn(desc, shift=(-shift_dir) * 0.15))
            self.wait(1.6)
            self.play(FadeOut(hl), FadeOut(desc))

        # 1. Формирование команды (taint переносится в cmd)
        show_step(
            first=2,
            last=3,
            color=YELLOW,
            title="Propagation в команду",
            text="snprintf переносит taint из user в буфер cmd",
            side="left",
        )

        # 2. Получение taint-метки для cmd
        show_step(
            first=5,
            last=5,
            color=ORANGE,
            title="dfsan_get_label(cmd)",
            text="Читаем объединённый taint для всей строки команды",
            side="right",
        )

        # 3. Проверка и логирование нарушения
        show_step(
            first=6,
            last=8,
            color=RED,
            title="report_taint_violation",
            text="""Если label ≠ 0, фиксируем нарушение
и выходим до system(cmd)""",
            side="left",
        )

        # 4. Безопасный sink
        show_step(
            first=11,
            last=11,
            color=GREEN,
            title="Безопасный sink",
            text="system(cmd) вызывается только если cmd не tainted",
            side="right",
        )

        # Легенда снизу
        legend_box = RoundedRectangle(
            corner_radius=0.1,
            width=9,
            height=1.3,
            color=YELLOW,
            fill_opacity=0.1,
            stroke_width=2,
        )
        legend_box.to_edge(DOWN, buff=0.4)

        legend_title = Text(
            "Taint-детекция перед опасными операциями", font_size=14, color=YELLOW, weight=BOLD
        )
        legend_title.next_to(legend_box, UP, buff=0.12)

        item1 = VGroup(
            Circle(radius=0.08, color=YELLOW, fill_opacity=1, stroke_width=0),
            VGroup(
                Text("Команда наследует taint", font_size=10, color=YELLOW),
                Text("от пользовательского ввода", font_size=10, color=YELLOW),
            ).arrange(DOWN, buff=0.02, aligned_edge=LEFT),
        ).arrange(RIGHT, buff=0.05)

        item2 = VGroup(
            Circle(radius=0.08, color=ORANGE, fill_opacity=1, stroke_width=0),
            VGroup(
                Text("dfsan_get_label() извлекает", font_size=10, color=ORANGE),
                Text("taint-состояние строки", font_size=10, color=ORANGE),
            ).arrange(DOWN, buff=0.02, aligned_edge=LEFT),
        ).arrange(RIGHT, buff=0.05)

        item3 = VGroup(
            Circle(radius=0.08, color=RED, fill_opacity=1, stroke_width=0),
            VGroup(
                Text("report_taint_violation()", font_size=10, color=RED),
                Text("блокирует опасный вызов", font_size=10, color=RED),
            ).arrange(DOWN, buff=0.02, aligned_edge=LEFT),
        ).arrange(RIGHT, buff=0.05)

        item4 = VGroup(
            Circle(radius=0.08, color=GREEN, fill_opacity=1, stroke_width=0),
            VGroup(
                Text("system(cmd) вызывается", font_size=10, color=GREEN),
                Text("только для clean данных", font_size=10, color=GREEN),
            ).arrange(DOWN, buff=0.02, aligned_edge=LEFT),
        ).arrange(RIGHT, buff=0.05)

        legend_items = VGroup(item1, item2, item3, item4).arrange(RIGHT, buff=0.35)
        legend_items.move_to(legend_box)

        self.play(
            FadeIn(legend_box),
            Write(legend_title),
            FadeIn(legend_items, lag_ratio=0.2),
            run_time=3,
        )
        self.wait(2.0)

        self.play(*[FadeOut(m) for m in self.mobjects])
