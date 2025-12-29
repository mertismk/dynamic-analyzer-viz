from manim import *
from pygments.styles.monokai import MonokaiStyle
from pygments.token import Name, Keyword

# OFFICIAL DOCUMENTATION
# Clang Static Analyzer - Taint Analysis:
# https://clang.llvm.org/docs/analyzer/user-docs/TaintAnalysisConfiguration.html
#
# DataFlowSanitizer (DFSan):
# https://clang.llvm.org/docs/DataFlowSanitizer.html
# API: dfsan_set_label(), dfsan_get_label()
# Compilation: clang -fsanitize=dataflow program.c

class TaintStyle(MonokaiStyle):
    styles = MonokaiStyle.styles.copy()
    styles[Name.Function] = "#a6e22e"
    styles[Name.Builtin] = "#66d9ef"
    styles[Keyword] = "#f92672"


class TaintCompilation(Scene):
    def construct(self):
        title = Text("Taint Propagation: Процесс компиляции", font_size=36)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title))
        self.wait(0.4)

        # Исходный код (слева)
        source_str = """int main() {
    char* user_input = getenv("CMD");
    char cmd[256];
    sprintf(cmd, "ls %s", user_input);
    system(cmd);  // Vulnerability!
    return 0;
}"""

        source_code = Code(
            code_string=source_str,
            language="c++",
            tab_width=4,
            formatter_style=TaintStyle,
            background="rectangle",
            add_line_numbers=False,
            background_config={
                "stroke_width": 2,
                "stroke_color": WHITE,
                "fill_color": BLACK,
                "fill_opacity": 0.9,
            },
        )
        source_label = Text("Исходный код", font_size=32, color=WHITE)
        source_label.next_to(source_code, UP, buff=0.12)

        source_grp = VGroup(source_code, source_label)
        source_grp.scale(0.6)
        source_grp.move_to(LEFT * 4.0 + DOWN * 0.2)

        # Инструментированный код (справа)
        inst_str = """int main() {
    // DFSan instrumentation:
    char* user_input = getenv("CMD");
    dfsan_set_label(TAINT, user_input);
    
    char cmd[256];
    sprintf(cmd, "ls %s", user_input);
    // propagation
    
    if (dfsan_get_label(cmd) != 0)
        report_vulnerability();
    
    system(cmd);
    return 0;
}"""

        inst_code = Code(
            code_string=inst_str,
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
        inst_label = Text("Инструментированный код", font_size=32, color=GREEN)
        inst_label.next_to(inst_code, UP, buff=0.12)

        inst_grp = VGroup(inst_code, inst_label)
        inst_grp.scale(0.6)
        inst_grp.move_to(RIGHT * 4.0 + DOWN * 0.2)

        # Компилятор
        compiler = RoundedRectangle(
            corner_radius=0.12,
            width=2.4,
            height=1.6,
            color=BLUE,
            fill_opacity=0.15,
            stroke_width=3,
        )
        compiler.move_to(DOWN * 2.6)

        compiler_text = VGroup(
            Text("Clang", font_size=20, weight=BOLD, color=BLUE),
            Text("-fsanitize=dataflow", font_size=13, color=YELLOW),
        ).arrange(DOWN, buff=0.06)
        compiler_text.move_to(compiler)

        # Стрелки
        arrow_left = Arrow(
            source_code.get_bottom(),
            compiler.get_left() + UP * 0.3,
            color=YELLOW,
            stroke_width=4,
            buff=0.12,
        )
        arrow_right = Arrow(
            compiler.get_right() + UP * 0.3,
            inst_code.get_bottom(),
            color=GREEN,
            stroke_width=4,
            buff=0.12,
        )

        # Появление общей схемы
        self.play(Create(source_code), Write(source_label))
        self.wait(0.4)

        self.play(Create(compiler), Write(compiler_text))
        self.wait(0.2)

        self.play(Create(arrow_left))
        self.wait(0.2)

        self.play(Create(inst_code), Write(inst_label))
        self.wait(0.2)

        self.play(Create(arrow_right))
        self.wait(0.6)

        explanation = Text(
            "DFSan добавляет инструментацию для отслеживания taint",
            font_size=16,
            color=YELLOW,
        )
        explanation.next_to(title, DOWN, buff=0.25)
        self.play(Write(explanation))
        self.wait(0.8)

        # Убираем лишнее, оставляем только правый код
        self.play(
            FadeOut(source_grp),
            FadeOut(arrow_left),
            FadeOut(arrow_right),
            FadeOut(compiler),
            FadeOut(compiler_text),
            inst_grp.animate.move_to(ORIGIN + UP * 0.4).scale(1.05),
            run_time=0.7,
        )
        self.wait(0.3)

        # Подсветка по строкам
        line_count = 14  # реальное число строк в inst_str
        line_height = inst_code.height / (line_count + 2)

        def highlight_lines(first: int, last: int, color):
            """Создаёт прямоугольник поверх строк [first; last] включительно (1-based)."""
            lines_span = last - first + 1
            rect = RoundedRectangle(
                corner_radius=0.04,
                width=inst_code.width * 0.86,
                height=line_height * lines_span,
                color=color,
                fill_color=color,
                fill_opacity=0.25,
                stroke_width=3,
            )
            rect.align_to(inst_code, LEFT).shift(RIGHT * 0.12)
            # центр блока по вертикали
            rect.move_to(
                inst_code.get_top()
                + DOWN * line_height * (first - 0.5),
                aligned_edge=UP,
            )
            return rect

        # dfsan_set_label
        self.play(FadeOut(explanation), run_time=0.4)

        init_highlight = highlight_lines(3, 4, RED)
        init_desc = VGroup(
            Text("dfsan_set_label()", font_size=14, color=RED, weight=BOLD),
            Text("SOURCE: помечает user_input как tainted", font_size=12, color=WHITE),
            Text("Документация: DataFlowSanitizer API", font_size=10, color=BLUE),
        ).arrange(DOWN, buff=0.08)
        init_desc.next_to(init_highlight, LEFT, buff=0.5)

        self.play(Create(init_highlight), FadeIn(init_desc, shift=RIGHT * 0.15))
        self.wait(1.4)
        self.play(FadeOut(init_highlight), FadeOut(init_desc))

        # sprintf
        prop_highlight = highlight_lines(6, 7, ORANGE)
        prop_desc = VGroup(
            Text("sprintf()", font_size=14, color=ORANGE, weight=BOLD),
            Text("PROPAGATION: taint переходит в cmd", font_size=12, color=WHITE),
        ).arrange(DOWN, buff=0.08)
        prop_desc.next_to(prop_highlight, RIGHT, buff=0.5)

        self.play(Create(prop_highlight), FadeIn(prop_desc, shift=LEFT * 0.15))
        self.wait(1.4)
        self.play(FadeOut(prop_highlight), FadeOut(prop_desc))

        # dfsan_get_label + report
        check_highlight = highlight_lines(9, 10, YELLOW)
        check_desc = VGroup(
            Text("dfsan_get_label()", font_size=14, color=YELLOW, weight=BOLD),
            Text("SINK: проверка cmd перед system()", font_size=12, color=WHITE),
        ).arrange(DOWN, buff=0.08)
        check_desc.next_to(check_highlight, RIGHT, buff=0.5)

        self.play(Create(check_highlight), FadeIn(check_desc, shift=LEFT * 0.15))
        self.wait(1.4)
        self.play(FadeOut(check_highlight), FadeOut(check_desc))

        # Финальное резюме
        summary_box = RoundedRectangle(
            corner_radius=0.1,
            width=8.5,
            height=1.2,
            color=YELLOW,
            fill_opacity=0.1,
            stroke_width=2,
        )
        summary_box.to_edge(DOWN, buff=0.5)

        summary_title = Text(
            "DataFlowSanitizer (DFSan)", font_size=22, color=YELLOW, weight=BOLD
        )
        summary_title.next_to(summary_box, UP, buff=0.15)

        summary_items = VGroup(
            VGroup(
                Circle(radius=0.08, color=RED, fill_opacity=1, stroke_width=0),
                Text("dfsan_set_label", font_size=11, color=RED, weight=BOLD),
            ).arrange(RIGHT, buff=0.1),
            VGroup(
                Circle(radius=0.08, color=ORANGE, fill_opacity=1, stroke_width=0),
                Text("propagation через операции", font_size=11, color=ORANGE, weight=BOLD),
            ).arrange(RIGHT, buff=0.1),
            VGroup(
                Circle(radius=0.08, color=YELLOW, fill_opacity=1, stroke_width=0),
                Text("dfsan_get_label перед sink", font_size=11, color=YELLOW, weight=BOLD),
            ).arrange(RIGHT, buff=0.1),
        ).arrange(RIGHT, buff=0.5)
        summary_items.move_to(summary_box)

        self.play(
            FadeIn(summary_box),
            Write(summary_title),
            FadeIn(summary_items, lag_ratio=0.2),
            run_time=1.5,
        )
        self.wait(2)

        self.play(*[FadeOut(m) for m in self.mobjects])
