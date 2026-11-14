"""
DNA Encryption Utilities
Converts images to DNA sequences and vice versa
"""

import base64
from io import BytesIO
from PIL import Image
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def image_to_binary(image_file):
    """Convert image to binary string"""
    logger.info("🔄 Starting image to binary conversion...")

    # Read image bytes
    image_bytes = image_file.read()
    logger.info(f"📁 Read {len(image_bytes)} bytes from image file")

    # Convert bytes to binary string
    logger.info("🔢 Converting bytes to binary string...")
    binary_string = ''.join(format(byte, '08b') for byte in image_bytes)
    logger.info(f"📊 Binary string length: {len(binary_string)} bits")
    logger.info(f"📋 First 100 binary characters: {binary_string[:100]}...")

    return binary_string, image_bytes


def binary_to_dna(binary_string):
    """
    Convert binary string to DNA sequence
    Binary to DNA mapping:
    00 -> A
    01 -> T
    10 -> G
    11 -> C
    """
    logger.info("🧬 Starting binary to DNA conversion...")
    logger.info(f"📊 Input binary string length: {len(binary_string)} bits")

    dna_sequence = ''
    conversion_count = {'00': 0, '01': 0, '10': 0, '11': 0}

    # Process binary string in pairs
    for i in range(0, len(binary_string), 2):
        if i + 1 < len(binary_string):
            pair = binary_string[i:i+2]
            if pair == '00':
                dna_sequence += 'A'
                conversion_count['00'] += 1
            elif pair == '01':
                dna_sequence += 'T'
                conversion_count['01'] += 1
            elif pair == '10':
                dna_sequence += 'G'
                conversion_count['10'] += 1
            elif pair == '11':
                dna_sequence += 'C'
                conversion_count['11'] += 1
        else:
            # Handle odd length (shouldn't happen with byte data)
            if binary_string[i] == '0':
                dna_sequence += 'A'
                logger.info("⚠️  Handling odd binary length with '0' -> 'A'")
            else:
                dna_sequence += 'T'
                logger.info("⚠️  Handling odd binary length with '1' -> 'T'")

    logger.info(f"🧬 DNA sequence length: {len(dna_sequence)} nucleotides")
    logger.info(f"📋 First 100 DNA characters: {dna_sequence[:100]}...")
    logger.info(f"📊 Binary pair distribution: {conversion_count}")
    logger.info(f"🧬 Final DNA composition: A={dna_sequence.count('A')}, T={dna_sequence.count('T')}, G={dna_sequence.count('G')}, C={dna_sequence.count('C')}")

    return dna_sequence


def image_to_dna(image_file):
    """Complete conversion: Image -> Binary -> DNA"""
    logger.info("🚀 Starting complete image to DNA conversion process...")
    logger.info("=" * 60)

    # Step 1: Image to Binary
    binary_string, image_bytes = image_to_binary(image_file)

    # Step 2: Binary to DNA
    dna_sequence = binary_to_dna(binary_string)

    # Final summary
    logger.info("=" * 60)
    logger.info("✅ Image to DNA conversion completed!")
    logger.info(f"📁 Original image size: {len(image_bytes)} bytes")
    logger.info(f"📊 Binary representation: {len(binary_string)} bits")
    logger.info(f"🧬 DNA sequence: {len(dna_sequence)} nucleotides")
    logger.info(f"📈 Compression ratio: {len(dna_sequence)/len(binary_string)*100:.2f}% (DNA vs Binary)")
    logger.info("=" * 60)

    return dna_sequence, len(image_bytes)


def dna_to_binary(dna_sequence):
    """
    Convert DNA sequence back to binary string
    DNA to Binary mapping:
    A -> 00
    T -> 01
    G -> 10
    C -> 11
    """
    logger.info("🔄 Starting DNA to binary conversion...")
    logger.info(f"🧬 Input DNA sequence length: {len(dna_sequence)} nucleotides")

    binary_string = ''
    dna_count = {'A': 0, 'T': 0, 'G': 0, 'C': 0}

    for nucleotide in dna_sequence:
        if nucleotide == 'A':
            binary_string += '00'
            dna_count['A'] += 1
        elif nucleotide == 'T':
            binary_string += '01'
            dna_count['T'] += 1
        elif nucleotide == 'G':
            binary_string += '10'
            dna_count['G'] += 1
        elif nucleotide == 'C':
            binary_string += '11'
            dna_count['C'] += 1

    logger.info(f"📊 Binary string length: {len(binary_string)} bits")
    logger.info(f"📋 First 100 binary characters: {binary_string[:100]}...")
    logger.info(f"🧬 DNA nucleotide distribution: {dna_count}")

    return binary_string


def binary_to_image(binary_string):
    """Convert binary string back to image bytes"""
    logger.info("🖼️  Starting binary to image conversion...")
    logger.info(f"📊 Input binary string length: {len(binary_string)} bits")

    # Convert binary string to bytes
    byte_array = bytearray()
    bytes_converted = 0

    for i in range(0, len(binary_string), 8):
        byte = binary_string[i:i+8]
        if len(byte) == 8:
            byte_array.append(int(byte, 2))
            bytes_converted += 1
        else:
            logger.warning(f"⚠️  Skipping incomplete byte: {byte}")

    image_bytes = bytes(byte_array)
    logger.info(f"📁 Converted {bytes_converted} bytes back to image")
    logger.info(f"🖼️  Final image size: {len(image_bytes)} bytes")

    return image_bytes


def dna_to_image(dna_sequence):
    """Complete decryption: DNA -> Binary -> Image"""
    logger.info("🔓 Starting complete DNA to image decryption process...")
    logger.info("=" * 60)

    # Step 1: DNA to Binary
    binary_string = dna_to_binary(dna_sequence)

    # Step 2: Binary to Image
    image_bytes = binary_to_image(binary_string)

    # Final summary
    logger.info("=" * 60)
    logger.info("✅ DNA to image decryption completed!")
    logger.info(f"🧬 Original DNA sequence: {len(dna_sequence)} nucleotides")
    logger.info(f"📊 Binary representation: {len(binary_string)} bits")
    logger.info(f"🖼️  Final image size: {len(image_bytes)} bytes")
    logger.info("=" * 60)

    return image_bytes


def generate_dna_key(length=8):
    """Generate random DNA sequence as decryption key"""
    import random
    nucleotides = ['A', 'T', 'G', 'C']
    return ''.join(random.choice(nucleotides) for _ in range(length))


def get_image_info(image_bytes):
    """Get image information"""
    try:
        image = Image.open(BytesIO(image_bytes))
        return {
            'format': image.format,
            'size': image.size,
            'mode': image.mode
        }
    except Exception as e:
        return None
