from manim import *


class MSanErrorDetection(Scene):
    def construct(self):
        # Заголовок
        title = Text("MSan: Обнаружение ошибки (UMR)", font_size=36, color=RED)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title))

        # Подпись текущей фазы
        phase_pos = title.get_bottom() + DOWN * 0.4
        phase_label = Text(" ", font_size=22, color=YELLOW)
        phase_label.move_to(phase_pos)
        self.add(phase_label)

        # Код с ошибкой слева
        code_lines = VGroup(
            Text("int main() {", font="Monospace", font_size=18),
            Text("int* p = new int;", font="Monospace", font_size=18),
            Text("// Забыли *p=10;", font="Monospace", font_size=18, color=GREY),
            Text("if (*p > 5) {", font="Monospace", font_size=18),
            Text("// ...", font="Monospace", font_size=18),
            Text("}", font="Monospace", font_size=18),
            Text("delete p;", font="Monospace", font_size=18),
            Text("}", font="Monospace", font_size=18),
        )
        code_lines.arrange(DOWN, aligned_edge=LEFT, buff=0.15)

        # Отступы
        indent = 0.3
        code_lines[1].shift(RIGHT * indent)
        code_lines[2].shift(RIGHT * indent)
        code_lines[3].shift(RIGHT * indent)
        code_lines[4].shift(RIGHT * indent * 2)
        code_lines[5].shift(RIGHT * indent)
        code_lines[6].shift(RIGHT * indent)

        code_box = SurroundingRectangle(code_lines, color=WHITE, buff=0.2)
        code_label = Text("Код с ошибкой", font_size=18).next_to(code_box, UP)
        code_grp = VGroup(code_box, code_lines, code_label)

        # Куча по центру
        heap_box = Rectangle(width=2.2, height=3.5, color=BLUE, fill_opacity=0.05)
        heap_label = Text("Куча", font_size=18, color=BLUE).next_to(heap_box, UP)
        heap_grp = VGroup(heap_box, heap_label)

        # Shadow-область справа
        shadow_box = Rectangle(width=2.2, height=3.5, color=GREY, fill_opacity=0.05)
        shadow_label = Text("Shadow", font_size=18, color=GREY).next_to(shadow_box, UP)
        shadow_grp = VGroup(shadow_box, shadow_label)

        # Расставляем объекты по сцене
        y_offset = -0.5
        code_grp.move_to([-4.5, y_offset, 0])
        heap_grp.move_to([0, y_offset, 0])
        shadow_grp.move_to([4.5, y_offset, 0])

        self.play(Create(code_grp), Create(heap_grp), Create(shadow_grp))

        # Ячейки внутри блоков
        heap_cell = Rectangle(width=1.8, height=0.7, color=BLUE)
        heap_cell.move_to(heap_box.get_center())

        shadow_cell = Rectangle(width=1.8, height=0.7, color=GREY)
        shadow_cell.move_to(shadow_box.get_center())

        # Хайлайтер для строки кода
        highlighter = SurroundingRectangle(
            code_lines[0], color=YELLOW, fill_opacity=0.2, stroke_width=0
        )
        highlighter.set_opacity(0)
        self.add(highlighter)

        def highlight(idx):
            target = SurroundingRectangle(
                code_lines[idx], color=YELLOW, fill_opacity=0.2, stroke_width=0
            )
            target.stretch_to_fit_width(code_box.width - 0.1)
            target.move_to(code_lines[idx])
            target.align_to(code_box, LEFT).shift(RIGHT * 0.05)
            return Transform(highlighter, target)

        # Анимация по шагам

        # Вход
        self.play(highlight(0))
        self.wait(0.5)

        # new int
        new_label1 = Text("Выделение памяти (Poisoned)", font_size=22, color=YELLOW)
        new_label1.move_to(phase_pos)

        shadow_val = Text("0xFF", font_size=22, color=RED, weight=BOLD).move_to(
            shadow_cell
        )

        self.play(highlight(1), ReplacementTransform(phase_label, new_label1))
        self.play(Create(heap_cell), Create(shadow_cell), FadeIn(shadow_val))
        self.wait(1)

        # Пропуск (комментарий)
        self.play(highlight(2))
        self.wait(0.5)

        # Чтение (*p > 5) -> ошибка
        new_label2 = Text(
            "Чтение (*p) -> проверка Shadow...", font_size=22, color=RED
        )
        new_label2.move_to(phase_pos)

        self.play(highlight(3), ReplacementTransform(new_label1, new_label2))
        self.wait(0.5)

        # Зум на Shadow
        self.play(Indicate(shadow_cell, color=RED, scale_factor=1.2))
        self.play(Indicate(shadow_val, color=RED, scale_factor=1.2))

        # 4. КОНСОЛЬ (ОТЧЕТ)
        console_box = RoundedRectangle(
            corner_radius=0.1,
            width=7,
            height=3.5,
            color=GREY,
            fill_color=BLACK,
            fill_opacity=0.95,
        )
        console_box.move_to(ORIGIN)

        console_header = Text("Терминал", font_size=16, color=WHITE).next_to(
            console_box, UP, buff=0.1
        )

        error_lines = VGroup(
            Text(
                "==12345==WARNING: MemorySanitizer: use-of-uninitialized-value",
                font="Monospace",
                font_size=14,
                color=RED,
            ),
            Text(
                "    #0 0x401234 in main example.cpp:4",
                font="Monospace",
                font_size=14,
                color=WHITE,
            ),
            Text(
                "    #1 0x7f... in __libc_start_main",
                font="Monospace",
                font_size=14,
                color=WHITE,
            ),
            Text(
                "SUMMARY: MemorySanitizer: use-of-uninitialized-value",
                font="Monospace",
                font_size=14,
                color=WHITE,
            ),
            Text("Exiting", font="Monospace", font_size=14, color=WHITE),
        )
        error_lines.arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        error_lines.move_to(console_box.get_center())

        self.play(
            FadeIn(console_box), Write(console_header), Write(error_lines), run_time=1.5
        )

        self.play(Wiggle(console_box))
        self.wait(3)

        self.play(*[FadeOut(mob) for mob in self.mobjects])
