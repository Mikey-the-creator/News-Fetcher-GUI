import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from news_fetcher import NewsFetcher
import webbrowser

class NewsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("📰 News Fetcher")
        self.root.geometry("850x600")
        self.root.configure(bg="#f5f6fa")
        self.fetcher = NewsFetcher()

        style = ttk.Style()
        style.theme_use("clam")

        # Headline style
        title_label = ttk.Label(root, text="News Fetcher", font=("Segoe UI", 20, "bold"))
        title_label.pack(pady=10)

        # ====== Input Frame ======
        input_frame = ttk.LabelFrame(root, text=" Search Filters ", padding=15)
        input_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(input_frame, text="Keyword:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.keyword_entry = ttk.Entry(input_frame, width=30)
        self.keyword_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Source (optional):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.source_entry = ttk.Entry(input_frame, width=30)
        self.source_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="From Date:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.date_entry = DateEntry(input_frame, width=28, background="darkblue",
                                    foreground="white", borderwidth=2,
                                    date_pattern="yyyy-mm-dd")
        self.date_entry.grid(row=2, column=1, padx=5, pady=5)

        # ====== Button Frame ======
        btn_frame = ttk.Frame(root)
        btn_frame.pack(pady=10)

        fetch_btn = ttk.Button(btn_frame, text="🔍 Fetch News", command=self.fetch_news)
        fetch_btn.grid(row=0, column=0, padx=10)

        save_btn = ttk.Button(btn_frame, text="💾 Save to CSV", command=self.save_news)
        save_btn.grid(row=0, column=1, padx=10)

        read_btn = ttk.Button(btn_frame, text="📖 Read Selected", command=self.read_selected)
        read_btn.grid(row=0, column=2, padx=10)

        # ====== Results Frame ======
        results_frame = ttk.LabelFrame(root, text=" Results ", padding=10)
        results_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("Title", "Source", "Date")
        self.tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=15)
        self.tree.heading("Title", text="Title")
        self.tree.heading("Source", text="Source")
        self.tree.heading("Date", text="Date")

        self.tree.column("Title", width=500, anchor="w")
        self.tree.column("Source", width=150, anchor="center")
        self.tree.column("Date", width=150, anchor="center")

        # Zebra striping for rows
        style.configure("Treeview", rowheight=25, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))
        style.map("Treeview", background=[("selected", "#2980b9")], foreground=[("selected", "white")])

        self.tree.tag_configure("oddrow", background="#f8f9fa")
        self.tree.tag_configure("evenrow", background="#e9ecef")

        # Scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)

        # Double click headline
        self.tree.bind("<Double-1>", self.show_article)

    def fetch_news(self):
        keyword = self.keyword_entry.get().strip() or "tesla"
        source = self.source_entry.get().strip() or None
        from_date = self.date_entry.get_date().strftime("%Y-%m-%d")

        self.fetcher.fetch_data(query=keyword, from_date=from_date, source=source)

        # Clear old rows
        for row in self.tree.get_children():
            self.tree.delete(row)

        if self.fetcher.df is not None:
            for i, (_, row) in enumerate(self.fetcher.df.iterrows()):
                title = row.get("title", "No Title")
                published = row.get("publishedAt", "No Date")
                src = row.get("source", {}).get("name", "Unknown")
                tag = "evenrow" if i % 2 == 0 else "oddrow"
                self.tree.insert("", tk.END, values=(title, src, published), tags=(tag,))
        else:
            messagebox.showinfo("No Results", "No articles found.")

    def save_news(self):
        if self.fetcher.df is not None:
            self.fetcher.save_to_csv("News_data.csv")
            messagebox.showinfo("Success", "News saved to News_data.csv")
        else:
            messagebox.showwarning("Warning", "No news data to save. Fetch news first.")

    def show_article(self, event):
        """Show article info on double click"""
        self.read_selected()

    def read_selected(self):
        """Show full article info in popup"""
        selected_item = self.tree.selection()
        if not selected_item or self.fetcher.df is None:
            return

        title_clicked = self.tree.item(selected_item[0])["values"][0]
        match = self.fetcher.df[self.fetcher.df["title"] == title_clicked]

        if not match.empty:
            article = match.iloc[0]
            title = article.get("title", "No Title")
            description = article.get("description", "No Description")
            url = article.get("url", "No URL")

            popup = tk.Toplevel(self.root)
            popup.title("📰 Full Article")
            popup.geometry("600x400")

            tk.Label(popup, text=title, wraplength=550, font=("Segoe UI", 12, "bold")).pack(pady=10)
            tk.Message(popup, text=description, width=550, font=("Segoe UI", 10)).pack(pady=10)
            tk.Label(popup, text=url, fg="blue", cursor="hand2").pack(pady=10)

            # Clickable link
            def open_link(event):
                webbrowser.open(url)
            popup.bind("<Button-1>", open_link)
