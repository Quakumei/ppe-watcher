from pathlib import Path
import os
from typing import List, Optional

from detectron2.data import DatasetCatalog
from detectron2.config import get_cfg
from detectron2 import model_zoo


def configure_cfg(
    num_classes: int,
    train_datasets: List[str] = [],
    test_datasets: List[str] = [],
    config_file: str = "COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml",
    batch_size: int = 8,
    epochs: int = 10,
    base_lr: float = 0.001,
    eval_period_epochs: float = 1,
    model_weights_path: Optional[Path] = None,
    output_dir: Optional[str] = None,
    solver_steps: List[int] = []
):
    cfg = get_cfg()
    cfg.merge_from_file(model_zoo.get_config_file(config_file))

    output_dir = str(output_dir)
    data_len = sum([len(DatasetCatalog.get(ds)) for ds in train_datasets])
    batches_per_epoch = data_len / batch_size
    max_iter = int(epochs * batches_per_epoch) + cfg.SOLVER.WARMUP_ITERS
    eval_period_iters = int(eval_period_epochs * batches_per_epoch)

    if model_weights_path:
        model_weights_path = Path(model_weights_path)
        if not model_weights_path.exists():
            raise FileNotFoundError(f"Model weights not found at {model_weights_path}")
        model_weights_path = str(model_weights_path)

    cfg.MODEL.WEIGHTS = model_weights_path or model_zoo.get_checkpoint_url(
        config_file
    )  # Let training initialize from model zoo
    if output_dir:
        cfg.OUTPUT_DIR = output_dir

    # Data
    cfg.MODEL.ROI_HEADS.NUM_CLASSES = num_classes  # Classes count without bg class
    cfg.DATASETS.TRAIN = train_datasets
    cfg.DATASETS.TEST = test_datasets

    # Optimization
    cfg.SOLVER.IMS_PER_BATCH = batch_size  # This is the real "batch size" commonly known to deep learning people
    cfg.SOLVER.BASE_LR = base_lr
    cfg.SOLVER.STEPS = solver_steps
    cfg.SOLVER.MAX_ITER = max_iter

    # Other
    cfg.DATALOADER.NUM_WORKERS = 2
    cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE = 256  # The "RoIHead batch size". 128 is faster, and good enough for this toy dataset (default: 512)
    cfg.SOLVER.CHECKPOINT_PERIOD = eval_period_iters
    cfg.TEST.EVAL_PERIOD = eval_period_iters

    if output_dir and cfg.OUTPUT_DIR:
        os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)
    return cfg

def configure_classification_cfg(
    num_classes: int,
    train_datasets: List[str] = [],
    test_datasets: List[str] = [],
    batch_size: int = 8,
    epochs: int = 10,
    base_lr: float = 0.001,
    eval_period_epochs: float = 1,
    output_dir: Optional[str] = None,
    solver_steps: List[int] = []
):
    cfg = get_cfg()
    # config_file: str = "COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml",
    # cfg.merge_from_file(model_zoo.get_config_file(config_file))

    output_dir = str(output_dir)
    data_len = sum([len(DatasetCatalog.get(ds)) for ds in train_datasets])
    batches_per_epoch = data_len / batch_size
    max_iter = int(epochs * batches_per_epoch) + cfg.SOLVER.WARMUP_ITERS
    eval_period_iters = int(eval_period_epochs * batches_per_epoch)

    if output_dir:
        cfg.OUTPUT_DIR = output_dir

    # Data
    cfg.MODEL.NUM_CLASSES = num_classes  # Classes count without bg class
    cfg.DATASETS.TRAIN = train_datasets
    cfg.DATASETS.TEST = test_datasets
    cfg.SOLVER.IMS_PER_BATCH = batch_size  # This is the real "batch size" commonly known to deep learning people
    cfg.SOLVER.BASE_LR = base_lr
    cfg.SOLVER.STEPS = solver_steps
    cfg.SOLVER.MAX_ITER = max_iter
    cfg.DATALOADER.NUM_WORKERS = 2
    cfg.SOLVER.CHECKPOINT_PERIOD = eval_period_iters
    cfg.TEST.EVAL_PERIOD = eval_period_iters

    if output_dir and cfg.OUTPUT_DIR:
        os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)
    return cfg


def get_infer_cfg(model_weights_path: Path, config_file: str, n_classes: int):
    return configure_cfg(
        n_classes, config_file=config_file, model_weights_path=model_weights_path
    )
