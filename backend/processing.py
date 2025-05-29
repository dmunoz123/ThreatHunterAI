import logging
from pathlib import Path
from threading import Event
import datetime
import asyncio

import pyshark
from aws_utils import AWSUtils
from parse import ParsePacket

logger = logging.getLogger(__name__)

class PacketCapture:
    """
    General Pyshark packet capture logic
    """
    
    def __init__(self, interface: str, packet_limit: int = 10_000, bucket_name: str = "daniel-aws-s3-mks-myawstestbucket", s3_prefix: str = "success_packet_capture_", socketio = None):
        self.interface = interface
        self.packet_limit = packet_limit
        self.stop_event = Event()
        self.s3_prefix = s3_prefix
        self.socketio = socketio
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.csv_path = Path("tmp") / f"capture_{timestamp}.csv"
        self.s3_key = f"{self.s3_prefix}{self.csv_path.name}"
        
        self.parser = ParsePacket(self.csv_path)
        self.aws = AWSUtils(bucket_name)
        self.cap = None

    def run(self):
        logger.info("Starting capture on %s (limit %d)",
                    self.interface, self.packet_limit)
        self.parser.open()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        self.cap = pyshark.LiveCapture(interface=self.interface)
        count = 0
        try:
            for packet in self.cap.sniff_continuously():
                if self.stop_event.is_set() or count >= self.packet_limit:
                    break

                # Parse, stream to CSV, and get the record dict
                record = self.parser.parse_and_write(packet)
                count += 1

                # Emit over WebSocket
                if self.socketio and record:
                    self.socketio.emit('packet', record, namespace='/packets')

        finally:
            # Always close capture and CSV
            if self.cap:
                try:
                    self.cap.close()
                except Exception:
                    logger.exception("Error closing capture")
            self.parser.close()

            # Upload to S3
            self.aws.upload_file(self.csv_path, self.s3_key)

    def stop(self):
        self.stop_event.set()
        logger.info("Stop requested")
        if self.cap:
            try:
                self.cap.close()
            except Exception:
                logger.exception("Error closing capture in stop()")