from manim import *
from pygments.styles.monokai import MonokaiStyle
from pygments.token import Name, Keyword

class TaintStyle(MonokaiStyle):
    styles = MonokaiStyle.styles.copy()
    styles[Name.Function] = "#a6e22e"
    styles[Name.Builtin] = "#66d9ef"
    styles[Keyword] = "#f92672"


class StaticAnalyzerTaintScene(Scene):
    def construct(self):
        # Палитра (согласована с другими сценами)
        C_SOURCE = PURPLE
        C_PROP = ORANGE
        C_FILTER = TEAL
        C_SINK = GREEN
        C_NOTE = YELLOW

        title = Text("Taint Propagation: Static Analyzer", font_size=34)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title))
        self.wait(0.3)

        subtitle = Text(
            "Правила задаются YAML-конфигом: Propagations -> Filters -> Sinks",
            font_size=16,
            color=C_NOTE,
        )
        subtitle.next_to(title, DOWN, buff=0.25)
        self.play(Write(subtitle))
        self.wait(0.5)

        # ===== ЧАСТЬ 1. МОДЕЛЬ ИЗ ДОКУМЕНТАЦИИ (примерные записи как в доке) =====
        source_str = """- Name: fread
  DstArgs: [0, -1]"""

        prop_str = """- Name: dirname
  SrcArgs: [0]
  DstArgs: [-1]"""

        sink_str = """- Name: system
  Args: [0]"""

        filter_str = """- Name: cleanse_first_arg
  Args: [0]"""

        def yaml_code_block(s: str, color):
            return Code(
                code_string=s,
                language="yaml",
                tab_width=2,
                formatter_style=TaintStyle,
                background="rectangle",
                add_line_numbers=False,
                background_config={
                    "stroke_width": 2.5,
                    "stroke_color": color,
                    "fill_color": color,
                    "fill_opacity": 0.18,
                },
            )

        source_code = yaml_code_block(source_str, C_SOURCE)
        prop_code = yaml_code_block(prop_str, C_PROP)
        sink_code = yaml_code_block(sink_str, C_SINK)

        source_label = Text("SOURCE", font_size=22, color=C_SOURCE, weight=BOLD).next_to(source_code, UP, buff=0.12)
        prop_label = Text("PROPAGATION", font_size=22, color=C_PROP, weight=BOLD).next_to(prop_code, UP, buff=0.12)
        sink_label = Text("SINK", font_size=22, color=C_SINK, weight=BOLD).next_to(sink_code, UP, buff=0.12)

        # ИСПРАВЛЕНО: расстояние увеличено с 4.2 до 4.6 для видимости стрелок
        source_grp = VGroup(source_code, source_label).scale(0.7).move_to(LEFT * 4.6 + UP * 0.35)
        prop_grp = VGroup(prop_code, prop_label).scale(0.7).move_to(ORIGIN + UP * 0.35)
        sink_grp = VGroup(sink_code, sink_label).scale(0.7).move_to(RIGHT * 4.6 + UP * 0.35)

        self.play(FadeIn(source_grp), FadeIn(prop_grp), FadeIn(sink_grp), run_time=0.8)
        self.wait(0.2)

        arrow1 = Arrow(source_code.get_right(), prop_code.get_left(), color=C_NOTE, stroke_width=4, buff=0.12)
        arrow2 = Arrow(prop_code.get_right(), sink_code.get_left(), color=C_NOTE, stroke_width=4, buff=0.12)
        a1t = Text("tainted", font_size=14, color=C_NOTE).next_to(arrow1, UP, buff=0.06)
        a2t = Text("tainted", font_size=14, color=C_NOTE).next_to(arrow2, UP, buff=0.06)

        self.play(Create(arrow1), Write(a1t))
        self.play(Create(arrow2), Write(a2t))
        self.wait(0.4)

        warn = Text("Если taint дошёл до SINK -> предупреждение", font_size=20, color=C_SOURCE, weight=BOLD)
        warn.to_edge(DOWN, buff=0.65)
        self.play(Write(warn))
        self.play(Wiggle(sink_code, scale_value=1.08))
        self.wait(0.9)

        self.play(FadeOut(warn), run_time=0.3)

        filter_code = yaml_code_block(filter_str, C_FILTER)
        filter_label = Text("FILTER", font_size=22, color=C_FILTER, weight=BOLD).next_to(filter_code, UP, buff=0.12)
        filter_grp = VGroup(filter_code, filter_label).scale(0.7).move_to(ORIGIN + DOWN * 2.05)

        self.play(FadeIn(filter_grp), run_time=0.55)

        expl = Text("FILTER может очистить Args -> данные будут без пометки taint", font_size=16, color=C_FILTER)
        expl.to_edge(DOWN, buff=0.65)
        self.play(Write(expl))
        self.wait(0.6)

        arrow2_new = Arrow(prop_code.get_bottom(), filter_label.get_top(), color=C_NOTE, stroke_width=4, buff=0.12)
        arrow3_clean = Arrow(filter_code.get_right(), sink_code.get_bottom() + UP * 0.12, color=C_SINK, stroke_width=4, buff=0.12)
        a3t = Text("clean", font_size=14, color=C_SINK).next_to(arrow3_clean, RIGHT, buff=0.06)

        self.play(FadeOut(arrow2), FadeOut(a2t), Create(arrow2_new), Create(arrow3_clean), Write(a3t), run_time=0.9)
        self.wait(0.4)

        self.play(FadeOut(expl), run_time=0.25)

        # ===== ПЕРЕХОД К ПРИМЕРУ НА КОДЕ =====
        # ИСПРАВЛЕНО: убрал промежуточный текст transition, чтобы не залезал на блоки
        # Просто меняем subtitle на пустой текст
        self.play(FadeOut(subtitle), run_time=0.3)
        self.wait(0.3)

        # Свернём часть 1 вверх, чтобы освободить место под пример
        model_grp = VGroup(
            source_grp, prop_grp, sink_grp,
            arrow1, a1t,
            arrow2_new, arrow3_clean, a3t,
            filter_grp,
        )
        self.play(model_grp.animate.scale(0.55).to_edge(UP, buff=0.95), run_time=0.8)
        self.wait(0.2)

        # ===== ЧАСТЬ 2. ПРИМЕР: КОД И YAML ДЛЯ НЕГО (связь с DFSan-сценой) =====
        code_str = """int main() {
  char* user_input = getenv("CMD");
  char cmd[256];
  sprintf(cmd, "ls %s", user_input);
  system(cmd);
  return 0;
}"""

        code_block_c = Code(
            code_string=code_str,
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
        ).scale(0.62)

        code_label = Text("Пример кода", font_size=24, color=WHITE, weight=BOLD)
        code_label.next_to(code_block_c, UP, buff=0.12)
        # ИСПРАВЛЕНО: поднял с 2.1 до 1.9, расстояние уменьшил с 3.8 до 3.2
        code_grp = VGroup(code_block_c, code_label).move_to(LEFT * 3.2 + DOWN * 1.9)

        yaml_str = """Propagations:
  - Name: getenv
    DstArgs: [-1]

  - Name: sprintf
    SrcArgs: [2]
    DstArgs: [0]

Sinks:
  - Name: system
    Args: [0]"""

        yaml_block = Code(
            code_string=yaml_str,
            language="yaml",
            tab_width=2,
            formatter_style=TaintStyle,
            background="rectangle",
            add_line_numbers=False,
            background_config={
                "stroke_width": 2,
                "stroke_color": GREY_B,
                "fill_color": BLACK,
                "fill_opacity": 0.9,
            },
        ).scale(0.62)

        yaml_label = Text("YAML-правила для анализатора", font_size=24, color=C_NOTE, weight=BOLD)
        yaml_label.next_to(yaml_block, UP, buff=0.12)
        # ИСПРАВЛЕНО: поднял с 2.1 до 1.9, расстояние уменьшил с 3.8 до 3.2
        yaml_grp = VGroup(yaml_block, yaml_label).move_to(RIGHT * 3.2 + DOWN * 1.9)

        self.play(FadeIn(code_grp), FadeIn(yaml_grp), run_time=0.75)
        self.wait(0.25)

        # Подсветки по строкам (в C-коде) — 1-based
        c_lines = len(code_str.splitlines())
        c_line_h = code_block_c.height / (c_lines + 2)

        def highlight_c(first, last, color):
            span = last - first + 1
            rect = RoundedRectangle(
                corner_radius=0.04,
                width=code_block_c.width * 0.9,
                height=c_line_h * span,
                color=color,
                fill_color=color,
                fill_opacity=0.22,
                stroke_width=3,
            )
            rect.align_to(code_block_c, LEFT).shift(RIGHT * 0.12)
            rect.move_to(code_block_c.get_top() + DOWN * c_line_h * (first - 0.5), aligned_edge=UP)
            return rect

        # Подсветки в YAML блоке (координаты примерные; ты потом подгонишь)
        y_getenv = RoundedRectangle(
            corner_radius=0.04,
            width=yaml_block.width * 0.92,
            height=yaml_block.height * 0.20,
            color=C_SOURCE,
            fill_color=C_SOURCE,
            fill_opacity=0.18,
            stroke_width=3,
        )
        y_sprintf = RoundedRectangle(
            corner_radius=0.04,
            width=yaml_block.width * 0.92,
            height=yaml_block.height * 0.26,
            color=C_PROP,
            fill_color=C_PROP,
            fill_opacity=0.18,
            stroke_width=3,
        )
        y_system = RoundedRectangle(
            corner_radius=0.04,
            width=yaml_block.width * 0.92,
            height=yaml_block.height * 0.18,
            color=C_SINK,
            fill_color=C_SINK,
            fill_opacity=0.18,
            stroke_width=3,
        )

        y_getenv.move_to(yaml_block.get_top() + DOWN * (yaml_block.height * 0.23))
        y_sprintf.move_to(yaml_block.get_center() + DOWN * (yaml_block.height * 0.03))
        y_system.move_to(yaml_block.get_bottom() + UP * (yaml_block.height * 0.17))

        # 1) getenv ↔ SOURCE rule
        h_getenv = highlight_c(2, 2, C_SOURCE)
        self.play(Create(h_getenv), Create(y_getenv), run_time=0.45)
        self.wait(0.55)
        self.play(FadeOut(h_getenv), FadeOut(y_getenv), run_time=0.25)

        # 2) sprintf ↔ PROP rule
        h_sprintf = highlight_c(4, 4, C_PROP)
        self.play(Create(h_sprintf), Create(y_sprintf), run_time=0.45)
        self.wait(0.55)
        self.play(FadeOut(h_sprintf), FadeOut(y_sprintf), run_time=0.25)

        # 3) system ↔ SINK rule
        h_system = highlight_c(5, 5, C_SINK)
        self.play(Create(h_system), Create(y_system), run_time=0.45)
        self.wait(0.6)
        self.play(FadeOut(h_system), FadeOut(y_system), run_time=0.25)

     
        self.wait(0.9)

        self.play(*[FadeOut(m) for m in self.mobjects])
