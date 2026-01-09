from manim import *
from pygments.styles.monokai import MonokaiStyle
from pygments.token import Name


class MSanStyle(MonokaiStyle):
    styles = MonokaiStyle.styles.copy()
    styles[Name.Function] = "#a6e22e"


class CompilationScene(Scene):
    def construct(self):
        title = Text("MemorySanitizer: Процесс компиляции", font_size=40, font="Inter")
        title.to_edge(UP, buff=0.3)
        self.play(Write(title))
        self.wait(0.5)

        source_code_str = """int main() {
    int* arr = new int[5];
    arr[0] = 10;
    arr[1] = 20;
    arr[3] = 40;
    arr[4] = 50;
    
    if (arr[0]) { }
    if (arr[2]) { }
    
    delete[] arr;
}"""

        source_code = Code(
            code_string=source_code_str,
            language="cpp",
            tab_width=4,
            formatter_style=MSanStyle,
            background="rectangle",
            add_line_numbers=False,
            background_config={
                "stroke_width": 2,
                "stroke_color": WHITE,
                "fill_color": BLACK,
                "fill_opacity": 0.9,
            },
        )

        source_label = Text("Исходный код", font_size=18, color=WHITE, font="Inter")
        source_label.next_to(source_code, UP, buff=0.15)

        source_grp = VGroup(source_code, source_label)
        source_grp.scale(0.75).to_edge(LEFT, buff=0.8).shift(UP * 0.8)

        self.play(
            FadeIn(source_code, shift=RIGHT * 0.3, scale=0.9),
            Write(source_label, run_time=0.8),
            run_time=1.2,
        )
        self.wait(0.6)

        compiler = RoundedRectangle(
            corner_radius=0.12,
            width=2.4,
            height=1.8,
            color=BLUE,
            fill_opacity=0.15,
            stroke_width=3,
        )
        compiler.next_to(source_code, DOWN, buff=0.8)

        compiler_text = VGroup(
            Text("Clang", font_size=22, weight=BOLD, color=BLUE, font="Inter"),
            Text(
                "-fsanitize=memory",
                font_size=15,
                color=YELLOW,
                weight=BOLD,
                font="Inter",
            ),
        ).arrange(DOWN, buff=0.15)
        compiler_text.move_to(compiler)

        arrow_to_compiler = CurvedArrow(
            source_code.get_bottom(),
            compiler.get_left() + UP * 0.3,
            color=YELLOW,
            stroke_width=4,
            angle=-TAU / 8,
        )

        self.play(
            Create(arrow_to_compiler),
            Create(compiler),
            Write(compiler_text),
            run_time=1,
        )
        self.wait(0.6)

        inst_code_str = """int main() {
    int* arr = new int[5];

    arr[0] = 10;
    __msan_unpoison(&arr[0], 4);
    arr[1] = 20;
    __msan_unpoison(&arr[1], 4);
    arr[3] = 40;
    __msan_unpoison(&arr[3], 4);
    arr[4] = 50;
    __msan_unpoison(&arr[4], 4);

    __msan_check_mem_is_initialized(&arr[0], 4);
    if (arr[0]) { }

    __msan_check_mem_is_initialized(&arr[2], 4);
    if (arr[2]) { }

    delete[] arr;
}"""

        inst_code = Code(
            code_string=inst_code_str,
            language="cpp",
            tab_width=4,
            formatter_style=MSanStyle,
            background="rectangle",
            add_line_numbers=True,
            background_config={
                "stroke_width": 2,
                "stroke_color": GREEN,
                "fill_color": BLACK,
                "fill_opacity": 0.9,
            },
        )

        inst_label = Text(
            "Инструментированный код", font_size=18, color=GREEN, font="Inter"
        )
        inst_label.next_to(inst_code, UP, buff=0.15)

        inst_grp = VGroup(inst_code, inst_label)
        inst_grp.scale(0.58).to_edge(RIGHT, buff=0.7).shift(UP * 0.5)

        arrow_from_compiler = CurvedArrow(
            compiler.get_right() + UP * 0.3,
            inst_code.get_bottom(),
            color=GREEN,
            stroke_width=4,
            angle=TAU / 8,
        )

        self.play(
            Create(arrow_from_compiler),
            Create(inst_code),
            Write(inst_label),
            run_time=1,
        )
        self.wait(2)

        self.play(
            FadeOut(title, shift=UP * 0.3),
            FadeOut(source_grp, shift=LEFT * 0.5),
            FadeOut(arrow_to_compiler, shift=DOWN * 0.3),
            FadeOut(arrow_from_compiler, shift=DOWN * 0.3),
            FadeOut(compiler, scale=0.8),
            FadeOut(compiler_text, scale=0.8),
            inst_grp.animate.scale(1.1).move_to(LEFT * 3.5 + DOWN * 0.3),
            run_time=1.2,
            rate_func=smooth,
        )
        self.wait(0.5)
