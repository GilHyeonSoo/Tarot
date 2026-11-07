import json
import unittest
from unittest.mock import patch

import app as backend


class DiscordSessionLogTests(unittest.TestCase):
    def setUp(self):
        backend.app.config['TESTING'] = True
        backend.limiter.enabled = False
        self.http = backend.app.test_client()
        self.webhook = patch.object(backend, 'DISCORD_WEBHOOK_URL', 'https://example.invalid/webhook')
        self.webhook.start()
        self.addCleanup(self.webhook.stop)
        self.sender = patch.object(backend.requests, 'post')
        self.post = self.sender.start()
        self.addCleanup(self.sender.stop)

    def payload(self, **changes):
        return {
            'sessionId': '12345678-1234-1234-1234-123456789abc',
            'situation': '오늘 기분이 좋아요. 어떻게 보내면 좋을까요?',
            'completed': True,
            'interpretation': '**태양** 카드처럼 작은 즐거움을 나누어보세요.\n즐거운 일을 기록해보세요.',
            'spread': 'one',
            'spreadLabel': '오늘의 메시지 (1장)',
            'device': {'summary': 'iPhone · Safari', 'userAgent': 'PRIVATE-USER-AGENT-TEST'},
            **changes,
        }

    def test_completed_reading_sends_question_and_full_advice_in_one_message(self):
        payload = self.payload(interpretation='**태양**의 즐거움을 나누어보세요. @everyone <@123>')
        response = self.http.post('/api/log-session', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json['delivered'])
        self.post.assert_called_once()
        sent = self.post.call_args.kwargs
        self.assertIn(payload['situation'], sent['json']['content'])
        self.assertIn('AI 해설\n', sent['json']['content'])
        self.assertIn(payload['interpretation'], sent['json']['content'])
        self.assertEqual(sent['json']['allowed_mentions'], {'parse': []})
        self.assertEqual(sent['params'], {'wait': 'true'})
        self.assertNotIn('files', sent)
        self.assertNotIn('세션:', sent['json']['content'])
        self.assertNotIn(payload['sessionId'], sent['json']['content'])
        self.assertNotIn('User-Agent', sent['json']['content'])
        self.assertNotIn(payload['device']['userAgent'], sent['json']['content'])
        self.assertIn('기기: iPhone · Safari', sent['json']['content'])

    def test_long_korean_reading_is_attached_in_full_without_extra_posts(self):
        payload = self.payload(interpretation=('카드의 조언을 천천히 살펴보세요.\n' * 400))
        self.assertGreater(len(payload['interpretation'].encode('utf-8')), 16384)
        response = self.http.post('/api/log-session', json=payload)
        self.assertEqual(response.status_code, 200)
        self.post.assert_called_once()
        sent = self.post.call_args.kwargs
        metadata = json.loads(sent['data']['payload_json'])
        filename, contents, mime = sent['files']['files[0]']
        self.assertLessEqual(len(metadata['content']), 2000)
        self.assertEqual(metadata['allowed_mentions'], {'parse': []})
        self.assertEqual(filename, 'tarot-reading.txt')
        self.assertIn('text/plain', mime)
        log = contents.decode('utf-8')
        self.assertIn(payload['situation'], log)
        self.assertIn(payload['interpretation'].strip(), log)
        for visible_text in [metadata['content'], filename, log]:
            self.assertNotIn('세션:', visible_text)
            self.assertNotIn(payload['sessionId'], visible_text)
            self.assertNotIn('User-Agent', visible_text)
            self.assertNotIn(payload['device']['userAgent'], visible_text)

    def test_emoji_length_uses_a_conservative_discord_limit(self):
        response = self.http.post('/api/log-session', json=self.payload(interpretation='🌙' * 1000))
        self.assertEqual(response.status_code, 200)
        self.assertIn('files', self.post.call_args.kwargs)

    def test_unfinished_session_never_sends_partial_advice(self):
        response = self.http.post('/api/log-session', json=self.payload(completed=False, interpretation='미완성 해설'))
        self.assertEqual(response.status_code, 200)
        message = self.post.call_args.kwargs['json']['content']
        self.assertIn('완료: 아니오', message)
        self.assertNotIn('미완성 해설', message)
        self.assertNotIn('AI 해설', message)

    def test_older_clients_without_advice_still_work(self):
        payload = self.payload()
        del payload['interpretation']
        self.assertEqual(self.http.post('/api/log-session', json=payload).status_code, 200)
        self.assertNotIn('AI 해설', self.post.call_args.kwargs['json']['content'])

    def test_rejects_invalid_advice_and_body_shapes_without_sending(self):
        for value in [None, [], {}, 42, 'a' * 10001]:
            self.assertEqual(self.http.post('/api/log-session', json=self.payload(interpretation=value)).status_code, 400)
        for value in [[], ['bad'], 'bad']:
            self.assertEqual(self.http.post('/api/log-session', json=value).status_code, 400)
        self.post.assert_not_called()

    def test_discord_failure_does_not_fail_the_reading_flow_or_leak_webhook(self):
        self.post.side_effect = RuntimeError('private webhook token')
        with self.assertLogs(backend.logger, level='ERROR') as logs:
            response = self.http.post('/api/log-session', json=self.payload())
        self.assertEqual(response.status_code, 502)
        self.assertFalse(response.json['success'])
        self.assertTrue(response.json['retryable'])
        self.assertNotIn('private webhook token', ''.join(logs.output))

    def test_missing_webhook_is_not_reported_as_a_successful_delivery(self):
        with patch.object(backend, 'DISCORD_WEBHOOK_URL', ''):
            response = self.http.post('/api/log-session', json=self.payload())
        self.assertEqual(response.status_code, 503)
        self.assertFalse(response.json['success'])
        self.assertFalse(response.json['retryable'])
        self.post.assert_not_called()

    def test_discord_permission_failure_is_not_retried(self):
        error = backend.requests.HTTPError('private webhook URL')
        error.response = type('Response', (), {'status_code': 403})()
        self.post.side_effect = error
        response = self.http.post('/api/log-session', json=self.payload())
        self.assertEqual(response.status_code, 502)
        self.assertFalse(response.json['retryable'])


if __name__ == '__main__':
    unittest.main()
