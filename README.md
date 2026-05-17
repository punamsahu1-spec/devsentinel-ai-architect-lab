# DevSentinel: Enterprise Agentic RAG Security Copilot

DevSentinel is a portfolio-grade GenAI architecture project designed to demonstrate how enterprise AI systems can combine deterministic guardrails, RAG, context engineering, memory, agentic workflows, multi-agent design, MCP-style tools, evaluation, observability, and human-in-the-loop controls.

## Purpose

DevSentinel acts like a security guard for engineering teams.

Before code is merged or deployed, DevSentinel checks whether the pull request contains risky content such as hardcoded passwords, API keys, database connection strings, or prompt-injection-like instructions.

The long-term goal is to build an AI-powered engineering security copilot that can review PRs, retrieve internal security policies, reason over risks, recommend remediation steps, and produce auditable ALLOW, BLOCK, or HUMAN_REVIEW decisions.

## Current Phase

Phase 1: Deterministic Guardrail Foundation.

## What It Does Today

The current version can:

- Scan PR diff text for hardcoded secrets.
- Detect basic prompt injection attempts.
- Validate whether the user query is engineering-related.
- Return a structured decision: ALLOW or BLOCK.

## Current Local Flow

```text
Developer query + PR diff
        ↓
Engineering scope validation
        ↓
Prompt injection check
        ↓
Secret scanning
        ↓
ALLOW or BLOCK decision