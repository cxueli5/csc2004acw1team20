import struct
from sunau import AUDIO_UNKNOWN_SIZE
import cv2
import numpy as np

from subprocess import call,STDOUT
from pydub import AudioSegment

import os
import shutil

import math
import wave

def roundup(x, base=1):
    return int(math.ceil(x / base)) * base

byte_depth_to_dtype = {1: np.uint8, 2: np.uint16, 4: np.uint32, 8: np.uint64}

def decode(coverObject, ListLSB):
    try:
        pathCoverObject, fileCoverObject = os.path.split(coverObject)
        filenameCoverObject, extCoverObject = os.path.splitext(fileCoverObject)
        extCoverObject = extCoverObject.split(".")[-1]

        ListLSB.sort()

        if (extCoverObject == "png" or extCoverObject == "bmp" or extCoverObject == "tiff"):
            decodeImage(coverObject, ListLSB, pathCoverObject)


        elif (extCoverObject == "avi" or extCoverObject == "mp4" or extCoverObject == "mov"):

            frame_extraction(coverObject)
            framePath = "./tmp/0.png"
            decodeImage(framePath, ListLSB, pathCoverObject)
            clean_tmp()

        elif (extCoverObject == "mp3"):
            pass
        
        elif (extCoverObject == "wav"):
            decodeAudio(coverObject, "decoded_from_wav.wav", len(ListLSB))
        elif (extCoverObject == "jpg"):
            decodeJPG(coverObject, "decoded_from_jpg.jpg", len(ListLSB))

    except:
        print("Error, cannot decode file")
    

    

#   Convert data to bin array
def to_bin(data):
    if isinstance(data, str):
        return ''.join([format(ord(i), "08b") for i in data])
    elif isinstance(data, bytes) or isinstance(data, np.ndarray):
        return [format(i, "08b") for i in data]
    elif isinstance(data, int) or isinstance(data, np.uint8):
        return format(data, "08b")
    else:
        raise TypeError("Type not supported")


def decodeImage(image_name, ListLSB, pathCoverObject):
    print("Decoding in progress...")
    image = cv2.imread(image_name)

    binary_data = ""

    for row in image:
        for pixel in row:  # taking out the LSBs
            r, g, b = to_bin(pixel)
            for i in ListLSB:
                binary_data += r[7 - i]
            for i in ListLSB:
                binary_data += g[7 - i]
            for i in ListLSB:
                binary_data += b[7 - i]


    all_bytes = [binary_data[i: i + 8] for i in range(0, len(binary_data), 8)]
    decoded_data = ""
    decoded_int = []

    for byte in all_bytes:
        decoded_data += chr(int(byte, 2))  # Storing the message in ASCII to find the stopping criteria "====="
        decoded_int.append(int(byte, 2))  # Storing the message in integers
        if decoded_data[-5:] == "=====":

            break

    docu = decoded_int[:-5]
    count = 0
    extension = ""

    for char in docu:
        extension += chr(char)
        if char == 43:
            count += 1
        if count == 2:
            break

    docu = docu[len(extension):]
    testing = struct.pack("{}B".format(len(docu)), *docu)  # Integer to original format

    with open(f'{pathCoverObject}/Output.' + extension[1:-1], "wb+") as f:
        f.write(testing)
    print("Decoding completed")
    return


# del the tmp folder
def clean_tmp(path="./tmp"):
    if os.path.exists(path):
        shutil.rmtree(path)
        print("Status:  tmp files are cleaned up")


# extract frames
def frame_extraction(video):
    if not os.path.exists("./tmp"):
        os.makedirs("tmp")
    temp_folder = "./tmp"
    print("Extracting Frames")
    print("Status:  tmp directory is created")

    vidcap = cv2.VideoCapture(video)

    count = 0

    while True:
        success, image = vidcap.read()
        if not success:
            break
        # Change extracted file path here
        cv2.imwrite(os.path.join("./tmp", "{:d}.png".format(count)), image)
        count += 1

    print("Total Frames: " + str(count))


def decodeJPG(image_path, output_path, num_lsb):
    with open(image_path, "rb") as file:
        data_image = file.read()

    data, fileExt = lsb_deinterleave_bytes(
        data_image, num_lsb
    )
    
    fileExt = fileExt.rstrip("\x00")

    # log.debug(
    #     f"Recovered {bytes_to_recover} bytes".ljust(30) + f" in {time() - start:.2f}s"
    # )

    output_file = open(output_path + "." + fileExt, "wb+")
    output_file.write(bytes(data))
    output_file.close()

def decodeAudio(sound_path, output_path, num_lsb):
    """Recover data from the file at sound_path to the file at output_path"""
    if sound_path is None:
        raise ValueError("WavSteg recovery requires an input sound file path")
    if output_path is None:
        raise ValueError("WavSteg recovery requires an output file path")
        
    sound = wave.open(sound_path, "r")

    # num_channels = sound.getnchannels()
    sample_width = sound.getsampwidth()
    num_frames = sound.getnframes()
    sound_frames = sound.readframes(num_frames)
    # log.debug("Files read".ljust(30) + f" in {time() - start:.2f}s")

    if sample_width != 1 and sample_width != 2:
        # Python's wave module doesn't support higher sample widths
        raise ValueError("File has an unsupported bit-depth")

    data, fileExt = lsb_deinterleave_bytes(
        sound_frames, num_lsb, byte_depth=sample_width
    )

    fileExt = fileExt.rstrip("\x00")


    # log.debug(
    #     f"Recovered {bytes_to_recover} bytes".ljust(30) + f" in {time() - start:.2f}s"
    # )

    output_file = open(output_path + "." + fileExt, "wb+")
    output_file.write(bytes(data))
    output_file.close()
    # log.debug("Written output file".ljust(30) + f" in {time() - start:.2f}s")

def lsb_deinterleave_bytes(carrier, num_lsb, byte_depth=1):
    """
    Deinterleave num_bits bits from the num_lsb LSBs of carrier.

    :param carrier: carrier bytes
    :param num_bits: number of num_bits to retrieve
    :param num_lsb: number of least significant bits to use
    :param byte_depth: byte depth of carrier values
    :return: The deinterleaved bytes
    """
    carrier_dtype = byte_depth_to_dtype[byte_depth]

    ## take out the size of the payload first
    header_bits = np.unpackbits(
        np.frombuffer(carrier, dtype=carrier_dtype, count=9*8).view(np.uint8)
    ).reshape(9*8, 8 * byte_depth)[:, 8 * byte_depth - num_lsb: 8 * byte_depth]
    
    bytes_to_recover = np.packbits(header_bits).tobytes()[0:4]
    fileExtB = np.packbits(header_bits).tobytes()[5:9]

    fileExt = fileExtB.decode("utf-8")

    num_bits = (int.from_bytes(bytes_to_recover, 'little') + 9) * 8

    plen = roundup(num_bits / num_lsb)
    
    payload_bits = np.unpackbits(
        np.frombuffer(carrier, dtype=carrier_dtype, count=plen).view(np.uint8)
    ).reshape(plen, 8 * byte_depth)[:, 8 * byte_depth - num_lsb: 8 * byte_depth]
    bytes_array = np.packbits(payload_bits).tobytes()[9: (num_bits) // 8]
    return bytes_array, fileExtB.decode("utf-8", 'ignore')