from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Ellipse, Rectangle
from kivy.clock import Clock
import math

PRIMARY_DARK = (0.12, 0.16, 0.23, 1)
INACTIVE_NAV = (0.88, 0.91, 0.94, 1)
ACCENT_CYAN = (0.02, 0.71, 0.83, 1)
ACCENT_ORANGE = (0.97, 0.45, 0.08, 1)
DANGER_RED = (0.93, 0.26, 0.26, 1)

PIE_COLORS = [
    (0.12, 0.16, 0.23, 1),
    (0.97, 0.45, 0.08, 1),
    (0.02, 0.71, 0.83, 1),
    (0.06, 0.72, 0.51, 1),
    (0.96, 0.62, 0.07, 1)
]


class ColorDot(Widget):
    def __init__(self, bg_color=(0, 0, 0, 1), **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        self.bind(pos=self.update_dot, size=self.update_dot)

    def update_dot(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[3])


class RoundedCard(BoxLayout):
    def __init__(self, bg_color=(1, 1, 1, 1), radius=15, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        self.radius = radius
        with self.canvas.before:
            Color(*self.bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class RoundedTextInput(TextInput):
    """Fixed TextInput preserving native touch, cursor, and input focus."""
    def __init__(self, radius=8, **kwargs):
        kwargs.setdefault('multiline', False)
        kwargs.setdefault('foreground_color', (0.1, 0.1, 0.1, 1))
        kwargs.setdefault('hint_text_color', (0.5, 0.5, 0.5, 1))
        kwargs.setdefault('cursor_color', (0.1, 0.1, 0.1, 1))
        kwargs.setdefault('background_normal', '')
        kwargs.setdefault('background_active', '')
        kwargs.setdefault('background_color', (0, 0, 0, 0))
        kwargs.setdefault('padding', [10, 8, 10, 8])
        super().__init__(**kwargs)
        self.radius = radius

        with self.canvas.before:
            Color(0.92, 0.94, 0.96, 1)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])

        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size


class RoundedButton(Button):
    def __init__(self, bg_color=PRIMARY_DARK, radius=12, **kwargs):
        kwargs.setdefault('background_color', (0, 0, 0, 0))
        kwargs.setdefault('color', (1, 1, 1, 1))
        kwargs.setdefault('bold', True)
        super().__init__(**kwargs)
        self.bg_color = bg_color
        self.radius = radius
        with self.canvas.before:
            self.color_canvas = Color(*self.bg_color)
            self.btn_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
        self.bind(pos=self.update_rect, size=self.update_rect)

    def set_bg_color(self, new_color):
        self.bg_color = new_color
        self.color_canvas.rgba = new_color

    def update_rect(self, *args):
        self.btn_rect.pos = self.pos
        self.btn_rect.size = self.size


class RoundedProgressBar(Widget):
    def __init__(self, ratio=0.0, fill_color=ACCENT_CYAN, **kwargs):
        super().__init__(**kwargs)
        self.ratio = min(max(ratio, 0.0), 1.0)
        self.fill_color = fill_color
        self.bind(pos=self.update_bar, size=self.update_bar)

    def update_bar(self, *args):
        self.canvas.clear()
        r = self.height / 2
        with self.canvas:
            Color(0.88, 0.91, 0.94, 1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[r])
            
            if self.ratio > 0:
                Color(*self.fill_color)
                fill_width = max(self.width * self.ratio, r * 2)
                RoundedRectangle(pos=self.pos, size=(min(fill_width, self.width), self.height), radius=[r])


class InteractivePieChart(Widget):
    def __init__(self, data=None, currency="₦", hover_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.data = data or {}
        self.currency = currency
        self.hover_callback = hover_callback
        self.hovered_idx = -1
        self.slices = []
        Window.bind(mouse_pos=self.on_mouse_move)
        self.bind(pos=self.draw_chart, size=self.draw_chart)

    def update_data(self, data, currency="₦"):
        self.data = data
        self.currency = currency
        self.draw_chart()

    def on_mouse_move(self, window, pos):
        if not self.data or not self.get_root_window() or self.parent is None:
            return
        
        local_pos = self.to_widget(*pos)
        if not self.collide_point(*local_pos):
            if self.hovered_idx != -1:
                self.hovered_idx = -1
                self.draw_chart()
                if self.hover_callback:
                    self.hover_callback(None, 0, 0)
            return

        cx, cy = self.center_x, self.center_y
        dx = local_pos[0] - cx
        dy = local_pos[1] - cy
        dist = math.hypot(dx, dy)

        base_size = min(self.width, self.height) * 0.85
        outer_r = base_size / 2
        inner_r = outer_r * 0.55

        if inner_r <= dist <= outer_r + 20:
            angle = math.degrees(math.atan2(dy, dx)) % 360
            found_idx = -1
            for idx, (s_angle, e_angle, cat, val) in enumerate(self.slices):
                if s_angle <= angle <= e_angle:
                    found_idx = idx
                    break

            if found_idx != self.hovered_idx:
                self.hovered_idx = found_idx
                self.draw_chart()
                if self.hover_callback and found_idx != -1:
                    cat, val = list(self.data.items())[found_idx]
                    total = sum(self.data.values())
                    pct = (val / total * 100) if total > 0 else 0
                    self.hover_callback(cat, val, pct)
        else:
            if self.hovered_idx != -1:
                self.hovered_idx = -1
                self.draw_chart()
                if self.hover_callback:
                    self.hover_callback(None, 0, 0)

    def draw_chart(self, *args):
        self.canvas.clear()
        self.slices = []
        if not self.data:
            return

        total = sum(self.data.values())
        if total <= 0:
            return

        base_size = min(self.width, self.height) * 0.85
        start_angle = 0

        with self.canvas:
            for idx, (cat, val) in enumerate(self.data.items()):
                angle = (val / total) * 360
                end_angle = start_angle + angle
                self.slices.append((start_angle, end_angle, cat, val))

                is_hovered = (idx == self.hovered_idx)
                size = base_size + (18 if is_hovered else 0)

                mid_angle_rad = math.radians(start_angle + angle / 2)
                offset = 10 if is_hovered else 0
                ox = math.cos(mid_angle_rad) * offset
                oy = math.sin(mid_angle_rad) * offset

                pos_x = (self.center_x + ox) - size / 2
                pos_y = (self.center_y + oy) - size / 2

                Color(*PIE_COLORS[idx % len(PIE_COLORS)])
                Ellipse(pos=(pos_x, pos_y), size=(size, size), angle_start=start_angle, angle_end=end_angle)
                start_angle = end_angle

            Color(1, 1, 1, 1)
            hole_size = base_size * 0.55
            Ellipse(pos=(self.center_x - hole_size / 2, self.center_y - hole_size / 2), size=(hole_size, hole_size))


class VerticalBarChart(Widget):
    def __init__(self, categories=None, budgets=None, actuals=None, currency="₦", **kwargs):
        super().__init__(**kwargs)
        self.categories = categories or []
        self.budgets = budgets or {}
        self.actuals = actuals or {}
        self.currency = currency
        self.bind(pos=self.draw_chart, size=self.draw_chart)

    def update_data(self, categories, budgets, actuals, currency):
        self.categories = categories
        self.budgets = budgets
        self.actuals = actuals
        self.currency = currency
        self.draw_chart()

    def draw_chart(self, *args):
        self.canvas.clear()
        if not self.categories:
            return

        max_val = max(
            max(list(self.budgets.values()) + [1]),
            max(list(self.actuals.values()) + [1])
        )

        padding = 20
        chart_width = self.width - (padding * 2)
        chart_height = self.height - (padding * 2)
        
        num_cats = len(self.categories)
        group_width = chart_width / max(num_cats, 1)
        bar_width = max(group_width * 0.3, 10)

        with self.canvas:
            Color(0.8, 0.8, 0.8, 1)
            Rectangle(pos=(self.x + padding, self.y + padding), size=(chart_width, 2))

            for idx, cat in enumerate(self.categories):
                b_val = self.budgets.get(cat, 0)
                a_val = self.actuals.get(cat, 0)

                b_height = (b_val / max_val) * (chart_height - 30) if max_val > 0 else 0
                a_height = (a_val / max_val) * (chart_height - 30) if max_val > 0 else 0

                group_x = self.x + padding + (idx * group_width) + (group_width / 2) - bar_width

                Color(*ACCENT_CYAN)
                Rectangle(pos=(group_x - bar_width / 2 - 2, self.y + padding + 2), size=(bar_width, b_height))

                Color(*ACCENT_ORANGE)
                Rectangle(pos=(group_x + bar_width / 2 + 2, self.y + padding + 2), size=(bar_width, a_height))


class DashboardScreen(Screen):
    def __init__(self, app_inst, **kwargs):
        super().__init__(**kwargs)
        self.app = app_inst
        self.build_ui()

    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=12, spacing=12)
        top_row = BoxLayout(orientation='horizontal', spacing=12, size_hint_y=0.48)

        pie_card = RoundedCard(orientation='vertical', padding=12, spacing=6)
        
        pie_head = BoxLayout(orientation='horizontal', size_hint_y=None, height=20)
        pie_head.add_widget(Label(text="EXPENSE BREAKDOWN", font_size='12sp', bold=True, color=(0.4, 0.4, 0.4, 1), halign='left'))
        
        self.lbl_hover_detail = Label(text="Hover a slice for details", font_size='11sp', bold=True, color=ACCENT_ORANGE, halign='right')
        self.lbl_hover_detail.bind(size=self.lbl_hover_detail.setter('text_size'))
        pie_head.add_widget(self.lbl_hover_detail)
        
        pie_card.add_widget(pie_head)
        
        pie_body = BoxLayout(orientation='horizontal', spacing=8)
        self.pie_chart = InteractivePieChart(size_hint_x=0.45, hover_callback=self.on_pie_hover)
        
        scroll_legend = ScrollView(size_hint_x=0.55)
        self.legend_box = BoxLayout(orientation='vertical', spacing=6, size_hint_y=None)
        self.legend_box.bind(minimum_height=self.legend_box.setter('height'))
        scroll_legend.add_widget(self.legend_box)

        pie_body.add_widget(self.pie_chart)
        pie_body.add_widget(scroll_legend)
        pie_card.add_widget(pie_body)
        top_row.add_widget(pie_card)

        qa_card = RoundedCard(orientation='vertical', padding=12, spacing=8)
        qa_card.add_widget(Label(text="Quick Add Expense", font_size='16sp', bold=True, color=(0.1, 0.1, 0.1, 1), size_hint_y=None, height=24))
        qa_card.add_widget(Label(text="Enter amount and pick category", font_size='11sp', color=(0.5, 0.5, 0.5, 1), size_hint_y=None, height=18))

        qa_form = BoxLayout(orientation='vertical', spacing=8)
        self.spinner_cat = Spinner(text='Select Category', values=list(self.app.budgets.keys()), size_hint_y=None, height=36, background_color=(0.9, 0.9, 0.9, 1), color=(0.1, 0.1, 0.1, 1))
        qa_form.add_widget(self.spinner_cat)

        self.input_amt = RoundedTextInput(hint_text="Amount", size_hint_y=None, height=36)
        qa_form.add_widget(self.input_amt)

        btn_add = RoundedButton(text="Add Expense", size_hint_y=None, height=36, on_press=self.add_expense)
        qa_form.add_widget(btn_add)

        qa_card.add_widget(qa_form)
        top_row.add_widget(qa_card)

        main_layout.add_widget(top_row)

        prog_card = RoundedCard(orientation='vertical', padding=12, spacing=8, size_hint_y=0.52)
        
        header_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=32)
        header_box.add_widget(Label(text="PROGRESS TRACKER", font_size='12sp', bold=True, color=(0.4, 0.4, 0.4, 1)))
        
        self.search_input = RoundedTextInput(hint_text="Search category...", size_hint_x=0.4)
        self.search_input.bind(text=self.render_dashboard)
        header_box.add_widget(self.search_input)
        prog_card.add_widget(header_box)

        self.lbl_rem_budget = Label(text="", font_size='14sp', bold=True, color=(0.1, 0.1, 0.1, 1), size_hint_y=None, height=24, halign='left')
        self.lbl_rem_budget.bind(size=self.lbl_rem_budget.setter('text_size'))
        prog_card.add_widget(self.lbl_rem_budget)

        scroll = ScrollView(size_hint=(1, 1))
        self.prog_rows = BoxLayout(orientation='vertical', spacing=8, size_hint_y=None)
        self.prog_rows.bind(minimum_height=self.prog_rows.setter('height'))
        scroll.add_widget(self.prog_rows)
        
        prog_card.add_widget(scroll)

        main_layout.add_widget(prog_card)
        self.add_widget(main_layout)

    def on_pie_hover(self, cat, val, pct):
        if cat:
            self.lbl_hover_detail.text = f"{cat}: {self.app.currency_symbol}{val:,.0f} ({pct:.1f}%)"
        else:
            self.lbl_hover_detail.text = "Hover a slice for details"

    def add_expense(self, instance):
        cat = self.spinner_cat.text
        amt_str = self.input_amt.text.strip()
        if cat in self.app.budgets:
            try:
                amt = float(amt_str)
                self.app.expenses.append({"Category": cat, "Amount": amt})
                self.input_amt.text = ""
                self.app.refresh_all()
            except ValueError:
                pass

    def render_dashboard(self, *args):
        self.spinner_cat.values = list(self.app.budgets.keys())
        
        totals = {}
        for e in self.app.expenses:
            totals[e["Category"]] = totals.get(e["Category"], 0) + e["Amount"]

        total_spent = sum(e["Amount"] for e in self.app.expenses)
        total_budget = sum(self.app.budgets.values())
        rem = total_budget - total_spent

        self.lbl_rem_budget.text = f"Remaining Budget: {self.app.currency_symbol}{rem:,.0f} / {self.app.currency_symbol}{total_budget:,.0f}"
        self.pie_chart.update_data(totals, self.app.currency_symbol)

        self.legend_box.clear_widgets()
        grand_total = sum(totals.values()) if totals else 1
        
        for idx, (cat, amt) in enumerate(totals.items()):
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=24, spacing=6)
            dot = ColorDot(bg_color=PIE_COLORS[idx % len(PIE_COLORS)], size_hint=(None, None), size=(12, 12))
            pct = (amt / grand_total) * 100
            
            lbl = Label(
                text=f"{cat} ({pct:.0f}%): {self.app.currency_symbol}{amt:,.0f}",
                font_size='11sp',
                color=(0.2, 0.2, 0.2, 1),
                halign='left',
                valign='center'
            )
            lbl.bind(size=lbl.setter('text_size'))
            
            row.add_widget(dot)
            row.add_widget(lbl)
            self.legend_box.add_widget(row)

        self.prog_rows.clear_widgets()
        query = self.search_input.text.lower().strip()

        for cat, limit in self.app.budgets.items():
            if query and query not in cat.lower():
                continue

            spent = totals.get(cat, 0)
            ratio = min(spent / limit, 1.0) if limit > 0 else 0
            color = ACCENT_ORANGE if ratio >= 1.0 else ACCENT_CYAN

            row = BoxLayout(orientation='vertical', size_hint_y=None, height=42, spacing=2)
            
            info_box = BoxLayout(orientation='horizontal')
            lbl_cat = Label(text=cat, bold=True, color=(0.1, 0.1, 0.1, 1), halign='left')
            lbl_cat.bind(size=lbl_cat.setter('text_size'))
            
            lbl_val = Label(text=f"{self.app.currency_symbol}{spent:,.0f} / {self.app.currency_symbol}{limit:,.0f}", color=(0.4, 0.4, 0.4, 1), halign='right')
            lbl_val.bind(size=lbl_val.setter('text_size'))
            
            info_box.add_widget(lbl_cat)
            info_box.add_widget(lbl_val)
            
            row.add_widget(info_box)
            row.add_widget(RoundedProgressBar(ratio=ratio, fill_color=color, size_hint_y=None, height=10))
            
            self.prog_rows.add_widget(row)


class BudgetScreen(Screen):
    def __init__(self, app_inst, **kwargs):
        super().__init__(**kwargs)
        self.app = app_inst
        self.inputs_map = {}
        self.build_ui()

    def build_ui(self):
        card = RoundedCard(orientation='vertical', padding=12, spacing=12)
        card.add_widget(Label(text="Add & Deduct Category Budgets", font_size='16sp', bold=True, color=(0.1, 0.1, 0.1, 1), size_hint_y=None, height=24))

        add_box = BoxLayout(orientation='horizontal', spacing=8, size_hint_y=None, height=36)
        self.in_new_cat = RoundedTextInput(hint_text="Category Name")
        self.in_new_bgt = RoundedTextInput(hint_text="Amount to Add")
        btn_add = RoundedButton(text="Add Budget", bg_color=ACCENT_CYAN, size_hint_x=0.35, on_press=self.add_category)

        add_box.add_widget(self.in_new_cat)
        add_box.add_widget(self.in_new_bgt)
        add_box.add_widget(btn_add)
        card.add_widget(add_box)

        deduct_box = BoxLayout(orientation='horizontal', spacing=8, size_hint_y=None, height=36)
        self.spinner_deduct = Spinner(text='Select Category', values=list(self.app.budgets.keys()), size_hint_x=0.35, background_color=(0.9, 0.9, 0.9, 1), color=(0.1, 0.1, 0.1, 1))
        self.in_deduct_amt = RoundedTextInput(hint_text="Amount to Deduct", size_hint_x=0.35)
        btn_deduct = RoundedButton(text="Deduct", bg_color=ACCENT_ORANGE, size_hint_x=0.3, on_press=self.deduct_budget)

        deduct_box.add_widget(self.spinner_deduct)
        deduct_box.add_widget(self.in_deduct_amt)
        deduct_box.add_widget(btn_deduct)
        card.add_widget(deduct_box)

        scroll = ScrollView()
        self.budget_list = BoxLayout(orientation='vertical', spacing=8, size_hint_y=None)
        self.budget_list.bind(minimum_height=self.budget_list.setter('height'))
        scroll.add_widget(self.budget_list)
        
        card.add_widget(scroll)
        
        layout = BoxLayout(padding=12)
        layout.add_widget(card)
        self.add_widget(layout)

    def add_category(self, instance):
        cat = self.in_new_cat.text.strip()
        amt_str = self.in_new_bgt.text.strip()
        try:
            amt = float(amt_str)
            if cat:
                current = self.app.budgets.get(cat, 0.0)
                self.app.budgets[cat] = current + amt
                self.in_new_cat.text = ""
                self.in_new_bgt.text = ""
                self.app.refresh_all()
        except ValueError:
            pass

    def deduct_budget(self, instance):
        cat = self.spinner_deduct.text
        amt_str = self.in_deduct_amt.text.strip()
        if cat in self.app.budgets:
            try:
                amt = float(amt_str)
                self.app.budgets[cat] = max(0.0, self.app.budgets[cat] - amt)
                self.in_deduct_amt.text = ""
                self.app.refresh_all()
            except ValueError:
                pass

    def delete_category(self, cat):
        if cat in self.app.budgets:
            del self.app.budgets[cat]
            self.app.expenses = [e for e in self.app.expenses if e["Category"] != cat]
            self.app.refresh_all()

    def update_single_budget(self, cat, text_value):
        try:
            val = float(text_value)
            self.app.budgets[cat] = val
        except ValueError:
            pass

    def render_budget_screen(self):
        categories = list(self.app.budgets.keys())
        self.spinner_deduct.values = categories
        self.spinner_deduct.text = 'Select Category' if categories else 'No Categories'

        self.budget_list.clear_widgets()
        self.inputs_map.clear()

        for cat, limit in list(self.app.budgets.items()):
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=36, spacing=8)
            lbl = Label(text=cat, bold=True, color=(0.1, 0.1, 0.1, 1), size_hint_x=0.35, halign='left')
            lbl.bind(size=lbl.setter('text_size'))
            row.add_widget(lbl)

            amt_input = RoundedTextInput(text=str(int(limit)), size_hint_x=0.4)
            amt_input.bind(text=lambda inst, val, c=cat: self.update_single_budget(c, val))
            row.add_widget(amt_input)

            btn_del = RoundedButton(text="Remove", bg_color=DANGER_RED, size_hint_x=0.25, on_press=lambda inst, c=cat: self.delete_category(c))
            row.add_widget(btn_del)

            self.budget_list.add_widget(row)


class ChartsScreen(Screen):
    def __init__(self, app_inst, **kwargs):
        super().__init__(**kwargs)
        self.app = app_inst
        
        card = RoundedCard(orientation='vertical', padding=12, spacing=8)
        card.add_widget(Label(text="BUDGET VS. ACTUAL SPENDING (BAR CHART)", font_size='14sp', bold=True, color=(0.1, 0.1, 0.1, 1), size_hint_y=None, height=24))
        
        key_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=20, spacing=12)
        
        k1 = BoxLayout(orientation='horizontal', spacing=4, size_hint_x=None, width=80)
        k1.add_widget(ColorDot(bg_color=ACCENT_CYAN, size_hint=(None, None), size=(12, 12)))
        k1.add_widget(Label(text="Budget", font_size='11sp', color=(0.2, 0.2, 0.2, 1)))
        
        k2 = BoxLayout(orientation='horizontal', spacing=4, size_hint_x=None, width=80)
        k2.add_widget(ColorDot(bg_color=ACCENT_ORANGE, size_hint=(None, None), size=(12, 12)))
        k2.add_widget(Label(text="Actual", font_size='11sp', color=(0.2, 0.2, 0.2, 1)))
        
        key_box.add_widget(k1)
        key_box.add_widget(k2)
        card.add_widget(key_box)

        self.bar_chart = VerticalBarChart()
        card.add_widget(self.bar_chart)

        layout = BoxLayout(padding=12)
        layout.add_widget(card)
        self.add_widget(layout)

    def render_charts_screen(self):
        totals = {}
        for e in self.app.expenses:
            totals[e["Category"]] = totals.get(e["Category"], 0) + e["Amount"]

        categories = list(self.app.budgets.keys())
        self.bar_chart.update_data(categories, self.app.budgets, totals, self.app.currency_symbol)


class SettingsScreen(Screen):
    def __init__(self, app_inst, **kwargs):
        super().__init__(**kwargs)
        self.app = app_inst
        self.build_ui()

    def build_ui(self):
        card = RoundedCard(orientation='vertical', padding=16, spacing=12)
        card.add_widget(Label(text="SETTINGS & PREFERENCES", font_size='16sp', bold=True, color=(0.1, 0.1, 0.1, 1), size_hint_y=None, height=24))

        row1 = BoxLayout(orientation='horizontal', size_hint_y=None, height=36)
        row1.add_widget(Label(text="User Name:", bold=True, color=(0.1, 0.1, 0.1, 1), size_hint_x=0.4))
        self.in_user = RoundedTextInput(text=self.app.user_name)
        row1.add_widget(self.in_user)
        card.add_widget(row1)

        row2 = BoxLayout(orientation='horizontal', size_hint_y=None, height=36)
        row2.add_widget(Label(text="Currency Symbol:", bold=True, color=(0.1, 0.1, 0.1, 1), size_hint_x=0.4))
        self.in_curr = RoundedTextInput(text=self.app.currency_symbol)
        row2.add_widget(self.in_curr)
        card.add_widget(row2)

        btn_save = RoundedButton(text="Save Settings", bg_color=ACCENT_CYAN, size_hint_y=None, height=40, on_press=self.save)
        card.add_widget(btn_save)

        btn_reset = RoundedButton(text="Reset Expenses", bg_color=ACCENT_ORANGE, size_hint_y=None, height=40, on_press=self.reset)
        card.add_widget(btn_reset)
        card.add_widget(Widget())

        layout = BoxLayout(padding=12)
        layout.add_widget(card)
        self.add_widget(layout)

    def save(self, instance):
        self.app.user_name = self.in_user.text.strip()
        self.app.currency_symbol = self.in_curr.text.strip()
        self.app.refresh_all()

    def reset(self, instance):
        self.app.expenses = []
        self.app.refresh_all()


class TreasureBudgetApp(App):
    def build(self):
        self.user_name = "Treasure"
        self.currency_symbol = "₦"

        self.budgets = {
            "Food": 110000.0,
            "Rent": 660000.0,
            "Transport": 45000.0,
            "Utilities": 85000.0,
            "Savings": 150000.0,
            "Entertainment": 50000.0
        }

        self.expenses = [
            {"Category": "Food", "Amount": 43400.0},
            {"Category": "Rent", "Amount": 660000.0},
            {"Category": "Transport", "Amount": 16500.0},
            {"Category": "Utilities", "Amount": 31000.0},
            {"Category": "Entertainment", "Amount": 20000.0}
        ]

        root_layout = BoxLayout(orientation='vertical')

        self.header = BoxLayout(orientation='vertical', size_hint_y=None, height=50, padding=[16, 8])
        self.lbl_welcome = Label(text="", font_size='18sp', bold=True, color=(0.1, 0.1, 0.1, 1), halign='left')
        self.lbl_welcome.bind(size=self.lbl_welcome.setter('text_size'))
        self.header.add_widget(self.lbl_welcome)
        root_layout.add_widget(self.header)

        self.sm = ScreenManager()
        self.screen_dash = DashboardScreen(self, name='Dashboard')
        self.screen_budget = BudgetScreen(self, name='Budget Setup')
        self.screen_charts = ChartsScreen(self, name='Visualization')
        self.screen_settings = SettingsScreen(self, name='Settings')

        self.sm.add_widget(self.screen_dash)
        self.sm.add_widget(self.screen_budget)
        self.sm.add_widget(self.screen_charts)
        self.sm.add_widget(self.screen_settings)

        root_layout.add_widget(self.sm)

        self.nav = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, padding=4, spacing=4)
        
        self.btn_dash = RoundedButton(text="Dashboard", on_press=lambda x: self.switch_screen('Dashboard'))
        self.btn_budget = RoundedButton(text="Budget", on_press=lambda x: self.switch_screen('Budget Setup'))
        self.btn_plus = RoundedButton(text="+", on_press=lambda x: self.switch_screen('Dashboard'))
        self.btn_charts = RoundedButton(text="Charts", on_press=lambda x: self.switch_screen('Visualization'))
        self.btn_settings = RoundedButton(text="Settings", on_press=lambda x: self.switch_screen('Settings'))

        self.nav_buttons = {
            'Dashboard': self.btn_dash,
            'Budget Setup': self.btn_budget,
            'Visualization': self.btn_charts,
            'Settings': self.btn_settings
        }

        self.nav.add_widget(self.btn_dash)
        self.nav.add_widget(self.btn_budget)
        self.nav.add_widget(self.btn_plus)
        self.nav.add_widget(self.btn_charts)
        self.nav.add_widget(self.btn_settings)

        root_layout.add_widget(self.nav)

        self.refresh_all()
        return root_layout

    def update_nav_styles(self):
        current = self.sm.current
        for name, btn in self.nav_buttons.items():
            if name == current:
                btn.set_bg_color(PRIMARY_DARK)
                btn.color = (1, 1, 1, 1)
            else:
                btn.set_bg_color(INACTIVE_NAV)
                btn.color = (0.1, 0.1, 0.1, 1)
        
        self.btn_plus.set_bg_color(PRIMARY_DARK)

    def switch_screen(self, name):
        self.sm.current = name
        Clock.schedule_once(lambda dt: self.refresh_all(), 0)

    def refresh_all(self):
        self.lbl_welcome.text = f"Welcome, {self.user_name}!"
        self.update_nav_styles()
        self.screen_dash.render_dashboard()
        self.screen_budget.render_budget_screen()
        self.screen_charts.render_charts_screen()


if __name__ == "__main__":
    TreasureBudgetApp().run()