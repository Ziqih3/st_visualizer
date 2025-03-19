from PyQt5.QtWidgets import (QSlider, QLabel, QVBoxLayout, QHBoxLayout,
                             QWidget, QFrame, QPushButton, QSizePolicy)
from PyQt5.QtCore import Qt, QDateTime, pyqtSignal, QSize
from PyQt5.QtGui import QFont


class FloatSlider(QFrame):
    """
    A custom slider widget that displays time information at different positions.
    It allows for a draggable slider with time labels showing timestamp and datetime formats.
    
    Signals:
        valueChanged(float): Emitted when the slider value changes, with normalized value between 0 and 1
        timeChanged(QDateTime): Emitted when the time changes, with the current QDateTime
    """
    valueChanged = pyqtSignal(float)
    timeChanged = pyqtSignal(QDateTime)  # New signal to emit the current time

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)

        # Set maximum height for the entire widget
        self.setMaximumHeight(60)

        # Set size policy to prevent vertical expansion
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Setup main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 2, 10, 2)
        self.main_layout.setSpacing(1)

        # Initialize time values
        self.start_time = QDateTime.currentDateTime()
        self.end_time = self.start_time.addDays(1)

        # For fine-grained control, we'll use a much higher range of values
        # This gives us approximately millisecond precision
        self.slider_max_value = 1000000  # 1 million steps for fine control

        # Create slider with finer resolution
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(self.slider_max_value)
        self.slider.setValue(0)
        self.slider.setTickPosition(
            QSlider.NoTicks)  # Remove ticks for smoother appearance
        self.slider.setMaximumHeight(20)
        self.slider.setMinimumHeight(15)

        # Enable tracking for real-time updates while dragging
        self.slider.setTracking(True)

        # Create labels for time values
        self.start_label = QLabel()
        self.current_label = QLabel()
        self.end_label = QLabel()

        # Set font styles for the labels
        self._setup_label_styles()

        # Setup label layout
        time_labels_layout = self._create_labels_layout()

        # Add widgets to main layout
        self.main_layout.addLayout(time_labels_layout)
        self.main_layout.addWidget(self.slider)

        # Connect signals for real-time updates
        self.slider.valueChanged.connect(self._handle_slider_change)

        # Initialize the labels
        self.update_time_labels()
        self.update_current_time()

    def sizeHint(self):
        """Provide size hint to the layout system"""
        return QSize(800, 40)

    def _setup_label_styles(self):
        """Set up styles for the time labels"""
        label_font = QFont("Consolas", 8)

        # Apply styles to all labels
        for label in [self.start_label, self.current_label, self.end_label]:
            label.setFont(label_font)
            label.setAlignment(Qt.AlignCenter)
            label.setMaximumHeight(20)

        # Current time label styling - make it stand out
        self.current_label.setStyleSheet("color: #0066cc; font-weight: bold;")

    def _create_labels_layout(self):
        """Create and return the layout for time labels"""
        time_labels_layout = QHBoxLayout()
        time_labels_layout.setContentsMargins(0, 0, 0, 0)
        time_labels_layout.setSpacing(2)

        # Add all three labels to the horizontal layout
        time_labels_layout.addWidget(self.start_label)
        time_labels_layout.addStretch()
        time_labels_layout.addWidget(self.current_label)
        time_labels_layout.addStretch()
        time_labels_layout.addWidget(self.end_label)

        return time_labels_layout

    def _handle_slider_change(self, value):
        """Handle slider value changes and emit normalized value and current time"""
        # Convert to normalized value (0 to 1)
        normalized_value = value / self.slider_max_value

        # Calculate current time
        total_millis = int((self.end_time.toMSecsSinceEpoch() -
                            self.start_time.toMSecsSinceEpoch()))
        current_millis = int(total_millis * normalized_value)
        current_time_ms = self.start_time.toMSecsSinceEpoch() + current_millis

        # Create QDateTime from milliseconds
        current_time = QDateTime.fromMSecsSinceEpoch(current_time_ms)

        # Update the current time label
        self.update_current_time(current_time)

        # Emit signals
        self.valueChanged.emit(normalized_value)
        self.timeChanged.emit(current_time)

    def update_time_labels(self):
        """Update the start and end time labels"""
        # Start time with 'Start:' prefix
        self.start_label.setText(
            f"Start: {self.start_time.toString('yyyy-MM-dd hh:mm:ss.zzz')}")

        # End time with 'End:' prefix
        self.end_label.setText(
            f"End: {self.end_time.toString('yyyy-MM-dd hh:mm:ss.zzz')}")

    def update_current_time(self, current_time=None):
        """Update the current time label
        
        Args:
            current_time (QDateTime, optional): The current time to display. If None,
                                               it will be calculated from the slider value.
        """
        if current_time is None:
            # Calculate current time based on slider position
            slider_value = self.slider.value()
            normalized_value = slider_value / self.slider_max_value

            total_millis = int((self.end_time.toMSecsSinceEpoch() -
                                self.start_time.toMSecsSinceEpoch()))
            current_millis = int(total_millis * normalized_value)
            current_time_ms = self.start_time.toMSecsSinceEpoch(
            ) + current_millis

            # Create QDateTime from milliseconds
            current_time = QDateTime.fromMSecsSinceEpoch(current_time_ms)

        # Update label with millisecond precision
        self.current_label.setText(
            f"{current_time.toString('yyyy-MM-dd hh:mm:ss.zzz')}")

    def set_time_range(self, start_time, end_time):
        """Set the time range for the slider
        
        Args:
            start_time (QDateTime): The start time
            end_time (QDateTime): The end time
        """
        self.start_time = start_time
        self.end_time = end_time

        # Make sure end time is after start time
        if self.end_time <= self.start_time:
            self.end_time = self.start_time.addSecs(
                3600)  # Add at least 1 hour

        self.update_time_labels()
        self.update_current_time()

    def get_current_time(self):
        """Get the current time based on slider position
        
        Returns:
            QDateTime: The current time
        """
        # Calculate current time with millisecond precision
        slider_value = self.slider.value()
        normalized_value = slider_value / self.slider_max_value

        total_millis = int((self.end_time.toMSecsSinceEpoch() -
                            self.start_time.toMSecsSinceEpoch()))
        current_millis = int(total_millis * normalized_value)
        current_time_ms = self.start_time.toMSecsSinceEpoch() + current_millis

        return QDateTime.fromMSecsSinceEpoch(current_time_ms)

    def get_normalized_value(self):
        """Get the normalized slider value (0-1)
        
        Returns:
            float: The normalized value between 0 and 1
        """
        return self.slider.value() / self.slider_max_value

    def set_normalized_value(self, value):
        """Set the slider position using a normalized value
        
        Args:
            value (float): A value between 0 and 1
        """
        slider_value = int(value * self.slider_max_value)
        self.slider.setValue(slider_value)

    def set_time(self, time):
        """Set the slider position based on a specific time
        
        Args:
            time (QDateTime): The time to set the slider to
        """
        if time < self.start_time or time > self.end_time:
            return  # Time is outside our range

        # Calculate normalized position
        total_millis = self.end_time.toMSecsSinceEpoch(
        ) - self.start_time.toMSecsSinceEpoch()
        elapsed_millis = time.toMSecsSinceEpoch(
        ) - self.start_time.toMSecsSinceEpoch()
        normalized_value = elapsed_millis / total_millis

        # Set slider value (will trigger update via signals)
        self.set_normalized_value(normalized_value)


# Example usage
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel

    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle("Float Slider Demo")
    window.setGeometry(100, 100, 800, 400)

    # Create central widget with layout
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)

    # Add a placeholder to take up space
    placeholder = QLabel("Content Area")
    placeholder.setAlignment(Qt.AlignCenter)
    placeholder.setStyleSheet(
        "background-color: #f0f0f0; border: 1px solid #ddd;")
    placeholder.setMinimumHeight(200)

    # Add the slider at the bottom
    slider = FloatSlider()

    # Add widgets to layout
    layout.addWidget(placeholder, 1)
    layout.addWidget(slider, 0)

    # Connect to value change signal
    slider.valueChanged.connect(
        lambda value: print(f"Value changed: {value:.6f}"))

    window.show()
    sys.exit(app.exec_())
