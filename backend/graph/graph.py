"""
Career Path Advisor - LangGraph Workflow
Defines the main StateGraph connecting all nodes in the pipeline.

Flow (parallel mode):
    parse -> extract -> [analyze, research] (parallel) -> match -> END

    After extract, analyze (LLM) and research (DB) run simultaneously.
    Match node waits for both to complete before executing.
"""
from langgraph.graph import StateGraph, END

from graph.state import CareerState
from graph.consts import PARSE, EXTRACT, ANALYZE, RESEARCH, MATCH
from graph.nodes.parse import parse_node
from graph.nodes.extract import extract_node
from graph.nodes.analyze import analyze_node
from graph.nodes.research import research_node
from graph.nodes.match import match_node


def build_graph() -> StateGraph:
    """
    Build the Career Path Advisor workflow graph.

    Uses fan-out / fan-in pattern:
      - extract fans out to [analyze, research] (parallel)
      - match fans in (waits for both to complete)
    """
    workflow = StateGraph(CareerState)

    # Add all nodes
    workflow.add_node(PARSE, parse_node)
    workflow.add_node(EXTRACT, extract_node)
    workflow.add_node(ANALYZE, analyze_node)
    workflow.add_node(RESEARCH, research_node)
    workflow.add_node(MATCH, match_node)

    # Set entry point
    workflow.set_entry_point(PARSE)

    # Sequential: parse -> extract
    workflow.add_edge(PARSE, EXTRACT)

    # Fan-out: extract -> [analyze, research] (parallel execution)
    workflow.add_edge(EXTRACT, ANALYZE)
    workflow.add_edge(EXTRACT, RESEARCH)

    # Fan-in: [analyze, research] -> match (waits for both)
    workflow.add_edge(ANALYZE, MATCH)
    workflow.add_edge(RESEARCH, MATCH)

    # End
    workflow.add_edge(MATCH, END)

    return workflow


# Compile the graph
career_advisor_graph = build_graph().compile()
