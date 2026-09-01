import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import transcript


def entry(**kw) -> str:
    return json.dumps(kw) + "\n"


def assistant(cache_read=0, cache_creation=0, inp=0, out=0, tools=(), **kw) -> str:
    return entry(
        type="assistant",
        message={
            "content": [{"type": "tool_use", "name": t} for t in tools],
            "usage": {
                "input_tokens": inp,
                "cache_creation_input_tokens": cache_creation,
                "cache_read_input_tokens": cache_read,
                "output_tokens": out,
            },
        },
        **kw,
    )


def human(text="ciao") -> str:
    return entry(type="user", message={"role": "user", "content": text})


def tool_result() -> str:
    return entry(
        type="user",
        message={"role": "user", "content": [{"type": "tool_result", "content": "ok"}]},
    )


def write(path: Path, *lines: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(lines), encoding="utf-8")
    return path


class TestLeg(unittest.TestCase):
    def test_sums_the_four_kinds_of_token(self):
        with TemporaryDirectory() as d:
            p = write(Path(d) / "s.jsonl", assistant(inp=1, cache_creation=2, cache_read=3, out=4))
            leg = transcript.read_leg(p, "x")
            self.assertEqual((leg.input, leg.cache_creation, leg.cache_read, leg.output), (1, 2, 3, 4))
            self.assertEqual(leg.total, 10)

    def test_spawn_context_is_the_first_prompt_not_the_sum(self):
        """Ciò che uno spawn carica è il prompt del **primo** turno. Sommare i
        prompt di tutti i turni conta lo stesso contesto una volta per turno, ed
        è il modo più facile di gonfiare la tesi che si vuole misurare."""
        with TemporaryDirectory() as d:
            p = write(
                Path(d) / "s.jsonl",
                assistant(inp=2, cache_creation=100, cache_read=900, out=5),
                assistant(cache_read=1010, out=5),
            )
            self.assertEqual(transcript.read_leg(p, "x").spawn_context, 1002)

    def test_counts_turns_tools_and_human_messages(self):
        with TemporaryDirectory() as d:
            p = write(
                Path(d) / "s.jsonl",
                human(), assistant(tools=("Read", "Bash")), tool_result(),
                assistant(), human(),
            )
            leg = transcript.read_leg(p, "x")
            self.assertEqual((leg.turns, leg.tools, leg.human_turns), (2, 2, 2))

    def test_tool_results_and_meta_are_not_human_turns(self):
        """Un risultato di tool è un'entrata `user`: contarlo come intervento
        umano gonfierebbe la metrica che D1 usa per il confronto."""
        with TemporaryDirectory() as d:
            p = write(
                Path(d) / "s.jsonl",
                tool_result(),
                entry(type="user", isMeta=True, message={"content": [{"type": "text", "text": "x"}]}),
            )
            self.assertEqual(transcript.read_leg(p, "x").human_turns, 0)

    def test_skips_malformed_lines(self):
        with TemporaryDirectory() as d:
            p = write(Path(d) / "s.jsonl", "{rotta\n", assistant(out=7), "\n")
            self.assertEqual(transcript.read_leg(p, "x").output, 7)


class TestSession(unittest.TestCase):
    def make(self, d: Path) -> Path:
        main = write(d / "sess.jsonl", human(), assistant(cache_read=1000, out=10))
        write(
            d / "sess" / "subagents" / "agent-1.jsonl",
            assistant(cache_creation=500, cache_read=100, out=5,
                      attributionAgent="explorer", attributionSkill=None, effort="low"),
        )
        write(
            d / "sess" / "subagents" / "agent-2.jsonl",
            assistant(cache_creation=500, cache_read=100, out=5, agentId="abc123"),
        )
        return main

    def test_splits_coordinator_from_subagents(self):
        with TemporaryDirectory() as d:
            s = transcript.read_session(self.make(Path(d)))
            self.assertEqual(s.coordinator.total, 1010)
            self.assertEqual(len(s.subagents), 2)
            self.assertEqual(s.subagent_total, 1210)

    def test_names_subagent_by_attribution_then_agent_id(self):
        with TemporaryDirectory() as d:
            s = transcript.read_session(self.make(Path(d)))
            self.assertEqual(sorted(a.name for a in s.subagents), ["abc123", "explorer"])

    def test_attribution_wins_over_agent_id_even_if_it_comes_later(self):
        """`agentId` sta già sulla prima riga, `attributionAgent` compare dal
        primo turno assistant: fermarsi alla prima riga utile dà l'id opaco al
        posto del ruolo, e un rapporto di ruoli opachi non si legge."""
        with TemporaryDirectory() as d:
            main = write(Path(d) / "s.jsonl", assistant(out=1))
            write(
                Path(d) / "s" / "subagents" / "agent-1.jsonl",
                entry(type="user", agentId="ff00", message={"content": "vai"}),
                assistant(out=1, agentId="ff00", attributionAgent="tester"),
            )
            self.assertEqual(transcript.read_session(main).subagents[0].name, "tester")

    def test_session_without_subagents_has_none(self):
        with TemporaryDirectory() as d:
            main = write(Path(d) / "solo.jsonl", assistant(out=1))
            s = transcript.read_session(main)
            self.assertEqual(s.subagents, [])
            self.assertEqual(s.subagent_total, 0)

    def test_report_states_the_split(self):
        with TemporaryDirectory() as d:
            out = transcript.report(transcript.read_session(self.make(Path(d))))
            self.assertIn("coordinatore", out)
            self.assertIn("explorer", out)
            self.assertIn("2.220", out)  # totale di sessione, separatore italiano


class TestAggregation(unittest.TestCase):
    def test_csv_has_a_row_per_leg_plus_header(self):
        with TemporaryDirectory() as d:
            main = write(Path(d) / "s.jsonl", human(), assistant(cache_read=9, out=1))
            write(Path(d) / "s" / "subagents" / "a.jsonl", assistant(out=2, attributionAgent="tester"))
            rows = transcript.csv_rows([transcript.read_session(main)])
            self.assertEqual(rows[0][0], "sessione")
            self.assertEqual([r[1] for r in rows[1:]], ["coordinatore", "tester"])

    def test_prompts_returns_only_human_asks(self):
        """Il corpus dei task di D1 esce dal lavoro già fatto, non
        dall'immaginazione: gli unici task rappresentativi sono quelli chiesti."""
        with TemporaryDirectory() as d:
            p = write(
                Path(d) / "s.jsonl",
                human("aggiungi il filtro"), tool_result(), assistant(out=1),
                human("ora i test"),
            )
            self.assertEqual(transcript.prompts(p), ["aggiungi il filtro", "ora i test"])

    def test_prompts_skips_slash_commands(self):
        """Un `/comando` è un'invocazione, non la descrizione di un task."""
        with TemporaryDirectory() as d:
            p = write(Path(d) / "s.jsonl", human("/graphify"), human("sistema il bug"))
            self.assertEqual(transcript.prompts(p), ["sistema il bug"])

    def test_prompts_drops_system_injections(self):
        """`<command-message>`, `<task-notification>`, `<local-command-stdout>`
        sono entrate `user` che l'utente non ha scritto: nel corpus dei task
        sarebbero rumore travestito da richiesta."""
        with TemporaryDirectory() as d:
            p = write(
                Path(d) / "s.jsonl",
                human("<command-message>graphify</command-message> <command-name>/graphify</command-name>"),
                human("<task-notification> <task-id>abc</task-id> </task-notification>"),
                human("This session is being continued from a previous conversation. Summary: ..."),
                human("vero task"),
            )
            self.assertEqual(transcript.prompts(p), ["vero task"])

    def test_prompts_drops_a_real_three_tag_injection(self):
        """Input vero, preso da un transcript archiviato. Tre tag di fila: se
        la regola per i tag autochiusi mangia anche quelli di apertura, la
        coppia si spezza e resta il testo interno travestito da richiesta."""
        with TemporaryDirectory() as d:
            p = write(Path(d) / "s.jsonl", human(
                "<command-name>/compact</command-name> "
                "<command-message>compact</command-message> "
                "<command-args></command-args>"))
            self.assertEqual(transcript.prompts(p), [])

    def test_prompts_keeps_the_ask_that_follows_an_injection(self):
        """`<ide_opened_file>` viene anteposto a un messaggio vero: scartare
        l'entrata intera perderebbe la richiesta, non il rumore."""
        with TemporaryDirectory() as d:
            p = write(
                Path(d) / "s.jsonl",
                human("<ide_opened_file>ha aperto x.md</ide_opened_file>allinea il file"),
            )
            self.assertEqual(transcript.prompts(p), ["allinea il file"])


if __name__ == "__main__":
    unittest.main()
