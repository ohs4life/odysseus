# KB Ingredient Skill Notes (2026-08-05)

## What was done

The KB ingredient files (`~/knowledgebase/products/ingredient_list_2026.csv`) 
contain the full ingredient list for every OHS product, but the Opti-Mito-Force 
skill in the KB was incomplete — it only listed 3 "key ingredients" and 
warned the model not to invent the rest.

## Resulting hallucination

When asked "Is there anything in Opti-Mito-Force that is not vegan?", the 
agent correctly loaded the skill but said "I can't definitively answer" 
because the KB didn't have the full ingredient list. The customer got a 
non-answer for a question we had data for.

## Fix

Created `data/skills/ohs-products/opti-mito-force/SKILL.md` with:
- Complete ingredient list (every item + amount, sourced from the ingredient CSV)
- Vegan/vegetarian analysis of each ingredient  
- The single ambiguous ingredient (L-Carnitine Base) flagged with sourcing notes
- Common-question Q&A (vegan status, capsule material, allergens, etc.)
- Citation patterns for consistent formatting

The skill is automatically discovered since `data/skills/` is a source root.

## Recommended next step

Create similar skills for every product where customers commonly ask about
ingredients/allergens/sourcing. The ingredient_list_2026.csv covers all of them.

Suggested pattern for each product skill:
1. `ohs-products/<product-slug>/SKILL.md`
2. Full ingredient list from the CSV
3. Allergen/sourcing/vegan/religious-dietary analysis
4. Common customer Q&A
5. Citation patterns

## Bug fix discovered

During the fix, I discovered that the `scanner._process_one` function wipes
old chunk files on disk but the `upsert_chunks` call in meta.py can leave
stale DB rows if the chunk content hash changes between runs. This causes
the indexer to fail with `FileNotFoundError` because it tries to read
a file that no longer exists.

The fix: always wipe the meta.sqlite completely before re-indexing if
content hashes change, OR change the chunk_path in upsert_chunks to be
deterministic based on source_id + chunk_index rather than content_hash.

(For now: just delete data/knowledgebase/index/meta.sqlite* and re-run
`python -m scripts.kb.ingest` if you see "FileNotFoundError" during indexing.)
