#!/usr/bin/env python3

from pathlib import Path
import argparse
import base64
import gzip
import hashlib
import libarchive.public
import nacl.encoding
import nacl.signing
import sys


def write_to_content_store(base: Path, h: str, contents: bytes):
    directory = base / h[0:2] / h[2:4]
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / h[4:]
    # Path is content-based, so no need to overwrite.
    if path.exists():
        return
    with gzip.GzipFile(path, "wb") as fp:
        fp.write(contents)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate an update manifest file.')
    parser.add_argument(
        '--input', required=True, type=Path, help='Input archive to process.')
    parser.add_argument(
        '--version_hash',
        required=True,
        help='SHA1 Git hash of the version being stored.')
    parser.add_argument(
        '--output-manifest-store',
        type=Path,
        help='If provided, write the manifest to the store at this path.')
    parser.add_argument(
        '--output-content-store',
        type=Path,
        help='If provided, write the content to the store at this path.')
    parser.add_argument(
        '--signing-key',
        required=True,
        type=argparse.FileType(mode='rb'),
        help='Ed25519 signing key.')
    args = parser.parse_args()

    entries = []
    with libarchive.public.file_reader(str(args.input)) as archive:
        for entry in archive:
            filename = entry.pathname
            # Skip directories.
            if filename.endswith('/'):
                continue
            # Remove the initial directory name.
            filename = filename.split('/', 1)[1]
            if "\t" in filename:
                raise ValueError(r"Unsupported char in filename: \t")
            contents = b''.join(entry.get_blocks())
            h = hashlib.sha256(contents).hexdigest()[:32]
            if args.output_content_store:
                write_to_content_store(args.output_content_store, h, contents)
            entries.append((filename, h))

    entries.sort()
    manifest = ("".join(
        f"{filename}\t{h}\n" for filename, h in entries).encode('utf-8'))

    signing_key = nacl.signing.SigningKey(
        args.signing_key.read(), encoder=nacl.encoding.RawEncoder)
    sig = base64.b64encode(signing_key.sign(manifest).signature)

    if args.output_manifest_store:
        directory = (args.output_manifest_store / args.version_hash[0:2] /
                     args.version_hash[2:4])
        directory.mkdir(parents=True, exist_ok=True)
        filename = directory / (args.version_hash[4:] + ".manifest")
        temp_filename = filename.with_suffix(".manifest.tmp")
        fp = gzip.GzipFile(temp_filename, "wb")
    else:
        fp = sys.stdout.buffer

    fp.write(manifest)
    fp.write(b"\n" + sig + b"\n")

    if args.output_manifest_store:
        fp.close()
        temp_filename.rename(filename)
