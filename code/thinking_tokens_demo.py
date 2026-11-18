"""Lesson 1.2.2 - Measure hidden thinking tokens and waiting time: fast tier vs. deep tier.

Needs an Anthropic API key. Sends the same question to Claude Haiku 5.5 (effort "low") and to
Claude Opus 5.5 (effort "high"). Costs a few cents at most.

  .\\run.ps1 thinking_tokens_demo.py --dry-run
  .\\run.ps1 thinking_tokens_demo.py
  .\\run.ps1 thinking_tokens_demo.py --question "your own question"

Prints, for each model: seconds until the first visible word, total seconds, the tokens you are
billed for as output, how many of them you can actually see, and the cost.
"""
import argparse
import json
import sys
import time

sys.dont_write_bytecode = True
from course_env import load_prices, require_anthropic_key, usd  # noqa: E402

QUESTION = ("A client has three invoices: $1,200 due March 3, $450 due March 17 and $980 due April 2. "
            "Today is March 20. Which invoices are overdue, and what is the total overdue amount? "
            "Answer in one short sentence.")
RUNS = [("haiku", "low"), ("opus", "high")]


def request(model_id, effort, question):
    return {"model": model_id, "max_tokens": 16000,
            "thinking": {"type": "adaptive", "display": "summarized"},
            "output_config": {"effort": effort},
            "messages": [{"role": "user", "content": question}]}


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--question", default=QUESTION)
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()
    prices = load_prices()["models"]

    if a.dry_run:
        for tier, effort in RUNS:
            print(json.dumps(request(prices[tier]["id"], effort, a.question), indent=2))
        return

    require_anthropic_key()
    import anthropic
    client = anthropic.Anthropic()
    print(f"QUESTION: {a.question}\n")
    for tier, effort in RUNS:
        m = prices[tier]
        started, first_word = time.time(), None
        with client.messages.stream(**request(m["id"], effort, a.question)) as stream:
            for _ in stream.text_stream:
                if first_word is None:
                    first_word = time.time() - started
            final = stream.get_final_message()
        total = time.time() - started
        answer = "".join(b.text for b in final.content if b.type == "text").strip()
        summary = " ".join(b.thinking for b in final.content if b.type == "thinking").strip()
        billed = final.usage.output_tokens            # includes the hidden thinking tokens
        visible = client.messages.count_tokens(       # free: how big is the answer you can read?
            model=m["id"], messages=[{"role": "user", "content": answer or "."}]).input_tokens
        visible -= client.messages.count_tokens(
            model=m["id"], messages=[{"role": "user", "content": "."}]).input_tokens - 1
        visible = max(1, min(visible, billed))
        cost = (final.usage.input_tokens * m["input"] + billed * m["output"]) / 1e6
        print(f"{m['name']} (effort {effort})")
        print(f"  answer:          {answer}")
        if summary:
            print(f"  thinking (summary): {summary[:160]}{'...' if len(summary) > 160 else ''}")
        print(f"  first word after {first_word or total:5.1f} s   done after {total:5.1f} s")
        print(f"  output billed:   {billed:,} tokens   visible: ~{visible:,}   hidden thinking: ~{billed - visible:,}")
        print(f"  cost:            {usd(cost)}\n")
    print("Hidden thinking is billed at the OUTPUT price. Use deep reasoning only where it pays off.")


if __name__ == "__main__":
    main()
