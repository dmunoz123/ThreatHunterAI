import csv
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ParsePacket:
    """
    Some parsing logic/definiton of a network packet, written to csv
    """

    def __init__(self, csv_path: Path):
        self.csv_path = csv_path
        self.csv_file = None
        self.writer = None
        self._base_time = None
        self._first = True

    def open(self):
        # Ensure directory exists
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)
        # Open file for writing
        self.csv_file = open(self.csv_path, 'w', newline='')

    def parse_and_write(self, packet) -> dict:
        # Parse one packet into a record and immediately append it as a CSV row

        if self._base_time is None:
            self._base_time = packet.sniff_time
        delta = (packet.sniff_time - self._base_time).total_seconds()

        eth = getattr(packet, 'eth', None)
        ip = getattr(packet, 'ip', None)
        tcp = getattr(packet, 'tcp', None)
        udp = getattr(packet, 'udp', None)

        record = {
            'Time': round(delta, 9),
            'Source': getattr(eth, 'src', None) or getattr(ip, 'src', None),
            'Destination': getattr(eth, 'dst', None) or getattr(ip, 'dst', None),
            'Protocol': packet.highest_layer,
            'Length': int(packet.length),
            'Source Port': getattr(tcp, 'srcport', None) or getattr(udp, 'srcport', None),
            'Destination Port': getattr(tcp, 'dstport', None) or getattr(udp, 'dstport', None),
            'bad_packet': 0,
        }

        if self._first:
            fieldnames = list(record.keys())
            self.writer = csv.DictWriter(self.csv_file, fieldnames=fieldnames)
            self.writer.writeheader()
            self._first = False

        # Write packet to CSV row
        try:
            self.writer.writerow(record)
        except Exception:
            logger.exception("Failed to write packet record to CSV")
            
        return record

    def close(self):
        if self.csv_file:
            self.csv_file.close()
