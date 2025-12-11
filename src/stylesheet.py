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