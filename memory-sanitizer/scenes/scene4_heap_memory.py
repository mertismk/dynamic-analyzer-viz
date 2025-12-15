from manim import *


class HeapShadowAnimation(Scene):
    def construct(self):
        title = Text("MSan: Работа с динамической памятью (Heap)", font_size=36)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title))

        phase_pos = title.get_bottom() + DOWN * 0.4
        phase_label = Text(" ", font_size=22, color=YELLOW)
        phase_label.move_to(phase_pos)
        self.add(phase_label)

        code_lines = VGroup(
            Text("void heap_test() {", font="Monospace", font_size=18),
            Text("int* p = new int;", font="Monospace", font_size=18),
            Text("*p = 10;", font="Monospace", font_size=18),
            Text("delete p;", font="Monospace", font_size=18),
            Text("}", font="Monospace", font_size=18),
        )

        code_lines.arrange(DOWN, aligned_edge=LEFT, buff=0.15)

        indent = 0.3
        code_lines[1].shift(RIGHT * indent)
        code_lines[2].shift(RIGHT * indent)
        code_lines[3].shift(RIGHT * indent)

        code_box = SurroundingRectangle(code_lines, color=WHITE, buff=0.2)
        code_label = Text("Код", font_size=18).next_to(code_box, UP)
        code_grp = VGroup(code_box, code_lines, code_label)

        heap_box = Rectangle(width=2.2, height=3.5, color=BLUE, fill_opacity=0.05)
        heap_label = Text("Куча (Heap)", font_size=18, color=BLUE).next_to(heap_box, UP)
        heap_grp = VGroup(heap_box, heap_label)

        shadow_box = Rectangle(width=2.2, height=3.5, color=GREY, fill_opacity=0.05)
        shadow_label = Text("Shadow", font_size=18, color=GREY).next_to(shadow_box, UP)
        shadow_grp = VGroup(shadow_box, shadow_label)

        y_offset = -0.5
        heap_grp.move_to([0, y_offset, 0])
        code_grp.move_to([-4.5, y_offset, 0])
        shadow_grp.move_to([4.5, y_offset, 0])

        self.play(Create(code_grp), Create(heap_grp), Create(shadow_grp))

        # небольшая легенда по значениям shadow
        legend = VGroup(
            Text("0x00 = OK", font_size=16, color=GREEN),
            Text("0xFF = Poison", font_size=16, color=RED),
        ).arrange(RIGHT, buff=1)
        legend.to_edge(DOWN, buff=0.3)
        self.play(Write(legend))

        # подсветка текущей строки кода
        highlighter = SurroundingRectangle(
            code_lines[0], color=YELLOW, fill_opacity=0.2, stroke_width=0
        )
        highlighter.set_opacity(0)
        self.add(highlighter)

        def highlight_line(line_idx):
            # подгоняем прямоугольник подсветки под рамку кода
            target = SurroundingRectangle(
                code_lines[line_idx], color=YELLOW, fill_opacity=0.2, stroke_width=0
            )
            target.stretch_to_fit_width(code_box.width - 0.1)
            target.move_to(code_lines[line_idx])
            target.align_to(code_box, LEFT).shift(RIGHT * 0.05)

            return Transform(highlighter, target)

        self.play(highlight_line(0))
        self.wait(0.5)

        new_label1 = Text(
            "1. new int; -> Выделение (Poisoned)", font_size=22, color=YELLOW
        )
        new_label1.move_to(phase_pos)

        heap_cell = Rectangle(width=1.8, height=0.7, color=BLUE)
        heap_cell.move_to(heap_box.get_center())

        shadow_cell = Rectangle(width=1.8, height=0.7, color=GREY)
        shadow_cell.move_to(shadow_box.get_center())

        shadow_val = Text("0xFF", font_size=22, color=RED, weight=BOLD).move_to(
            shadow_cell
        )

        self.play(highlight_line(1), ReplacementTransform(phase_label, new_label1))
        self.play(Create(heap_cell), Create(shadow_cell), FadeIn(shadow_val))
        self.wait(1)

        new_label2 = Text(
            "2. *p = 10; -> Инициализация (Clean)", font_size=22, color=YELLOW
        )
        new_label2.move_to(phase_pos)

        val_10 = Text("10", font_size=22, color=GREEN, weight=BOLD).move_to(heap_cell)
        shadow_clean = Text("0x00", font_size=22, color=GREEN, weight=BOLD).move_to(
            shadow_cell
        )

        self.play(highlight_line(2), ReplacementTransform(new_label1, new_label2))
        self.play(
            FadeIn(val_10),
            ReplacementTransform(shadow_val, shadow_clean),
            Indicate(shadow_cell, color=GREEN),
        )
        self.wait(1)

        new_label3 = Text(
            "3. delete p; -> Освобождение (Poisoned)", font_size=22, color=YELLOW
        )
        new_label3.move_to(phase_pos)

        shadow_poison = Text("0xFF", font_size=22, color=RED, weight=BOLD).move_to(
            shadow_cell
        )
        val_trash = Text("???", font_size=22, color=RED).move_to(heap_cell)

        self.play(highlight_line(3), ReplacementTransform(new_label2, new_label3))
        self.play(
            ReplacementTransform(val_10, val_trash),
            ReplacementTransform(shadow_clean, shadow_poison),
            Indicate(shadow_cell, color=RED),
        )
        self.wait(1)

        self.play(
            FadeOut(heap_cell),
            FadeOut(val_trash),
            FadeOut(shadow_cell),
            FadeOut(shadow_poison),
        )

        self.play(highlight_line(4))
        self.wait(2)

        self.play(*[FadeOut(mob) for mob in self.mobjects])
