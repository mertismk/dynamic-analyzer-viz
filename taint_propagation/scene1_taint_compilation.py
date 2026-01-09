from manim import *
from pygments.styles.monokai import MonokaiStyle
from pygments.token import Name, Keyword


class TaintStyle(MonokaiStyle):
    styles = MonokaiStyle.styles.copy()
    styles[Name.Function] = "#a6e22e"
    styles[Name.Builtin] = "#66d9ef"
    styles[Keyword] = "#f92672"


def code_box(code_obj: Mobject) -> Mobject:
    return getattr(code_obj, "background_mobject", code_obj)


def make_code_highlight(
    code_obj: Mobject,
    *,
    total_lines: int,
    first: int,
    last: int,
    width_scale: float,
    height_scale: float,
    corner_radius: float,
    stroke_width: float,
    stroke_color,
    fill_opacity: float,
    fill_color=None,
    x_pad_align: float = 0.20,   # сдвиг вправо после align_to(LEFT)
    top_pad_lines: float = 0.8,  # то самое "0.8" в твоей формуле
) -> RoundedRectangle:
    """
    Универсальная рамка/подсветка по строкам для Code.

    Ты задаёшь только:
      - total_lines (кол-во строк)
      - first/last (диапазон строк)

    Остальные параметры (цвета/толщина/скругление/масштабы ширины-высоты)
    передаются как константы, чтобы их не дублировать.

    Логика позиционирования и расчёта высоты сохранена как в твоей версии.
    """
    frame = code_box(code_obj)
    line_height = frame.height / (total_lines + top_pad_lines)

    lines_span = last - first + 1
    rect = RoundedRectangle(
        corner_radius=corner_radius,
        width=frame.width * width_scale,
        height=line_height * lines_span * height_scale,
        color=stroke_color,
        stroke_width=stroke_width,
        fill_opacity=fill_opacity,
        fill_color=(fill_color if fill_color is not None else stroke_color),
    )

    rect.align_to(frame, LEFT).shift(RIGHT * x_pad_align)

    code_top = frame.get_top()
    first_line_center = code_top + DOWN * (line_height * top_pad_lines)
    target_center = first_line_center + DOWN * line_height * (first - 1)
    span_center = target_center + DOWN * line_height * (lines_span - 1) * 0.5
    rect.move_to([rect.get_center()[0], span_center[1], 0])

    return rect


class TaintCompilationFixed(Scene):
    def construct(self):
        LEFT_PANEL_POS = LEFT * 4.5 + DOWN * 0.2
        RIGHT_PANEL_POS = RIGHT * 4.25 + DOWN * 0.2
        CENTER_PANEL_POS = ORIGIN + UP * 0.15

        C_SOURCE = PURPLE
        C_PROP = ORANGE
        C_CHECK = TEAL
        C_SINK = GREEN

        title = Text("Taint Propagation: Процесс компиляции", font_size=36)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title))
        self.wait(0.4)

        # Исходный код (слева)
        source_str = """int main() {
    char* user_input = getenv("CMD");
    char cmd[256];
    sprintf(cmd, "ls %s", user_input);
    system(cmd);
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
        source_label.next_to(code_box(source_code), UP, buff=0.12)
        source_grp = VGroup(source_code, source_label).scale(0.55)
        source_grp.move_to(LEFT_PANEL_POS)

        # Компилятор
        compiler = RoundedRectangle(
            corner_radius=0.12,
            width=2.4,
            height=1.6,
            color=BLUE,
            fill_opacity=0.15,
            stroke_width=3,
        )
        compiler.move_to(DOWN * 3.0)
        compiler_text = VGroup(
            Text("Clang", font_size=20, weight=BOLD, color=BLUE),
            Text("-fsanitize=dataflow", font_size=13, color=YELLOW),
        ).arrange(DOWN, buff=0.06)
        compiler_text.move_to(compiler)

        arrow_left = Arrow(
            code_box(source_code).get_bottom(),
            compiler.get_left() + UP * 0.3,
            color=YELLOW,
            stroke_width=4,
            buff=0.12,
        )

        self.play(Create(source_code), Write(source_label))
        self.wait(0.4)
        self.play(Create(compiler), Write(compiler_text))
        self.wait(0.2)
        self.play(Create(arrow_left))
        self.wait(0.4)

        # Базовый код справа
        base_str = """int main() {
    char* user_input = getenv("CMD");
    char cmd[256];
    sprintf(cmd, "ls %s", user_input);
    system(cmd);
    return 0;
}"""

        base_code = Code(
            code_string=base_str,
            language="c++",
            tab_width=4,
            formatter_style=TaintStyle,
            background="rectangle",
            add_line_numbers=False,
            background_config={
                "stroke_width": 2,
                "stroke_color": GREY_B,
                "fill_color": BLACK,
                "fill_opacity": 0.9,
            },
        ).scale(0.55)
        base_code.move_to(RIGHT_PANEL_POS)

        inst_label = Text("Инструментированный код", font_size=32, color=WHITE).scale(0.55)
        inst_label.next_to(code_box(base_code), UP, buff=0.12)
        inst_label.add_updater(lambda m: m.next_to(code_box(base_code), UP, buff=0.12))

        arrow_right = Arrow(
            compiler.get_right() + UP * 0.3,
            code_box(base_code).get_bottom(),
            color=YELLOW,
            stroke_width=4,
            buff=0.12,
        )

        def arrow_right_updater(m: Arrow):
            m.put_start_and_end_on(
                compiler.get_right() + UP * 0.3,
                code_box(base_code).get_bottom(),
            )

        arrow_right.add_updater(arrow_right_updater)

        self.play(Create(base_code), Write(inst_label))
        self.wait(0.2)
        self.play(Create(arrow_right))
        self.wait(0.5)

        # Добавляемые блоки
        added_1_str = """    dfsan_label TAINT = 1;
    dfsan_set_label(TAINT, user_input,
                    strlen(user_input) + 1);"""

        added_1 = Code(
            code_string=added_1_str,
            language="c++",
            tab_width=4,
            formatter_style=TaintStyle,
            background="rectangle",
            add_line_numbers=False,
            background_config={
                "stroke_width": 2,
                "stroke_color": GREY_B,
                "fill_color": BLACK,
                "fill_opacity": 0.6,
                "corner_radius": 0.1,
            },
        ).scale(0.55)

        added_2_str = """    if (dfsan_read_label(cmd,
                         strlen(cmd) + 1) != 0)
        report_vulnerability();
"""

        added_2 = Code(
            code_string=added_2_str,
            language="c++",
            tab_width=4,
            formatter_style=TaintStyle,
            background="rectangle",
            add_line_numbers=False,
            background_config={
                "stroke_width": 2,
                "stroke_color": GREY_B,
                "fill_color": BLACK,
                "fill_opacity": 0.6,
                "corner_radius": 0.1,
            },
        ).scale(0.55)

        added_1.next_to(code_box(base_code), RIGHT, buff=0.8).shift(UP * 0.6)
        added_2.next_to(code_box(base_code), RIGHT, buff=0.8).shift(DOWN * 0.3)

        explanation = Text(
            "Компилятор добавляет вызовы DFSan API:",
            font_size=16,
            color=GREY,
        )
        explanation.next_to(title, DOWN, buff=0.25)

        self.play(Write(explanation))
        self.wait(0.3)
        self.play(FadeIn(added_1, shift=LEFT * 0.3))
        self.wait(0.3)
        self.play(FadeIn(added_2, shift=LEFT * 0.3))
        self.wait(0.5)

        # Финальный инструментированный код
        inst_str = """int main() {
    char* user_input = getenv("CMD");
    dfsan_label TAINT = 1;
    dfsan_set_label(TAINT, user_input,
                    strlen(user_input) + 1);

    char cmd[256];
    sprintf(cmd, "ls %s", user_input);

    if (dfsan_read_label(cmd,
                         strlen(cmd) + 1) != 0)
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
                "stroke_color": GREY_B,
                "fill_color": BLACK,
                "fill_opacity": 0.9,
            },
        ).scale(0.55)

        inst_code.move_to(base_code)
        inst_code.shift(code_box(base_code).get_center() - code_box(inst_code).get_center())

        # ВАЖНО: добавляем inst_code заранее, но делаем его невидимым
        self.add(inst_code)
        inst_code.set_opacity(0)

        # 1) Замена base_code -> inst_code (лейбл/стрелка ПОКА остаются привязаны к base_code)
        self.play(
            ReplacementTransform(base_code, inst_code),
            inst_code.animate.set_opacity(1),
            FadeOut(added_1),
            FadeOut(added_2),
            run_time=1.0,
        )

        # Плавно "пересадить" лейбл и стрелку на inst_code (без телепорта)
        inst_label.clear_updaters()
        arrow_right.clear_updaters()

        target_label_pos = inst_label.copy().next_to(code_box(inst_code), UP, buff=0.12).get_center()

        target_arrow = Arrow(
            compiler.get_right() + UP * 0.3,
            code_box(inst_code).get_bottom(),
            color=YELLOW,
            stroke_width=4,
            buff=0.12,
        )

        self.play(
            inst_label.animate.move_to(target_label_pos),
            Transform(arrow_right, target_arrow),
            run_time=0.35,
        )

        inst_label.add_updater(lambda m: m.next_to(code_box(inst_code), UP, buff=0.12))

        def arrow_right_updater2(m: Arrow):
            m.put_start_and_end_on(
                compiler.get_right() + UP * 0.3,
                code_box(inst_code).get_bottom(),
            )

        arrow_right.add_updater(arrow_right_updater2)

        # ===== УПРОЩЁННЫЕ РАМКИ (нужно только: total_lines, first, last) =====
        TOTAL_LINES_INST = len(inst_str.splitlines())

        highlight_box_1 = make_code_highlight(
            inst_code,
            total_lines=TOTAL_LINES_INST,
            first=3,
            last=5,
            width_scale=0.74,
            height_scale=1.0,
            corner_radius=0.08,
            stroke_width=3,
            stroke_color=GREY,
            fill_opacity=0.0,
            x_pad_align=0.20,
            top_pad_lines=0.8,
        )

        highlight_box_2 = make_code_highlight(
            inst_code,
            total_lines=TOTAL_LINES_INST,
            first=10,
            last=12,
            width_scale=0.74,
            height_scale=1.0,
            corner_radius=0.08,
            stroke_width=3,
            stroke_color=GREY,
            fill_opacity=0.0,
            x_pad_align=0.20,
            top_pad_lines=0.8,
        )
        # ===================================================================

        self.play(Create(highlight_box_1), Create(highlight_box_2), run_time=0.6)
        self.wait(1.0)
        self.play(FadeOut(highlight_box_1), FadeOut(highlight_box_2), run_time=0.4)
        self.wait(0.6)

        # 3) Убираем окружение, но НЕ inst_code и НЕ inst_label
        to_remove = [source_grp, arrow_left, arrow_right, compiler, compiler_text, explanation]
        self.play(*[FadeOut(mob) for mob in to_remove], run_time=0.45)
        self.wait(0.05)

        # 4) Плавно перемещаем код + лейбл (лейбл продолжает следовать апдейтером)
        CENTER_TARGET = CENTER_PANEL_POS + LEFT * 0.12
        self.play(inst_code.animate.move_to(CENTER_TARGET), run_time=0.8)

        # фиксируем лейбл (чтобы дальше не дрожал от пересчётов)
        inst_label.clear_updaters()

        # 5) Создаем "чистый" final_inst_code прямо поверх inst_code и бесшовно заменяем
        final_inst_code = Code(
            code_string=inst_str,
            language="c++",
            tab_width=4,
            formatter_style=TaintStyle,
            background="rectangle",
            add_line_numbers=False,
            background_config={
                "stroke_width": 2,
                "stroke_color": GREY_B,
                "fill_color": BLACK,
                "fill_opacity": 0.9,
            },
        ).scale(0.55)

        final_inst_code.move_to(inst_code)
        final_inst_code.shift(code_box(inst_code).get_center() - code_box(final_inst_code).get_center())

        final_inst_label = Text("Инструментированный код", font_size=32, color=WHITE).scale(0.55)
        final_inst_label.move_to(inst_label)

        self.play(
            ReplacementTransform(inst_code, final_inst_code),
            ReplacementTransform(inst_label, final_inst_label),
            run_time=0.45,
        )
        self.wait(0.5)

        # ЛЕГЕНДА
        legend_box = RoundedRectangle(
            corner_radius=0.12,
            width=10.2,
            height=0.95,
            color=YELLOW,
            fill_color=BLACK,
            fill_opacity=0.25,
            stroke_width=2,
        )

        source_item = VGroup(Dot(color=C_SOURCE), Text("SOURCE: dfsan_set_label", font_size=16, color=C_SOURCE)).arrange(
            RIGHT, buff=0.18
        )
        prop_item = VGroup(Dot(color=C_PROP), Text("PROPAGATION: операции/вызовы", font_size=16, color=C_PROP)).arrange(
            RIGHT, buff=0.18
        )
        check_item = VGroup(Dot(color=C_CHECK), Text("CHECK: dfsan_read_label", font_size=16, color=C_CHECK)).arrange(
            RIGHT, buff=0.18
        )
        sink_item = VGroup(Dot(color=C_SINK), Text("SINK: system(cmd)", font_size=16, color=C_SINK)).arrange(
            RIGHT, buff=0.18
        )

        legend_items = VGroup(
            source_item,
            prop_item,
            check_item,
            sink_item,
        ).arrange_in_grid(rows=2, cols=2, buff=(1.2, 0.25), aligned_edge=LEFT)

        legend = VGroup(legend_box, legend_items)
        legend_items.move_to(legend_box)
        legend.scale(0.85)
        legend.next_to(code_box(final_inst_code), DOWN, buff=0.25)

        self.play(FadeIn(legend), run_time=0.5)

        # ===== УПРОЩЁННЫЕ ПОДСВЕТКИ (нужно только: total_lines, first, last) =====
        TOTAL_LINES_FINAL = len(inst_str.splitlines())

        source_highlight = make_code_highlight(
            final_inst_code,
            total_lines=TOTAL_LINES_FINAL,
            first=3,
            last=5,
            width_scale=0.93,
            height_scale=1.05,
            corner_radius=0.04,
            stroke_width=3,
            stroke_color=C_SOURCE,
            fill_opacity=0.25,
            fill_color=C_SOURCE,
            x_pad_align=0.20,
            top_pad_lines=0.8,
        )

        prop_highlight = make_code_highlight(
            final_inst_code,
            total_lines=TOTAL_LINES_FINAL,
            first=7,
            last=8,
            width_scale=0.93,
            height_scale=1.05,
            corner_radius=0.04,
            stroke_width=3,
            stroke_color=C_PROP,
            fill_opacity=0.25,
            fill_color=C_PROP,
            x_pad_align=0.20,
            top_pad_lines=0.8,
        )

        check_highlight = make_code_highlight(
            final_inst_code,
            total_lines=TOTAL_LINES_FINAL,
            first=10,
            last=12,
            width_scale=0.93,
            height_scale=1.05,
            corner_radius=0.04,
            stroke_width=3,
            stroke_color=C_CHECK,
            fill_opacity=0.25,
            fill_color=C_CHECK,
            x_pad_align=0.20,
            top_pad_lines=0.8,
        )

        sink_highlight = make_code_highlight(
            final_inst_code,
            total_lines=TOTAL_LINES_FINAL,
            first=14,
            last=14,
            width_scale=0.93,
            height_scale=1.05,
            corner_radius=0.04,
            stroke_width=3,
            stroke_color=C_SINK,
            fill_opacity=0.25,
            fill_color=C_SINK,
            x_pad_align=0.20,
            top_pad_lines=0.8,
        )
        # =========================================================================

        self.play(
            Create(source_highlight),
            Create(prop_highlight),
            Create(check_highlight),
            Create(sink_highlight),
            run_time=0.8
        )
        self.wait(0.5)

        init_desc = VGroup(
            Text("dfsan_set_label()", font_size=17, color=C_SOURCE, weight=BOLD),
            Text("SOURCE: помечает байты\nuser_input как tainted", font_size=13, color=WHITE),
        ).arrange(DOWN, buff=0.12)
        init_desc.next_to(source_highlight, LEFT, buff=0.5)
        self.play(FadeIn(init_desc, shift=RIGHT * 0.15))
        self.wait(1.4)

        prop_desc = VGroup(
            Text("sprintf()", font_size=17, color=C_PROP, weight=BOLD),
            Text("PROPAGATION: метка может\nперейти в cmd", font_size=13, color=WHITE),
        ).arrange(DOWN, buff=0.12)
        prop_desc.next_to(prop_highlight, RIGHT, buff=0.5)
        self.play(FadeIn(prop_desc, shift=LEFT * 0.15))
        self.wait(1.4)

        check_desc = VGroup(
            Text("dfsan_read_label()", font_size=17, color=C_CHECK, weight=BOLD),
            Text("CHECK: проверка метки cmd\nперед system()", font_size=13, color=WHITE),
        ).arrange(DOWN, buff=0.12)
        check_desc.next_to(check_highlight, LEFT, buff=0.5)
        self.play(FadeIn(check_desc, shift=RIGHT * 0.15))
        self.wait(1.4)

        sink_desc = VGroup(
            Text("system()", font_size=17, color=C_SINK, weight=BOLD),
            Text("SINK: использование данных\nв опасном вызове", font_size=13, color=WHITE),
        ).arrange(DOWN, buff=0.12)
        sink_desc.next_to(sink_highlight, RIGHT, buff=0.5)
        self.play(FadeIn(sink_desc, shift=LEFT * 0.15))
        self.wait(1.2)

        self.play(
            FadeOut(source_highlight),
            FadeOut(prop_highlight),
            FadeOut(check_highlight),
            FadeOut(sink_highlight),
            FadeOut(init_desc),
            FadeOut(prop_desc),
            FadeOut(check_desc),
            FadeOut(sink_desc),
            run_time=0.5
        )

        self.play(FadeOut(legend), run_time=0.35)
        self.play(FadeOut(final_inst_label), run_time=0.2)
        self.play(*[FadeOut(m) for m in self.mobjects])
