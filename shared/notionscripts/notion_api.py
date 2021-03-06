#!/usr/bin/env -S PATH="${PATH}:/usr/local/bin" python3
from notionscripts.block_presenter import BlockPresenter

from cachetools import cached

from notion.client import NotionClient
from notion.block import TextBlock


class NotionApi():
    def __init__(self, token):
        self.token = token

    @cached(cache={})
    def client(self):
        return NotionClient(token_v2=self.token, monitor=False)

    def __collection_view(self, collection_id, view_id):
        return self.client().get_collection_view(f"https://www.notion.so/{collection_id}?v={view_id}")

    def block_content(self, block_id):
        block = self.client().get_block(block_id)

        return BlockPresenter(block)

    def block_children(self, block_id):
        block = self.client().get_block(block_id)

        return [BlockPresenter(child) for child in block.children]

    def block_append(self, block_id, data):
        block = self.client().get_block(block_id)

        new_block = block.children.add_new(TextBlock, title=data["title"])

        return BlockPresenter(new_block)

    def block_update(self, block_id, data):
        block = self.client().get_block(block_id)

        with self.client().as_atomic_transaction():
            for key, val in data.items():
                setattr(block, key, val)

        return BlockPresenter(block)

    def block_delete(self, block_id):
        block = self.client().get_block(block_id)

        block.remove()

        return BlockPresenter(block)

    def collection_view_content(self, collection_id, view_id):
        collection_view = self.__collection_view(collection_id, view_id)
        results = collection_view.default_query().execute()

        return [BlockPresenter(row) for row in results]

    def collection_append(self, collection_id, view_id, data):
        collection_view = self.__collection_view(collection_id, view_id)

        row = collection_view.collection.add_row(**data)

        return BlockPresenter(row)
