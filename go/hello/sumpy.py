from pathlib import Path


def run_sumpy() -> None:
    inp_buff_paths = []
    inp_buff_paths.append(Path("./output_write_multi_50k_buffer0k.txt"))
    inp_buff_paths.append(Path("./output_write_multi_50k_buffer1k.txt"))
    inp_buff_paths.append(Path("./output_write_multi_50k_buffer10k.txt"))
    inp_buff_paths.append(Path("./output_write_multi_500k_buffer0k.txt"))
    inp_buff_paths.append(Path("./output_write_multi_500k_buffer0k_16.txt"))
    inp_buff_paths.append(Path("./output_write_multi_500k_buffer1k.txt"))
    inp_buff_paths.append(Path("./output_write_multi_500k_buffer10k.txt"))
    inp_buff_paths.append(Path("./output_write_multi_500k_buffer100k.txt"))
    inp_buff_paths.append(Path("./output_write_multi_500k_buffer100k_16.txt"))

    for inp_buff_path in inp_buff_paths:
        total = 0
        with inp_buff_path.open() as f:
            for line in f:
                if line[0] == "+":
                    total += int(line)
        print(f"total {inp_buff_path}\t{total:,}")


if __name__ == "__main__":
    run_sumpy()
