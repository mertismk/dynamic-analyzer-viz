from manim import *
from pygments.styles.monokai import MonokaiStyle
from pygments.token import Name, Keyword

# OFFICIAL DOCUMENTATION
# Clang Static Analyzer - Taint Analysis:
# https://clang.llvm.org/docs/analyzer/user-docs/TaintAnalysisConfiguration.html
#
# DataFlowSanitizer (DFSan):
# https://clang.llvm.org/docs/DataFlowSanitizer.html
# Concept: Source - Propagation - Sink


class TaintStyle(MonokaiStyle):
    styles = MonokaiStyle.styles.copy()
    styles[Name.Function] = "#a6e22e"
    styles[Name.Builtin] = "#66d9ef"
    styles[Keyword] = "#f92672"


class SourcePropagationSinkScene(Scene):
    def construct(self):
        title = Text("Taint Propagation: Source / Propagation / Sink", font_size=36)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title))
        self.wait(0.4)

        subtitle = Text(
            "Путь tainted-данных: от источника до опасного sink",
            font_size=16,
            color=YELLOW,
        )
        subtitle.next_to(title, DOWN, buff=0.25)
        self.play(Write(subtitle))
        self.wait(0.7)

        # source / propagation / sink блоки

        # source
        source_str = """
        getenv(\"CMD\")
        fread(...)
        HTTP params"""

        source_code = Code(
            code_string=source_str,
            language="c++",
            tab_width=4,
            formatter_style=TaintStyle,
            background="rectangle",
            add_line_numbers=False,
            background_config={
                "stroke_width": 2.5,
                "stroke_color": RED,
                "fill_color": RED,
                "fill_opacity": 0.2,
            },
        )

        source_label = Text("SOURCE", font_size=24, color=RED, weight=BOLD)
        source_label.next_to(source_code, UP, buff=0.12)

        source_grp = VGroup(source_code, source_label)
        source_grp.scale(0.9)
        source_grp.move_to(LEFT * 4.4 + UP * 0.3)

        # propagation
        prop_str = """
        x = y;
        strcpy(a, b);
        sprintf(cmd, ...)"""

        prop_code = Code(
            code_string=prop_str,
            language="c++",
            tab_width=4,
            formatter_style=TaintStyle,
            background="rectangle",
            add_line_numbers=False,
            background_config={
                "stroke_width": 2.5,
                "stroke_color": ORANGE,
                "fill_color": ORANGE,
                "fill_opacity": 0.2,
            },
        )

        prop_label = Text("PROPAGATION", font_size=24, color=ORANGE, weight=BOLD)
        prop_label.next_to(prop_code, UP, buff=0.12)

        prop_grp = VGroup(prop_code, prop_label)
        prop_grp.scale(0.9)
        prop_grp.move_to(ORIGIN + UP * 0.3)

        # sink
        sink_str = """
        system(cmd)
        exec(...)
        SQL query"""

        sink_code = Code(
            code_string=sink_str,
            language="c++",
            tab_width=4,
            formatter_style=TaintStyle,
            background="rectangle",
            add_line_numbers=False,
            background_config={
                "stroke_width": 2.5,
                "stroke_color": GREEN,
                "fill_color": GREEN,
                "fill_opacity": 0.2,
            },
        )

        sink_label = Text("SINK", font_size=24, color=GREEN, weight=BOLD)
        sink_label.next_to(sink_code, UP, buff=0.12)

        sink_grp = VGroup(sink_code, sink_label)
        sink_grp.scale(0.9)
        sink_grp.move_to(RIGHT * 4.4 + UP * 0.3)

        # Появление трёх блоков
        self.play(FadeIn(source_grp))
        self.wait(0.3)
        self.play(FadeIn(prop_grp))
        self.wait(0.3)
        self.play(FadeIn(sink_grp))
        self.wait(0.7)

        # Стрелки taint-потока
        arrow1 = Arrow(
            source_code.get_right(),
            prop_code.get_left(),
            color=YELLOW,
            stroke_width=4,
            buff=0.12,
        )
        arrow1_label = Text("tainted", font_size=14, color=YELLOW)
        arrow1_label.next_to(arrow1, UP, buff=0.06)

        arrow2 = Arrow(
            prop_code.get_right(),
            sink_code.get_left(),
            color=YELLOW,
            stroke_width=4,
            buff=0.12,
        )
        arrow2_label = Text("tainted", font_size=14, color=YELLOW)
        arrow2_label.next_to(arrow2, UP, buff=0.06)

        self.play(Create(arrow1), Write(arrow1_label))
        self.wait(0.6)
        self.play(Create(arrow2), Write(arrow2_label))
        self.wait(1.0)

        # Ветка без санитайзера (уязвимость)
        warning = Text(
            "Уязвимость: загрязненные данные достигают sink",
            font_size=20,
            color=RED,
            weight=BOLD,
        )
        warning.to_edge(DOWN, buff=0.5)

        self.play(Write(warning))
        self.play(Wiggle(sink_code, scale_value=1.1))
        self.wait(1.4)

        # Добавляем санитайзер между prop и sink
        self.play(FadeOut(warning), run_time=0.5)

        # Санитайзер
        sanitizer_str = """
        validate / escape / check"""

        sanitizer_code = Code(
            code_string=sanitizer_str,
            language="c++",
            tab_width=4,
            formatter_style=TaintStyle,
            background="rectangle",
            add_line_numbers=False,
            background_config={
                "stroke_width": 2.5,
                "stroke_color": BLUE,
                "fill_color": BLUE,
                "fill_opacity": 0.2,
            },
        )

        sanitizer_label = Text("SANITIZER", font_size=24, color=BLUE, weight=BOLD)
        sanitizer_label.next_to(sanitizer_code, UP, buff=0.12)

        sanitizer_grp = VGroup(sanitizer_code, sanitizer_label)
        sanitizer_grp.scale(0.9)
        sanitizer_grp.move_to(ORIGIN + DOWN * 2)


        expl = Text(
            "Sanitizer очищает данные, taint не доходит до sink",
            font_size=16,
            color=BLUE,
        )
        expl.to_edge(DOWN, buff=0.5)

        self.play(FadeIn(sanitizer_grp), Write(expl))
        self.wait(0.8)

        # Новые стрелки: prop - San - sink (без уязвимости)
        arrow2_new = Arrow(
            prop_code.get_bottom(),
            sanitizer_label.get_top(),
            color=YELLOW,
            stroke_width=4,
            buff=0.12,
        )
        arrow3_clean = Arrow(
            sanitizer_code.get_right(),
            sink_code.get_bottom() + UP * 0.12,
            color=GREEN,
            stroke_width=4,
            buff=0.12,
        )
        arrow3_label = Text("clean", font_size=14, color=GREEN)
        arrow3_label.next_to(arrow3_clean, RIGHT, buff=0.06)

        # Убираем старый tainted-стрелку ко sink
        self.play(
            FadeOut(arrow2),
            FadeOut(arrow2_label),
            Create(arrow2_new),
            Create(arrow3_clean),
            Write(arrow3_label),
        )
        self.wait(1.2)

        ok_sign = Text(
            "Уязвимости нет (загрязнение прервано до sink)",
            font_size=20,
            color=GREEN,
            weight=BOLD,
        )
        ok_sign.move_to(expl.get_center())

        self.play(FadeOut(expl), Write(ok_sign))
        self.wait(1.6)

        self.play(*[FadeOut(m) for m in self.mobjects])
