import json
import tempfile
import unittest
from pathlib import Path

from fwbuild import comply

# Trascrizione vera: una sessione su haiku che legge `nota.txt`.
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "stream.jsonl"


def lines() -> list[str]:
    return FIXTURE.read_text(encoding="utf-8").splitlines()


def write(d: str, rows: list[str]) -> Path:
    path = Path(d) / "stream.jsonl"
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return path


class TestRead(unittest.TestCase):
    def test_reads_tool_calls_in_order_from_a_real_transcript(self):
        """Le chiamate sono ciò che si etichetta: una persa o fuori ordine fa
        leggere come saltato un passo che la regola ha visto eseguire."""
        got = comply.read(FIXTURE)
        self.assertEqual([c.name for c in got.calls], ["Read"])
        self.assertTrue(got.calls[0].input["file_path"].endswith("nota.txt"))
        self.assertIsNone(got.calls[0].parent)
        self.assertEqual(got.result, "prima riga della nota")
        self.assertFalse(got.is_error)

        rows = lines()
        later = json.loads(next(r for r in rows if '"tool_use"' in r and '"assistant"' in r))
        later["message"]["content"][0].update(name="Grep", input={"pattern": "x"})
        with tempfile.TemporaryDirectory() as d:
            got = comply.read(write(d, rows[:-1] + [json.dumps(later), rows[-1]]))
        self.assertEqual([c.name for c in got.calls], ["Read", "Grep"])

    def test_a_transcript_without_result_is_not_a_completed_run(self):
        """Una sessione interrotta ha le chiamate fatte fin lì: contarla come
        esecuzione completa abbassa la conformità di una regola che non ha
        avuto il tempo di arrivare in fondo."""
        with tempfile.TemporaryDirectory() as d:
            got = comply.read(write(d, lines()[:-1]))
        self.assertIsNone(got.result)
        self.assertEqual([c.name for c in got.calls], ["Read"])

    def test_a_line_that_is_not_json_names_its_number(self):
        with tempfile.TemporaryDirectory() as d:
            path = write(d, lines()[:3] + ["non json"] + lines()[3:])
            with self.assertRaises(ValueError) as e:
                comply.read(path)
        self.assertIn(":4:", str(e.exception))


if __name__ == "__main__":
    unittest.main()
