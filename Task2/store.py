import logging

from google.cloud import datastore


LOGGER = logging.getLogger(__name__)

NONE_TEXT = "None"
NO_COMMANDS = "NO COMMANDS"


class DatastoreStorage:
    def __init__(self):
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = datastore.Client()
        return self._client

    def key(self, kind, name):
        return self.client.key(kind, name)

    def get(self, key):
        return self.client.get(key)

    def put(self, entity):
        self.client.put(entity)

    def delete(self, key):
        self.client.delete(key)

    def entity(self, key):
        return datastore.Entity(key=key)

    def delete_kind(self, kind):
        query = self.client.query(kind=kind)
        keys = [entity.key for entity in query.fetch()]
        if keys:
            self.client.delete_multi(keys)


class MemoryStorage:
    def __init__(self):
        self.entities = {}

    def key(self, kind, name):
        return (kind, name)

    def get(self, key):
        value = self.entities.get(key)
        return None if value is None else dict(value)

    def put(self, entity):
        self.entities[entity["_key"]] = dict(entity)

    def delete(self, key):
        self.entities.pop(key, None)

    def entity(self, key):
        return {"_key": key}

    def delete_kind(self, kind):
        for key in list(self.entities):
            if key[0] == kind:
                del self.entities[key]


class Database:
    VARIABLE = "Task2Variable"
    VALUE_COUNT = "Task2ValueCount"
    OPERATION = "Task2Operation"
    STATE = "Task2State"

    def __init__(self, storage=None):
        self.storage = storage or DatastoreStorage()

    def set(self, name, value):
        before_exists, before_value = self._read_value(name)
        self._write_value(name, True, value)
        self._record_operation(name, before_exists, before_value, True, value)
        LOGGER.info("SET %s=%s", name, value)
        return self._format_change(name, True, value)

    def get(self, name):
        exists, value = self._read_value(name)
        LOGGER.info("GET %s", name)
        return value if exists else NONE_TEXT

    def unset(self, name):
        before_exists, before_value = self._read_value(name)
        self._write_value(name, False, None)
        self._record_operation(name, before_exists, before_value, False, None)
        LOGGER.info("UNSET %s", name)
        return self._format_change(name, False, None)

    def numequalto(self, value):
        entity = self.storage.get(self.storage.key(self.VALUE_COUNT, value))
        count = entity["count"] if entity else 0
        LOGGER.info("NUMEQUALTO %s -> %s", value, count)
        return str(count)

    def undo(self):
        state = self._state()
        op_id = state.get("undo_head")
        if not op_id:
            LOGGER.info("UNDO with no commands")
            return NO_COMMANDS

        op = self.storage.get(self.storage.key(self.OPERATION, op_id))
        self._write_value(op["name"], op["before_exists"], op.get("before_value"))

        state["undo_head"] = op.get("prev_undo")
        op["prev_redo"] = state.get("redo_head")
        state["redo_head"] = op_id
        self.storage.put(op)
        self._save_state(state)

        LOGGER.info("UNDO %s", op["name"])
        return self._format_change(op["name"], op["before_exists"], op.get("before_value"))

    def redo(self):
        state = self._state()
        op_id = state.get("redo_head")
        if not op_id:
            LOGGER.info("REDO with no commands")
            return NO_COMMANDS

        op = self.storage.get(self.storage.key(self.OPERATION, op_id))
        self._write_value(op["name"], op["after_exists"], op.get("after_value"))

        state["redo_head"] = op.get("prev_redo")
        op["prev_undo"] = state.get("undo_head")
        state["undo_head"] = op_id
        self.storage.put(op)
        self._save_state(state)

        LOGGER.info("REDO %s", op["name"])
        return self._format_change(op["name"], op["after_exists"], op.get("after_value"))

    def end(self):
        for kind in (self.VARIABLE, self.VALUE_COUNT, self.OPERATION, self.STATE):
            self.storage.delete_kind(kind)
        LOGGER.info("END cleaned datastore")
        return "CLEANED"

    def _record_operation(self, name, before_exists, before_value, after_exists, after_value):
        state = self._state()
        op_id = state["next_operation_id"]
        op = self.storage.entity(self.storage.key(self.OPERATION, op_id))
        op.update(
            {
                "name": name,
                "before_exists": before_exists,
                "before_value": before_value,
                "after_exists": after_exists,
                "after_value": after_value,
                "prev_undo": state.get("undo_head"),
                "prev_redo": None,
            }
        )
        state["next_operation_id"] = op_id + 1
        state["undo_head"] = op_id
        state["redo_head"] = None
        self.storage.put(op)
        self._save_state(state)

    def _state(self):
        key = self.storage.key(self.STATE, "main")
        state = self.storage.get(key)
        if state:
            return state

        state = self.storage.entity(key)
        state.update({"undo_head": None, "redo_head": None, "next_operation_id": 1})
        return state

    def _save_state(self, state):
        self.storage.put(state)

    def _read_value(self, name):
        entity = self.storage.get(self.storage.key(self.VARIABLE, name))
        if entity is None:
            return False, None
        return True, entity["value"]

    def _write_value(self, name, exists, value):
        old_exists, old_value = self._read_value(name)
        if old_exists and (not exists or old_value != value):
            self._change_count(old_value, -1)
        if exists and (not old_exists or old_value != value):
            self._change_count(value, 1)

        key = self.storage.key(self.VARIABLE, name)
        if exists:
            entity = self.storage.entity(key)
            entity["value"] = value
            self.storage.put(entity)
        else:
            self.storage.delete(key)

    def _change_count(self, value, delta):
        key = self.storage.key(self.VALUE_COUNT, value)
        entity = self.storage.get(key)
        count = (entity["count"] if entity else 0) + delta
        if count <= 0:
            self.storage.delete(key)
            return

        if entity is None:
            entity = self.storage.entity(key)
        entity["count"] = count
        self.storage.put(entity)

    @staticmethod
    def _format_change(name, exists, value):
        return f"{name} = {value if exists else NONE_TEXT}"
