import unittest

from cat import exports


class ExportTest(unittest.TestCase):
    def doc(self):
        return {"title": '教师节/试译', "segments": [
            {"source": "第一段\u000b原文", "target": "First target"},
            {"source": "第二段", "target": ""},
        ]}

    def test_modes_are_validated(self):
        for mode in exports.MODES:
            self.assertTrue(exports.export_markdown(self.doc(), mode))
        for mode in ("bogus", "", "Target"):
            with self.assertRaises(ValueError):
                exports.export_markdown(self.doc(), mode)

    def test_control_characters_and_filenames_are_cleaned(self):
        document = self.doc()
        markdown = exports.export_markdown(document, 'stacked')
        self.assertIn('第一段原文', markdown)
        self.assertNotIn('\u000b', markdown)
        self.assertEqual(exports.safe_name('教师节/试译'), '教师节试译')
        self.assertEqual(exports.safe_name('   '), 'tiskill-CAT')
        self.assertEqual(exports.filename(document, 'target', 'docx'), '教师节试译-译文.docx')

    def test_empty_target_keeps_positions(self):
        document = {"title": "t", "segments": [{"source": "甲", "target": ""}, {"source": "乙", "target": "B"}]}
        self.assertNotIn('甲', exports.export_markdown(document, 'target'))
        self.assertIn('B', exports.export_markdown(document, 'target'))
        table = exports.export_markdown(document, 'table')
        self.assertIn('| 甲 | ', table)


if __name__ == '__main__': unittest.main()
