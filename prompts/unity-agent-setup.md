---
title: Unity Agent Setup Prompt
status: active
owner: chrysa
last-reviewed: 2026-10-03
---

# Unity Agent Setup Prompt

## Purpose

Canonical prompt applied to **every** Unity project (new or existing) to wire the
official Unity agent plugin, the Unity CLI and the Unity MCP server, without creating
a hidden dependency on one coding agent. It is step 5 of
[`workflows/unity-project-flow.md`](../workflows/unity-project-flow.md).

Paste it verbatim into the coding agent, from the Unity project root.
The prompt body is kept in its original language (French) on purpose: it is the
owner-authored input, not repository documentation.

## Prompt

```text
Contexte : je veux intégrer le plugin officiel Unity pour Claude Code dans ce projet Unity, sans créer de dépendance cachée à Claude.

Objectif : installer et vérifier le plugin, le Unity CLI et le serveur MCP Unity, en gardant mes automatisations portables vers d'autres agents.

Étapes :
1. Vérifie la version de Claude Code (`claude --version`) et signale si elle est trop ancienne pour le système de plugins.
2. Vérifie la version Unity du projet (ProjectSettings/ProjectVersion.txt). Le contrôle live de l'Editor requiert Unity 6.0+ : si ce n'est pas le cas, arrête-toi et dis-le-moi.
3. Installe le plugin en scope local (projet uniquement, pas global) :
   - claude plugin marketplace add Unity-Technologies/unity-agent-plugin
   - claude plugin install unity@unity-agent-plugin --scope local
   Si une commande échoue en shell, donne-moi l'équivalent en slash command (/plugin …) à lancer moi-même.
4. Vérifie que le Unity CLI est disponible (`unity --version`). Sinon, propose la méthode d'installation officielle et attends mon accord avant d'installer quoi que ce soit.
5. Pour le contrôle live de l'Editor : guide-moi pour `unity auth login` (je le fais moi-même), puis propose `unity pipeline install` dans le projet et attends mon accord.
6. Liste les skills Unity effectivement chargés et résume en 1 ligne chacun ceux pertinents pour ce projet.

Contraintes :
- Demande-moi confirmation avant toute installation, modification de package ou commit.
- Tout script ou automatisation que tu écris doit s'appuyer sur le Unity CLI ou le MCP standard, jamais sur une fonctionnalité propre à Claude Code, pour rester réutilisable avec un autre agent.
- Aucune trace de Claude ou d'Anthropic dans le dépôt : pas de Co-Authored-By dans les commits, aucune mention dans les fichiers, README, docs ou commentaires.
- Vérifie que la config locale du plugin (.claude/settings.local.json ou équivalent) n'est pas commitée ; ajoute-la au .gitignore si besoin, après accord.

Livrable final : un récap court de ce qui est installé, ce qui reste à faire de mon côté, et les éventuels blocages.
```

## Scope notes

- "No trace in the repository" covers what this setup adds. The `CLAUDE.md` /
  `AGENTS.md` / `.claude/` files distributed by `shared-standards` are out of its scope.
- Other agents: the same plugin ships for Codex
  (`codex plugin marketplace add Unity-Technologies/unity-agent-plugin`,
  `codex plugin add unity@unity-agent-plugin`) and Grok; the MCP server is registered
  for any client with `unity mcp configure <client>`.
