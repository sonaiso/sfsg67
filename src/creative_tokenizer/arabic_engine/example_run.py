"""Example run of the Arabic Engine pipeline.

Demonstrates the full pipeline on: كَتَبَ زَيْدٌ الرِّسَالَةَ
(Zayd wrote the letter)

Produces:
  - Lexical closure for each word
  - Ontological concepts (entity / event)
  - Dalāla links (mutabaqa + isnad)
  - Syntax tree
  - Time/space anchoring
  - Judgment
  - Evaluation (truth + guidance state)
  - Inference (existential fact derivation)
"""

from creative_tokenizer.arabic_engine.inference.world_model import WorldModel
from creative_tokenizer.arabic_engine.pipeline import run_pipeline


def main() -> None:
    text = "كَتَبَ زَيْدٌ الرِّسَالَةَ"
    print(f"Input: {text}")
    print("=" * 60)

    # Create a world model with some background facts
    world = WorldModel()
    world.add("زيد", "موجود", confidence=1.0)
    world.add("كتابة", "فعل", confidence=0.9)

    result = run_pipeline(text, world=world)

    # 1. Normalization
    print(f"\n1. Normalized: {result.normalized.text!r}")

    # 2–4. Per-word analysis
    print("\n2–4. Word analyses:")
    for i, w in enumerate(result.words):
        print(f"\n  [{i}] surface={w.surface!r}")
        print(f"      root={w.root_pattern.root!r}  pattern={w.root_pattern.pattern!r}")
        print(f"      pos={w.root_pattern.pos!r}")
        print(f"      token_id={w.token.token_id}")
        print(f"      concept: {w.concept.label_en} (type={w.concept.semantic_type.name})")
        print(f"      dalala_mutabaqa: accepted={w.dalala_mutabaqa.accepted}, "
              f"confidence={w.dalala_mutabaqa.confidence:.2f}")
        if w.dalala_isnad is not None:
            print(f"      dalala_isnad: accepted={w.dalala_isnad.accepted}, "
                  f"confidence={w.dalala_isnad.confidence:.2f}")

    # 5. Syntax tree
    print("\n5. Syntax tree:")
    for node in result.syntax_tree:
        print(f"  pos={node.position}  role={node.role.name}  "
              f"head={node.head_index}  id={node.node_id}")

    # 6. Time/space
    print(f"\n6. Time anchor: {result.time_space.time_anchor.name}")
    print(f"   Space anchor: {result.time_space.space_anchor.name}")

    # 7. Judgment
    j = result.judgment
    print(f"\n7. Judgment: subject={j.subject}, predicate={j.predicate}, "
          f"object={j.object_id}, polarity={j.polarity}")

    # 8. Evaluation
    e = result.evaluation
    print(f"\n8. Evaluation: truth={e.truth_state.name}, "
          f"guidance={e.guidance_state.name}, confidence={e.confidence:.2f}")

    # 9. Inference
    if result.inference is not None:
        inf = result.inference
        print(f"\n9. Inference: rule={inf.rule.name}, "
              f"confidence={inf.confidence:.2f}")
        print(f"   Conclusion: subject={inf.conclusion.subject!r}, "
              f"predicate={inf.conclusion.predicate!r}, "
              f"truth={inf.conclusion.truth_state.name}")
    else:
        print("\n9. Inference: (no world model provided)")

    print("\n" + "=" * 60)
    print("Pipeline complete.")


if __name__ == "__main__":
    main()
