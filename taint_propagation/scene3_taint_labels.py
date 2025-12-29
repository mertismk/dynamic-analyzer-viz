from manim import *
from pygments.styles.monokai import MonokaiStyle
from pygments.token import Name, Keyword


class TaintStyle(MonokaiStyle):
    styles = MonokaiStyle.styles.copy()
    styles[Name.Function] = "#a6e22e"
    styles[Name.Builtin] = "#66d9ef"
    styles[Keyword] = "#f92672"


class TaintLabelsScene(Scene):
    def construct(self):
        title = Text("Taint Propagation: Taint Labels", font_size=36)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title))
        self.wait(0.4)

        subtitle = Text(
            "DFSan хранит taint в label-ах, которые привязаны к памяти",
            font_size=16,
            color=YELLOW,
        )
        subtitle.next_to(title, DOWN, buff=0.25)
        self.play(Write(subtitle))
        self.wait(0.7)

        # Блок кода
        code_str = """// DFSan example with labels
dfsan_label input_label = dfsan_create_label("user input", 0);
char *user = getenv("CMD");
dfsan_set_label(input_label, user, strlen(user));

char cmd[256];
sprintf(cmd, "ls %s", user);

dfsan_label cmd_label = dfsan_get_label(cmd);
if (cmd_label != 0) {
    report_vulnerability();
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
            "Использование taint labels в DFSan",
            font_size=16,
            color=GREEN,
        )
        code_label.next_to(code, UP, buff=0.12)

        code_grp = VGroup(code, code_label)
        code_grp.scale(0.6)
        code_grp.move_to(UP * 0.5)

        self.play(Create(code), Write(code_label))
        self.wait(0.6)

        # Подсветка областей кода
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
                # code.get_top() + DOWN * line_height,
                aligned_edge=UP,
            )
            return rect

        def show_step(first, last, color, title, text, side="left"):
            hl = highlight_lines(first, last, color)
            desc = VGroup(
                Text(title, font_size=12, color=color, weight=BOLD),
                Text(text, font_size=10, color=WHITE),
            ).arrange(DOWN, buff=0.05, aligned_edge=LEFT)

            shift_dir = LEFT if side == "left" else RIGHT
            desc.next_to(hl, shift_dir, buff=0.35)

            self.play(Create(hl), FadeIn(desc, shift=(-shift_dir) * 0.15))
            self.wait(1.6)
            self.play(FadeOut(hl), FadeOut(desc))

        # 1. dfsan_create_label()
        show_step(
            first=2,
            last=2,
            color=RED,
            title="dfsan_create_label()",
            text="""Создаёт taint label
для логического источника""",
            side="left",
        )

        # 2. dfsan_set_label()
        show_step(
            first=4,
            last=4,
            color=ORANGE,
            title="dfsan_set_label()",
            text="Присваивает label байтам памяти (user)",
            side="left",
        )

        # 3. Propagation через sprintf
        show_step(
            first=6,
            last=7,
            color=YELLOW,
            title="Propagation",
            text="Операции автоматически переносят label-ы",
            side="right",
        )

        # 4. dfsan_get_label() + if
        show_step(
            first=9,
            last=10,
            color=BLUE,
            title="dfsan_get_label()",
            text="""Считывает объединённый label
для cmd перед проверкой""",
            side="right",
        )

        # Легенда labels внизу
        legend_box = RoundedRectangle(
            corner_radius=0.1,
            width=11,
            height=1.3,
            color=YELLOW,
            fill_opacity=0.1,
            stroke_width=2,
        )
        legend_box.to_edge(DOWN, buff=0.4)

        legend_title = Text(
            "DFSan labels (taint метки)", font_size=14, color=YELLOW, weight=BOLD
        )
        legend_title.next_to(legend_box, UP, buff=0.12)

        item1 = VGroup(
            Circle(radius=0.08, color=RED, fill_opacity=1, stroke_width=0),
            Text("Создаются для источников (SOURCE)", font_size=11, color=RED),
        ).arrange(RIGHT, buff=0.08)

        item2 = VGroup(
            Circle(radius=0.08, color=ORANGE, fill_opacity=1, stroke_width=0),
            Text("Автоматически распространяются при операциях", font_size=11, color=ORANGE),
        ).arrange(RIGHT, buff=0.08)

        item3 = VGroup(
            Circle(radius=0.08, color=GREEN, fill_opacity=1, stroke_width=0),
            Text("Проверяются перед sink (условие if)", font_size=11, color=GREEN),
        ).arrange(RIGHT, buff=0.08)

        legend_items = VGroup(item1, item2, item3).arrange(RIGHT, buff=0.4)
        legend_items.move_to(legend_box)

        self.play(
            FadeIn(legend_box),
            Write(legend_title),
            FadeIn(legend_items, lag_ratio=0.2),
            run_time=3,
        )
        self.wait(2)
