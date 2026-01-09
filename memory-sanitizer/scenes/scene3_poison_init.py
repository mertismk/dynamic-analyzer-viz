from manim import *
from pygments.styles.monokai import MonokaiStyle
from pygments.token import Name


class MSanStyle(MonokaiStyle):
    styles = MonokaiStyle.styles.copy()
    styles[Name.Function] = "#a6e22e"


class PoisonInitScene(Scene):
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
            "MSan: Выделение и инициализация памяти",
            font_size=38,
            color=BLUE_B,
            font="Inter",
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

        line_height = inst_code.height / 22

        phase2 = Text(
            "Этап 1: Выделение памяти",
            font_size=18,
            color=YELLOW,
            weight=BOLD,
            font="Inter",
        )
        phase2.next_to(title, DOWN, buff=0.25)

        highlight2 = RoundedRectangle(
            corner_radius=0.05,
            width=inst_code.width * 0.88,
            height=line_height * 1.4,
            color=RED,
            fill_color=RED,
            fill_opacity=0.25,
            stroke_width=0,
        )
        highlight2.align_to(inst_code, LEFT).shift(RIGHT * 0.12)
        highlight2.move_to(
            inst_code.get_top() + DOWN * (line_height * 1.45), aligned_edge=UP
        )

        self.play(Write(phase2), FadeIn(highlight2), run_time=0.8)

        self.play(
            Create(VGroup(heap_box, heap_label, shadow_box, shadow_label)), run_time=1
        )

        self.play(
            Create(heap_cells),
            Create(shadow_cells),
            *[FadeIn(idx) for idx in heap_indices],
            run_time=0.8
        )

        shadow_vals = VGroup()
        for i in range(5):
            val = Text("1", font_size=15, color=RED, weight=BOLD, font="Inter").move_to(
                shadow_cells[i]
            )
            shadow_vals.add(val)

        self.play(*[FadeIn(v, scale=1.3) for v in shadow_vals], run_time=0.8)
        self.play(FadeIn(legend, shift=UP * 0.2), run_time=0.8)
        self.wait(1.2)
        self.play(FadeOut(highlight2), FadeOut(phase2), run_time=0.5)

        phase3 = Text(
            "Этап 2: Инициализация 0, 1, 3, 4 (пропуск 2)",
            font_size=18,
            color=YELLOW,
            weight=BOLD,
            font="Inter",
        )
        phase3.next_to(title, DOWN, buff=0.25)

        highlight3 = RoundedRectangle(
            corner_radius=0.05,
            width=inst_code.width * 0.88,
            height=line_height * 8.4,
            color=GREEN,
            fill_color=GREEN,
            fill_opacity=0.25,
            stroke_width=0,
        )
        highlight3.align_to(inst_code, LEFT).shift(RIGHT * 0.12)
        highlight3.move_to(
            inst_code.get_top() + DOWN * (line_height * 3.85), aligned_edge=UP
        )

        self.play(Write(phase3), FadeIn(highlight3), run_time=0.8)

        heap_vals = []
        shadow_clean_vals = []

        init_indices = [0, 1, 3, 4]
        init_values = [10, 20, 40, 50]

        for idx, val in zip(init_indices, init_values):
            h_val = Text(
                str(val), font_size=14, color=GREEN, weight=BOLD, font="Inter"
            ).move_to(heap_cells[idx])
            s_val = Text(
                "0", font_size=15, color=GREEN, weight=BOLD, font="Inter"
            ).move_to(shadow_cells[idx])

            self.play(
                FadeIn(h_val, scale=1.2),
                ReplacementTransform(shadow_vals[idx], s_val),
                Flash(heap_cells[idx], color=GREEN, flash_radius=0.25),
                run_time=0.4,
            )
            heap_vals.append(h_val)
            shadow_clean_vals.append(s_val)

        h_val_2 = Text("?", font_size=14, color=GREY_A, font="Inter").move_to(
            heap_cells[2]
        )
        self.play(FadeIn(h_val_2), run_time=0.3)

        self.wait(1.5)
        self.play(FadeOut(highlight3), FadeOut(phase3), run_time=0.5)
        self.wait(0.3)
