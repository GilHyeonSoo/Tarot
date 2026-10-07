"""Keep the browser connection alive even while the AI provider is silent."""
import json
import logging
import os
import queue
import threading
import time

from openai import APIConnectionError, APITimeoutError, AuthenticationError, RateLimitError
from httpx import TimeoutException, TransportError

logger = logging.getLogger(__name__)
HEARTBEAT_SECONDS = 10
READING_TIMEOUT_SECONDS = 90
_slots = threading.BoundedSemaphore(max(1, int(os.getenv('AI_MAX_CONCURRENT', '4'))))


def _event(data):
    return f'data: {json.dumps(data, ensure_ascii=False)}\n\n'


def stream_reading(client, messages, max_tokens):
    if not _slots.acquire(blocking=False):
        yield _event({'error': '서버가 잠시 혼잡합니다.', 'code': 'busy', 'retryable': True})
        return

    events = queue.Queue(maxsize=32)
    cancelled = threading.Event()

    def publish(data):
        while not cancelled.is_set():
            try:
                events.put(data, timeout=0.2)
                return
            except queue.Full:
                continue

    def produce():
        stream = None
        try:
            if cancelled.is_set():
                return
            stream = client.chat.completions.create(
                model='deepseek-chat', messages=messages,
                temperature=0.25, max_tokens=max_tokens, stream=True,
            )
            has_content = False
            finish_reason = None
            for chunk in stream:
                if cancelled.is_set():
                    return
                if not chunk.choices:
                    continue
                choice = chunk.choices[0]
                if choice.delta.content:
                    has_content = True
                    publish({'content': choice.delta.content})
                if choice.finish_reason:
                    finish_reason = choice.finish_reason
            if has_content and finish_reason == 'stop':
                publish({'done': True})
            else:
                publish({'error': '해설이 완성되지 않았습니다.', 'code': 'interrupted',
                         'retryable': finish_reason != 'length'})
        except Exception as exc:
            # Log failure type, never the user's question or provider credentials.
            logger.warning('AI reading failed: %s', type(exc).__name__)
            code = 'timeout' if isinstance(exc, (APITimeoutError, TimeoutException)) else 'server'
            if isinstance(exc, RateLimitError):
                code = 'busy'
            retryable = isinstance(exc, (APIConnectionError, APITimeoutError, RateLimitError, TransportError))
            status = getattr(exc, 'status_code', 0) or 0
            retryable = retryable or status >= 500
            if isinstance(exc, AuthenticationError):
                retryable = False
            publish({'error': '해설을 가져오지 못했습니다.', 'code': code, 'retryable': retryable})
        finally:
            try:
                if stream is not None:
                    try:
                        stream.close()
                    except Exception as exc:
                        logger.warning('AI stream cleanup failed: %s', type(exc).__name__)
            finally:
                _slots.release()

    worker = threading.Thread(target=produce, daemon=True, name='tarot-reading')
    try:
        worker.start()
    except Exception:
        _slots.release()
        raise

    deadline = time.monotonic() + READING_TIMEOUT_SECONDS
    try:
        yield ': keepalive\n\n'
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                yield _event({'error': '해설 대기 시간이 초과되었습니다.', 'code': 'timeout', 'retryable': True})
                return
            try:
                data = events.get(timeout=min(HEARTBEAT_SECONDS, remaining))
            except queue.Empty:
                yield ': keepalive\n\n'
                continue
            yield _event(data)
            if data.get('done') or data.get('error'):
                return
    finally:
        # Disconnected browsers must not leave producers blocked on a full queue.
        cancelled.set()
