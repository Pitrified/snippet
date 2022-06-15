"""Minimal script to test model unloading."""
import gc
from time import sleep
from timeit import default_timer

from pynvml import (
    nvmlDeviceGetHandleByIndex,
    nvmlDeviceGetMemoryInfo,
    nvmlInit,
)
import torch
from transformers.pipelines import pipeline
from sentence_transformers import SentenceTransformer


def print_gpu_utilization():
    """Print useful GPU stats.

    https://huggingface.co/docs/transformers/main/en/perf_train_gpu_one
    """
    nvmlInit()
    handle = nvmlDeviceGetHandleByIndex(0)
    info = nvmlDeviceGetMemoryInfo(handle)
    print(f"GPU memory occupied: {info.used//1024**2} MB.")


def main():
    """Minimal script to test model unloading."""
    sleep_amount = 1

    print("Loading model")
    pipe = pipeline("translation", model=f"Helsinki-NLP/opus-mt-en-fr")
    print(pipe("Sphinx of black quartz judge my vow."))
    print_gpu_utilization()
    sleep(sleep_amount)

    # https://github.com/huggingface/transformers/issues/1664
    # print("Moving model")
    # pipe.module.to("cpu")
    # print_gpu_utilization()
    # sleep(sleep_amount)

    print("Deleting model")
    del pipe
    print_gpu_utilization()
    sleep(sleep_amount)

    print("Emptying cache")
    gc.collect()
    torch.cuda.empty_cache()
    print_gpu_utilization()

    # print("Emptying cache again")
    # with torch.cuda.device("cuda:0"):
    #     gc.collect()
    #     torch.cuda.empty_cache()
    # print_gpu_utilization()
    # sleep(sleep_amount)

    print("Loading another model to check if our stats are truthful")
    pipefr = pipeline("translation", model=f"Helsinki-NLP/opus-mt-fr-en")
    print_gpu_utilization()
    sleep(sleep_amount)

    print(pipefr("Je suis vexé."))
    print_gpu_utilization()
    sleep(sleep_amount)

    # device_name = "cpu"
    device_name = "cuda:0"
    # device = torch.device(device_name)

    print("Loading a third model")
    sentence_transformer = SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2",
        device=device_name,
    )
    print_gpu_utilization()
    sleep(sleep_amount)

    start = default_timer()
    embeddings = sentence_transformer.encode(
        [
            "The quick brown fox jumps over the lazy dog.",
            "Sphinx of black quartz judge my vow.",
        ]
    )
    end = default_timer()
    print(f"Embedding on {device_name} took {end-start:.2f}s")
    print_gpu_utilization()
    sleep(sleep_amount)


if __name__ == "__main__":
    main()
