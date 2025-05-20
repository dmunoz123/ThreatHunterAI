import logging
from pathlib import Path
from threading import Event
import datetime
import pandas as pd
import pyshark
import asyncio
import boto3
import os

logger = logging.getLogger(__name__)

class PacketCapture:
    def __init__(self, interface: str, packet_limit: int = 10_000, bucket_name: str = "daniel-aws-s3-mks-myawstestbucket", s3_prefix: str = "success_packet_capture_", socketio = None):
        self.interface = interface
        self.packet_limit = packet_limit
        self.stop_event = Event()
        self.s3_prefix = s3_prefix
        self.socketio = socketio
        
        self.cap = None
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.csv_path = Path("tmp") / f"capture_{timestamp}.csv"
        self.s3_key = f"{self.s3_prefix}{self.csv_path.name}"
        
        self.bucket_name = bucket_name
        if bucket_name:
            self.s3 = boto3.client("s3")

    def _parse_packet(self, packet, base_time):
        try:
            if base_time is None:
                base_time = packet.sniff_time
            delta = (packet.sniff_time - base_time).total_seconds()

            eth = getattr(packet, "eth", None)
            ip = getattr(packet, "ip", None)
            tcp = getattr(packet, "tcp", None)
            udp = getattr(packet, "udp", None)

            src_ip = getattr(eth, "src", None) or getattr(ip, "src", None)
            dst_ip = getattr(eth, "dst", None) or getattr(ip, "dst", None)
            src_prt = getattr(tcp, "srcport", None) or getattr(
                udp, "srcport", None)
            dst_prt = getattr(tcp, "dstport", None) or getattr(
                udp, "dstport", None)

            record = {
                "Time": round(delta, 9),
                "Source": str(src_ip) if src_ip else None,
                "Destination": str(dst_ip) if dst_ip else None,
                "Protocol": packet.highest_layer,
                "Length": int(packet.length),
                "Source Port": float(src_prt) if src_prt else None,
                "Destination Port": float(dst_prt) if dst_prt else None,
                "bad_packet": 0,
            }
            return record, base_time

        except Exception:
            logger.exception("Failed to parse packet %d", packet.number if hasattr(packet, "number") else -1)
            return None, base_time

    def _write_and_upload(self, records):
        # 1) write to local file
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)
        df = pd.DataFrame(records)
        df.to_csv(self.csv_path, index=False)
        logger.info("Wrote %d records to %s", len(records), self.csv_path)

        # 2) upload via multipart streaming
        if self.bucket_name:
            try:
                self.s3.upload_file(
                    Filename=str(self.csv_path),
                    Bucket=self.bucket_name,
                    Key=self.s3_key
                )
                logger.info("Uploaded to s3://%s/%s",
                            self.bucket_name, self.s3_key)
            except Exception:
                logger.exception("Failed upload to s3")

        # 3) cleanup local file
        try:
            os.remove(self.csv_path)
            logger.info("Removed local file %s", self.csv_path)
        except OSError:
            logger.warning("Could not remove %s", self.csv_path)

    def run(self):
        logger.info("Starting capture on %s (limit %d packets)", self.interface, self.packet_limit)
        records = []
        base_time = None

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        self.cap = pyshark.LiveCapture(interface=self.interface)
        try:
            for count, packet in enumerate(self.cap.sniff_continuously(),
                                            start=1):
                # stop flag or limit reached?
                if self.stop_event.is_set() or count > self.packet_limit:
                    break

                record, base_time = self._parse_packet(packet, base_time)
                if not record:
                    continue

                # emit & log
                logger.info("Captured packet %d: %r", count, record)
                if self.socketio:
                    self.socketio.emit(
                        'packet', record, namespace='/packets'
                    )
                records.append(record)

        finally:
            if self.cap:
                self.cap.close()

        if records:
            self._write_and_upload(records)
        else:
            logger.warning("No records captured on %s", self.interface)

    def stop(self):
        # 1) signal the loop to exit
        self.stop_event.set()
        logger.info("PacketCapture.stop() called — stop_event set")

        # 3) now aggressively shut down the capture
        if self.cap:
            try:
                logger.info("Calling cap.close()")
                self.cap.close()
            except Exception:
                logger.exception("Error in cap.close()")

            proc = getattr(self.cap, "_process", None)
            if proc:
                try:
                    logger.info("Killing tshark subprocess (pid %s)", proc.pid)
                    proc.kill()
                except Exception:
                    logger.exception("Failed to kill tshark process")
