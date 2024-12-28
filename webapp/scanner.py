import ctypes

# Load the SDK DLL (update the path to where DPFPDD.dll is located)
dp_sdk = ctypes.CDLL(r'C:\AMSUFB\DigitalPersona\Bin\DPJasPer.dll')  # Replace with actual path

# Define functions and their argument/return types
dp_sdk.DPFPInit.argtypes = []
dp_sdk.DPFPInit.restype = ctypes.c_int

dp_sdk.DPFPCapture.argtypes = [ctypes.c_void_p]
dp_sdk.DPFPCapture.restype = ctypes.c_int

# Initialize the scanner
def initialize_scanner():
    result = dp_sdk.DPFPInit()
    if result != 0:
        raise Exception("Failed to initialize scanner")

# Capture a fingerprint
def capture_fingerprint():
    fingerprint_data = ctypes.create_string_buffer(1024)
    result = dp_sdk.DPFPCapture(ctypes.byref(fingerprint_data))
    if result != 0:
        raise Exception("Failed to capture fingerprint")
    return fingerprint_data.raw
