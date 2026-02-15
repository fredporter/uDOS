from wizard.routes import ucode_stream_utils as utils


def test_sse_event_format():
    payload = utils.sse_event("chunk", {"text": "hello"})
    text = payload.decode("utf-8")
    assert text.startswith("event: chunk\n")
    assert "data: " in text
    assert text.endswith("\n\n")


def test_iter_text_chunks_single_line():
    chunks = list(utils.iter_text_chunks("hello"))
    assert chunks == ["hello"]


def test_iter_text_chunks_multiline():
    chunks = list(utils.iter_text_chunks("a\nb\nc"))
    assert chunks == ["a\n", "b\n", "c"]
