"""
Career Path Advisor - LangGraph Workflow
Defines the main StateGraph connecting all nodes in the pipeline.
"""
from langgraph.graph import StateGraph, END

from graph.state import CareerState
from graph.consts import PARSE, EXTRACT, ANALYZE, RESEARCH, MATCH
from graph.nodes.parse import parse_node
from graph.nodes.extract import extract_node
from graph.nodes.analyze import analyze_node
from graph.nodes.research import research_node
from graph.nodes.match import match_node

def build_graph(enable_review: bool = False) -> StateGraph:
    """
    Build the Career Path Advisor workflow graph.

    Args:
        enable_review: If True, includes the review/reflection loop.
                       Default False for faster results (~15s vs ~35s).

    Flow (fast mode):
        parse -> extract -> analyze -> research -> match -> generate -> END

    Flow (review mode):
        parse -> extract -> analyze -> research -> match -> generate -> review
                                                                        |
                                                     (needs revision) -> generate
                                                     (done)           -> END
    """
    workflow = StateGraph(CareerState)

    # Add core nodes (generate removed)
    workflow.add_node(PARSE, parse_node)
    workflow.add_node(EXTRACT, extract_node)
    workflow.add_node(ANALYZE, analyze_node)
    workflow.add_node(RESEARCH, research_node)
    workflow.add_node(MATCH, match_node)

    # Set entry point
    workflow.set_entry_point(PARSE)

    # Add sequential edges
    workflow.add_edge(PARSE, EXTRACT)
    workflow.add_edge(EXTRACT, ANALYZE)
    workflow.add_edge(ANALYZE, RESEARCH)
    workflow.add_edge(RESEARCH, MATCH)
    
    # End workflow after match
    workflow.add_edge(MATCH, END)

    return workflow


# Compile the graph for use (fast mode by default)
career_advisor_graph = build_graph(enable_review=False).compile()
