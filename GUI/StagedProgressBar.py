import tkinter as tk
from tkinter import ttk
import uuid


def ensure_colour_friendly_theme(root: tk.Tk) -> None:
    style = ttk.Style(root)
    if style.theme_use() != "clam":
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass


class StagedProgress(ttk.Frame):
    """
    Single-row widget:
      [Title]  [Progressbar.................]  [value/total]

    IMPORTANT:
    - Supports passing style="SomeStyle.Horizontal.TProgressbar" (your code does this).
      That 'style' is applied to the Progressbar, not the Frame.
    """
    def __init__(
        self,
        parent,
        title="",
        stages=5,
        length=180,              # requested length only; grid will stretch it
        show_value=True,
        bar_color="#4A90E2",
        trough_color="#D9D9D9",
        title_padx=(0, 6),
        value_padx=(6, 0),
        **kwargs
    ):
        # You pass style=... from your UI. That must NOT go to ttk.Frame.
        progressbar_style = kwargs.pop("style", None)

        super().__init__(parent, **kwargs)

        if stages < 1:
            raise ValueError("stages must be >= 1")

        self.stages = int(stages)
        self.var = tk.IntVar(value=0)

        self._bar_color = bar_color
        self._trough_color = trough_color

        # ---- Title (col 0) ----
        self.title_var = tk.StringVar(value=title)
        self.title_label = ttk.Label(self, textvariable=self.title_var)
        self.title_label.grid(row=0, column=0, sticky="w", padx=title_padx)

        # ---- Style ----
        # If caller provided a style name, use that as-is (your code configures thickness/colors).
        # Otherwise create an internal style.
        self._style = ttk.Style(self)
        if progressbar_style is not None:
            self._style_name = progressbar_style
        else:
            self._style_name = f"StagedPB.{uuid.uuid4().hex}.Horizontal.TProgressbar"
            self._apply_style()

        # ---- Progressbar (col 1) ----
        self.bar = ttk.Progressbar(
            self,
            orient="horizontal",
            mode="determinate",
            maximum=self.stages,
            variable=self.var,
            style=self._style_name,
            length=length,   # initial requested length
        )
        self.bar.grid(row=0, column=1, sticky="ew")

        # ---- Value label (col 2) ----
        self.value_label = None
        if show_value:
            self.value_var = tk.StringVar()
            self.value_label = ttk.Label(self, textvariable=self.value_var, width=6, anchor="e")
            self.value_label.grid(row=0, column=2, sticky="e", padx=value_padx)
            self._sync_value()

        # Make the bar column expand to fill all available space
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=0)

    def _apply_style(self) -> None:
        self._style.configure(
            self._style_name,
            background=self._bar_color,
            troughcolor=self._trough_color,
            bordercolor=self._trough_color,
            lightcolor=self._bar_color,
            darkcolor=self._bar_color,
        )

    def set_colors(self, bar_color=None, trough_color=None) -> None:
        # Only applies if using internal style; if an external style was passed in,
        # it should be configured by the caller.
        if bar_color is not None:
            self._bar_color = bar_color
        if trough_color is not None:
            self._trough_color = trough_color

        # If style name looks like ours, we control it. Otherwise leave it alone.
        if self._style_name.startswith("StagedPB."):
            self._apply_style()

    def set_title(self, title: str) -> None:
        self.title_var.set(title)

    def _sync_value(self) -> None:
        if self.value_label is not None:
            self.value_var.set(f"{self.var.get()}/{self.stages}")

    def set_stage(self, stage: int) -> None:
        stage = max(0, min(self.stages, int(stage)))
        self.var.set(stage)
        self._sync_value()

    def next_stage(self) -> None:
        self.set_stage(self.var.get() + 1)

    def reset(self) -> None:
        self.set_stage(0)


# --- demo ---
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Compact Discrete Progress Bars")

    ensure_colour_friendly_theme(root)

    outer = ttk.Frame(root, padding=12)
    outer.pack(fill="both", expand=True)

    p = StagedProgress(outer, title="Taxi", stages=10, show_value=True)
    p.pack(fill="x", expand=True)

    controls = ttk.Frame(outer)
    controls.pack(anchor="w", pady=(10, 0))
    ttk.Button(controls, text="+1", command=p.next_stage).pack(side="left")
    ttk.Button(controls, text="Reset", command=p.reset).pack(side="left", padx=(6, 0))

    root.mainloop()
