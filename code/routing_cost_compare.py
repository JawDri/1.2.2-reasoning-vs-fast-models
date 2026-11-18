"""Lesson 1.2.2 - One model for everything vs. 3-tier routing: the monthly bill.

Free, offline, no API key. Prices come from prices.json (check the pricing page and update it).
Thinking tokens are billed as OUTPUT tokens; the numbers per tier below are assumptions you can
change (measure your own with thinking_tokens_demo.py).

  .\\run.ps1 routing_cost_compare.py
  .\\run.ps1 routing_cost_compare.py --messages 200000 --tier3-share 0.10
"""
import argparse
import sys

sys.dont_write_bytecode = True
from course_env import load_prices  # noqa: E402


def cost(price, runs, tokens_in, tokens_out, thinking):
    return runs * (tokens_in * price["input"] + (tokens_out + thinking) * price["output"]) / 1e6


def main():
    pr = load_prices()["models"]
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--messages", type=int, default=50_000, help="messages per month")
    p.add_argument("--input-tokens", type=int, default=1500)
    p.add_argument("--output-tokens", type=int, default=300)
    p.add_argument("--tier1-share", type=float, default=0.70, help="simple: answered by the fast tier")
    p.add_argument("--tier3-share", type=float, default=0.05, help="hard: needs deep reasoning")
    p.add_argument("--router-output", type=int, default=20, help="tokens the classifier writes")
    p.add_argument("--thinking", type=int, nargs=3, default=[0, 200, 2000], metavar=("T1", "T2", "T3"),
                   help="thinking tokens per message on each tier (low / low / high effort)")
    a = p.parse_args()
    tier2_share = 1 - a.tier1_share - a.tier3_share
    n, tin, tout = a.messages, a.input_tokens, a.output_tokens
    t1, t2, t3 = a.thinking
    fast, work, deep = pr["haiku"], pr["sonnet"], pr["opus"]

    print(f"{n:,} messages a month, {tin:,} input + {tout:,} output tokens each.")
    print(f"Prices per 1M tokens (in / out): Tier 1 {fast['name']} ${fast['input']:.2f} / ${fast['output']:.2f},"
          f" Tier 2 {work['name']} ${work['input']:.2f} / ${work['output']:.2f},"
          f" Tier 3 {deep['name']} ${deep['input']:.2f} / ${deep['output']:.2f}\n")

    everything = cost(deep, n, tin, tout, t3)
    print(f"A) EVERYTHING ON TIER 3 ({deep['name']}, {t3:,} thinking tokens per message)")
    print(f"   {f'{n:,} x ({tin:,} in + {tout + t3:,} out)':<32} = ${everything:>10,.2f} / month")
    print(f"   {'of which: hidden thinking':<32} = ${n * t3 * deep['output'] / 1e6:>10,.2f}\n")

    rows = [
        ("Router (Tier 1, every message)", cost(fast, n, tin, a.router_output, 0)),
        (f"{a.tier1_share:>4.0%} simple   -> Tier 1", cost(fast, n * a.tier1_share, tin, tout, t1)),
        (f"{tier2_share:>4.0%} standard -> Tier 2", cost(work, n * tier2_share, tin, tout, t2)),
        (f"{a.tier3_share:>4.0%} hard     -> Tier 3", cost(deep, n * a.tier3_share, tin, tout, t3)),
    ]
    print("B) ROUTED: a fast classifier first, then the cheapest tier that can do the job")
    for label, c in rows:
        print(f"   {label:<32} = ${c:>10,.2f}")
    routed = sum(c for _, c in rows)
    print(f"   {'TOTAL':<32} = ${routed:>10,.2f} / month")
    print(f"\nRouting is {1 - routed / everything:.0%} cheaper, and {1 - a.tier3_share:.0%} of messages"
          " never wait for deep reasoning.")


if __name__ == "__main__":
    main()
