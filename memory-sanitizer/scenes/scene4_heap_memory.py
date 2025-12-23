from manim import *
from pygments.styles.monokai import MonokaiStyle
from pygments.token import Name


class MSanStyle(MonokaiStyle):
    styles = MonokaiStyle.styles.copy()
    styles[Name.Function] = "#a6e22e"


class DeleteAndPoison(Scene):
    def construct(self):
        title = Text("MSan: Освобождение памяти", font_size=36, color=ORANGE)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title))
        self.wait(0.5)

        code_str = """int main() {
    __msan_init();

    int* ptr = new int[10];
    __msan_poison(ptr, 40);

    ptr[5] = 0;
    __msan_unpoison(&ptr[5], 4);

    __msan_check(&ptr[5], 4);
    if (ptr[5]) { }

    delete[] ptr;
    __msan_poison(ptr, 40);
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
                "stroke_color": ORANGE,
                "fill_color": BLACK,
                "fill_opacity": 0.9,
            },
        )

        code_label = Text("Освобождение памяти", font_size=16, color=ORANGE)
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

        phase1 = Text(
            "Начальное состояние: ptr[5] инициализирован", font_size=15, color=YELLOW
        )
        phase1.next_to(title, DOWN, buff=0.25)

        self.play(Write(phase1))

        heap_vals = VGroup()
        shadow_vals = VGroup()

        for i in range(10):
            if i == 5:
                h_val = Text("0", font_size=10, color=GREEN, weight=BOLD).move_to(
                    heap_cells[i]
                )
                s_val = Text("0", font_size=11, color=GREEN, weight=BOLD).move_to(
                    shadow_cells[i]
                )
            else:
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
        self.play(FadeOut(phase1))

        line_height = code.height / 17

        phase2 = Text("delete[] ptr — освобождение памяти", font_size=15, color=RED)
        phase2.next_to(title, DOWN, buff=0.25)

        highlight2 = RoundedRectangle(
            corner_radius=0.05,
            width=code.width * 0.88,
            height=line_height * 2.4,
            color=RED,
            fill_color=RED,
            fill_opacity=0.25,
            stroke_width=0,
        )
        highlight2.align_to(code, LEFT).shift(RIGHT * 0.15)
        highlight2.move_to(
            code.get_top() + DOWN * (line_height * 12.9), aligned_edge=UP
        )

        self.play(Write(phase2), FadeIn(highlight2))

        trash_vals = VGroup()
        poison_vals = VGroup()

        for i in range(10):
            trash = Text("✗", font_size=10, color=RED).move_to(heap_cells[i])
            poison = Text("1", font_size=11, color=RED, weight=BOLD).move_to(
                shadow_cells[i]
            )
            trash_vals.add(trash)
            poison_vals.add(poison)

        for i in range(10):
            self.play(
                ReplacementTransform(heap_vals[i], trash_vals[i]),
                ReplacementTransform(shadow_vals[i], poison_vals[i]),
                Flash(heap_cells[i], color=RED, flash_radius=0.25, num_lines=8),
                Flash(shadow_cells[i], color=RED, flash_radius=0.25, num_lines=8),
                run_time=0.15,
            )

        warning_box = RoundedRectangle(
            corner_radius=0.1,
            width=3.8,
            height=0.9,
            color=RED,
            fill_color=BLACK,
            fill_opacity=0.95,
            stroke_width=4,
        )
        warning_box.next_to(shadow_box, DOWN, buff=0.3)

        warning_text = VGroup(
            Text("⚠ Память освобождена!", font_size=13, color=RED, weight=BOLD),
            Text("Любое обращение — ошибка", font_size=10, color=WHITE),
        ).arrange(DOWN, buff=0.1)
        warning_text.move_to(warning_box)

        self.play(FadeIn(warning_box), Write(warning_text))
        self.wait(2)

        self.play(*[FadeOut(mob) for mob in self.mobjects])
