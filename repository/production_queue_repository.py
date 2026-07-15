from models.production_queue_entry import ProductionQueueEntry
from repository.json_repository import load_json, save_json


class ProductionQueueRepository:
    def __init__(self, file_path):
        self.file_path = file_path

    def get_all(self) -> list[ProductionQueueEntry]:
        return [ProductionQueueEntry.from_dict(item) for item in load_json(self.file_path)]

    def enqueue(self, entry: ProductionQueueEntry) -> ProductionQueueEntry:
        entries = self.get_all()
        entries.append(entry)
        save_json(self.file_path, [e.to_dict() for e in entries])
        return entry
