"""
Cavity Control GUI
Author: Andrei Militaru (event handlers and logic), GitHub Copilot (layout and structure)
Organization: Institute of Science and Technology Austria (ISTA)
Date: October 2025
Description: GUI for controlling narrow-linewidth optical cavity with 
demodulation recorder and function generator.
"""

import sys
from experiment_interface.mach_zehnder_utils.mach_zehnder_lock import df2tc
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QDoubleSpinBox, QCheckBox, QComboBox, QPushButton,
    QGroupBox, QGridLayout, QFrame, QSizePolicy, QTabWidget,
    QSlider
)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont, QIcon


class CavityControlGUI(QMainWindow):
    """Main GUI for optical cavity control"""
    # Update waveform list to match device capabilities, removing triangle
    WAVEFORMS = ["sin", "square", "ramp"]

    def __init__(self, mdrec=None, fg=None, parent=None, device_id=None,
                  dither_pid=None, dither_drive_demod=None, dither_in_demod=None,
                  verbose=False):
        """Initialize the GUI with optional verbose mode"""
        super().__init__(parent)
        self.verbose = verbose
        self.mdrec = mdrec
        self.fg = fg
        self.device_id = device_id
        self.dither_pid = dither_pid
        self.dither_drive_demod = dither_drive_demod
        self.dither_in_demod = dither_in_demod

        # Initialize UI
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle('Optical Cavity Control')
        self.setGeometry(100, 100, 800, 600)

        # Create central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        # Create two main panels
        top_panel = self.create_controls_panel()
        bottom_panel = self.create_monitoring_panel()

        # Add panels to main layout
        main_layout.addWidget(top_panel, 3)  # Control panel takes more space
        main_layout.addWidget(bottom_panel, 1)

        # Set central widget
        self.setCentralWidget(central_widget)
        # Set initial values from devices
        self.set_initial_values_from_devices()

    def get_mdrec_p_gain(self):
        """Get P gain from mdrec"""
        response = self.mdrec.lock_in.get(f'/{self.device_id}/pids/{self.dither_pid}/p')
        return float(response[self.device_id]['pids'][str(self.dither_pid)]['p']['value'][0])

    def get_mdrec_i_gain(self):
        """Get I gain from mdrec"""
        response = self.mdrec.lock_in.get(f'/{self.device_id}/pids/{self.dither_pid}/i') 
        return float(response[self.device_id]['pids'][str(self.dither_pid)]['i']['value'][0])

    def get_mdrec_bandwidth(self):
        """Get bandwidth from mdrec"""
        response = self.mdrec.lock_in.get(f'/{self.device_id}/pids/{self.dither_pid}/demod/timeconstant')
        return df2tc(float(response[self.device_id]['pids'][str(self.dither_pid)]['demod']['timeconstant']['value'][0]))

    def get_mdrec_pid_enabled(self):
        """Get PID enabled state from mdrec"""
        response = self.mdrec.lock_in.get(f'/{self.device_id}/pids/{self.dither_pid}/enable')
        return float(response[self.device_id]['pids'][str(self.dither_pid)]['enable']['value'][0]) == 1

    def get_mdrec_keep_i(self):
        """Get keep I value from mdrec"""
        response = self.mdrec.lock_in.get(f'/{self.device_id}/pids/{self.dither_pid}/keepint')
        return float(response[self.device_id]['pids'][str(self.dither_pid)]['keepint']['value'][0]) == 1

    def get_mdrec_output_offset(self):
        """Get output offset from mdrec"""
        response = self.mdrec.lock_in.get(f'/{self.device_id}/sigouts/0/offset')
        return float(response[self.device_id]['sigouts']['0']['offset']['value'][0])

    def get_mdrec_dither_freq(self):
        """Get dither frequency from mdrec"""
        response = self.mdrec.lock_in.get(f'/{self.device_id}/oscs/{self.dither_drive_demod}/freq')
        # Convert Hz to kHz for display
        return float(response[self.device_id]['oscs'][str(self.dither_drive_demod)]['freq']['value'][0]) / 1000.0

    def get_mdrec_dither_strength(self):
        """Get dither strength from mdrec"""
        response = self.mdrec.lock_in.get(f'/{self.device_id}/sigouts/0/amplitudes/{self.dither_drive_demod}')
        return float(response[self.device_id]['sigouts']['0']['amplitudes'][str(self.dither_drive_demod)]['value'][0])

    def get_mdrec_demod_phase(self):
        """Get demodulation phase from mdrec"""
        response = self.mdrec.lock_in.get(f'/{self.device_id}/demods/{self.dither_in_demod}/phaseshift')
        return float(response[self.device_id]['demods'][str(self.dither_in_demod)]['phaseshift']['value'][0])

    def get_fg_waveform(self):
        """Get waveform from fg"""
        # Strip any whitespace and convert to lowercase to ensure proper matching
        return self.fg.out_waveform.strip().lower()

    def get_fg_amplitude(self):
        """Get amplitude from fg in mV"""
        return self.fg.out_amplitude * 1000  # Convert V to mV

    def get_fg_frequency(self):
        """Get frequency from fg"""
        return self.fg.out_frequency

    def get_fg_offset(self):
        """Get offset from fg"""
        return self.fg.out_offset

    def get_fg_output_enabled(self):
        """Get output enabled state from fg"""
        return self.fg.out

    def get_mdrec_dither_enable(self):
        """Get dither enable state from mdrec"""
        response = self.mdrec.lock_in.get(f'/{self.device_id}/sigouts/0/enables/{self.dither_drive_demod}')
        return float(response[self.device_id]['sigouts']['0']['enables'][str(self.dither_drive_demod)]['value'][0]) == 1

    def set_initial_values_from_devices(self):
        """Set initial values for widgets from mdrec and fg"""
        if self.mdrec:
            # Block signals during initialization to prevent unnecessary updates
            self.p_gain_spinbox.blockSignals(True)
            self.i_gain_spinbox.blockSignals(True)
            self.bandwidth_spinbox.blockSignals(True)
            self.pid_enable_checkbox.blockSignals(True)
            self.keep_i_checkbox.blockSignals(True)
            self.offset_spinbox.blockSignals(True)
            self.dither_freq_spinbox.blockSignals(True)
            self.dither_strength_spinbox.blockSignals(True)
            self.demod_phase_spinbox.blockSignals(True)
            
            # Set values
            self.p_gain_spinbox.setValue(self.get_mdrec_p_gain())
            self.i_gain_spinbox.setValue(self.get_mdrec_i_gain())
            self.bandwidth_spinbox.setValue(self.get_mdrec_bandwidth())
            self.pid_enable_checkbox.setChecked(self.get_mdrec_pid_enabled())
            self.keep_i_checkbox.setChecked(self.get_mdrec_keep_i())
            
            # Get offset value first and block signals
            self.offset_spinbox.blockSignals(True)
            self.offset_slider.blockSignals(True)
            
            # Get current offset value from device
            offset_value = self.get_mdrec_output_offset()
            
            # Set base offset to the device value and initialize fine adjustment to 0
            self.base_offset = offset_value
            
            # Initialize fine offset slider to 0
            self.fine_offset_slider.blockSignals(True)
            self.fine_offset_slider.setValue(0)
            self.fine_offset_label.setText("0.0 mV")
            self.fine_offset_slider.blockSignals(False)
            
            # Set spinbox to the total (which is just base offset now)
            self.offset_spinbox.blockSignals(True)
            self.offset_spinbox.setValue(offset_value)
            self.offset_spinbox.blockSignals(False)
            
            # Set slider to match base offset
            self.offset_slider.blockSignals(True)
            self.offset_slider.setValue(int(offset_value * 100))
            self.offset_slider.blockSignals(False)
            
            # Update status indicators after setting values
            self.output_value_label.setText(f"{offset_value:.3f} V")
            self.update_status_indicators()
            
            # Unblock signals after setting values
            self.p_gain_spinbox.blockSignals(False)
            self.i_gain_spinbox.blockSignals(False)
            self.bandwidth_spinbox.blockSignals(False)
            self.pid_enable_checkbox.blockSignals(False)
            self.keep_i_checkbox.blockSignals(False)
            self.offset_spinbox.blockSignals(False)
            self.dither_freq_spinbox.blockSignals(False)
            self.dither_strength_spinbox.blockSignals(False)
            self.demod_phase_spinbox.blockSignals(False)
            
        if self.fg:
            # Block signals for FG controls
            self.waveform_combo.blockSignals(True)
            self.amplitude_spinbox.blockSignals(True)
            self.freq_spinbox.blockSignals(True)
            self.fg_offset_spinbox.blockSignals(True)
            self.output_checkbox.blockSignals(True)
            
            # Set values
            self.waveform_combo.setCurrentText(self.get_fg_waveform())
            self.amplitude_spinbox.setValue(self.get_fg_amplitude())
            self.freq_spinbox.setValue(self.get_fg_frequency())
            self.fg_offset_spinbox.setValue(self.get_fg_offset())
            self.output_checkbox.setChecked(self.get_fg_output_enabled())
            
            # Unblock signals
            self.waveform_combo.blockSignals(False)
            self.amplitude_spinbox.blockSignals(False)
            self.freq_spinbox.blockSignals(False)
            self.fg_offset_spinbox.blockSignals(False)
            self.output_checkbox.blockSignals(False)

        # Initialize fine offset slider to 0
        self.fine_offset_slider.blockSignals(True)
        self.fine_offset_slider.setValue(0)  # Always start at 0
        self.fine_offset_label.setText("0.0 mV")
        self.fine_offset_slider.blockSignals(False)

    def create_controls_panel(self):
        """Create the main controls panel with tabs"""
        panel = QTabWidget()
        
        # Create tabs for different control groups
        pid_tab = self.create_pid_controls()
        fg_tab = self.create_fg_controls()
        demod_tab = self.create_demod_controls()
        
        # Add tabs to panel
        panel.addTab(pid_tab, "PID Controls")
        panel.addTab(fg_tab, "Function Generator")
        panel.addTab(demod_tab, "Demodulation Settings")
        
        return panel
    
    def create_pid_controls(self):
        """Create PID controller controls"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # PID Parameters Group
        pid_group = QGroupBox("PID Parameters")
        pid_layout = QGridLayout()

        # P Gain
        pid_layout.addWidget(QLabel("P Gain:"), 0, 0)
        self.p_gain_spinbox = QDoubleSpinBox()
        self.p_gain_spinbox.setRange(-1000000, 1000000)
        self.p_gain_spinbox.setValue(0.0)
        self.p_gain_spinbox.setDecimals(3)
        self.p_gain_spinbox.setSingleStep(0.1)
        self.p_gain_spinbox.setKeyboardTracking(False)  # Only update when Enter is pressed
        self.p_gain_spinbox.valueChanged.connect(self.on_p_gain_changed)
        pid_layout.addWidget(self.p_gain_spinbox, 0, 1)

        # I Gain
        pid_layout.addWidget(QLabel("I Gain:"), 1, 0)
        self.i_gain_spinbox = QDoubleSpinBox()
        self.i_gain_spinbox.setRange(-1000000, 1000000)
        self.i_gain_spinbox.setValue(0.0)
        self.i_gain_spinbox.setDecimals(3)
        self.i_gain_spinbox.setSingleStep(0.1)
        self.i_gain_spinbox.setKeyboardTracking(False)  # Only update when Enter is pressed
        self.i_gain_spinbox.valueChanged.connect(self.on_i_gain_changed)
        pid_layout.addWidget(self.i_gain_spinbox, 1, 1)

        # Bandwidth
        pid_layout.addWidget(QLabel("Bandwidth (Hz):"), 2, 0)
        self.bandwidth_spinbox = QDoubleSpinBox()
        self.bandwidth_spinbox.setRange(0.1, 1000000)
        self.bandwidth_spinbox.setValue(100.0)
        self.bandwidth_spinbox.setDecimals(1)
        self.bandwidth_spinbox.setSingleStep(10)
        self.bandwidth_spinbox.setKeyboardTracking(False)  # Only update when Enter is pressed
        self.bandwidth_spinbox.valueChanged.connect(self.on_bandwidth_changed)
        pid_layout.addWidget(self.bandwidth_spinbox, 2, 1)

        # PID Enable
        pid_layout.addWidget(QLabel("PID Enable:"), 3, 0)
        self.pid_enable_checkbox = QCheckBox()
        self.pid_enable_checkbox.setChecked(False)
        self.pid_enable_checkbox.stateChanged.connect(self.on_pid_enable_changed)
        pid_layout.addWidget(self.pid_enable_checkbox, 3, 1)

        # Keep I Value
        pid_layout.addWidget(QLabel("Keep I Value:"), 4, 0)
        self.keep_i_checkbox = QCheckBox()
        self.keep_i_checkbox.setChecked(True)
        self.keep_i_checkbox.stateChanged.connect(self.on_keep_i_changed)
        pid_layout.addWidget(self.keep_i_checkbox, 4, 1)

        pid_group.setLayout(pid_layout)
        layout.addWidget(pid_group)

        # Output Settings Group
        output_group = QGroupBox("Output Settings")
        output_layout = QGridLayout()

        # Output Signal Offset (now shows total including fine adjustment)
        output_layout.addWidget(QLabel("Total Output (V):"), 0, 0)
        self.offset_spinbox = QDoubleSpinBox()
        self.offset_spinbox.setRange(0, 5.0)
        # Default to 2V instead of 0V for better starting point
        self.offset_spinbox.setValue(2.0)
        self.offset_spinbox.setDecimals(3)
        self.offset_spinbox.setSingleStep(0.01)
        self.offset_spinbox.setKeyboardTracking(False)  # Only update when Enter is pressed
        self.offset_spinbox.valueChanged.connect(self.on_offset_changed)
        output_layout.addWidget(self.offset_spinbox, 0, 1)

        # Add a slider for visual control of offset - update range to match 0-5V
        self.offset_slider = QSlider(Qt.Horizontal)
        self.offset_slider.setRange(0, 500)  # 0-5V with 0.01V resolution
        self.offset_slider.setValue(200)  # Default to 2.0V (matching spinbox)
        self.offset_slider.valueChanged.connect(self.on_offset_slider_changed)
        output_layout.addWidget(self.offset_slider, 1, 0, 1, 2)

        # Fine offset adjustment
        output_layout.addWidget(QLabel("Fine Adjustment (mV):"), 2, 0)
        self.fine_offset_slider = QSlider(Qt.Horizontal)
        self.fine_offset_slider.setRange(-25, 25)  # -25mV to +25mV (each step is 1mV)
        self.fine_offset_slider.setValue(0)
        self.fine_offset_slider.setTickPosition(QSlider.TicksBelow)
        self.fine_offset_slider.setTickInterval(5)  # Ticks at -25, -20, ..., 20, 25 mV
        self.fine_offset_slider.valueChanged.connect(self.on_fine_offset_slider_changed)
        output_layout.addWidget(self.fine_offset_slider, 2, 1)
        
        # Fine offset value display
        self.fine_offset_label = QLabel("0.0 mV")
        output_layout.addWidget(self.fine_offset_label, 3, 1)
        
        # Store the base offset (without fine adjustment) as an instance variable
        self.base_offset = 2.0  # Default to 2.0V

        # Remove the separate Total Output display since spinbox now shows total

        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

        # Add stretch to push controls to the top
        layout.addStretch()

        # Set initial state of offset based on PID enable
        self.update_offset_spinbox_state()

        return widget
    
    def create_fg_controls(self):
        """Create function generator controls"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Function Generator Settings Group
        fg_group = QGroupBox("Function Generator Settings")
        fg_layout = QGridLayout()

        # Waveform Selection
        fg_layout.addWidget(QLabel("Waveform:"), 0, 0)
        self.waveform_combo = QComboBox()
        # Modify the waveform combo box initialization to use class attribute
        self.waveform_combo.addItems(self.WAVEFORMS)
        self.waveform_combo.currentIndexChanged.connect(self.on_waveform_changed)
        fg_layout.addWidget(self.waveform_combo, 0, 1)

        # Amplitude (in mV)
        fg_layout.addWidget(QLabel("Amplitude (mV):"), 1, 0)
        self.amplitude_spinbox = QDoubleSpinBox()
        self.amplitude_spinbox.setRange(0.0, 10000.0)  # 0-10V in mV
        self.amplitude_spinbox.setValue(1000.0)  # Default 1V = 1000mV
        self.amplitude_spinbox.setDecimals(1)
        self.amplitude_spinbox.setSingleStep(1.0)
        self.amplitude_spinbox.setKeyboardTracking(False)
        self.amplitude_spinbox.valueChanged.connect(self.on_amplitude_changed)
        fg_layout.addWidget(self.amplitude_spinbox, 1, 1)

        # Amplitude fine adjustment
        fg_layout.addWidget(QLabel("Fine Adjustment (mV):"), 2, 0)
        self.amplitude_fine_slider = QSlider(Qt.Horizontal)
        self.amplitude_fine_slider.setRange(-50, 50)  # ±50mV adjustment
        self.amplitude_fine_slider.setValue(0)
        self.amplitude_fine_slider.setTickPosition(QSlider.TicksBelow)
        self.amplitude_fine_slider.setTickInterval(10)
        self.amplitude_fine_slider.valueChanged.connect(self.on_amplitude_fine_changed)
        fg_layout.addWidget(self.amplitude_fine_slider, 2, 1)
        
        # Fine adjustment value display
        self.amplitude_fine_label = QLabel("0 mV")
        fg_layout.addWidget(self.amplitude_fine_label, 3, 1)

        # Frequency
        fg_layout.addWidget(QLabel("Frequency (Hz):"), 4, 0)
        self.freq_spinbox = QDoubleSpinBox()
        self.freq_spinbox.setRange(0.01, 1000000)
        self.freq_spinbox.setValue(1000.0)
        self.freq_spinbox.setDecimals(1)
        self.freq_spinbox.setSingleStep(100)
        self.freq_spinbox.setKeyboardTracking(False)  # Only update when Enter is pressed
        self.freq_spinbox.valueChanged.connect(self.on_freq_changed)
        fg_layout.addWidget(self.freq_spinbox, 4, 1)

        # Auto-calculated offset display
        fg_layout.addWidget(QLabel("Total Offset (mV):"), 5, 0)
        self.fg_offset_spinbox = QDoubleSpinBox()
        self.fg_offset_spinbox.setRange(-5000.0, 5000.0)  # ±5V in mV
        self.fg_offset_spinbox.setValue(0.0)
        self.fg_offset_spinbox.setDecimals(1)
        self.fg_offset_spinbox.setButtonSymbols(QDoubleSpinBox.NoButtons)
        self.fg_offset_spinbox.setReadOnly(True)
        self.fg_offset_spinbox.setStyleSheet("background-color: #f0f0f0;")
        fg_layout.addWidget(self.fg_offset_spinbox, 5, 1)

        # Output Toggle
        fg_layout.addWidget(QLabel("Output:"), 6, 0)
        self.output_checkbox = QCheckBox("Enabled")
        self.output_checkbox.setChecked(False)
        self.output_checkbox.stateChanged.connect(self.on_output_toggled)
        fg_layout.addWidget(self.output_checkbox, 6, 1)

        fg_group.setLayout(fg_layout)
        layout.addWidget(fg_group)

        # Add stretch to push controls to the top
        layout.addStretch()

        return widget
    
    def create_demod_controls(self):
        """Create demodulation controls"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Dither Tone Group
        dither_group = QGroupBox("Dither Tone")
        dither_layout = QGridLayout()
        
        # Dither Frequency (now in kHz)
        dither_layout.addWidget(QLabel("Frequency (kHz):"), 0, 0)
        self.dither_freq_spinbox = QDoubleSpinBox()
        self.dither_freq_spinbox.setRange(0.0001, 100.0)  # 0.1 Hz to 100 kHz
        self.dither_freq_spinbox.setValue(0.1)  # Default 100 Hz = 0.1 kHz
        self.dither_freq_spinbox.setDecimals(3)
        self.dither_freq_spinbox.setSingleStep(0.1)
        self.dither_freq_spinbox.setKeyboardTracking(False)
        self.dither_freq_spinbox.valueChanged.connect(self.on_dither_freq_changed)
        dither_layout.addWidget(self.dither_freq_spinbox, 0, 1)
        
        # Dither Drive Strength
        dither_layout.addWidget(QLabel("Drive Strength (mV):"), 1, 0)
        self.dither_strength_spinbox = QDoubleSpinBox()
        self.dither_strength_spinbox.setRange(0.0, 1000.0)  # 0-1000 mV range
        self.dither_strength_spinbox.setValue(100.0)  # Default 100 mV
        self.dither_strength_spinbox.setDecimals(3)
        self.dither_strength_spinbox.setSingleStep(1)
        self.dither_strength_spinbox.setKeyboardTracking(False)  # Only update when Enter is pressed
        self.dither_strength_spinbox.valueChanged.connect(self.on_dither_strength_changed)
        dither_layout.addWidget(self.dither_strength_spinbox, 1, 1)
        
        # Enable dither (checkbox)
        dither_layout.addWidget(QLabel("Enable Dither:"), 2, 0)
        self.dither_enable_checkbox = QCheckBox()
        self.dither_enable_checkbox.setChecked(True)
        self.dither_enable_checkbox.stateChanged.connect(self.on_dither_enable_changed)
        dither_layout.addWidget(self.dither_enable_checkbox, 2, 1)

        dither_group.setLayout(dither_layout)
        layout.addWidget(dither_group)
        
        # Demodulation Phase Group
        demod_group = QGroupBox("Demodulation")
        demod_layout = QGridLayout()
        
        # Demodulation Phase
        demod_layout.addWidget(QLabel("Phase (deg):"), 0, 0)
        self.demod_phase_spinbox = QDoubleSpinBox()
        self.demod_phase_spinbox.setRange(-180.0, 180.0)
        self.demod_phase_spinbox.setValue(0.0)
        self.demod_phase_spinbox.setDecimals(1)
        self.demod_phase_spinbox.setSingleStep(1.0)
        self.demod_phase_spinbox.setKeyboardTracking(False)  # Only update when Enter is pressed
        self.demod_phase_spinbox.valueChanged.connect(self.on_demod_phase_changed)
        demod_layout.addWidget(self.demod_phase_spinbox, 0, 1)
        
        # Phase adjustment slider
        self.phase_slider = QSlider(Qt.Horizontal)
        self.phase_slider.setRange(-180, 180)
        self.phase_slider.setValue(0)
        self.phase_slider.valueChanged.connect(self.on_phase_slider_changed)
        demod_layout.addWidget(self.phase_slider, 1, 0, 1, 2)
        
        demod_group.setLayout(demod_layout)
        layout.addWidget(demod_group)
        
        # Add stretch to push controls to the top
        layout.addStretch()
        
        return widget
    
    def create_monitoring_panel(self):
        """Create the monitoring panel"""
        panel = QGroupBox("Status")
        layout = QGridLayout(panel)
        
        # Status labels
        layout.addWidget(QLabel("PID Status:"), 0, 0)
        self.pid_status_label = QLabel("Unlocked")
        self.pid_status_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(self.pid_status_label, 0, 1)
        
        layout.addWidget(QLabel("Output Value:"), 1, 0)
        self.output_value_label = QLabel("0.000 V")
        layout.addWidget(self.output_value_label, 1, 1)
        
        layout.addWidget(QLabel("Function Generator:"), 0, 2)
        self.fg_status_label = QLabel("Inactive")
        layout.addWidget(self.fg_status_label, 0, 3)
        
        layout.addWidget(QLabel("Dither Status:"), 1, 2)
        self.dither_status_label = QLabel("Enabled")
        self.dither_status_label.setStyleSheet("color: green;")
        layout.addWidget(self.dither_status_label, 1, 3)
        
        # Add spacer item to push status labels to the left
        layout.setColumnStretch(4, 1)
        
        return panel
    
    def update_offset_spinbox_state(self):
        """Update the state of the offset spinbox based on PID enable"""
        is_pid_enabled = self.pid_enable_checkbox.isChecked()
        self.offset_spinbox.setEnabled(not is_pid_enabled)
        self.offset_slider.setEnabled(not is_pid_enabled)
        self.fine_offset_slider.setEnabled(not is_pid_enabled)  # Also disable fine adjustment
        
        # Update the appearance to indicate it's disabled
        if is_pid_enabled:
            self.offset_spinbox.setStyleSheet("background-color: #f0f0f0;")
            self.offset_slider.setStyleSheet("background-color: #f0f0f0;")
            self.fine_offset_slider.setStyleSheet("background-color: #f0f0f0;")
            self.fine_offset_label.setStyleSheet("color: #a0a0a0;")
        else:
            self.offset_spinbox.setStyleSheet("")
            self.offset_slider.setStyleSheet("")
            self.fine_offset_slider.setStyleSheet("")
            self.fine_offset_label.setStyleSheet("")

    def update_status_indicators(self):
        """Update status indicators based on current state"""
        # PID status indicator
        if self.pid_enable_checkbox.isChecked():
            self.pid_status_label.setText("Locked")
            self.pid_status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.pid_status_label.setText("Unlocked")
            self.pid_status_label.setStyleSheet("color: red; font-weight: bold;")
            
        # FG status indicator
        if self.output_checkbox.isChecked():
            self.fg_status_label.setText(f"Active ({self.waveform_combo.currentText()})")
            self.fg_status_label.setStyleSheet("color: green;")
        else:
            self.fg_status_label.setText("Inactive")
            self.fg_status_label.setStyleSheet("color: gray;")
            
        # Dither status indicator
        if self.dither_enable_checkbox.isChecked():
            self.dither_status_label.setText("Enabled")
            self.dither_status_label.setStyleSheet("color: green;")
        else:
            self.dither_status_label.setText("Disabled")
            self.dither_status_label.setStyleSheet("color: gray;")
    
    # Event handlers for slider controls
    @pyqtSlot(int)
    def on_offset_slider_changed(self, value):
        """Handle offset slider change"""
        # Convert slider value (0-500) to voltage (0-5V) - this is the new base offset
        self.base_offset = value / 100.0
        
        # Get current fine adjustment in volts
        fine_offset_v = (self.fine_offset_slider.value() * 0.5) / 1000.0
        
        # Calculate total offset
        total_offset_v = self.base_offset + fine_offset_v
        
        # Update spinbox with total value (without triggering valueChanged signal)
        self.offset_spinbox.blockSignals(True)
        self.offset_spinbox.setValue(total_offset_v)
        self.offset_spinbox.blockSignals(False)
        
        # Apply to device if PID is disabled
        if self.mdrec and not self.pid_enable_checkbox.isChecked():
            self.mdrec.lock_in.set(f'/{self.device_id}/sigouts/0/offset', total_offset_v)
            self.output_value_label.setText(f"{total_offset_v:.3f} V")

    @pyqtSlot(int)
    def on_phase_slider_changed(self, value):
        """Handle phase slider change"""
        self.demod_phase_spinbox.setValue(float(value))
        # No need to call on_demod_phase_changed as the spinbox valueChanged signal will trigger it
    
    # Event handlers for PID controls
    @pyqtSlot(float)
    def on_p_gain_changed(self, value):
        """Handle P gain changed event"""
        if self.mdrec:
            self.log(f"P gain changed to {value}")
            self.mdrec.lock_in.set(f'/{self.device_id}/pids/{self.dither_pid}/p', value)

    @pyqtSlot(float)
    def on_i_gain_changed(self, value):
        """Handle I gain changed event"""
        if self.mdrec:
            self.log(f"I gain changed to {value}")
            self.mdrec.lock_in.set(f'/{self.device_id}/pids/{self.dither_pid}/i', value)

    @pyqtSlot(float)
    def on_bandwidth_changed(self, value):
        """Handle bandwidth changed event"""
        if self.mdrec:
            self.log(f"Bandwidth changed to {value}")
            self.mdrec.lock_in.set(f'/{self.device_id}/pids/{self.dither_pid}/demod/timeconstant', df2tc(value))

    @pyqtSlot(int)
    def on_pid_enable_changed(self, state):
        """Handle PID enable changed event"""
        enabled = state == Qt.Checked
        if self.mdrec:
            self.log(f"PID enable changed to {enabled}")
            self.mdrec.lock_in.set(f'/{self.device_id}/pids/{self.dither_pid}/enable', int(enabled))
        self.update_offset_spinbox_state()
        self.update_status_indicators()
        if not enabled and self.mdrec:
            # When disabling PID, set output offset to current offset spinbox value
            offset_value = self.offset_spinbox.value()
            self.log(f"Setting output offset to {offset_value} V on PID disable")
            offset_value = self.mdrec.lock_in.get(f'/{self.device_id}/sigouts/0/offset')

    @pyqtSlot(int)
    def on_keep_i_changed(self, state):
        """Handle keep I value changed event"""
        enabled = state == Qt.Checked
        if self.mdrec:
            self.log(f"Keep I value changed to {enabled}")
            self.mdrec.lock_in.set(f'/{self.device_id}/pids/{self.dither_pid}/keepint', int(enabled))

    @pyqtSlot(float)
    def on_offset_changed(self, value):
        """Handle offset changed event - now treats input as total value"""
        if self.mdrec and not self.pid_enable_checkbox.isChecked():
            # Apply the total offset directly to the device
            self.log(f"Total offset changed to {value:.3f} V")
            self.mdrec.lock_in.set(f'/{self.device_id}/sigouts/0/offset', value)
            
            # Calculate the new base offset by removing the fine adjustment
            fine_offset_v = (self.fine_offset_slider.value() * 0.5) / 1000.0
            self.base_offset = value - fine_offset_v
            
            # Update slider to match new base offset (not total)
            self.offset_slider.blockSignals(True)
            self.offset_slider.setValue(int(self.base_offset * 100))
            self.offset_slider.blockSignals(False)
            
            # Update status display
            self.output_value_label.setText(f"{value:.3f} V")

    @pyqtSlot(bool)
    def on_lock_toggled(self, checked):
        """Handle lock button toggle"""
        if self.pid_enable_checkbox.isChecked() != checked:
            self.pid_enable_checkbox.setChecked(checked)
        # No need to handle the actual locking as it's done in on_pid_enable_changed
    
    # Event handlers for dither and demod controls
    @pyqtSlot(float)
    def on_dither_freq_changed(self, value):
        """Handle dither frequency changed event (value in kHz)"""
        if self.mdrec:
            self.log(f"Dither frequency changed to {value:.3f} kHz")
            # Convert kHz to Hz for device setting
            self.mdrec.lock_in.set(f'/{self.device_id}/oscs/{self.dither_drive_demod}/freq', value * 1000.0)

    @pyqtSlot(float)
    def on_dither_strength_changed(self, value):
        """Handle dither strength changed event (value in mV)"""
        if self.mdrec:
            self.log(f"Dither strength changed to {value:.3f} mV")
            # Convert mV to V for device setting
            self.mdrec.lock_in.set(f'/{self.device_id}/sigouts/0/amplitudes/{self.dither_drive_demod}', value/1000.0)

    @pyqtSlot(int)
    def on_dither_enable_changed(self, state):
        """Handle dither enable changed event"""
        enabled = state == Qt.Checked
        if self.mdrec:
            self.log(f"Dither enable changed to {enabled}")
            self.mdrec.lock_in.set(f'/{self.device_id}/sigouts/0/enables/{self.dither_drive_demod}', int(enabled))
            self.update_status_indicators()

    @pyqtSlot(float)
    def on_demod_phase_changed(self, value):
        """Handle demodulation phase changed event"""
        if self.mdrec:
            self.log(f"Demodulation phase changed to {value:.1f} deg")
            self.mdrec.lock_in.set(f'/{self.device_id}/demods/{self.dither_in_demod}/phaseshift', value)
            # Fix the phase slider update by extracting the value from the response
            self.phase_slider.blockSignals(True)
            response = self.mdrec.lock_in.get(f'/{self.device_id}/demods/{self.dither_in_demod}/phaseshift')
            phase_value = float(response[self.device_id]['demods'][str(self.dither_in_demod)]['phaseshift']['value'][0])
            self.phase_slider.setValue(int(phase_value))
            self.phase_slider.blockSignals(False)
    
    # Event handlers for function generator controls
    @pyqtSlot(int)
    def on_waveform_changed(self, index):
        """Handle waveform selection changed event"""
        waveform = self.WAVEFORMS[index]  # Get waveform from index
        if self.fg:
            self.log(f"Waveform changed to {waveform}")
            self.fg.out_waveform = waveform  # Set waveform using fg's property
        self.update_status_indicators()
    
    @pyqtSlot(float)
    def on_amplitude_changed(self, value_mv):
        """Handle base amplitude changed event (value in mV)"""
        if self.fg:
            # Add the fine adjustment to get total amplitude
            total_amplitude_mv = value_mv + self.amplitude_fine_slider.value()
            value_v = total_amplitude_mv / 1000.0  # Convert mV to V
            self.log(f"Amplitude changed to {total_amplitude_mv:.1f} mV")
            self.fg.out_amplitude = value_v
            
            # Set offset to half of total amplitude
            offset_mv = total_amplitude_mv / 2.0
            offset_v = offset_mv / 1000.0
            self.fg.out_offset = offset_v
            self.fg_offset_spinbox.setValue(offset_mv)  # Update display in mV

    @pyqtSlot(int)
    def on_amplitude_fine_changed(self, fine_mv):
        """Handle fine amplitude adjustment changed event"""
        if self.fg:
            self.amplitude_fine_label.setText(f"{fine_mv:+d} mV")
            # Calculate total amplitude by adding fine adjustment to base
            total_amplitude_mv = self.amplitude_spinbox.value() + fine_mv
            value_v = total_amplitude_mv / 1000.0  # Convert mV to V
            self.log(f"Fine adjustment: {fine_mv:+d} mV, total amplitude: {total_amplitude_mv:.1f} mV")
            self.fg.out_amplitude = value_v
            
            # Set offset to half of total amplitude
            offset_mv = total_amplitude_mv / 2.0
            offset_v = offset_mv / 1000.0
            self.fg.out_offset = offset_v
            self.fg_offset_spinbox.setValue(offset_mv)  # Update display in mV

    @pyqtSlot(float)
    def on_freq_changed(self, value):
        """Handle frequency changed event"""
        if self.fg:
            self.log(f"Frequency changed to {value:.1f} Hz")
            self.fg.out_frequency = value

    @pyqtSlot(int)
    def on_output_toggled(self, state):
        """Handle output toggled event"""
        enabled = state == Qt.Checked
        if self.fg:
            self.log(f"Output toggled to {enabled}")
            self.fg.out = enabled
            self.update_status_indicators()

    @pyqtSlot(int)
    def on_fine_offset_slider_changed(self, value):
        """Handle fine offset slider change"""
        # Each step is 0.5mV (value goes from -25 to 25, so *0.5 gives -12.5 to +12.5 mV)
        fine_offset_mv = value * 0.5  # Changed back to 0.5 for finer control
        self.fine_offset_label.setText(f"{fine_offset_mv:+.1f} mV")
        
        # Calculate total offset
        fine_offset_v = fine_offset_mv / 1000.0  # Convert mV to V
        total_offset_v = self.base_offset + fine_offset_v
        
        # Update spinbox with total value (without triggering valueChanged signal)
        self.offset_spinbox.blockSignals(True)
        self.offset_spinbox.setValue(total_offset_v)
        self.offset_spinbox.blockSignals(False)
        
        # Apply to device if PID is disabled
        if self.mdrec and not self.pid_enable_checkbox.isChecked():
            self.log(f"Fine adjustment: {fine_offset_mv:+.1f} mV, total offset: {total_offset_v:.3f} V")
            self.mdrec.lock_in.set(f'/{self.device_id}/sigouts/0/offset', total_offset_v)
            self.output_value_label.setText(f"{total_offset_v:.3f} V")

    def log(self, message):
        """Log message if verbose mode is enabled"""
        if self.verbose:
            print(message)


# Example usage:
def main(mdrec=None, fg=None, device_id=None, dither_pid=None, dither_drive_demod=None, dither_in_demod=None, verbose=False):
    app = QApplication(sys.argv)
    # Set app style for consistent appearance across platforms
    app.setStyle("Fusion")
    
    # Assuming mdrec and fg are already initialized elsewhere
    window = CavityControlGUI(mdrec=mdrec, fg=fg, device_id=device_id, dither_pid=dither_pid,
                              dither_drive_demod=dither_drive_demod, dither_in_demod=dither_in_demod,
                              verbose=verbose)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    from experiment_interface.zhinst_utils.demodulation_recorder import zhinst_demod_recorder
    from experiment_interface.control.device.function_generator import SingleOutput

    ip_PC = '10.21.217.191'
    ip_fg = '10.21.217.150'
    device_id = 'dev30794'

    pid_dither = 1
    dither_drive_demod = 2
    dither_in_demod = 3

    # Use VISA resource string for function generator
    visa_resource_fg = f"TCPIP0::{ip_fg}::inst0::INSTR"

    dummy_test = False

    if not dummy_test:
        mdrec = zhinst_demod_recorder(ip_PC, devtype='MFLI')
        fg = SingleOutput(visa_resource_fg)
    else:
        mdrec = None 
        fg = None 

    main(mdrec=mdrec, fg=fg, device_id=device_id, dither_pid=pid_dither,    
         dither_drive_demod=dither_drive_demod, dither_in_demod=dither_in_demod,
         verbose=False)
