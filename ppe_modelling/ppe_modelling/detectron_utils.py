import os
import random

import cv2
import typing as tp
import matplotlib.pyplot as plt
import numpy as np

from detectron2.utils.visualizer import Visualizer, ColorMode
from detectron2.data import DatasetCatalog, MetadataCatalog
from detectron2.data.datasets import register_coco_instances


def unregister_if_exists(ds_name):
    if ds_name in DatasetCatalog.list():
        DatasetCatalog.remove(ds_name)
        MetadataCatalog.remove(ds_name)


def register_coco_ds(ds_path, subset, ds_name) -> None:
    unregister_if_exists(ds_name)
    json_path = os.path.join(ds_path, f"annotations/instances_{subset}.json")
    imgs_path = os.path.join(ds_path, f"images/{subset}")
    register_coco_instances(ds_name, {}, json_path, imgs_path)


def visualize_sample(ax: plt.Axes, sample: dict, ds_metadata) -> None:
    image = cv2.imread(sample["file_name"])
    visualizer = Visualizer(image[:, :, ::-1], metadata=ds_metadata, scale=0.3)
    out = visualizer.draw_dataset_dict(sample)
    ax.imshow(out.get_image())
    ax.axis("off")


def visualize_ds(
    ds: tp.List[dict], ds_metadata, n: int = 10, cols: int = 3
) -> tp.List[dict]:
    samples = random.sample(ds, n)
    rows = (n + cols - 1) // cols  # Compute the number of rows needed
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 3, rows * 3))
    axes = axes.flatten() if isinstance(axes, np.ndarray) else [axes]

    for ax, sample in zip(axes, samples):
        visualize_sample(ax, sample, ds_metadata)

    # Hide any unused subplots
    for ax in axes[len(samples) :]:
        ax.axis("off")

    plt.tight_layout()
    plt.show()
    return samples


def infer_sample(predictor, sample, ds_metadata) -> None:
    image = cv2.imread(sample["file_name"])
    visualizer = Visualizer(
        image[:, :, ::-1],
        metadata=ds_metadata,
        scale=0.3,
        instance_mode=ColorMode.IMAGE_BW,
    )
    prediction = predictor(image)
    out = visualizer.draw_instance_predictions(prediction["instances"].to("cpu"))
    plt.imshow(out.get_image())
    plt.axis("off")
    plt.show()
    return prediction


def infer_ds(predictor, ds, ds_metadata, n=10) -> tp.List[dict]:
    samples = random.sample(ds, n)
    predictions = []
    for sample in samples:
        prediction = infer_sample(predictor, sample, ds_metadata)
        predictions.append(prediction)
    return samples, predictions
