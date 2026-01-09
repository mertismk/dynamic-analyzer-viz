from manim import *
from pygments.styles.monokai import MonokaiStyle
from pygments.token import Name


class MSanStyle(MonokaiStyle):
    styles = MonokaiStyle.styles.copy()
    styles[Name.Function] = "#a6e22e"


class ChecksScene(Scene):
    def construct(self):
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
        inst_grp.scale(0.638).move_to(LEFT * 3.5 + DOWN * 0.3)
        self.add(inst_grp)

        title = Text(
            "MSan: Проверка памяти при чтении", font_size=38, color=BLUE_B, font="Inter"
        )
        title.to_edge(UP, buff=0.3)
        self.add(title)

        legend = VGroup(
            VGroup(
                Rectangle(
                    width=0.3, height=0.3, color=GREEN, fill_opacity=0.8, stroke_width=2
                ),
                Text(
                    "0 = инициализировано",
                    font_size=16,
                    color=GREEN,
                    weight=BOLD,
                    font="Inter",
                ),
            ).arrange(RIGHT, buff=0.15),
            VGroup(
                Rectangle(
                    width=0.3, height=0.3, color=RED, fill_opacity=0.8, stroke_width=2
                ),
                Text(
                    "1 = не инициализировано",
                    font_size=16,
                    color=RED,
                    weight=BOLD,
                    font="Inter",
                ),
            ).arrange(RIGHT, buff=0.15),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        legend.to_corner(DR, buff=0.5)
        self.add(legend)

        heap_box = RoundedRectangle(
            corner_radius=0.1,
            width=2.8,
            height=1.5,
            color=BLUE,
            fill_opacity=0.08,
            stroke_width=2.5,
        )
        heap_label = Text(
            "Основная память arr[5]",
            font_size=16,
            color=BLUE,
            weight=BOLD,
            font="Inter",
        )
        heap_label.next_to(heap_box, UP, buff=0.15)

        shadow_box = RoundedRectangle(
            corner_radius=0.1,
            width=2.8,
            height=1.5,
            color=GREY,
            fill_opacity=0.08,
            stroke_width=2.5,
        )
        shadow_label = Text(
            "Теневая память (Shadow)",
            font_size=16,
            color=GREY,
            weight=BOLD,
            font="Inter",
        )
        shadow_label.next_to(shadow_box, UP, buff=0.15)

        mem_blocks = VGroup(heap_box, shadow_box)
        mem_blocks.arrange(DOWN, buff=0.6)
        mem_blocks.move_to(RIGHT * 3.3 + UP * 0.2)

        heap_label.next_to(heap_box, UP, buff=0.15)
        shadow_label.next_to(shadow_box, UP, buff=0.15)

        self.add(heap_box, heap_label, shadow_box, shadow_label)

        heap_cells = VGroup()
        shadow_cells = VGroup()

        for i in range(5):
            h_cell = RoundedRectangle(
                corner_radius=0.04,
                width=0.48,
                height=0.55,
                color=BLUE,
                fill_opacity=0.15,
                stroke_width=2.5,
            )
            heap_cells.add(h_cell)

            s_cell = RoundedRectangle(
                corner_radius=0.04,
                width=0.48,
                height=0.55,
                color=GREY,
                fill_opacity=0.15,
                stroke_width=2.5,
            )
            shadow_cells.add(s_cell)

        heap_cells.arrange(RIGHT, buff=0.08)
        heap_cells.move_to(heap_box.get_center())

        shadow_cells.arrange(RIGHT, buff=0.08)
        shadow_cells.move_to(shadow_box.get_center())

        heap_indices = VGroup()
        for i in range(5):
            idx = Text(str(i), font_size=14, color=BLUE_B, weight=BOLD, font="Inter")
            idx.next_to(heap_cells[i], UP, buff=0.06)
            heap_indices.add(idx)

        self.add(heap_cells, shadow_cells, *heap_indices)

        heap_vals = [
            Text("10", font_size=14, color=GREEN, weight=BOLD, font="Inter").move_to(
                heap_cells[0]
            ),
            Text("20", font_size=14, color=GREEN, weight=BOLD, font="Inter").move_to(
                heap_cells[1]
            ),
            Text("?", font_size=14, color=GREY_A, font="Inter").move_to(heap_cells[2]),
            Text("40", font_size=14, color=GREEN, weight=BOLD, font="Inter").move_to(
                heap_cells[3]
            ),
            Text("50", font_size=14, color=GREEN, weight=BOLD, font="Inter").move_to(
                heap_cells[4]
            ),
        ]

        shadow_vals = [
            Text("0", font_size=15, color=GREEN, weight=BOLD, font="Inter").move_to(
                shadow_cells[0]
            ),
            Text("0", font_size=15, color=GREEN, weight=BOLD, font="Inter").move_to(
                shadow_cells[1]
            ),
            Text("1", font_size=15, color=RED, weight=BOLD, font="Inter").move_to(
                shadow_cells[2]
            ),
            Text("0", font_size=15, color=GREEN, weight=BOLD, font="Inter").move_to(
                shadow_cells[3]
            ),
            Text("0", font_size=15, color=GREEN, weight=BOLD, font="Inter").move_to(
                shadow_cells[4]
            ),
        ]

        for h, s in zip(heap_vals, shadow_vals):
            self.add(h, s)

        line_height = inst_code.height / 22

        phase4 = Text(
            "Этап 3: Проверка arr[0] - успех",
            font_size=18,
            color=GREEN,
            weight=BOLD,
            font="Inter",
        )
        phase4.next_to(title, DOWN, buff=0.25)

        highlight4 = RoundedRectangle(
            corner_radius=0.05,
            width=inst_code.width * 1,
            height=line_height * 2.4,
            color=GREEN,
            fill_color=GREEN,
            fill_opacity=0.25,
            stroke_width=0,
        )
        highlight4.align_to(inst_code, LEFT).shift(RIGHT * 0.12)
        highlight4.move_to(
            inst_code.get_top() + DOWN * (line_height * 13.05), aligned_edge=UP
        )

        self.play(Write(phase4), FadeIn(highlight4), run_time=0.8)

        check_frame_0 = SurroundingRectangle(
            shadow_cells[0], color=GREEN, buff=0.1, stroke_width=4
        )
        self.play(Create(check_frame_0))
        self.play(Indicate(shadow_vals[0], color=GREEN, scale_factor=1.4))

        success_box = RoundedRectangle(
            corner_radius=0.1,
            width=3.2,
            height=0.8,
            color=GREEN,
            fill_color=BLACK,
            fill_opacity=0.95,
            stroke_width=4,
        )
        success_box.next_to(shadow_cells[0], DOWN, buff=0.5)

        success_text = VGroup(
            Text("✓ OK!", font_size=16, color=GREEN, weight=BOLD, font="Inter"),
            Text("Память инициализирована", font_size=14, color=WHITE, font="Inter"),
        ).arrange(DOWN, buff=0.08)
        success_text.move_to(success_box)

        self.play(FadeIn(success_box), Write(success_text), run_time=0.8)
        self.wait(1.5)

        self.play(
            FadeOut(success_box),
            FadeOut(success_text),
            FadeOut(check_frame_0),
            FadeOut(highlight4),
            FadeOut(phase4),
            run_time=0.5,
        )
        self.wait(0.3)

        phase5 = Text(
            "Этап 4: Проверка arr[2] - UMR ОШИБКА",
            font_size=18,
            color=RED,
            weight=BOLD,
            font="Inter",
        )
        phase5.next_to(title, DOWN, buff=0.25)

        highlight5 = RoundedRectangle(
            corner_radius=0.05,
            width=inst_code.width * 1,
            height=line_height * 2.5,
            color=RED,
            fill_color=ORANGE,
            fill_opacity=0.25,
            stroke_width=0,
        )
        highlight5.align_to(inst_code, LEFT).shift(RIGHT * 0.12)
        highlight5.move_to(
            inst_code.get_top() + DOWN * (line_height * 16.15), aligned_edge=UP
        )

        self.play(Write(phase5), FadeIn(highlight5), run_time=0.8)

        self.play(
            Indicate(shadow_cells[2], color=RED, scale_factor=1.5),
            Indicate(shadow_vals[2], color=RED, scale_factor=1.5),
            run_time=1,
        )
        self.wait(0.3)

        error_box = RoundedRectangle(
            corner_radius=0.12,
            width=6.8,
            height=2.0,
            color=RED,
            fill_color=BLACK,
            fill_opacity=0.95,
            stroke_width=5,
        )
        error_box.to_edge(DOWN, buff=0.4)

        error_header = Text(
            "⚠ MSan ERROR DETECTED", font_size=18, color=RED, weight=BOLD, font="Inter"
        )

        error_details = VGroup(
            Text(
                "WARNING: MemorySanitizer:",
                font_size=15,
                color=RED,
                weight=BOLD,
                font="Inter",
            ),
            Text(
                "use-of-uninitialized-value",
                font_size=15,
                color=RED,
                weight=BOLD,
                font="Inter",
            ),
            Text("at main() arr[2]", font_size=14, color=YELLOW, font="Inter"),
            Text("SUMMARY: UMR detected", font_size=14, color=WHITE, font="Inter"),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)

        error_content = VGroup(error_header, error_details).arrange(DOWN, buff=0.25)
        error_content.move_to(error_box.get_center())

        self.play(FadeIn(error_box, scale=0.95), Write(error_content), run_time=1.5)

        self.play(Wiggle(error_box, scale_value=1.03))
        self.wait(2.5)

        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)
