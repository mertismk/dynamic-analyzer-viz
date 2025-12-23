from manim import *
from pygments.styles.monokai import MonokaiStyle
from pygments.token import Name


class MSanStyle(MonokaiStyle):
    styles = MonokaiStyle.styles.copy()
    styles[Name.Function] = "#a6e22e"


class MSanErrorDetection(Scene):
    def construct(self):
        title = Text("MSan: Обнаружение ошибки UMR", font_size=36, color=RED)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title))
        self.wait(0.5)

        code_str = """int main() {
    __msan_init();

    int* ptr = new int[10];
    __msan_poison(ptr, 40);

    // ptr[5] = 0;
    // __msan_unpoison(&ptr[5], 4);

    __msan_check(&ptr[0], 4);
    if (ptr[0]) { }

    delete[] ptr;
}"""

        code = Code(
            code_string=code_str,
            language="cpp",
            tab_width=4,
            formatter_style=MSanStyle,
            background="rectangle",
            add_line_numbers=True,
            background_config={
                "stroke_width": 2,
                "stroke_color": RED,
                "fill_color": BLACK,
                "fill_opacity": 0.9,
            },
        )

        code_label = Text(
            "Код с ошибкой (пропущена инициализация)", font_size=16, color=RED
        )
        code_label.next_to(code, UP, buff=0.12)

        code_group = VGroup(code, code_label)
        code_group.scale(0.65)
        code_group.move_to(LEFT * 3.3 + DOWN * 0.1)

        self.play(Create(code), Write(code_label))
        self.wait(0.5)

        legend = VGroup(
            Text("✓ 0 = инициализировано", font_size=13, color=GREEN),
            Text("✗ 1 = не инициализировано", font_size=13, color=RED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        legend.to_corner(DR, buff=0.4)
        self.play(FadeIn(legend, shift=UP * 0.2))

        heap_box = RoundedRectangle(
            corner_radius=0.1,
            width=3.8,
            height=2.5,
            color=BLUE,
            fill_opacity=0.08,
            stroke_width=2.5,
        )
        heap_label = Text(
            "Основная память (ptr[10])", font_size=15, color=BLUE
        ).next_to(heap_box, UP, buff=0.15)

        shadow_box = RoundedRectangle(
            corner_radius=0.1,
            width=3.8,
            height=2.5,
            color=GREY,
            fill_opacity=0.08,
            stroke_width=2.5,
        )
        shadow_label = Text(
            "Теневая память (Shadow)", font_size=15, color=GREY
        ).next_to(shadow_box, UP, buff=0.15)

        mem_blocks = VGroup(heap_box, shadow_box)
        mem_blocks.arrange(DOWN, buff=0.5)
        mem_blocks.move_to(RIGHT * 3.2 + DOWN * 0.1)

        heap_label.next_to(heap_box, UP, buff=0.15)
        shadow_label.next_to(shadow_box, UP, buff=0.15)

        self.play(Create(VGroup(heap_box, heap_label, shadow_box, shadow_label)))

        heap_cells = VGroup()
        shadow_cells = VGroup()

        for i in range(10):
            h_cell = RoundedRectangle(
                corner_radius=0.03,
                width=0.34,
                height=0.42,
                color=BLUE,
                fill_opacity=0.15,
                stroke_width=2,
            )
            heap_cells.add(h_cell)

            s_cell = RoundedRectangle(
                corner_radius=0.03,
                width=0.34,
                height=0.42,
                color=GREY,
                fill_opacity=0.15,
                stroke_width=2,
            )
            shadow_cells.add(s_cell)

        heap_cells.arrange_in_grid(rows=2, cols=5, buff=0.06)
        heap_cells.move_to(heap_box.get_center())

        shadow_cells.arrange_in_grid(rows=2, cols=5, buff=0.06)
        shadow_cells.move_to(shadow_box.get_center())

        heap_indices = VGroup()
        for i in range(10):
            idx = Text(str(i), font_size=9, color=BLUE_B, weight=BOLD)
            idx.next_to(heap_cells[i], UP, buff=0.05)
            heap_indices.add(idx)

        self.play(
            Create(heap_cells),
            Create(shadow_cells),
            *[FadeIn(idx) for idx in heap_indices],
            run_time=0.8
        )

        line_height = code.height / 16

        phase1 = Text("Этап 1: Выделение памяти (poisoned)", font_size=15, color=YELLOW)
        phase1.next_to(title, DOWN, buff=0.25)

        highlight1 = RoundedRectangle(
            corner_radius=0.05,
            width=code.width * 0.88,
            height=line_height * 2.1,
            color=RED,
            fill_color=RED,
            fill_opacity=0.25,
            stroke_width=0,
        )
        highlight1.align_to(code, LEFT).shift(RIGHT * 0.15)
        highlight1.move_to(
            code.get_top() + DOWN * (line_height * 4.05), aligned_edge=UP
        )

        self.play(Write(phase1), FadeIn(highlight1))

        heap_vals = VGroup()
        shadow_vals = VGroup()
        for i in range(10):
            h_val = Text("?", font_size=10, color=GREY_A).move_to(heap_cells[i])
            s_val = Text("1", font_size=11, color=RED, weight=BOLD).move_to(
                shadow_cells[i]
            )
            heap_vals.add(h_val)
            shadow_vals.add(s_val)

        self.play(
            *[FadeIn(v) for v in heap_vals],
            *[FadeIn(v) for v in shadow_vals],
            run_time=0.8
        )
        self.wait(1.2)
        self.play(FadeOut(highlight1), FadeOut(phase1))

        phase2 = Text("Этап 2: Инициализация пропущена!", font_size=15, color=GREY)
        phase2.next_to(title, DOWN, buff=0.25)

        highlight2 = RoundedRectangle(
            corner_radius=0.05,
            width=code.width * 0.88,
            height=line_height * 2.1,
            color=GREY,
            fill_color=GREY,
            fill_opacity=0.2,
            stroke_width=2,
            stroke_opacity=0.6,
        )
        highlight2.align_to(code, LEFT).shift(RIGHT * 0.15)
        highlight2.move_to(
            code.get_top() + DOWN * (line_height * 7.05), aligned_edge=UP
        )

        self.play(Write(phase2), FadeIn(highlight2))

        skip_label = Text(
            "⚠ Строки закомментированы", font_size=12, color=YELLOW, weight=BOLD
        ).next_to(highlight2, RIGHT, buff=0.2)

        self.play(FadeIn(skip_label, shift=LEFT * 0.3))
        self.wait(1.5)
        self.play(FadeOut(highlight2), FadeOut(phase2), FadeOut(skip_label))

        phase3 = Text("Этап 3: Попытка чтения ptr[0]", font_size=15, color=RED)
        phase3.next_to(title, DOWN, buff=0.25)

        highlight3 = RoundedRectangle(
            corner_radius=0.05,
            width=code.width * 0.88,
            height=line_height * 2.1,
            color=RED,
            fill_color=ORANGE,
            fill_opacity=0.25,
            stroke_width=0,
        )
        highlight3.align_to(code, LEFT).shift(RIGHT * 0.15)
        highlight3.move_to(
            code.get_top() + DOWN * (line_height * 10.05), aligned_edge=UP
        )

        self.play(Write(phase3), FadeIn(highlight3))
        self.wait(0.5)

        self.play(
            Indicate(shadow_cells[0], color=RED, scale_factor=1.4),
            Indicate(shadow_vals[0], color=RED, scale_factor=1.4),
            run_time=1,
        )
        self.wait(0.3)

        error_box = RoundedRectangle(
            corner_radius=0.12,
            width=6.5,
            height=1.8,
            color=RED,
            fill_color=BLACK,
            fill_opacity=0.95,
            stroke_width=4,
        )
        error_box.to_edge(DOWN, buff=0.3)

        error_header = Text(
            "⚠ MSan ERROR DETECTED",
            font="Monospace",
            font_size=14,
            color=RED,
            weight=BOLD,
        )

        error_details = VGroup(
            Text(
                "WARNING: MemorySanitizer: use-of-uninitialized-value",
                font="Monospace",
                font_size=11,
                color=RED,
            ),
            Text("  at main() line 11", font="Monospace", font_size=11, color=YELLOW),
            Text(
                "SUMMARY: UMR (Uninitialized Memory Read) detected",
                font="Monospace",
                font_size=11,
                color=WHITE,
            ),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)

        error_content = VGroup(error_header, error_details).arrange(DOWN, buff=0.2)
        error_content.move_to(error_box.get_center())

        self.play(FadeIn(error_box, scale=0.95), Write(error_content), run_time=1.5)

        self.play(Wiggle(error_box, scale_value=1.03))
        self.wait(2.5)

        self.play(*[FadeOut(mob) for mob in self.mobjects])
