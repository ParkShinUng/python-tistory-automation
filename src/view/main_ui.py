from tkinter import filedialog, messagebox
from datetime import datetime

import customtkinter as ctk
import os

# --- 설정 상수 ---
MAX_FILES = 15
MAX_TAGS = 10  # 태그 키워드 최대 개수 제한
APP_TITLE = "Tistory Posting Automation Program"
APP_GEOMETRY = "800x800"


class AutomationApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- 기본 설정 ---
        self.title(APP_TITLE)
        self.geometry(APP_GEOMETRY)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- 데이터 저장 ---
        self.uploaded_files = []  # 업로드된 파일 경로 저장
        self.file_tag_entries = {}  # {파일명: CTkEntry 객체} 저장
        self.default_entry_border_color = ctk.ThemeManager.theme["CTkEntry"]["border_color"][0]

        # --- 메인 프레임 설정 ---
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        # UI 레이아웃 비율 설정: 파일 목록(1), 로그 영역(0.4), 컨트롤 영역(0)
        self.main_frame.grid_rowconfigure(1, weight=5)  # 파일 목록
        self.main_frame.grid_rowconfigure(2, weight=2)  # 로그 영역
        self.main_frame.grid_rowconfigure(3, weight=0)  # 컨트롤 영역

        ## 1. 파일 업로드 및 제한 표시 영역 (Row 0)
        # ----------------------------------------------------------------------
        self.upload_frame = ctk.CTkFrame(self.main_frame)
        self.upload_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        self.upload_frame.columnconfigure(0, weight=1)
        self.select_button = ctk.CTkButton(
            self.upload_frame,
            text=f"📁 파일 선택 (최대 {MAX_FILES}개)",
            command=self.select_files
        )
        self.select_button.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="w")
        self.dnd_label = ctk.CTkLabel(
            self.upload_frame,
            text="파일 드래그 & 드롭 (추가 라이브러리 필요)",
            fg_color="gray20",
            corner_radius=6,
            anchor="center"
        )
        self.dnd_label.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="ew")

        ## 2. 파일 목록 및 태그 입력 영역 (ScrollFrame - Row 1)
        # ----------------------------------------------------------------------
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.main_frame,
            label_text=f"업로드 파일 목록 및 태그 입력 (* 최대 Tag 개수 {MAX_TAGS}개, 띄어쓰기 구분, 중복 키워드 불가)",
            label_font=ctk.CTkFont(weight="bold")
        )
        self.scroll_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.scroll_frame.columnconfigure(0, weight=4)  # 파일명 영역
        self.scroll_frame.columnconfigure(1, weight=6)  # 태그 입력 영역
        self.info_label = ctk.CTkLabel(
            self.scroll_frame,
            height=200,
            text="파일을 선택하거나 드래그하여 업로드하세요.",
            text_color="gray"
        )
        self.info_label.grid(row=0, column=0, columnspan=2, padx=10, pady=50)

        ## 3. 로그 출력 영역 (CTkTextbox - Row 2)
        # ----------------------------------------------------------------------
        self.log_textbox = ctk.CTkTextbox(
            self.main_frame,
            height=150,
            corner_radius=6,
            fg_color=("gray90", "gray15"),
            wrap="word"  # 단어 단위 줄바꿈 설정
        )
        self.log_textbox.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        self.log_textbox.insert("end", f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 프로그램이 시작되었습니다.\n")
        self.log_textbox.configure(state="disabled")

        ## 4. 하단 컨트롤 영역 (Row 3)
        # ----------------------------------------------------------------------
        self.control_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.control_frame.grid(row=3, column=0, padx=10, pady=(5, 10), sticky="ew")
        self.control_frame.columnconfigure(0, weight=1)
        self.control_frame.columnconfigure(1, weight=0)

        # 현재 업로드 개수 표시
        self.count_label = ctk.CTkLabel(self.control_frame, text=f"업로드 개수: 0 / {MAX_FILES}개")
        self.count_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # 자동화 시작 버튼
        self.start_button = ctk.CTkButton(
            self.control_frame,
            text="Start",
            command=self.start_automation
        )
        self.start_button.grid(row=0, column=1, padx=10, pady=10, sticky="e")

    # ----------------------------------------------------------------------
    #                             기능 구현
    # ----------------------------------------------------------------------

    def log_message(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"

        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", log_entry)
        self.log_textbox.see("end")  # 스크롤을 맨 아래로 이동
        self.log_textbox.configure(state="disabled")
        print(log_entry.strip())

    def select_files(self):
        self.log_message("[Success] 파일 선택 대화상자를 엽니다.")

        file_paths = filedialog.askopenfilenames(title="파일 선택", filetypes=(("모든 파일", "*.html"),))

        if file_paths:
            new_files = [path for path in file_paths if path not in self.uploaded_files]
            space_left = MAX_FILES - len(self.uploaded_files)
            files_to_add = new_files[:space_left]

            if not files_to_add and len(self.uploaded_files) >= MAX_FILES:
                messagebox.showwarning("Error", f"최대 {MAX_FILES}개 파일만 업로드 가능합니다.")
                self.log_message(f"[Error] 파일 업로드 제한({MAX_FILES}개) 초과.")
                return

            self.uploaded_files.extend(files_to_add)
            self.log_message(f"[Success] 새로운 파일 {len(files_to_add)}개 추가됨. 총 {len(self.uploaded_files)}개.")

            if len(new_files) > space_left:
                messagebox.showwarning(
                    "Error",
                    f"{len(new_files) - space_left}개의 파일이 최대 개수 제한({MAX_FILES}개)으로 인해 제외되었습니다."
                )
                self.log_message(f"[Error] {len(new_files) - space_left}개 파일이 제한으로 제외됨.")

            self.update_file_list_ui()

    def update_file_list_ui(self):
        """uploaded_files 리스트 기반 UI 업데이트."""
        # 1. 기존 위젯 모두 제거 및 Entry 객체 초기화
        for widget in self.scroll_frame.winfo_children():
            if widget is not self.info_label:
                widget.destroy()
        self.file_tag_entries.clear()

        # 2. 파일 목록 업데이트
        if self.uploaded_files:
            self.info_label.grid_forget()
            header_file = ctk.CTkLabel(self.scroll_frame, text="파일명", font=ctk.CTkFont(weight="bold"))
            header_file.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
            header_tag = ctk.CTkLabel(self.scroll_frame, text="Tag 입력", font=ctk.CTkFont(weight="bold"))
            header_tag.grid(row=0, column=1, padx=10, pady=(10, 5), sticky="w")

            for i, path in enumerate(self.uploaded_files):
                row_index = i + 1
                file_name = os.path.basename(path)

                file_label = ctk.CTkLabel(
                    self.scroll_frame,
                    text=file_name,
                    anchor="w",
                    wraplength=350
                )
                file_label.grid(row=row_index, column=0, padx=10, pady=5, sticky="ew")

                tag_entry = ctk.CTkEntry(
                    self.scroll_frame,
                    placeholder_text="예: 파이썬, CustomTkinter, 자동화, 블로그"
                )
                tag_entry.grid(row=row_index, column=1, padx=10, pady=5, sticky="ew")
                self.file_tag_entries[file_name] = tag_entry

        else:
            self.info_label.grid(row=0, column=0, columnspan=2, padx=10, pady=50)

        # 3. 개수 표시 업데이트
        self.count_label.configure(text=f"업로드 개수: {len(self.uploaded_files)} / {MAX_FILES}개")
        self.log_message("[Success] 파일 업로드 완료.")

    def start_automation(self):
        """자동화 시작 버튼 클릭 시 호출됩니다. 태그 10개 제한 유효성 검사를 수행합니다."""
        self.log_message("[Success] 자동화 시작 요청")

        # 1. 파일 업로드 여부 확인
        if not self.uploaded_files:
            messagebox.showwarning("Error", "업로드된 파일이 없습니다. 파일을 먼저 선택해주세요.")
            self.log_message("[Error] 업로드된 파일이 없어 자동화 중단.")
            return

        is_valid = True
        default_color = ctk.ThemeManager.theme["CTkEntry"]["border_color"][0]

        for entry in self.file_tag_entries.values():
            entry.configure(border_color=default_color)

        # 3. 태그 개수 유효성 검사
        for file_name, tag_entry in self.file_tag_entries.items():
            tags_raw = tag_entry.get()
            tags = [t.strip() for t in tags_raw.split(' ') if t.strip()]

            self.log_message(f"[Valid] '{file_name}' 파일 태그 유효성 검사 중...")

            # 중복 검사
            if len(tags) != len(set(tags)):
                tag_entry.configure(border_color="red")
                messagebox.showerror(
                    "Valid Error",
                    f"'{file_name}' 파일의 태그에 **중복된 키워드**가 포함되어 있습니다.\n\n입력 필드를 확인해주세요."
                )
                self.log_message(f"[Error] '{file_name}' 태그 중복 발견.")
                is_valid = False
                break

            # 키워드 개수 검사 & 중복 키워드 검사
            if len(tags) > MAX_TAGS:
                tag_entry.configure(border_color="red")
                messagebox.showerror(
                    "Valid Error",
                    f"'{file_name}' 파일의 태그 키워드가 최대 {MAX_TAGS}개를 초과했습니다. (현재 {len(tags)}개)\n\n입력 필드를 확인해주세요."
                )
                self.log_message(f"[Error] '{file_name}' 태그 개수({len(tags)}개) 초과.")
                is_valid = False
                break

        # 4. 자동화 실행 또는 중단
        if is_valid:
            # 모든 유효성 검사 통과
            messagebox.showinfo("자동화 시작", "[Success] 모든 유효성 검사 통과. 자동화 프로세스를 시작합니다.")
            self.log_message("[Success] 모든 유효성 검사 통과! 포스팅 자동화 Start")

            # --- 실제 자동화 로직을 여기에 구현 ---
            auto_post_dict = dict()
            for file_path in self.uploaded_files:
                file_name = os.path.basename(file_path)
                entry = self.file_tag_entries[file_name]
                tags_raw = entry.get()
                tag_list = [t.strip() for t in tags_raw.split(' ') if t.strip()]

                auto_post_dict[file_path] = tag_list

            # 자동화 시작 Send Signal
        else:
            self.log_message("[Error] 유효성 검사 실패로 자동화 Stop.")


if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    app = AutomationApp()
    app.mainloop()