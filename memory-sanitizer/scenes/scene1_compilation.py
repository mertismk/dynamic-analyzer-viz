from manim import *


class CompilationWithInstrumentation(Scene):
    def construct(self):
        title = Text("MemorySanitizer: Процесс компиляции", font_size=36)
        title.to_edge(UP, buff=0.2)
        self.play(Write(title))

        # Позиция для пояснений
        info_pos = title.get_bottom() + DOWN * 0.6
        current_info = Text(" ", font_size=24, color=YELLOW)
        current_info.move_to(info_pos)
        self.add(current_info)

        # Исходный код
        source_lines = VGroup(
            Text("int main() {", font="Monospace", font_size=18),
            Text("int* ptr = new int[10];", font="Monospace", font_size=18),
            Text("ptr[5] = 0;", font="Monospace", font_size=18),
            Text("if (ptr[0]) {", font="Monospace", font_size=18),
            Text("// ...", font="Monospace", font_size=18),
            Text("}", font="Monospace", font_size=18),
            Text("delete[] ptr;", font="Monospace", font_size=18),
            Text("return 0;", font="Monospace", font_size=18),
            Text("}", font="Monospace", font_size=18),
        )
        source_lines.arrange(DOWN, aligned_edge=LEFT, buff=0.15)

        indent = 0.3
        for i in [1, 2, 3, 5, 6, 7]:
            source_lines[i].shift(RIGHT * indent)
        source_lines[4].shift(RIGHT * indent * 2)

        source_box = SurroundingRectangle(source_lines, color=WHITE, buff=0.2)
        source_label = Text("Исходный код", font_size=18).next_to(source_box, UP)

        source_grp = VGroup(source_box, source_lines, source_label)
        source_grp.to_edge(LEFT, buff=0.5).shift(DOWN * 0.8)

        self.play(Create(source_box), Write(source_lines), Write(source_label))

        # Компилятор
        compiler = Rectangle(width=3, height=2.2, color=BLUE, fill_opacity=0.2)
        compiler.move_to(ORIGIN + DOWN * 2.8)

        compiler_text = VGroup(
            Text("Clang", font_size=24, weight=BOLD),
            Text("(Компилятор C++)", font_size=14, color=BLUE_A),
            Text("-fsanitize=memory", font_size=16, color=YELLOW),
        ).arrange(DOWN, buff=0.15)
        compiler_text.move_to(compiler)

        arrow_to_compiler = Arrow(
            source_box.get_bottom(),
            compiler.get_left(),
            buff=0.1,
            color=YELLOW,
            stroke_width=4,
        )

        # Показываем объяснение флага перед компилятором
        flag_explanation = Text(
            "Флаг: включить инструментацию памяти", font_size=20, color=YELLOW
        )
        flag_explanation.move_to(info_pos)

        self.play(Write(flag_explanation))
        self.wait(1.5)
        self.play(FadeOut(flag_explanation))

        self.play(GrowArrow(arrow_to_compiler), Create(compiler), Write(compiler_text))
        self.wait(1)

        # Инструментированный код
        inst_lines = VGroup(
            Text("int main() {", font="Monospace", font_size=18),
            Text("// Shadow memory setup", font="Monospace", font_size=16, color=GREY),
            Text("int* ptr = new int[10];", font="Monospace", font_size=18),
            Text("__msan_poison(ptr, 40);", font="Monospace", font_size=16, color=RED),
            Text("ptr[5] = 0;", font="Monospace", font_size=18),
            Text(
                "__msan_unpoison(&ptr[5], 4);",
                font="Monospace",
                font_size=16,
                color=GREEN,
            ),
            Text(
                "__msan_check(&ptr[0], 4);",
                font="Monospace",
                font_size=16,
                color=YELLOW,
            ),
            Text("if (ptr[0]) { }", font="Monospace", font_size=18),
            Text("delete[] ptr;", font="Monospace", font_size=18),
            Text("}", font="Monospace", font_size=18),
        )
        inst_lines.arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        for i in range(1, len(inst_lines)):
            inst_lines[i].shift(RIGHT * indent)

        inst_box = SurroundingRectangle(inst_lines, color=GREEN, buff=0.2)
        inst_label = Text("Инструментированный код", font_size=18, color=GREEN).next_to(
            inst_box, UP
        )

        inst_grp = VGroup(inst_box, inst_lines, inst_label)
        inst_grp.to_edge(RIGHT, buff=0.5).shift(DOWN * 0.8)

        arrow_from_compiler = Arrow(
            compiler.get_right(),
            inst_box.get_bottom(),
            buff=0.1,
            color=GREEN,
            stroke_width=4,
        )

        self.play(
            GrowArrow(arrow_from_compiler),
            Create(inst_box),
            Write(inst_lines),
            Write(inst_label),
        )
        self.wait(1)

        # Подсветка для синхронизации исходного и инструментированного кода
        hl_src = SurroundingRectangle(
            source_lines[0], color=YELLOW, fill_opacity=0.2, stroke_width=0
        ).set_opacity(0)
        hl_inst = SurroundingRectangle(
            inst_lines[0], color=YELLOW, fill_opacity=0.2, stroke_width=0
        ).set_opacity(0)
        self.add(hl_src, hl_inst)

        current_top_text = Text(" ", font_size=1)  # Заглушка

        def show_step(src_idx, inst_indices, text, color=WHITE):
            nonlocal current_top_text

            t_src = SurroundingRectangle(
                source_lines[src_idx], color=YELLOW, fill_opacity=0.2, stroke_width=0
            )
            t_src.stretch_to_fit_width(source_box.width).move_to(
                source_lines[src_idx]
            ).align_to(source_box, LEFT)

            grp = VGroup(*[inst_lines[i] for i in inst_indices])
            t_inst = SurroundingRectangle(
                grp, color=YELLOW, fill_opacity=0.2, stroke_width=0
            )
            t_inst.stretch_to_fit_width(inst_box.width).move_to(grp).align_to(
                inst_box, LEFT
            )

            new_text = Text(text, font_size=22, color=color).move_to(info_pos)

            self.play(
                Transform(hl_src, t_src),
                Transform(hl_inst, t_inst),
                FadeOut(current_top_text),
                FadeIn(new_text),
            )
            current_top_text = new_text

        # Poison при выделении памяти
        show_step(
            1,
            [2, 3],
            "new[] -> __msan_poison() — помечаем память как неинициализированную",
            RED,
        )
        self.wait(2)

        # Unpoison при записи
        show_step(
            2,
            [4, 5],
            "Запись -> __msan_unpoison() — помечаем байты как инициализированные",
            GREEN,
        )
        self.wait(2)

        # Check при чтении
        show_step(
            3,
            [6, 7],
            "Чтение -> __msan_check() — проверяем shadow перед использованием",
            YELLOW,
        )
        self.wait(2)

        final_text = Text(
            "MSan автоматически отслеживает инициализацию памяти",
            font_size=24,
            color=BLUE,
        )
        final_text.move_to(info_pos)
        self.play(
            FadeOut(current_top_text),
            FadeIn(final_text),
            FadeOut(hl_src),
            FadeOut(hl_inst),
        )
        self.wait(3)

        self.play(*[FadeOut(mob) for mob in self.mobjects])
