from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from .constants import MACHINE_PLANS, MIN_WITHDRAW_USD, PLATFORM_RATE_BRL, DATABASE_FILE
from .core import PlatformState
from .utils import format_brl, format_datetime_br, format_usd, platform_usd_to_brl, read_database


class MiningPlatformApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Plataforma de Mineração Simulada")
        self.geometry("1080x760")
        self.minsize(960, 680)
        self.configure(bg="#f4f6f8")

        self.state = PlatformState()

        self.login_frame = None
        self.main_frame = None

        self.balance_usd_var = tk.StringVar(value=format_usd(0))
        self.balance_brl_var = tk.StringVar(value=format_brl(0))
        self.active_contracts_var = tk.StringVar(value="0")
        self.daily_profit_var = tk.StringVar(value=format_usd(0))
        self.estimated_return_var = tk.StringVar(value=format_usd(0))

        self.deposit_value_var = tk.StringVar(value="")
        self.withdraw_value_var = tk.StringVar(value="")
        self.withdraw_brl_preview_var = tk.StringVar(value=format_brl(0))

        self.contracts_tree: ttk.Treeview | None = None
        self.transactions_tree: ttk.Treeview | None = None

        self._render_login()

    def _render_login(self) -> None:
        if self.main_frame is not None:
            self.main_frame.destroy()

        self.login_frame = ttk.Frame(self, padding=24)
        self.login_frame.pack(fill="both", expand=True)

        card = ttk.Frame(self.login_frame, padding=24)
        card.place(relx=0.5, rely=0.5, anchor="center")

        title = ttk.Label(card, text="Plataforma de Mineração", font=("Segoe UI", 20, "bold"))
        title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))

        subtitle = ttk.Label(
            card,
            text="Acesse seu painel para gerenciar planos, ganhos e saques.",
            font=("Segoe UI", 10),
        )
        subtitle.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 16))

        ttk.Label(card, text="Nome completo").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Label(card, text="E-mail").grid(row=3, column=0, sticky="w", pady=4)
        ttk.Label(card, text="Senha").grid(row=4, column=0, sticky="w", pady=4)

        self.name_entry = ttk.Entry(card, width=35)
        self.email_entry = ttk.Entry(card, width=35)
        self.password_entry = ttk.Entry(card, show="*", width=35)

        self.name_entry.grid(row=2, column=1, pady=4)
        self.email_entry.grid(row=3, column=1, pady=4)
        self.password_entry.grid(row=4, column=1, pady=4)

        login_button = ttk.Button(card, text="Entrar / Criar Conta", command=self._handle_sign_in)
        login_button.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(16, 0))

    def _handle_sign_in(self) -> None:
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        if not name or not email or not password:
            messagebox.showwarning("Campos obrigatórios", "Preencha nome, e-mail e senha para continuar.")
            return

        self.state.sign_in(name=name, email=email)
        self._render_main()
        self._refresh_all()

    def _render_main(self) -> None:
        if self.login_frame is not None:
            self.login_frame.destroy()

        self.main_frame = ttk.Frame(self, padding=16)
        self.main_frame.pack(fill="both", expand=True)

        header = ttk.Frame(self.main_frame)
        header.pack(fill="x", pady=(0, 12))

        user_name = self.state.user["name"] if self.state.user else "Usuário"
        ttk.Label(header, text=f"Olá, {user_name}", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        ttk.Label(
            header,
            text="Sistema de mineração digital simulada",
            font=("IX - UX", 10),
        ).pack(anchor="w")

        notebook = ttk.Notebook(self.main_frame)
        notebook.pack(fill="both", expand=True)

        dashboard_tab = ttk.Frame(notebook, padding=12)
        machines_tab = ttk.Frame(notebook, padding=12)
        deposit_tab = ttk.Frame(notebook, padding=12)
        withdraw_tab = ttk.Frame(notebook, padding=12)
        database_tab = ttk.Frame(notebook, padding=12)

        notebook.add(dashboard_tab, text="Dashboard")
        notebook.add(machines_tab, text="Máquinas")
        notebook.add(deposit_tab, text="Depósito")
        notebook.add(withdraw_tab, text="Saque")
        notebook.add(database_tab, text="Dados (debug)")
    
        

        self._build_dashboard_tab(dashboard_tab)
        self._build_machines_tab(machines_tab)
        self._build_deposit_tab(deposit_tab)
        self._build_withdraw_tab(withdraw_tab)

    def _build_dashboard_tab(self, parent: ttk.Frame) -> None:
        top_card = ttk.LabelFrame(parent, text="Saldo da Plataforma", padding=12)
        top_card.pack(fill="x")

        ttk.Label(top_card, text="Saldo disponível (USD da plataforma):", font=("Segoe UI", 10)).grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(top_card, textvariable=self.balance_usd_var, font=("Segoe UI", 20, "bold")).grid(
            row=1, column=0, sticky="w", pady=(4, 2)
        )
        ttk.Label(top_card, text="Equivalente estimado em BRL:").grid(row=2, column=0, sticky="w")
        ttk.Label(top_card, textvariable=self.balance_brl_var, font=("Segoe UI", 11, "bold")).grid(
            row=3, column=0, sticky="w", pady=(2, 2)
        )
        ttk.Label(top_card, text="Cotação fixa: 1 USD da plataforma = R$ 6,00").grid(
            row=4, column=0, sticky="w", pady=(2, 8)
        )
        ttk.Button(top_card, text="Atualizar rendimentos diários", command=self._handle_apply_earnings).grid(
            row=5, column=0, sticky="w"
        )

        stats = ttk.Frame(parent)
        stats.pack(fill="x", pady=(12, 10))

        stat1 = ttk.LabelFrame(stats, text="Máquinas ativas", padding=10)
        stat2 = ttk.LabelFrame(stats, text="Lucro diário", padding=10)
        stat3 = ttk.LabelFrame(stats, text="Retorno previsto", padding=10)

        stat1.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        stat2.grid(row=0, column=1, sticky="nsew", padx=(0, 8))
        stat3.grid(row=0, column=2, sticky="nsew")

        stats.columnconfigure(0, weight=1)
        stats.columnconfigure(1, weight=1)
        stats.columnconfigure(2, weight=1)

        ttk.Label(stat1, textvariable=self.active_contracts_var, font=("Segoe UI", 16, "bold")).pack(anchor="w")
        ttk.Label(stat2, textvariable=self.daily_profit_var, font=("Segoe UI", 16, "bold")).pack(anchor="w")
        ttk.Label(stat3, textvariable=self.estimated_return_var, font=("Segoe UI", 16, "bold")).pack(anchor="w")

        contracts_box = ttk.LabelFrame(parent, text="Máquinas em andamento", padding=8)
        contracts_box.pack(fill="both", expand=True, pady=(0, 10))

        self.contracts_tree = ttk.Treeview(
            contracts_box,
            columns=("plano", "diario", "restantes", "retorno", "inicio"),
            show="headings",
            height=6,
        )
        for col, title, width in [
            ("plano", "Plano", 180),
            ("diario", "Lucro Diário", 120),
            ("restantes", "Dias Restantes", 120),
            ("retorno", "Retorno Previsto", 140),
            ("inicio", "Início", 160),
        ]:
            self.contracts_tree.heading(col, text=title)
            self.contracts_tree.column(col, width=width, anchor="w")

        self.contracts_tree.pack(fill="both", expand=True)

        tx_box = ttk.LabelFrame(parent, text="Movimentações recentes", padding=8)
        tx_box.pack(fill="both", expand=True)

        self.transactions_tree = ttk.Treeview(
            tx_box,
            columns=("descricao", "valor", "data"),
            show="headings",
            height=7,
        )
        for col, title, width in [
            ("descricao", "Descrição", 360),
            ("valor", "Valor", 110),
            ("data", "Data", 150),
        ]:
            self.transactions_tree.heading(col, text=title)
            self.transactions_tree.column(col, width=width, anchor="w")

        self.transactions_tree.pack(fill="both", expand=True)

    def _build_machines_tab(self, parent: ttk.Frame) -> None:
        ttk.Label(parent, text="Escolha sua máquina virtual", font=("Segoe UI", 16, "bold")).pack(anchor="w")
        ttk.Label(parent, text="Cada plano possui retorno diário fixo e prazo definido.").pack(anchor="w", pady=(0, 10))

        plans_container = ttk.Frame(parent)
        plans_container.pack(fill="both", expand=True)

        for plan in MACHINE_PLANS:
            card = ttk.LabelFrame(plans_container, text=plan.name, padding=12)
            card.pack(fill="x", pady=6)

            ttk.Label(card, text=f"Valor de contratação: {format_usd(plan.contract_value_usd)}").grid(
                row=0, column=0, sticky="w"
            )
            ttk.Label(card, text=f"Prazo de duração: {plan.duration_days} dias").grid(
                row=1, column=0, sticky="w"
            )
            ttk.Label(card, text=f"Lucro diário fixo: {format_usd(plan.daily_profit_usd)}").grid(
                row=2, column=0, sticky="w"
            )
            ttk.Label(card, text=f"Retorno total previsto: {format_usd(plan.total_return_usd)}").grid(
                row=3, column=0, sticky="w", pady=(0, 8)
            )

            ttk.Button(card, text="Contratar máquina", command=lambda p=plan.id: self._handle_buy_machine(p)).grid(
                row=4, column=0, sticky="w"
            )

    def _build_deposit_tab(self, parent: ttk.Frame) -> None:
        ttk.Label(parent, text="Depósito / Ativação de saldo", font=("Segoe UI", 16, "bold")).pack(anchor="w")
        ttk.Label(parent, text=f"Cotação fixa: 1 USD da plataforma = R$ {PLATFORM_RATE_BRL:.2f}").pack(
            anchor="w", pady=(0, 10)
        )

        form = ttk.LabelFrame(parent, text="Adicionar saldo", padding=12)
        form.pack(fill="x")

        ttk.Label(form, text="Valor do depósito (BRL):").grid(row=0, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.deposit_value_var, width=24).grid(row=1, column=0, sticky="w", pady=(4, 10))
        ttk.Button(form, text="Confirmar depósito", command=self._handle_deposit).grid(row=2, column=0, sticky="w")

    def _build_withdraw_tab(self, parent: ttk.Frame) -> None:
        ttk.Label(parent, text="Solicitação de saque", font=("Segoe UI", 16, "bold")).pack(anchor="w")
        ttk.Label(parent, text=f"Valor mínimo para saque: {format_usd(MIN_WITHDRAW_USD)}").pack(
            anchor="w", pady=(0, 10)
        )

        form = ttk.LabelFrame(parent, text="Solicitar saque", padding=12)
        form.pack(fill="x")

        ttk.Label(form, text="Valor do saque (USD da plataforma):").grid(row=0, column=0, sticky="w")
        withdraw_entry = ttk.Entry(form, textvariable=self.withdraw_value_var, width=24)
        withdraw_entry.grid(row=1, column=0, sticky="w", pady=(4, 4))
        withdraw_entry.bind("<KeyRelease>", self._refresh_withdraw_preview)

        ttk.Label(form, text="Equivalente estimado em BRL:").grid(row=2, column=0, sticky="w")
        ttk.Label(form, textvariable=self.withdraw_brl_preview_var, font=("Segoe UI", 10, "bold")).grid(
            row=3, column=0, sticky="w", pady=(2, 8)
        )

        ttk.Button(form, text="Solicitar saque", command=self._handle_withdraw).grid(row=4, column=0, sticky="w")

    def _parse_amount(self, raw_value: str) -> float:
        normalized = raw_value.strip().replace(".", "").replace(",", ".")
        if not normalized:
            return 0.0
        try:
            return float(normalized)
        except ValueError:
            return 0.0

    def _refresh_withdraw_preview(self, _event=None) -> None:
        value_usd = self._parse_amount(self.withdraw_value_var.get())
        preview = platform_usd_to_brl(value_usd, PLATFORM_RATE_BRL)
        self.withdraw_brl_preview_var.set(format_brl(preview))

    def _handle_apply_earnings(self) -> None:
        credited = self.state.apply_daily_earnings()
        self._refresh_all()
        if credited > 0:
            messagebox.showinfo("Rendimentos atualizados", f"Crédito aplicado: {format_usd(credited)}")
        else:
            messagebox.showinfo("Sem novos créditos", "Não houve novos rendimentos para creditar hoje.")

    def _handle_buy_machine(self, plan_id: str) -> None:
        ok, message = self.state.buy_machine(plan_id)
        self._refresh_all()
        if ok:
            messagebox.showinfo("Sucesso", message)
        else:
            messagebox.showwarning("Não foi possível contratar", message)

    def _handle_deposit(self) -> None:
        amount_brl = self._parse_amount(self.deposit_value_var.get())
        if amount_brl <= 0:
            messagebox.showwarning("Valor inválido", "Informe um valor de depósito maior que zero.")
            return

        self.state.add_deposit_brl(amount_brl)
        self.deposit_value_var.set("")
        self._refresh_all()
        messagebox.showinfo("Depósito confirmado", "O saldo foi creditado com sucesso.")

    def _handle_withdraw(self) -> None:
        amount_usd = self._parse_amount(self.withdraw_value_var.get())
        ok, message = self.state.request_withdraw_usd(amount_usd)
        self._refresh_all()

        if ok:
            self.withdraw_value_var.set("")
            self._refresh_withdraw_preview()
            messagebox.showinfo("Solicitação enviada", message)
        else:
            messagebox.showwarning("Saque não solicitado", message)

    def _refresh_all(self) -> None:
        self.balance_usd_var.set(format_usd(self.state.wallet_usd))
        self.balance_brl_var.set(format_brl(platform_usd_to_brl(self.state.wallet_usd, PLATFORM_RATE_BRL)))
        self.active_contracts_var.set(str(len(self.state.active_contracts)))
        self.daily_profit_var.set(format_usd(self.state.total_daily_profit_usd))
        self.estimated_return_var.set(format_usd(self.state.estimated_portfolio_return_usd))

        if self.contracts_tree is not None:
            for row in self.contracts_tree.get_children():
                self.contracts_tree.delete(row)

            for contract in self.state.active_contracts:
                remaining_days = contract.duration_days - contract.days_paid
                total_return = contract.duration_days * contract.daily_profit_usd
                self.contracts_tree.insert(
                    "",
                    "end",
                    values=(
                        contract.plan_name,
                        format_usd(contract.daily_profit_usd),
                        remaining_days,
                        format_usd(total_return),
                        format_datetime_br(contract.start_date),
                    ),
                )

        if self.transactions_tree is not None:
            for row in self.transactions_tree.get_children():
                self.transactions_tree.delete(row)

            for tx in self.state.transactions[:15]:
                signal = "+" if tx.amount_usd >= 0 else "-"
                self.transactions_tree.insert(
                    "",
                    "end",
                    values=(
                        tx.description,
                        f"{signal}{format_usd(abs(tx.amount_usd))}",
                        format_datetime_br(tx.created_at),
                    ),
                )
    
    class DatabaseTab(ttk.Frame):
        def __init__(self, parent: ttk.Frame, state: PlatformState) -> None:
            super().__init__(parent, padding=12)
            self.parent = parent
            self.state = state
            self._build_ui()

        def _build_ui(self) -> None:
            ttk.Label(self, text="Dados atuais da plataforma (debug)", font=("Segoe UI", 16, "bold")).pack(anchor="w")

            data_text = tk.Text(self, wrap="none", height=20)
            data_text.pack(fill="both", expand=True)

            database_content = read_database(DATABASE_FILE)
            database_content = f"Usuário:\n{self.state.user}\n\nMáquinas ativas:\n"
            for contract in self.state.active_contracts:    [
                database_content += f"- {contract.plan_name} (início: {format_datetime_br(contract.start_date)}, dias pagos: {contract.days_paid}/{contract.duration_days})\n"
            ]
            data_text.insert("1.0", database_content)
            data_text.configure(state="disabled", font=("Courier New", 10))


def run() -> None:
    app = MiningPlatformApp()
    app.mainloop()
