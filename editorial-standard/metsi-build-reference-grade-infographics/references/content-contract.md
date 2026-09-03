# Content contract

Create a `content-manifest.json` before drawing. The infographic is valid only when the manifest and visible SVG express the same model.

## Required fields

```json
{
  "title": "Short descriptive title",
  "claim": "The single proposition the visual must make understandable.",
  "source_sections": [
    {"id": "s1", "heading": "Source heading", "summary": "Supporting idea"}
  ],
  "nodes": [
    {
      "id": "n1",
      "label": "Visible label",
      "role": "actor|system|evidence|decision|process|boundary|outcome|constraint",
      "source": ["s1"],
      "purpose": "Why this node is necessary"
    }
  ],
  "edges": [
    {
      "id": "e1",
      "from": "n1",
      "to": "n2",
      "relation": "flow|dependency|authority|evidence|feedback|transformation|boundary",
      "source": ["s1"],
      "meaning": "What the connection asserts"
    }
  ]
}
```

## Writing rules

- Use concise labels that remain semantically complete.
- Prefer nouns for entities and verbs for processes or relations.
- Do not repeat the same title or paragraph in several nodes.
- Do not use placeholders such as “concepto”, “elemento”, “dato” or “proceso” without qualification.
- Do not add a visual element merely to balance the composition.
- Keep every visible label traceable to one or more source sections.
- Preserve meaningful asymmetry. Different roles may require different shapes, sizes, or positions.

## Conceptual audit

Before rendering, answer:

1. What does the reader understand after seeing the diagram that prose alone made harder to perceive?
2. Which relation is the visual's central explanatory mechanism?
3. What would be conceptually false if a node or edge were removed?
4. Which decision, risk, or boundary becomes visible?
5. Does the topology match the claim, or merely resemble a familiar diagram?

If these answers are weak, redesign before styling.
