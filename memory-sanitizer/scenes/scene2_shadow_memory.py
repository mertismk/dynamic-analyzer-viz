from manim import *


class ShadowMemoryMapping(Scene):
    def construct(self):
        title = Text("MSan: Теневая память (Shadow Memory)", font_size=36)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title))

        intro_text = VGroup(
            Text(
                "Проблема: как отследить, инициализирован ли каждый байт?",
                font_size=22,
                color=YELLOW,
            ),
            Text(
                "Решение: для каждого байта памяти создаём", font_size=20, color=WHITE
            ),
            Text(
                "специальный байт-метку в «теневой памяти»", font_size=20, color=WHITE
            ),
        ).arrange(DOWN, buff=0.2)
        intro_text.move_to(ORIGIN)

        self.play(Write(intro_text))
        self.wait(3)
        self.play(FadeOut(intro_text))

        demo_label = Text(
            "Концепция: 1 байт памяти = 1 байт метаданных", font_size=20, color=YELLOW
        )
        demo_label.next_to(title, DOWN, buff=0.3)
        self.play(Write(demo_label))

        mem_byte = Square(side_length=1, color=BLUE, fill_opacity=0.2)
        mem_byte_label = Text("Байт памяти", font_size=16, color=BLUE).next_to(
            mem_byte, UP
        )
        mem_byte_val = Text("?", font_size=24, color=WHITE).move_to(mem_byte)
        mem_grp = VGroup(mem_byte, mem_byte_label, mem_byte_val)
        mem_grp.shift(LEFT * 2.5)

        arrow_demo = Arrow(ORIGIN, ORIGIN, color=YELLOW)

        shadow_byte = Square(side_length=1, color=GREY, fill_opacity=0.2)
        shadow_byte_label = Text("Shadow байт", font_size=16, color=GREY).next_to(
            shadow_byte, UP
        )
        shadow_byte_val = Text("1", font_size=24, color=RED).move_to(shadow_byte)
        shadow_grp = VGroup(shadow_byte, shadow_byte_label, shadow_byte_val)
        shadow_grp.shift(RIGHT * 2.5)

        demo_group = VGroup(mem_grp, shadow_grp).move_to(ORIGIN)
        arrow_demo = Arrow(
            mem_byte.get_right(), shadow_byte.get_left(), color=YELLOW, buff=0.2
        )

        arrow_label = Text("отображается в", font_size=14, color=YELLOW).next_to(
            arrow_demo, UP, buff=0.1
        )

        self.play(FadeIn(mem_grp))
        self.play(GrowArrow(arrow_demo), Write(arrow_label))
        self.play(FadeIn(shadow_grp))
        self.wait(1)

        # Объяснение значений
        explanation = Text(
            "1 = не инициализирован, 0 = инициализирован", font_size=18, color=WHITE
        )
        explanation.to_edge(DOWN, buff=1)
        self.play(Write(explanation))
        self.wait(2)

        self.play(
            *[
                FadeOut(mob)
                for mob in [
                    mem_grp,
                    shadow_grp,
                    arrow_demo,
                    arrow_label,
                    demo_label,
                    explanation,
                ]
            ]
        )

        main_label = Text("Принцип 1-к-1 отображения", font_size=20, color=YELLOW)
        main_label.next_to(title, DOWN, buff=0.3)
        self.play(Write(main_label))

        mem_group = VGroup()

        # App Memory
        app_mem = Rectangle(width=3.2, height=6, color=BLUE, fill_opacity=0.1)
        app_label = Text("Память Приложения", font_size=24, color=BLUE).next_to(
            app_mem, UP
        )

        # Shadow Memory
        shadow_mem = Rectangle(width=3.2, height=6, color=GREY, fill_opacity=0.1)
        shadow_label = Text("Теневая Память", font_size=24, color=GREY).next_to(
            shadow_mem, UP
        )

        blocks = VGroup(app_mem, shadow_mem)
        blocks.arrange(RIGHT, buff=3.5)

        app_label.next_to(app_mem, UP)
        shadow_label.next_to(shadow_mem, UP)

        mem_group.add(app_mem, app_label, shadow_mem, shadow_label)
        mem_group.scale(0.85)
        mem_group.move_to(ORIGIN).shift(DOWN * 0.3)

        self.play(Create(mem_group))

        map_arrow = Arrow(
            app_mem.get_center(), shadow_mem.get_center(), color=YELLOW, buff=0
        )
        map_label = Text(
            "Каждый байт → Shadow байт", font_size=16, color=YELLOW
        ).next_to(map_arrow, UP)
        self.play(GrowArrow(map_arrow), Write(map_label))

        def create_byte_block(
            bits, box_color, text_color, label_text, label_color=WHITE
        ):
            bits_group = VGroup()
            for b in bits:
                box = Square(side_length=0.3, color=box_color, fill_opacity=0.2)
                txt = Text(b, font_size=16, color=text_color)
                txt.move_to(box)
                bits_group.add(VGroup(box, txt))
            bits_group.arrange(RIGHT, buff=0)

            label = Text(label_text, font_size=14, color=label_color)
            label.next_to(bits_group, UP, buff=0.1)

            return VGroup(bits_group, label)

        # Инициализированная память
        y1 = app_mem.get_top() + DOWN * 1.8

        row1_app = create_byte_block("10100101", BLUE, WHITE, "Адрес: 0x10", BLUE_A)
        row1_app.move_to(y1)
        row1_app.set_x(app_mem.get_x())

        y1_shadow = shadow_mem.get_top() + DOWN * 1.8
        row1_shadow = create_byte_block("00000000", GREY, GREEN, "Чисто (Clean)", GREEN)
        row1_shadow.move_to(y1_shadow)
        row1_shadow.set_x(shadow_mem.get_x())

        self.play(FadeIn(row1_app))
        self.play(TransformFromCopy(row1_app[0], row1_shadow[0]), Write(row1_shadow[1]))

        # Неинициализированная память
        y2 = app_mem.get_top() + DOWN * 3.2

        row2_app = create_byte_block("????????", BLUE, RED, "Адрес: 0x20", BLUE_A)
        row2_app.move_to(y2)
        row2_app.set_x(app_mem.get_x())

        y2_shadow = shadow_mem.get_top() + DOWN * 3.2
        row2_shadow = create_byte_block("11111111", GREY, RED, "Мусор (Poisoned)", RED)
        row2_shadow.move_to(y2_shadow)
        row2_shadow.set_x(shadow_mem.get_x())

        self.play(FadeIn(row2_app))
        self.play(TransformFromCopy(row2_app[0], row2_shadow[0]), Write(row2_shadow[1]))

        # Частично инициализированная память
        y3 = app_mem.get_top() + DOWN * 4.6

        row3_app = create_byte_block("11110000", BLUE, WHITE, "Адрес: 0x30", BLUE_A)
        row3_app.move_to(y3)
        row3_app.set_x(app_mem.get_x())

        bits_mixed = VGroup()
        shadow_bits = "00001111"
        for b in shadow_bits:
            c = GREEN if b == "0" else RED
            box = Square(side_length=0.3, color=GREY, fill_opacity=0.2)
            txt = Text(b, font_size=16, color=c)
            txt.move_to(box)
            bits_mixed.add(VGroup(box, txt))
        bits_mixed.arrange(RIGHT, buff=0)

        label_partial = Text("Частично (Partial)", font_size=14, color=YELLOW)
        label_partial.next_to(bits_mixed, UP, buff=0.1)

        row3_shadow = VGroup(bits_mixed, label_partial)

        y3_shadow = shadow_mem.get_top() + DOWN * 4.6
        row3_shadow.move_to(y3_shadow)
        row3_shadow.set_x(shadow_mem.get_x())

        self.play(FadeIn(row3_app))
        self.play(TransformFromCopy(row3_app[0], row3_shadow[0]), Write(label_partial))

        # Легенда
        legend = VGroup(
            Text("0 = Иниц.", color=GREEN, font_size=24),
            Text("|", font_size=24, color=GREY),
            Text("1 = Не иниц. (Poison)", color=RED, font_size=24),
        ).arrange(RIGHT, buff=0.5)

        legend.to_edge(DOWN, buff=0.5)

        self.play(Write(legend))
        self.wait(3)

        self.play(*[FadeOut(mob) for mob in self.mobjects])
