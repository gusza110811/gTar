import sys
import glob
import os
import math
import zlib
from collections import deque

class archiver:
    @staticmethod
    def find_optimal_cluster_size(file_size: int):
        best_score = float("inf")
        best_cluster_size = 1
        best_cluster_count = 1

        for cluster_size in range(1, 256):
            clusters = math.ceil(file_size / cluster_size)

            if clusters > 2**32:
                continue

            score = cluster_size * 1.5 + clusters * 1.0

            if score < best_score:
                best_score = score
                best_cluster_count = clusters
                best_cluster_size = cluster_size

        return best_cluster_size, best_cluster_count

    @staticmethod
    def main(sources: list[str], output):
        output = output.replace("\\","/")
        print(f"Archiving to {output}:")

        with open(output, "wb") as archive:
            archive.write(b"GTAR\x00")
            for source in sources:
                if os.path.isfile(source):
                    with open(source, "rb") as sourcefile:
                        source = source.replace("\\","/")
                        source = source.replace("C:","")
                        if source.startswith("/"): source = source[1:]
                        data = sourcefile.read()
                        filelength = len(data)
                        clustersize, clustercount = archiver.find_optimal_cluster_size(filelength)
                        padding = (clustercount * clustersize) - filelength

                        filename_bytes = source.encode("utf-8")
                        if len(filename_bytes) > 255:
                            raise ValueError(f"Filename too long: {source}")

                        print(f"  - {source} ({filelength} bytes), cluster: {clustersize} x {clustercount}")

                        # Header (8 bytes + filename)
                        archive.write(bytes([0xFF]))  # Header marker (1 byte)
                        archive.write(clustersize.to_bytes(1)) # Cluster size (1 byte)
                        archive.write(clustercount.to_bytes(4)) # Cluster count (4 bytes)
                        archive.write(padding.to_bytes(1)) # Padding size (1 byte)
                        archive.write(len(filename_bytes).to_bytes(1)) # Filename length (1 byte)
                        archive.write(filename_bytes) # Filename (0-255 byte)

                        archive.write(data)
                        archive.write(b'\x00' * padding)

        print("Done")

class extractor:
    DEBUG = False

    @staticmethod
    def main(source):
        with open(source, 'rb') as archivefile:
            print(f"Extracting {source}")
            archive = deque(archivefile.read())  # use deque here
            magic = [archive.popleft() for _ in range(5)]
            if bytes(magic) != b"GTAR\x00": sys.exit("Not a gTar file")
            while True:
                try:
                    archive.popleft()  # skip Header marker
                except IndexError:
                    break

                clustersize = archive.popleft()
                clustercountbytes = [archive.popleft() for _ in range(4)]
                clustercount = int.from_bytes(bytes(clustercountbytes))
                padding = archive.popleft()
                filenamelength = archive.popleft()

                filename = ''.join(chr(archive.popleft()) for _ in range(filenamelength))
                data = bytes(archive.popleft() for _ in range((clustercount * clustersize) - padding))
                
                # Discard padding
                for _ in range(padding):
                    archive.popleft()

                if extractor.DEBUG:
                    print(f"csize: {clustersize}")
                    print(f"cnum: {clustercount}")
                    print(f"pad: {padding}")
                    print(f"namelen: {filenamelength}")
                    print(f"name : {filename}")
                    print("data:")
                    print(data)
                    continue
                print(f"Discovered {filename}")
                path = "/".join(filename.split("/")[:-1])
                if path:
                    os.makedirs(path, exist_ok=True)
                with open(filename,'wb') as file:
                    file.write(data)

if __name__ == "__main__":
    args = sys.argv[1:]

    archive = None
    outname = None
    sources = []

    outmode = False
    sourcemode = False
    sourceforever = False

    for arg in args:
        if outmode:
            outname = arg
            outmode = False
            continue
        if sourcemode:
            sources += glob.glob(arg, recursive=True)
            sourcemode = False
            continue
        if sourceforever:
            sources += glob.glob(arg, recursive=True)
            continue

        if arg.startswith("--"):
            flag = arg[2:].lower()
            if flag == "archive":
                archive = True
            elif flag == "extract":
                archive = False
            elif flag == "out":
                outmode = True
            elif flag == "source":
                sourcemode = True
            elif flag == "sources":
                sourceforever = True
            continue

        if arg.startswith("-"):
            for flag in arg[1:]:
                if flag == "a":
                    archive = True
                elif flag == "e":
                    archive = False
                elif flag == "o":
                    outmode = True
                elif flag == "s":
                    sourcemode = True
                elif flag == "S":
                    sourceforever = True

    if archive is None:
        sys.exit("Mode not specified. Use --archive or --extract.")
    
    if archive:
        if (outname is None):
            print("No output name specified, defaulting to `archive.gtar`")
            outname = "archive"
        outname += ".gtar"
    print()
    if archive:
        if not sources:
            sys.exit("No sources provided.")
        archiver.main(sources, outname)
    else:
        if not sources:
            sys.exit("No sources provided for extraction.")
        for source in sources:
            extractor.main(source)
