import struct
from typing import List
import cv2
import numpy as np


from subprocess import call, STDOUT
import subprocess
import os
import shutil
from pydub import AudioSegment

import os
from math import ceil
from time import time

import math
import wave

def roundup(x, base=1):
    return int(ceil(x / base)) * base

byte_depth_to_dtype = {1: np.uint8, 2: np.uint16, 4: np.uint32, 8: np.uint64}

def encodeAudio(sound_path, file_path, output_path, num_lsb):
    """Hide data from the file at file_path (payload) in the sound file (cover) at sound_path"""
    if sound_path is None:
        raise ValueError("WavSteg hiding requires an input sound file path")
    if file_path is None:
        raise ValueError("WavSteg hiding requires a secret file path")
    if output_path is None:
        raise ValueError("WavSteg hiding requires an output sound file path")

    sound = wave.open(sound_path, "r")

    extPayload = os.path.splitext(file_path)
    extPayload = extPayload[1]

    params = sound.getparams()
    num_channels = sound.getnchannels()
    sample_width = sound.getsampwidth()
    num_frames = sound.getnframes()
    num_samples = num_frames * num_channels

    # We can hide up to num_lsb bits in each sample of the sound file
    max_bytes_to_hide = (num_samples * num_lsb) // 8
    file_size = os.stat(file_path).st_size

    # log.debug(f"Using {num_lsb} LSBs, we can hide {max_bytes_to_hide} bytes")

    start = time()
    sound_frames = sound.readframes(num_frames)
    with open(file_path, "rb") as file:
        data = file.read()
    # log.debug("Files read".ljust(30) + f" in {time() - start:.2f}s")

    if file_size > max_bytes_to_hide:
        required_lsb = math.ceil(file_size * 8 / num_samples)
        raise ValueError(
            "Input file too large to hide, "
            f"requires {required_lsb} LSBs, using {num_lsb}"
        )

    if sample_width != 1 and sample_width != 2:
        # Python's wave module doesn't support higher sample widths
        raise ValueError("File has an unsupported bit-depth")

    start = time()
    sound_frames = lsb_interleave_bytes(
        sound_frames, data, num_lsb, extPayload, byte_depth=sample_width
    )
    # log.debug(f"{file_size} bytes hidden".ljust(30) + f" in {time() - start:.2f}s")

    start = time()
    sound_steg = wave.open(output_path, "w")
    sound_steg.setparams(params)
    sound_steg.writeframes(sound_frames)
    sound_steg.close()
    # log.debug("Output wav written".ljust(30) + f" in {time() - start:.2f}s")

def lsb_interleave_bytes(carrier, payload, num_lsb, extPayload, truncate=False, byte_depth=1):
    """
    Interleave the bytes of payload into the num_lsb LSBs of carrier.

    :param carrier: cover bytes
    :param payload: payload bytes
    :param num_lsb: number of least significant bits to use
    :param truncate: if True, will only return the interleaved part
    :param byte_depth: byte depth of carrier values
    :return: The interleaved bytes
    """

    plen = len(payload) ## length of payload in bytes
    test_bytes = plen.to_bytes(4, 'little')
    test_bytes += str.encode(extPayload)
    padding = "\0"*(5-len(extPayload))

    test_bytes += str.encode(padding)
    test_bytes += payload

    plen += 9

    payload_bits = np.zeros(shape=(plen, 8), dtype=np.uint8)

    payload_bits[:plen, :] = np.unpackbits(
        np.frombuffer(test_bytes, dtype=np.uint8, count=plen)
    ).reshape(plen, 8)

    bit_height = roundup(plen * 8 / num_lsb)
    payload_bits.resize(bit_height * num_lsb)

    carrier_dtype = byte_depth_to_dtype[byte_depth]
    carrier_bits = np.unpackbits(
        np.frombuffer(carrier, dtype=carrier_dtype, count=bit_height).view(np.uint8)
    ).reshape(bit_height, 8 * byte_depth)

    carrier_bits[:, 8 * byte_depth - num_lsb: 8 * byte_depth] = payload_bits.reshape(
        bit_height, num_lsb
    )

    ret = np.packbits(carrier_bits).tobytes()
    return ret if truncate else ret + carrier[byte_depth * bit_height:]

def encode(coverObject, payload, ListLSB):

    pathCoverObject, fileCoverObject = os.path.split(coverObject)
    filenameCoverObject, extCoverObject = os.path.splitext(fileCoverObject)
    extCoverObject = extCoverObject.split(".")[-1]

    pathPayload, filePayload = os.path.split(payload)
    filenamePayload, extPayload = os.path.splitext(filePayload)
    extPayload = extPayload.split(".")[-1]


    # ListLSB.sort()

    with open(payload, "rb") as f:
        file = f.read()

    # Unpack payload bytes into integer list.
    payloadBytes = list(struct.unpack("{}B".format(len(file)), file))

    if (extCoverObject == "png" or extCoverObject == "bmp" or extCoverObject == "tiff"):

        imageEncode = encodeImage(
            coverObject, payloadBytes, ListLSB, extPayload)

        encodedObject = os.path.join(
            pathCoverObject, f"{filenameCoverObject}_encoded.{extCoverObject}")

        cv2.imwrite(encodedObject, imageEncode)

    elif (extCoverObject == "mov" or extCoverObject == "mp4" or extCoverObject == "avi"):
        # extract frames into tmp
        frame_extraction(coverObject)

        # seperate video from audio
        os.system("ffmpeg -i " + coverObject + " -q:a 0 -map a ./tmp/AudioVisualFileTypes.mp3 -y")
        # call(["ffmpeg", " -i ", coverObject, " -q:a", " 0", " -map", " a", " /tmp/AudioVisualFileTypes.mp3", " -y"], stdout=open(os.devnull, "w"),
        #     stderr=STDOUT)

        # read frame number
        # frameNumber = input("Enter frame number: ")
        # framePath = "tmp/" + frameNumber + ".png"
        framePath = "./tmp/0.png"

        # cover img = sel frame
        # origianl cover frame = save a copy of sel frame before encode
        # coverImg = framePath
        # originalCoverFrame = cv2.imread(coverImg)

        # encode and create a copy of encoded frame
        encodedFrame = encodeVideo(
            framePath, payloadBytes, ListLSB, extPayload)

        cv2.imwrite('Encoded Frame.png', encodedFrame)
        # del selected frame from tmp folder
        os.remove(framePath)
        # # rename/move and store the encoded frame in tmp
        # path = os.path.join('./tmp/', 'Encoded Frame.png')
        # f = open(path, "a+")

        shutil.move('Encoded Frame.png', "./tmp/Encoded Frame.png")
        os.rename('./tmp/Encoded Frame.png', framePath)

        if extCoverObject == "mp4":
            # combine images all frames into a video
            os.system("ffmpeg -i ./tmp/%d.png -vcodec png  tmp/video.avi -y")

            # combine video with audio
            os.system(f"ffmpeg -i ./tmp/video.avi -i tmp/AudioVisualFileTypes.mp3 -codec copy {pathCoverObject}/stegowAudio.avi -y")

            os.system(f"ffmpeg -i {pathCoverObject}/stegowAudio.avi -f avi -c:v rawvideo -pix_fmt rgb32 {pathCoverObject}/stego.mp4")

            # combine images all frames into a video
            #os.system("ffmpeg -r 30 -f image2 -s 1920x1080 -i ./tmp/%d.png -vcodec libx264 -crf 25  -pix_fmt yuv420p ./tmp/test.mp4")
            #os.system("ffmpeg -i ./tmp/test.mp4 -i ./tmp/AudioVisualFileTypes.mp3 -map 0:v -map 1:a -c:v copy -shortest ./video/stego.mp4")

        elif extCoverObject == "mov":
                        # combine images all frames into a video
            os.system("ffmpeg -i ./tmp/%d.png -vcodec png  tmp/video.avi -y")

            # combine video with audio
            os.system(f"ffmpeg -i ./tmp/video.avi -i tmp/AudioVisualFileTypes.mp3 -codec copy {pathCoverObject}/stegowAudio.avi -y")

            os.system(f"ffmpeg -i {pathCoverObject}/stegowAudio.avi -f avi -c:v rawvideo -pix_fmt rgb32 {pathCoverObject}/stego.mov")

            # # combine images all frames into a video
            # os.system("ffmpeg -i ./tmp/%d.png -vcodec png  tmp/video.avi -y")

            # # combine video with audio
            # os.system(f"ffmpeg -i ./tmp/video.mov -i tmp/AudioVisualFileTypes.mp3 -codec copy {pathCoverObject}/stego.mov -y")

        elif extCoverObject == "avi":
                        # combine images all frames into a video
            os.system("ffmpeg -i ./tmp/%d.png -vcodec png  tmp/video.avi -y")

            # combine video with audio
            os.system(f"ffmpeg -i ./tmp/video.avi -i tmp/AudioVisualFileTypes.mp3 -codec copy {pathCoverObject}/stegowAudio.avi -y")

            os.system(f"ffmpeg -i {pathCoverObject}/stegowAudio.avi -f avi -c:v rawvideo -pix_fmt rgb32 {pathCoverObject}/stego.avi")

            # # combine images all frames into a video
            # os.system("ffmpeg -r 30 -f image2 -s 1920x1080 -i ./tmp/%d.png -vcodec libx264 -crf 25  -pix_fmt yuv420p ./tmp/test.avi")
            # os.system("ffmpeg -i ./tmp/test.avi -i ./tmp/AudioVisualFileTypes.mp3 -map 0:v -map 1:a -c:v copy -shortest ./video/stego.avi")


        clean_tmp()

    elif (extCoverObject == "mp3"):
        sound = AudioSegment.from_mp3(coverObject)
        sound.export("temp_wav.wav", format = "wav")
        encodeAudio("temp_wav.wav", payload, "encoded_audio.wav", len(ListLSB))

    elif (extCoverObject == "wav"):
        encodeAudio(coverObject, payload, "encoded_audio.wav", len(ListLSB))

    elif (extCoverObject == "jpg"):
        encodeJPG(coverObject, payload, "encoded_jpg.jpg", len(ListLSB))


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


#   Function to encode into image file
def encodeImage(image_name, secret_data, LSBtochange, extPayload):
    image = cv2.imread(image_name)
    n_bytes = (image.shape[0] * image.shape[1] * 3 // 8) * len(LSBtochange)
    print("[*] Maximum bits we can encode:", n_bytes)

    starter = "+" + extPayload + "+"
    for char in starter[::-1]:
        secret_data.insert(0, char)

    secret_data += "====="

    print("Payload Bit size: ", len(secret_data))
    if len(secret_data) > n_bytes:
        # pass
        # return "Error"
        raise ValueError(
            "Insufficient bits, need bigger image or lesser data")
    print("Encoding in progress...")
    data_index = 0

    binary_secret_data = []
    for i in secret_data:  # Change every integer in the list into 8bits format
        binary_secret_data.append(to_bin(i))
    binary_secret_data = ''.join(binary_secret_data)

    data_len = len(binary_secret_data)
    for row in image:  # Changing the number of LSBs based on user input
        for pixel in row:
            r, g, b = to_bin(pixel)
            proxy = list(r)
            for LSBits in LSBtochange:
                if data_index < data_len:
                    proxy[7 - LSBits] = binary_secret_data[data_index]
                    data_index += 1
            pixel[0] = int(''.join(proxy), 2)
            proxy = list(g)
            for LSBits in LSBtochange:
                if data_index < data_len:
                    proxy[7 - LSBits] = binary_secret_data[data_index]
                    data_index += 1
            pixel[1] = int(''.join(proxy), 2)
            proxy = list(b)
            for LSBits in LSBtochange:
                if data_index < data_len:
                    proxy[7 - LSBits] = binary_secret_data[data_index]
                    data_index += 1
            pixel[2] = int(''.join(proxy), 2)
            if data_index >= data_len:
                break
    print("Encoding completed")
    return image


def encodeVideo(image_name, secret_data, LSBtochange, extPayload):
    image = cv2.imread(image_name)
    # calculate the maximum bytes to encode
    n_bytes = image.shape[0] * image.shape[1] * 3 // 8
    print("Maximum byte encodable:", n_bytes)

    starter = "+" + extPayload + "+"
    for char in starter[::-1]:
        secret_data.insert(0, char)

    secret_data += "====="
    print("Payload Byte size: ", len(secret_data))
    if len(secret_data) > n_bytes:
        raise ValueError(
            "Insufficient bits, need bigger image or lesser data")
    print("Encoding in progress...")
    data_index = 0

    # Change every integer in the list into 8bits format
    binary_secret_data = []
    for i in secret_data:
        binary_secret_data.append(to_bin(i))
    binary_secret_data = ''.join(binary_secret_data)

    # Changing the number of LSBs based on user input
    data_len = len(binary_secret_data)
    for row in image:
        for pixel in row:
            r, g, b = to_bin(pixel)
            proxy = list(r)
            for LSBits in LSBtochange:
                if data_index < data_len:
                    # hide the data into least significant bit of red pixel
                    proxy[7 - LSBits] = binary_secret_data[data_index]
                    data_index += 1
            # convert to int for red pixel
            pixel[0] = int(''.join(proxy), 2)

            proxy = list(g)
            for LSBits in LSBtochange:
                if data_index < data_len:
                    # hide the data into least significant bit of green pixel
                    proxy[7 - LSBits] = binary_secret_data[data_index]
                    data_index += 1
            # convert to int for green pixel
            pixel[1] = int(''.join(proxy), 2)

            proxy = list(b)
            for LSBits in LSBtochange:
                if data_index < data_len:
                    # hide the data into least significant bit of blue pixel
                    proxy[7 - LSBits] = binary_secret_data[data_index]
                    data_index += 1
            # convert to int for blue pixel
            pixel[2] = int(''.join(proxy), 2)
            # if data is encoded, just break out of the loop
            if data_index >= data_len:
                break

    return image

def encodeJPG(image_path, file_path, output_path, num_lsb):
    """Hide data from the file at file_path (payload) in the sound file (cover) at sound_path"""
    if image_path is None:
        raise ValueError("requires an input sound file path")
    if file_path is None:
        raise ValueError("requires a secret file path")
    if output_path is None:
        raise ValueError("requires an output sound file path")

    # sound = wave.open(sound_path, "r")

    extPayload = os.path.splitext(file_path)
    extPayload = extPayload[1]

    # params = sound.getparams()
    # num_channels = sound.getnchannels()
    # sample_width = sound.getsampwidth()
    # num_frames = sound.getnframes()
    # num_samples = num_frames * num_channels

    with open(image_path, "rb") as file:
        data_jpg = file.read()

    # We can hide up to num_lsb bits in each sample of the sound file
    max_bytes_to_hide = (len(data_jpg) * num_lsb) // 8
    file_size = os.stat(file_path).st_size

    # log.debug(f"Using {num_lsb} LSBs, we can hide {max_bytes_to_hide} bytes")
    with open(file_path, "rb") as file:
        data = file.read()
    # log.debug("Files read".ljust(30) + f" in {time() - start:.2f}s")

    if file_size > max_bytes_to_hide:
        required_lsb = math.ceil(file_size * 8 / len(data_jpg))
        raise ValueError(
            "Input file too large to hide, "
            f"requires {required_lsb} LSBs, using {num_lsb}"
        )
    
    jpg_bytes = lsb_interleave_bytes(
        data_jpg, data, num_lsb, extPayload
    )

    output_file = open(output_path, "wb+")
    output_file.write(jpg_bytes)
    output_file.close()


    # log.debug(f"{file_size} bytes hidden".ljust(30) + f" in {time() - start:.2f}s")


# del the tmp folder
def clean_tmp(path="./tmp"):
    pass


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
