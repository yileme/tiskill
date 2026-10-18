import json
from pathlib import Path
from unittest import TestCase, mock
from cat import agent

class AgentTest(TestCase):
    def test_cli_contract(self):
        def run(args, **kw):
            self.assertIn('read-only', args)
            self.assertIn('--search', args)
            self.assertIn('--ephemeral', args)
            self.assertIn('question', kw['input'])
            Path(args[args.index('--output-last-message')+1]).write_text(json.dumps({'reply':'ok','after':None,'reason':None}))
            return mock.Mock(returncode=0)
        with mock.patch.object(agent.shutil,'which',return_value='/bin/codex'), mock.patch.object(agent.subprocess,'run',side_effect=run):
            self.assertEqual(agent.respond({'source':'源','target':'target'},'question',[])['reply'],'ok')

    def test_shortcuts_load_real_skill_rules(self):
        self.assertIn('证据',agent.skill_context('collocation'))
        self.assertIn('tis-real-english',agent.skill_context('collocation'))
        self.assertIn('简体中文',agent.skill_context('plain'))

    def test_skill_contents_and_references_are_loaded(self):
        root = Path(agent.__file__).resolve().parents[1] / 'skills'
        for action, names in [('collocation', ['tis-usage-evidence', 'tis-real-english']), ('plain', ['tis-plain-language'])]:
            context = agent.skill_context(action)
            for name in names:
                self.assertIn((root/name/'SKILL.md').read_text(), context)
                for ref in (root/name/'references').glob('*.md'):
                    self.assertIn(ref.read_text(), context)

    def test_unknown_action_rejected(self):
        with self.assertRaises(ValueError): agent.respond({'source':'s','target':'t'},'q',[],'unknown')

    def test_citation_shape_is_not_verification(self):
        def run(args, **kw):
            Path(args[args.index('--output-last-message')+1]).write_text(json.dumps({'reply':'“fabricated quote” [source](https://example.com)', 'after':None, 'reason':None}))
            return mock.Mock(returncode=0)
        with mock.patch.object(agent.shutil,'which',return_value='/bin/codex'), mock.patch.object(agent.subprocess,'run',side_effect=run):
            result=agent.respond({'source':'s','target':'t'},'q',[],'collocation')
            self.assertEqual(result['evidenceStatus'], 'unverified')
            self.assertIn('待人工核对', result['reply'])

    def test_every_action_receives_shared_voice_and_safety(self):
        voice = (Path(agent.__file__).resolve().parents[1]/'docs/voice-and-interaction.md').read_text()
        for action in ('discussion', 'collocation', 'plain', 'ambiguity', 'terminology'):
            with self.subTest(action=action):
                def run(args, **kw):
                    self.assertIn(voice, kw['input'])
                    self.assertIn('不执行 shell、MCP', kw['input'])
                    self.assertIn('只输出指定 JSON', kw['input'])
                    if action == 'ambiguity':
                        self.assertIn('原文条件、否定和承诺强度', kw['input'])
                    Path(args[args.index('--output-last-message')+1]).write_text(json.dumps({'reply':'待核实', 'after':None, 'reason':None}))
                    return mock.Mock(returncode=0)
                with mock.patch.object(agent.shutil, 'which', return_value='/bin/codex'), mock.patch.object(agent.subprocess, 'run', side_effect=run):
                    result = agent.respond({'source':'尚未批准','target':'has been approved'}, '检查', [], action)
                    self.assertIsNone(result['after'])
                    if action in ('collocation', 'terminology'):
                        self.assertEqual(result['evidenceStatus'], 'unverified')

    def test_missing_shared_voice_fails_before_cli_execution(self):
        with mock.patch.object(agent.shutil, 'which', return_value='/bin/codex'), mock.patch.object(agent.Path, 'read_text', side_effect=FileNotFoundError), mock.patch.object(agent.subprocess, 'run') as run:
            with self.assertRaises(FileNotFoundError):
                agent.respond({'source':'s','target':'t'}, 'q', [])
            run.assert_not_called()
