"""
============================================================
  LinkedIn Job Scraper — Desktop App
  UI: CustomTkinter | Dark Theme | Times New Roman
============================================================
"""

import os
import sys
import time
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime, timezone, timedelta
from urllib.parse import quote
import customtkinter as ctk

# ── App Theme ──
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ── Constants ──
APIFY_ACTOR = "curious_coder/linkedin-jobs-scraper"
APIFY_RUN_URL = f"https://api.apify.com/v2/acts/{APIFY_ACTOR.replace('/', '~')}/runs"
JOB_TYPE_CODE = "F"

FONT_TITLE   = ("Anthropic Sans", 28, "bold")
FONT_LABEL   = ("Anthropic Sans", 16)
FONT_SMALL   = ("Anthropic Sans", 14)
FONT_LOG     = ("Courier New", 13)
FONT_BTN     = ("Anthropic Sans", 16, "bold")
FONT_SECTION = ("Anthropic Sans", 18, "bold")

COUNTRIES = [
    "United States", "United Kingdom", "Canada", "Australia",
    "Germany", "India", "Singapore", "Netherlands", "France"
]
COUNTRY_CODES = {
    "United States": "US", "United Kingdom": "GB", "Canada": "CA",
    "Australia": "AU", "Germany": "DE", "India": "IN",
    "Singapore": "SG", "Netherlands": "NL", "France": "FR"
}
WORK_TYPES = ["Remote", "Hybrid", "On-site", "Any"]
WORK_TYPE_CODES = {"Remote": "2", "Hybrid": "3", "On-site": "1", "Any": None}
MAX_JOBS_OPTIONS = ["25", "50", "75", "100"]

# ── Colors ──
BG_MAIN    = "#1a1a1a"
BG_CARD    = "#242424"
BG_INPUT   = "#2e2e2e"
ACCENT     = "#d97706"
ACCENT2    = "#f59e0b"
TEXT_PRI   = "#f5f5f0"
TEXT_SEC   = "#a8a8a0"
TEXT_MUT   = "#6b6b65"
SUCCESS    = "#4ade80"
ERROR      = "#f87171"
WARN       = "#fbbf24"
BORDER     = "#3a3a3a"


class LinkedInScraperApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("LinkedIn Job Scraper")
        self.geometry("1200x900")
        self.minsize(1000, 800)
        self.configure(fg_color=BG_MAIN)

        self._jobs_data = None
        self._is_scraping = False

        self._build_ui()

    # ─────────────────────────────────────────
    #  UI Construction
    # ─────────────────────────────────────────

    def _build_ui(self):
        # ── Header ──
        header = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=0, height=80)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="LinkedIn Job Scraper",
            font=FONT_TITLE,
            text_color=TEXT_PRI
        ).pack(side="left", padx=28, pady=16)

        ctk.CTkLabel(
            header,
            text="Job search made easier",
            font=FONT_SMALL,
            text_color=TEXT_MUT
        ).pack(side="right", padx=28, pady=16)

        # ── Thin accent line ──
        accent_bar = ctk.CTkFrame(self, fg_color=ACCENT, height=2, corner_radius=0)
        accent_bar.pack(fill="x")

        # ── Main body: left config + right log ──
        body = ctk.CTkFrame(self, fg_color=BG_MAIN)
        body.pack(fill="both", expand=True, padx=0, pady=0)
        body.columnconfigure(0, weight=4)
        body.columnconfigure(1, weight=5)
        body.rowconfigure(0, weight=1)

        self._build_config_panel(body)
        self._build_log_panel(body)

    def _build_config_panel(self, parent):
        panel = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=0)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 1), pady=0)

        scroll = ctk.CTkScrollableFrame(panel, fg_color=BG_CARD, scrollbar_button_color=BORDER)
        scroll.pack(fill="both", expand=True, padx=0, pady=0)

        pad = {"padx": 24}

        # ── Section: Credentials ──
        self._section_label(scroll, "API Credentials")

        self._field_label(scroll, "Apify API Key")
        self.api_key_var = ctk.StringVar()
        self.api_key_entry = ctk.CTkEntry(
            scroll, textvariable=self.api_key_var,
            show="•", height=46, corner_radius=6,
            fg_color=BG_INPUT, border_color=BORDER, border_width=1,
            text_color=TEXT_PRI, font=FONT_SMALL
        )
        self.api_key_entry.pack(fill="x", **pad, pady=(0, 6))

        self._toggle_btn = ctk.CTkButton(
            scroll, text="Show Key", width=90, height=26,
            fg_color="transparent", border_color=BORDER, border_width=1,
            text_color=TEXT_SEC, font=FONT_SMALL, corner_radius=4,
            hover_color=BG_INPUT, command=self._toggle_key_visibility
        )
        self._toggle_btn.pack(anchor="e", padx=24, pady=(0, 16))

        # ── Section: Search Parameters ──
        self._section_label(scroll, "Search Parameters")

        self._field_label(scroll, "Job Role")
        self.role_var = ctk.StringVar(value="")
        ctk.CTkEntry(
            scroll, textvariable=self.role_var,
            height=46, corner_radius=6,
            fg_color=BG_INPUT, border_color=BORDER, border_width=1,
            text_color=TEXT_PRI, font=FONT_SMALL
        ).pack(fill="x", **pad, pady=(0, 14))

        self._field_label(scroll, "Country")
        self.country_var = ctk.StringVar(value="")
        ctk.CTkOptionMenu(
            scroll, variable=self.country_var, values=COUNTRIES,
            height=46, corner_radius=6,
            fg_color=BG_INPUT, button_color=ACCENT, button_hover_color=ACCENT2,
            text_color=TEXT_PRI, font=FONT_SMALL, dropdown_font=FONT_SMALL,
            dropdown_fg_color=BG_CARD, dropdown_text_color=TEXT_PRI,
            dropdown_hover_color=BG_INPUT
        ).pack(fill="x", **pad, pady=(0, 14))

        self._field_label(scroll, "Work Type")
        self.work_type_var = ctk.StringVar(value="")
        ctk.CTkOptionMenu(
            scroll, variable=self.work_type_var, values=WORK_TYPES,
            height=46, corner_radius=6,
            fg_color=BG_INPUT, button_color=ACCENT, button_hover_color=ACCENT2,
            text_color=TEXT_PRI, font=FONT_SMALL, dropdown_font=FONT_SMALL,
            dropdown_fg_color=BG_CARD, dropdown_text_color=TEXT_PRI,
            dropdown_hover_color=BG_INPUT
        ).pack(fill="x", **pad, pady=(0, 14))

        self._field_label(scroll, "Max Jobs to Scrape")
        self.max_jobs_var = ctk.StringVar(value="")
        ctk.CTkOptionMenu(
            scroll, variable=self.max_jobs_var, values=MAX_JOBS_OPTIONS,
            height=46, corner_radius=6,
            fg_color=BG_INPUT, button_color=ACCENT, button_hover_color=ACCENT2,
            text_color=TEXT_PRI, font=FONT_SMALL, dropdown_font=FONT_SMALL,
            dropdown_fg_color=BG_CARD, dropdown_text_color=TEXT_PRI,
            dropdown_hover_color=BG_INPUT
        ).pack(fill="x", **pad, pady=(0, 22))

        # ── Divider ──
        ctk.CTkFrame(scroll, fg_color=BORDER, height=1, corner_radius=0).pack(fill="x", padx=24, pady=(0, 22))

        # ── Scrape Button ──
        self.scrape_btn = ctk.CTkButton(
            scroll, text="Start Scraping",
            height=52, corner_radius=6,
            fg_color=ACCENT, hover_color=ACCENT2,
            text_color="#0f0f0f", font=FONT_BTN,
            command=self._start_scraping
        )
        self.scrape_btn.pack(fill="x", padx=24, pady=(0, 12))

        # ── Download Button ──
        self.download_btn = ctk.CTkButton(
            scroll, text="Download Excel",
            height=52, corner_radius=6,
            fg_color=BG_INPUT, hover_color="#3a3a3a",
            text_color=TEXT_MUT, font=FONT_BTN,
            border_color=BORDER, border_width=1,
            state="disabled",
            command=self._download_excel
        )
        self.download_btn.pack(fill="x", padx=24, pady=(0, 24))

        # ── Status bar ──
        self.status_var = ctk.StringVar(value="")
        self.status_label = ctk.CTkLabel(
            panel, textvariable=self.status_var,
            font=FONT_SMALL, text_color=TEXT_MUT,
            anchor="w"
        )
        self.status_label.pack(fill="x", padx=24, pady=(0, 12))

    def _build_log_panel(self, parent):
        panel = ctk.CTkFrame(parent, fg_color=BG_MAIN, corner_radius=0)
        panel.grid(row=0, column=1, sticky="nsew", pady=0)
        panel.rowconfigure(1, weight=1)
        panel.columnconfigure(0, weight=1)

        log_header = ctk.CTkFrame(panel, fg_color=BG_CARD, corner_radius=0, height=44)
        log_header.grid(row=0, column=0, sticky="ew")
        log_header.grid_propagate(False)

        ctk.CTkLabel(
            log_header, text="Activity Log",
            font=FONT_SECTION, text_color=TEXT_PRI, anchor="w"
        ).pack(side="left", padx=20, pady=10)

        clear_btn = ctk.CTkButton(
            log_header, text="Clear", width=64, height=26,
            fg_color="transparent", border_color=BORDER, border_width=1,
            text_color=TEXT_SEC, font=FONT_SMALL, corner_radius=4,
            hover_color=BG_INPUT, command=self._clear_log
        )
        clear_btn.pack(side="right", padx=16, pady=9)

        self.log_box = tk.Text(
            panel,
            bg="#111111", fg=TEXT_PRI,
            font=FONT_LOG,
            relief="flat", bd=0,
            wrap="word",
            state="disabled",
            cursor="arrow",
            selectbackground=ACCENT,
            insertbackground=TEXT_PRI,
            padx=16, pady=12
        )
        self.log_box.grid(row=1, column=0, sticky="nsew")

        self.log_box.tag_config("info",    foreground=TEXT_SEC)
        self.log_box.tag_config("success", foreground=SUCCESS)
        self.log_box.tag_config("error",   foreground=ERROR)
        self.log_box.tag_config("warn",    foreground=WARN)
        self.log_box.tag_config("accent",  foreground=ACCENT2)
        self.log_box.tag_config("dim",     foreground=TEXT_MUT)

        scrollbar = ctk.CTkScrollbar(panel, command=self.log_box.yview, button_color=BORDER)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.log_box.configure(yscrollcommand=scrollbar.set)

    # ─────────────────────────────────────────
    #  Helper UI builders
    # ─────────────────────────────────────────

    def _section_label(self, parent, text):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=24, pady=(20, 8))
        ctk.CTkLabel(frame, text=text, font=FONT_SECTION, text_color=ACCENT2, anchor="w").pack(side="left")
        ctk.CTkFrame(frame, fg_color=BORDER, height=1).pack(side="left", fill="x", expand=True, padx=(10, 0), pady=7)

    def _field_label(self, parent, text):
        ctk.CTkLabel(
            parent, text=text,
            font=FONT_LABEL, text_color=TEXT_SEC, anchor="w"
        ).pack(fill="x", padx=24, pady=(0, 6))

    def _toggle_key_visibility(self):
        current = self.api_key_entry.cget("show")
        if current == "•":
            self.api_key_entry.configure(show="")
            self._toggle_btn.configure(text="Hide Key")
        else:
            self.api_key_entry.configure(show="•")
            self._toggle_btn.configure(text="Show Key")

    # ─────────────────────────────────────────
    #  Logging
    # ─────────────────────────────────────────

    def _log(self, msg, tag="info"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"[{timestamp}]  ", "dim")
        self.log_box.insert("end", f"{msg}\n", tag)
        self.log_box.configure(state="disabled")
        self.log_box.see("end")

    def _clear_log(self):
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

    def _set_status(self, text, color=TEXT_MUT):
        self.status_var.set(text)
        self.status_label.configure(text_color=color)

    # ─────────────────────────────────────────
    #  Scraping Logic
    # ─────────────────────────────────────────

    def _start_scraping(self):
        if self._is_scraping:
            return

        api_key = self.api_key_var.get().strip()
        role    = self.role_var.get().strip()
        country = self.country_var.get()
        work    = self.work_type_var.get()
        max_j   = int(self.max_jobs_var.get())

        if not api_key:
            self._log("API key is required.", "error")
            return
        if not role:
            self._log("Job role cannot be empty.", "error")
            return

        self._jobs_data = None
        self.download_btn.configure(state="disabled", text_color=TEXT_MUT, fg_color=BG_INPUT)
        self._is_scraping = True
        self.scrape_btn.configure(state="disabled", text="Scraping…")
        self._set_status("Running…", ACCENT2)

        thread = threading.Thread(target=self._scrape_thread, args=(api_key, role, country, work, max_j), daemon=True)
        thread.start()

    def _scrape_thread(self, api_key, role, country, work_type_label, max_jobs):
        import requests

        try:
            self._log(f"Starting search — {role} | {country} | {work_type_label} | Max {max_jobs}", "accent")

            country_code = COUNTRY_CODES.get(country, country)
            work_code    = WORK_TYPE_CODES.get(work_type_label)
            url = self._build_url(role, country, work_code)

            self._log(f"LinkedIn URL built.", "info")
            self._log(f"Sending request to Apify…", "info")

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            }
            payload = {"urls": [url], "count": max_jobs, "scrapeCompany": False}

            resp = requests.post(APIFY_RUN_URL, headers=headers, json=payload, timeout=30)
            if resp.status_code not in (200, 201):
                self._log(f"Apify error {resp.status_code}: {resp.text[:200]}", "error")
                return

            run_data   = resp.json()
            run_id     = run_data["data"]["id"]
            dataset_id = run_data["data"]["defaultDatasetId"]
            self._log(f"Scraper started. Run ID: {run_id}", "success")
            self._log("Waiting for results…", "info")

            status_url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={api_key}"
            for i in range(120):
                time.sleep(3)
                r = requests.get(status_url, timeout=15)
                status = r.json()["data"]["status"]
                if i % 5 == 0:
                    self._log(f"Status: {status} (polling…)", "dim")
                if status == "SUCCEEDED":
                    self._log("Apify run completed successfully.", "success")
                    break
                elif status in ("FAILED", "ABORTED", "TIMED-OUT"):
                    self._log(f"Run ended with status: {status}", "error")
                    return
            else:
                self._log("Timed out waiting for Apify.", "error")
                return

            items_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={api_key}&limit=100&format=json"
            r = requests.get(items_url, timeout=30)
            raw_jobs = r.json()
            self._log(f"Retrieved {len(raw_jobs)} raw listings from LinkedIn.", "info")

            jobs = self._filter_and_clean(raw_jobs, work_type_label)
            self._log(f"{len(jobs)} jobs match filters (last 24 hrs, {work_type_label}, Full-time).", "success")
            self._log(f"With salary: {sum(1 for j in jobs if j['has_salary'])}   |   Without salary: {sum(1 for j in jobs if not j['has_salary'])}", "info")

            if not jobs:
                self._log("No matching jobs found. Try a broader search.", "warn")
                return

            self._jobs_data = {
                "jobs": jobs,
                "role": role,
                "country": country,
                "work_type": work_type_label
            }

            self._log("Results ready. Click Download Excel to save.", "accent")
            self.after(0, self._enable_download)

        except Exception as e:
            self._log(f"Unexpected error: {e}", "error")
        finally:
            self._is_scraping = False
            self.after(0, lambda: self.scrape_btn.configure(state="normal", text="Start Scraping"))
            self.after(0, lambda: self._set_status("Done", SUCCESS))

    def _build_url(self, role, country_name, work_type_code):
        base = "https://www.linkedin.com/jobs/search/?"
        params = f"keywords={quote(role)}&location={quote(country_name)}"
        params += f"&f_JT={JOB_TYPE_CODE}&f_TPR=r86400"
        if work_type_code:
            params += f"&f_WT={work_type_code}"
        params += "&position=1&pageNum=0"
        return base + params

    def _filter_and_clean(self, jobs, work_type_label):
        import re
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        cleaned = []

        for job in jobs:
            posted_str = job.get("postedAt", "")
            try:
                posted_dt = datetime.fromisoformat(posted_str.replace("Z", "+00:00"))
                if posted_dt < cutoff:
                    continue
                posted_display = posted_dt.strftime("%Y-%m-%d %H:%M UTC")
            except Exception:
                posted_display = posted_str[:10] if posted_str else "Unknown"

            salary = job.get("salary", "").strip()
            if not salary:
                patterns = [
                    r'\$[\d,]+(?:\.\d+)?(?:\s*[-–]\s*\$[\d,]+(?:\.\d+)?)?\s*(?:/yr|/year|per year|annually)',
                    r'\$[\d,]+(?:\.\d+)?(?:\s*[-–]\s*\$[\d,]+(?:\.\d+)?)?\s*(?:/hr|/hour|per hour|hourly)',
                    r'\$[\d,]+(?:k|K)(?:\s*[-–]\s*\$[\d,]+(?:k|K)?)?',
                ]
                for pat in patterns:
                    m = re.search(pat, job.get("descriptionText", "") or "", re.IGNORECASE)
                    if m:
                        salary = m.group(0).strip()
                        break

            salary_display = salary if salary else "Not Listed"
            workplace_types = job.get("workplaceTypes", [])
            work_type_actual = ", ".join(workplace_types) if workplace_types else (
                "Remote" if job.get("workRemoteAllowed") else work_type_label
            )

            cleaned.append({
                "title":      job.get("title", "N/A"),
                "company":    job.get("companyName", "N/A"),
                "location":   job.get("location", "N/A"),
                "work_type":  work_type_actual,
                "employment": job.get("employmentType", "Full-time"),
                "salary":     salary_display,
                "posted":     posted_display,
                "seniority":  job.get("seniorityLevel", "N/A"),
                "industry":   job.get("industries", "N/A"),
                "link":       job.get("link", ""),
                "apply_url":  job.get("applyUrl", ""),
                "has_salary": salary_display != "Not Listed",
            })
        return cleaned

    def _enable_download(self):
        self.download_btn.configure(
            state="normal",
            fg_color=SUCCESS,
            text_color="#0f0f0f",
            hover_color="#22c55e",
            text="Download Excel"
        )

    # ─────────────────────────────────────────
    #  Download Excel
    # ─────────────────────────────────────────

    def _download_excel(self):
        if not self._jobs_data:
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")],
            initialfile=f"LinkedIn_Jobs_{self._jobs_data['role'].replace(' ', '_')}_{datetime.now().strftime('%d%b%Y')}.xlsx",
            title="Save Excel Report"
        )
        if not path:
            return

        self._log(f"Saving Excel to: {path}", "info")
        try:
            self._write_excel(path)
            self._log(f"Excel saved successfully.", "success")
            messagebox.showinfo("Saved", f"File saved to:\n{path}")
        except Exception as e:
            self._log(f"Failed to save Excel: {e}", "error")
            messagebox.showerror("Error", str(e))

    def _write_excel(self, output_path):
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.utils import get_column_letter

        jobs         = self._jobs_data["jobs"]
        role         = self._jobs_data["role"]
        country_name = self._jobs_data["country"]
        work_type    = self._jobs_data["work_type"]

        wb = Workbook()
        ws = wb.active
        ws.title = f"{role[:20]} Jobs"

        # ── Colors ──
        COLOR_HEADER_BG = "2D2D2D"
        COLOR_HEADER_FG = "FFFFFF"
        COLOR_SUBHEADER = "F2F2F2"
        COLOR_ALT_ROW   = "F9F9F9"
        COLOR_WHITE     = "FFFFFF"
        COLOR_MUTED     = "999999"
        COLOR_LINK      = "1155CC"

        thin   = Side(style="thin", color="DDDDDD")
        border = Border(left=thin, right=thin, top=thin, bottom=thin)

        def style_cell(cell, bold=False, size=10, bg=None, align="left",
                       wrap=False, italic=False, underline=False, color=None):
            cell.font = Font(
                name="Arial", size=size, bold=bold, italic=italic,
                underline="single" if underline else None,
                color=color or "000000"
            )
            if bg:
                cell.fill = PatternFill("solid", start_color=bg)
            cell.alignment = Alignment(horizontal=align, vertical="center", wrap_text=wrap)
            cell.border = border

        # ── Row 1: Title ──
        ws.row_dimensions[1].height = 32
        ws.merge_cells("A1:M1")
        title = ws["A1"]
        title.value = f"{role}  ·  {country_name}  ·  {work_type}  ·  Scraped {datetime.now().strftime('%d %b %Y')}"
        style_cell(title, bold=True, size=13, bg=COLOR_HEADER_BG, align="center", color=COLOR_HEADER_FG)

        # ── Row 2: Meta summary ──
        ws.row_dimensions[2].height = 22
        meta = [
            ("Total Jobs",     len(jobs)),
            ("With Salary",    sum(1 for j in jobs if j["has_salary"])),
            ("Without Salary", sum(1 for j in jobs if not j["has_salary"])),
            ("Employment",     "Full-time"),
            ("Period",         "Last 24 Hours"),
        ]
        col = 1
        for label, val in meta:
            lc = ws.cell(row=2, column=col, value=label)
            style_cell(lc, bold=True, size=9, bg=COLOR_SUBHEADER, align="center", color="555555")
            vc = ws.cell(row=2, column=col + 1, value=val)
            style_cell(vc, size=9, bg=COLOR_SUBHEADER, align="center")
            col += 2
        for c in range(col, 14):
            style_cell(ws.cell(row=2, column=c), bg=COLOR_SUBHEADER)

        # ── Row 3: Spacer ──
        ws.row_dimensions[3].height = 6
        for c in range(1, 14):
            ws.cell(row=3, column=c).fill = PatternFill("solid", start_color="EEEEEE")

        # ── Row 4: Column Headers ──
        ws.row_dimensions[4].height = 30
        columns = [
            ("#",            4),
            ("Job Title",   28),
            ("Company",     20),
            ("Location",    18),
            ("Work Mode",   13),
            ("Job Type",    13),
            ("Salary",      22),
            ("Posted",      14),
            ("Seniority",   15),
            ("Industry",    18),
            ("HR Email",    26),
            ("LinkedIn URL",38),
            ("Apply URL",   28),
        ]
        for i, (name, width) in enumerate(columns, 1):
            cell = ws.cell(row=4, column=i, value=name)
            style_cell(cell, bold=True, size=10, bg=COLOR_HEADER_BG,
                       align="center", color=COLOR_HEADER_FG)
            ws.column_dimensions[get_column_letter(i)].width = width

        # ── Data Rows ──
        for idx, job in enumerate(jobs, 1):
            row = idx + 4
            ws.row_dimensions[row].height = 30
            bg = COLOR_WHITE if idx % 2 == 0 else COLOR_ALT_ROW

            values = [
                idx,
                job["title"],
                job["company"],
                job["location"],
                job["work_type"],
                job["employment"],
                job["salary"],
                job["posted"],
                job["seniority"],
                job["industry"],
                "",                 # HR Email — fill manually
                job["link"],
                job["apply_url"],
            ]

            for col, val in enumerate(values, 1):
                cell = ws.cell(row=row, column=col, value=val)

                if col == 1:
                    style_cell(cell, size=9, bg=bg, align="center", color="777777")
                elif col == 7:
                    has_sal = job["has_salary"]
                    style_cell(cell, size=9, bg=bg, bold=has_sal, italic=not has_sal,
                               color="1A7A3C" if has_sal else COLOR_MUTED)
                elif col == 11:
                    style_cell(cell, size=9, bg="FFFDE7", align="left")
                elif col in (12, 13):
                    style_cell(cell, size=9, bg=bg, underline=bool(val),
                               color=COLOR_LINK if val else COLOR_MUTED)
                else:
                    style_cell(cell, size=9, bg=bg, wrap=(col == 2))

        # ── Freeze & Filter ──
        ws.freeze_panes = "B5"
        ws.auto_filter.ref = f"A4:M{len(jobs) + 4}"

        wb.save(output_path)


# ─────────────────────────────────────────
#  Entry Point
# ─────────────────────────────────────────

if __name__ == "__main__":
    app = LinkedInScraperApp()
    app.mainloop()