from pathlib import Path
from datetime import datetime

from .logger import logger


def write_string_to_file(file: Path | str, data: str):
    file = Path(file)
    with open(file, "w") as f:
        f.write(data)
    logger.info(f"Wrote file: {str(file)}")


def current_day_tag(format_str: str = "%d%b"):
    return datetime.now().strftime(format_str).lower()


def current_run_tag():
    return datetime.now().strftime("%d%b-%H_%M_%S").lower()


def system_info_banner() -> str:
    import os
    import psutil
    import subprocess
    import platform

    nvcc_version = subprocess.run(
        ["nvcc", "--version"], text=True, capture_output=True
    ).stdout.strip()
    ram_info = f"{round(psutil.virtual_memory().total / (1024**3), 2)} GB"
    cpu_info = f"{platform.processor() or 'Unknown CPU'} ({os.cpu_count()} cores)"
    system = platform.system()
    machine = platform.machine()
    version = platform.version()
    os_name = platform.platform()

    torch_version = None
    cuda_version = None
    gpu_info = None
    try:
        import torch

        torch_version = ".".join(torch.__version__.split(".")[:2])
        cuda_version = torch.__version__.split("+")[-1]
        if torch.cuda.is_available():
            gpu_info = torch.cuda.get_device_name(0)
        else:
            gpu_info = "No GPU available"
    except ImportError:
        pass

    detectron_version = None
    try:
        import detectron2

        detectron_version = detectron2.__version__
    except ImportError:
        pass

    banner = [
        "=== System Information ===",
        f"System: {system}",
        f"Machine: {machine}",
        f"OS Version: {version}",
        f"OS Name: {os_name}",
        "",
        "=== Hardware Information ===",
        f"RAM: {ram_info}",
        f"CPU: {cpu_info}",
        f"GPU: {gpu_info}",
        f"nvcc: {nvcc_version}",
        "",
        "=== Libraries Information ===",
        f"torch: {torch_version}; cuda: {cuda_version}",
        f"detectron2: {detectron_version}",
    ]
    return "\n".join(banner)
