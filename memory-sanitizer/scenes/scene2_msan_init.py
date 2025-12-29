from manim import *
from pygments.styles.monokai import MonokaiStyle
from pygments.token import Name


class MSanStyle(MonokaiStyle):
    styles = MonokaiStyle.styles.copy()
    styles[Name.Function] = "#a6e22e"


class MSanInitScene(Scene):
    def construct(self):
        inst_code_str = """int main() {
    int* arr = new int[5];
    __msan_allocated_memory(arr, 20);

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
        inst_grp.scale(0.62).move_to(LEFT * 3.5 + DOWN * 0.3)

        self.add(inst_grp)

        title = Text(
            "MSan: Автоматическая инициализация",
            font_size=38,
            color=BLUE_B,
            font="Inter",
        )
        title.to_edge(UP, buff=0.3)
        self.play(Write(title))
        self.wait(0.3)

        phase1 = Text(
            "При старте программы",
            font_size=18,
            color=YELLOW,
            weight=BOLD,
            font="Inter",
        )
        phase1.next_to(title, DOWN, buff=0.25)
        self.play(Write(phase1), run_time=0.8)

        # Виртуальное адресное пространство (вертикальная схема)
        memory_title = Text(
            "Виртуальная память процесса:",
            font_size=16,
            color=WHITE,
            weight=BOLD,
            font="Inter",
        )
        memory_title.move_to(RIGHT * 3.3 + UP * 2.2)

        # Общий контейнер виртуальной памяти
        vm_container = RoundedRectangle(
            corner_radius=0.1,
            width=3.5,
            height=5.2,
            color=GREY_B,
            fill_opacity=0.05,
            stroke_width=2,
        )
        vm_container.next_to(memory_title, DOWN, buff=0.3)

        self.play(
            FadeIn(memory_title, shift=DOWN * 0.2), Create(vm_container), run_time=1
        )
        self.wait(0.3)

        # Стек
        stack_box = Rectangle(
            width=3.0, height=0.8, color=BLUE_C, fill_opacity=0.2, stroke_width=2
        )
        stack_label = Text(
            "Stack", font_size=14, color=BLUE_C, weight=BOLD, font="Inter"
        )
        stack = VGroup(stack_box, stack_label.move_to(stack_box))
        stack.move_to(vm_container.get_top() + DOWN * 0.5)

        # Куча
        heap_box = Rectangle(
            width=3.0, height=0.8, color=BLUE, fill_opacity=0.2, stroke_width=2
        )
        heap_label = Text("Heap", font_size=14, color=BLUE, weight=BOLD, font="Inter")
        heap = VGroup(heap_box, heap_label.move_to(heap_box))
        heap.next_to(stack, DOWN, buff=0.15)

        # Данные программы
        data_box = Rectangle(
            width=3.0, height=0.6, color=BLUE_A, fill_opacity=0.15, stroke_width=2
        )
        data_label = Text("Data", font_size=13, color=BLUE_A, font="Inter")
        data = VGroup(data_box, data_label.move_to(data_box))
        data.next_to(heap, DOWN, buff=0.15)

        # Код программы
        code_box = Rectangle(
            width=3.0, height=0.6, color=BLUE_A, fill_opacity=0.15, stroke_width=2
        )
        code_label = Text("Code", font_size=13, color=BLUE_A, font="Inter")
        code_mem = VGroup(code_box, code_label.move_to(code_box))
        code_mem.next_to(data, DOWN, buff=0.15)

        self.play(
            FadeIn(stack, shift=DOWN * 0.2),
            FadeIn(heap, shift=DOWN * 0.2),
            FadeIn(data, shift=DOWN * 0.2),
            FadeIn(code_mem, shift=DOWN * 0.2),
            run_time=1,
            lag_ratio=0.2,
        )
        self.wait(0.5)

        # ТЕНЕВАЯ ПАМЯТЬ появляется
        shadow_box = Rectangle(
            width=3.0, height=1.5, color=GREY, fill_opacity=0.25, stroke_width=3
        )
        shadow_label = VGroup(
            Text("Shadow Memory", font_size=15, color=GREY, weight=BOLD, font="Inter"),
            Text("(Теневая память)", font_size=12, color=GREY, font="Inter"),
        ).arrange(DOWN, buff=0.05)
        shadow_label.move_to(shadow_box)
        shadow = VGroup(shadow_box, shadow_label)
        shadow.next_to(code_mem, DOWN, buff=0.15)

        # Стрелка и подпись "MSan выделяет"
        arrow_msan = Arrow(
            vm_container.get_left() + LEFT * 0.3,
            shadow_box.get_left(),
            color=YELLOW,
            stroke_width=4,
            buff=0.1,
        )
        msan_label = Text(
            "MSan выделяет\nавтоматически",
            font_size=14,
            color=YELLOW,
            font="Inter",
            weight=BOLD,
        )
        msan_label.next_to(arrow_msan, LEFT, buff=0.2)

        self.play(GrowArrow(arrow_msan), Write(msan_label), run_time=0.8)
        self.play(
            FadeIn(shadow, shift=UP * 0.3, scale=0.9),
            Flash(shadow_box, color=YELLOW, flash_radius=0.8, num_lines=12),
            run_time=1.2,
        )
        self.wait(0.8)

        # Связь - просто текст с соотношением
        mapping_label = Text(
            "1 байт Shadow → 1 байт памяти",
            font_size=13,
            color=GREY,
            font="Inter",
            slant=ITALIC,
        )
        mapping_label.next_to(shadow, DOWN, buff=0.25)

        # Финальное пояснение - размещаем слева от контейнера
        explanation = VGroup(
            Text(
                "Хранит статус:", font_size=15, color=WHITE, font="Inter", weight=BOLD
            ),
            Text("0 = инициализирован ✓", font_size=14, color=GREEN, font="Inter"),
            Text("1 = не инициализирован ✗", font_size=14, color=RED, font="Inter"),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        explanation.next_to(vm_container, LEFT, buff=0.6).shift(DOWN * 1.5)

        self.play(
            FadeIn(mapping_label, shift=UP * 0.2),
            FadeIn(explanation, shift=RIGHT * 0.2, lag_ratio=0.15),
            run_time=1.2,
        )
        self.wait(2.5)

        # Убираем всё
        self.play(
            FadeOut(memory_title),
            FadeOut(vm_container),
            FadeOut(stack),
            FadeOut(heap),
            FadeOut(data),
            FadeOut(code_mem),
            FadeOut(shadow),
            FadeOut(arrow_msan),
            FadeOut(msan_label),
            FadeOut(mapping_label),
            FadeOut(explanation),
            FadeOut(phase1),
            run_time=0.8,
        )
        self.wait(0.3)
