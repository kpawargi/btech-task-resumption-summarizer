from typing import List, Tuple, Callable


def _try_tiktoken_counter() -> Callable[[str], int]:
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        return lambda s: len(enc.encode(s))
    except Exception:
        return lambda s: max(1, len(s.split()))


def chunk_by_token_budget(
    sentence_spans: List[Tuple[str, int, int]],
    token_budget: int,
    overlap_tokens: int = 0,
    min_chunk_tokens: int = 30,
) -> List[Tuple[str, int, int, int]]:
    """
    Returns list of chunks: (chunk_text, char_start, char_end, token_count)

    Strategy:
    - Greedy pack sentences until token_budget reached
    - If overlap_tokens > 0, keep overlap by reusing last few tokens (approx by sentences)
    """
    count_tokens = _try_tiktoken_counter()

    chunks: List[Tuple[str, int, int, int]] = []
    i = 0
    n = len(sentence_spans)

    while i < n:
        cur_texts = []
        cur_start = sentence_spans[i][1]
        cur_end = sentence_spans[i][2]

        cur_tokens = 0
        j = i

        while j < n:
            sent, s_start, s_end = sentence_spans[j]
            t = count_tokens(sent)
            # if single sentence exceeds budget, force include it
            if cur_tokens == 0 and t > token_budget:
                cur_texts = [sent]
                cur_tokens = t
                cur_start, cur_end = s_start, s_end
                j += 1
                break

            if cur_tokens + t <= token_budget:
                cur_texts.append(sent)
                cur_tokens += t
                cur_end = s_end
                j += 1
            else:
                break

        chunk_text = " ".join(cur_texts).strip()
        if chunk_text:
            # enforce min chunk size when possible (except last chunk)
            if cur_tokens < min_chunk_tokens and j < n:
                # try to add one more sentence if it doesn't explode budget too much
                sent, s_start, s_end = sentence_spans[j]
                t = count_tokens(sent)
                if cur_tokens + t <= int(token_budget * 1.25):
                    cur_texts.append(sent)
                    cur_tokens += t
                    cur_end = s_end
                    chunk_text = " ".join(cur_texts).strip()
                    j += 1

            chunks.append((chunk_text, cur_start, cur_end, cur_tokens))

        if overlap_tokens <= 0:
            i = j
        else:
            # Approximate overlap by stepping back 1-2 sentences depending on overlap_tokens
            # (simple but stable for slice-1)
            back = 1
            if len(cur_texts) >= 3 and overlap_tokens > token_budget * 0.2:
                back = 2
            i = max(i + 1, j - back)

    return chunks
