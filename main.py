import argparse

from analyzer.pipeline import run


def main():
    parser = argparse.ArgumentParser(description="AI customer feedback and ticket analyzer")
    parser.add_argument("--input", default="data/tickets.csv")
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()

    results, rejected, mode = run(args.input, args.output_dir, args.offline)

    print(f"Mode: {mode}")
    print(f"Processed: {len(results)} | Rejected: {len(rejected)}")
    print()
    for r in results:
        print(f"[{r['id']}] {r['category']} | {r['priority']} | {r['sentiment']} | {r['product']} ({r['method']})")
    print()
    for r in rejected:
        print(f"[{r['id']}] Rejected: {r['reason']}")


if __name__ == "__main__":
    main()