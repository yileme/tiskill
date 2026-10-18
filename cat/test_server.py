import json
import os
from pathlib import Path
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from cat import server


class EditorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.http = server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        cls.thread = threading.Thread(target=cls.http.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.http.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown(); cls.http.server_close()

    def setUp(self):
        # Each test gets an isolated data directory, so tests cannot leak projects into each other.
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        server.DATA = Path(self.temp.name)

    def call(self, route, body=None, method='GET', raw=False, binary=False):
        payload = json.dumps(body).encode() if body is not None else None
        request = Request(self.base + route, payload, {'Origin': self.base, 'Content-Type': 'application/json'} if body is not None else {}, method=method)
        try:
            with urlopen(request) as response:
                data = response.read()
                status = response.status
        except HTTPError as error:
            return error.code, json.loads(error.read())
        if binary:
            return status, data
        text_route = (raw or route.startswith('/api/export')
                      or route.split('?')[0] in ('/', '/index.html', '/style.css', '/app.js'))
        return status, data.decode() if text_route else json.loads(data)

    def test_evidence_routes_removed(self):
        for path in ['/evidence.js', '/api/evidence', '/api/practice']:
            self.assertEqual(self.call(path, raw=True)[0], 404)
        for method in ['POST', 'PATCH', 'DELETE']:
            for path in ['/api/evidence', '/api/practice']:
                self.assertEqual(self.call(path, {}, method)[0], 404)


    def test_roundtrip_conflicts_undo_export(self):
        status, project = self.call('/api/project', {'title': '测试译稿', 'segments': [{'source': '一日为师'}]}, 'POST')
        self.assertEqual(status, 200)
        self.assertEqual(len(project['segments']), 1)
        self.assertEqual(self.call('/api/project', {'title': 'replace', 'segments': [{'source': 'new'}]}, 'POST')[0], 409)
        status, saved = self.call('/api/segments/1', {'target': 'A teacher for a day', 'status': 'draft', 'expectedVersion': 0}, 'PATCH')
        self.assertEqual(status, 200)
        self.assertEqual(self.call('/api/segments/1', {'target': 'stale', 'expectedVersion': 0}, 'PATCH')[0], 409)
        proposal = {'segmentId': '1', 'before': 'A teacher for a day', 'after': 'A teacher for one day', 'expectedVersion': 1}
        status, applied = self.call('/api/proposals/apply', {'proposal': proposal}, 'POST')
        self.assertEqual(applied['segment']['target'], 'A teacher for one day')
        self.assertEqual(self.call('/api/proposals/apply', {'proposal': proposal}, 'POST')[0], 409)
        status, undone = self.call('/api/undo', {'segmentId': '1', 'expectedVersion': 2}, 'POST')
        self.assertEqual(undone['segment']['target'], 'A teacher for a day')
        self.assertEqual(self.call('/api/project')[1]['segments'][0]['target'], 'A teacher for a day')
        self.assertIn('A teacher for a day', self.call('/api/export.md')[1])

    def test_notes_roundtrip_independent_of_translation_and_history(self):
        self.call('/api/project', {'title':'Notes','segments':[{'source':'一'},{'source':'二'}]}, 'POST')
        self.call('/api/segments/1', {'target':'One','expectedVersion':0}, 'PATCH')
        before = self.call('/api/project')[1]
        route = '/api/segments/1/note'
        self.assertEqual(self.call(route, {'note':'核实术语','expectedNote':''}, 'PATCH')[0], 200)
        details = self.call('/api/segments/1/details')[1]
        self.assertEqual(details['note'], '核实术语')
        self.assertEqual(details['history'], [{'target':'','status':'empty'}])
        self.assertEqual(self.call('/api/project')[1], before)
        self.assertEqual(server.read_data()['notes']['1'], '核实术语')
        self.assertEqual(self.call('/api/segments/2/details')[1]['note'], '')
        self.assertEqual(self.call(route, {'note':'','expectedNote':'核实术语'}, 'PATCH')[0], 200)
        self.assertEqual(self.call('/api/segments/1/details')[1]['note'], '')

    def test_notes_conflict_validation_and_missing_segment(self):
        project = self.call('/api/project', {'title':'Notes','segments':[{'source':'一'}]}, 'POST')[1]
        route = '/api/segments/1/note'
        self.call(route, {'note':'saved','expectedNote':''}, 'PATCH')
        self.assertEqual(self.call(route, {'note':'stale','expectedNote':''}, 'PATCH')[0], 409)
        self.assertEqual(self.call(route, {'note':'other','expectedNote':'saved','projectId':'old'}, 'PATCH')[0], 409)
        for payload in ({'note':42,'expectedNote':'saved'}, {'note':'x'*5001,'expectedNote':'saved'}, {'note':'missing guard'}):
            self.assertEqual(self.call(route, payload, 'PATCH')[0], 400)
        self.assertEqual(self.call('/api/segments/missing/details')[0], 404)
        self.assertEqual(self.call('/api/segments/missing/note', {'note':'x','expectedNote':''}, 'PATCH')[0], 404)
        self.assertEqual(self.call('/api/segments/1/details')[1]['note'], 'saved')
        self.assertEqual(self.call(route, {'note':'x'*5000,'expectedNote':'saved'}, 'PATCH')[0], 200)
        self.assertEqual(self.call('/details.js', raw=True)[0], 200)

    def test_static_page_exposes_cat_grid(self):
        status, html = self.call('/', raw=True)
        self.assertEqual(status, 200)
        for marker in ('段号', '状态', '原文', '译文', 'quick-find', 'concordance-input', 'confirm-segment'):
            self.assertIn(marker, html)
        status, script = self.call('/app.js', raw=True)
        self.assertEqual(status, 200)
        self.assertIn('confirmSegment', script)
        self.assertIn("status: 'confirmed'", script)
        status, css = self.call('/style.css', raw=True)
        self.assertEqual(status, 200)
        self.assertIn('.segment-row', css)

    def test_export_modes_fonts_and_docx_structure(self):
        import io, zipfile
        self.call('/api/project', {'title': '导出测试 A/B', 'segments': [
            {'source': '第一段原文'}, {'source': '第二段原文'}]}, 'POST')
        self.call('/api/segments/1', {'target': 'First target', 'status': 'confirmed', 'expectedVersion': 0}, 'PATCH')
        self.call('/api/segments/2', {'target': 'Second target', 'status': 'draft', 'expectedVersion': 0}, 'PATCH')

        status, text = self.call('/api/export.md?mode=target', raw=True)
        self.assertEqual(status, 200)
        self.assertIn('First target', text)
        self.assertNotIn('第一段原文', text)

        _status, text = self.call('/api/export.md?mode=stacked', raw=True)
        self.assertIn('第一段原文', text)
        self.assertIn('First target', text)

        _status, text = self.call('/api/export.md?mode=table', raw=True)
        self.assertIn('| 原文 | 译文 |', text)

        _status, html = self.call('/api/export.html?mode=table', raw=True)
        self.assertIn('Arial', html)
        self.assertIn('SimSun', html)
        self.assertIn('第一段原文', html)
        self.assertIn('A4 landscape', html)

        _status, blob = self.call('/api/export.docx?mode=table', binary=True)
        self.assertTrue(blob.startswith(b'PK'), 'docx must be a zip container')
        with zipfile.ZipFile(io.BytesIO(blob)) as archive:
            names = archive.namelist()
            document = archive.read('word/document.xml').decode()
            styles = archive.read('word/styles.xml').decode()
        for name in ('[Content_Types].xml', '_rels/.rels', 'word/document.xml', 'word/styles.xml'):
            self.assertIn(name, names)
        self.assertIn('<w:tbl>', document)
        self.assertIn('第一段原文', document)
        self.assertIn('First target', document)
        self.assertIn('w:eastAsia="SimSun"', styles)
        self.assertIn('w:ascii="Arial"', styles)

        _status, single = self.call('/api/export.docx?mode=target', binary=True)
        with zipfile.ZipFile(io.BytesIO(single)) as archive:
            single_document = archive.read('word/document.xml').decode()
        self.assertIn('First target', single_document)
        self.assertNotIn('第一段原文', single_document)
        self.assertNotIn('<w:tbl>', single_document)

        self.assertEqual(self.call('/api/export.md?mode=bogus')[0], 400)
        self.assertEqual(self.call('/api/export.docx?mode=bogus')[0], 400)

    def test_export_download_headers(self):
        self.call('/api/project', {'title': '导出标题', 'segments': [{'source': '原文'}]}, 'POST')
        request = Request(self.base + '/api/export.docx?mode=stacked')
        with urlopen(request) as response:
            disposition = response.headers['Content-Disposition']
            content_type = response.headers['Content-Type']
        self.assertIn('attachment', disposition)
        self.assertIn("filename*=UTF-8''", disposition)
        self.assertIn('%E5%AF%BC%E5%87%BA', disposition)  # "导出" percent-encoded
        self.assertEqual(content_type, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')

    def test_resource_routes(self):
        body={'kind':'terms','source':'设备','target':'device','sourceLocale':'zh-CN','targetLocale':'en'}
        self.assertEqual(self.call('/api/resources',body,'POST')[0],200)
        code,data=self.call('/api/resources?kind=terms&sourceLocale=zh-CN&targetLocale=en')
        self.assertEqual(code,200)
        self.assertEqual(data['items'][0]['target'],'device')

    def test_csv_library_mount_and_edit(self):
        csv='source,target,sourceLocale,targetLocale\n临床试验,clinical trial,zh-CN,en\n'
        code,lib=self.call('/api/libraries',{'kind':'terms','name':'术语试验','csv':csv},'POST')
        self.assertEqual(code,200)
        ident=lib['library']['id']
        items=self.call('/api/resources?kind=terms&sourceLocale=zh-CN&targetLocale=en')[1]['items']
        item=next(x for x in items if x['libraryId']==ident)
        payload={'id':item['id'],'libraryId':ident,'target':'clinical trials','expectedTarget':item['target']}
        self.assertEqual(self.call('/api/resources',payload,'PATCH')[0],200)
        self.assertEqual(self.call('/api/resources',payload,'PATCH')[0],409)
        self.assertEqual(self.call('/api/libraries',{'id':ident,'mounted':False},'PATCH')[0],200)
        self.assertFalse(any(x['libraryId']==ident for x in self.call('/api/resources?kind=terms&sourceLocale=zh-CN&targetLocale=en')[1]['items']))

    def test_project_mount_isolation_and_csv_download(self):
        from uuid import UUID
        first = self.call('/api/project', {'title':'A','segments':[{'source':'设备'}]}, 'POST')[1]
        UUID(first['id'])
        lib = self.call('/api/libraries', {'kind':'terms','name':'Private A','csvContent':'source,target,sourceLocale,targetLocale\n设备,device,zh-CN,en\n'}, 'POST')[1]['library']
        route = '/api/resources?kind=terms&sourceLocale=zh-CN&targetLocale=en'
        item = next(x for x in self.call(route)[1]['items'] if x['libraryId'] == lib['id'])
        self.assertEqual(self.call('/api/library.csv?id='+lib['id'], binary=True)[0], 200)
        second = self.call('/api/project', {'title':'B','segments':[{'source':'设备'}], 'confirmReplace':True}, 'POST')[1]
        self.assertNotEqual(first['id'], second['id'])
        self.assertFalse(any(x['libraryId']==lib['id'] for x in self.call(route)[1]['items']))
        self.assertEqual(self.call('/api/library.csv?id='+lib['id'], binary=True)[0], 400)
        edit = {'id':item['id'],'libraryId':lib['id'],'target':'equipment','expectedVersion':item['version'],'expectedTarget':item['target']}
        self.assertEqual(self.call('/api/resources',edit,'PATCH')[0],400)
        self.call('/api/libraries', {'libraryId':lib['id'],'mounted':True}, 'POST')
        self.assertEqual(self.call('/api/resources',edit,'PATCH')[0],200)
        self.assertEqual(self.call('/api/resources',edit,'PATCH')[0],409)

    def test_chat_action_forwarded(self):
        from unittest.mock import patch
        self.call('/api/project', {'title':'A','segments':[{'source':'源'}]}, 'POST')
        with patch.object(server.agent, 'respond', return_value={'reply':'ok','after':None}) as respond:
            self.assertEqual(self.call('/api/chat', {'segmentId':'1','message':'检查','action':'plain'}, 'POST')[0],200)
            self.assertEqual(respond.call_args.args[3], 'plain')

    def test_confirm_then_next_segment_persists(self):
        self.call('/api/project', {'title': '确认流程', 'segments': [{'source': '第一段'}, {'source': '第二段'}]}, 'POST')
        self.call('/api/segments/1', {'target': 'First segment', 'status': 'confirmed', 'expectedVersion': 0}, 'PATCH')
        project = self.call('/api/project')[1]
        self.assertEqual(project['segments'][0]['status'], 'confirmed')
        self.assertEqual(project['segments'][1]['status'], 'empty')


if __name__ == '__main__': unittest.main()
