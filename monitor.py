import sys
import os
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QGridLayout
from PyQt5.QtGui import QPixmap, QScreen
from PyQt5.QtCore import QFileSystemWatcher, Qt


class ImageMonitor(QWidget):
    def __init__(self, folder1, folder2):
        super().__init__()
        self.folder1 = folder1
        self.folder2 = folder2
        self.images_per_page = 2 
        self.current_page = 0


        screen = QApplication.primaryScreen().size()
        self.setFixedSize(screen) 

        self.layout = QVBoxLayout()
        self.grid_layout = QGridLayout()
        self.button_layout = QHBoxLayout()

        # Image labels (2x2 grid)
        self.image_labels = [[QLabel(self) for _ in range(2)] for _ in range(2)]
        for row in range(2):
            for col in range(2):
                self.image_labels[row][col].setScaledContents(True)  # Prevents stretching issues
                self.image_labels[row][col].setAlignment(Qt.AlignCenter)
                self.grid_layout.addWidget(self.image_labels[row][col], row, col)


        self.prev_button = QPushButton("Previous")
        self.next_button = QPushButton("Next")
        self.prev_button.clicked.connect(self.prev_page)
        self.next_button.clicked.connect(self.next_page)


        self.button_layout.addWidget(self.prev_button)
        self.button_layout.addWidget(self.next_button)


        self.layout.addLayout(self.grid_layout)
        self.layout.addLayout(self.button_layout)
        self.setLayout(self.layout)

        self.watcher = QFileSystemWatcher()
        self.watcher.addPath(self.folder1)
        self.watcher.addPath(self.folder2)
        self.watcher.directoryChanged.connect(self.update_images)


        self.folder1_images = []
        self.folder2_images = []
        self.update_images()


        self.showFullScreen()

    def update_images(self):
        self.folder1_images = sorted(
            [os.path.join(self.folder1, f) for f in os.listdir(self.folder1) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        )
        self.folder2_images = sorted(
            [os.path.join(self.folder2, f) for f in os.listdir(self.folder2) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        )

        max_len = max(len(self.folder1_images), len(self.folder2_images))
        self.folder1_images += [None] * (max_len - len(self.folder1_images))
        self.folder2_images += [None] * (max_len - len(self.folder2_images))

        self.update_grid()

    def update_grid(self):
        start_idx = self.current_page * self.images_per_page
        end_idx = start_idx + self.images_per_page

        current_images1 = self.folder1_images[start_idx:end_idx]
        current_images2 = self.folder2_images[start_idx:end_idx]

        screen_width = self.width()
        screen_height = self.height()

        for row in range(2):
            if row < len(current_images1) and current_images1[row]:
                pixmap = QPixmap(current_images1[row])
                self.image_labels[row][0].setPixmap(pixmap.scaled(screen_width // 2, screen_height // 2, Qt.KeepAspectRatio))
            else:
                self.image_labels[row][0].clear()

            if row < len(current_images2) and current_images2[row]:
                pixmap = QPixmap(current_images2[row])
                self.image_labels[row][1].setPixmap(pixmap.scaled(screen_width // 2, screen_height // 2, Qt.KeepAspectRatio))
            else:
                self.image_labels[row][1].clear()


        self.prev_button.setEnabled(self.current_page > 0)
        self.next_button.setEnabled(end_idx < len(self.folder1_images) or end_idx < len(self.folder2_images))

    def next_page(self):
        if (self.current_page + 1) * self.images_per_page < len(self.folder1_images) or \
           (self.current_page + 1) * self.images_per_page < len(self.folder2_images):
            self.current_page += 1
            self.update_grid()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_grid()

if __name__ == "__main__":
    folder1 = "runtime/20250210_005132_flight_testing/annotated_detections"
    folder2 = "runtime/20250210_005132_flight_testing/source"

    app = QApplication(sys.argv)
    window = ImageMonitor(folder1, folder2)
    window.setWindowTitle("Image Viewer")
    sys.exit(app.exec_())