from manim import *
from pygments.styles.monokai import MonokaiStyle
from pygments.token import Name


class MSanStyle(MonokaiStyle):
    styles = MonokaiStyle.styles.copy()
    styles[Name.Function] = "#a6e22e"
    styles[Name.Builtin] = "#66d9ef"


class CompilationWithInstrumentation(Scene):
    def construct(self):
        title = Text("MemorySanitizer: Процесс компиляции", font_size=36)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title))
        self.wait(0.5)

        source_code_str = """int main() {
    int* ptr = new int[10];
    ptr[5] = 0;
    if (ptr[0]) { }
    delete[] ptr;
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

        source_label = Text("Исходный код", font_size=16, color=WHITE)
        source_label.next_to(source_code, UP, buff=0.12)

        source_grp = VGroup(source_code, source_label)
        source_grp.scale(0.7).to_edge(LEFT, buff=0.8).shift(UP * 0.8)

        self.play(Create(source_code), Write(source_label))
        self.wait(0.6)

        compiler = RoundedRectangle(
            corner_radius=0.12,
            width=2.2,
            height=1.6,
            color=BLUE,
            fill_opacity=0.15,
            stroke_width=3,
        )
        compiler.move_to(DOWN * 1.2)

        compiler_text = VGroup(
            Text("Clang", font_size=20, weight=BOLD, color=BLUE),
            Text("-fsanitize=", font_size=13, color=GREY),
            Text("memory", font_size=13, color=YELLOW, weight=BOLD),
        ).arrange(DOWN, buff=0.1)
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
    __msan_init();

    int* ptr = new int[10];
    __msan_poison(ptr, 40);

    ptr[5] = 0;
    __msan_unpoison(&ptr[5], 4);

    __msan_check(&ptr[0], 4);
    if (ptr[0]) { }

    delete[] ptr;
}"""

        inst_code = Code(
            code_string=inst_code_str,
            language="cpp",
            tab_width=4,
            formatter_style=MSanStyle,
            background="rectangle",
            add_line_numbers=False,
            background_config={
                "stroke_width": 2,
                "stroke_color": GREEN,
                "fill_color": BLACK,
                "fill_opacity": 0.9,
            },
        )

        inst_label = Text("Инструментированный код", font_size=16, color=GREEN)
        inst_label.next_to(inst_code, UP, buff=0.12)

        inst_grp = VGroup(inst_code, inst_label)
        inst_grp.scale(0.62).to_edge(RIGHT, buff=0.8).shift(UP * 0.8)

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
        self.wait(1)

        explanation = Text(
            "Компилятор автоматически вставляет:", font_size=15, color=YELLOW
        )
        explanation.next_to(title, DOWN, buff=0.2)
        self.play(Write(explanation))
        self.wait(0.5)

        self.play(
            FadeOut(source_grp),
            FadeOut(arrow_to_compiler),
            FadeOut(arrow_from_compiler),
            FadeOut(compiler),
            FadeOut(compiler_text),
            inst_grp.animate.move_to(ORIGIN + UP * 0.3).scale(1.15),
            run_time=0.8,
        )
        self.wait(0.3)

        line_height = inst_code.height / 16

        init_highlight = RoundedRectangle(
            corner_radius=0.04,
            width=inst_code.width * 0.85,
            height=line_height * 1.0,
            color=BLUE,
            fill_color=BLUE,
            fill_opacity=0.25,
            stroke_width=3,
        )
        init_highlight.align_to(inst_code, LEFT).shift(RIGHT * 0.12)
        init_highlight.move_to(
            inst_code.get_top() + DOWN * (line_height * 2.05), aligned_edge=UP
        )

        init_desc = VGroup(
            Text("__msan_init()", font_size=13, color=BLUE, weight=BOLD),
            Text("↓", font_size=10, color=BLUE),
            Text("Инициализация MSan", font_size=11, color=WHITE),
        ).arrange(DOWN, buff=0.08)
        init_desc.next_to(init_highlight, LEFT, buff=0.4)

        self.play(
            Create(init_highlight), FadeIn(init_desc, shift=RIGHT * 0.15), run_time=0.8
        )
        self.wait(1.2)
        self.play(FadeOut(init_highlight), FadeOut(init_desc), run_time=0.5)

        poison_highlight = RoundedRectangle(
            corner_radius=0.04,
            width=inst_code.width * 0.85,
            height=line_height * 1.0,
            color=RED,
            fill_color=RED,
            fill_opacity=0.25,
            stroke_width=3,
        )
        poison_highlight.align_to(inst_code, LEFT).shift(RIGHT * 0.12)
        poison_highlight.move_to(
            inst_code.get_top() + DOWN * (line_height * 5.05), aligned_edge=UP
        )

        poison_desc = VGroup(
            Text("__msan_poison()", font_size=13, color=RED, weight=BOLD),
            Text("↓", font_size=10, color=RED),
            Text("Пометить память как", font_size=11, color=WHITE),
            Text("неинициализированную", font_size=11, color=RED),
        ).arrange(DOWN, buff=0.05)
        poison_desc.next_to(poison_highlight, LEFT, buff=0.35)

        self.play(
            Create(poison_highlight),
            FadeIn(poison_desc, shift=RIGHT * 0.15),
            run_time=0.8,
        )
        self.wait(1.2)
        self.play(FadeOut(poison_highlight), FadeOut(poison_desc), run_time=0.5)

        unpoison_highlight = RoundedRectangle(
            corner_radius=0.04,
            width=inst_code.width * 0.85,
            height=line_height * 1.0,
            color=GREEN,
            fill_color=GREEN,
            fill_opacity=0.25,
            stroke_width=3,
        )
        unpoison_highlight.align_to(inst_code, LEFT).shift(RIGHT * 0.12)
        unpoison_highlight.move_to(
            inst_code.get_top() + DOWN * (line_height * 8.05), aligned_edge=UP
        )

        unpoison_desc = VGroup(
            Text("__msan_unpoison()", font_size=13, color=GREEN, weight=BOLD),
            Text("↓", font_size=10, color=GREEN),
            Text("Пометить память как", font_size=11, color=WHITE),
            Text("инициализированную", font_size=11, color=GREEN),
        ).arrange(DOWN, buff=0.05)
        unpoison_desc.next_to(unpoison_highlight, RIGHT, buff=0.35)

        self.play(
            Create(unpoison_highlight),
            FadeIn(unpoison_desc, shift=LEFT * 0.15),
            run_time=0.8,
        )
        self.wait(1.2)
        self.play(FadeOut(unpoison_highlight), FadeOut(unpoison_desc), run_time=0.5)

        check_highlight = RoundedRectangle(
            corner_radius=0.04,
            width=inst_code.width * 0.85,
            height=line_height * 1.0,
            color=ORANGE,
            fill_color=ORANGE,
            fill_opacity=0.25,
            stroke_width=3,
        )
        check_highlight.align_to(inst_code, LEFT).shift(RIGHT * 0.12)
        check_highlight.move_to(
            inst_code.get_top() + DOWN * (line_height * 10.05), aligned_edge=UP
        )

        check_desc = VGroup(
            Text("__msan_check()", font_size=13, color=ORANGE, weight=BOLD),
            Text("↓", font_size=10, color=ORANGE),
            Text("Проверить память", font_size=11, color=WHITE),
            Text("перед использованием", font_size=11, color=ORANGE),
        ).arrange(DOWN, buff=0.05)
        check_desc.next_to(check_highlight, RIGHT, buff=0.35)

        self.play(
            Create(check_highlight), FadeIn(check_desc, shift=LEFT * 0.15), run_time=0.8
        )
        self.wait(1.2)
        self.play(FadeOut(check_highlight), FadeOut(check_desc), run_time=0.5)

        self.play(FadeOut(explanation), run_time=0.5)

        summary_box = RoundedRectangle(
            corner_radius=0.1,
            width=7,
            height=1.2,
            color=YELLOW,
            fill_opacity=0.1,
            stroke_width=2,
        )
        summary_box.to_edge(DOWN, buff=0.5)

        summary_title = Text(
            "Функции MemorySanitizer:", font_size=14, color=YELLOW, weight=BOLD
        )
        summary_title.next_to(summary_box, UP, buff=0.15)

        summary_items = VGroup(
            VGroup(
                Circle(radius=0.08, color=BLUE, fill_opacity=1, stroke_width=0),
                Text("__msan_init", font_size=11, color=BLUE, weight=BOLD),
            ).arrange(RIGHT, buff=0.1),
            VGroup(
                Circle(radius=0.08, color=RED, fill_opacity=1, stroke_width=0),
                Text("__msan_poison", font_size=11, color=RED, weight=BOLD),
            ).arrange(RIGHT, buff=0.1),
            VGroup(
                Circle(radius=0.08, color=GREEN, fill_opacity=1, stroke_width=0),
                Text("__msan_unpoison", font_size=11, color=GREEN, weight=BOLD),
            ).arrange(RIGHT, buff=0.1),
            VGroup(
                Circle(radius=0.08, color=ORANGE, fill_opacity=1, stroke_width=0),
                Text("__msan_check", font_size=11, color=ORANGE, weight=BOLD),
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

        self.play(*[FadeOut(mob) for mob in self.mobjects])
