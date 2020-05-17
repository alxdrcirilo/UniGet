import os

path = "downloaded/"
with open(path + "merged.fasta", "w") as output_file:
    for _, file in enumerate(os.listdir(path)):
        print(_)
        with open(os.path.join(path, file)) as input_file:
            for line in input_file:
                output_file.write(line)