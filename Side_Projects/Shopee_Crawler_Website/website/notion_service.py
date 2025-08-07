import os
import json
import time
import threading
from datetime import datetime, timedelta
from notion_client import Client
import logging
import pytz

class NotionUpdatesService:
    def __init__(self, integration_token, page_id):
        # Configure Notion client
        self.notion = Client(auth=integration_token)
        self.page_id = page_id
        self.cache_file = 'instance/notion_cache.json'
        self.cache_duration = 30 * 60  # Increase to 30 minutes for better performance
        self.max_blocks = 50  # Limit number of blocks to process
        
        # 設定 UTC+8 時區
        self.taipei_tz = pytz.timezone('Asia/Taipei')
        
        # Ensure cache directory exists
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _load_cache(self):
        """Load cached data from file"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading cache: {e}")
        return None

    def _save_cache(self, data):
        """Save data to cache file"""
        try:
            cache_data = {
                'timestamp': time.time(),
                'data': data
            }
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving cache: {e}")

    def _is_cache_valid(self, cache_data):
        """Check if cached data is still valid"""
        if not cache_data or 'timestamp' not in cache_data:
            return False
        
        cache_time = cache_data['timestamp']
        current_time = time.time()
        return (current_time - cache_time) < self.cache_duration

    def _parse_rich_text(self, rich_text_array):
        """Parse rich text array and return plain text with basic formatting"""
        if not rich_text_array:
            return ""
        
        text_parts = []
        for text_obj in rich_text_array:
            text = text_obj.get('plain_text', '')
            
            # Handle basic formatting
            annotations = text_obj.get('annotations', {})
            if annotations.get('bold'):
                text = f"**{text}**"
            if annotations.get('italic'):
                text = f"*{text}*"
            if annotations.get('code'):
                text = f"`{text}`"
            
            text_parts.append(text)
        
        return ''.join(text_parts)

    def _fetch_block_children(self, block_id, depth=0, max_depth=3):
        """Recursively fetch children of a block"""
        if depth > max_depth:
            return []
        
        try:
            children_response = self.notion.blocks.children.list(block_id=block_id)
            children = []
            
            for child_block in children_response['results']:
                parsed_child = self._parse_block(child_block, depth + 1, max_depth)
                if parsed_child:
                    children.append(parsed_child)
            
            return children
        except Exception as e:
            self.logger.error(f"Error fetching children for block {block_id}: {e}")
            return []

    def _parse_block(self, block, depth=0, max_depth=3):
        """Parse a single block and its children"""
        block_type = block['type']
        block_data = {
            'id': block['id'],
            'type': block_type,
            'created_time': block['created_time'],
            'depth': depth,
            'children': []
        }
        
        # Handle different block types
        if block_type == 'paragraph':
            rich_text = block['paragraph']['rich_text']
            content = self._parse_rich_text(rich_text)
            if content.strip():
                block_data['content'] = content
            else:
                return None
                
        elif block_type in ['heading_1', 'heading_2', 'heading_3']:
            rich_text = block[block_type]['rich_text']
            content = self._parse_rich_text(rich_text)
            if content.strip():
                block_data['content'] = content
            else:
                return None
                
        elif block_type == 'bulleted_list_item':
            rich_text = block['bulleted_list_item']['rich_text']
            content = self._parse_rich_text(rich_text)
            if content.strip():
                block_data['content'] = content
                block_data['type'] = 'list_item'
            else:
                return None
                
        elif block_type == 'numbered_list_item':
            rich_text = block['numbered_list_item']['rich_text']
            content = self._parse_rich_text(rich_text)
            if content.strip():
                block_data['content'] = content
            else:
                return None
                
        elif block_type == 'toggle':
            rich_text = block['toggle']['rich_text']
            content = self._parse_rich_text(rich_text)
            if content.strip():
                block_data['content'] = content
                # Fetch children of the toggle
                block_data['children'] = self._fetch_block_children(block['id'], depth, max_depth)
            else:
                return None
                
        elif block_type == 'code':
            code_data = block['code']
            content = self._parse_rich_text(code_data['rich_text'])
            language = code_data.get('language', 'text')
            if content.strip():
                block_data['content'] = content
                block_data['language'] = language
            else:
                return None
                
        elif block_type == 'callout':
            rich_text = block['callout']['rich_text']
            content = self._parse_rich_text(rich_text)
            icon = block['callout'].get('icon', {})
            if content.strip():
                block_data['content'] = content
                if icon.get('emoji'):
                    block_data['icon'] = icon['emoji']
            else:
                return None
                
        elif block_type == 'quote':
            rich_text = block['quote']['rich_text']
            content = self._parse_rich_text(rich_text)
            if content.strip():
                block_data['content'] = content
            else:
                return None
                
        else:
            # For unsupported block types, try to get any text content
            self.logger.info(f"Unsupported block type: {block_type}")
            return None
        
        # If the block has children and we haven't reached max depth, fetch them
        if block.get('has_children') and depth < max_depth and block_type != 'toggle':
            block_data['children'] = self._fetch_block_children(block['id'], depth, max_depth)
        
        return block_data

    def _fetch_from_notion(self):
        """Fetch latest data from Notion API with performance optimizations"""
        try:
            self.logger.info("Fetching updates from Notion...")
            
            # Get page content
            page = self.notion.pages.retrieve(page_id=self.page_id)
            
            # Get page blocks (content) with pagination limit
            blocks_response = self.notion.blocks.children.list(
                block_id=self.page_id,
                page_size=self.max_blocks  # Limit number of blocks
            )
            
            # Parse all blocks recursively (but limit depth)
            updates = []
            processed_count = 0
            for block in blocks_response['results']:
                if processed_count >= self.max_blocks:
                    break
                parsed_block = self._parse_block(block, max_depth=2)  # Limit depth
                if parsed_block:
                    updates.append(parsed_block)
                processed_count += 1
            
            result = {
                'page_title': page['properties'].get('title', {}).get('title', [{}])[0].get('plain_text', 'Updates'),
                'last_edited': page['last_edited_time'],
                'updates': updates,
                'fetch_time': datetime.now(self.taipei_tz).isoformat(),
                'total_blocks': len(updates)
            }
            
            self.logger.info(f"Successfully fetched {len(updates)} updates from Notion")
            return result
            
        except Exception as e:
            self.logger.error(f"Error fetching from Notion: {e}")
            return None

    def get_updates(self, force_refresh=False):
        """Get updates with caching logic"""
        # Try to load from cache first
        if not force_refresh:
            cache_data = self._load_cache()
            if cache_data and self._is_cache_valid(cache_data):
                self.logger.info("Serving updates from cache")
                return cache_data['data']
        
        # Fetch fresh data from Notion
        fresh_data = self._fetch_from_notion()
        if fresh_data:
            self._save_cache(fresh_data)
            return fresh_data
        
        # Fallback to cached data if API fails
        cache_data = self._load_cache()
        if cache_data and 'data' in cache_data:
            self.logger.warning("API failed, serving stale cache data")
            return cache_data['data']
        
        # Complete fallback
        return {
            'page_title': 'Updates',
            'last_edited': datetime.now(self.taipei_tz).isoformat(),
            'updates': [],
            'fetch_time': datetime.now(self.taipei_tz).isoformat(),
            'error': 'Unable to load updates'
        }

    def warm_cache_if_needed(self):
        """Check if cache needs warming and do it in background if possible"""
        cache_data = self._load_cache()
        
        # If cache is expired or doesn't exist, try to warm it
        if not cache_data or not self._is_cache_valid(cache_data):
            try:
                # Try a quick non-blocking cache refresh
                import threading
                
                def background_refresh():
                    try:
                        self.logger.info("Background cache warming started")
                        fresh_data = self._fetch_from_notion()
                        if fresh_data:
                            self._save_cache(fresh_data)
                            self.logger.info("Background cache warming completed")
                    except Exception as e:
                        self.logger.error(f"Background cache warming failed: {e}")
                
                # Start background thread for cache warming
                thread = threading.Thread(target=background_refresh, daemon=True)
                thread.start()
                
            except Exception as e:
                self.logger.error(f"Failed to start background cache warming: {e}")

    def refresh_cache(self):
        """Manually refresh the cache"""
        return self.get_updates(force_refresh=True)
