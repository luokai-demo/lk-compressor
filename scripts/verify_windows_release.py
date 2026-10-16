"""启动实际打包的 EXE，确认 Qt 主窗口初始化并弹出启动提示。"""

import ctypes
from ctypes import wintypes
from pathlib import Path
import subprocess
import sys
import tempfile
import time


def check_executable_window(executable: Path) -> None:
    """在两分钟内检查指定 EXE 的启动窗口，失败时抛出明确错误。"""
    # Windows 窗口和进程 API，明确句柄宽度以支持 x64。
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    user32.EnumWindows.argtypes = [callback_type, wintypes.LPARAM]
    user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
    kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD,
                                                  wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    # 只接受当前发行文件创建的窗口，避免其他进程造成误判。
    is_ready = False

    @callback_type
    def inspect_window(window: int, context: int) -> bool:
        """查找启动提示，并核实所属进程的完整 EXE 路径。"""
        nonlocal is_ready
        # 当前窗口标题和所属进程编号。
        title = ctypes.create_unicode_buffer(256)
        user32.GetWindowTextW(window, title, len(title))
        if title.value != '启动提示':
            return True
        process_id = wintypes.DWORD()
        user32.GetWindowThreadProcessId(window, ctypes.byref(process_id))
        process_handle = kernel32.OpenProcess(0x1000, False, process_id.value)
        if not process_handle:
            raise ctypes.WinError(ctypes.get_last_error())
        try:
            # 获取真实文件路径，PyInstaller 父子进程均指向同一个发行文件。
            image_path = ctypes.create_unicode_buffer(32768)
            path_size = wintypes.DWORD(len(image_path))
            if not kernel32.QueryFullProcessImageNameW(process_handle, 0, image_path,
                                                       ctypes.byref(path_size)):
                raise ctypes.WinError(ctypes.get_last_error())
            is_ready = Path(image_path.value).resolve() == executable
            return not is_ready
        finally:
            kernel32.CloseHandle(process_handle)

    with tempfile.TemporaryDirectory(prefix='lk-release-') as directory:
        # 启动实际单文件程序，不注入测试专用生产入口。
        process = subprocess.Popen([str(executable)], cwd=directory)
        try:
            # 大型单文件首次解压和 Qt 初始化的截止时间。
            deadline = time.monotonic() + 120
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    raise RuntimeError(f'发行程序在窗口出现前退出，退出码：{process.returncode}')
                user32.EnumWindows(inspect_window, 0)
                if is_ready:
                    print('Windows EXE 启动验证通过：Qt 窗口与启动提示正常初始化')
                    return
                time.sleep(0.5)
            raise TimeoutError('发行程序在两分钟内没有显示启动提示')
        finally:
            # 关闭 PyInstaller 父子进程，避免临时目录与日志句柄残留。
            if process.poll() is None:
                subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'],
                               check=True, capture_output=True, timeout=15)
            process.wait(timeout=15)


if __name__ == '__main__':
    if sys.platform != 'win32':
        raise RuntimeError('发行程序启动验证仅支持 Windows')
    if len(sys.argv) != 2:
        raise ValueError('请传入待验证的 Windows EXE 文件路径')
    check_executable_window(Path(sys.argv[1]).resolve(strict=True))
