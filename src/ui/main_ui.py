import customtkinter as ctk
# Tkinter의 filedialog와 messagebox를 CustomTkinter와 함께 사용합니다.
from tkinter import filedialog, messagebox
import os

# --- 설정 상수 ---
MAX_FILES = 15
MAX_TAGS = 10  # 태그 키워드 최대 개수 제한
APP_TITLE = "Tistory Posting Automation Program"
APP_GEOMETRY = "800x600"


class AutomationApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- 기본 설정 ---
        self.title(APP_TITLE)
        self.geometry(APP_GEOMETRY)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.default_entry_border_color = ctk.ThemeManager.theme["CTkEntry"]["border_color"][0]

        # --- 데이터 저장 ---
        self.uploaded_files = []  # 업로드된 파일 경로 저장
        self.file_tag_entries = {}  # {파일명: CTkEntry 객체} 저장

        # --- 메인 프레임 설정 ---
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        ## 파일 업로드 및 제한 표시 영역
        # ----------------------------------------------------------------------
        self.upload_frame = ctk.CTkFrame(self.main_frame)
        self.upload_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        self.upload_frame.columnconfigure(0, weight=1)
        self.upload_frame.columnconfigure(1, weight=0)

        # 파일 업로드 버튼
        self.select_button = ctk.CTkButton(
            self.upload_frame,
            text=f"📁 파일 선택 (최대 {MAX_FILES}개)",
            command=self.select_files
        )
        self.select_button.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="w")

        # 드래그 앤 드롭 안내 레이블
        self.dnd_label = ctk.CTkLabel(
            self.upload_frame,
            text="파일 드래그 & 드롭 (추가 라이브러리 필요)",
            fg_color="gray20",
            corner_radius=8,
            anchor="center"
        )
        self.dnd_label.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="ew")

        ## 2. 파일 목록 및 태그 입력 영역 (스크롤 가능)
        # ----------------------------------------------------------------------
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.main_frame,
            label_text=f"업로드 파일 목록 및 태그 입력 \n* 최대 Tag 개수 {MAX_TAGS}개, 띄어쓰기 구분, 중복 키워드 불가)"
        )
        self.scroll_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.scroll_frame.columnconfigure(0, weight=4)  # 파일명 영역
        self.scroll_frame.columnconfigure(1, weight=6)  # 태그 입력 영역

        # 초기 파일 목록 안내 레이블 (동적으로 숨겨지거나 표시됨)
        self.info_label = ctk.CTkLabel(
            self.scroll_frame,
            height=200,
            text="파일을 선택하거나 드래그하여 업로드하세요.",
            text_color="gray"
        )
        self.info_label.grid(row=0, column=0, columnspan=2, padx=10, pady=50)

        ## 3. 하단 컨트롤 영역
        # ----------------------------------------------------------------------
        self.control_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.control_frame.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="ew")
        self.control_frame.columnconfigure(0, weight=1)
        self.control_frame.columnconfigure(1, weight=0)

        # 현재 업로드 개수 표시
        self.count_label = ctk.CTkLabel(
            self.control_frame,
            text=f"업로드 개수: 0 / {MAX_FILES}개"
        )
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

    def select_files(self):
        """파일 업로드. 최대 15개 제한"""

        file_paths = filedialog.askopenfilenames(
            title="파일 선택",
            filetypes=(("모든 파일", "*.html"),)
        )

        if file_paths:
            new_files = [path for path in file_paths if path not in self.uploaded_files]

            space_left = MAX_FILES - len(self.uploaded_files)
            files_to_add = new_files[:space_left]

            if not files_to_add and len(self.uploaded_files) >= MAX_FILES:
                messagebox.showwarning("경고", f"최대 {MAX_FILES}개 파일만 업로드 가능합니다.")
                return

            self.uploaded_files.extend(files_to_add)

            if len(new_files) > space_left:
                messagebox.showwarning(
                    "경고",
                    f"{len(new_files) - space_left}개의 파일이 최대 개수 제한({MAX_FILES}개)으로 인해 제외되었습니다."
                )

            self.update_file_list_ui()

    def update_file_list_ui(self):
        """uploaded_files 리스트 기반 UI 업데이트."""

        # 1. 기존 위젯 모두 제거 및 Entry 객체 초기화
        for widget in self.scroll_frame.winfo_children():
            if widget is not self.info_label:
                widget.destroy()

        # 이전 Entry 객체 저장소를 초기화하고, UI를 새로 그리면서 다시 채웁니다.
        self.file_tag_entries.clear()

        # 2. 파일 목록 업데이트
        if self.uploaded_files:
            self.info_label.grid_forget()

            # 헤더 생성
            header_file = ctk.CTkLabel(self.scroll_frame, text="파일명", font=ctk.CTkFont(weight="bold"))
            header_file.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
            header_tag = ctk.CTkLabel(self.scroll_frame, text="Tag 입력", font=ctk.CTkFont(weight="bold"))
            header_tag.grid(row=0, column=1, padx=10, pady=(10, 5), sticky="w")

            for i, path in enumerate(self.uploaded_files):
                row_index = i + 1
                file_name = os.path.basename(path)

                # 파일명 레이블 (Col: 0)
                file_label = ctk.CTkLabel(
                    self.scroll_frame,
                    text=file_name,
                    anchor="w",
                    wraplength=350
                )
                file_label.grid(row=row_index, column=0, padx=10, pady=5, sticky="ew")

                # 태그 입력 Entry (Col: 1)
                tag_entry = ctk.CTkEntry(
                    self.scroll_frame,
                    placeholder_text="예: 파이썬, CustomTkinter, 자동화, 블로그"
                )
                tag_entry.grid(row=row_index, column=1, padx=10, pady=5, sticky="ew")

                # Entry 객체를 저장
                self.file_tag_entries[file_name] = tag_entry

        else:
            # 파일이 없으면 안내 레이블 다시 표시
            self.info_label.grid(row=0, column=0, columnspan=2, padx=10, pady=50)

        # 3. 개수 표시 업데이트
        self.count_label.configure(text=f"업로드 개수: {len(self.uploaded_files)} / {MAX_FILES}개")

    def start_automation(self):
        """자동화 시작 버튼 클릭 시 호출됩니다. 태그 10개 제한 유효성 검사를 수행합니다."""

        # 1. 파일 업로드 여부 확인
        if not self.uploaded_files:
            messagebox.showwarning("Error", "업로드된 파일이 없습니다. 파일을 먼저 선택해주세요.")
            return

        is_valid = True

        # 2. 이전 유효성 검사 실패 흔적 초기화
        # 모든 Entry의 테두리 색상을 기본 색상으로 되돌립니다.
        for entry in self.file_tag_entries.values():
            entry.configure(border_color=self.default_entry_border_color)

        # 3. 태그 개수 유효성 검사
        for file_name, tag_entry in self.file_tag_entries.items():
            tags_raw = tag_entry.get()

            # 태그 문자열을 띄어쓰기로 구분하고, 각 항목의 앞뒤 공백을 제거한 후, 빈 문자열 제거
            tags = [t.strip() for t in tags_raw.split(' ') if t.strip()]

            if len(tags) != len(set(tags)):
                # 중복 항목이 발견된 경우
                tag_entry.configure(border_color="red")
                messagebox.showerror(
                    "유효성 검사 오류",
                    f"'{file_name}' 파일의 태그에 **중복된 키워드**가 포함되어 있습니다.\n\n입력 필드를 확인해주세요."
                )
                is_valid = False
                break

            # 키워드 개수 검사 & 중복 키워드 검사
            if len(tags) > MAX_TAGS:
                # 유효성 검사 실패
                messagebox.showerror(
                    "유효성 검사 오류",
                    f"'{file_name}' 파일의 태그 키워드가 최대 {MAX_TAGS}개를 초과했습니다. (현재 {len(tags)}개)\n\n입력 필드를 확인해주세요."
                )

                tag_entry.configure(border_color="red")
                is_valid = False
                break

        # 4. 자동화 실행 또는 중단
        if is_valid:
            # 모든 유효성 검사 통과
            messagebox.showinfo("자동화 시작", "✅ 모든 유효성 검사 통과. 자동화 프로세스를 시작합니다.")

            # --- 실제 자동화 로직을 여기에 구현 ---
            print("\n--- 최종 자동화 데이터 ---")
            for file_path in self.uploaded_files:
                file_name = os.path.basename(file_path)
                entry = self.file_tag_entries[file_name]
                final_tags_raw = entry.get()
                final_tags = [t.strip() for t in final_tags_raw.split(',') if t.strip()]

                # file_path (원본 파일 경로)와 final_tags (최종 태그 리스트)를 사용하여 블로그 포스팅 자동화 로직을 구현합니다.
                print(f"파일 경로: {file_path}")
                print(f"파일 이름: {file_name}")
                print(f"적용될 태그: {final_tags}")
            print("--------------------------")

        else:
            print("태그 유효성 검사 실패로 자동화를 시작하지 않습니다.")


if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    app = AutomationApp()
    app.mainloop()