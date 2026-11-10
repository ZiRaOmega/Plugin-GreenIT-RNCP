# Recherche skills et verdict de sécurité

## Sources consultées

- Anthropic, Agent Skills : https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- Anthropic, dépôt public de skills : https://github.com/anthropics/skills
- Anthropic, skill PPTX : https://github.com/anthropics/skills/blob/main/skills/pptx/SKILL.md
- Anthropic, skill PDF : https://github.com/anthropics/skills/blob/main/skills/pdf/SKILL.md
- OpenAI, catalogue de skills : https://github.com/openai/skills
- OpenAI, skill slides (référencehistorique) : https://github.com/openai/skills/blob/main/skills/.curated/slides/SKILL.md
- Superpowers : https://github.com/obra/superpowers
- Superpowers, brainstorming : https://github.com/obra/superpowers/blob/main/skills/brainstorming/SKILL.md
- Design review (designpowers) : https://github.com/owl-listener/designpowers/blob/main/skills/design-review/SKILL.md
- Design review (agentic-design-system) : https://github.com/aa-on-ai/agentic-design-system/blob/main/skills/design-review/SKILL.md
- Claude Design Skill : https://github.com/andykaufseo/claude-design-skill
- PowerPoint skill : https://github.com/PracticalSwan/agent-skills/blob/main/powerpoint-ppt/SKILL.md

## Ce qui a été utilisé

- idées de structure de revue (verdict, constats, priorités) ;
- critères de QA PPTX (chevauchement, marges, typographie, sources) ;
- principes de design (une idée par slide, palette liée au projet, pas de barres décoratives) ;
- approche “review-only” sans réécriture.

## Ce qui n’a pas été installé

Aucun skill tiers n’a été installé ni exécuté. Aucun code distant n’a été lancé. Les dépôts ont été lus via `raw.githubusercontent.com` et l’API GitHub, sans clonage exécutable.

## Verdict sécurité

- lecture seule des sources web ;
- aucun `pip install`, `npm install` ou script tiers exécuté ;
- aucun secret ajouté ;
- le plugin reviewer est original, avec scripts locaux ;
- les dépendances utilisées sont déjà présentes (`pypdf`, `python-pptx`, `Pillow`, `openpyxl`).

## Limites

- La revue PDF est textuelle, pas une revue visuelle rasterisée.
- La revue PPTX est structurelle.
- Le contrôle RNCP vérifie la complétude, pas la qualité des preuves.
