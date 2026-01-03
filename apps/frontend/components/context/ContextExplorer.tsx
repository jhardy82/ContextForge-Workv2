
import dagre from '@dagrejs/dagre';
import {
    addEdge,
    Background,
    Connection,
    Controls,
    Edge,
    MiniMap,
    Node,
    Panel,
    ReactFlow,
    ReactFlowProvider,
    useEdgesState,
    useNodesState,
    useReactFlow,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useCallback, useEffect } from 'react';

import { motion } from 'framer-motion';

import { useContextGraph } from '@/api/features/useContextGraph';
import { Button } from '@/components/ui/button';
import { useUIStore } from '@/stores/uiStore';
import { AlertCircle, Loader2 } from 'lucide-react';

const nodeStyle = {
    background: 'rgba(30, 41, 59, 0.4)', // Slightly transparent slate
    color: '#f8fafc',
    border: '1px solid rgba(148, 163, 184, 0.1)',
    padding: '12px 16px',
    borderRadius: '12px',
    fontSize: '13px',
    fontWeight: 500,
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    backdropFilter: 'blur(12px)',
    width: 180,
    textAlign: 'center' as const,
    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
};

// --- Types ---
interface ContextNode extends Node {
    data: {
        label: string;
        kind: string;
        depth: number;
        originalId: string;
    }
}

// --- Layout Helper ---
const getLayoutedElements = (nodes: Node[], edges: Edge[], direction = 'TB') => {
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));

  const isHorizontal = direction === 'LR';
  dagreGraph.setGraph({ rankdir: direction });

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: 150, height: 50 });
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  const newNodes = nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    return {
      ...node,
      targetPosition: isHorizontal ? 'left' : 'top',
      sourcePosition: isHorizontal ? 'right' : 'bottom',
      // We are shifting the dagre node position (anchor=center center) to the top left
      // so it matches the React Flow node anchor point (top left).
      position: {
        x: nodeWithPosition.x - 75, // half width
        y: nodeWithPosition.y - 25, // half height
      },
    };
  });

  return { nodes: newNodes, edges };
};

// --- Main Layout Component to be wrapped ---
function ContextGraphLayout() {
    const { data: graphData, isLoading, error, refetch } = useContextGraph();
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const { fitView } = useReactFlow();
    const selectedId = useUIStore((state) => state.selectedId);

    // Effect to focus on selected node
    useEffect(() => {
        if (selectedId && nodes.length > 0) {
            // Find node to get position?
            // xyflow `fitView` takes `nodes` array of {id}.
            // We verify the node exists first
            const targetNode = nodes.find(n => n.id === selectedId || n.data.originalId === selectedId);
            if (targetNode) {
                 fitView({ nodes: [{ id: targetNode.id }], duration: 800, padding: 0.5 });
            }
        }
    }, [selectedId, nodes, fitView]);

    // Process Data into Nodes/Edges
    useEffect(() => {
        if (!graphData) return;

        const rawNodes: ContextNode[] = [];
        const rawEdges: Edge[] = [];

        // 1. Create Nodes
        graphData.forEach((item) => {
            rawNodes.push({
                id: item.id,
                position: { x: 0, y: 0 }, // Initial, will be calculated by dagre
                data: {
                    label: item.title,
                    kind: item.kind,
                    depth: item.depth,
                    originalId: item.id
                },
                type: 'default', // Using standard node type for now
                style: {
                    ...nodeStyle,
                    // Dynamic border color based on kind?
                    borderColor: item.kind === 'active' ? 'var(--color-primary)' : nodeStyle.border
                }
            });
        });

        // 2. Create Edges from 'path'
        // API returns path like [grandparent_id, parent_id, self_id]
        // Edge is parent -> self
        graphData.forEach((item) => {
            if (item.path && item.path.length > 1) {
                // The immediate parent is the second to last item
                // The item itself is the last item
                 const parentId = item.path[item.path.length - 2];
                 // Ensure parent exists in our dataset (it should)
                 // Prevent duplicates: edge ID = parent-child
                 const edgeId = `${parentId}-${item.id}`;

                 // Check if edge already exists (set logic preferable but list small enough)
                 if (!rawEdges.find(e => e.id === edgeId)) {
                     rawEdges.push({
                         id: edgeId,
                         source: parentId,
                         target: item.id,
                         type: 'smoothstep',
                         animated: true,
                         style: { stroke: '#64748b' }
                     });
                 }
            }
        });

        // 3. Apply Layout
        const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
            rawNodes,
            rawEdges
        );

        // @ts-ignore - xyflow types can be picky about derived nodes
        setNodes(layoutedNodes);
        setEdges(layoutedEdges);

        // Fit view after a brief delay to allow rendering
        setTimeout(() => fitView(), 50);

    }, [graphData, setNodes, setEdges, fitView]);

    const onConnect = useCallback(
        (params: Connection) => setEdges((eds) => addEdge(params, eds)),
        [setEdges],
      );

    if (isLoading) {
        return (
            <div className="flex h-full items-center justify-center text-cyan-400">
                <Loader2 className="w-8 h-8 animate-spin mr-2" />
                <span>Loading Knowledge Graph...</span>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex h-full flex-col items-center justify-center text-red-400">
                <AlertCircle className="w-10 h-10 mb-2" />
                <p>Failed to load context graph.</p>
                <Button variant="outline" size="sm" onClick={() => refetch()} className="mt-4">
                    Retry
                </Button>
            </div>
        );
    }

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
            className="w-full h-full relative"
        >
            <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onConnect={onConnect}
                fitView
                className="bg-transparent"
            >
                <Background color="#94a3b8" gap={24} size={1} className="opacity-10" />
                <Controls className="glass border-white/10 fill-foreground stroke-foreground text-foreground rounded-lg overflow-hidden m-4 shadow-xl" />
                <MiniMap
                    className="glass rounded-xl border-white/10 m-4 shadow-xl overflow-hidden"
                    nodeStrokeColor="transparent"
                    nodeColor="#334155"
                    maskColor="rgba(0,0,0,0.6)"
                    style={{ height: 120, width: 160 }}
                    zoomable pannable
                />
                <Panel position="top-right" className="m-4">
                    <div className="glass px-4 py-2 rounded-full border border-white/10 text-xs font-mono text-muted-foreground flex items-center gap-3 shadow-lg backdrop-blur-md">
                        <div className="flex items-center gap-1.5">
                            <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse shadow-[0_0_8px_rgba(34,211,238,0.5)]"></div>
                            <span>Active</span>
                        </div>
                        <div className="w-px h-3 bg-white/10"></div>
                         <div className="font-bold text-foreground">
                            {nodes.length} Nodes
                        </div>
                    </div>
                </Panel>
            </ReactFlow>
        </motion.div>
    );
}

// --- Export Wrapper with Provider ---
export function ContextExplorer() {
    return (
        <div className="h-full w-full overflow-hidden relative">
            <ReactFlowProvider>
                <ContextGraphLayout />
            </ReactFlowProvider>
        </div>
    );
}
