from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QLineEdit, QPushButton,
    QScrollArea, QTextEdit, QFileDialog, QMessageBox,
    QFrame, QGroupBox, QSizePolicy, QMenuBar, QMenu,
    QDialog, QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox, QSpacerItem
)
from PyQt6.QtCore import Qt, QDateTime, QSize
from PyQt6.QtGui import QFont, QIcon, QAction
from playwright.sync_api import sync_playwright
from chainshift_playwright_extension import get_sync_browser

import os
import sys
import json  # JSON 처리를 위해 추가

from src.config import Config

# --- 설정 상수 ---
MAX_FILES = 15
MAX_TAGS = 10
APP_TITLE = "Tistory Post Automation"
LOGIN_DATA_FILE = Config.AUTH_FILE_PATH

# --- 공통 스타일 설정 (배경색 변경) ---
# (STYLE_SHEET는 코드 길이를 위해 생략하며, 이전 코드와 동일합니다.)
STYLE_SHEET = """
QWidget {
    background-color: #1c1c1c;
    color: #ecf0f1;
    font-family: Arial;
    font-size: 14px;
}
QMenuBar { background-color: #252525; color: #ecf0f1; border: none; }
QMenuBar::item { padding: 5px 10px; }
QMenuBar::item:selected { background-color: #2980b9; }
QMenu { background-color: #252525; border: 1px solid #7f8c8d; }
QMenu::item:selected { background-color: #2980b9; }
QGroupBox {
    border: 2px solid #353535; border-radius: 8px; margin-top: 10px;
    padding-top: 20px; font-weight: bold; color: #f1c40f;
}
QPushButton {
    background-color: #3498db; color: white; border: none;
    border-radius: 6px; padding: 10px 15px; font-weight: bold;
}
QPushButton:hover { background-color: #2980b9; }
QPushButton#StartButton { background-color: #27ae60; min-height: 50px; font-size: 16px; }
QPushButton#StartButton:hover { background-color: #2ecc71; }
QPushButton#ClearButton { background-color: #e74c3c; min-height: 40px; }
QPushButton#ClearButton:hover { background-color: #c0392b; }
QPushButton#RemoveFileButton {
    background-color: #e74c3c; color: white; border: none; border-radius: 4px;
    padding: 5px; min-width: 30px; max-width: 30px; min-height: 30px;
    max-height: 30px; font-size: 14px; font-weight: bold; margin-left: 5px;
}
QPushButton#RemoveFileButton:hover { background-color: #c0392b; }
QPushButton#ScrollUploadButton {
    background-color: #3498db; min-height: 50px; font-size: 16px; padding: 15px;
    border-radius: 10px; margin: 50px; border: 2px dashed #95a5a6;
}
QPushButton#ScrollUploadButton:hover { background-color: #2980b9; }
QLineEdit {
    border: 1px solid #7f8c8d; border-radius: 4px; padding: 5px;
    background-color: #252525; color: #ecf0f1;
}
QLineEdit[valid="true"] { border: 2px solid #2ecc71; }
QLineEdit[valid="false"] { border: 2px solid #e74c3c; }
QTextEdit {
    background-color: #0a0a0a; color: #00ff00; border: 1px solid #34495e;
    border-radius: 4px; padding: 8px;
}
QFrame#SeparatorLine { border: none; background-color: #666666; min-height: 1px; max-height: 1px; margin: 0px; padding: 0px; }
#DndArea { border: 2px dashed #95a5a6; border-radius: 8px; background-color: #252525; color: #95a5a6; padding: 20px; }
QTableWidget { background-color: #252525; gridline-color: #34495e; border: 1px solid #34495e; }
QHeaderView::section { background-color: #34495e; color: #ecf0f1; padding: 5px; border: 1px solid #34495e; font-weight: bold; }
QComboBox {
    background-color: #34495e; color: #ecf0f1; border: 1px solid #7f8c8d;
    border-radius: 4px; padding: 5px 10px; min-width: 150px;
}
QComboBox::drop-down { border: 0px; }
QComboBox QAbstractItemView { border: 1px solid #7f8c8d; selection-background-color: #2980b9; }
"""


# ----------------------------------------------------------------------
#                             로그인 등록 대화상자
# ----------------------------------------------------------------------

class LoginRegisterDialog(QDialog):
    # ... (기존 LoginRegisterDialog 클래스 유지)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("새로운 로그인 정보 등록")
        self.setModal(True)
        self.setGeometry(200, 400, 700, 200)
        self.setStyleSheet(STYLE_SHEET)

        self.result_data = None
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        form_layout = QGridLayout()

        form_layout.addWidget(QLabel("Tistory ID:"), 0, 0)
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("ID를 입력하세요")
        form_layout.addWidget(self.id_input, 0, 1)

        form_layout.addWidget(QLabel("Password:"), 1, 0)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Password를 입력하세요")
        form_layout.addWidget(self.password_input, 1, 1)

        form_layout.addWidget(QLabel("Blog URL:"), 2, 0)
        self.blog_name_input = QLineEdit()
        self.blog_name_input.setPlaceholderText("포스팅 할 블로그 주소의 URL 부분 (ex. https://korea-beauty-editor-best.tistory.com/)")
        form_layout.addWidget(self.blog_name_input, 2, 1)

        main_layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        self.register_button = QPushButton("등록하기")
        self.cancel_button = QPushButton("취소")

        self.register_button.clicked.connect(self._register_clicked)
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addStretch(1)
        button_layout.addWidget(self.register_button)
        button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(button_layout)

    def _register_clicked(self):
        id_val = self.id_input.text().strip()
        pw_val = self.password_input.text()
        blog_val = self.blog_name_input.text().strip()

        if not id_val or not pw_val or not blog_val:
            QMessageBox.warning(self, "경고", "ID, Password, Blog 이름은 필수 입력 항목입니다.")
            return

        self.result_data = {
            'ID': id_val,
            'PW': pw_val,
            'POST_URL': f"https://{blog_val}.tistory.com"  # URL 형식으로 저장
        }
        self.accept()

    def get_data(self):
        return self.result_data


# ----------------------------------------------------------------------
#                             로그인 설정 화면
# ----------------------------------------------------------------------

class LoginConfigWindow(QWidget):
    def __init__(self, parent_app, login_data):
        super().__init__()
        self.parent_app = parent_app
        self.login_data = login_data
        self.setWindowTitle("Tistory 로그인 정보 관리")
        self.resize(700, 400)
        self.setStyleSheet(STYLE_SHEET)

        self._setup_ui()
        self.load_login_data()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)

        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(3)
        # JSON 키 값에 맞게 헤더 레이블 변경
        self.table_widget.setHorizontalHeaderLabels(["ID", "Password (숨김)", "Blog URL"])

        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        main_layout.addWidget(self.table_widget)

        button_layout = QHBoxLayout()
        self.register_new_button = QPushButton("➕ 새로운 정보 등록")
        self.register_new_button.clicked.connect(self.open_register_dialog)

        button_layout.addStretch(1)
        button_layout.addWidget(self.register_new_button)

        main_layout.addLayout(button_layout)

    def load_login_data(self):
        """저장된 로그인 정보를 테이블에 출력합니다."""
        self.table_widget.setRowCount(0)

        # self.login_data는 이제 list[dict] 형태의 JSON 데이터 구조를 따릅니다.
        for row_index, data in enumerate(self.login_data):
            self.table_widget.insertRow(row_index)

            # JSON 키값: "ID"
            id_item = QTableWidgetItem(data.get('ID', 'N/A'))
            self.table_widget.setItem(row_index, 0, id_item)

            # JSON 키값: "PW" (숨김 처리)
            pw_item = QTableWidgetItem(data.get('PW', 'N/A'))
            self.table_widget.setItem(row_index, 1, pw_item)

            # JSON 키값: "POST_URL"
            blog_item = QTableWidgetItem(data.get('POST_URL', 'N/A'))
            self.table_widget.setItem(row_index, 2, blog_item)

            id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            pw_item.setFlags(pw_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            blog_item.setFlags(blog_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

        # 메인 앱의 드롭다운도 갱신하도록 요청
        self.parent_app._populate_id_dropdown()

    def open_register_dialog(self):
        """등록 버튼 클릭 시 새 정보 입력 대화상자를 엽니다."""
        self.parent_app.log_message("[Action] 새로운 로그인 정보 등록 다이얼로그 열기.")

        dialog = LoginRegisterDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_data = dialog.get_data()
            if new_data:
                # Playwright Login 추가
                user_data_dir_name = f"{new_data.ID}_user_data_tistory"
                user_info_dir_path = os.path.join(
                    Config.USER_DATA_DIR_PATH,
                    user_data_dir_name
                )

                if not os.path.isdir(user_info_dir_path):
                    os.mkdir(user_info_dir_path)

                with sync_playwright() as p:
                    browser = get_sync_browser(p, user_info_dir_path, Config.headless)

                    page = browser.pages[0] if browser.pages else browser.new_page()
                    page.goto(Config.TISTORY_LOGIN_URL, wait_until="load")

                    page.wait_for_selector('a.btn_login', timeout=10000)
                    login_btn = page.locator('a.btn_login')
                    if login_btn.count() > 0:
                        login_btn.click()
                        page.locator('input[name="loginId"]').fill(new_data.ID)
                        page.locator('input[name="password"]').fill(new_data.PW)
                        page.locator('button[type="submit"]').click()
                        page.wait_for_load_state("networkidle")
                        page.wait_for_url("https://www.tistory.com/", timeout=30000)

                # Login 확인 버튼 클릭 시 아래 코드 실행

                # 1. 데이터 추가
                self.login_data.append(new_data)

                # 2. JSON 파일 저장
                self.parent_app.save_login_data_to_json()

                # 3. 테이블 갱신
                self.load_login_data()

                self.parent_app.log_message(
                    f"[Success] 로그인 정보 등록 완료 및 파일 저장: ID={new_data['ID']}, URL={new_data['POST_URL']}")


# ----------------------------------------------------------------------
#                             메인 앱 클래스
# ----------------------------------------------------------------------

class AutomationApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(QSize(950, 900))
        self.setStyleSheet(STYLE_SHEET)

        self.uploaded_files = []
        self.file_tag_entries = {}
        self.login_config_window = None
        self.current_selected_id = None


        self.setup_ui()

        self.login_data = self.load_login_data_from_json()
        self._populate_id_dropdown()

        self._setup_scroll_content_widgets()
        self.update_file_list_ui()
        self.log_message("[System] 애플리케이션 시작. Black Theme 적용됨.")

    # ----------------------------------------------------------------------
    #                             JSON 파일 처리
    # ----------------------------------------------------------------------

    def load_login_data_from_json(self):
        """JSON 파일에서 로그인 데이터를 로드합니다."""
        if not os.path.exists(LOGIN_DATA_FILE):
            self.log_message(f"[Info] 로그인 파일 '{LOGIN_DATA_FILE}'이 존재하지 않아 빈 목록으로 시작합니다.")
            return []

        try:
            with open(LOGIN_DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.log_message(f"[Success] 로그인 정보 {len(data)}개를 '{LOGIN_DATA_FILE}'에서 로드했습니다.")
                return data
        except json.JSONDecodeError:
            QMessageBox.critical(self, "파일 오류", f"'{LOGIN_DATA_FILE}' 파일 형식이 올바르지 않습니다.")
            self.log_message(f"[Error] '{LOGIN_DATA_FILE}' 파일 JSON 디코딩 오류 발생.")
            return []
        except Exception as e:
            QMessageBox.critical(self, "파일 오류", f"파일 로드 중 오류 발생: {e}")
            self.log_message(f"[Error] 파일 로드 중 예외 발생: {e}")
            return []

    def save_login_data_to_json(self):
        """현재 login_data를 JSON 파일에 저장합니다."""
        try:
            # indent=2를 사용하여 가독성 있게 저장
            with open(LOGIN_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.login_data, f, indent=2, ensure_ascii=False)
            self.log_message(f"[Success] 로그인 정보가 '{LOGIN_DATA_FILE}'에 저장되었습니다.")
        except Exception as e:
            QMessageBox.critical(self, "파일 저장 오류", f"로그인 정보 저장 중 오류 발생: {e}")
            self.log_message(f"[Error] 파일 저장 중 예외 발생: {e}")

    # ----------------------------------------------------------------------
    #                             UI 설정
    # ----------------------------------------------------------------------

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self._create_menu_bar(main_layout)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 10, 20, 20)

        content_layout.addWidget(self._create_id_selection_area())
        content_layout.addWidget(self._create_file_list_area(), stretch=6)
        content_layout.addWidget(self._create_bottom_controls())
        content_layout.addWidget(self._create_log_area(), stretch=3)

        main_layout.addLayout(content_layout)

    def _create_id_selection_area(self):
        """현재 등록된 ID를 선택하는 드롭다운 컨트롤 영역을 생성합니다."""

        id_frame = QFrame(self)
        id_layout = QHBoxLayout(id_frame)
        id_layout.setContentsMargins(0, 0, 0, 10)

        id_layout.addWidget(QLabel("✅ 포스팅에 사용할 계정 ID 선택:"))

        self.id_dropdown = QComboBox(self)
        self.id_dropdown.currentIndexChanged.connect(self._handle_id_selection_change)
        id_layout.addWidget(self.id_dropdown)

        id_layout.addStretch(1)

        return id_frame

    def _populate_id_dropdown(self):
        """login_data를 기반으로 드롭다운 목록을 채우고 상태를 설정합니다."""

        self.id_dropdown.clear()

        if not self.login_data:
            self.id_dropdown.addItem("등록된 ID가 없습니다. Login 설정에서 추가하세요.")
            self.id_dropdown.setEnabled(False)
            self.current_selected_id = None
            return

        self.id_dropdown.setEnabled(True)
        # ID는 "ID" 키를 사용하여 가져옵니다.
        id_list = [data['ID'] for data in self.login_data if 'ID' in data]

        if not id_list:
            self.id_dropdown.addItem("등록된 ID가 없습니다. Login 설정에서 추가하세요.")
            self.id_dropdown.setEnabled(False)
            self.current_selected_id = None
            return

        self.id_dropdown.addItems(id_list)

        # 초기 선택 ID 설정 (첫 번째 항목)
        self.current_selected_id = id_list[0]
        self.log_message(f"[System] 기본 포스팅 ID가 '{self.current_selected_id}'로 설정되었습니다.")

    def _handle_id_selection_change(self, index):
        """드롭다운에서 ID 선택이 변경되었을 때 호출됩니다."""

        if self.id_dropdown.count() == 0 or index < 0:
            return

        selected_id = self.id_dropdown.currentText()

        if selected_id != self.current_selected_id:
            self.current_selected_id = selected_id
            self.log_message(f"[Change] 포스팅 ID가 '{self.current_selected_id}'로 변경되었습니다.")

    def _create_menu_bar(self, parent_layout):
        # ... (기존 _create_menu_bar 로직 유지)
        menu_bar = QMenuBar(self)

        file_menu = menu_bar.addMenu('파일')

        login_config_action = QAction('🔑 Login 설정', self)
        login_config_action.triggered.connect(self.show_login_config)
        file_menu.addAction(login_config_action)

        file_menu.addSeparator()

        exit_action = QAction('종료', self)
        exit_action.triggered.connect(QApplication.instance().quit)
        file_menu.addAction(exit_action)

        help_menu = menu_bar.addMenu('도움말(&H)')
        help_menu.addAction(QAction('정보', self))

        parent_layout.addWidget(menu_bar)

    def _create_file_list_area(self):
        # ... (기존 _create_file_list_area 로직 유지)
        hint = f"최대 파일 업로드 개수 : {MAX_FILES}개, TAG 입력 : 띄어쓰기로 구분, 중복 불가, 최대 {MAX_TAGS}개"
        file_list_group = QGroupBox(f"포스팅 파일 업로드 및 태그 입력({hint})", self)
        file_list_vbox = QVBoxLayout(file_list_group)
        file_list_vbox.setContentsMargins(10, 25, 10, 10)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none; background-color: transparent;")

        self.scroll_content = QWidget()
        self.scroll_content_layout = QGridLayout(self.scroll_content)
        self.scroll_content_layout.setContentsMargins(0, 0, 0, 0)

        self.scroll_content_layout.setVerticalSpacing(0)

        self.scroll_area.setWidget(self.scroll_content)

        file_list_vbox.addWidget(self.scroll_area)
        return file_list_group

    def _setup_scroll_content_widgets(self):
        # ... (기존 _setup_scroll_content_widgets 로직 유지)
        self.scroll_upload_button = QPushButton("➕ HTML 파일 업로드(Click Or Drag)", self)
        self.scroll_upload_button.setObjectName("ScrollUploadButton")
        self.scroll_upload_button.clicked.connect(self.select_files)
        self.scroll_upload_button.hide()

        self.scroll_content_layout.setRowStretch(0, 1)
        self.scroll_content_layout.setRowStretch(2, 1)
        self.scroll_content_layout.setColumnStretch(0, 1)
        self.scroll_content_layout.setColumnStretch(2, 1)

        self.scroll_content_layout.addWidget(self.scroll_upload_button, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.scroll_content_layout.setRowStretch(3, 0)

    def _create_log_area(self):
        # ... (기존 _create_log_area 로직 유지)
        log_group = QGroupBox("실시간 처리 로그 및 상태", self)
        log_vbox = QVBoxLayout(log_group)
        log_vbox.setContentsMargins(10, 25, 10, 10)

        self.count_label = QLabel(f"현재 파일 개수: 0 / {MAX_FILES}개", self)
        self.count_label.setStyleSheet("color: #3498db; font-weight: bold; margin-bottom: 5px;")
        log_vbox.addWidget(self.count_label)

        self.log_textbox = QTextEdit(self)
        self.log_textbox.setReadOnly(True)
        log_vbox.addWidget(self.log_textbox)

        return log_group

    def _create_bottom_controls(self):
        # ... (기존 _create_bottom_controls 로직 유지)
        control_frame = QFrame(self)
        control_layout = QHBoxLayout(control_frame)
        control_layout.setContentsMargins(0, 5, 0, 0)

        control_layout.addStretch(1)

        self.clear_files_button = QPushButton("🗑️ 전체 목록 초기화", self)
        self.clear_files_button.setObjectName("ClearButton")
        self.clear_files_button.clicked.connect(self.clear_files)
        control_layout.addWidget(self.clear_files_button)

        control_layout.addSpacing(10)

        self.start_button = QPushButton("TISTORY 포스팅 자동화 시작", self)
        self.start_button.setObjectName("StartButton")
        self.start_button.clicked.connect(self.start_automation)
        control_layout.addWidget(self.start_button)

        return control_frame

    # ----------------------------------------------------------------------
    #                             기능 구현 (로그인 설정 화면 표시)
    # ----------------------------------------------------------------------

    def show_login_config(self):
        """Login 설정 메뉴를 클릭했을 때 로그인 관리 화면을 엽니다."""

        if self.login_config_window and self.login_config_window.isVisible():
            self.login_config_window.raise_()
            self.login_config_window.activateWindow()
            self.log_message("[Info] 로그인 관리 화면이 이미 열려 있습니다. 활성화합니다.")
            return

        self.log_message("[Action] 로그인 관리 화면을 출력합니다.")

        # 창을 열 때마다 현재 로드된 데이터를 전달
        self.login_config_window = LoginConfigWindow(self, self.login_data)
        self.login_config_window.show()

    # ----------------------------------------------------------------------
    #                             기능 구현 (기존)
    # ----------------------------------------------------------------------

    def log_message(self, message):
        """텍스트박스에 메시지를 출력하고 스크롤을 최신 내용으로 이동시킵니다."""
        timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        log_entry = f"[{timestamp}] {message}"

        self.log_textbox.append(log_entry)
        self.log_textbox.ensureCursorVisible()
        print(log_entry)

    def select_files(self):
        self.log_message("[Action] 파일 선택 기능이 호출되었습니다.")
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "포스팅 파일 선택", "", "HTML 파일 (*.html);;모든 파일 (*.*)"
        )
        if file_paths:
            new_files = [path for path in file_paths if path not in self.uploaded_files]
            space_left = MAX_FILES - len(self.uploaded_files)
            files_to_add = new_files[:space_left]
            if not files_to_add and len(self.uploaded_files) >= MAX_FILES:
                QMessageBox.warning(self, "Error", f"최대 {MAX_FILES}개 파일만 업로드 가능합니다.")
                self.log_message(f"[Error] 파일 업로드 제한({MAX_FILES}개) 초과.")
                return
            self.uploaded_files.extend(files_to_add)
            self.log_message(f"[Success] 새로운 파일 {len(files_to_add)}개 추가됨. 총 {len(self.uploaded_files)}개.")
            if len(new_files) > space_left:
                QMessageBox.warning(self, "Error",
                                    f"{len(new_files) - space_left}개의 파일이 최대 개수 제한({MAX_FILES}개)으로 인해 제외되었습니다.")
                self.log_message(f"[Error] {len(new_files) - space_left}개 파일이 제한으로 제외됨.")
            self.update_file_list_ui()

    def clear_files(self):
        if not self.uploaded_files:
            self.log_message("[Info] 목록이 이미 비어 있습니다.")
            return
        reply = QMessageBox.question(
            self, '확인', "업로드된 파일 목록을 **모두** 초기화하시겠습니까?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.uploaded_files.clear()
            self.update_file_list_ui()
            self.log_message("[Action] 파일 목록을 초기화했습니다.")

    def remove_file(self, file_path):
        try:
            self.uploaded_files.remove(file_path)
            file_name = os.path.basename(file_path)
            if file_name in self.file_tag_entries:
                del self.file_tag_entries[file_name]
            self.update_file_list_ui()
            self.log_message(f"[Action] '{file_name}' 파일을 목록에서 제거했습니다.")
        except ValueError:
            self.log_message(f"[Error] '{file_path}' 파일을 목록에서 찾을 수 없습니다.")

    def _create_file_row(self, file_path):
        file_name = os.path.basename(file_path)
        file_label = QLabel(f"📄 {file_name}")
        file_label.setWordWrap(False)
        file_label.setTextElideMode(Qt.TextElideMode.ElideRight)
        tag_entry = QLineEdit(self)
        tag_entry.setPlaceholderText("예: 파이썬 CustomTkinter 자동화")
        tag_entry.setProperty("valid", "true")
        tag_entry.setStyleSheet(tag_entry.styleSheet() + STYLE_SHEET)
        tag_entry.returnPressed.connect(lambda entry=tag_entry: self.start_automation_single_file(entry))
        self.file_tag_entries[file_name] = tag_entry
        remove_button = QPushButton("❌", self)
        remove_button.setObjectName("RemoveFileButton")
        remove_button.clicked.connect(lambda _, path=file_path: self.remove_file(path))
        tag_control_widget = QWidget()
        tag_control_layout = QHBoxLayout(tag_control_widget)
        tag_control_layout.setContentsMargins(0, 0, 0, 0)
        tag_control_layout.setSpacing(5)
        tag_control_layout.addWidget(tag_entry, stretch=1)
        tag_control_layout.addWidget(remove_button)
        return file_label, tag_control_widget

    def update_file_list_ui(self):
        items_to_keep = [self.scroll_upload_button]
        all_widgets_to_remove = []
        for i in reversed(range(self.scroll_content_layout.count())):
            item = self.scroll_content_layout.itemAt(i)
            widget = item.widget()
            if widget and widget not in items_to_keep:
                all_widgets_to_remove.append(widget)
                self.scroll_content_layout.removeItem(item)
            elif not widget and item.spacerItem():
                self.scroll_content_layout.removeItem(item)
        for widget in all_widgets_to_remove:
            widget.deleteLater()

        if self.uploaded_files:
            self.scroll_upload_button.hide()
            self.clear_files_button.show()
            self.start_button.setEnabled(True)
            self.scroll_content_layout.setRowStretch(0, 0)
            self.scroll_content_layout.setRowStretch(2, 0)
            self.scroll_content_layout.setColumnStretch(0, 0)
            self.scroll_content_layout.setColumnStretch(2, 0)
            header_file = QLabel("파일명")
            header_file.setFont(QFont(header_file.font().family(), -1, QFont.Weight.Bold))
            self.scroll_content_layout.addWidget(header_file, 0, 0, Qt.AlignmentFlag.AlignLeft)
            header_tag = QLabel(f"Tag 키워드 (띄어쓰기 구분) 및 관리")
            header_tag.setFont(QFont(header_tag.font().family(), -1, QFont.Weight.Bold))
            self.scroll_content_layout.addWidget(header_tag, 0, 1, Qt.AlignmentFlag.AlignLeft)
            for i, path in enumerate(self.uploaded_files):
                data_row = i * 2 + 1
                separator_row = i * 2 + 2
                file_label, tag_control_widget = self._create_file_row(path)
                self.scroll_content_layout.addWidget(file_label, data_row, 0,
                                                     Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                self.scroll_content_layout.addWidget(tag_control_widget, data_row, 1)
                if i < len(self.uploaded_files) - 1:
                    separator = QFrame(self)
                    separator.setObjectName("SeparatorLine")
                    separator.setFrameShape(QFrame.Shape.HLine)
                    separator.setFrameShadow(QFrame.Shadow.Sunken)
                    self.scroll_content_layout.addWidget(separator, separator_row, 0, 1, 2)
            self.scroll_content_layout.setColumnStretch(0, 6)
            self.scroll_content_layout.setColumnStretch(1, 4)
            last_row = len(self.uploaded_files) * 2 + 1
            self.scroll_content_layout.setRowStretch(last_row, 1)
        else:
            self.scroll_upload_button.show()
            self.clear_files_button.hide()
            self.start_button.setEnabled(False)
            self.scroll_content_layout.setRowStretch(0, 1)
            self.scroll_content_layout.setRowStretch(2, 1)
            self.scroll_content_layout.setColumnStretch(0, 1)
            self.scroll_content_layout.setColumnStretch(2, 1)
            self.scroll_content_layout.setRowStretch(3, 0)
        self.count_label.setText(f"현재 파일 개수: {len(self.uploaded_files)} / {MAX_FILES}개")
        self.log_message("[System] 파일 목록 UI 업데이트 완료.")

    def validate_tags(self, file_name, tag_entry):
        tags_raw = tag_entry.text()
        tags = [t.strip() for t in tags_raw.split(' ') if t.strip()]
        tag_entry.setProperty("valid", "true")
        tag_entry.style().polish(tag_entry)
        if len(tags) != len(set(tags)):
            tag_entry.setProperty("valid", "false")
            tag_entry.style().polish(tag_entry)
            QMessageBox.critical(self, "🚫 유효성 오류", f"'{file_name}' 파일의 태그에 **중복된 키워드**가 있습니다.\n\n수정해주세요.")
            self.log_message(f"[Error] '{file_name}' 태그 중복 발견.")
            return False
        if len(tags) > MAX_TAGS:
            tag_entry.setProperty("valid", "false")
            tag_entry.style().polish(tag_entry)
            QMessageBox.critical(self, "🚫 유효성 오류",
                                 f"'{file_name}' 파일의 태그 키워드가 최대 {MAX_TAGS}개를 초과했습니다. (현재 {len(tags)}개)\n\n수정해주세요.")
            self.log_message(f"[Error] '{file_name}' 태그 개수({len(tags)}개) 초과.")
            return False
        return True

    def start_automation_single_file(self, tag_entry):
        file_name_to_check = None
        for name, entry in self.file_tag_entries.items():
            if entry is tag_entry:
                file_name_to_check = name
                break
        if file_name_to_check:
            is_valid = self.validate_tags(file_name_to_check, tag_entry)
            if is_valid:
                tag_entry.setProperty("valid", "true")
                tag_entry.style().polish(tag_entry)
                self.log_message(f"[Valid OK] '{file_name_to_check}' 태그 유효성 검사 통과.")
            else:
                self.log_message(f"[Valid Failed] '{file_name_to_check}' 태그 검사 실패.")

    def start_automation(self):
        self.log_message("[Action] 자동화 시작 요청")
        if not self.uploaded_files:
            QMessageBox.warning(self, "Error", "업로드된 파일이 없습니다. 파일을 먼저 선택해주세요.")
            self.log_message("[Error] 업로드된 파일이 없어 자동화 중단.")
            return
        if not self.current_selected_id:
            QMessageBox.warning(self, "Error", "포스팅에 사용할 로그인 ID를 선택해주세요.")
            self.log_message("[Error] 선택된 로그인 ID가 없어 자동화 중단.")
            return

        is_valid = True
        post_tuple_list = []
        for file_path in self.uploaded_files:
            file_name = os.path.basename(file_path)
            tag_entry = self.file_tag_entries.get(file_name)
            if tag_entry:
                self.log_message(f"[Valid] '{file_name}' 파일 태그 유효성 검사 중...")
                if not self.validate_tags(file_name, tag_entry):
                    is_valid = False
                    break
        if is_valid:
            QMessageBox.information(self, "✨ 자동화 시작",
                                    f"모든 유효성 검사 통과! ID: {self.current_selected_id}로 포스팅 프로세스를 시작합니다.")
            self.log_message(f"[Success] 포스팅 자동화 Start (ID: {self.current_selected_id})")
            for file_path in self.uploaded_files:
                file_name = os.path.basename(file_path)
                entry = self.file_tag_entries[file_name]
                tags_raw = entry.text()
                tag_list = [t.strip() for t in tags_raw.split(' ') if t.strip()]
                post_tuple_list.append((file_path, tag_list))
            self.log_message(f"[Data Ready] 자동화에 사용될 포스팅 데이터 {len(post_tuple_list)}개 준비 완료.")
        else:
            QMessageBox.critical(self, "🛑 자동화 중단", "태그 유효성 검사에 실패했습니다. 빨간색으로 표시된 입력 필드를 수정해주세요.")
            self.log_message("[Error] 유효성 검사 실패로 자동화 Stop.")


# ----------------------------------------------------------------------

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AutomationApp()
    window.show()
    sys.exit(app.exec())