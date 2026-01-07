from manim import *
from pygments.styles.monokai import MonokaiStyle
from pygments.token import Name, Keyword

# OFFICIAL DOCUMENTATION
# Clang Static Analyzer - Taint Analysis:
# https://clang.llvm.org/docs/analyzer/user-docs/TaintAnalysisConfiguration.html
#
# DataFlowSanitizer (DFSan) user doc:
# https://clang.llvm.org/docs/DataFlowSanitizer.html
# DFSan API (полный список интерфейса):
# https://clang.llvm.org/docs/DataFlowSanitizerDesign.html


class TaintStyle(MonokaiStyle):
    styles = MonokaiStyle.styles.copy()
    styles[Name.Function] = "#a6e22e"
    styles[Name.Builtin] = "#66d9ef"
    styles[Keyword] = "#f92672"


class TaintCompilation(Scene):
    def construct(self):
        # Контрастные цвета для легенды/подсветки
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
        source_label.next_to(source_code, UP, buff=0.12)
        source_grp = VGroup(source_code, source_label)
        source_grp.scale(0.55)
        source_grp.move_to(LEFT * 4.5 + DOWN * 0.2)

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

        # Стрелка слева
        arrow_left = Arrow(
            source_code.get_bottom(),
            compiler.get_left() + UP * 0.3,
            color=YELLOW,
            stroke_width=4,
            buff=0.12,
        )

        # Появление исходного кода и компилятора
        self.play(Create(source_code), Write(source_label))
        self.wait(0.4)
        self.play(Create(compiler), Write(compiler_text))
        self.wait(0.2)
        self.play(Create(arrow_left))
        self.wait(0.4)

        # ====== АНИМАЦИЯ ВДВИГАНИЯ СТРОК ======
        
        # Сначала показываем базовый код справа (без инструментации)
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
        )

        inst_label = Text("Инструментированный код", font_size=32, color=WHITE)
        inst_label.next_to(base_code, UP, buff=0.12)
        base_grp = VGroup(base_code, inst_label)
        base_grp.scale(0.55)
        base_grp.move_to(RIGHT * 4.5 + DOWN * 0.2)

        arrow_right = Arrow(
            compiler.get_right() + UP * 0.3,
            base_code.get_bottom(),
            color=YELLOW,
            stroke_width=4,
            buff=0.12,
        )

        self.play(Create(base_code), Write(inst_label))
        self.wait(0.2)
        self.play(Create(arrow_right))
        self.wait(0.5)

        # Создаем добавляемые строки как отдельные Code блоки
        added_1_str = """  dfsan_label TAINT = 1;
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
                "stroke_color": GREY,
                "fill_color": GREY,
                "fill_opacity": 0.2,
            },
        ).scale(0.55)

        added_2_str = """  if (dfsan_read_label(cmd, 
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
                "stroke_color": GREY,
                "fill_color": GREY,
                "fill_opacity": 0.2,
            },
        ).scale(0.55)

        # Позиционируем добавляемые блоки справа от кода (начальная позиция)
        added_1.next_to(base_code, RIGHT, buff=0.8).shift(UP * 0.6)
        added_2.next_to(base_code, RIGHT, buff=0.8).shift(DOWN * 0.3)

        # Пояснение
        explanation = Text(
            "Компилятор добавляет вызовы DFSan API:",
            font_size=16,
            color=GREY,
        )
        explanation.next_to(title, DOWN, buff=0.25)
        self.play(Write(explanation))
        self.wait(0.3)

        # Показываем добавляемые блоки
        self.play(FadeIn(added_1, shift=LEFT * 0.3))
        self.wait(0.3)
        self.play(FadeIn(added_2, shift=LEFT * 0.3))
        self.wait(0.5)

        # Теперь создаем финальный инструментированный код
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

        # Анимация "вдвигания" - трансформируем базовый код в финальный
        self.play(
            Transform(base_code, inst_code),
            FadeOut(added_1),
            FadeOut(added_2),
            run_time=1.0
        )
        self.wait(0.8)

        # ИСПРАВЛЕНО: полностью пересоздаем сцену с правильным финальным кодом
        # Удаляем ВСЁ и создаем заново
        self.play(
            FadeOut(source_grp),
            FadeOut(arrow_left),
            FadeOut(arrow_right),
            FadeOut(compiler),
            FadeOut(compiler_text),
            FadeOut(explanation),
            FadeOut(base_code),  # Удаляем трансформированный код
            FadeOut(inst_label),  # Удаляем старый label
            run_time=0.5,
        )
        
        # Создаем свежий финальный код с правильным позиционированием
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
        )
        
        final_inst_label = Text("Инструментированный код", font_size=32, color=WHITE)
        final_inst_label.next_to(final_inst_code, UP, buff=0.12)
        final_inst_grp = VGroup(final_inst_code, final_inst_label)
        final_inst_grp.scale(0.55)
        final_inst_grp.move_to(ORIGIN + UP * 0.15)

        # Показываем новый код
        self.play(FadeIn(final_inst_grp), run_time=0.5)
        self.wait(0.25)

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
        legend_items = VGroup(
            VGroup(Dot(color=C_SOURCE), Text("SOURCE: dfsan_set_label", font_size=16, color=C_SOURCE)).arrange(RIGHT, buff=0.18),
            VGroup(Dot(color=C_PROP), Text("PROPAGATION: операции/вызовы", font_size=16, color=C_PROP)).arrange(RIGHT, buff=0.18),
            VGroup(Dot(color=C_CHECK), Text("CHECK: dfsan_read_label", font_size=16, color=C_CHECK)).arrange(RIGHT, buff=0.18),
            VGroup(Dot(color=C_SINK), Text("SINK: system(cmd)", font_size=16, color=C_SINK)).arrange(RIGHT, buff=0.18),
        ).arrange_in_grid(rows=2, cols=2, buff=(0.9, 0.2), aligned_edge=LEFT)
        legend = VGroup(legend_box, legend_items)
        legend_items.move_to(legend_box)
        legend.scale(0.85)
        legend.next_to(final_inst_code, DOWN, buff=0.25)

        self.play(FadeIn(legend), run_time=0.5)

        # Функция подсветки строк
        line_count = len(inst_str.splitlines())
        line_height = final_inst_code.height / (line_count + 0.8)

        def highlight_lines(first: int, last: int, color):
            lines_span = last - first + 1
            rect = RoundedRectangle(
                corner_radius=0.04,
                width=final_inst_code.width * 0.88,
                height=line_height * lines_span * 0.90,
                color=color,
                fill_color=color,
                fill_opacity=0.25,
                stroke_width=3,
            )
            rect.align_to(final_inst_code, LEFT).shift(RIGHT * 0.15)
            code_top = final_inst_code.get_top()
            first_line_center = code_top + DOWN * (line_height * 0.8)
            target_center = first_line_center + DOWN * line_height * (first - 1)
            span_center = target_center + DOWN * line_height * (lines_span - 1) * 0.5
            rect.move_to([rect.get_center()[0], span_center[1], 0])
            return rect

        # SOURCE: dfsan_set_label (строки 3-5)
        init_highlight = highlight_lines(3, 5, C_SOURCE)
        init_desc = VGroup(
            Text("dfsan_set_label()", font_size=14, color=C_SOURCE, weight=BOLD),
            Text("SOURCE: помечает байты user_input как tainted", font_size=12, color=WHITE),
        ).arrange(DOWN, buff=0.08)
        init_desc.next_to(init_highlight, LEFT, buff=0.5)

        self.play(Create(init_highlight), FadeIn(init_desc, shift=RIGHT * 0.15))
        self.wait(1.4)
        self.play(FadeOut(init_highlight), FadeOut(init_desc))

        # PROPAGATION: sprintf (строки 6-7)
        prop_highlight = highlight_lines(6, 7, C_PROP)
        prop_desc = VGroup(
            Text("sprintf()", font_size=14, color=C_PROP, weight=BOLD),
            Text("PROPAGATION: метка может перейти в cmd", font_size=12, color=WHITE),
        ).arrange(DOWN, buff=0.08)
        prop_desc.next_to(prop_highlight, RIGHT, buff=0.5)

        self.play(Create(prop_highlight), FadeIn(prop_desc, shift=LEFT * 0.15))
        self.wait(1.4)
        self.play(FadeOut(prop_highlight), FadeOut(prop_desc))

        # CHECK: dfsan_read_label (строки 9-11)
        check_highlight = highlight_lines(9, 11, C_CHECK)
        check_desc = VGroup(
            Text("dfsan_read_label()", font_size=14, color=C_CHECK, weight=BOLD),
            Text("CHECK: проверка метки cmd перед system()", font_size=12, color=WHITE),
        ).arrange(DOWN, buff=0.08)
        check_desc.next_to(check_highlight, RIGHT, buff=0.5)

        self.play(Create(check_highlight), FadeIn(check_desc, shift=LEFT * 0.15))
        self.wait(1.4)
        self.play(FadeOut(check_highlight), FadeOut(check_desc))

        # SINK: system (строка 13)
        sink_highlight = highlight_lines(13, 13, C_SINK)
        sink_desc = VGroup(
            Text("system()", font_size=14, color=C_SINK, weight=BOLD),
            Text("SINK: использование данных в опасном вызове", font_size=12, color=WHITE),
        ).arrange(DOWN, buff=0.08)
        sink_desc.next_to(sink_highlight, RIGHT, buff=0.5)

        self.play(Create(sink_highlight), FadeIn(sink_desc, shift=LEFT * 0.15))
        self.wait(1.2)
        self.play(FadeOut(sink_highlight), FadeOut(sink_desc))

        self.play(FadeOut(legend), run_time=0.35)
        self.play(*[FadeOut(m) for m in self.mobjects])
