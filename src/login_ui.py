import os

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QLabel, QLineEdit, QHBoxLayout, QPushButton, QMessageBox, \
    QWidget, QTableWidget, QHeaderView, QTableWidgetItem
from chainshift_playwright_extension import get_sync_browser
from playwright.sync_api import sync_playwright

from config import Config
from stylesheet import STYLE_SHEET


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

        reply = QMessageBox()
        reply.setWindowTitle('Login Complete Confirmation')
        reply.setText("로그인 완료 후 확인 버튼 클릭.")
        reply.setStandardButtons(QMessageBox.StandardButton.Yes)

        # Playwright Login 추가
        user_data_dir_name = f"{id_val}_user_data_tistory"
        user_info_dir_path = os.path.join(
            Config.USER_DATA_DIR_PATH,
            user_data_dir_name
        )

        if not os.path.isdir(user_info_dir_path):
            os.makedirs(user_info_dir_path)

        with sync_playwright() as p:
            browser = get_sync_browser(p, user_info_dir_path, Config.headless)

            page = browser.pages[0] if browser.pages else browser.new_page()
            page.goto(Config.TISTORY_LOGIN_URL, wait_until="load")

            if page.locator('a.btn_login').is_visible():
                login_btn = page.locator('a.btn_login')
                login_btn.click()
                page.locator('input[name="loginId"]').fill(id_val)
                page.locator('input[name="password"]').fill(pw_val)
                page.locator('button[type="submit"]').click()
                page.wait_for_load_state("networkidle")

                reply.exec()
                if reply is QMessageBox.StandardButton.Yes:
                    browser.close()

        self.result_data = {
            'ID': id_val,
            'PW': pw_val,
            'POST_URL': blog_val
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
                # 1. 데이터 추가
                self.login_data.append(new_data)

                # 2. JSON 파일 저장
                self.parent_app.save_login_data_to_json()

                # 3. 테이블 갱신
                self.load_login_data()

                self.parent_app.log_message(
                    f"[Success] 로그인 정보 등록 완료 및 파일 저장: ID={new_data['ID']}, URL={new_data['POST_URL']}")