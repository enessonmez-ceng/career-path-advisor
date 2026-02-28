# Lazy imports — allows importing submodules independently
def __getattr__(name):
    if name in ("career_advisor_graph", "build_graph"):
        from graph.graph import career_advisor_graph, build_graph
        return locals()[name]
    raise AttributeError(f"module 'graph' has no attribute {name}")
