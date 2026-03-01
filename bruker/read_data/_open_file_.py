import struct
import zlib
from pathlib import Path

LFH_SIG = b"PK\x03\x04"
DD_SIG  = b"PK\x07\x08"

def _read_lfh(buf: memoryview, off: int):
    # Local file header is 30 bytes after signature
    if off + 30 > len(buf):
        return None
    sig = bytes(buf[off:off+4])
    if sig != LFH_SIG:
        return None

    # <IHHHHHIIIHH = sig, ver, flag, comp, mtime, mdate, crc, csize, usize, nlen, elen
    sig_i, ver, flag, comp, mtime, mdate, crc, csize, usize, nlen, elen = struct.unpack_from(
        "<IHHHHHIIIHH", buf, off
    )
    name_off = off + 30
    name = bytes(buf[name_off:name_off+nlen]).decode("utf-8", errors="replace")
    extra_off = name_off + nlen
    data_off = extra_off + elen
    return {
        "off": off,
        "ver": ver,
        "flag": flag,
        "comp": comp,
        "crc": crc,
        "csize": csize,
        "usize": usize,
        "name": name,
        "data_off": data_off,
        "nlen": nlen,
        "elen": elen,
    }

def _find_next_lfh(buf: memoryview, start: int) -> int:
    return bytes(buf).find(LFH_SIG, start)

def recover_zip_streaming(path_in: str, out_dir: str = "recovered"):
    path = (Path(__file__).parent / out_dir)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    data = memoryview(Path(path_in).read_bytes())

    off = 0
    recovered = []

    while True:
        idx = bytes(data).find(LFH_SIG, off)
        if idx == -1:
            break

        h = _read_lfh(data, idx)
        if not h:
            break

        name = h["name"]
        flag = h["flag"]
        comp = h["comp"]
        data_off = h["data_off"]

        # Bit 3 => sizes/CRC are in a data descriptor after file data
        has_dd = bool(flag & 0x0008)

        # Directory entries can exist (name ends with '/')
        if name.endswith("/"):
            off = data_off
            continue

        # Decide extraction strategy
        try:
            if not has_dd and h["csize"] > 0:
                # Simple case: sizes known
                csize = h["csize"]
                comp_bytes = bytes(data[data_off:data_off+csize])

                if comp == 0:
                    payload = comp_bytes
                elif comp == 8:
                    payload = zlib.decompress(comp_bytes, -15)
                else:
                    print(f"Skip (unsupported compression {comp}): {name}")
                    off = data_off + csize
                    continue

                (path / Path(name).name).write_bytes(payload)
                recovered.append((name, len(payload)))
                off = data_off + csize
                continue

            # Streaming case (sizes in data descriptor or unknown)
            if comp == 0:
                # Stored + data descriptor is awkward without sizes:
                # fallback: search forward for next header, treat bytes in-between as payload candidate.
                next_idx = _find_next_lfh(data, data_off)
                if next_idx == -1:
                    next_idx = len(data)
                payload = bytes(data[data_off:next_idx])
                (outp / Path(name).name).write_bytes(payload)
                recovered.append((name, len(payload)))
                off = next_idx
                continue

            if comp != 8:
                print(f"Skip (unsupported compression {comp}): {name}")
                off = data_off + 1
                continue

            # Deflate streaming: inflate until end-of-stream
            decomp = zlib.decompressobj(-15)
            out_bytes = bytearray()

            pos = data_off
            chunk = 64 * 1024

            while pos < len(data):
                block = bytes(data[pos:pos+chunk])
                if not block:
                    break
                out_bytes.extend(decomp.decompress(block))
                pos += len(block)

                # When the stream ends, unused_data begins (start of DD or next header)
                if decomp.eof:
                    break

            # Flush remaining
            out_bytes.extend(decomp.flush())

            if not out_bytes:
                print(f"Failed (no output): {name}")
                off = data_off + 1
                continue

            (path / Path(name).name).write_bytes(out_bytes)
            recovered.append((name, len(out_bytes)))

            # Advance offset:
            # If eof, decomp.unused_data contains bytes after end of deflate stream.
            # Compute where we landed.
            if decomp.eof:
                # pos currently points just after last block we fed;
                # unused_data is within the last block, so step back by its length.
                off = pos - len(decomp.unused_data)

                # If there's a data descriptor, optionally skip it.
                if has_dd:
                    # Data descriptor is either:
                    #  - optional signature + 12 bytes (crc32, csize, usize) OR
                    #  - no signature + 12 bytes
                    if bytes(data[off:off+4]) == DD_SIG:
                        off += 4 + 12
                    else:
                        off += 12
            else:
                # Truncated stream; move forward a bit to look for next header
                print(f"Partial deflate (truncated): {name}")
                nxt = _find_next_lfh(data, data_off)
                off = nxt if nxt != -1 else len(data)

        except Exception as e:
            print(f"Error on {name}: {e}")
            off = data_off + 1

    print("Recovered entries:")
    for n, sz in recovered:
        print(f"  {n} -> {sz} bytes")
    return recovered

