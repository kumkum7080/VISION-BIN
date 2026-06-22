import time
import sys

class HardwareController:
    def __init__(self, use_mock=None):
        self.mock_mode = use_mock
        self.current_position_steps = 0  # Home position (0 steps = 0 degrees)
        self.steps_per_rev = 200        # Standard 1.8 degree step NEMA 17/23 motor
        
        # Mapping bins (0-5) to absolute step positions (60 degree increments)
        # 60 degrees = (60 / 360) * 200 = 33.33 -> 33 steps
        # 120 degrees = (120 / 360) * 200 = 66.67 -> 67 steps
        # 180 degrees = 100 steps, etc.
        self.bin_steps = {
            0: 0,     # Plastic: 0 degrees
            1: 33,    # Paper: 60 degrees
            2: 67,    # Metal: 120 degrees
            3: 100,   # Glass: 180 degrees
            4: 133,   # Organic: 240 degrees
            5: 167    # E-waste: 300 degrees
        }
        
        # GPIO Pin Definitions (BCM numbering)
        self.STEP_PIN = 18
        self.DIR_PIN = 23
        self.EN_PIN = 24
        
        self.LJ12_PIN = 17   # Inductive proximity
        self.LJC18_PIN = 27  # Capacitive proximity
        self.IR_PIN = 22     # Entry trigger
        
        self.SERVO_GATE = 25  # Shutter entry gate
        self.SERVO_DROP = 8   # Tray drop trapdoor
        
        # Mock values database
        self.mock_db = {
            "inductive": False,
            "capacitive": False,
            "moisture": 0.0,
            "weight": 0.0,
            "entry_trigger": False
        }
        
        # Attempt to load RPi.GPIO or Jetson.GPIO
        if self.mock_mode is None:
            try:
                import RPi.GPIO as GPIO
                self.GPIO = GPIO
                self.mock_mode = False
                self._setup_gpio()
                print("[HW] Successfully initialized physical RPi.GPIO controllers.")
            except ImportError:
                try:
                    import Jetson.GPIO as GPIO
                    self.GPIO = GPIO
                    self.mock_mode = False
                    self._setup_gpio()
                    print("[HW] Successfully initialized physical Jetson.GPIO controllers.")
                except ImportError:
                    self.mock_mode = True
                    print("[HW] No GPIO library detected. Running in MOCK HARDWARE mode.")
                    
    def _setup_gpio(self):
        self.GPIO.setmode(self.GPIO.BCM)
        self.GPIO.setwarnings(False)
        
        # Setup output pins
        self.GPIO.setup(self.STEP_PIN, self.GPIO.OUT)
        self.GPIO.setup(self.DIR_PIN, self.GPIO.OUT)
        self.GPIO.setup(self.EN_PIN, self.GPIO.OUT)
        self.GPIO.setup(self.SERVO_GATE, self.GPIO.OUT)
        self.GPIO.setup(self.SERVO_DROP, self.GPIO.OUT)
        
        # Setup input pins with pull-down resistors
        self.GPIO.setup(self.LJ12_PIN, self.GPIO.IN, pull_up_down=self.GPIO.PUD_DOWN)
        self.GPIO.setup(self.LJC18_PIN, self.GPIO.IN, pull_up_down=self.GPIO.PUD_DOWN)
        self.GPIO.setup(self.IR_PIN, self.GPIO.IN, pull_up_down=self.GPIO.PUD_DOWN)
        
        # Enable stepper driver (active low typically, check driver settings)
        self.GPIO.output(self.EN_PIN, self.GPIO.LOW)
        
    def cleanup(self):
        if not self.mock_mode:
            self.GPIO.cleanup()
            print("[HW] GPIO resources released.")
            
    # =========================================================================
    # SENSOR READINGS
    # =========================================================================
    def set_mock_sensor_values(self, inductive, capacitive, moisture, weight, entry=False):
        """Used in simulation to feed mock sensor states to the controller."""
        self.mock_db["inductive"] = inductive
        self.mock_db["capacitive"] = capacitive
        self.mock_db["moisture"] = moisture
        self.mock_db["weight"] = weight
        self.mock_db["entry_trigger"] = entry

    def read_inductive(self):
        if self.mock_mode:
            return self.mock_db["inductive"]
        return self.GPIO.input(self.LJ12_PIN) == self.GPIO.HIGH

    def read_capacitive(self):
        if self.mock_mode:
            return self.mock_db["capacitive"]
        return self.GPIO.input(self.LJC18_PIN) == self.GPIO.HIGH

    def read_moisture(self):
        # In real HW: read analog input via ADC (e.g. MCP3008 SPI)
        # Here we return the mock value or an averaged threshold
        return self.mock_db["moisture"]

    def read_weight(self):
        # In real HW: read serial data pulses from HX711 load cell amplifier
        return self.mock_db["weight"]

    def check_entry_trigger(self):
        if self.mock_mode:
            return self.mock_db["entry_trigger"]
        return self.GPIO.input(self.IR_PIN) == self.GPIO.HIGH

    # =========================================================================
    # ACTUATOR CONTROLS
    # =========================================================================
    def rotate_to_bin(self, bin_id):
        """
        Rotates the stepper motor to point the Teflon chute to the target bin compartment.
        To avoid wire twisting, it rotates relative to home (0 steps), and resets back later.
        """
        if bin_id not in self.bin_steps:
            print(f"[HW] Error: Invalid bin ID {bin_id}")
            return
            
        target_steps = self.bin_steps[bin_id]
        step_diff = target_steps - self.current_position_steps
        
        if step_diff == 0:
            print(f"[HW] Stepper already at Bin {bin_id} position.")
            return
            
        self._move_stepper(step_diff)
        self.current_position_steps = target_steps
        print(f"[HW] Stepper rotated to Bin {bin_id} (absolute position: {self.current_position_steps} steps).")

    def reset_to_home(self):
        """Rotates the stepper back to home position (0 degrees) to reset wire tension."""
        if self.current_position_steps == 0:
            return
        step_diff = -self.current_position_steps
        self._move_stepper(step_diff)
        self.current_position_steps = 0
        print("[HW] Stepper returned to home position.")

    def _move_stepper(self, steps):
        direction = 1 if steps > 0 else 0
        abs_steps = abs(steps)
        
        print(f"[HW] Moving stepper: {abs_steps} steps in {'Clockwise' if direction == 1 else 'Counter-Clockwise'} direction...")
        
        if self.mock_mode:
            # Simulate step delays
            time.sleep(abs_steps * 0.005)
            return
            
        # Physical GPIO execution
        # Set Direction
        self.GPIO.output(self.DIR_PIN, self.GPIO.HIGH if direction == 1 else self.GPIO.LOW)
        
        # Send pulses to step pin
        for _ in range(abs_steps):
            self.GPIO.output(self.STEP_PIN, self.GPIO.HIGH)
            time.sleep(0.002) # 2ms pulse width
            self.GPIO.output(self.STEP_PIN, self.GPIO.LOW)
            time.sleep(0.002)

    def operate_gate(self, open_gate=True):
        """Opens or closes the entry shutter gate servo to prevent secondary waste drops."""
        angle = 90 if open_gate else 0
        print(f"[HW] Operating Entry Gate Servo: {'OPEN' if open_gate else 'CLOSE'} (Angle: {angle} degrees)")
        if self.mock_mode:
            time.sleep(0.5)
            return
            
        # In real HW: output PWM duty cycle corresponding to angle on SERVO_GATE pin
        # Duty cycle calculation: 2.5% to 12.5% mapping 0 to 180 degrees
        pwm = self.GPIO.PWM(self.SERVO_GATE, 50) # 50Hz frequency
        pwm.start(0)
        duty = 2.5 + (angle / 180.0) * 10.0
        pwm.ChangeDutyCycle(duty)
        time.sleep(0.5)
        pwm.stop()

    def operate_drop_tray(self, open_drop=True):
        """Opens or closes the tray trapdoor servo to drop sorted waste into the Teflon chute."""
        angle = 90 if open_drop else 0
        print(f"[HW] Operating Drop Tray Servo: {'DROP' if open_drop else 'RESET'} (Angle: {angle} degrees)")
        if self.mock_mode:
            time.sleep(0.5)
            return
            
        pwm = self.GPIO.PWM(self.SERVO_DROP, 50)
        pwm.start(0)
        duty = 2.5 + (angle / 180.0) * 10.0
        pwm.ChangeDutyCycle(duty)
        time.sleep(0.5)
        pwm.stop()

if __name__ == "__main__":
    # Test stepper rotation and servo gate operations in mock mode
    hw = HardwareController(use_mock=True)
    hw.operate_gate(open_gate=False)  # Close gate
    hw.rotate_to_bin(2)              # Rotate to Metal
    hw.operate_drop_tray(open_drop=True)  # Open drop
    time.sleep(1)
    hw.operate_drop_tray(open_drop=False) # Reset drop
    hw.reset_to_home()               # Reset stepper
    hw.operate_gate(open_gate=True)   # Open gate
