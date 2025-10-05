import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from ..zhinst_utils.demodulation_recorder import zhinst_demod_recorder
from ..mach_zehnder_stabilization import MachZehnderManager
from ..mach_zehnder_utils.dummy_manager import DummyMZManager
from .config_dialog import ConfigDialog

class MZControlGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mach-Zehnder Control")
        
        # Get configuration
        config_dialog = ConfigDialog()
        config_dialog.mainloop()
        
        if not config_dialog.result:
            self.destroy()
            return
            
        # Initialize manager based on mode
        if not config_dialog.result['dummy_mode']: 
            # Initialize hardware
            self.mdrec = zhinst_demod_recorder(
                config_dialog.result['ip'],
                devtype=config_dialog.result['device_type']
            )
            
            # Initialize real manager
            self.manager = MachZehnderManager(
                self.mdrec,
                config_path=config_dialog.result['config_path'],
                lock_check_interval=config_dialog.result['interval']
            )

        else:
            self.manager = DummyMZManager(
                lock_check_interval=config_dialog.result['interval']
            )
        
        self._create_widgets()
        self._center_window()
        
    def _create_widgets(self):
        # Calibration Frame
        calib_frame = ttk.LabelFrame(self, text="Calibration")
        calib_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        
        ttk.Button(calib_frame, text="Range Calibration", 
                   command=self._range_calibration).pack(pady=5)
        
        ttk.Button(calib_frame, text="Save PID Config", 
                   command=self.manager.save_current_pid_config).pack(pady=5)
        ttk.Button(calib_frame, text="Load PID Config", 
                   command=self.manager.load_latest_pid_config).pack(pady=5)
        
        # Visibility Frame
        vis_frame = ttk.LabelFrame(self, text="Visibility")
        vis_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
        
        ttk.Button(vis_frame, text="Measure Visibility", 
                   command=self._measure_visibility).pack(pady=5)
        self.vis_label = ttk.Label(vis_frame, text="No measurement")
        self.vis_label.pack(pady=5)
        self.vis_time = ttk.Label(vis_frame, text="")
        self.vis_time.pack(pady=5)
        
        # Lock Quality Frame
        lock_frame = ttk.LabelFrame(self, text="Lock Quality")
        lock_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        
        ttk.Button(lock_frame, text="Evaluate Lock", 
                   command=self._evaluate_lock).pack(pady=5)
        self.lock_label = ttk.Label(lock_frame, text="No measurement")
        self.lock_label.pack(pady=5)
        self.lock_time = ttk.Label(lock_frame, text="") 
        self.lock_time.pack(pady=5)  
        
        # Control Frame
        ctrl_frame = ttk.LabelFrame(self, text="Control")
        ctrl_frame.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")
        
        # Setpoint control
        sp_frame = ttk.Frame(ctrl_frame)
        sp_frame.pack(pady=5)
        ttk.Label(sp_frame, text="Setpoint:").pack(side=tk.LEFT)
        self.sp_var = tk.StringVar(value=str(self.manager.setpoint))
        self.sp_entry = ttk.Entry(sp_frame, textvariable=self.sp_var)
        self.sp_entry.pack(side=tk.LEFT, padx=5)
        self.sp_entry.bind('<Return>', self._update_setpoint)
        
        # Monitoring control
        self.monitor_var = tk.BooleanVar()
        self.monitor_check = ttk.Checkbutton(
            ctrl_frame, 
            text="Monitor Locks",
            variable=self.monitor_var,
            command=self._toggle_monitoring
        )
        self.monitor_check.pack(pady=5)
    
    def _range_calibration(self):
        if messagebox.askyesno("Confirm", "Run range calibration?"):
            self.manager.perform_range_calibration()
    
    def _format_timestamp(self, timestamp_str: str) -> str:
        """Convert ISO timestamp to readable format"""
        dt = datetime.fromisoformat(timestamp_str)
        return dt.strftime("%d.%m.%Y at %H:%M:%S")

    def _measure_visibility(self):
        result = self.manager.perform_visibility_calibration()
        self.vis_label.config(
            text=f"Visibility: {result['visibility']:.3f}")
        self.vis_time.config(
            text=f"Measured: {self._format_timestamp(result['timestamp'])}")
    
    def _evaluate_lock(self):
        result = self.manager.evaluate_current_lock()
        self.lock_label.config(
            text=f"Lock Quality: {self.manager.latest_lock_quality:.3f}")
        self.lock_time.config(
            text=f"Measured: {self._format_timestamp(result['timestamp'])}")  
    
    def _update_setpoint(self, event=None):
        try:
            value = float(self.sp_var.get())
            self.manager.setpoint = value
        except ValueError:
            self.sp_var.set(str(self.manager.setpoint))
    
    def _toggle_monitoring(self):
        if self.monitor_var.get():
            self.manager.start_monitoring()
        else:
            self.manager.stop_monitoring()
    
    def _center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')

if __name__ == "__main__":
    app = MZControlGUI()
    app.mainloop()
